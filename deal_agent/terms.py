"""The transaction's terms as data, plus every derivation the document performs.

The point of this module is that the document's headline percentages are not
inputs — they are *results* of the fund's existing waterfall (2/98 commitments,
1x ROC, 30% carry) and of the price NLP is paying. Recomputing them from the
primitives is what lets the agent say "31.4% is right, 69.6% is a typo" instead
of parroting both.

All money is in $M unless a name says otherwise; all shares are fractions.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class DealTerms:
    """Primitives taken straight from the document (see section ids in comments)."""

    # --- The fund as it stands today [S1] ---
    fund_size: float = 45.612
    class_a_commitment: float = 0.912  # GP, stated as 2%
    class_b_commitment: float = 44.700  # LPs, stated as 98%
    capital_distributed: float = 11.0
    remaining_roc: float = 35.0
    nav: float = 360.0
    carry: float = 0.30  # "Carry after ROC"

    # --- NLP's purchase [S3][S5] ---
    check: float = 35.0
    discount: float = 0.35
    feeder_share_of_check: float = 0.10  # NLPF's slice of the $35M
    feeder_liqpref_multiple: float = 9.86
    x1_class_b: float = 0.014  # "(x1=1.4%) of the Class B" bought by NLPF
    x2_portco: float = 0.126  # "(x2=12.6%) of SB2's stakes in each of the portcos"

    # --- Percentages the document states as the operative deal terms ---
    # These are what the parties would sign; `derive()` checks them against the
    # arithmetic and `findings.py` reports where they disagree.
    stated_post_roc_class_a: float = 0.314  # [S2]
    stated_post_roc_class_b: float = 0.696  # [S2] - sums to 101% with the line above
    stated_tail_class_a: float = 0.314  # [S4]
    stated_tail_class_b: float = 0.545  # [S4] old LPs, i.e. Class B1
    stated_tail_nlp: float = 0.141  # [S4] NLPI direct + NLPF Class B2 combined

    @property
    def class_a_share_of_commitments(self) -> float:
        return self.class_a_commitment / self.fund_size

    @property
    def class_b_share_of_commitments(self) -> float:
        return self.class_b_commitment / self.fund_size

    @property
    def feeder_contribution(self) -> float:
        """NLPF's primary cheque into SB2 Mauritius - $3.5M."""
        return self.check * self.feeder_share_of_check

    @property
    def onshore_contribution(self) -> float:
        """NLPI's onshore purchase of portco shares - $31.5M."""
        return self.check - self.feeder_contribution

    @property
    def feeder_liqpref(self) -> float:
        """9.86x on $3.5M = $34.51M.

        NLP's 1x is settled through two legs, both conveniently measured on the
        feeder's $3.5M, and they add to 10x = the whole $35M cheque:

            9.86x   the liqpref, SB2 -> NLPF in Mauritius        $34.51M
            0.14x   NLPI's pro-rata share sales, onshore         $ 0.49M
           -----                                                --------
           10.00x   NLP's 1x                                     $35.00M

        That is why the pref is 9.86x and not a round 10x: SB2 cannot prefer
        what it no longer owns, so the pref is the balance after NLPI's own
        pro-rata sales. The size of the second leg - and therefore of the pref -
        depends on how much NLPI sells alongside SB2 at each exit, which the
        document gives two answers for. See `pref_consistency`.
        """
        return self.feeder_contribution * self.feeder_liqpref_multiple


# Portfolio companies, using the document's own abbreviations [S5].
PORTCOS: dict[str, str] = {
    "we": "WheelsEye",
    "mg": "MG (never spelled out in the document)",
    "niyo": "Niyo",
    "freo": "Freo",
    "kredx": "KredX",
}


