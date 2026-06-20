# Architecture

## Why it isn't a pure on-device app

iOS exposes no API to answer a cellular (PSTN) call, read its audio, or inject
audio into it. The relevant frameworks and their hard limits:

- **CallKit** — lets a *VoIP* app present and manage its own internet calls. It
  cannot answer or access the audio of a normal carrier call.
- **Call Directory extension** — can only supply block lists and caller-ID
  labels. No call control, no audio.
- **No background "call screening" hook** exists for third-party apps.

So "intercept all calls and become an answering machine" is delivered the only
way it can be: the call is **forwarded** off the device to a phone number you
control (Twilio), where a server answers it and runs the AI conversation. The
iPhone app configures that server and reads what it captured.

## Components

### Telephony (Twilio)
- Receives the forwarded call on your Twilio number.
- On each step, POSTs a webhook to the backend; the backend replies with **TwiML**
  (`<Gather input="speech">`, `<Say>`). Twilio does speech-to-text on the caller
  and text-to-speech for the agent (Amazon Polly voice).
- Sends the final transcript to you via SMS.

### Backend (`backend/app`)
- `main.py` — FastAPI. `/twilio/voice` greets and asks who's calling;
  `/twilio/gather` is hit on every caller utterance and returns the agent's next
  line (or hangs up); `/twilio/status` finalizes the call. `/api/*` is the
  companion-app JSON API, guarded by `X-API-Key`.
- `claude_agent.py` — builds the system prompt and calls Claude with a
  **structured-output** schema, so each turn returns `{ speech, should_end,
  caller_name, intent, callback_*, is_automated }`. Thinking is off for latency.
- `db.py` — SQLite. `calls` (one row per call + extracted facts + summary),
  `turns` (every line spoken, both sides), `settings` (the single editable row).
- `config.py` — secrets and tunables from environment / `.env`.

### iPhone app (`ios/AnsweringAgent`)
- SwiftUI. `APIClient` stores the server URL + key on-device and talks to `/api/*`.
- `OnboardingView` connects to the backend; `CallListView` / `CallDetailView`
  show logs and transcripts; `SettingsView` edits name, transcript phone, and the
  automated-caller defaults.

## Conversation control flow

```
/twilio/voice
  └─ greet + "Who is speaking?"  ──▶ <Gather> → /twilio/gather

/twilio/gather  (per caller utterance)
  ├─ store caller turn
  ├─ Claude → next agent turn (structured)
  ├─ store agent turn + extracted facts
  └─ should_end? ── yes ─▶ <Say> goodbye + <Hangup> ─▶ _finalize
                  └─ no  ─▶ <Say> reply + <Gather> → /twilio/gather

/twilio/status (call ended)
  └─ _finalize: summarize (Claude) + mark complete + SMS owner
```

`_finalize` is idempotent, so whether the agent hangs up or the caller drops, the
call is summarized and you're texted exactly once.

## Extending it

- **Push instead of SMS:** add APNs and push a notification on finalize; the app
  already polls, so a silent push that triggers a refresh is a small addition.
- **Recordings:** add `record="true"` to the TwiML and store the Twilio recording
  URL on the call row.
- **Real-time streaming TTS/STT:** swap the `<Gather>` turn-based flow for Twilio
  Media Streams + a streaming STT/TTS provider for lower latency and barge-in.
- **Per-contact behaviour:** branch on `From` in `/twilio/voice` to greet known
  contacts differently.
