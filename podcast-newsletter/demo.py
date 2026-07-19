"""Offline demo — renders a sample digest with no network calls and no API key.

    python demo.py

Writes ./outbox/digest-demo.html and opens it in your browser if it can. This
exercises the real newsletter assembly + rendering + delivery (dry-run) path
using canned fixtures, so you can see the output before wiring up sourcing,
Anthropic, or SMTP.
"""
from __future__ import annotations

import os
import webbrowser
from datetime import date, datetime, timezone

# Force dry-run so emailer.deliver() writes a file instead of trying SMTP.
os.environ.setdefault("DRY_RUN", "true")

from app import emailer  # noqa: E402
from app.newsletter import (  # noqa: E402
    ChartRow,
    ChartSection,
    DeepDive,
    Newsletter,
)
from app.podcasts import Episode, Podcast  # noqa: E402
from app.summarize import EpisodeSummary  # noqa: E402

_FIXTURE_EPISODE = Episode(
    guid="demo-guid-42",
    title="Episode 42 — Scaling a Seed-Stage Company Without Losing the Plot",
    summary="A candid conversation with a founder-turned-operator on hiring your first "
    "ten people, saying no to the wrong customers, and keeping runway honest.",
    published=datetime(2026, 3, 4, tzinfo=timezone.utc),
    link="https://example.com/podcast/ep42",
    duration="48:11",
)

_FIXTURE_SUMMARY = EpisodeSummary(
    summary="The host sits down with an early-stage operator to unpack the messy middle of "
    "company building. They dig into how to hire your first ten people for slope over "
    "polish, why premature enterprise deals can quietly bend a roadmap, and a simple habit "
    "for keeping runway math honest when optimism runs high.",
    key_points=[
        "Hire for trajectory, not just current skill",
        "Saying no to the wrong customer protects the roadmap",
        "Revisit runway assumptions monthly, out loud",
    ],
    why_listen="Best for first-time founders navigating the jump from prototype to team.",
)


def _demo_newsletter() -> Newsletter:
    issue = Newsletter(
        for_date=date(2026, 3, 5),
        subject="🎧 Podcast Digest — Thursday, Mar 5",
    )
    issue.deep_dives.append(
        DeepDive(
            show_title="The Operators",
            apple_url="https://podcasts.apple.com/us/podcast/the-operators/id100",
            episode=_FIXTURE_EPISODE,
            summary=_FIXTURE_SUMMARY,
        )
    )
    tech = ChartSection(
        topic="Technology",
        rows=[
            ChartRow(1, Podcast(itunes_id="1", title="Lex Fridman Podcast", author="Lex Fridman",
                                apple_url="https://podcasts.apple.com/us/podcast/id1",
                                description="Conversations about AI, science, and the human condition.")),
            ChartRow(2, Podcast(itunes_id="2", title="Acquired", author="Ben & David",
                                apple_url="https://podcasts.apple.com/us/podcast/id2",
                                description="The stories and strategies behind great companies.")),
            ChartRow(3, Podcast(itunes_id="3", title="Hard Fork", author="The New York Times",
                                apple_url="https://podcasts.apple.com/us/podcast/id3",
                                description="The week in tech, made sense of.")),
        ],
    )
    business = ChartSection(
        topic="Business",
        rows=[
            ChartRow(1, Podcast(itunes_id="4", title="How I Built This", author="Guy Raz",
                                apple_url="https://podcasts.apple.com/us/podcast/id4",
                                description="Founders on the companies they built.")),
            ChartRow(2, Podcast(itunes_id="5", title="The Twenty Minute VC", author="Harry Stebbings",
                                apple_url="https://podcasts.apple.com/us/podcast/id5",
                                description="Venture capital, founders, and fundraising.")),
        ],
    )
    issue.charts.extend([tech, business])
    return issue


def main() -> None:
    issue = _demo_newsletter()
    status = emailer.deliver(issue.subject, issue.html, issue.for_date)
    path = os.path.abspath(os.path.join("outbox", f"digest-{issue.for_date.isoformat()}.html"))
    print("Subject:", issue.subject)
    print(f"Deep dives: {len(issue.deep_dives)} · Topic charts: {len(issue.charts)}")
    print(status)
    if os.path.exists(path):
        print("Open:", path)
        try:
            webbrowser.open("file://" + path)
        except Exception:
            pass


if __name__ == "__main__":
    main()
