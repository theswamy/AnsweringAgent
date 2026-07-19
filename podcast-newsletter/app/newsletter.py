"""Assemble and render the daily newsletter.

Two things go in every issue:

1. **Deep dives** — for each show you follow, the next episode in its back
   catalogue, summarized in full. Each day we step one episode older, so over
   time you work through a show's history "one prior episode a day". Episodes we
   have already featured are skipped via the sent-episode dedupe.

2. **Topic charts** — for each topic you enabled, today's Apple Podcasts top-N,
   each linking to the source so you can go listen.

The rendered HTML is a self-contained, inline-styled email that also reads fine
as a saved web page (the web UI serves it back from the archive).
"""
from __future__ import annotations

import html as _html
from dataclasses import dataclass, field
from datetime import date

from . import db
from .config import get_settings
from .podcasts import Episode, Podcast, fetch_episodes, top_podcasts
from .summarize import EpisodeSummary, _strip_html, summarize_episode


@dataclass
class DeepDive:
    show_title: str
    apple_url: str | None
    episode: Episode
    summary: EpisodeSummary


@dataclass
class ChartRow:
    rank: int
    podcast: Podcast


@dataclass
class ChartSection:
    topic: str
    rows: list[ChartRow]


@dataclass
class Newsletter:
    for_date: date
    subject: str
    deep_dives: list[DeepDive] = field(default_factory=list)
    charts: list[ChartSection] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def html(self) -> str:
        return render_html(self)


async def _next_backcatalog_episode(show: dict) -> tuple[Episode, int] | None:
    """The first not-yet-sent episode at or below the show's cursor, with its index."""
    episodes = await fetch_episodes(show["feed_url"])
    if not episodes:
        return None
    idx = max(0, int(show["cursor"]))
    while idx < len(episodes):
        ep = episodes[idx]
        if not db.already_sent(show["id"], ep.guid):
            return ep, idx
        idx += 1
    return None


async def build_newsletter(for_date: date | None = None) -> Newsletter:
    """Gather today's content, writing dedupe/cursor state as a side effect."""
    settings = get_settings()
    for_date = for_date or date.today()
    issue = Newsletter(for_date=for_date, subject=f"🎧 Podcast Digest — {for_date:%A, %b %-d}")

    # 1) Deep dives from followed shows' back catalogues.
    for show in db.list_shows():
        found = await _next_backcatalog_episode(show)
        if not found:
            issue.notes.append(f"No new back-catalogue episode for {show['title']} today.")
            continue
        episode, idx = found
        summary = summarize_episode(show["title"], episode)
        issue.deep_dives.append(
            DeepDive(
                show_title=show["title"],
                apple_url=show.get("apple_url"),
                episode=episode,
                summary=summary,
            )
        )
        db.mark_sent(show["id"], episode.guid)
        db.set_cursor(show["id"], idx + 1)

    # 2) Topic charts.
    for topic in db.list_topics(enabled_only=True):
        try:
            shows = await top_podcasts(int(topic["genre_id"]), settings.country, settings.top_n)
        except Exception:  # a flaky chart fetch shouldn't sink the whole issue
            issue.notes.append(f"Could not load the {topic['name']} chart today.")
            continue
        rows = [ChartRow(rank=i + 1, podcast=p) for i, p in enumerate(shows)]
        issue.charts.append(ChartSection(topic=topic["name"], rows=rows))

    return issue


# --------------------------------------------------------------------------- #
# Rendering                                                                    #
# --------------------------------------------------------------------------- #

