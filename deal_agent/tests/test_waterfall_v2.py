"""The v2 waterfall: NLP's entitlement stated in aggregate, topped up by SB2.

These tests pin the numbers quoted in docs/TERM_SHEET_V2.md, and the two
properties that motivate the rewrite: the split is exact whatever the mix of
exits, and - with the cap - whatever order they happen in.

    python -m unittest discover -s deal_agent/tests -t .
"""
from __future__ import annotations

import random
import unittest

from deal_agent.terms import DealTerms, derive
from deal_agent.waterfall import (
    ExitV2,
    Venue,
    onshore_stake,
    run_waterfall_v2,
)

TERMS = DealTerms()
ECON = derive(TERMS)

#: The worked example in §9: the previous version's own two exits, corrected.
BASE_CASE = [
    ExitV2("WheelsEye", 20.0, Venue.ONSHORE, 800.0),
    ExitV2("Niyo", 15.0, Venue.ONSHORE, 500.0),
    ExitV2("Niyo", 10.0, Venue.ONSHORE, 500.0),
]


def _targets(total: float) -> dict[str, float]:
    pool = max(total - TERMS.check, 0.0)
    return {
        "class_a": ECON.tail_class_a * pool,
        "class_b1_old_lps": ECON.tail_class_b1 * pool,
        "nlp_total": min(total, TERMS.check) + ECON.tail_nlp_total * pool,
    }


class WorkedExampleTest(unittest.TestCase):
    """§9 of the term sheet, line by line."""

    def setUp(self):
        self.result = run_waterfall_v2(BASE_CASE, theta=1.0)

    def test_nlpi_holds_12_6_pct_of_every_position(self):
        self.assertAlmostEqual(self.result.onshore_stake, 0.126, places=6)

    def test_wheelseye_line(self):
        dist = self.result.events[0]
        self.assertAlmostEqual(dist.nlpi_direct, 2.52, places=2)
        self.assertAlmostEqual(dist.sb2_receipts, 17.48, places=2)
        self.assertAlmostEqual(dist.top_up_priority, 17.48, places=2)
        self.assertEqual((dist.class_a, dist.class_b1), (0.0, 0.0))
        self.assertAlmostEqual(dist.priority_outstanding_after, 15.0, places=2)
        # 2.5% of the company sold: NLPI 0.315%, SB2 2.185%
        self.assertAlmostEqual(2.5 * TERMS.x2_portco, 0.315, places=4)

    def test_priority_is_satisfied_exactly_on_the_first_35m(self):
        first_two = self.result.events[:2]
        self.assertAlmostEqual(first_two[-1].priority_outstanding_after, 0.0, places=9)
        direct = sum(d.nlpi_direct for d in first_two)
        pref = sum(d.top_up_priority for d in first_two)
        self.assertAlmostEqual(direct, 4.41, places=2)
        self.assertAlmostEqual(pref, 30.59, places=2)
        self.assertAlmostEqual(direct + pref, TERMS.check, places=6)
        # the two legs, on the feeder's $3.5M
        self.assertAlmostEqual(pref / TERMS.feeder_contribution, 8.74, places=2)
        self.assertAlmostEqual(direct / TERMS.feeder_contribution, 1.26, places=2)

    def test_tail_tranche_splits_four_ways(self):
        dist = self.result.events[2]
        self.assertAlmostEqual(dist.nlpi_direct, 1.26, places=2)
        self.assertAlmostEqual(dist.top_up_tail, 0.15, places=2)
        self.assertAlmostEqual(dist.class_a, 3.14, places=2)
        self.assertAlmostEqual(dist.class_b1, 5.45, places=2)

    def test_totals(self):
        totals = self.result.totals
        self.assertAlmostEqual(totals["nlp_total"], 36.41, places=2)
        self.assertAlmostEqual(totals["class_a"], 3.14, places=2)
        self.assertAlmostEqual(totals["class_b1_old_lps"], 5.45, places=2)
        self.assertAlmostEqual(
            sum(totals[k] for k in ("nlp_total", "class_a", "class_b1_old_lps")),
            self.result.total_proceeds,
            places=6,
        )


