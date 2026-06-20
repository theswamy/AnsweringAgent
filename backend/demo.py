"""End-to-end demo of the Answering Agent — runs the REAL backend offline.

What's real here:
  • The actual FastAPI routes (/twilio/voice, /twilio/gather, /twilio/status)
  • The real TwiML the server hands back to Twilio (what the caller would hear)
  • Real SQLite persistence of the call + every transcript turn
  • The real companion JSON API (/api/calls, /api/calls/{sid})

What's stubbed (so it runs with no API key / no phone line):
  • claude_agent.advance_conversation / summarize_call  → a scripted "model"
    (set ANTHROPIC_API_KEY to use the real model instead)
  • Twilio's outbound SMS send → captured and printed instead of sent

Run:  python demo.py
"""
from __future__ import annotations

import os
import re
import sys
import tempfile

# --- isolate the demo: dummy config + throwaway DB -------------------------- #
os.environ.setdefault("ANTHROPIC_API_KEY", "demo")
os.environ["DATABASE_PATH"] = os.path.join(tempfile.mkdtemp(), "demo.db")
os.environ["PUBLIC_BASE_URL"] = "https://demo.local"
os.environ["APP_API_KEY"] = "demo-key"
os.environ["TWILIO_ACCOUNT_SID"] = "ACdemo"
os.environ["TWILIO_AUTH_TOKEN"] = "demo"
os.environ["TWILIO_PHONE_NUMBER"] = "+15550000000"

from fastapi.testclient import TestClient  # noqa: E402

from app import claude_agent, db, main  # noqa: E402

USE_LIVE_MODEL = os.environ.get("ANTHROPIC_API_KEY", "demo") != "demo"


# --------------------------------------------------------------------------- #
# Stub the model unless a real key is present. The scripted replies mimic what
# Claude returns: the structured per-turn dict the real engine produces.
# --------------------------------------------------------------------------- #
def scripted_advance(history, user_name, agent_defaults):
    caller_turns = sum(1 for t in history if t["role"] == "caller")
    if caller_turns == 1:
        return {
            "speech": f"Thanks, Priya. What would you like to convey to {user_name}?",
            "should_end": False, "caller_name": "Priya (Apollo Clinic)",
            "intent": None, "callback_requested": False,
            "callback_number": None, "callback_time": None, "is_automated": False,
        }
    if caller_turns == 2:
        return {
            "speech": ("Got it — a reminder about the dental appointment tomorrow "
                       "at 3 PM, and you'd like a callback. What number and time "
                       "work best?"),
            "should_end": False, "caller_name": "Priya (Apollo Clinic)",
            "intent": "Confirming dental appointment tomorrow at 3 PM; requests a callback",
            "callback_requested": True, "callback_number": None,
            "callback_time": None, "is_automated": False,
        }
    return {
        "speech": ("Perfect, I've noted 408-555-0192 after 5 PM today. I'll pass "
                   f"everything to {user_name}. Goodbye!"),
        "should_end": True, "caller_name": "Priya (Apollo Clinic)",
        "intent": "Confirming dental appointment tomorrow at 3 PM; requests a callback",
        "callback_requested": True, "callback_number": "408-555-0192",
        "callback_time": "after 5 PM today", "is_automated": False,
    }


def scripted_summary(transcript, user_name):
    return ("Priya from Apollo Clinic called to remind you of your dental "
            "appointment tomorrow at 3 PM and asked you to call back. "
            "Reach her at 408-555-0192 any time after 5 PM today.")


if not USE_LIVE_MODEL:
    claude_agent.advance_conversation = scripted_advance
    claude_agent.summarize_call = scripted_summary
    main.claude_agent.advance_conversation = scripted_advance
    main.claude_agent.summarize_call = scripted_summary


# --- capture the SMS instead of really sending it --------------------------- #
SENT_SMS: list[dict] = []


class FakeMessages:
    def create(self, to, from_, body):
        SENT_SMS.append({"to": to, "from": from_, "body": body})


class FakeTwilioClient:
    def __init__(self, *a, **k): pass
    messages = FakeMessages()


main.TwilioClient = FakeTwilioClient


