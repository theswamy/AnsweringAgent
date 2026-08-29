# Routing the $35M: two models

SB2 / NLP secondary · August 2026. Generated from `deal_agent`; see
`deal_agent/tests/test_uniform_rule.py` for the assertions behind every figure.

## What does not change

NLP's cheque is $35M and buys 14.36% of the fund's economics — a 35% discount to the LP's
share of NAV — in both models. Above the priority return, distributions split Class A
31.40%, Class B1 54.24%, NLP 14.36% in both. NLP is whole at exactly $35M of exits in both.
What changes is how much of that travels through the fund rather than being paid to NLPI
directly.

## The two models

| | Model A · 10% offshore | Model B · 20% offshore |
|---|---|---|
| NLPF cheque · Singapore feeder into SB2 | $3.50M | $7.00M |
| NLPI cheque · onshore India | $31.50M | $28.00M |
| x1 — held through the fund, Class B2 | 1.436% | 2.872% |
| x2 — held directly by NLPI | 12.92% | 11.49% |
| x1 + x2 | 14.36% | 14.36% |
| Every exit cheque: to NLPI | 12.92% | 11.49% |
| Every exit cheque: to SB2 | 87.08% | 88.51% |
| Liquidation preference | $30.48M | $30.98M |
| …as a multiple of the NLPF cheque | 8.71x | 4.43x |
| NLPI's own sales, in the priority period | $4.52M | $4.02M |
| Both legs together | $35.00M · 10.00x | $35.00M · 5.00x |
| SB2's receipts after the preference — Class A | 36.06% | 35.47% |
| …Class B1 | 62.29% | 61.28% |
| …Class B2 | 1.65% | 3.24% |
| In absolute terms — A / B1 / NLP | 31.40 / 54.24 / 14.36 | 31.40 / 54.24 / 14.36 |
| Discount to the LP's share of NAV, both vehicles | 35.00% | 35.00% |

## The same exits under each model

$20M in WheelsEye at $800M, then a $25M secondary in Niyo at $500M in tranches of $15M
and $10M.

**Model A · 10% offshore**

| Exit | Cheque | to NLPI | to SB2 | of which pref | Class B2 | Class A | Class B1 |
|---|---|---|---|---|---|---|---|
| WheelsEye | $20.00M | $2.58M | $17.42M | $17.42M | — | — | — |
| Niyo · first $15M | $15.00M | $1.94M | $13.06M | $13.06M | — | — | — |
| Niyo · next $10M | $10.00M | $1.29M | $8.71M | — | $0.14M | $3.14M | $5.42M |

**Model B · 20% offshore**

| Exit | Cheque | to NLPI | to SB2 | of which pref | Class B2 | Class A | Class B1 |
|---|---|---|---|---|---|---|---|
| WheelsEye | $20.00M | $2.30M | $17.70M | $17.70M | — | — | — |
| Niyo · first $15M | $15.00M | $1.72M | $13.28M | $13.28M | — | — | — |
| Niyo · next $10M | $10.00M | $1.15M | $8.85M | — | $0.29M | $3.14M | $5.42M |

In both models the first two exits return NLP exactly $35M, and the third tranche splits
$3.14M / $5.42M / $1.44M to Class A, Class B1 and NLP.

## What differs in consequence

- **Where the tail is paid.** Of NLP's 14.36%, Model A pays 12.92% onshore and
  1.436% through the fund; Model B pays 11.49% onshore and
  2.872% through the fund. Model B routes twice as much of NLP's long-run
  share through Mauritius.
- **The onshore purchase.** $31.50M in Model A against
  $28.00M in Model B — the base on which Indian transfer pricing
  and capital gains withholding apply.
- **The preference multiple.** 8.71x against
  4.43x. The dollar amount is almost identical
  ($30.48M against $30.98M); the multiple differs because the NLPF cheque it is
  measured on doubles.
- **Repatriation.** The preference carries $30.48M in Model A and $30.98M in
  Model B, so the NLPF-to-NLPI route carries a similar amount in the priority period. Over
  the tail, Model B leaves more with NLPF.
- **Regulatory headroom.** Model B requires 20% of the cheque to move offshore-to-offshore
  into SB2 Mauritius, against 10%.

---

x1 and x2 are NLP's 14.36% split pro rata to the two cheques. 14.36% is a 35% discount to
the LP's share of NAV ($257.25M); the document's stated 14.1% is that figure rounded, and
docs/DISCOUNT_BASIS.md compares it with measuring the same 35% against the fund's whole
$360M NAV. All figures are recomputed from the final cheque and NAV at signing.
