"""An answering agent for the SB2 / NLP secondary transaction document.

    from deal_agent import ask
    print(ask("Is the liqpref actually satisfied after the two example exits?"))

The document itself lives in `document.py`; its arithmetic is reproduced in
`terms.py` and `waterfall.py`; what the analysis found is in `findings.py`.
"""
from __future__ import annotations

from .agent import ClaudeAnswerer, OfflineAnswerer, build_answerer, report
from .terms import DealTerms, derive, nlp_returns, old_lp_tradeoff
from .waterfall import DOCUMENT_EXITS, ExitEvent, SplitConvention, run_waterfall

__all__ = [
    "ask",
    "report",
    "build_answerer",
    "ClaudeAnswerer",
    "OfflineAnswerer",
    "DealTerms",
    "derive",
    "old_lp_tradeoff",
    "nlp_returns",
    "ExitEvent",
    "SplitConvention",
    "run_waterfall",
    "DOCUMENT_EXITS",
]


def ask(question: str, prefer_model: bool = True) -> str:
    """One-shot question. Uses Claude if ANTHROPIC_API_KEY is set, else the
    deterministic offline answerer."""
    answerer, _ = build_answerer(prefer_model=prefer_model)
    return answerer.ask(question)
