"""The v2 rule: NLPI takes 12.6% of every exit cheque, without exception.

NLPI holds the shares directly where it can (the India-domiciled portcos) and
takes the same 12.6% through a company-level put/call where it cannot (the
Delaware and Singapore entities), so the buyer writes two cheques at every
exit regardless of domicile. That uniformity is what keeps the preference at a
single number and the sharing ratios flat.

Pins the figures in docs/TERM_SHEET_V2.md §7 and §9.
"""
from __future__ import annotations

import unittest

from deal_agent.terms import DealTerms, derive, pref_consistency
from deal_agent.waterfall import (
    DOCUMENT_EXITS,
    PREF_AT_X2,
    ExitEvent,
    SplitConvention,
    run_waterfall,
)

TERMS = DealTerms()
ECON = derive(DealTerms())


class TwoLegsTest(unittest.TestCase):
    """§7 — the preference and NLPI's own sales add to 10x of the feeder's $3.5M."""

    def test_pref_is_87_4_pct_of_the_cheque(self):
        self.assertAlmostEqual(PREF_AT_X2, (1 - TERMS.x2_portco) * TERMS.check, places=2)
        self.assertAlmostEqual(PREF_AT_X2 / TERMS.feeder_contribution, 8.74, places=2)

    def test_the_legs_add_to_ten_times(self):
        check = pref_consistency(TERMS.x2_portco)
        self.assertAlmostEqual(check["consistent_multiple"], 8.74, places=2)
        self.assertAlmostEqual(check["second_leg_multiple"], 1.26, places=2)
        self.assertAlmostEqual(
            check["consistent_multiple"] + check["second_leg_multiple"], 10.0, places=6
        )


class WorkedExampleTest(unittest.TestCase):
    """§9 — the previous version's own three tranches, corrected."""

    def setUp(self):
        self.result = run_waterfall(
            DOCUMENT_EXITS, convention=SplitConvention.STRUCTURE, liqpref=PREF_AT_X2
        )

    def test_wheelseye(self):
        dist = self.result.events[0]
        self.assertAlmostEqual(dist.nlpi_direct, 2.52, places=2)
        self.assertAlmostEqual(dist.sb2_receipts, 17.48, places=2)
        self.assertAlmostEqual(dist.to_nlpf_pref, 17.48, places=2)
        self.assertAlmostEqual(2.5 * TERMS.x2_portco, 0.315, places=4)

    def test_priority_clears_on_the_first_35m(self):
        first_two = self.result.events[:2]
        self.assertAlmostEqual(first_two[-1].pref_outstanding_after, 0.0, places=6)
        direct = sum(d.nlpi_direct for d in first_two)
        pref = sum(d.to_nlpf_pref for d in first_two)
        self.assertAlmostEqual(direct, 4.41, places=2)
        self.assertAlmostEqual(pref, 30.59, places=2)
        self.assertAlmostEqual(direct + pref, TERMS.check, places=2)

    def test_tail_tranche(self):
        dist = self.result.events[2]
        self.assertAlmostEqual(dist.nlpi_direct, 1.26, places=2)
        self.assertAlmostEqual(dist.class_a, 3.14, places=2)
        self.assertAlmostEqual(dist.class_b1, 5.45, places=2)
        self.assertAlmostEqual(dist.class_b2_nlpf, 0.15, places=2)

    def test_totals(self):
        totals = self.result.totals
        self.assertAlmostEqual(totals["nlp_total"], 36.41, places=2)
        self.assertAlmostEqual(totals["class_a"], 3.14, places=2)
        self.assertAlmostEqual(totals["class_b1_old_lps"], 5.45, places=2)


class FlatRatiosTest(unittest.TestCase):
    """§8 — once the preference is spent the ratios are flat, at any size or order."""

    def test_sb2_internal_split(self):
        self.assertAlmostEqual(ECON.sb2_share_class_a, 0.3593, places=4)
        self.assertAlmostEqual(ECON.sb2_share_class_b1, 0.6236, places=4)
        self.assertAlmostEqual(ECON.sb2_share_class_b2, 0.0172, places=4)
        self.assertAlmostEqual(
            ECON.sb2_share_class_a + ECON.sb2_share_class_b1 + ECON.sb2_share_class_b2,
            1.0,
            places=9,
        )

    def test_absolute_ratios_hold_on_any_exit_after_the_priority(self):
        for size in (5.0, 40.0, 250.0):
            result = run_waterfall(
                [ExitEvent("clear", 40.0), ExitEvent("tail", size)], liqpref=PREF_AT_X2
            )
            dist = result.events[1]
            self.assertAlmostEqual(dist.class_a / size, ECON.tail_class_a, places=6)
            self.assertAlmostEqual(dist.class_b1 / size, ECON.tail_class_b1, places=6)
            self.assertAlmostEqual(dist.nlp_total / size, ECON.tail_nlp_total, places=6)


