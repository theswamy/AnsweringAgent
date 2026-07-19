# 🎧 Podcast Digest

A small webapp that emails you **one daily podcast newsletter**:

- **Top charts by topic** — for each topic you enable (Technology, Business,
  News, … any Apple Podcasts genre), today's **top 10** shows, each linking to
  the source so you can go listen.
- **A deep dive a day** — for every show you follow, a full summary of the next
  episode in its back catalogue. Each day it steps **one prior episode** older,
  so over time you work through a show's history one episode at a time.
- **Delivered by email** every morning, with a source link on everything.

There's a little web control panel to pick your topics, add specific shows, run a
send on demand, and read past issues.

---

## How it fits together

```
 Apple Podcasts charts ─┐
 iTunes lookup / search ─┼─▶  podcasts.py   (find shows + read their RSS feeds)
 each show's RSS feed  ─┘          │
                                   ▼
                              newsletter.py  (assemble: deep dives + topic charts)
                                   │  episode show notes
                                   ▼
                               summarize.py  (Claude writes the episode summaries)
                                   │  HTML
                                   ▼
                                emailer.py   (SMTP send — or save to ./outbox in dry-run)
                                   ▲
                                   │
        Web control panel  ──▶  main.py (FastAPI)  ──▶  scheduler.py (daily at SEND_HOUR)
        (topics, shows, run,        │
         archive)             SQLite (db.py): topics, followed shows,
                              back-catalogue cursor, sent-episode dedupe, archive
```

**Why Apple Podcasts?** Its charts and lookup/search APIs are free and need no
key, and every show exposes an RSS feed we read episodes from. Apple doesn't
publish numeric star ratings via a public API, so the per-genre **top charts** —
which Apple ranks largely by popularity and ratings — are the best available
proxy for "top rated on this topic".

**Why summarize from show notes?** No audio pipeline, cheap to run daily, and
show notes are what publishers write to describe an episode. The prompt tells
Claude to stay honest when notes are thin rather than invent detail. (Swapping in
real transcript summarization later is just a change to `summarize.py`.)

---

## Quick start

