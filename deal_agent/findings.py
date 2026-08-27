"""What the analysis found: arithmetic that does not close, terms whose basis is
ambiguous, and the questions that have to be answered before this can be papered.

Each finding is checked against the model where it can be - `check()` returns
the live numbers so the register cannot quietly go stale if the terms change.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .terms import DealTerms, derive, old_lp_tradeoff, pref_consistency
from .waterfall import DOCUMENT_EXITS, SplitConvention, run_waterfall


@dataclass(frozen=True)
class Finding:
    id: str
    severity: str  # high | medium | low
    kind: str  # arithmetic | basis | economics | structure | execution | drafting
    title: str
    detail: str
    sections: tuple[str, ...]
    resolution: str
    check: Callable[[], str] | None = None
    #: open | closed. Closed findings are kept, with what closed them, so the
    #: register stays a record of the negotiation rather than only its present state.
    status: str = "open"


    def evidence(self) -> str:
        return self.check() if self.check else ""


def _f1() -> str:
    t = DealTerms()
    return (
        f"stated {t.stated_post_roc_class_a:.1%} + {t.stated_post_roc_class_b:.1%} = "
        f"{t.stated_post_roc_class_a + t.stated_post_roc_class_b:.1%}; "
        f"recomputed Class B = {derive(t).class_b_profit_share:.2%}"
    )


def _f2() -> str:
    struct = run_waterfall(DOCUMENT_EXITS[:1], convention=SplitConvention.STRUCTURE).events[0]
    doc = run_waterfall(DOCUMENT_EXITS[:1], convention=SplitConvention.DOC_EXAMPLES).events[0]
    at_x2 = pref_consistency(DealTerms().x2_portco)
    return (
        f"$20M WheelsEye exit: x2=12.6% gives NLPI ${struct.nlpi_direct:,.2f}M and SB2 "
        f"${struct.sb2_receipts:,.2f}M; the document's 1.4% gives NLPI "
        f"${doc.nlpi_direct:,.2f}M and SB2 ${doc.sb2_receipts:,.2f}M - a "
        f"${struct.nlpi_direct - doc.nlpi_direct:,.2f}M difference on one exit. It also sets "
        f"the pref multiple: at x2 the consistent pref is "
        f"{at_x2['consistent_multiple']:.2f}x (${at_x2['consistent_pref']:,.2f}M), not 9.86x"
    )


def _f3() -> str:
    doc = run_waterfall(DOCUMENT_EXITS[:2], convention=SplitConvention.DOC_EXAMPLES)
    struct = run_waterfall(DOCUMENT_EXITS[:2], convention=SplitConvention.STRUCTURE)
    return (
        f"at the marker the pref is exhausted to the cent on the document's own split "
        f"(${doc.pref_outstanding:,.2f}M outstanding, NLP repaid "
        f"${doc.totals['nlp_total']:,.2f}M); at x2=12.6% the same $35M of exits leaves "
        f"${struct.pref_outstanding:,.2f}M outstanding"
    )


def _f4() -> str:
    t, e = DealTerms(), derive(DealTerms())
    return (
        f"x1=1.4% of Class B is {t.x1_class_b * e.class_b_profit_share:.2%} of absolute; "
        f"[S10] treats Class B2 as 2% of absolute; reaching NLP's {e.tail_nlp_total:.1%} "
        f"alongside a {e.tail_nlp_direct:.1%} direct stake needs "
        f"{e.tail_nlp_feeder:.2%} of absolute, i.e. "
        f"{e.tail_nlp_feeder / e.class_b_profit_share:.2%} of Class B"
    )


def _f5() -> str:
    as_sized = run_waterfall(DOCUMENT_EXITS[:2], convention=SplitConvention.DOC_EXAMPLES)
    netted_twice = run_waterfall(
        DOCUMENT_EXITS[:2], convention=SplitConvention.DOC_EXAMPLES,
        count_direct_against_pref=True,
    )
    return (
        f"the 9.86x sizing nets the onshore slice off once: NLP is repaid exactly "
        f"${as_sized.totals['nlp_total']:,.2f}M at the marker. Netting it off twice in the "
        f"drafting would repay ${netted_twice.totals['nlp_total']:,.2f}M and start the tail early"
    )


def _f14() -> str:
    at_x1 = pref_consistency(DealTerms().x1_class_b)
    at_x2 = pref_consistency(DealTerms().x2_portco)
    return (
        f"pref = (1 - onshore%) x $35M: {at_x1['consistent_multiple']:.2f}x at 1.4%, "
        f"{at_x2['consistent_multiple']:.2f}x at 12.6%. Holding 9.86x while NLPI takes 12.6% "
        f"means the pref only clears after ${at_x2['exits_until_pref_exhausted']:,.2f}M of "
        f"exits, by which point NLP has taken ${at_x2['over_recovery']:,.2f}M more than its 1x"
    )


def _f6() -> str:
    t = DealTerms()
    return (
        f"Class A's share of the remaining ROC is "
        f"{t.class_a_share_of_commitments * t.remaining_roc:,.2f}M, which the $35M - paid by NLP "
        f"to Class B holders - does not fund"
    )


def _f7() -> str:
    t = DealTerms()
    return (
        f"${t.feeder_contribution:,.2f}M of new money carries a "
        f"{t.feeder_liqpref_multiple:.2f}x pref = ${t.feeder_liqpref:,.2f}M of priority claim "
        f"ranking ahead of both existing classes - "
        f"{t.feeder_liqpref / t.check:.1%} of the whole NLP cheque, against "
        f"{t.feeder_contribution / t.check:.0%} of the money"
    )


def _f11() -> str:
    t, e = DealTerms(), derive(DealTerms())
    return (
        f"LP NAV {e.lp_nav:,.2f} vs 260 stated; cheque as % of LP "
        f"{e.nlp_pct_of_lp_undiscounted:.2%} vs 13% stated; grossed up for the discount "
        f"{e.nlp_pct_of_lp_discounted:.2%} vs 20% stated; NLP profit share "
        f"{e.nlp_derived_profit_share:.2%} vs {t.stated_tail_nlp:.1%} stated"
    )


def _f13() -> str:
    trade = old_lp_tradeoff(360.0)
    return (
        f"at NAV, Class B1 receives ${trade['class_b1_with_deal']:,.1f}M with the deal against "
        f"${trade['class_b1_without_deal']:,.1f}M without it (${trade['difference']:,.1f}M), and "
        f"is indifferent at ${trade['breakeven_total_proceeds']:,.1f}M of total future proceeds"
    )


FINDINGS: tuple[Finding, ...] = (
    Finding(
        "F1",
        "low",
        "arithmetic",
        "The post-ROC cap table sums to 101%",
        "[S2] gives Class A 31.4% and Class B 69.6%. Recomputing from the fund's own "
        "primitives - 2%/98% commitments, $35M ROC returned first, 30% carry on the "
        "balance - Class A is 31.40% and Class B is 68.60%. The tail in [S4] "
        "(31.4 + 54.5 + 14.1 = 100) confirms 68.60% is the intended figure, so 69.6% is a "
        "typo rather than a different assumption.",
        ("S1", "S2", "S4"),
        "Change Class B to 68.6%.",
        _f1,
    ),
    Finding(
        "F2",
        "high",
        "basis",
        "The worked exits split the buyer's cheque on x1 instead of x2",
        "[S5] sells NLPI 12.6% (x2) of SB2's stake in each portco, and the tail in [S10] "
        "duly splits the buyer's cheque 88/12. But the WheelsEye exit [S8] and the first "
        "Niyo tranche [S9] split it 98.6/1.4 - that 1.4% is x1, which is a percentage of "
        "Class B inside the fund, not a percentage of a portco position. [S8] makes the "
        "substitution visible: it computes NLP's slice as '2.5% * x2_WE' but then prints "
        "0.035% of WheelsEye, which is 2.5% x 1.4%. At x2 it would be 0.315%.",
        ("S5", "S8", "S9", "S10"),
        "Restate [S8] and [S9] at 87.4/12.6 and re-derive the pref multiple with them, or "
        "say explicitly why NLPI's onshore slice differs before and after the pref is repaid.",
        _f2,
    ),
    Finding(
        "F3",
        "high",
        "arithmetic",
        "The pref now clears exactly at the marker - CLOSED by the 9.86x restatement",
        "Previously [S9] declared the pref satisfied after SB2 had received $19.72M + $14.79M "
        "= $34.51M against a $35M pref, $0.49M short. The 27 Aug revision resizes the pref to "
        "9.86x = $34.51M and shows the derivation, so on the document's own split the pref is "
        "exhausted to the cent at the marker and NLP has been repaid exactly $35.00M across "
        "both entities. The reason is sound: SB2 cannot grant a pref over the shares it has "
        "already sold to NLPI, so the pref covers only the part of each exit SB2 still owns. "
        "What survives is that the principle is applied to the wrong percentage: the sizing nets "
        "off 1.4%, which is NLPF's interest inside the fund and never arrives outside the pref, "
        "rather than the 12.6% SB2 actually sold at the portco level (see F2 and F14).",
        ("S5", "S8", "S9", "S10"),
        "Nothing to fix as drafted. Re-derive the multiple if x1 or x2 move at signing.",
        _f3,
        "closed",
    ),
    Finding(
        "F4",
        "high",
        "basis",
        "x1 is quoted in three different denominators",
        "x1 = 1.4% is defined as a share of Class B [S5], used as a share of a portco "
        "cheque [S8][S9], and appears as 2% of absolute in the tail [S10]. These are three "
        "different numbers. If x1 really is 1.4% of Class B, the feeder's Class B2 is 0.96% "
        "of absolute and NLP's total is 13.56%, not the 14.1% in [S4].",
        ("S4", "S5", "S8", "S9", "S10"),
        "Fix NLP's total entitlement (14.1%) and NLPI's direct stake (x2 = 12.6%), then "
        "back-solve x1 - about 1.5% of absolute, i.e. ~2.2% of Class B - and state which "
        "denominator each percentage is in.",
        _f4,
    ),
    Finding(
        "F5",
        "medium",
        "economics",
        "NLP's 'first 35M' is now measured across both entities - CLOSED, but say so in terms",
        "The question was whether NLPI's onshore receipts counted towards the first $35M. The "
        "sizing answers it in principle: the pref is $35M less what NLP receives outside it, so "
        "the two entities are made whole together and the pref is exhausted at the same moment. "
        "That is the right answer, but it is implicit in a multiple - and the multiple nets off "
        "the wrong percentage (F2). "
        "Drafting that nets NLPI's receipts off the pref again - reading '$35M to NLP' literally "
        "on top of a pref already net of it - would under-repay NLP and start the tail early.",
        ("S4", "S5", "S8", "S9"),
        "State the priority return as an aggregate $35M across NLPF and NLPI, with the pref "
        "expressed as the balance after NLPI's onshore receipts, so the netting is explicit "
        "and cannot be applied twice.",
        _f5,
        "closed",
    ),
    Finding(
        "F6",
        "medium",
        "economics",
        "Class A's share of the remaining ROC is not funded",
        "[S6] assumes Class A and Class B are both 'whole', i.e. 1x DPI has occurred, but "
        "the $35M that makes that true is paid to Class B holders [S3]. Class A's 2% of the "
        "remaining ROC - $0.70M - has no source, and the tail in [S4] starts only after "
        "NLP's $35M, so it is not recovered there either.",
        ("S3", "S4", "S6"),
        "Either have Class A sell 2% into the transaction (grossing the cheque up), or give "
        "Class A a $0.70M ROC layer ahead of the tail, and say which.",
        _f6,
    ),
    Finding(
        "F7",
        "high",
        "structure",
        "The pref is a $34.51M priority claim funded with $3.5M",
        "NLPF contributes $3.5M for a 9.86x pref [S5]. That is deliberate - it sizes the pref "
        "to the NLP cheque so that NLPI's onshore purchase price can be repaid "
        "through the Mauritius entity - but the economic effect is a $34.51M senior claim on "
        "the fund's future distributions against $3.5M of new money, and it ranks ahead of "
        "both existing classes. It is also participating: [S10] leaves Class B2 sharing in "
        "the tail after the pref is repaid.",
        ("S5", "S10"),
        "Say in terms that the pref is participating and capped at $35M in aggregate across "
        "both NLP entities, and confirm the LPAC/LP consent needed for a claim senior to "
        "existing Class B.",
        _f7,
    ),
    Finding(
        "F8",
        "high",
        "structure",
        "The document's own open question: NLPF cannot pay NLPI",
        "Asked twice [S8][S9]: NLPF collects the pref in Singapore/Mauritius, but NLPI - "
        "which funded $31.5M of the $35M - is the entity that needs the money. Nothing in "
        "the document creates a path from NLPF's receipts to NLPI. This is the load-bearing "
        "gap: the pref is the mechanism for repaying NLPI's purchase price, and it repays "
        "the wrong entity.",
        ("S5", "S8", "S9"),
        "Resolve the return path before anything else - the alternative is to give NLPI its "
        "1x back at the portco level (a larger onshore slice until repaid), which changes "
        "every number in the worked exits.",
        None,
    ),
    Finding(
        "F9",
        "medium",
        "execution",
        "The pro-rata exit undertaking needs the portcos and their other shareholders",
        "[S7] has SB2 and NLP agreeing to sell pro-rata at any exit, secondary or IPO, "
        "'effectively like a put-call'. [S5] flags the SHA amendment for Delaware entities "
        "only, but the India-domiciled portcos need the equivalent, and in both cases the "
        "amendment interacts with existing ROFR, tag-along and drag rights held by other "
        "investors - each of whom has to consent.",
        ("S5", "S7"),
        "List, per portco, the consent needed and whether a put/call between two "
        "shareholders is enforceable there; IPO lock-ups will also override the pro-rata "
        "undertaking for a period.",
        None,
    ),
    Finding(
        "F10",
        "high",
        "execution",
        "Onshore transfer at a 35% discount, with tax 'assumed to be grossed up'",
        "$31.5M of the cheque buys Indian portco shares from a Mauritius fund at a discount "
        "to carrying value [S5]. That is a non-resident-to-non-resident-to-resident chain "
        "with a fair-value floor on the inbound price and capital-gains withholding at the "
        "SB2 level. [S6] assumes any leakage at the company level is grossed up 'however "
        "this could be revisited' - i.e. the number that determines x2, and therefore every "
        "exit split, is currently an assumption.",
        ("S5", "S6"),
        "Price the transfer taxes and confirm the discount survives the pricing floor, then "
        "re-derive x1 and x2 from the grossed-up cheque.",
        None,
    ),
    Finding(
        "F11",
        "low",
        "drafting",
        "Rounding: the stated percentages are 0.2-0.9pp off the arithmetic",
        "[S6] says exact numbers will differ, which covers this, but the gaps compound "
        "through the waterfall and one of them (14.1% vs 14.36%) is the operative sharing "
        "ratio.",
        ("S3", "S4", "S6"),
        "Recompute the sharing ratios from the final cheque and NAV at signing rather than "
        "carrying the illustrative percentages into the documents.",
        _f11,
    ),
    Finding(
        "F12",
        "low",
        "drafting",
        "'mg' is never expanded, and the portco list is not tied to positions",
        "[S5] lists x2_we, x2_mg, x2_niyo, x2_freo, x2_kredx. 'mg' appears nowhere else, and "
        "the document gives no position sizes, so x2 cannot be checked against the $31.5M "
        "it is supposed to buy.",
        ("S5",),
        "Attach a schedule: per portco, SB2's holding, carrying value, and the 12.6% slice "
        "in shares and dollars, summing to $31.5M.",
        None,
    ),
    Finding(
        "F14",
        "high",
        "drafting",
        "The pref multiple is a derived number and should be drafted as one",
        "9.86x is not an independently negotiated term - it is (1 - the share paid to NLP "
        "outside the pref) x $35M / $3.5M. Two things follow. First, the share in that formula "
        "has to be a portco-level one: only x2 = 12.6% reaches NLP without passing through SB2, "
        "so the multiple is 8.74x, not 9.86x. Second, [S9] derives 9.86 as (19.72 + 14.79) / "
        "3.5, which reads as though it came out of the two illustrative exits; it did not, and "
        "the rule holds for any exit sequence. Since [S6] says the exact x1 and x2 will differ, "
        "every change to them moves the multiple.",
        ("S5", "S6", "S9"),
        "Draft the pref as an amount with a formula - '$34.51M, being $35M less NLPI's onshore "
        "percentage of it' - or as a cap on aggregate priority receipts across both entities, "
        "rather than as a hard multiple on the feeder's $3.5M.",
        _f14,
    ),
    Finding(
        "F13",
        "medium",
        "economics",
        "The trade for the old LPs is liquidity, not upside - at any plausible outcome",
        "Class B1 swaps 14.1% of all future profit for $35M of cash now. Because the $35M is "
        "close to the $34.30M of ROC they were owed anyway, they are indifferent at roughly "
        "$40M of total future proceeds against a $360M carrying value; above that they are "
        "giving up value, and at NAV they give up about $45M. That is the 35% discount doing "
        "its job, and it is a defensible price for certainty - but it should be presented as "
        "the price of de-risking, not as a neutral restructuring.",
        ("S3", "S4"),
        "Show LPs the give-up at a range of outcomes (0.25x-1.5x of NAV) alongside the "
        "immediate 1x DPI, so the consent is informed.",
        _f13,
    ),
)

BY_ID = {f.id: f for f in FINDINGS}


def format_findings(findings: tuple[Finding, ...] = FINDINGS, verbose: bool = True) -> str:
    order = {"high": 0, "medium": 1, "low": 2}
    lines: list[str] = []
    for finding in sorted(
        findings,
        key=lambda f: (f.status == "closed", order.get(f.severity, 9), int(f.id[1:])),
    ):
        status = "" if finding.status == "open" else f"/{finding.status.upper()}"
        lines.append(
            f"{finding.id}  [{finding.severity.upper()}/{finding.kind}{status}]  {finding.title}"
        )
        if verbose:
            lines.append(f"    sections: {', '.join(finding.sections)}")
            lines.append(f"    {finding.detail}")
            evidence = finding.evidence()
            if evidence:
                lines.append(f"    numbers:  {evidence}")
            lines.append(f"    fix:      {finding.resolution}")
        lines.append("")
    return "\n".join(lines).rstrip()