@dataclass(frozen=True)
class Economics:
    """Everything the document's numbers imply, recomputed from `DealTerms`."""

    # Value split today, before NLP
    profit_above_roc: float
    class_a_profit_share: float
    class_b_profit_share: float
    gp_value: float
    class_b_profit_value: float
    lp_nav: float

    # Pricing of NLP's cheque
    nlp_pct_of_lp_undiscounted: float
    nlp_pct_of_lp_discounted: float
    nlp_derived_profit_share: float

    # Operative post-transaction sharing ratios (fractions of every $1 of
    # distribution once NLP's first $35M is repaid)
    tail_class_a: float
    tail_class_b1: float
    tail_nlp_total: float
    tail_nlp_direct: float  # NLPI, taken at the portco level (= x2)
    tail_nlp_feeder: float  # NLPF Class B2, taken inside SB2

    # The same tail expressed as shares of SB2's own receipts, which is how the
    # fund's distribution notice would read [S10]
    sb2_share_class_a: float
    sb2_share_class_b1: float
    sb2_share_class_b2: float

    @property
    def sb2_share_of_proceeds(self) -> float:
        return 1.0 - self.tail_nlp_direct

    def as_dict(self) -> dict[str, float]:
        return asdict(self)


def derive(terms: DealTerms = DealTerms()) -> Economics:
    """Rebuild the document's percentages from the fund's primitives.

    Two things are worth knowing about the shape of this waterfall:

    * With a single 1x hurdle and no catch-up tiers, the GP's share of profit is
      constant at `a + carry * (1 - a)` regardless of how much profit there is.
      That is why the document can quote fixed ratios instead of a tiered
      waterfall without changing anyone's economics.
    * The secondary is sold out of Class B, so Class A is not diluted: Class A
      keeps 31.4% of every absolute dollar, and NLP's 14.1% comes entirely out
      of Class B's 68.6%.
    """
    a = terms.class_a_share_of_commitments
    profit = terms.nav - terms.remaining_roc

    class_a_profit_share = a + terms.carry * (1 - a)
    class_b_profit_share = 1 - class_a_profit_share
    gp_value = profit * class_a_profit_share
    class_b_profit_value = profit * class_b_profit_share

    # What a Class B holder owns today: its pro-rata slice of the unreturned
    # capital, plus its share of profit above the ROC.
    lp_nav = terms.class_b_share_of_commitments * terms.remaining_roc + class_b_profit_value

    undiscounted = terms.check / lp_nav
    discounted = undiscounted / (1 - terms.discount)

    # The document's stated 14.1% is the operative term; the derived figure is
    # kept alongside it so the gap is visible rather than silently smoothed.
    nlp_derived_profit_share = discounted * class_b_profit_share

    tail_nlp = terms.stated_tail_nlp
    tail_class_a = terms.stated_tail_class_a
    tail_class_b1 = 1.0 - tail_class_a - tail_nlp

    # NLPI's direct portco stake is fixed by the structure at x2; whatever is
    # left of NLP's entitlement has to arrive through the feeder's Class B2.
    tail_nlp_direct = terms.x2_portco
    tail_nlp_feeder = tail_nlp - tail_nlp_direct

    sb2_share = 1.0 - tail_nlp_direct
    return Economics(
        profit_above_roc=profit,
        class_a_profit_share=class_a_profit_share,
        class_b_profit_share=class_b_profit_share,
        gp_value=gp_value,
        class_b_profit_value=class_b_profit_value,
        lp_nav=lp_nav,
        nlp_pct_of_lp_undiscounted=undiscounted,
        nlp_pct_of_lp_discounted=discounted,
        nlp_derived_profit_share=nlp_derived_profit_share,
        tail_class_a=tail_class_a,
        tail_class_b1=tail_class_b1,
        tail_nlp_total=tail_nlp,
        tail_nlp_direct=tail_nlp_direct,
        tail_nlp_feeder=tail_nlp_feeder,
        sb2_share_class_a=tail_class_a / sb2_share,
        sb2_share_class_b1=tail_class_b1 / sb2_share,
        sb2_share_class_b2=tail_nlp_feeder / sb2_share,
    )


