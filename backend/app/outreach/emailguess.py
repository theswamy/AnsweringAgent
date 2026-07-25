"""Founder-name cleaning and email-pattern generation.

Sanjay's rule: when the domain is known, try ``firstname@`` and
``firstname.lastname@``. We generate those first, then a few common fallbacks,
in priority order. Verification (MX / SMTP / a finder API) happens elsewhere;
this module is pure string logic and fully unit-testable.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

# Honorifics / role suffixes that appear in the board's "Best Founder" field,
# e.g. "Abhinav Kumar (CEO, IIT Delhi)", "Aditya Varma (CEO)".
_PAREN_RE = re.compile(r"\([^)]*\)")
_TITLE_TOKENS = {
    "mr", "mrs", "ms", "dr", "prof",
    "ceo", "cto", "coo", "cofounder", "co-founder", "founder",
}
_NON_NAME_TOKENS = {"unknown", "n/a", "na", "tbd", ""}


def clean_founder_name(raw: str | None) -> str | None:
    """Strip parentheticals, titles and punctuation to a plain "First Last".

    Returns ``None`` when there's nothing usable (blank, "Unknown", or a value
    that is really the company name rather than a person — the caller decides
    that separately via :func:`looks_like_person`).
    """
    if not raw:
        return None
    name = _PAREN_RE.sub(" ", raw)
    name = name.replace(".", " ").replace(",", " ")
    tokens = [t for t in name.split() if t]
    tokens = [t for t in tokens if t.lower().strip(".") not in _TITLE_TOKENS]
    cleaned = " ".join(tokens).strip()
    if not cleaned or cleaned.lower() in _NON_NAME_TOKENS:
        return None
    return cleaned


def looks_like_person(founder: str | None, company: str | None) -> bool:
    """Heuristic: is ``founder`` an actual person, not the company name again?

    On the board, missing founders are recorded as the company name (e.g.
    "Catalogus", "Onya Diamonds") or "Unknown". Those must not be emailed as if
    they were a person; they route to founder discovery instead.
    """
    cleaned = clean_founder_name(founder)
    if cleaned is None:
        return False
    if company:
        c = re.sub(r"[^a-z0-9]", "", company.lower())
        f = re.sub(r"[^a-z0-9]", "", cleaned.lower())
        # Founder string is (or is contained in) the company name -> not a person.
        if f and (f == c or f in c or c in f):
            return False
    # A single token with no space is usually a brand, not a full name.
    return len(cleaned.split()) >= 2


def domain_from_website(website: str | None) -> str | None:
    """Extract a bare email domain from a website URL/host."""
    if not website:
        return None
    raw = website.strip()
    if not raw:
        return None
    if "//" not in raw:
        raw = "//" + raw
    host = urlparse(raw).netloc or urlparse(raw).path
    host = host.split("/")[0].strip().lower()
    if host.startswith("www."):
        host = host[4:]
    return host or None


def _ascii_token(token: str) -> str:
    return re.sub(r"[^a-z]", "", token.lower())


def email_candidates(founder_name: str, domain: str) -> list[str]:
    """Ordered list of likely addresses for ``founder_name`` at ``domain``.

    Priority follows Sanjay's stated preference (firstname, then
    firstname.lastname), then common fallbacks. De-duplicated, order preserved.
    """
    name = clean_founder_name(founder_name)
    domain = (domain or "").strip().lower().lstrip("@")
    if not name or not domain:
        return []

    tokens = [_ascii_token(t) for t in name.split()]
    tokens = [t for t in tokens if t]
    if not tokens:
        return []

    first = tokens[0]
    last = tokens[-1] if len(tokens) > 1 else ""

    patterns: list[str] = [first]
    if last:
        patterns += [
            f"{first}.{last}",
            f"{first}{last}",
            f"{first[0]}{last}",
            f"{first}.{last[0]}",
            f"{first}_{last}",
            last,
        ]
    seen: set[str] = set()
    out: list[str] = []
    for local in patterns:
        addr = f"{local}@{domain}"
        if addr not in seen:
            seen.add(addr)
            out.append(addr)
    return out
