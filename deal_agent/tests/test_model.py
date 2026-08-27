"""The document is the test oracle.

Every number the document states about itself is asserted here, against the
model that the agent answers from. Where the document contradicts itself the
test pins both readings and names the finding, so the contradiction cannot be
"fixed" by quietly changing the model.

    python -m unittest discover -s deal_agent/tests -t .
"""
from __future__ import annotations

import unittest

from deal_agent import document, tools
from deal_agent.findings import BY_ID, FINDINGS
from deal_agent.terms import (
    DealTerms,
    derive,
    nlp_returns,
    old_lp_tradeoff,
    pref_consistency,
)
from deal_agent.waterfall import (
    DOCUMENT_EXITS,
    ExitEvent,
    SplitConvention,
    run_waterfall,
)

TERMS = DealTerms()
ECON = derive(TERMS)


class TestStatedArithmetic(unittest.TestCase):
    """[S1][S3] - the document's own summary figures."""

    def test_commitments_are_2_98(self):
        self.assertAlmostEqual(TERMS.class_a_share_of_commitments, 0.02, places=4)
        self.assertAlmostEqual(TERMS.class_b_share_of_commitments, 0.98, places=4)

    def test_profit_above_roc_is_325(self):
        self.assertAlmostEqual(ECON.profit_above_roc, 325.0)

    def test_gp_stake_is_about_100m_at_31_4_pct(self):
        self.assertAlmostEqual(ECON.class_a_profit_share, 0.314, places=4)
        self.assertAlmostEqual(ECON.gp_value, 100.0, delta=2.1)  # "about $100M"

    def test_lp_profits_about_225m_and_lp_nav_about_260m(self):
        self.assertAlmostEqual(ECON.class_b_profit_value, 225.0, delta=2.1)
        self.assertAlmostEqual(ECON.lp_nav, 260.0, delta=3.0)

    def test_cheque_is_13_pct_of_lp_and_20_pct_after_discount(self):
        self.assertAlmostEqual(ECON.nlp_pct_of_lp_undiscounted, 0.13, delta=0.007)
        self.assertAlmostEqual(ECON.nlp_pct_of_lp_discounted, 0.20, delta=0.010)

    def test_derived_nlp_share_is_close_to_the_stated_14_1_pct(self):
        self.assertAlmostEqual(ECON.nlp_derived_profit_share, 0.141, delta=0.003)


class TestCapTable(unittest.TestCase):
    def test_stated_post_roc_cap_table_does_not_close(self):
        """F1: [S2] sums to 101%."""
        stated = TERMS.stated_post_roc_class_a + TERMS.stated_post_roc_class_b
        self.assertAlmostEqual(stated, 1.01, places=4)
        self.assertAlmostEqual(ECON.class_b_profit_share, 0.686, places=3)

    def test_tail_closes_to_100_pct(self):
        """[S4] - and this is what confirms Class B is 68.6%, not 69.6%."""
        self.assertAlmostEqual(
            ECON.tail_class_a + ECON.tail_class_b1 + ECON.tail_nlp_total, 1.0, places=9
        )
        self.assertAlmostEqual(ECON.tail_class_b1, 0.545, places=3)

    def test_class_a_is_not_diluted_by_the_secondary(self):
        self.assertAlmostEqual(ECON.tail_class_a, ECON.class_a_profit_share, places=4)
        self.assertAlmostEqual(
            ECON.tail_class_b1 + ECON.tail_nlp_total, ECON.class_b_profit_share, places=4
        )

    def test_sb2_internal_shares_match_the_document(self):
        """[S10] - 35.3% / 62.5% / 2.27% of SB2's receipts."""
        self.assertAlmostEqual(ECON.sb2_share_class_a, 0.353, delta=0.007)
        self.assertAlmostEqual(ECON.sb2_share_class_b1, 0.625, delta=0.002)
        self.assertAlmostEqual(ECON.sb2_share_class_b2, 0.0227, delta=0.006)

    def test_88_12_split_of_the_buyers_cheque(self):
        """[S10] - 88% to SB2, 12% to NLPI, against x2 = 12.6%."""
        self.assertAlmostEqual(ECON.sb2_share_of_proceeds, 0.874, places=4)