if __name__ == "__main__":
    unittest.main()


class RoutingModelTest(unittest.TestCase):
    """Routing the cheque differently changes the plumbing, not the economics.

    Pins the two models in docs/ROUTING_MODELS.md.
    """

    def test_ten_percent_offshore(self):
        from deal_agent.terms import routing_model

        terms, econ, pref = routing_model(0.10)
        self.assertAlmostEqual(terms.feeder_contribution, 3.50, places=2)
        self.assertAlmostEqual(terms.onshore_contribution, 31.50, places=2)
        self.assertAlmostEqual(terms.x1_class_b, 0.0141, places=6)
        self.assertAlmostEqual(terms.x2_portco, 0.1269, places=6)
        self.assertAlmostEqual(pref, 30.56, places=2)
        self.assertAlmostEqual(pref / terms.feeder_contribution, 8.73, places=2)
        self.assertAlmostEqual(econ.sb2_share_class_b2, 0.0161, places=4)

    def test_twenty_percent_offshore(self):
        from deal_agent.terms import routing_model

        terms, econ, pref = routing_model(0.20)
        self.assertAlmostEqual(terms.feeder_contribution, 7.00, places=2)
        self.assertAlmostEqual(terms.onshore_contribution, 28.00, places=2)
        self.assertAlmostEqual(terms.x1_class_b, 0.0282, places=6)
        self.assertAlmostEqual(terms.x2_portco, 0.1128, places=6)
        self.assertAlmostEqual(pref, 31.05, places=2)
        self.assertAlmostEqual(pref / terms.feeder_contribution, 4.44, places=2)
        self.assertAlmostEqual(econ.sb2_share_class_b2, 0.0318, places=4)

    def test_the_economics_are_identical_across_routings(self):
        from deal_agent.terms import routing_model

        for fraction in (0.05, 0.10, 0.20, 0.35, 0.50):
            terms, econ, pref = routing_model(fraction)
            # x1 + x2 is NLP's whole share, and the absolute split never moves
            self.assertAlmostEqual(terms.x1_class_b + terms.x2_portco, 0.141, places=9)
            self.assertAlmostEqual(econ.tail_class_a, 0.314, places=9)
            self.assertAlmostEqual(econ.tail_class_b1, 0.545, places=9)
            self.assertAlmostEqual(econ.tail_nlp_total, 0.141, places=9)
            # both vehicles always pay the same price per unit of economics
            feeder_price = terms.feeder_contribution / (terms.x1_class_b * terms.nav)
            onshore_price = terms.onshore_contribution / (terms.x2_portco * terms.nav)
            self.assertAlmostEqual(feeder_price, onshore_price, places=9)
            # and the two legs always return exactly the cheque
            self.assertAlmostEqual(pref + terms.x2_portco * terms.check, terms.check, places=9)

    def test_the_two_legs_total_the_inverse_of_the_offshore_fraction(self):
        from deal_agent.terms import routing_model

        for fraction in (0.10, 0.20, 0.25):
            terms, _, pref = routing_model(fraction)
            legs = terms.check / terms.feeder_contribution
            self.assertAlmostEqual(legs, 1 / fraction, places=6)
            self.assertAlmostEqual(
                (pref + terms.x2_portco * terms.check) / terms.feeder_contribution,
                legs,
                places=6,
            )

    def test_worked_exits_under_both_models(self):
        from deal_agent.terms import routing_model

        expected = {
            0.10: [(2.54, 17.46, 17.46), (1.90, 13.10, 13.10), (1.27, 8.73, 0.0)],
            0.20: [(2.26, 17.74, 17.74), (1.69, 13.31, 13.31), (1.13, 8.87, 0.0)],
        }
        for fraction, rows in expected.items():
            terms, econ, pref = routing_model(fraction)
            result = run_waterfall(
                DOCUMENT_EXITS, terms=terms, econ=econ,
                convention=SplitConvention.STRUCTURE, liqpref=pref,
            )
            for dist, (direct, sb2, to_pref) in zip(result.events, rows):
                self.assertAlmostEqual(dist.nlpi_direct, direct, places=2)
                self.assertAlmostEqual(dist.sb2_receipts, sb2, places=2)
                self.assertAlmostEqual(dist.to_nlpf_pref, to_pref, places=2)
            # the tail tranche lands on the same absolute split either way
            tail = result.events[2]
            self.assertAlmostEqual(tail.class_a, 3.14, places=2)
            self.assertAlmostEqual(tail.class_b1, 5.45, places=2)
            self.assertAlmostEqual(tail.nlp_total, 1.41, places=2)
