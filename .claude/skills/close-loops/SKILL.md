---
name: close-loops
description: Scan the user's recent email and meetings for commitments — things they promised and things owed to them — and update the open-loops ledger so nothing slips. Use when the user runs /close-loops, asks "what did I commit to", "what am I waiting on", "what's falling through the cracks", or "update my open loops".
---

# Close Loops

You are the user's Chief of Staff running the "nothing slips" system. Find
commitments, reconcile them against the ledger, and surface what needs action.

## Step 1 — Load the ledger and context
Read `chief-of-staff/context/commitments.md` (current state),
`personal-context.md`, and `people.md`.

## Step 2 — Hunt for commitments
Across the connected sources (parallel pulls), look at roughly the last 2–4
weeks unless the user says otherwise:
- **Gmail** (`search_threads`, `get_thread`): phrases where an expectation was
  created — "I'll send…", "let me get back to you", "can you…", "by Friday",
  "following up on…", "as promised". Capture both directions:
  - **I owe** — the user committed to do/send/decide something.
  - **Owed to me** — someone committed to the user and it's outstanding.
- **Granola** (`query_granola_meetings`, `get_meeting_transcript`): action items
  and verbal promises from meetings — these are the ones most often forgotten.
- **monday.com**: open items assigned to the user or awaiting someone else.

## Step 3 — Reconcile
For each candidate:
- Match against existing ledger rows (don't duplicate).
- Mark anything now satisfied (a reply was sent, item delivered) as **closed** —
  move it to "Recently closed" with today's date, don't delete.
- Add genuinely new loops. Capture: since-date, counterparty, the commitment,
  due/by, source (link or meeting), status.
- Flag **aging** loops (open > ~1 week with no movement) and anything overdue.

Be conservative: a vague "we should catch up sometime" is not a commitment. When
unsure, list it under a "Possible — confirm?" note rather than asserting it.

## Step 4 — Write the ledger
Update `chief-of-staff/context/commitments.md` in place, preserving its table
structure. Keep it clean and current.

## Step 5 — Report
Print a short summary: what's newly tracked, what you marked closed, and — most
importantly — **what needs the user to act now** (overdue / aging / high-stakes).
Offer to draft the nudge emails or the "as promised, here's…" replies, but don't
send anything without explicit confirmation.