class MixAndOrderTest(unittest.TestCase):
    """§6 and §8: the properties a fixed preference multiple cannot deliver."""

    def test_onshore_stake_is_grossed_up_for_theta(self):
        self.assertAlmostEqual(onshore_stake(1.0), 0.126, places=6)
        self.assertAlmostEqual(onshore_stake(0.70), 0.18, places=6)
        with self.assertRaises(ValueError):
            onshore_stake(0.0)

    def test_exact_whatever_the_venue_mix(self):
        for venue in Venue:
            result = run_waterfall_v2([ExitV2("p", 120.0, venue)], theta=0.70)
            targets = _targets(120.0)
            for key, want in targets.items():
                self.assertAlmostEqual(result.totals[key], want, places=6, msg=f"{venue} {key}")

    def test_exact_whatever_the_order_with_the_cap(self):
        onshore = [ExitV2(f"on{i}", 252 / 6, Venue.ONSHORE) for i in range(6)]
        mauritius = [ExitV2(f"off{i}", 108 / 3, Venue.MAURITIUS) for i in range(3)]
        orderings = [mauritius + onshore, onshore + mauritius]
        rng = random.Random(11)
        for _ in range(6):
            shuffled = onshore + mauritius
            rng.shuffle(shuffled)
            orderings.append(list(shuffled))

        for order in orderings:
            result = run_waterfall_v2(order, theta=0.70)
            targets = _targets(360.0)
            for key, want in targets.items():
                self.assertAlmostEqual(result.totals[key], want, places=6, msg=key)

    def test_without_the_cap_the_order_matters(self):
        """The $9.8M in §8 - why the cap is required when theta < 89.4%."""
        onshore = [ExitV2(f"on{i}", 252 / 6, Venue.ONSHORE) for i in range(6)]
        mauritius = [ExitV2(f"off{i}", 108 / 3, Venue.MAURITIUS) for i in range(3)]
        result = run_waterfall_v2(
            mauritius + onshore, theta=0.70, cap_direct_to_entitlement=False
        )
        ahead = result.totals["nlp_total"] - _targets(360.0)["nlp_total"]
        self.assertAlmostEqual(ahead, 9.83, places=2)

    def test_the_cap_never_binds_in_the_base_case(self):
        """theta = 100% puts NLPI's stake at 12.6%, below its 14.1% tail share."""
        self.assertLess(onshore_stake(1.0), ECON.tail_nlp_total)
        self.assertAlmostEqual(
            TERMS.x2_portco / ECON.tail_nlp_total, 0.894, places=3  # the threshold in §8
        )
        capped = run_waterfall_v2(BASE_CASE, theta=1.0)
        uncapped = run_waterfall_v2(BASE_CASE, theta=1.0, cap_direct_to_entitlement=False)
        self.assertEqual(capped.totals, uncapped.totals)

    def test_the_implied_multiple_is_not_a_stable_term(self):
        """§7: same base case, different cheque boundaries, different multiple."""
        clean = run_waterfall_v2(BASE_CASE, theta=1.0).implied_pref_multiple
        self.assertAlmostEqual(clean, 8.74, places=2)

        straddling = run_waterfall_v2(
            [ExitV2("WheelsEye", 20.0, Venue.ONSHORE), ExitV2("Niyo", 25.0, Venue.ONSHORE)],
            theta=1.0,
        )
        self.assertNotAlmostEqual(straddling.implied_pref_multiple, 8.74, places=2)
        # ... with identical economics
        for key, want in _targets(45.0).items():
            self.assertAlmostEqual(straddling.totals[key], want, places=6, msg=key)


if __name__ == "__main__":
    unittest.main()
