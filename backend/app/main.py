"""FastAPI server.

Two surfaces:
  • /twilio/*  — webhooks Twilio calls while a forwarded phone call is live.
  • /api/*     — JSON API the iPhone companion app uses to configure the agent
                 and read call logs + transcripts. Protected by X-API-Key.

Call flow (each step is a separate HTTP request from Twilio):
  incoming call ─▶ POST /twilio/voice    greet + ask "who is speaking?"
  caller speaks ─▶ POST /twilio/gather   Claude replies, ask next thing, or hang up
  call ends     ─▶ POST /twilio/status   finalize: summarize + text the owner
"""
from __future__ import annotations

import logging

from fastapi import Depends, FastAPI, Form, Header, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from twilio.rest import Client as TwilioClient
from twilio.twiml.voice_response import Gather, VoiceResponse

from . import claude_agent, db
from .config import get_settings

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("answering_agent")

app = FastAPI(title="Answering Agent")


@app.on_event("startup")
def _startup() -> None:
    db.init_db()


# --------------------------------------------------------------------------- #
# Twilio voice webhooks                                                        #
# --------------------------------------------------------------------------- #

def _gather(action: str) -> Gather:
    """A speech-input gather. Twilio does speech-to-text; `auto` end-of-speech
    detection ends the turn when the caller stops talking."""
    return Gather(
        input="speech",
        action=action,
        method="POST",
        speech_timeout="auto",
        language="en-US",
        action_on_empty_result=True,  # still call us back if they say nothing
    )


@app.post("/twilio/voice")
async def voice(request: Request) -> Response:
    form = await request.form()
    call_sid = form.get("CallSid", "")
    db.create_call(call_sid, form.get("From", ""), form.get("To", ""))

    s = db.get_user_settings()
    name = s["user_name"]

    vr = VoiceResponse()
    greeting = (
        f"Hi - this is {name}'s agent, {name} isn't available. Who is speaking?"
    )
    db.add_turn(call_sid, "agent", greeting)

    g = _gather(action=f"{get_settings().public_base_url}/twilio/gather?retry=0")
    g.say(greeting, voice="Polly.Joanna")
    vr.append(g)
    # If the gather produced nothing at all, loop back once.
    vr.redirect(f"{get_settings().public_base_url}/twilio/gather?retry=0", method="POST")
    return Response(content=str(vr), media_type="application/xml")


@app.post("/twilio/gather")
async def gather(request: Request, retry: int = 0) -> Response:
    form = await request.form()
    call_sid = form.get("CallSid", "")
    speech = (form.get("SpeechResult") or "").strip()

    s = db.get_user_settings()
    name, defaults = s["user_name"], s["agent_defaults"]
    base = get_settings().public_base_url
    vr = VoiceResponse()

    # No speech captured — reprompt a couple of times, then wrap up.
    if not speech:
        if retry >= get_settings().max_no_input_retries:
            bye = f"I didn't catch that. I'll let {name} know you called. Goodbye."
            db.add_turn(call_sid, "agent", bye)
            vr.say(bye, voice="Polly.Joanna")
            vr.hangup()
            _finalize(call_sid)
            return Response(content=str(vr), media_type="application/xml")
        prompt = "Sorry, I didn't catch that. Could you say that again?"
        db.add_turn(call_sid, "agent", prompt)
        g = _gather(action=f"{base}/twilio/gather?retry={retry + 1}")
        g.say(prompt, voice="Polly.Joanna")
        vr.append(g)
        vr.redirect(f"{base}/twilio/gather?retry={retry + 1}", method="POST")
        return Response(content=str(vr), media_type="application/xml")

    # Record what the caller said and ask Claude for the next turn.
    db.add_turn(call_sid, "caller", speech)
    history = [{"role": t["role"], "text": t["text"]} for t in db.get_turns(call_sid)]

    try:
        turn = claude_agent.advance_conversation(history, name, defaults)
    except Exception:  # never drop the call on a model error
        log.exception("Claude turn failed for %s", call_sid)
        turn = {
            "speech": f"Thank you. I'll pass your message to {name}. Goodbye.",
            "should_end": True,
        }

    db.add_turn(call_sid, "agent", turn["speech"])
    db.update_call(
        call_sid,
        caller_name=turn.get("caller_name"),
        intent=turn.get("intent"),
        callback_requested=1 if turn.get("callback_requested") else None,
        callback_number=turn.get("callback_number"),
        callback_time=turn.get("callback_time"),
        is_automated=1 if turn.get("is_automated") else None,
    )

    if turn.get("should_end"):
        vr.say(turn["speech"], voice="Polly.Joanna")
        vr.hangup()
        _finalize(call_sid)
    else:
        g = _gather(action=f"{base}/twilio/gather?retry=0")
        g.say(turn["speech"], voice="Polly.Joanna")
        vr.append(g)
        vr.redirect(f"{base}/twilio/gather?retry=0", method="POST")

    return Response(content=str(vr), media_type="application/xml")


