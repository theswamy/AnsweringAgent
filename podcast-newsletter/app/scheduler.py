"""A tiny in-process daily scheduler.

Runs :func:`app.runner.run_daily` once per day at ``send_hour`` in the configured
timezone. It's deliberately simple — a background asyncio task that sleeps until
the next occurrence — so the whole app is a single process with no cron or
external worker. For a hardened deployment you'd instead disable this and drive
`POST /api/run` from a real scheduler (system cron, GitHub Actions, k8s CronJob).
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from .config import get_settings
from .runner import run_daily

log = logging.getLogger("podcast_digest.scheduler")


def _seconds_until_next_run() -> float:
    s = get_settings()
    tz = ZoneInfo(s.timezone)
    now = datetime.now(tz)
    target = now.replace(hour=s.send_hour, minute=0, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return (target - now).total_seconds()


async def scheduler_loop() -> None:
    while True:
        delay = _seconds_until_next_run()
        log.info("Next digest in %.1f hours", delay / 3600)
        await asyncio.sleep(delay)
        try:
            result = await run_daily()
            log.info("Daily digest sent: %s", result.delivery)
        except Exception:  # never let one bad day kill the loop
            log.exception("Daily digest run failed")
        # Guard against firing twice inside the same target minute.
        await asyncio.sleep(60)
