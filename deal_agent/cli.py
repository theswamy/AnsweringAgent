"""Command line for the answering agent.

    python -m deal_agent ask "why isn't the liqpref satisfied?"
    python -m deal_agent chat            # interactive, keeps context
    python -m deal_agent report          # the standing analysis
    python -m deal_agent findings --severity high
    python -m deal_agent exits --exit Freo:50:900 --convention structure
    python -m deal_agent outcome 180
    python -m deal_agent doc S8
"""
from __future__ import annotations

import argparse
import sys

from . import tools
from .agent import build_answerer, report
from .waterfall import SplitConvention


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m deal_agent",
        description="Answering agent for the SB2 / NLP secondary transaction document.",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Force the deterministic answerer even if ANTHROPIC_API_KEY is set.",
    )
    parser.add_argument("--verbose", action="store_true", help="Show the agent's tool calls.")
    sub = parser.add_subparsers(dest="command", required=True)

    ask_cmd = sub.add_parser("ask", help="Ask one question.")
    ask_cmd.add_argument("question", nargs="+")

    sub.add_parser("chat", help="Interactive session (keeps context between questions).")
    sub.add_parser("report", help="Print the full standing analysis.")

    findings_cmd = sub.add_parser("findings", help="The findings register.")
    findings_cmd.add_argument("--id", default="", help="A single finding, e.g. F3.")
    findings_cmd.add_argument("--severity", default="", choices=["", "high", "medium", "low"])
    findings_cmd.add_argument("--kind", default="")

    exits_cmd = sub.add_parser("exits", help="Run exits through the waterfall.")
    exits_cmd.add_argument(
        "--exit",
        dest="exits",
        action="append",
        default=[],
        metavar="PORTCO:PROCEEDS[:VALUATION]",
        help="Repeatable, in order, $M. Omit to use the document's own exits.",
    )
    exits_cmd.add_argument(
        "--convention",
        default=SplitConvention.STRUCTURE.value,
        choices=[c.value for c in SplitConvention],
    )
    exits_cmd.add_argument(
        "--pref-counts-onshore",
        action="store_true",
        help="Count NLPI's onshore proceeds against NLP's $35M priority return (see F5).",
    )

    outcome_cmd = sub.add_parser("outcome", help="Price an outcome for each side.")
    outcome_cmd.add_argument("total_future_proceeds", type=float, help="$M, e.g. 360")

    doc_cmd = sub.add_parser("doc", help="Read the document.")
    doc_cmd.add_argument("query", nargs="*", help="Keywords or a section id; omit for all.")

    sub.add_parser("terms", help="The structured terms and every derived percentage.")

    args = parser.parse_args(argv)

    if args.command == "report":
        print(report())
        return 0
    if args.command == "findings":
        print(tools.list_findings(finding_id=args.id, severity=args.severity, kind=args.kind))
        return 0
    if args.command == "exits":
        print(
            tools.model_exits(
                exits=[_parse_exit(spec) for spec in args.exits] or None,
                convention=args.convention,
                count_direct_against_pref=args.pref_counts_onshore,
            )
        )
        return 0
    if args.command == "outcome":
        print(tools.outcome_analysis(args.total_future_proceeds))
        return 0
    if args.command == "doc":
        print(tools.read_document(" ".join(args.query)))
        return 0
    if args.command == "terms":
        print(tools.deal_terms())
        return 0

    answerer, model_backed = build_answerer(
        prefer_model=not args.offline, verbose=args.verbose
    )
    if args.command == "ask":
        if not model_backed:
            print(_offline_notice(), file=sys.stderr)
        print(answerer.ask(" ".join(args.question)))
        return 0

    # chat
    print("Answering agent for the SB2 / NLP secondary. Ctrl-D or 'exit' to leave.")
    print(_offline_notice() if not model_backed else f"Model: {answerer.model}")
    while True:
        try:
            question = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if question.lower() in {"exit", "quit"}:
            return 0
        if question:
            print()
            print(answerer.ask(question))


def _parse_exit(spec: str) -> dict[str, object]:
    parts = spec.split(":")
    if len(parts) < 2:
        raise SystemExit(f"--exit wants PORTCO:PROCEEDS[:VALUATION], got {spec!r}")
    event: dict[str, object] = {"portco": parts[0], "proceeds": float(parts[1])}
    if len(parts) > 2 and parts[2]:
        event["company_valuation"] = float(parts[2])
    return event


def _offline_notice() -> str:
    return (
        "(offline mode: deterministic keyword answers over the same deal model - "
        "set ANTHROPIC_API_KEY for the full agent)"
    )
