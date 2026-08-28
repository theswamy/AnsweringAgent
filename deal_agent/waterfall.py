"""The exit waterfall: who gets paid what, in what order, on each exit.

Two layers, because NLP comes in through two entities [S5]:

    buyer's cheque for an SB2 portco position
        |-- NLPI's direct slice, paid onshore in India, straight to NLP
        `-- SB2's slice, paid into the fund in Mauritius, then
                |-- 100% to NLPF until the 9.86x liqpref ($34.51M) is repaid
                `-- thereafter Class A / Class B1 / Class B2 pari-passu

The document splits that first layer two different ways - 98.6/1.4 in the
worked WheelsEye and first-Niyo exits [S8][S9], and 88/12 in the tail [S10] -
so the split is a parameter here (`SplitConvention`) rather than a constant. The
88/12 version is the one consistent with x2 = 12.6%; the other substitutes x1
(a Class B percentage) for x2 (a portco percentage). See findings F2 and F12.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .terms import DealTerms, Economics, derive


class SplitConvention(str, Enum):
    #: NLPI takes x2 = 12.6% of every portco cheque. Consistent with [S5][S10].
    STRUCTURE = "structure"
    #: NLPI takes 1.4%, as the worked exits in [S8] and [S9] have it.
    DOC_EXAMPLES = "doc_examples"


@dataclass(frozen=True)
class ExitEvent:
    """A sale of part of SB2's original position in one portfolio company.

    `proceeds` is the buyer's total cheque, i.e. what SB2 and NLPI receive
    between them for the combined position.
    """

    portco: str
    proceeds: float
    company_valuation: float | None = None
    label: str = ""

    @property
    def stake_sold_pct(self) -> float | None:
        if not self.company_valuation:
            return None
        return self.proceeds / self.company_valuation


@dataclass
class EventDistribution:
    event: ExitEvent
    nlpi_direct: float
    sb2_receipts: float
    to_nlpf_pref: float
    class_a: float
    class_b1: float
    class_b2_nlpf: float
    pref_outstanding_after: float

    @property
    def nlp_total(self) -> float:
        return self.nlpi_direct + self.to_nlpf_pref + self.class_b2_nlpf

    @property
    def in_pref_phase(self) -> bool:
        return self.to_nlpf_pref > 0


@dataclass
class WaterfallResult:
    convention: SplitConvention
    count_direct_against_pref: bool
    liqpref: float
    events: list[EventDistribution] = field(default_factory=list)

    @property
    def total_proceeds(self) -> float:
        return sum(d.event.proceeds for d in self.events)

    @property
    def totals(self) -> dict[str, float]:
        return {
            "class_a": sum(d.class_a for d in self.events),
            "class_b1_old_lps": sum(d.class_b1 for d in self.events),
            "nlp_via_pref": sum(d.to_nlpf_pref for d in self.events),
            "nlp_class_b2": sum(d.class_b2_nlpf for d in self.events),
            "nlp_direct_onshore": sum(d.nlpi_direct for d in self.events),
            "nlp_total": sum(d.nlp_total for d in self.events),
        }

    @property
    def pref_outstanding(self) -> float:
        return self.events[-1].pref_outstanding_after if self.events else 0.0

    @property
    def pref_satisfied(self) -> bool:
        return self.pref_outstanding <= 1e-9


def run_waterfall(
    events: list[ExitEvent],
    terms: DealTerms = DealTerms(),
    econ: Economics | None = None,
    convention: SplitConvention = SplitConvention.STRUCTURE,
    count_direct_against_pref: bool = False,
    liqpref: float | None = None,
) -> WaterfallResult:
    """Walk a sequence of exits through both layers of the waterfall.

    `liqpref` overrides the pref amount, for testing a multiple other than the
    stated 9.86x - 8.74x is the figure consistent with x2 = 12.6% (finding F2).

    `count_direct_against_pref` nets NLPI's onshore receipts off the pref a
    second time. The 9.86x sizing already nets them off once, ex ante, which is
    what makes NLP whole at exactly $35M; setting this flag as well under-repays
    it, and is here to show what that mis-drafting would cost (finding F5).
    """
    econ = econ or derive(terms)
    direct_pct = (
        terms.x2_portco if convention is SplitConvention.STRUCTURE else terms.x1_class_b
    )

    outstanding = terms.feeder_liqpref if liqpref is None else liqpref
    result = WaterfallResult(
        convention=convention,
        count_direct_against_pref=count_direct_against_pref,
        liqpref=outstanding,
    )

    for event in events:
        nlpi_direct = event.proceeds * direct_pct
        sb2_receipts = event.proceeds - nlpi_direct

        if count_direct_against_pref:
            outstanding = max(outstanding - nlpi_direct, 0.0)

        to_pref = min(sb2_receipts, outstanding)
        outstanding -= to_pref
        residual = sb2_receipts - to_pref

        # Class A is not diluted by the secondary, so the residual is split on
        # shares of SB2's receipts, not of the absolute cheque [S10].
        result.events.append(
            EventDistribution(
                event=event,
                nlpi_direct=nlpi_direct,
                sb2_receipts=sb2_receipts,
                to_nlpf_pref=to_pref,
                class_a=residual * econ.sb2_share_class_a,
                class_b1=residual * econ.sb2_share_class_b1,
                class_b2_nlpf=residual * econ.sb2_share_class_b2,
                pref_outstanding_after=outstanding,
            )
        )
    return result


#: The two exits the document works through [S7][S8][S9][S10].
DOCUMENT_EXITS: list[ExitEvent] = [
    ExitEvent("WheelsEye", 20.0, 800.0, label="A) $20M in WheelsEye at $800M"),
    ExitEvent("Niyo", 15.0, 500.0, label="B(a)) first $15M of the Niyo secondary"),
    ExitEvent("Niyo", 10.0, 500.0, label="B(b)) next $10M of the Niyo secondary"),
]


def format_result(result: WaterfallResult) -> str:
    """A distribution notice a human can read, one block per exit."""
    lines = [
        f"Convention: NLPI takes "
        f"{result.events[0].nlpi_direct / result.events[0].event.proceeds:.1%} of each cheque "
        f"({result.convention.value}); pref ${result.liqpref:,.2f}M"
        + (" (netted against onshore receipts a second time)" if result.count_direct_against_pref else "")
        + "."
        if result.events
        else "No exits modelled.",
        "",
    ]
    for dist in result.events:
        event = dist.event
        head = event.label or f"{event.portco} ${event.proceeds:,.2f}M"
        stake = event.stake_sold_pct
        if stake is not None:
            head += f"  ({stake:.3%} of {event.portco} at ${event.company_valuation:,.0f}M)"
        lines.append(head)
        lines.append(f"  NLPI (onshore, direct)      ${dist.nlpi_direct:8,.2f}M")
        lines.append(f"  SB2 (Mauritius)             ${dist.sb2_receipts:8,.2f}M")
        if dist.to_nlpf_pref:
            lines.append(f"    -> NLPF liqpref           ${dist.to_nlpf_pref:8,.2f}M")
        if dist.class_a or dist.class_b1 or dist.class_b2_nlpf:
            lines.append(f"    -> Class A (GP)           ${dist.class_a:8,.2f}M")
            lines.append(f"    -> Class B1 (old LPs)     ${dist.class_b1:8,.2f}M")
            lines.append(f"    -> Class B2 (NLPF)        ${dist.class_b2_nlpf:8,.2f}M")
        lines.append(
            f"  pref outstanding after      ${dist.pref_outstanding_after:8,.2f}M"
            + ("  <- SATISFIED" if dist.pref_outstanding_after <= 1e-9 else "")
        )
        lines.append("")

    totals = result.totals
    lines.append(f"Totals on ${result.total_proceeds:,.2f}M of exits")
    for name, value in totals.items():
        lines.append(f"  {name:24} ${value:8,.2f}M")
    lines.append(f"  pref outstanding         ${result.pref_outstanding:8,.2f}M")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# v2: the aggregate-entitlement waterfall
# ---------------------------------------------------------------------------
#
# The document sizes NLP's priority return as a fixed multiple on NLPF's $3.5M.
# That only works if NLPI's share of every exit cheque is the same known
# number. It is not: SB2 holds part of its portfolio onshore in India, where
# NLPI can take direct delivery, and part in Mauritius (including the Delaware
# companies), where it cannot. So NLPI takes 12.6%/theta of an onshore cheque
# and nothing at all of a Mauritius one, and only averages 12.6% across the
# whole portfolio - which means no fixed multiple can be right in advance.
#
# The fix is to state NLP's entitlement in aggregate across both vehicles and
# let SB2 top it up out of its own receipts:
#
#   1. the buyer pays NLPI its shareholding percentage of the cheque directly,
#      and that counts towards NLP's entitlement;
#   2. SB2 pays NLPF whatever is needed to bring NLP's cumulative receipts up
#      to its cumulative entitlement (100% of the first $35M, then 14.1%);
#   3. SB2 splits the balance between Class A and Class B1, 36.6 / 63.4.
#
# Class A then receives exactly 31.4% and Class B1 exactly 54.5% of every
# dollar above the priority, whatever the onshore/offshore mix turns out to be.


class Venue(str, Enum):
    #: Shares held onshore in India - NLPI owns a slice and is paid directly.
    ONSHORE = "onshore"
    #: Shares held in Mauritius, Delaware companies included - NLPI owns none.
    MAURITIUS = "mauritius"


@dataclass(frozen=True)
class ExitV2:
    portco: str
    proceeds: float
    venue: Venue = Venue.ONSHORE
    company_valuation: float | None = None
    label: str = ""


@dataclass
class EventV2:
    event: ExitV2
    nlpi_direct: float
    sb2_receipts: float
    top_up_priority: float
    top_up_tail: float
    class_a: float
    class_b1: float
    priority_outstanding_after: float

    @property
    def nlp_total(self) -> float:
        return self.nlpi_direct + self.top_up_priority + self.top_up_tail


@dataclass
class ResultV2:
    onshore_stake: float
    events: list[EventV2] = field(default_factory=list)

    @property
    def totals(self) -> dict[str, float]:
        return {
            "class_a": sum(e.class_a for e in self.events),
            "class_b1_old_lps": sum(e.class_b1 for e in self.events),
            "nlp_direct_onshore": sum(e.nlpi_direct for e in self.events),
            "nlp_via_sb2": sum(e.top_up_priority + e.top_up_tail for e in self.events),
            "nlp_total": sum(e.nlp_total for e in self.events),
        }

    @property
    def total_proceeds(self) -> float:
        return sum(e.event.proceeds for e in self.events)

    @property
    def implied_pref_multiple(self) -> float:
        """What the pref multiple turns out to be, ex post, on this sequence."""
        priority = sum(e.top_up_priority for e in self.events)
        return priority / DealTerms().feeder_contribution


def onshore_stake(theta: float, terms: DealTerms = DealTerms()) -> float:
    """NLPI's stake in each India-held position.

    `theta` is the share of SB2's NAV held onshore. NLPI bought 12.6% of the
    whole portfolio's economics but can only hold the onshore part, so its stake
    in that part has to be grossed up for it to average 12.6% overall.
    """
    if not 0 < theta <= 1:
        raise ValueError("theta must be in (0, 1]")
    return terms.x2_portco / theta


def run_waterfall_v2(
    events: list[ExitV2],
    theta: float = 0.70,
    terms: DealTerms = DealTerms(),
    econ: Economics | None = None,
    cap_direct_to_entitlement: bool = True,
) -> ResultV2:
    """Walk exits through the aggregate-entitlement waterfall.

    `cap_direct_to_entitlement` is the one substantive choice. NLPI's stake in
    each onshore position is 12.6%/theta - 18.0% at theta = 70% - which is more
    than NLP's 14.1% tail share. So on an onshore exit in the tail NLPI collects
    more than NLP is entitled to, and a top-up can only stop, not reverse: the
    excess is recoverable only out of later Mauritius exits, if any remain. Left
    uncapped the split becomes order-dependent (selling Mauritius first leaves
    NLP $9.83M ahead on a full realisation of the illustration).

    With the cap, NLPI sells in each exit the lesser of its pro-rata shareholding
    and the amount that keeps NLP's cumulative receipts equal to its cumulative
    entitlement, keeping the shares it does not sell for later. Every ordering
    then lands on the stated ratios exactly.
    """
    econ = econ or derive(terms)
    stake = onshore_stake(theta, terms)
    sb2_a = econ.tail_class_a / (econ.tail_class_a + econ.tail_class_b1)
    sb2_b1 = econ.tail_class_b1 / (econ.tail_class_a + econ.tail_class_b1)

    result = ResultV2(onshore_stake=stake)
    cumulative_distributions = 0.0
    nlp_received = 0.0

    for event in events:
        direct = event.proceeds * (stake if event.venue is Venue.ONSHORE else 0.0)

        # NLP's cumulative entitlement: all of the first $35M, then its tail share.
        gross_after = cumulative_distributions + event.proceeds
        priority_entitlement = min(gross_after, terms.check)
        tail_pool = max(gross_after - terms.check, 0.0)
        tail_entitlement = econ.tail_nlp_total * tail_pool

        if cap_direct_to_entitlement:
            headroom = priority_entitlement + tail_entitlement - nlp_received
            direct = min(direct, max(headroom, 0.0))

        sb2 = event.proceeds - direct
        cumulative_distributions = gross_after
        nlp_received += direct

        # Top up out of SB2's receipts, priority layer first.
        top_up_priority = min(max(priority_entitlement - nlp_received, 0.0), sb2)
        nlp_received += top_up_priority
        top_up_tail = min(
            max(priority_entitlement + tail_entitlement - nlp_received, 0.0),
            sb2 - top_up_priority,
        )
        nlp_received += top_up_tail

        residual = sb2 - top_up_priority - top_up_tail
        result.events.append(
            EventV2(
                event=event,
                nlpi_direct=direct,
                sb2_receipts=sb2,
                top_up_priority=top_up_priority,
                top_up_tail=top_up_tail,
                class_a=residual * sb2_a,
                class_b1=residual * sb2_b1,
                priority_outstanding_after=max(terms.check - min(nlp_received, terms.check), 0.0),
            )
        )
    return result