_STYLE = """
body{margin:0;background:#f4f4f7;font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:#1c1c28;}
.wrap{max-width:640px;margin:0 auto;padding:24px 16px;}
.card{background:#ffffff;border-radius:14px;padding:24px;margin-bottom:20px;box-shadow:0 1px 3px rgba(20,20,40,.06);}
h1{font-size:24px;margin:0 0 4px;}
.date{color:#6b6b7b;font-size:14px;margin-bottom:20px;}
h2{font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:#7a5cff;margin:0 0 14px;}
h3{font-size:18px;margin:0 0 6px;}
.meta{color:#8a8a99;font-size:13px;margin:0 0 12px;}
.summary{font-size:15px;line-height:1.6;margin:0 0 12px;}
ul{margin:0 0 12px;padding-left:20px;}
li{font-size:14px;line-height:1.5;margin-bottom:4px;}
.why{font-size:14px;font-style:italic;color:#55556a;margin:0 0 14px;}
a.btn{display:inline-block;background:#7a5cff;color:#fff!important;text-decoration:none;font-size:14px;font-weight:600;padding:9px 16px;border-radius:8px;}
.rank{display:inline-block;width:26px;color:#7a5cff;font-weight:700;}
.chartrow{padding:10px 0;border-bottom:1px solid #eee;font-size:15px;}
.chartrow:last-child{border-bottom:none;}
.chartrow a{color:#1c1c28;text-decoration:none;font-weight:600;}
.author{color:#8a8a99;font-size:13px;}
.foot{color:#9a9aa8;font-size:12px;text-align:center;padding:8px 0 24px;}
.notes{color:#9a9aa8;font-size:12px;}
"""


def _esc(text: str) -> str:
    return _html.escape(text or "")


def _deep_dive_html(dd: DeepDive) -> str:
    ep = dd.episode
    listen_url = ep.link or dd.apple_url or ep.audio_url or "#"
    when = f"{ep.published:%b %-d, %Y}" if ep.published else "date unknown"
    points = ""
    if dd.summary.key_points:
        items = "".join(f"<li>{_esc(p)}</li>" for p in dd.summary.key_points)
        points = f"<ul>{items}</ul>"
    why = f'<p class="why">{_esc(dd.summary.why_listen)}</p>' if dd.summary.why_listen else ""
    return f"""
    <div class="card">
      <h2>Deep dive · {_esc(dd.show_title)}</h2>
      <h3>{_esc(ep.title)}</h3>
      <p class="meta">{_esc(when)}{(' · ' + _esc(ep.duration)) if ep.duration else ''}</p>
      <p class="summary">{_esc(dd.summary.summary)}</p>
      {points}
      {why}
      <a class="btn" href="{_esc(listen_url)}">Listen →</a>
    </div>
    """


def _chart_html(section: ChartSection) -> str:
    rows = []
    for row in section.rows:
        p = row.podcast
        url = p.apple_url or p.feed_url or "#"
        desc = _strip_html(p.description)
        desc = (desc[:110] + "…") if len(desc) > 110 else desc
        author = f' · <span class="author">{_esc(p.author)}</span>' if p.author else ""
        blurb = f'<div class="author">{_esc(desc)}</div>' if desc and desc != p.title else ""
        rows.append(
            f'<div class="chartrow"><span class="rank">{row.rank}</span>'
            f'<a href="{_esc(url)}">{_esc(p.title)}</a>{author}{blurb}</div>'
        )
    return f"""
    <div class="card">
      <h2>Top {len(section.rows)} · {_esc(section.topic)}</h2>
      {''.join(rows)}
    </div>
    """


def render_html(issue: Newsletter) -> str:
    body_parts: list[str] = []
    if issue.deep_dives:
        body_parts.extend(_deep_dive_html(dd) for dd in issue.deep_dives)
    if issue.charts:
        body_parts.extend(_chart_html(sec) for sec in issue.charts)
    if not issue.deep_dives and not issue.charts:
        body_parts.append(
            '<div class="card"><p class="summary">No podcasts to report today. '
            "Add some topics or shows to your digest.</p></div>"
        )
    if issue.notes:
        notes = '<p class="notes">' + "<br>".join(_esc(n) for n in issue.notes) + "</p>"
    else:
        notes = '<p class="notes">That&rsquo;s everything for today.</p>'

    return f"""<!doctype html>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>{_STYLE}</style></head>
<body><div class="wrap">
  <h1>🎧 Podcast Digest</h1>
  <div class="date">{issue.for_date:%A, %B %-d, %Y}</div>
  {''.join(body_parts)}
  <div class="card">{notes}</div>
  <div class="foot">Built for you by Podcast Digest · one prior episode a day.</div>
</div></body></html>"""