class TestLiqPref(unittest.TestCase):
    def test_pref_is_the_cheque_net_of_a_1_4_pct_slice_as_stated(self):
        """[S5] - 9.86x on $3.5M, i.e. 98.6% of the $35M cheque."""
        self.assertAlmostEqual(TERMS.feeder_contribution, 3.5)
        self.assertAlmostEqual(TERMS.onshore_contribution, 31.5)
        self.assertAlmostEqual(TERMS.feeder_liqpref, 34.51, places=6)
        self.assertAlmostEqual(
            TERMS.feeder_liqpref, (1 - TERMS.x1_class_b) * TERMS.check, places=6
        )

    def test_document_exit_a_reproduced_exactly(self):
        """[S8] - SB2 $19.72M, NLP $0.28M, all of SB2's share to the pref."""
        dist = run_waterfall(
            DOCUMENT_EXITS[:1], convention=SplitConvention.DOC_EXAMPLES
        ).events[0]
        self.assertAlmostEqual(dist.sb2_receipts, 19.72, places=2)
        self.assertAlmostEqual(dist.nlpi_direct, 0.28, places=2)
        self.assertAlmostEqual(dist.to_nlpf_pref, 19.72, places=2)
        self.assertEqual(dist.class_a, 0.0)

    def test_document_exit_b_a_reproduced_exactly(self):
        """[S9] - SB2 $14.79M, NLPI $0.21M."""
        dist = run_waterfall(
            DOCUMENT_EXITS[:2], convention=SplitConvention.DOC_EXAMPLES
        ).events[1]
        self.assertAlmostEqual(dist.sb2_receipts, 14.79, places=2)
        self.assertAlmostEqual(dist.nlpi_direct, 0.21, places=2)

    def test_marker_is_now_exact_on_the_documents_own_split(self):
        """F3, closed - (19.72 + 14.79) / 3.5 = 9.86 clears the pref to the cent,
        and repays NLP exactly its $35M across both entities."""
        result = run_waterfall(DOCUMENT_EXITS[:2], convention=SplitConvention.DOC_EXAMPLES)
        self.assertTrue(result.pref_satisfied)
        self.assertAlmostEqual(result.totals["nlp_via_pref"], 34.51, places=6)
        self.assertAlmostEqual(result.totals["nlp_total"], TERMS.check, places=6)
        self.assertEqual(result.totals["class_a"], 0.0)

    def test_the_same_exits_leave_the_pref_outstanding_at_x2(self):
        """F2/F14 - the 9.86x sizing assumes a 1.4% onshore slice."""
        result = run_waterfall(DOCUMENT_EXITS[:2])
        self.assertFalse(result.pref_satisfied)
        self.assertAlmostEqual(result.pref_outstanding, 3.92, places=2)
        # NLP is still repaid exactly its 1x at $35M of exits - it is the pref
        # running past that point, not the repayment, that costs the other classes.
        self.assertAlmostEqual(result.totals["nlp_total"], TERMS.check, places=6)

    def test_pref_multiple_is_a_function_of_the_onshore_slice(self):
        """The stated 9.86x is what nets off x1; 8.74x is what nets off x2.

        Only a portco-level slice reaches NLP without passing through SB2, so
        x2 is the basis the principle requires - x1 is a fund-level interest and
        the pref already takes 100% of SB2's receipts while it runs.
        """
        at_x1 = pref_consistency(TERMS.x1_class_b)
        self.assertAlmostEqual(at_x1["consistent_multiple"], 9.86, places=6)
        self.assertAlmostEqual(at_x1["consistent_pref"], TERMS.feeder_liqpref, places=6)

        at_x2 = pref_consistency(TERMS.x2_portco)
        self.assertAlmostEqual(at_x2["consistent_multiple"], 8.74, places=6)
        self.assertAlmostEqual(at_x2["consistent_pref"], 30.59, places=6)
        self.assertAlmostEqual(at_x2["over_recovery"], 4.49, places=2)

    def test_nothing_reaches_nlp_outside_the_pref_on_account_of_x1(self):
        """Why 9.86x's $0.49M is phantom: while the pref runs, SB2 distributes
        100% to NLPF, so the feeder's Class B2 share is zero until it clears."""
        during = run_waterfall(DOCUMENT_EXITS[:1]).events[0]
        self.assertGreater(during.to_nlpf_pref, 0.0)
        self.assertEqual(during.class_b2_nlpf, 0.0)
        self.assertEqual(during.class_a, 0.0)

    def test_an_8_74x_pref_clears_exactly_at_x2(self):
        result = run_waterfall(DOCUMENT_EXITS[:2], liqpref=30.59)
        self.assertTrue(result.pref_satisfied)
        self.assertAlmostEqual(result.totals["nlp_total"], TERMS.check, places=6)

    def test_pref_is_satisfied_across_the_document_exits_either_way(self):
        for convention in SplitConvention:
            result = run_waterfall(DOCUMENT_EXITS, convention=convention)
            self.assertTrue(result.pref_satisfied, convention)
            self.assertAlmostEqual(
                result.totals["nlp_via_pref"], TERMS.feeder_liqpref, places=6
            )

    def test_tail_shares_apply_once_the_pref_is_repaid(self):
        """[S10] - "from now on for all subsequent distributions".

        The stated absolute shares (31.4 / 54.5 / 14.1) only hold on an exit that
        happens entirely after the pref is repaid. A tranche that straddles the
        pref is split, which is the mechanical half of finding F3.
        """
        result = run_waterfall([ExitEvent("Freo", 45.0), ExitEvent("KredX", 100.0)])
        self.assertTrue(result.pref_satisfied)

        steady = result.events[1]
        self.assertAlmostEqual(steady.class_a / 100.0, ECON.tail_class_a, places=6)
        self.assertAlmostEqual(steady.class_b1 / 100.0, ECON.tail_class_b1, places=6)
        self.assertAlmostEqual(steady.nlp_total / 100.0, ECON.tail_nlp_total, places=6)

    def test_a_straddling_tranche_is_split_not_shared_pro_rata(self):
        """The transition exit pays the pref first, so Class A's slice of it is
        below 31.4% - the document's tail table cannot be applied to it."""
        dist = run_waterfall([ExitEvent("Freo", 435.0)]).events[0]
        self.assertLess(dist.class_a / (435.0 - TERMS.check), ECON.tail_class_a)