**Easiest — the control panel on your laptop.** Double-click **`run.command`**
(macOS) or **`run.bat`** (Windows). The first run sets everything up, then your
browser opens to <http://localhost:8000> where you can pick topics, add
podcasts, manage recipients, preview an issue, and read the archive. Requires
[Python 3.11+](https://www.python.org/downloads/) installed.

**From a terminal:**

```bash
cd podcast-newsletter
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# See a sample issue immediately — no keys, no network:
python demo.py            # writes & opens ./outbox/digest-*.html

# Run the control panel:
cp .env.example .env      # fill in what you have (all optional to start)
uvicorn app.main:app --reload
# open http://localhost:8000
```

With **no configuration at all** the app still runs end to end: it sources real
podcasts, writes summaries from show notes (no Anthropic key needed), and saves
each issue to `./outbox/` instead of emailing (dry-run). Add keys to upgrade each
stage.

---

## Configuration (`.env`)

| Variable | What it does |
|---|---|
| `ANTHROPIC_API_KEY` | Enables Claude-written summaries. Without it, the digest echoes trimmed show notes. |
| `CLAUDE_MODEL` | Defaults to `claude-opus-4-8`; `claude-haiku-4-5` is cheaper for daily sends. |
| `SMTP_HOST` / `SMTP_PORT` / `SMTP_USERNAME` / `SMTP_PASSWORD` / `SMTP_USE_TLS` | Email relay. Works with a Gmail app password, SendGrid, SES, Postmark, etc. |
| `EMAIL_FROM` | The sending account (e.g. a generic `digest@yourdomain`). |
| `EMAIL_TO` | Seeds the **first** recipient on first run. After that, manage the whole recipient list in the web UI — the digest is Bcc'd to everyone on it. |
| `DRY_RUN` | `true` (or blank SMTP) → save to `./outbox/` instead of emailing. |
| `COUNTRY` | Apple storefront for charts/search (`us`, `in`, …). |
| `TOP_N` | Shows per topic chart (default 10). |
| `SUMMARIZE_TOP_LIST` | Reserved flag for adding one-line takes to chart rows (off by default to keep token cost low). |
| `SEND_HOUR` / `TIMEZONE` | When the built-in scheduler sends each day. |
| `DATABASE_PATH` | SQLite file location. |

Gmail: create an app password at <https://myaccount.google.com/apppasswords>, set
`SMTP_HOST=smtp.gmail.com`, `SMTP_PORT=587`, username = your address, password =
the app password.

You don't have to edit `.env` at all for local use: open the control panel and
fill in the **Email settings** panel (sender, SMTP host/port, username, app
password), then hit **Send test email** to confirm it works. Those values are
saved in the local database. Environment variables, when present, take
precedence — that's how the cloud/CI path keeps secrets in env instead of the DB.

---

## Sending daily

Two options:

1. **Built-in scheduler.** Just keep `uvicorn app.main:app` running — it fires
   the send once a day at `SEND_HOUR` in your `TIMEZONE`.
2. **External scheduler.** Run the one-shot command from cron / GitHub Actions /
   a k8s CronJob and let it own the timing:
   ```bash
   python -m app.cli run
   ```

### GitHub Actions (no server needed)

A ready-made workflow lives at [`.github/workflows/podcast-digest.yml`](../.github/workflows/podcast-digest.yml).
It runs `python -m app.cli run` daily and persists the digest state (back-catalogue
cursor + dedupe) across runs via the Actions cache.

To turn it on:

1. Add repository **secrets** (Settings → Secrets and variables → Actions):
   `SMTP_HOST`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `EMAIL_FROM`, and optionally
   `ANTHROPIC_API_KEY`. Optional **variables**: `EMAIL_TO`, `SMTP_PORT`, `COUNTRY`,
   `TOP_N`.
2. **Merge the workflow to your repository's default branch** — GitHub only runs
   `schedule:` triggers from the default branch. Until then, use the **Run
   workflow** button (a `workflow_dispatch` with an optional dry-run toggle) to
   test from any branch.

Caveat: an unused Actions cache is evicted after ~7 days. Running daily keeps it
warm; a long pause resets the back-catalogue walk (harmless — it just re-features
recent episodes). If you want durable state, run option 1 or 2 on a host with a
persistent disk instead.

---

## API

| Method & path | Purpose |
|---|---|
| `GET /` | Web control panel |
| `GET /api/genres` | Apple genre catalogue for the topic picker |
| `GET/POST /api/topics`, `POST /api/topics/{id}/toggle`, `DELETE /api/topics/{id}` | Manage topics |
| `GET/POST /api/shows`, `POST /api/shows/resolve`, `DELETE /api/shows/{id}` | Manage followed shows (add by search text, Apple Podcasts link, iTunes id, or RSS URL) |
| `POST /api/run` | Build + deliver today's issue now |
| `GET/POST /api/email-settings`, `POST /api/email-settings/test` | View/save the sender + SMTP config from the UI; send a test email |
| `GET/POST /api/recipients`, `DELETE /api/recipients/{id}` | Manage who the digest is emailed to |
| `GET /api/newsletters`, `GET /api/newsletters/{id}` | Archive list and one issue's HTML |

### Recipients / your team

The digest is Bcc'd to everyone on the recipient list, so addresses stay private
as the list grows. Start solo and add colleagues from the **Recipients** section
of the control panel. Use a generic sending account (e.g. `digest@yourdomain`) as
`EMAIL_FROM` so the newsletter reads as coming from the team, not a person.

---

## Layout

```
podcast-newsletter/
├── app/
│   ├── config.py       env-driven settings
│   ├── podcasts.py     Apple charts + iTunes lookup/search + RSS parsing
│   ├── summarize.py    Claude episode summaries (falls back to show notes)
│   ├── newsletter.py   assemble the issue + render the HTML email
│   ├── emailer.py      SMTP send / dry-run to ./outbox
│   ├── db.py           SQLite: topics, shows, back-catalogue cursor, dedupe, archive
│   ├── runner.py       build → archive → deliver
│   ├── scheduler.py    in-process daily job
│   ├── cli.py          `python -m app.cli run`
│   └── main.py         FastAPI web UI + JSON API
├── static/index.html   control panel (vanilla JS)
├── run.command         double-click launcher (macOS/Linux)
├── run.bat             double-click launcher (Windows)
├── demo.py             offline end-to-end sample (no keys, no network)
├── requirements.txt
└── .env.example
```

## Notes & limits

- **Ratings:** the per-topic ranking is Apple's chart order, the best public
  proxy for "top rated"; Apple doesn't expose star ratings via a public API.
- **Summaries** are built from RSS show notes, not audio transcripts.
- The bundled scheduler is a single in-process loop — fine for one recipient. For
  a hardened deployment, disable it and drive `python -m app.cli run` from a real
  scheduler.