# --------------------------------------------------------------------------- #
# Pretty printing
# --------------------------------------------------------------------------- #
def say_lines(twiml: str) -> list[str]:
    """Pull the spoken <Say> text out of the TwiML the server returned."""
    return [re.sub(r"\s+", " ", s).strip() for s in re.findall(r"<Say[^>]*>(.*?)</Say>", twiml, re.S)]


def hr(title=""):
    print("\n" + "─" * 64)
    if title:
        print(title)
        print("─" * 64)


def main_demo():
    client = TestClient(main.app)
    db.init_db()  # the startup hook only fires under the context-manager form

    print("=" * 64)
    print("  ANSWERING AGENT — LIVE BACKEND DEMO")
    print(f"  model: {'REAL Anthropic API' if USE_LIVE_MODEL else 'scripted stand-in (no API key)'}")
    print("=" * 64)

    # Configure the agent exactly as the iPhone app would (PUT /api/settings).
    client.put(
        "/api/settings",
        headers={"X-API-Key": "demo-key"},
        json={"user_name": "Sanjay", "user_phone": "+14155551234",
              "send_transcript_sms": True},
    )
    print("\n[iPhone app] Saved agent settings: name=Sanjay, "
          "text transcripts to +14155551234")

    call_sid = "CADEMO0001"
    base_form = {"CallSid": call_sid, "From": "+14085550192", "To": "+15550000000"}

    hr("📞  INCOMING CALL  (your phone didn't answer → forwarded to the agent)")
    r = client.post("/twilio/voice", data=base_form)
    for line in say_lines(r.text):
        print(f"   🤖 agent:  {line}")

    # The simulated caller's spoken turns (Twilio would transcribe these).
    caller_script = [
        "Hi, this is Priya calling from Apollo Clinic.",
        "I wanted to remind Sanjay about his dental appointment tomorrow at 3 PM, "
        "and ask him to call us back.",
        "He can reach us at 408 555 0192 any time after 5 PM today.",
    ]

    for utterance in caller_script:
        print(f"\n   🧑 caller: {utterance}")
        r = client.post("/twilio/gather?retry=0", data={**base_form, "SpeechResult": utterance})
        for line in say_lines(r.text):
            print(f"   🤖 agent:  {line}")
        if "<Hangup" in r.text:
            print("   ☎️  (agent hung up)")

    # Twilio fires the status callback when the call ends.
    client.post("/twilio/status", data={**base_form, "CallStatus": "completed"})

    # --- What got stored + sent --------------------------------------------- #
    hr("💾  STORED CALL RECORD  (GET /api/calls/{sid} — what the iPhone app shows)")
    detail = client.get(f"/api/calls/{call_sid}", headers={"X-API-Key": "demo-key"}).json()
    print(f"   Caller name ....... {detail['caller_name']}")
    print(f"   From .............. {detail['from_number']}")
    print(f"   Intent ............ {detail['intent']}")
    print(f"   Callback requested  {'yes' if detail['callback_requested'] else 'no'}")
    print(f"   Callback number ... {detail['callback_number']}")
    print(f"   Callback time ..... {detail['callback_time']}")
    print(f"   Automated caller .. {'yes' if detail['is_automated'] else 'no'}")
    print(f"   Status ............ {detail['status']}")
    print(f"\n   Summary: {detail['summary']}")

    hr("📝  FULL TRANSCRIPT  (every turn, stored in SQLite)")
    print(detail["transcript"])

    hr("✉️   TRANSCRIPT TEXTED TO YOU  (the SMS the agent sent)")
    if SENT_SMS:
        sms = SENT_SMS[0]
        print(f"   to: {sms['to']}   from: {sms['from']}\n")
        print("   " + sms["body"].replace("\n", "\n   "))
    else:
        print("   (none)")

    hr("📋  CALL LIST  (GET /api/calls — the Calls tab)")
    for c in client.get("/api/calls", headers={"X-API-Key": "demo-key"}).json():
        flag = " [callback]" if c["callback_requested"] else ""
        print(f"   • {c['caller_name'] or c['from_number']} — {c['intent']}{flag}")

    print("\n" + "=" * 64)
    print("  Demo complete. Every line above came from the real backend code;")
    print("  only the model replies and the SMS transport were stubbed offline.")
    print("=" * 64)


if __name__ == "__main__":
    main_demo()
