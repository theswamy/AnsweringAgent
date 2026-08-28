# Routing the $35M: two models

SB2 / NLP secondary · August 2026. Generated from `deal_agent`; see
`deal_agent/tests/test_uniform_rule.py` for the assertions behind every figure.

## What does not change

NLP's cheque is $35M and buys 14.1% of the fund's economics at a 31.05% discount to
carrying value in both models. Above the priority return, distributions split Class A
31.4%, Class B1 54.5%, NLP 14.1% in both. NLP is whole at exactly $35M of exits in both.
What changes is how much of that travels through the fund rather than being paid to NLPI
directly.

## The two models

| | Model A · 10% offshore | Model B · 20% offshore |
|---|---|---|
| NLPF cheque · Singapore feeder into SB2 | $3.50M | $7.00M |
| NLPI cheque · onshore India | $31.50M | $28.00M |
| x1 — held through the fund, Class B2 | 1.41% | 2.82% |
| x2 — held directly by NLPI | 12.69% | 11.28% |
| x1 + x2 | 14.10% | 14.10% |
| Every exit cheque: to NLPI | 12.69% | 11.28% |
| Every exit cheque: to SB2 | 87.31% | 88.72% |
| Liquidation preference | $30.56M | $31.05M |
| …as a multiple of the NLPF cheque | 8.73x | 4.44x |
| NLPI's own sales, in the priority period | $4.44M | $3.95M |
| Both legs together | $35.00M · 10.00x | $35.00M · 5.00x |
| SB2's receipts after the preference — Class A | 35.96% | 35.39% |
| …Class B1 | 62.42% | 61.43% |
| …Class B2 | 1.61% | 3.18% |
| In absolute terms — A / B1 / NLP | 31.4 / 54.5 / 14.1 | 31.4 / 54.5 / 14.1 |
| Discount to carrying value, both vehicles | 31.05% | 31.05% |

## The same exits under each model

$20M in WheelsEye at $800M, then a $25M secondary in Niyo at $500M in tranches of $15M
and $10M.

**Model A · 10% offshore**

| Exit | Cheque | to NLPI | to SB2 | of which pref | Class B2 | Class A | Class B1 |
|---|---|---|---|---|---|---|---|
| WheelsEye | $20.00M | $2.54M | $17.46M | $17.46M | — | — | — |
| Niyo · first $15M | $15.00M | $1.90M | $13.10M | $13.10M | $0.00M | $0.00M | $0.00M |
| Niyo · next $10M | $10.00M | $1.27M | $8.73M | — | $0.14M | $3.14M | $5.45M |

**Model B · 20% offshore**

| Exit | Cheque | to NLPI | to SB2 | of which pref | Class B2 | Class A | Class B1 |
|---|---|---|---|---|---|---|---|
| WheelsEye | $20.00M | $2.26M | $17.74M | $17.74M | — | — | — |
| Niyo · first $15M | $15.00M | $1.69M | $13.31M | $13.31M | — | — | — |
| Niyo · next $10M | $10.00M | $1.13M | $8.87M | — | $0.28M | $3.14M | $5.45M |

In both models the first two exits return NLP exactly $35M, and the third tranche splits
$3.14M / $5.45M / $1.41M to Class A, Class B1 and NLP.

## What differs in consequence

- **Where the tail is paid.** Of NLP's 14.1%, Model A pays 12.69% onshore and
  1.41% through the fund; Model B pays 11.28% onshore and
  2.82% through the fund. Model B routes twice as much of NLP's long-run
  share through Mauritius.
- **The onshore purchase.** $31.50M in Model A against
  $28.00M in Model B — the base on which Indian transfer pricing
  and capital gains withholding apply.
- **The preference multiple.** 8.73x against
  4.44x. The dollar amount is almost identical
  ($30.56M against $31.05M); the multiple differs because the NLPF cheque it is
  measured on doubles.
- **Repatriation.** The preference carries $30.56M in Model A and $31.05M in
  Model B, so the NLPF-to-NLPI route carries a similar amount in the priority period. Over
  the tail, Model B leaves more with NLPF.
- **Regulatory headroom.** Model B requires 20% of the cheque to move offshore-to-offshore
  into SB2 Mauritius, against 10%.

---

x1 and x2 are NLP's 14.1% split pro rata to the two cheques, which is why they sum to
14.10% exactly here rather than to the 14.0% the previous document's rounded 1.4% and 12.6%
produced. All figures are recomputed from the final cheque and NAV at signing.
