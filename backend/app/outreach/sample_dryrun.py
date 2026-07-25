"""Read-only sample run for internal team review.

Runs the real qualifier + template over a captured batch of 25 companies from
the MicroVC Sourcing board (2026-04) and prints what the agent would do. It
writes NOTHING to monday and sends NOTHING. Purpose: let the team approve the
selection and the email voice before any live outreach.

    python -m app.outreach.sample_dryrun

The ``domain_area`` phrases below are what the Claude "brain" produces per
company in the live pipeline; they are inlined here so the sample is fully
deterministic and offline.
"""
from __future__ import annotations

from .emailguess import (
    clean_founder_name,
    domain_from_website,
    email_candidates,
    looks_like_person,
)
from .models import Candidate, QualificationVerdict
from .qualify import qualify
from .template import render_first_touch, render_subject

SAMPLE_CALENDLY = "https://calendly.com/sanjay-prime/30min"

# Captured from board 18410878634 (first 25 To-Reach-Out rows). Each tuple:
# (name, group/fund, founder, sector, website, stage, one_liner, domain_area)
BATCH: list[dict] = [
    dict(name="True Diamond", fund="Zeropearl VC", founder="Darayus Mehta", sector="d2c_consumer", website=None, stage="Pre-Series A", domain_area="lab-grown diamond jewellery"),
    dict(name="Gully Labs", fund="Zeropearl VC", founder="Arjun Singh", sector="d2c_consumer", website="https://gullylabs.in", stage="Series A", domain_area="homegrown footwear and streetwear"),
    dict(name="OZi", fund="Zeropearl VC", founder="Amit Sah", sector="other", website=None, stage="Seed", domain_area="consumer brands"),
    dict(name="Smylo", fund="Zeropearl VC", founder="Abhishek Agrawal", sector="d2c_consumer", website=None, stage="Pre-Series A follow-on", domain_area="pet nutrition and wellness"),
    dict(name="Cura Care", fund="Zeropearl VC", founder="Abhinav Kumar (CEO, IIT Delhi)", sector=None, website=None, stage="Pre-Seed", domain_area="at-home dental care"),
    dict(name="Catalogus", fund="Zeropearl VC", founder="Catalogus", sector="ai_ml", website=None, stage="Pre-Seed", domain_area="applied AI for e-commerce"),
    dict(name="Tryo", fund="Zeropearl VC", founder="Meet Saparia", sector="d2c_consumer", website=None, stage="Pre-Seed", domain_area="fashion commerce"),
    dict(name="Zanskar", fund="Zeropearl VC", founder="Anshul Mittal (IIT Delhi)", sector=None, website=None, stage="Seed", domain_area="science-backed wellness"),
    dict(name="Akinna", fund="Zeropearl VC", founder="Annika Saraf (CEO)", sector=None, website=None, stage="Pre-Seed", domain_area="luxury fashion and accessories"),
    dict(name="Supply6", fund="Zeropearl VC", founder="Vaibhav Bhandari (CEO)", sector=None, website=None, stage="Seed", domain_area="nutrition and wellness"),
    dict(name="Affluense AI", fund="Zeropearl VC", founder="Sumit Sahu (CEO)", sector=None, website=None, stage="Pre-Seed", domain_area="applied AI for wealth management"),
    dict(name="ONYA (ONYA Diamonds)", fund="Zeropearl VC", founder="Onya Diamonds", sector="d2c_consumer", website=None, stage="Pre-Seed", domain_area="lab-grown diamond jewellery"),
    dict(name="Frex", fund="Zeropearl VC", founder="Aditya Varma (CEO)", sector=None, website=None, stage="Pre-Seed", domain_area="cross-border payments"),
    dict(name="P-TAL", fund="Zeropearl VC", founder="Aditya Agrawal (CEO)", sector=None, website=None, stage="Seed", domain_area="heritage craft consumer brands"),
    dict(name="Boba Bhai", fund="Zeropearl VC", founder="Dhruv Kohli (CEO)", sector=None, website=None, stage="Series A", domain_area="new-age F&B and QSR"),
    dict(name="SteamPRO", fund="Zeropearl VC", founder="Sumir Chadha", sector="d2c_consumer", website=None, stage="Seed", domain_area="bath-tech and home wellness"),
    dict(name="Affordplan", fund="Unitary Helion", founder="Aditya Sharma", sector="healthtech", website=None, stage="Series C (follow-on)", domain_area="healthcare financing"),
    dict(name="Shubham Housing Finance", fund="Unitary Helion", founder="Nishant Bansal", sector="fintech", website=None, stage="Late Stage (follow-on)", domain_area="housing finance"),
    dict(name="Everhope Oncology", fund="W Health Ventures", founder="Everhope Oncology", sector="healthtech", website=None, stage="Seed (incubation)", domain_area="oncology care"),
    dict(name="BabyMD", fund="W Health Ventures", founder="Deeksha Senguttuvan", sector="healthtech", website=None, stage="Seed", domain_area="paediatric healthcare"),
    dict(name="Nivaan Care", fund="W Health Ventures", founder="Nivesh Khandelwal", sector="healthtech", website=None, stage="Series A", domain_area="pain management healthcare"),
    dict(name="Elevate Now", fund="W Health Ventures", founder="Unknown", sector="healthtech", website=None, stage="Seed", domain_area="metabolic health"),
    dict(name="BeatO", fund="W Health Ventures", founder="BeatO", sector="healthtech", website=None, stage="Series B", domain_area="diabetes management"),
    dict(name="Mylo", fund="W Health Ventures", founder="Vinit Garg", sector="healthtech", website=None, stage="Series B", domain_area="parenting and mother-and-baby care"),
    dict(name="Good Health Company", fund="W Health Ventures", founder="Samarth Sindhi", sector="healthtech", website=None, stage="Seed", domain_area="healthcare services"),
]


