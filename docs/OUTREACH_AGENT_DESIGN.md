# Founder Outreach Agent — Design

A deal-sourcing agent for Prime VP. Given the companies already curated on the
**MicroVC Sourcing** monday.com board, it finds the founder's email, sends a
personalized first-touch on Sanjay's behalf, runs the reply dialog, and books a
30-minute intro call — advancing each company through the board's outreach
pipeline as it goes.

This is a design document for review. **No production code is written yet.**

---

## 1. Principles (decided)

1. **monday.com is the System of Record.** The agent invents no new database.
   It reads candidates from the board and writes every state change and every
   message back onto the company's item. If it isn't on the board, it didn't
   happen.
2. **Gmail is only transport.** Outbound and inbound email flow through a
   **dedicated send-from address** used for nothing else. Each message is
   mirrored to the monday item as an update, so the full conversation is visible
   on the board without opening an inbox.
3. **Human-approved first touch, autonomous replies.** Every first email waits
   for Sanjay's approval (at least until the tone is trusted). Once a founder
   replies, the agent handles the back-and-forth on its own — but escalates to
   Sanjay on anything sensitive (see §7).
4. **Tight qualification.** Only companies backed by the target micro-VCs, and
   only those at or before Series A. Anything later is passed, not pursued.

---

## 2. The board is the spine

Board: **MicroVC Sourcing — 2026-04** (`18410878634`, Main workspace). ~981
companies, grouped by micro-VC. The agent uses these columns:

| Purpose | Column | id | Notes |
|---|---|---|---|
| Company name | Company | `name` | |
| Micro-VC filter | MicroVC (dropdown) + group | `dropdown_mm2wd7b0` | group title is the fund |
| **Pipeline state** | Outreach Status (status) | `color_mm2w2wv` | drives the whole loop |
| Stage gate | Stage | `text_mm2wcv77` | free text |
| Stage gate (backup) | Last Round Type | `text_mm2whw` | e.g. "Seed", "Series A/B" |
| Founder target | Best Founder | `text_mm2ww997` | who we email |
| Founder research | Best Founder LinkedIn | `link_mm2wccf8` | personalization |
| Email domain | Best Founder Domain / Website | `text_mm2wpqc2` / `link_mm2w7w62` | email guessing |
| Personalization | One-Line Description | `long_text_mm2wzcyv` | what they do |
| Personalization | Notes / DD Notes | `long_text_mm2w9kc5` / `long_text_mm2wz8qt` | our prior view |
| Context | Last Round Date / Lead / All Investors | `date_mm2wpxaj` / `text_mm2wjxx5` / `long_text_mm2wyzp2` | |

### Outreach Status is the state machine (`color_mm2w2wv`)

```
To Reach Out  →  Sent  →  Replied  →  Meeting  →  Pitched
      │                                              
      └──────────────►  Pass   (disqualified or declined)
```

The agent only ever picks up items in **To Reach Out**, and moves each one
forward exactly one state at a time, writing the reason for every transition as
a monday update.

---

## 3. Qualification rules (decided)

Applied before any email is drafted:

1. **Micro-VC membership** — the company's group / `MicroVC` value must be in the
   target set. (The board is already scoped to your funds, so this is a
   sanity check, not the primary filter.)
2. **Stage gate** — **skip anything past Series A.** Parse `Stage` and
   `Last Round Type`; if the latest round is Series B or later (B/C/D/E, Growth,
   Late), the company is disqualified.
   - Disqualified → set **Outreach Status = Pass**, and record the reason
     **"Too Late for Prime"** as an update on the item. *(Open item 8.6: use the
     existing `Pass` label + reason note, or add a dedicated
     "Pass — Too Late for Prime" label to the column.)*
3. **Already in flight** — skip anything not in `To Reach Out` (already Sent,
   Replied, Passed, etc.), so re-runs are idempotent.

---

## 4. The pipeline

