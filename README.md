# Answering Agent

An intelligent answering machine for your iPhone. When you can't take a call, it
picks up, greets the caller as **your agent**, finds out who's calling and what
they want, handles callback requests, deals with robocalls/IVRs by your rules,
stores everything, and texts you the transcript.

> **The greeting it gives, verbatim:**
> *"Hi - this is {YourName}'s agent, {YourName} isn't available. Who is speaking?"*
> Then it asks what they'd like to convey, and has a short, focused conversation.

---

## ⚠️ Read this first — how call answering really works on iPhone

**iOS does not let any app intercept, answer, or listen to the audio of a normal
phone call.** There is no public API for it — `CallKit` is only for VoIP apps to
present *their own* calls, and the Call Directory extension can only *block or
label* numbers. A standalone on-device app that auto-answers your cellular calls
and talks to the caller **cannot be built** and would be rejected by Apple.

Every real "AI answers my calls" product works the same way, and so does this one:

```
   Caller ──dials──▶ Your iPhone
                         │  (you don't pick up)
                         │  carrier conditional call forwarding
                         ▼
                   Twilio phone number
                         │  webhooks (TwiML)
                         ▼
        ┌─────────────────────────────────────┐
        │  Answering Agent backend (this repo) │
        │  • greets + converses (Claude)       │
        │  • Twilio does speech-to-text & TTS  │
        │  • stores logs + transcripts (SQLite)│
        │  • texts you the transcript          │
        └─────────────────────────────────────┘
                         ▲
                         │  JSON API (X-API-Key)
                   iPhone companion app (SwiftUI)
                   • set your name + defaults
                   • read call logs + transcripts
```

So you get exactly the behaviour you asked for — it just runs as **call
forwarding → a cloud number → an AI voice agent**, with the iPhone app as the
control panel. No jailbreak, fully within Apple's rules.

---

## Repository layout

| Path | What it is |
|---|---|
| `backend/` | Python (FastAPI) service: Twilio voice webhooks + Claude + SQLite + companion API |
| `ios/AnsweringAgent/` | SwiftUI companion app source (onboarding, call list, transcript, settings) |
| `deal_agent/` | A second, unrelated answering agent: Q&A over the SB2 / NLP secondary transaction document (see below) |
| `docs/` | Architecture and setup notes, plus the deal analysis |

## How the requested behaviour maps to the code

| Your requirement | Where it lives |
|---|---|
| Greeting "Hi - this is {Name}'s agent…" + "Who is speaking?" | `backend/app/main.py` → `/twilio/voice` |
| "What would you like to convey to {Name}?" + crisp conversation | `backend/app/claude_agent.py` (system prompt) |
| Keep conversations short and to the point | system prompt: one–two sentences per turn |
| Callback → ask for convenient time/date and number | system prompt + structured `callback_*` fields |
| Caller is an agent/IVR → follow user defaults | `agent_defaults` setting, editable in the app |
| Store all logs + conversation history | `backend/app/db.py` (`calls`, `turns` tables) |
| Send you the transcript | `/twilio/status` → `_finalize` → SMS to your phone |

---

## Try it without a phone or API key

`backend/demo.py` runs the **real backend** end-to-end with a simulated caller —
real FastAPI routes, real TwiML, real SQLite persistence, real companion API.
Only the model replies and Twilio's SMS send are stubbed so it runs offline
(set `ANTHROPIC_API_KEY` to use the real model instead).

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python demo.py
```

It prints the incoming call, the agent's spoken greeting and conversation, the
stored call record + transcript, and the SMS that would be texted to you.

## Setup

### 1. Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then fill in the values
uvicorn app.main:app --reload --port 8000
```

Fill `.env`:
- `ANTHROPIC_API_KEY` — from the Anthropic Console. Model defaults to
  `claude-opus-4-8`; set `CLAUDE_MODEL=claude-haiku-4-5` if you want lower
  per-turn latency on live calls.
- `TWILIO_*` — your Twilio account SID, auth token, and the Twilio number.
- `PUBLIC_BASE_URL` — a public HTTPS URL for this server. Locally, run
  `ngrok http 8000` and use the `https://…ngrok…` URL. In production, your
  deployed host.
- `APP_API_KEY` — a long random string; you'll paste it into the iPhone app.

### 2. Twilio number

1. Buy a voice-capable phone number in the Twilio Console.
2. Under the number's **Voice configuration**:
   - **A call comes in** → Webhook → `POST {PUBLIC_BASE_URL}/twilio/voice`
   - **Call status changes** → `POST {PUBLIC_BASE_URL}/twilio/status`

