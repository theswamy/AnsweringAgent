"""Orchestration: build today's issue, archive it, and deliver it."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from . import db, emailer
from .newsletter import build_newsletter


@dataclass
class RunResult:
    newsletter_id: int
    subject: str
    deep_dives: int
    topics: int
    delivery: str


async def run_daily(for_date: date | None = None) -> RunResult:
    """The full daily job. Safe to call manually (web UI) or from the scheduler."""
    issue = await build_newsletter(for_date)
    status = emailer.deliver(issue.subject, issue.html, issue.for_date)
    sent = status.startswith("Emailed")
    nid = db.save_newsletter(issue.for_date.isoformat(), issue.subject, issue.html, sent)
    return RunResult(
        newsletter_id=nid,
        subject=issue.subject,
        deep_dives=len(issue.deep_dives),
        topics=len(issue.charts),
        delivery=status,
    )
