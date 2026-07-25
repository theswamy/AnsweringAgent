"""Sanjay's first-touch template and its personalization slots.

The template voice is Sanjay's own (provided verbatim). Only two slots are
filled per company — ``{{Firstname}}`` and ``{{domain area}}`` — and the
Calendly link is appended. Anything more elaborate (a bespoke opening line) is
the brain's job; this module guarantees a correct, on-voice baseline with no
LLM in the loop.
"""
from __future__ import annotations

# Sanjay's verbatim template. Slots: {{Firstname}}, {{domain area}}.
FIRST_TOUCH_TEMPLATE = """\
Hi {{Firstname}}

Sanjay Swamy here, co-founder & Managing Partner at PrimeVP. I've been a serial \
entrepreneur, Aadhaar-volunteer, and started Prime along with my partners 12 \
years ago - today we have an amazing portfolio of 50+ companies that we backed \
when they were at a concept or fledgling-stage and have grown into what you now \
know as Mygate, Niyo, WheelsEye, Quizizz, Dozee and many more over the years. \
Some of our exited portfolio include Recko (Stripe), Happay (Cred), Ezetap \
(Razorpay), Zipdial (Twitter) and more.

As a VC, we are a high-conviction investor who will pick one company in a space \
and back the founders all the way. As entrepreneurs-turned-VCs, we do like to be \
actively engaged as long as we can contribute to your success and unlike others \
our entire partnership is always available for you to leverage as a portfolio \
company.

Your space of {{domain area}} is currently of great interest to us and I'd like \
to see if we could schedule a short Video Call to introduce each other and get \
the dialog going.

Do let me know if you'd like to speak and a convenient time that works for you - \
I'm also taking the liberty of adding my calendar link here: {{calendly_url}}

Cheers

Sanjay"""

DEFAULT_SUBJECT = "PrimeVP <> {company}"

# Map the board's sector tag ("Best Founder Domain") to a natural phrase that
# reads well in "Your space of ___". Unmapped/empty tags fall back to the brain
# or to a phrase derived from the one-liner.
_SECTOR_TO_PHRASE = {
    "d2c_consumer": "consumer brands and D2C",
    "consumer": "consumer",
    "healthtech": "healthcare and health-tech",
    "fintech": "fintech",
    "ai_ml": "applied AI",
    "saas": "SaaS",
    "b2b_saas": "B2B SaaS",
    "edtech": "education technology",
    "climate": "climate and sustainability",
    "deeptech": "deep tech",
    "logistics": "logistics and supply chain",
}


def sector_to_domain_area(sector_tag: str | None) -> str | None:
    """Human-readable ``{{domain area}}`` phrase for a board sector tag."""
    if not sector_tag:
        return None
    key = sector_tag.strip().lower()
    if key in ("", "other", "others", "n/a", "na"):
        return None
    return _SECTOR_TO_PHRASE.get(key, key.replace("_", " "))


def render_first_touch(
    *,
    first_name: str,
    domain_area: str,
    calendly_url: str,
) -> str:
    """Fill the template. All three slots are required — the caller resolves a
    fallback for ``domain_area`` (sector map, brain, or one-liner) before here,
    so the sent email never contains a literal "{{...}}"."""
    for label, value in (("first_name", first_name), ("domain_area", domain_area),
                         ("calendly_url", calendly_url)):
        if not value or not str(value).strip():
            raise ValueError(f"render_first_touch: {label} is required and was empty")

    return (
        FIRST_TOUCH_TEMPLATE
        .replace("{{Firstname}}", first_name.strip())
        .replace("{{domain area}}", domain_area.strip())
        .replace("{{calendly_url}}", calendly_url.strip())
    )


def render_subject(company: str) -> str:
    return DEFAULT_SUBJECT.format(company=company.strip())
