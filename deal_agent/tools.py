"""The tools the answering agent is given, and their implementations.

The agent is not asked to do arithmetic in its head. Anything numeric goes
through `waterfall.py` / `terms.py`, which reproduce the document's own worked
examples exactly, so a wrong answer is a wrong tool call rather than a wrong
sum. The same dispatch table backs the CLI's non-model commands.
"""
from __future__ import annotations

import json
from typing import Any

from . import document
from .findings import FINDINGS, format_findings
from .terms import PORTCOS, DealTerms, derive, nlp_returns, old_lp_tradeoff, pref_consistency
from .waterfall import (
    DOCUMENT_EXITS,
    ExitEvent,
    SplitConvention,
    format_result,
    run_waterfall,
)

TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "name": "read_document",
        "description": (
            "Read the transaction document. With no query it returns every section; "
            "with a query it returns the sections most relevant to it. Section ids "
            "(S1-S10) are what you cite in answers."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Keywords, or a section id."},
            },
        },
    },
    {
        "name": "deal_terms",
        "description": (
            "The transaction's terms as structured data, plus every percentage "
            "recomputed from the fund's primitives (commitments, ROC, carry, the "
            "purchase price and the discount): the post-ROC cap table, the "
            "post-transaction sharing ratios, and the same ratios expressed as shares "
            "of SB2's own receipts."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "model_exits",
        "description": (
            "Run exits through the two-layer waterfall (NLPI's onshore slice at the "
            "portco level, then SB2's receipts to the NLPF liqpref and on to Class A / "
            "B1 / B2). Call with no exits to model the two the document works through."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "exits": {
                    "type": "array",
                    "description": "Exits in order. Omit to use the document's own examples.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "portco": {"type": "string"},
                            "proceeds": {
                                "type": "number",
                                "description": "Buyer's total cheque in $M for the combined "
                                "SB2 + NLPI position.",
                            },
                            "company_valuation": {
                                "type": "number",
                                "description": "Optional, $M, to report the stake sold.",
                            },
                        },
                        "required": ["portco", "proceeds"],
                    },
                },
                "convention": {
                    "type": "string",
                    "enum": [c.value for c in SplitConvention],
                    "description": "'structure' splits each cheque 87.4/12.6 per x2 (default); "
                    "'doc_examples' splits it 98.6/1.4 as the worked exits in S8/S9 do.",
                },
                "liqpref": {
                    "type": "number",
                    "description": "Override the pref amount in $M. Defaults to the stated "
                    "9.86x on $3.5M = $34.51M; 30.59 (8.74x) is the figure consistent with the "
                    "12.6% SB2 actually sold at the portco level.",
                },
                "count_direct_against_pref": {
                    "type": "boolean",
                    "description": "Net NLPI's onshore proceeds off the pref a second time. The "
                    "9.86x sizing already nets them off once; passing true shows what "
                    "double-netting in the drafting would cost NLP.",
                },
            },
        },
    },
    {
        "name": "outcome_analysis",
        "description": (
            "What the deal is worth to each side at a given total future realisation "
            "from the remaining portfolio ($M): the old LPs' position with and without "
            "the transaction, their indifference point, and NLP's proceeds and MOIC."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "total_future_proceeds": {
                    "type": "number",
                    "description": "Everything the remaining portfolio ever distributes, $M. "
                    "The document's carrying value is 360.",
                },
            },
            "required": ["total_future_proceeds"],
        },
    },
    {
        "name": "list_findings",
        "description": (
            "The analysis register: arithmetic that does not close, terms whose basis "
            "is ambiguous, and open execution questions - each with the document "
            "sections it comes from, live numbers, and a suggested fix."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "finding_id": {"type": "string", "description": "e.g. 'F3' for one finding."},
                "severity": {"type": "string", "enum": ["high", "medium", "low"]},
                "kind": {
                    "type": "string",
                    "enum": ["arithmetic", "basis", "economics", "structure", "execution", "drafting"],
                },
            },
        },
    },
]


def read_document(query: str = "") -> str:
    if not query:
        return document.FULL_TEXT
    hits = document.search(query)
    if not hits:
        return document.FULL_TEXT
    return "\n\n".join(f"[{s.id}] {s.title}\n{s.text}" for s in hits)