@app.post("/twilio/status")
async def status(request: Request) -> Response:
    """Twilio status callback — fires when the call ends for any reason
    (caller hung up, dropped, etc.). Ensures we always finalize."""
    form = await request.form()
    call_sid = form.get("CallSid", "")
    if form.get("CallStatus") in {"completed", "no-answer", "busy", "failed", "canceled"}:
        _finalize(call_sid)
    return Response(status_code=204)


def _finalize(call_sid: str) -> None:
    """Idempotent: summarize the call, mark it complete, and text the owner."""
    call = db.get_call(call_sid)
    if not call or call["status"] == "completed":
        return

    transcript = db.transcript_text(call_sid)
    s = db.get_user_settings()
    try:
        summary = claude_agent.summarize_call(transcript, s["user_name"])
    except Exception:
        log.exception("Summary failed for %s", call_sid)
        summary = "(summary unavailable)"

    db.update_call(call_sid, status="completed", ended_at=db._now(), summary=summary)
    _maybe_text_owner(call_sid, summary, transcript)


def _maybe_text_owner(call_sid: str, summary: str, transcript: str) -> None:
    s = db.get_user_settings()
    cfg = get_settings()
    if not s["send_transcript_sms"] or not s["user_phone"]:
        return
    if not (cfg.twilio_account_sid and cfg.twilio_auth_token and cfg.twilio_phone_number):
        log.warning("Twilio SMS not configured; skipping transcript text.")
        return
    call = db.get_call(call_sid) or {}
    body = (
        f"📞 New message via your agent\n"
        f"From: {call.get('caller_name') or call.get('from_number') or 'Unknown'}\n\n"
        f"{summary}\n\n— transcript —\n{transcript}"
    )[:1550]  # keep SMS to a sane length
    try:
        TwilioClient(cfg.twilio_account_sid, cfg.twilio_auth_token).messages.create(
            to=s["user_phone"], from_=cfg.twilio_phone_number, body=body
        )
    except Exception:
        log.exception("Failed to send transcript SMS for %s", call_sid)


# --------------------------------------------------------------------------- #
# Companion-app JSON API                                                        #
# --------------------------------------------------------------------------- #

def require_api_key(x_api_key: str = Header(default="")) -> None:
    if x_api_key != get_settings().app_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")


class SettingsUpdate(BaseModel):
    user_name: str | None = None
    user_phone: str | None = None
    agent_defaults: str | None = None
    send_transcript_sms: bool | None = None


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/settings", dependencies=[Depends(require_api_key)])
def api_get_settings() -> dict:
    return db.get_user_settings()


@app.put("/api/settings", dependencies=[Depends(require_api_key)])
def api_update_settings(body: SettingsUpdate) -> dict:
    fields = body.model_dump(exclude_none=True)
    if "send_transcript_sms" in fields:
        fields["send_transcript_sms"] = 1 if fields["send_transcript_sms"] else 0
    return db.update_user_settings(**fields)


@app.get("/api/calls", dependencies=[Depends(require_api_key)])
def api_list_calls() -> JSONResponse:
    return JSONResponse(db.list_calls())


@app.get("/api/calls/{call_sid}", dependencies=[Depends(require_api_key)])
def api_get_call(call_sid: str) -> JSONResponse:
    call = db.get_call(call_sid)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    call["turns"] = db.get_turns(call_sid)
    call["transcript"] = db.transcript_text(call_sid)
    return JSONResponse(call)