### Stage A — Select & qualify
Read `To Reach Out` items → apply §3 rules → produce a work list. Disqualified
items are passed immediately with a logged reason.

### Stage B — Resolve founder email
1. Determine the domain from `Best Founder Domain`, else the `Website` column.
2. Generate candidates in priority order:
   `firstname@domain`, `firstname.lastname@domain`, `flastname@domain`,
   `firstnamel@domain`.
3. **Verify before sending** — MX lookup on the domain, then SMTP RCPT probe
   (with graceful handling of catch-all domains, which can't be verified). An
   optional finder API (Hunter/Apollo) can be slotted in here later for higher
   confidence.
4. Record the chosen address + confidence as an update. If nothing verifies,
   set status to a "needs manual email" state (open item 8.6) and skip sending.

### Stage C — Draft the first touch
A personalized email built from: `One-Line Description`, `Stage`, founder
background (from the Best Founder columns + LinkedIn), the backing micro-VC, and
Sanjay's voice/thesis config (§6). Short, specific, non-templated — references
what the company actually does and why Prime VP is a fit.

The draft is posted to the monday item and **held for Sanjay's approval**
(approval mechanism — open item 8.4).

### Stage D — Send & record
On approval, send from the dedicated address → set **Outreach Status = Sent** →
post the sent email as an update with timestamp and message-id. A follow-up
(nudge) is scheduled if no reply (cadence — open item 8.2).

### Stage E — Handle replies
On an inbound reply to a live thread:
1. Mirror the reply onto the monday item; set **Outreach Status = Replied**.
2. Classify intent: interested / wants info / not now / not a fit / sensitive.
3. Draft and (autonomously) send a reply within guardrails, **or escalate** (§7).
4. When the founder is warm, share the **Calendly link** and ask them to grab a
   slot.

### Stage F — Schedule & hand off
On a booking (detection — open item 8.3), set **Outreach Status = Meeting**,
post the confirmed time as an update. The call itself is captured by **Granola**;
no scheduling integration beyond Calendly is required.

---

## 5. Architecture

A small **Python service** (matching the repo's existing FastAPI + `anthropic`
SDK stack), with four integrations and two entry points.

```
                ┌──────────────────────────────────────────┐
                │            Outreach Agent (Python)         │
                │                                            │
  monday.com ◄──┤  SoR adapter   ── read candidates,         │
  (board API)   │                   write status + updates   │
                │                                            │
  Anthropic  ◄──┤  Brain         ── draft / classify /        │
  (Claude)      │                   personalize (structured)  │
                │                                            │
  Gmail      ◄──┤  Mailer        ── send from dedicated addr, │
  (dedicated)   │                   read replies              │
                │                                            │
  Calendly   ◄──┤  Scheduler     ── share link, detect book  │
                └──────────────────────────────────────────┘
     ▲                         ▲
     │ (1) batch run           │ (2) inbound webhook
  "process To Reach Out"    Gmail push / Calendly webhook
```

- **Entry point 1 — batch run.** Walks `To Reach Out`, does Stages A–D, queues
  drafts for approval. Runnable on demand or on a schedule.
- **Entry point 2 — event handler.** Reacts to inbound founder replies and
  Calendly bookings (Stages E–F).
- **The Brain** uses Claude with **structured outputs** (same pattern as
  `backend/app/claude_agent.py`) so every decision returns a predictable JSON
  shape: `{ action, draft_subject, draft_body, intent, escalate, reason }`.

> Note on this environment vs. production: the monday/Gmail **MCP connectors**
> available in this Claude session are ideal for interactive/prototype runs. A
> deployed service talks to the same systems via their **direct APIs**
> (monday GraphQL, Gmail API, Calendly API) with its own credentials. The build
> plan (§9) starts MCP-driven and hardens toward direct APIs.

---

## 6. Voice & personalization config

To sound like Sanjay and not like a bot, the agent needs a small config file:

- Sanjay's 2–3 line bio + Prime VP's thesis / check size / stage focus.
- What makes a company interesting (so the "why I'm reaching out" line is real).
- Tone rules (concise, warm, no hype, Indian founder ecosystem context).
- **2–3 real outreach emails** Sanjay has sent that landed well — the single
  biggest lever on quality. (These can also be pulled from the Gmail Sent
  folder later.)
- Signature + the dedicated address's display name.

---

## 7. Guardrails, autonomy & escalation

- **First touch:** always Sanjay-approved (open item 8.4 picks the mechanism).
- **Replies:** autonomous **except** — escalate to Sanjay when the founder
  raises **terms/valuation/pricing**, asks something the agent can't answer from
  config, expresses **negative sentiment / asks to stop** (→ honor opt-out and
  mark Pass), requests intros/commitments, or when classification confidence is
  low.
- **Never:** make commitments on Prime VP's behalf, quote numbers, or invent
  facts about the fund.
- **Volume cap:** a per-day send ceiling (deliverability, §8) — the batch run
  stops at the cap and resumes next run.
- **Opt-out:** any "not interested / unsubscribe" → stop the thread, set Pass,
  log reason. No further follow-ups.

---

## 8. Deliverability & compliance (needs attention)

A **brand-new sending address has no reputation**, and this is cold outreach —
the fastest way to get filtered to spam or blocklisted is to blast volume on
day one. Recommendations:

- Confirm **SPF, DKIM, DMARC** are set for the sending domain.
- **Warm up**: start at a low daily volume (e.g. 10–20/day) and ramp.
- Verify addresses before sending (Stage B) to keep **bounce rate low** —
  guessed addresses bounce, and bounces wreck reputation.
- Plain-text-ish, no tracking pixels, real signature, easy opt-out.
- Respect the volume cap and per-thread follow-up limit.

---

## 9. Phased build plan

Each phase is independently reviewable; nothing sends without your sign-off
until Phase 4.

- **Phase 0 — Config & scaffolding.** Repo module, secrets/env, target micro-VC
  set, stage-rule parser, voice config skeleton. No side effects.
- **Phase 1 — Read-only qualification (dry run).** Pull `To Reach Out`, apply
  §3, output the qualified list + proposed Pass reasons. **Writes nothing.** You
  eyeball the selection.
- **Phase 2 — Email resolution.** Domain/pattern guessing + verification over
  the qualified list; report hit rate. Still no sends.
- **Phase 3 — Draft generation + approval queue.** Personalized drafts posted to
  monday for approval. Still no sends; you read the drafts on the board.
- **Phase 4 — Send + status writeback.** On approval, send from the dedicated
  address, set `Sent`, log the update. Volume-capped. First real emails.
- **Phase 5 — Reply handling.** Inbound classification, autonomous replies +
  escalation, Calendly share.
- **Phase 6 — Scheduling + close the loop.** Booking detection → `Meeting`;
  follow-up cadence; opt-out handling.

---

## 10. Open items to confirm

1. **Voice config** — send the bio/thesis + 2–3 sample outreach emails (§6).
2. **Follow-up cadence** — how many nudges if no reply, and spacing?
   (Default proposal: 2 follow-ups at +4 and +8 days, then stop.)
3. **Booking detection** — Calendly webhook (cleanest) vs. detecting the Calendly
   confirmation email in the inbox. Which do you have access to set up?
4. **Approval mechanism** — how do you want to approve first-touch drafts?
   Options: a monday status flip (e.g. an "Approve" label) the agent watches;
   a daily digest email you reply to; or a simple review screen.
5. **Dedicated address** — what is it, and is it on `primevp.in` or a separate
   domain? (Determines the warm-up/authentication work in §8.)
6. **Pass labeling** — reuse the existing `Pass` label + reason note, or add a
   dedicated **"Pass — Too Late for Prime"** label to the Outreach Status column?
7. **Send-time voice** — should the first email be signed as Sanjay directly, or
   as "on behalf of Sanjay"? (Affects reply-to and framing.)
