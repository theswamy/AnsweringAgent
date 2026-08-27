"""The source document, kept verbatim and cut into citable sections.

The agent is only allowed to speak about this transaction on the basis of this
text (plus the arithmetic in `terms.py` / `waterfall.py`, which is derived from
it). Sections carry stable ids so every answer can point at where it came from.

Source: Google Doc 1vepHdrEY2IuuM9TjwH0ced5FOrRerA0ugtr0gxD8tFU, as revised
2026-08-27 (the liqpref restated from 10x to 9.86x). The wording below is the document's; only the Markdown escaping
that the export added has been removed.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Section:
    id: str
    title: str
    text: str


SECTIONS: tuple[Section, ...] = (
    Section(
        "S1",
        "Fund principles and current state",
        """The principles of the transaction is as follows

Class A: GP 2% (0.912M)
Class B: LP 98% ($44.7M

Fund Size: $45.612M

Capital Distributed: $11.0M
Remaining Return of Capital (ROC): $35.0M

Current Fund NAV: 360
Carry after ROC: 30%""",
    ),
    Section(
        "S2",
        "Post-ROC cap table",
        """Post ROC, the CAP table effectively becomes:

Class A: 31.4%
Class B: 69.6%""",
    ),
    Section(
        "S3",
        "What NLP is buying",
        """NLP would like to purchase $35M worth of equity from the ClassB shareholders
at a 35% discount - provided they get their 1x back and subsequently participate
pari-passu with other ClassB shareholders.

If you take out the ROC, the fund has a profit of $325M. The GP stake works out to
about $100M, and LP profits about $225M - making the LP NAV effectively $260M.

As such a 35M check effectively is 13% of the LP and with a discount of 35% becomes 20%.""",
    ),
    Section(
        "S4",
        "Post-transaction flow of returns",
        """As such post this transaction the flow of returns would be as follows

- First 35M - goes straight back to the NLP
- Remaining distributions are share in the following ratio:
    - Class A: 31.4%
    - Class B: 54.5%
    - NLP: 14.1%""",
    ),
    Section(
        "S5",
        "NLP's two entities and how the $35M is written",
        """NLP will come through two entities, one direct and one which can only
participate in the Portfolio companies directly in their India entities.

Let's assume they can write 10% from their Feeder vehicle in Singapore directly into
the fund in Mauritius and the rest can only be done onshore in India.

NLP writes a check of $35M as follows:

- NLPF (Feeder in Singapore) puts in $3.5M (10%) to SB2 Mauritius - this comes with a
  ~10x (9.86 to be precise) liqpref and they buy (x1=1.4%) of the Class B
- NLPI (India Fund) $31.5M is used to acquire (x2=12.6%) % of SB2's stakes in each of
  the portcos from SB2 in India
  - These will be direct shareholdings in the target companies, i.e. x2_we, x2_mg,
    x2_niyo, x2_freo, x2_kredx.
  - For Delaware entities, the companies will also need to modify their SHA to include
    a put/call option for these shares.""",
    ),
    Section(
        "S6",
        "Stated assumptions",
        """- For purposes of this discussion let's assume x1 = 1.4% and x2 = 12.6%. EXACT
  numbers will be slightly different
- *Let's also assume that ClassA and Class B both participate and are both now "whole"
  - i.e. 1x DPI has occurred. If the $35M has to be grossed up or down a tad, so be it.
  If there is some tax leakage in selling at the company level, that is assumed to be
  grossed up - however this could be revisited*""",
    ),
    Section(
        "S7",
        "Exit conditions",
        """EXIT Conditions

- SB2 and NLP agree to sell pro-rata at time of any exits - whether secondary or at IPO
  or post an IPO - effectively like a put-call on these portco shares

At exit

Assume two exits happen
- First $20M in WheelsEye
- Next $25M in Niyo""",
    ),
    Section(
        "S8",
        "Worked exit A - $20M in WheelsEye at $800M",
        """A) $20M in WheelsEye at $800M (2.5% of the company)

- Buyer pays $20M to two sellers
- SB2 gets $19.72M for 98.6% or 2.465% of WE
- NLP gets $0.28M for 2.5%*x2_WE shares - 0.035% of WE (1.4% of the transaction)
- SB2 distributes the entire 19.72M to NLP as part of the LiqPref.

- Open Question: NLP_F then distributes pro-rata to NLP in India - how does the NLP
  India fund receive its returns?""",
    ),
    Section(
        "S9",
        "Worked exit B(a) - first $15M of the Niyo secondary",
        """2. $25 M in Secondary in Niyo at $500M (6% of the company)

a) First $15 M
- Same as above transaction
- Buyer pays $14.79M to SB2 for sale of 2.958% of Niyo
- Buyer pays $0.21M to NLPI for sale of 0.042% of Niyo
- SB2 distributes entire proceeds of $14.79M to NLPF under the Liqpref

(19.72+14.79)/3.5 = 9.86 - LIQPREF SATISFIED!

- Open Question: NLP_F then distributes pro-rata to NLP in India - how does the NLPI
  fund receive its returns?""",
    ),
    Section(
        "S10",
        "Worked exit B(b) - the pari-passu tail",
        """b) Next $10 M, and from now on for all subsequent distributions:

- Buyer writes two checks - 88% to SB2 and 12% to NLPI
- SB2(88%) is distributed as follows for sale of 88% of the holding
- Class A: 31% of absolute, or 35.3% of SB2 receipts
- Class B1 (Old LPs): 55% of absolute, or 62.5% of SB2 receipts
- Class B2 (NLPF): 2% of absolute, or 2.27% of SB2 receipts

- NLPI: 12% for sale of 12% of the holding""",
    ),
)

BY_ID = {s.id: s for s in SECTIONS}

FULL_TEXT = "\n\n".join(f"[{s.id}] {s.title}\n{s.text}" for s in SECTIONS)


def search(query: str, limit: int = 4) -> list[Section]:
    """Cheap keyword scoring — the document is ten short sections, so there is
    nothing here that an embedding index would earn its keep on."""
    words = [w for w in _tokens(query) if len(w) > 2]
    scored: list[tuple[int, Section]] = []
    for section in SECTIONS:
        haystack = _tokens(section.title + " " + section.text)
        score = sum(haystack.count(w) for w in words)
        # A section id typed directly ("what does S8 say") is an exact request.
        if section.id.lower() in words:
            score += 100
        if score:
            scored.append((score, section))
    scored.sort(key=lambda pair: (-pair[0], pair[1].id))
    return [section for _, section in scored[:limit]]


def _tokens(text: str) -> list[str]:
    return "".join(c.lower() if c.isalnum() else " " for c in text).split()
