"""Typed data model for the outreach pipeline.

A ``Candidate`` is one company as read from the monday board, plus everything
the pipeline learns about it (qualification verdict, resolved contact, drafts).
Keeping this as plain pydantic models means every stage has a predictable,
serializable shape and the board's messy free-text stays quarantined behind
parsing.
"""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class OutreachStatus(str, Enum):
    """Mirrors the board's ``Outreach Status`` column (color_mm2w2wv) labels."""

    TO_REACH_OUT = "To Reach Out"
    SENT = "Sent"
    REPLIED = "Replied"
    MEETING = "Meeting"
    PITCHED = "Pitched"
    PASS = "Pass"


class StageVerdict(str, Enum):
    """Result of applying the stage gate to a company."""

    QUALIFIED = "qualified"            # at or before Series A
    TOO_LATE = "too_late"             # Series B+ / Late / Growth -> Pass
    UNKNOWN = "unknown"               # stage couldn't be determined


class QualificationVerdict(str, Enum):
    """Overall qualify decision, combining every gate."""

    QUALIFIED = "qualified"
    DISQUALIFIED = "disqualified"     # a hard gate failed (e.g. too late)
    SKIPPED = "skipped"              # not actionable (already in flight, etc.)


class Candidate(BaseModel):
    """A company on the board, as far as the pipeline is concerned."""

    # --- Identity / board linkage ---
    item_id: str
    name: str
    group_title: str = ""             # the backing micro-VC (group is authoritative)
    url: str = ""

    # --- Raw board fields (may be missing / messy) ---
    outreach_status: str | None = None
    stage_text: str | None = None            # Stage (text_mm2wcv77)
    last_round_type: str | None = None       # Last Round Type (text_mm2whw)
    best_founder: str | None = None          # Best Founder (text_mm2ww997)
    founder_linkedin: str | None = None      # Best Founder LinkedIn (link_mm2wccf8)
    sector_tag: str | None = None            # "Best Founder Domain" is a SECTOR tag
    website: str | None = None               # Website (link_mm2w7w62)
    one_liner: str | None = None             # One-Line Description (long_text_mm2wzcyv)
    micro_vc_dropdown: str | None = None      # unreliable co-investor field; kept for reference

    @property
    def backing_fund(self) -> str:
        """The micro-VC that backs this company. The group is authoritative;
        the ``MicroVC`` dropdown is sparsely populated and often lists
        co-investors, so it is never used as the source of truth."""
        return self.group_title.strip()


class Contact(BaseModel):
    """A resolved founder contact ready (or not) for sending."""

    founder_name: str | None = None
    domain: str | None = None                 # email domain, e.g. "gullylabs.in"
    email_candidates: list[str] = Field(default_factory=list)
    chosen_email: str | None = None
    confidence: float = 0.0                   # 0..1
    source: str = ""                          # how we found it (board / web / verified)
    needs_info: bool = False                  # True -> park, do not email a guess
    notes: str = ""


class QualificationResult(BaseModel):
    verdict: QualificationVerdict
    stage_verdict: StageVerdict
    reason: str
    detected_stage: str | None = None