def pref_consistency(
    onshore_pct: float | None = None,
    terms: DealTerms = DealTerms(),
) -> dict[str, float]:
    """Size the pref against the pro-rata slice NLPI sells alongside SB2.

    NLP's 1x arrives through two legs and they must add to $35M. If NLPI sells
    `d` of every exit pro-rata and keeps those proceeds, the pref is the balance:

        pref = (1 - d) x $35M

    Both legs are then exhausted at the same moment: NLP has taken `d * X`
    onshore and `(1 - d) * X` through the pref, so it is whole at X = $35M of
    exits and not a dollar earlier or later.

    So the multiple is derived, not independently negotiated - and the document
    gives two values for `d`. Its worked exits sell 1.4% pro-rata, which is what
    produces the stated 9.86x + 0.14x. If NLPI instead sells the x2 = 12.6% that
    [S5] says it owns, the legs are 8.74x + 1.26x - the same $35M, a smaller
    pref. Keeping 9.86x while NLPI sells 12.6% leaves the pref running past
    NLP's 1x, over-repaying it out of Class A and Class B1.
    """
    d = terms.x1_class_b if onshore_pct is None else onshore_pct
    consistent = (1 - d) * terms.check
    stated = terms.feeder_liqpref
    # How much of the portfolio has to sell before the stated pref is exhausted,
    # and what NLP has received in total by then.
    exits_to_exhaust = stated / (1 - d) if d < 1 else float("inf")
    return {
        "onshore_pct": d,
        "stated_pref": stated,
        "stated_multiple": terms.feeder_liqpref_multiple,
        "consistent_pref": consistent,
        "consistent_multiple": consistent / terms.feeder_contribution,
        "exits_until_pref_exhausted": exits_to_exhaust,
        "nlp_priority_receipts": exits_to_exhaust,
        "over_recovery": exits_to_exhaust - terms.check,
    }


def old_lp_tradeoff(
    total_future_proceeds: float,
    terms: DealTerms = DealTerms(),
    econ: Economics | None = None,
) -> dict[str, float]:
    """What the existing LPs (Class B1) give up, and get, at a given outcome.

    `total_future_proceeds` is everything the remaining portfolio ever
    distributes, in $M, measured on SB2's pre-transaction position.

    Without the deal: Class B takes 98% of the remaining $35M ROC, then 68.6% of
    the profit. With the deal: Class B1 has $35M of cash at close and then 54.5%
    of everything above NLP's repaid $35M.
    """
    econ = econ or derive(terms)
    roc_returned = min(total_future_proceeds, terms.remaining_roc)
    profit = max(total_future_proceeds - terms.remaining_roc, 0.0)

    without_deal = (
        terms.class_b_share_of_commitments * roc_returned + econ.class_b_profit_share * profit
    )
    # The $35M is cash today; the tail is contingent on the same portfolio.
    with_deal = terms.check + econ.tail_class_b1 * profit

    # Indifference point, solved on profit: 0.98*ROC + b*P = check + b1*P.
    spread = econ.class_b_profit_share - econ.tail_class_b1
    breakeven_profit = (
        (terms.check - terms.class_b_share_of_commitments * terms.remaining_roc) / spread
        if spread
        else float("inf")
    )
    return {
        "total_future_proceeds": total_future_proceeds,
        "profit_above_roc": profit,
        "class_b1_without_deal": without_deal,
        "class_b1_with_deal": with_deal,
        "difference": with_deal - without_deal,
        "breakeven_profit": breakeven_profit,
        "breakeven_total_proceeds": breakeven_profit + terms.remaining_roc,
    }


def nlp_returns(
    total_future_proceeds: float,
    terms: DealTerms = DealTerms(),
    econ: Economics | None = None,
) -> dict[str, float]:
    """NLP's gross proceeds and MOIC at a given portfolio outcome.

    NLP is repaid its $35M first, then takes 14.1% of the rest, so it is whole
    as long as the remaining portfolio returns at least $35M against a $360M
    carrying value - that is the protection it is paying the 35% discount for.
    """
    econ = econ or derive(terms)
    repaid = min(total_future_proceeds, terms.check)
    tail = econ.tail_nlp_total * max(total_future_proceeds - terms.check, 0.0)
    proceeds = repaid + tail
    return {
        "total_future_proceeds": total_future_proceeds,
        "pref_repaid": repaid,
        "tail_proceeds": tail,
        "total_proceeds": proceeds,
        "moic": proceeds / terms.check,
    }
