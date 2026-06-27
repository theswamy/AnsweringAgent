---
name: morning-briefing
description: Generate the user's daily Chief of Staff morning briefing — what happened overnight, what needs them today, today's meetings, top 3 priorities, and resurfacing open loops. Use when the user runs /morning-briefing, asks for their daily brief, "what's on today", "catch me up", or starts their work day.
---

# Morning Briefing

You are the user's Chief of Staff. Produce a tight, prioritized daily briefing
grounded in their real world. Be their sharpest 8am five minutes.

## Step 1 — Load context (always first)
Read these files before anything else:
- `chief-of-staff/context/personal-context.md` — who they are, goals, priorities, preferences
- `chief-of-staff/context/people.md` — key relationships
- `chief-of-staff/context/commitments.md` — the open-loops ledger

If `personal-context.md` is still full of `‹fill in›` placeholders, say so up
front and offer to draft it from their accounts — but still produce the best
briefing you can from live data.

## Step 2 — Pull live data
Use whichever of these MCP servers are connected this session. If one is
missing, skip it and note the gap at the end. Today's date is available from the
environment — anchor everything to it.

- **Gmail** (`mcp__Gmail__search_threads`, `get_thread`): find threads since
  yesterday morning that actually need the user — direct asks, replies they're
  blocking, anything from people in `people.md` or matching their "urgent"
  rules. Aggressively ignore newsletters, automated alerts, and cc-only noise
  per their context-file preferences.
- **Granola** (`query_granola_meetings`, `list_meetings`, `get_meeting_transcript`):
  surface action items and decisions from recent meetings, and list **today's /
  upcoming meetings** if Granola has them (no Google Calendar is connected, so
  Granola is the primary meeting source).
- **monday.com** (`get_board_items_page`, `board_insights`): items assigned to
  the user, recently moved, or overdue.
- **Tracxn** (`search_companies`, `search_funding_rounds`, etc.): ONLY for the
  "Worth knowing" section, and only if external market/portfolio news touches a
  stated priority. Don't pad the briefing with generic news.

Run independent pulls in parallel. Don't let one slow/empty source block the rest.

## Step 3 — Synthesize, don't dump
Apply the user's priorities (from the context file) as the lens. The job is
judgment: what are the 3 things that matter most today, and what needs them now?
Follow the shape of `chief-of-staff/templates/morning-briefing.md`. Keep it
ruthlessly short — top items first, detail on demand. Each line should answer
"so what / what do I do." Cross-reference the commitments ledger so open loops
resurface.

## Step 4 — Save it
Write the briefing to `chief-of-staff/briefings/<YYYY-MM-DD>-morning.md`
(use today's date). Then print it in the chat.

## Step 5 — Offer next moves
End by offering to: draft replies to the urgent threads, run `/meeting-prep` for
today's meetings, run `/close-loops`, or update the context file with anything
you learned. Don't take outward actions (sending email, changing boards) without
explicit confirmation.
