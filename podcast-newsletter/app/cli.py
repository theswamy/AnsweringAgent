"""Command line entry point, for driving the daily send from cron / CI.

    python -m app.cli run          # build + deliver today's issue once, then exit

Use this instead of the in-process scheduler when you'd rather a real scheduler
(system cron, a GitHub Actions schedule, a k8s CronJob) own the timing.
"""
from __future__ import annotations

import argparse
import asyncio

from . import db
from .runner import run_daily


def main() -> None:
    parser = argparse.ArgumentParser(prog="podcast-digest")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("run", help="Build and deliver today's digest once.")
    args = parser.parse_args()

    if args.cmd == "run":
        db.init_db()
        result = asyncio.run(run_daily())
        print(result.subject)
        print(f"{result.deep_dives} deep dive(s), {result.topics} topic chart(s).")
        print(result.delivery)


if __name__ == "__main__":
    main()
