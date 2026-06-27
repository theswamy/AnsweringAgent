# 🧑‍💼 Chief of Staff

Your personal AI Chief of Staff, built for Claude Code. It does the work a great
human chief of staff does — keeps your context, prepares you for the day,
preps you before meetings, makes sure nothing you committed to slips, and helps
you reflect weekly — by reading from the accounts you've already connected
(Gmail, Granola, Google Drive, monday.com, Tracxn).

> Inspired by Andreas Horn's "AI Chief of Staff" pattern: spend a little time
> once, then get a daily briefing, pre-meeting briefs, a personal context file,
> a loop-closing system for commitments, and a weekly review — automatically.

---

## The five pillars

| Command | What it does | Reads from |
|---|---|---|
| `/morning-briefing` | Your daily brief: what happened overnight, what needs you today, the day's meetings, and your top 3 priorities. | Gmail, Granola, monday.com, Tracxn |
| `/meeting-prep` | A focused brief before a specific meeting: who you're meeting, history, open threads, and a suggested agenda. | Granola, Gmail, Tracxn |
| `/close-loops` | Scans for commitments — things you promised and things owed to you — and updates your open-loops ledger so nothing slips. | Gmail, Granola, monday.com |
| `/weekly-review` | A Friday/Sunday retrospective: what moved, what stalled, what to focus on next week, plus one coaching observation. | Everything + your ledger |
| *(context file)* | `context/personal-context.md` — the always-on memory every command reads first so the output is about *your* world, not generic. | You (edit it) |

---

## Setup (about 15 minutes, once)

1. **Fill in your context file.** Open
   [`context/personal-context.md`](context/personal-context.md) and replace the
   placeholders with your real role, goals, key people, and preferences. This is
   the single most important step — every command reads it first. (You can also
   run `/morning-briefing` and ask me to help draft it from your live accounts.)

2. **Confirm your accounts are connected.** These commands use the MCP servers
   already configured for your sessions: **Gmail**, **Granola**, **Google
   Drive**, **monday.com**, and **Tracxn**. If one isn't connected in a given
   session, the command degrades gracefully and tells you what it skipped.

3. **Run it.** In any Claude Code session in this repo:
   ```
   /morning-briefing
   ```

4. **(Optional) Automate it.** See [`AUTOMATION.md`](AUTOMATION.md) to have the
   morning briefing run on a schedule and land in `briefings/` (and optionally
   your inbox) without you lifting a finger. See [`AUTOMATION.md`](AUTOMATION.md).

---

## How it stays *yours*

- **Memory lives in `context/`** — `personal-context.md` (who you are),
  `people.md` (your key relationships), and `commitments.md` (the open-loops
  ledger the system maintains for you). Everything the assistant generates is
  grounded in these files.
- **Briefings are saved** to `briefings/YYYY-MM-DD-*.md` so you have a searchable
  history of what mattered each day.
- **You stay in control.** Nothing is sent to anyone unless you turn on the
  email step in `AUTOMATION.md`. Read commands never modify your inboxes or
  boards; the only thing the system writes is files inside this folder.

---

## Folder layout

```
chief-of-staff/
├── README.md                 ← you are here
├── AUTOMATION.md             ← optional scheduled briefings
├── context/
│   ├── personal-context.md   ← who you are, goals, preferences (EDIT THIS)
│   ├── people.md             ← key relationships & how you work with them
│   └── commitments.md        ← open-loops ledger (auto-maintained)
├── templates/
│   ├── morning-briefing.md   ← output shape for the daily brief
│   └── weekly-review.md      ← output shape for the weekly retro
└── briefings/                ← generated briefings land here
```

The runnable commands live in `.claude/skills/` at the repo root
(`morning-briefing`, `meeting-prep`, `close-loops`, `weekly-review`).