class TestSplitConventions(unittest.TestCase):
    def test_x1_substituted_for_x2_in_the_worked_exits(self):
        """F2/F12 - 2.5% x x2 is 0.315% of WheelsEye, not the stated 0.035%."""
        self.assertAlmostEqual(0.025 * TERMS.x2_portco, 0.00315, places=6)
        self.assertAlmostEqual(0.025 * TERMS.x1_class_b, 0.00035, places=6)

    def test_convention_moves_2_24m_on_the_20m_exit(self):
        structure = run_waterfall(DOCUMENT_EXITS[:1]).events[0]
        as_written = run_waterfall(
            DOCUMENT_EXITS[:1], convention=SplitConvention.DOC_EXAMPLES
        ).events[0]
        self.assertAlmostEqual(structure.nlpi_direct - as_written.nlpi_direct, 2.24, places=2)

    def test_x1_denominators_disagree(self):
        """F4 - 1.4% of Class B is 0.96% of absolute; the tail needs ~1.5%."""
        self.assertAlmostEqual(
            TERMS.x1_class_b * ECON.class_b_profit_share, 0.0096, places=4
        )
        self.assertAlmostEqual(ECON.tail_nlp_feeder, 0.015, places=4)


class TestOutcomes(unittest.TestCase):
    def test_nlp_is_protected_until_the_portfolio_returns_less_than_the_cheque(self):
        self.assertAlmostEqual(nlp_returns(35.0)["moic"], 1.0, places=6)
        self.assertLess(nlp_returns(20.0)["moic"], 1.0)

    def test_nlp_makes_2_3x_at_the_carrying_value(self):
        self.assertAlmostEqual(nlp_returns(360.0)["moic"], 2.31, places=2)

    def test_old_lps_give_up_about_45m_at_the_carrying_value(self):
        trade = old_lp_tradeoff(360.0)
        self.assertAlmostEqual(trade["difference"], -45.1, delta=0.1)

    def test_old_lps_indifference_point_is_low(self):
        """F13 - about $40M of total future proceeds against a $360M carrying value."""
        trade = old_lp_tradeoff(360.0)
        self.assertAlmostEqual(trade["breakeven_total_proceeds"], 40.0, delta=0.5)
        at_breakeven = old_lp_tradeoff(trade["breakeven_total_proceeds"])
        self.assertAlmostEqual(at_breakeven["difference"], 0.0, places=6)

    def test_nothing_is_created_or_destroyed(self):
        """Every dollar of every exit lands with exactly one party."""
        for convention in SplitConvention:
            for counts in (False, True):
                result = run_waterfall(
                    DOCUMENT_EXITS + [ExitEvent("KredX", 120.0)],
                    convention=convention,
                    count_direct_against_pref=counts,
                )
                paid = sum(
                    d.nlpi_direct + d.to_nlpf_pref + d.class_a + d.class_b1 + d.class_b2_nlpf
                    for d in result.events
                )
                self.assertAlmostEqual(paid, result.total_proceeds, places=6)