def deal_terms() -> str:
    terms = DealTerms()
    econ = derive(terms)
    payload = {
        "stated_terms": {
            "fund_size_musd": terms.fund_size,
            "class_a_commitment_musd": terms.class_a_commitment,
            "class_b_commitment_musd": terms.class_b_commitment,
            "capital_distributed_musd": terms.capital_distributed,
            "remaining_roc_musd": terms.remaining_roc,
            "nav_musd": terms.nav,
            "carry_after_roc": terms.carry,
            "nlp_cheque_musd": terms.check,
            "discount": terms.discount,
            "nlpf_contribution_musd": terms.feeder_contribution,
            "nlpf_liqpref_multiple": terms.feeder_liqpref_multiple,
            "nlpf_liqpref_musd": terms.feeder_liqpref,
            "nlpf_liqpref_note": "9.86x = 98.6% of $35M, as stated. SB2 cannot grant a pref "
            "over shares it has already sold, but what it sold at the portco level is x2 = "
            "12.6% to NLPI, not x1 = 1.4% (NLPF's interest inside the fund) - so the "
            "consistent figure is 8.74x = $30.59M. See pref_consistency and finding F2.",
            "nlpi_onshore_musd": terms.onshore_contribution,
            "x1_pct_of_class_b": terms.x1_class_b,
            "x2_pct_of_portco_stakes": terms.x2_portco,
            "stated_post_roc_cap_table": {
                "class_a": terms.stated_post_roc_class_a,
                "class_b": terms.stated_post_roc_class_b,
                "note": "sums to 101%; see finding F1",
            },
            "stated_tail": {
                "class_a": terms.stated_tail_class_a,
                "class_b1_old_lps": terms.stated_tail_class_b,
                "nlp": terms.stated_tail_nlp,
            },
            "portcos": PORTCOS,
        },
        "recomputed": econ.as_dict(),
        "pref_consistency": {
            "at_x1_1_4_pct": pref_consistency(terms.x1_class_b),
            "at_x2_12_6_pct": pref_consistency(terms.x2_portco),
            "rule": "pref = (1 - NLPI's onshore share) x $35M, so the multiple is derived "
            "from the split, not negotiated independently (findings F2, F14)",
        },
        "recomputed_notes": {
            "class_a_profit_share": "2% commitment + 30% carry on the LPs' 98% = 31.40% of all "
            "profit above the ROC, at any profit level (single 1x hurdle, no catch-up tiers).",
            "sb2_share_of_proceeds": "87.4% - what reaches the fund after NLPI's onshore slice.",
            "tail_nlp_feeder": "back-solved: NLP's stated 14.1% less NLPI's 12.6% direct stake.",
        },
    }
    return json.dumps(payload, indent=2, default=str)


def model_exits(
    exits: list[dict[str, Any]] | None = None,
    convention: str = SplitConvention.STRUCTURE.value,
    count_direct_against_pref: bool = False,
    liqpref: float | None = None,
) -> str:
    events = (
        [
            ExitEvent(
                portco=str(e.get("portco", "portco")),
                proceeds=float(e["proceeds"]),
                company_valuation=(
                    float(e["company_valuation"]) if e.get("company_valuation") else None
                ),
            )
            for e in exits
        ]
        if exits
        else DOCUMENT_EXITS
    )
    result = run_waterfall(
        events,
        convention=SplitConvention(convention),
        count_direct_against_pref=count_direct_against_pref,
        liqpref=float(liqpref) if liqpref is not None else None,
    )
    return format_result(result)


def outcome_analysis(total_future_proceeds: float) -> str:
    trade = old_lp_tradeoff(float(total_future_proceeds))
    nlp = nlp_returns(float(total_future_proceeds))
    return json.dumps({"old_lps_class_b1": trade, "nlp": nlp}, indent=2)


def list_findings(
    finding_id: str = "", severity: str = "", kind: str = ""
) -> str:
    selected = FINDINGS
    if finding_id:
        selected = tuple(f for f in selected if f.id.upper() == finding_id.upper())
    if severity:
        selected = tuple(f for f in selected if f.severity == severity)
    if kind:
        selected = tuple(f for f in selected if f.kind == kind)
    if not selected:
        return "No findings match that filter."
    return format_findings(selected)


DISPATCH = {
    "read_document": read_document,
    "deal_terms": deal_terms,
    "model_exits": model_exits,
    "outcome_analysis": outcome_analysis,
    "list_findings": list_findings,
}


def call(name: str, arguments: dict[str, Any]) -> str:
    handler = DISPATCH.get(name)
    if handler is None:
        return f"Unknown tool: {name}"
    try:
        return handler(**arguments)
    except Exception as exc:  # a bad tool call should be recoverable by the model
        return f"Tool {name} failed on {arguments!r}: {exc}"
