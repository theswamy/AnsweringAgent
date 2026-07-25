"""Unit tests for the deterministic outreach core.

Stage strings are taken verbatim from the live MicroVC Sourcing board so the
gate is tested against real-world messiness, not idealized inputs.
"""
from __future__ import annotations

import pytest

from app.outreach.emailguess import (
    clean_founder_name,
    domain_from_website,
    email_candidates,
    looks_like_person,
)
from app.outreach.models import (
    Candidate,
    QualificationVerdict,
    StageVerdict,
)
from app.outreach.qualify import classify_stage, qualify
from app.outreach.template import (
    render_first_touch,
    render_subject,
    sector_to_domain_area,
)


# --------------------------------------------------------------------------- #
# Stage gate                                                                    #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "text,expected",
    [
        ("Pre-Seed", StageVerdict.QUALIFIED),
        ("Seed", StageVerdict.QUALIFIED),
        ("Seed (incubation)", StageVerdict.QUALIFIED),
        ("Pre-Series A", StageVerdict.QUALIFIED),
        ("Pre-Series A follow-on", StageVerdict.QUALIFIED),
        ("Series A", StageVerdict.QUALIFIED),
        ("Series B", StageVerdict.TOO_LATE),
        ("Series C (follow-on)", StageVerdict.TOO_LATE),
        ("Late Stage (follow-on)", StageVerdict.TOO_LATE),
        ("Growth", StageVerdict.TOO_LATE),
        ("", StageVerdict.UNKNOWN),
        (None, StageVerdict.UNKNOWN),
    ],
)
def test_classify_stage(text, expected):
    verdict, _ = classify_stage(text)
    assert verdict is expected


def test_classify_stage_takes_latest_round_across_fields():
    # A Seed company that later did a Series B is a Series B company.
    verdict, _ = classify_stage("Seed", "Series B")
    assert verdict is StageVerdict.TOO_LATE


def test_pre_series_a_not_confused_with_series_a_letter():
    verdict, _ = classify_stage("Pre-Series A")
    assert verdict is StageVerdict.QUALIFIED


def _cand(**kw) -> Candidate:
    base = dict(item_id="1", name="Acme", group_title="Kae Capital",
                outreach_status="To Reach Out")
    base.update(kw)
    return Candidate(**base)


def test_qualify_too_late_is_disqualified_with_reason():
    res = qualify(_cand(stage_text="Series C (follow-on)"))
    assert res.verdict is QualificationVerdict.DISQUALIFIED
    assert "Too Late for Prime" in res.reason


def test_qualify_seed_passes():
    res = qualify(_cand(stage_text="Seed"))
    assert res.verdict is QualificationVerdict.QUALIFIED


def test_qualify_skips_items_already_in_pipeline():
    res = qualify(_cand(outreach_status="Sent", stage_text="Seed"))
    assert res.verdict is QualificationVerdict.SKIPPED


def test_qualify_respects_target_fund_allowlist():
    res = qualify(_cand(group_title="Some Other Fund", stage_text="Seed"),
                  target_funds={"Kae Capital"})
    assert res.verdict is QualificationVerdict.SKIPPED


def test_qualify_unknown_stage_default_in_but_flagged():
    res = qualify(_cand(stage_text=None, last_round_type=None))
    assert res.verdict is QualificationVerdict.QUALIFIED
    assert "unknown" in res.reason.lower()


# --------------------------------------------------------------------------- #
# Founder name / email guessing                                                 #
# --------------------------------------------------------------------------- #
def test_clean_founder_name_strips_titles_and_parens():
    assert clean_founder_name("Abhinav Kumar (CEO, IIT Delhi)") == "Abhinav Kumar"
    assert clean_founder_name("Aditya Varma (CEO)") == "Aditya Varma"
    assert clean_founder_name("Unknown") is None
    assert clean_founder_name("") is None


def test_looks_like_person_rejects_company_name_and_unknown():
    assert looks_like_person("Arjun Singh", "Gully Labs") is True
    assert looks_like_person("Catalogus", "Catalogus") is False
    assert looks_like_person("Onya Diamonds", "ONYA (ONYA Diamonds)") is False
    assert looks_like_person("Unknown", "Elevate Now") is False


def test_domain_from_website():
    assert domain_from_website("https://gullylabs.in") == "gullylabs.in"
    assert domain_from_website("www.example.com/about") == "example.com"
    assert domain_from_website("http://foo.co.in") == "foo.co.in"
    assert domain_from_website(None) is None


def test_email_candidates_priority_order():
    cands = email_candidates("Arjun Singh", "gullylabs.in")
    assert cands[0] == "arjun@gullylabs.in"
    assert cands[1] == "arjun.singh@gullylabs.in"
    assert "asingh@gullylabs.in" in cands
    # de-duplicated
    assert len(cands) == len(set(cands))


def test_email_candidates_single_token_name():
    cands = email_candidates("Cher", "brand.com")
    assert cands == ["cher@brand.com"]


def test_email_candidates_needs_domain_and_name():
    assert email_candidates("Arjun Singh", "") == []
    assert email_candidates("Unknown", "brand.com") == []


# --------------------------------------------------------------------------- #
# Template                                                                      #
# --------------------------------------------------------------------------- #
def test_sector_to_domain_area():
    assert sector_to_domain_area("d2c_consumer") == "consumer brands and D2C"
    assert sector_to_domain_area("ai_ml") == "applied AI"
    assert sector_to_domain_area("other") is None
    assert sector_to_domain_area(None) is None
    assert sector_to_domain_area("healthtech") == "healthcare and health-tech"


def test_render_first_touch_fills_all_slots():
    body = render_first_touch(
        first_name="Arjun",
        domain_area="consumer brands and D2C",
        calendly_url="https://calendly.com/sanjay-prime/30min",
    )
    assert "Hi Arjun" in body
    assert "Your space of consumer brands and D2C" in body
    assert "https://calendly.com/sanjay-prime/30min" in body
    assert "{{" not in body  # no unfilled slots


def test_render_first_touch_requires_nonempty_slots():
    with pytest.raises(ValueError):
        render_first_touch(first_name="", domain_area="x", calendly_url="y")


def test_render_subject():
    assert render_subject("Gully Labs") == "PrimeVP <> Gully Labs"
