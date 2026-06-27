# Automating your Chief of Staff

The commands work great on demand. But the real magic of a chief of staff is
that it happens *to* you — the briefing is waiting when you wake up. Here's how
to put each pillar on a schedule. All of this is opt-in; nothing runs
automatically until you set it up.

## Option A — Claude Code scheduled tasks (recommended)

Claude Code on the web can schedule a session to run on a cron. To turn on a
daily morning briefing, just tell me in a session:

> "Schedule my morning briefing every weekday at 7:30am IST."

I'll create a cron task that opens a session in this repo and runs
`/morning-briefing`. The briefing lands in `chief-of-staff/briefings/` (and, if
you ask, gets emailed to you — see below). Useful cadences:

| Pillar | Suggested schedule |
|---|---|
| `/morning-briefing` | Every weekday, ~7:30am your time |
| `/close-loops` | Twice a week (e.g. Mon & Thu mornings) |
| `/weekly-review` | Friday afternoon or Sunday evening |
| `/meeting-prep` | 30–60 min before meetings (or batch each morning) |

To change or stop a schedule, just ask ("move my briefing to 8am", "pause the
weekly review"). I manage the cron entries for you.

> Note on timing: cron schedules here are typically expressed in UTC. Tell me
> your time zone and I'll convert (e.g. 7:30am IST = 02:00 UTC).

## Option B — Email the briefing to yourself

The briefing is most useful in your inbox. With Gmail connected, I can, as the
last step of the scheduled run, **create a draft** (or send, if you prefer) to
sanjay@primevp.in with the briefing as the body. Say:

> "After the morning briefing, email it to me."

Default is a **draft** so you stay in control; switch to auto-send only once
you trust the output. (Sending email is an outward action — I'll confirm the
behavior with you before turning on auto-send.)

## Option C — Save to Google Drive

If you'd rather read briefings in Drive than in the repo, I can also write each
briefing to a Drive folder via the Google Drive MCP (`create_file`). Say "also
save my briefings to a Drive folder called Chief of Staff."

## What runs unattended needs connected accounts

A scheduled run only sees the MCP servers that are connected for automated
sessions. If a source isn't available in an unattended run, the briefing simply
notes what it skipped — it won't fail. If your morning briefings start coming
back thin, check that Gmail / Granola / monday / Tracxn are connected for
scheduled sessions, not just interactive ones.

## Privacy & control

- Read commands never modify your inboxes or boards.
- The only files written are inside `chief-of-staff/`.
- No email is ever sent without you explicitly enabling it.
- You can pause or delete any schedule at any time — just ask.