def _candidate(row: dict) -> Candidate:
    return Candidate(
        item_id=row["name"], name=row["name"], group_title=row["fund"],
        outreach_status="To Reach Out", stage_text=row["stage"],
        last_round_type=row["stage"], best_founder=row["founder"],
        sector_tag=row["sector"], website=row["website"],
    )


def run() -> None:
    qualified, disqualified, needs_info = [], [], []

    for row in BATCH:
        cand = _candidate(row)
        res = qualify(cand)
        if res.verdict is QualificationVerdict.DISQUALIFIED:
            disqualified.append((row, res))
            continue
        if res.verdict is QualificationVerdict.SKIPPED:
            continue
        # Qualified — can we address a real person and resolve an email?
        if not looks_like_person(row["founder"], row["name"]):
            needs_info.append((row, "founder name missing on board"))
            continue
        domain = domain_from_website(row["website"])
        emails = email_candidates(row["founder"], domain) if domain else []
        qualified.append((row, cand, domain, emails))

    n = len(BATCH)
    print(f"\n{'='*70}\n SAMPLE DRY RUN — {n} companies (batch of 25)  |  writes nothing\n{'='*70}")
    print(f"  Qualified & ready to personalize : {len(qualified)}")
    print(f"  Needs Info (founder lookup first): {len(needs_info)}")
    print(f"  Disqualified (past Series A)      : {len(disqualified)}")

    print(f"\n{'-'*70}\n DISQUALIFIED — set Outreach Status = Pass, reason 'Too Late for Prime'\n{'-'*70}")
    for row, res in disqualified:
        print(f"  • {row['name']:<26} {res.detected_stage}")

    print(f"\n{'-'*70}\n NEEDS INFO — parked; founder discovery runs before any email\n{'-'*70}")
    for row, why in needs_info:
        print(f"  • {row['name']:<26} ({why})")

    print(f"\n{'-'*70}\n QUALIFIED — personalization per company\n{'-'*70}")
    print(f"  {'Company':<22}{'{{Firstname}}':<14}{'{{domain area}}':<34}email guess")
    for row, cand, domain, emails in qualified:
        first = (clean_founder_name(row["founder"]) or "").split()[0]
        email = emails[0] if emails else "(resolve via web lookup)"
        print(f"  {row['name']:<22}{first:<14}{row['domain_area']:<34}{email}")

    # Show one fully-rendered email so the team can approve the actual voice.
    demo = qualified[1]  # Gully Labs — has a website, so a real email guess
    row, cand, domain, emails = demo
    first = clean_founder_name(row["founder"]).split()[0]
    print(f"\n{'='*70}\n EXAMPLE RENDERED EMAIL — {row['name']}\n{'='*70}")
    print(f"  To:      {emails[0]}")
    print(f"  Subject: {render_subject(row['name'])}\n")
    print(render_first_touch(first_name=first, domain_area=row["domain_area"],
                             calendly_url=SAMPLE_CALENDLY))
    print()


if __name__ == "__main__":
    run()