class TestDocumentAndFindings(unittest.TestCase):
    def test_every_section_is_reachable_and_cited_by_a_finding(self):
        cited = {s for finding in FINDINGS for s in finding.sections}
        self.assertEqual(set(document.BY_ID) - cited, set())

    def test_findings_reference_real_sections(self):
        for finding in FINDINGS:
            for section in finding.sections:
                self.assertIn(section, document.BY_ID, f"{finding.id} cites {section}")

    def test_finding_evidence_still_computes(self):
        for finding in FINDINGS:
            self.assertIsInstance(finding.evidence(), str)

    def test_search_finds_the_pref_sections(self):
        self.assertIn("S9", [s.id for s in document.search("liqpref satisfied niyo")])

    def test_section_id_lookup(self):
        self.assertIn("WheelsEye at $800M", tools.read_document("S8"))

    def test_source_text_carries_the_9_86x_restatement(self):
        """If the document is revised again, the model must not drift from it."""
        self.assertIn("9.86", document.BY_ID["S5"].text)
        self.assertIn("(19.72+14.79)/3.5 = 9.86", document.BY_ID["S9"].text)

    def test_closed_findings_are_kept_with_their_evidence(self):
        closed = [f for f in FINDINGS if f.status == "closed"]
        self.assertEqual({f.id for f in closed}, {"F3", "F5"})
        for finding in closed:
            self.assertIn("CLOSED", finding.title)


class TestTools(unittest.TestCase):
    def test_every_schema_has_an_implementation(self):
        for schema in tools.TOOL_SCHEMAS:
            self.assertIn(schema["name"], tools.DISPATCH)

    def test_bad_tool_call_is_reported_not_raised(self):
        self.assertIn("failed", tools.call("model_exits", {"exits": [{"portco": "x"}]}))
        self.assertIn("Unknown tool", tools.call("nope", {}))

    def test_terms_tool_is_json(self):
        import json

        payload = json.loads(tools.deal_terms())
        self.assertAlmostEqual(payload["recomputed"]["class_b_profit_share"], 0.686, places=3)

    def test_offline_answerer_covers_its_advertised_topics(self):
        from deal_agent.agent import OfflineAnswerer

        agent = OfflineAnswerer()
        for question in (
            "what is the cap table",
            "why is the liqpref a problem",
            "walk me through the wheelseye exit",
            "is this worth it for the old LPs",
            "what are the high severity findings",
            "explain the entity structure",
            "how was the price set",
        ):
            answer = agent.ask(question)
            self.assertNotIn("cannot answer", answer, question)
            self.assertGreater(len(answer), 200, question)


if __name__ == "__main__":
    unittest.main()