### 3. Forward your iPhone to the Twilio number

Use your carrier's **conditional** call forwarding so only *unanswered* calls go
to the agent (you still take the calls you want). On most US carriers, dial:

| Condition | Code (replace `+1NUMBER` with your Twilio number) |
|---|---|
| When unanswered | `*61*+1NUMBER#` then call |
| When busy | `*67*+1NUMBER#` then call |
| When unreachable | `*62*+1NUMBER#` then call |

To forward **every** call unconditionally: `**21*+1NUMBER#`. To cancel: `#21#`.
Codes vary by carrier — check yours. (iOS Settings → Phone → Call Forwarding
only does *unconditional* forwarding.)

### 4. iPhone companion app

The SwiftUI sources are in `ios/AnsweringAgent/`. To run them:

1. In Xcode: **File → New → Project → iOS App** (SwiftUI, name it `AnsweringAgent`).
2. Delete the generated `ContentView.swift` and the app entry file, then drag in
   every file from `ios/AnsweringAgent/` (keep the `Models/`, `Networking/`,
   `Views/` groups).
3. Build and run on your device or the simulator.
4. On first launch, enter your `PUBLIC_BASE_URL` and the `APP_API_KEY`.
5. Open the **Agent** tab, set your name, your phone number for transcripts, and
   the defaults for automated callers. Save.

Now miss a call to your iPhone — the agent answers, talks to the caller, and the
call appears in the **Calls** tab with a summary and the full transcript (and
you get a text).

---

## `deal_agent/` — answering agent for the SB2 / NLP secondary

A separate thing that happens to live in the same repo: an agent that answers
questions about a fund-secondary term sheet — NLP's $35M purchase of Class B
exposure to SB2, through a Singapore feeder and an India fund.

```bash
python -m deal_agent report                                  # the standing analysis
python -m deal_agent ask "is the liqpref actually satisfied?"
python -m deal_agent chat                                    # interactive, keeps context
python -m deal_agent findings --severity high
python -m deal_agent exits --exit Freo:50:900                 # any exit, through the waterfall
python -m deal_agent outcome 180                              # priced for each side
python -m deal_agent doc S8                                   # the source text
```

No numbers are generated by a language model. The document's arithmetic is
reimplemented in `deal_agent/terms.py` and `deal_agent/waterfall.py` — they
reproduce its worked exits to the cent — and the agent is given them as tools, so
it quotes computed figures and cites section ids rather than doing sums in its
head. `deal_agent/findings.py` is the analysis register: fourteen findings, each
checked against the live model, with the two the 27 August revision closed kept as a
record.

With `ANTHROPIC_API_KEY` set it runs Claude with those tools. Without one it falls
back to a deterministic keyword answerer over the same model, and says so — so the
CLI and the tests work offline.

What the analysis found is written up in [`docs/DEAL_ANALYSIS.md`](docs/DEAL_ANALYSIS.md),
and [`docs/presentation/sb2-nlp-flow.html`](docs/presentation/sb2-nlp-flow.html) is a
14-slide walkthrough of the flow for people who need the logic rather than the register
(open it in a browser; arrow keys advance it).
The headline: the document's own arithmetic is sound, but the liqpref repays NLPF
while NLPI funded 90% of the cheque (its own open question, asked twice), and the worked
exits split the buyer's cheque on x1 where the structure says x2 — which now also sets
the pref multiple, since 9.86x is $35M netted against a 1.4% onshore slice. At x2 =
12.6% it should be 8.74x.

```bash
python -m unittest discover -s deal_agent/tests -t .          # 45 tests, no deps
```

---

## Notes, limits, and privacy

- **Latency:** Twilio handles speech-to-text and text-to-speech; Claude generates
  each reply. Expect a short pause per turn. `claude-haiku-4-5` is snappier.
- **Cost:** Twilio per-minute voice + per-message SMS, plus Anthropic tokens per
  turn. All low for personal use; watch them if you scale up.
- **Privacy:** transcripts and recordings of *other people* are involved. Some
  jurisdictions require informing callers they're being recorded/processed — the
  greeting already tells them they've reached an agent. Check your local law.
- **Security:** the companion API is guarded by `APP_API_KEY`; serve the backend
  over HTTPS and consider enabling Twilio request signature validation before
  exposing it publicly.

See `docs/ARCHITECTURE.md` for a deeper walkthrough.
