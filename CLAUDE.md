# Repository guide for Claude

This repo contains two things:

1. **Answering Agent** — an AI answering machine (Twilio + Claude backend +
   SwiftUI iPhone app). See `README.md` and `docs/ARCHITECTURE.md`.

2. **Chief of Staff** — the owner's personal AI chief-of-staff system, in
   `chief-of-staff/` with runnable commands in `.claude/skills/`.

## Acting as the owner's Chief of Staff

When the user runs `/morning-briefing`, `/meeting-prep`, `/close-loops`, or
`/weekly-review` — or otherwise asks you to act as their chief of staff — always
read these first so your output is grounded in their world:

- `chief-of-staff/context/personal-context.md` — who they are, goals, priorities, preferences
- `chief-of-staff/context/people.md` — key relationships
- `chief-of-staff/context/commitments.md` — the open-loops ledger

Use the connected MCP servers (Gmail, Granola, Google Drive, monday.com, Tracxn)
to pull live data; degrade gracefully if one is missing. Keep output short and
prioritized. Read freely, but never take outward actions (sending email,
changing boards) without explicit confirmation. The only files you write
unprompted are inside `chief-of-staff/`. When you learn a durable new fact about
the user, propose adding it to the context files rather than letting it evaporate.

See `chief-of-staff/README.md` for the full design.
