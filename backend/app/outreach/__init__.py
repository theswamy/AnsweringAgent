"""Founder Outreach Agent.

A deal-sourcing agent for Prime VP. It reads curated companies from the
MicroVC Sourcing monday.com board (the System of Record), qualifies them,
resolves the founder's email, sends an approved personalized first-touch on
Sanjay's behalf, runs the reply dialog, and books a 30-minute intro call.

See ``docs/OUTREACH_AGENT_DESIGN.md`` for the full design.

This package is layered so the deterministic core (``qualify``, ``emailguess``,
``template``) has no external dependencies and is unit-tested in isolation; the
I/O adapters (monday, gmail, calendly) and the Claude brain build on top.
"""
from __future__ import annotations

__all__ = ["models", "qualify", "emailguess", "template"]
