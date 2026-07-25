"""Qualification gates.

The core rule (decided with Sanjay): **skip anything past Series A.** Companies
at Pre-Seed / Seed / Pre-Series A / Series A qualify; Series B and later,
"Late Stage", and "Growth" are disqualified with reason "Too Late for Prime".

Stage lives in free text on the board (``Stage`` and ``Last Round Type``), with
real-world values like "Pre-Series A follow-on", "Seed (incubation)",
"Series C (follow-on)" and "Late Stage (follow-on)" — so the parser is
deliberately tolerant.
"""
from __future__ import annotations

import re

from .models import (
    Candidate,
    OutreachStatus,
    QualificationResult,
    QualificationVerdict,
    StageVerdict,
)

TOO_LATE_REASON = "Too Late for Prime"

# Ordered greatest-first so "Series A/B" style values resolve to the later round.
_SERIES_RE = re.compile(r"series[\s\-]*([a-h])\b", re.IGNORECASE)

# Phrases that unambiguously mean "later than Series A".
_LATE_KEYWORDS = (
    "late stage",
    "late-stage",
    "growth",
    "mezzanine",
    "pre-ipo",
    "pre ipo",
    "ipo",
    "series b",
    "series c",
    "series d",
    "series e",
)

# Phrases that mean "at or before Series A" even when a stray letter appears
# (e.g. "Pre-Series A" contains "series a" but is earlier than A).
_EARLY_KEYWORDS = (
    "pre-seed",
    "pre seed",
    "preseed",
    "angel",
    "seed",
    "incubation",
    "bridge",
    "pre-series a",
    "pre series a",
)


def classify_stage(*texts: str | None) -> tuple[StageVerdict, str | None]:
    """Classify one or more stage strings into a single verdict.

    When several fields disagree we take the *latest* round mentioned across all
    of them — a company that did a Seed then a Series B is a Series B company.
    Returns ``(verdict, detected_stage_label)``.
    """
    joined = " | ".join(t for t in texts if t)
    if not joined.strip():
        return StageVerdict.UNKNOWN, None

    lowered = joined.lower()

    # 1) Highest-precedence signal: an explicit series letter beyond A anywhere.
    latest_letter = None
    for m in _SERIES_RE.finditer(lowered):
        # Guard against "pre-series a" — the "pre" makes it earlier than A.
        start = m.start()
        preceding = lowered[max(0, start - 5):start]
        if "pre" in preceding:
            continue
        letter = m.group(1).lower()
        if latest_letter is None or letter > latest_letter:
            latest_letter = letter
    if latest_letter is not None:
        if latest_letter > "a":
            return StageVerdict.TOO_LATE, _label(joined)
        return StageVerdict.QUALIFIED, _label(joined)

    # 2) Other explicit "too late" phrasing (Late Stage, Growth, IPO...).
    if any(k in lowered for k in _LATE_KEYWORDS):
        return StageVerdict.TOO_LATE, _label(joined)

    # 3) Early-stage phrasing qualifies.
    if any(k in lowered for k in _EARLY_KEYWORDS):
        return StageVerdict.QUALIFIED, _label(joined)

    # 4) Couldn't tell.
    return StageVerdict.UNKNOWN, _label(joined)


def _label(raw: str) -> str:
    """Pick the most informative single stage token for display/logging."""
    return raw.split("|")[0].strip() or raw.strip()


def qualify(
    candidate: Candidate,
    *,
    target_funds: set[str] | None = None,
    qualify_unknown_stage: bool = True,
) -> QualificationResult:
    """Apply every gate to a candidate.

    Gates, in order:
      1. Actionability — only ``To Reach Out`` items are worked (idempotent re-runs).
      2. Micro-VC membership — ``backing_fund`` must be in ``target_funds`` when
         a set is supplied. Defaults to no restriction because the board is
         already scoped to Sanjay's funds.
      3. Stage gate — skip anything past Series A.

    ``qualify_unknown_stage`` controls the default when the stage can't be read:
    on this board an unreadable stage skews early, so we keep the company but
    flag the low confidence in the reason.
    """
    status = (candidate.outreach_status or "").strip()
    if status and status != OutreachStatus.TO_REACH_OUT.value:
        return QualificationResult(
            verdict=QualificationVerdict.SKIPPED,
            stage_verdict=StageVerdict.UNKNOWN,
            reason=f"Already in pipeline (status={status!r}); left untouched.",
        )

    if target_funds is not None:
        fund = candidate.backing_fund.lower()
        allowed = {f.strip().lower() for f in target_funds}
        if fund not in allowed:
            return QualificationResult(
                verdict=QualificationVerdict.SKIPPED,
                stage_verdict=StageVerdict.UNKNOWN,
                reason=f"Backing fund {candidate.backing_fund!r} not in target set.",
            )

    stage_verdict, detected = classify_stage(candidate.stage_text, candidate.last_round_type)

    if stage_verdict is StageVerdict.TOO_LATE:
        return QualificationResult(
            verdict=QualificationVerdict.DISQUALIFIED,
            stage_verdict=stage_verdict,
            reason=f"{TOO_LATE_REASON} (stage={detected!r}).",
            detected_stage=detected,
        )

    if stage_verdict is StageVerdict.UNKNOWN and not qualify_unknown_stage:
        return QualificationResult(
            verdict=QualificationVerdict.DISQUALIFIED,
            stage_verdict=stage_verdict,
            reason="Stage could not be determined; parked by policy.",
            detected_stage=detected,
        )

    reason = "Qualified"
    if stage_verdict is StageVerdict.UNKNOWN:
        reason = "Qualified (stage unknown — low confidence, defaulted in)."
    return QualificationResult(
        verdict=QualificationVerdict.QUALIFIED,
        stage_verdict=stage_verdict,
        reason=reason,
        detected_stage=detected,
    )
