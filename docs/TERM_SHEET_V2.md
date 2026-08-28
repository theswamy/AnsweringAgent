# SB2 / NLP Secondary — Principles of the Transaction

**Version 2 · 27 August 2026.** Same economics as the previous version. What changed is
the arithmetic that was inconsistent and the way the liquidation preference is expressed.
Every figure here is computed from the fund's own primitives; the changelog at the end
lists each change and why.

One mechanism is called out up front because everything downstream depends on it — the
**company-level put/call in §6**, which is what gives NLPI the same 12.6% of every exit
whatever the company's domicile. If that does not hold for some portco, its exits stop
splitting 87.4 / 12.6 and §7 to §9 have to be re-derived for it.

---

## 1. The fund today

| | |
|---|---|
| Class A — GP | 2% · $0.912M |
| Class B — LP | 98% · $44.700M |
| Fund size | $45.612M |
| Capital distributed | $11.0M |
| Remaining return of capital (ROC) | $35.0M |
| Current fund NAV | $360M |
| Carry, after ROC | 30% |

## 2. Who owns the upside today

Profit above the remaining ROC: **$360M − $35M = $325M**.

| | Share of profit | Value |
|---|---|---|
| Class A | 2% commitment + 30% carry on the LPs' 98% = **31.4%** | $102.0M |
| Class B | **68.6%** | $223.0M |

Because there is a single 1x hurdle and no catch-up tiers, these shares hold at **any**
level of profit — which is what lets the rest of this document use flat ratios instead of a
tiered waterfall.

LP NAV = 98% of the $35M ROC + $223.0M = **$257.3M** (call it $260M).

## 3. What NLP is buying

$35M of Class B's economics at a 35% discount, taking its 1x back first and then
participating pari passu.

| | |
|---|---|
| $35M ÷ $257.3M of LP NAV | 13.6% of the LP |
| ÷ 0.65, for the 35% discount | **20.9%** of the LP's economics |
| × Class B's 68.6% of profit | **14.1%** of all profit |

## 4. The sharing ratio after the transaction

Of every dollar distributed once NLP's priority return is satisfied:

| Class A | Class B1 — old LPs | NLP |
|---|---|---|
| **31.4%** | **54.5%** | **14.1%** |

Class A is not diluted: the secondary is sold out of Class B, so NLP's 14.1% comes
entirely out of Class B's 68.6%.

## 5. How the $35M is written

Only 10% of the cheque can move offshore-to-offshore, so NLP comes in through two
vehicles:

| Vehicle | Cheque | What it acquires | Economics acquired | Worth at NAV | Discount |
|---|---|---|---|---|---|
| **NLPF** — Singapore feeder | $3.5M (10%) | new **Class B2** units in SB2 Mauritius | **x1 = 1.4%** | $5.04M | 30.6% |
| **NLPI** — India fund | $31.5M (90%) | shares in the portcos, directly | **x2 = 12.6%** | $45.36M | 30.6% |

**x1** and **x2** are the two vehicles' shares of the fund's total economics, and are used
with those names throughout. Both vehicles are priced identically per unit of economics —
the 10 / 90 split of the cheque buys a 10 / 90 split of NLP's interest.

x1 + x2 = 14.0%, against the 14.1% used for NLP in §4. The difference is rounding at one
decimal, and both are recomputed at signing (§11 item 6).

NLPF's money is **primary** capital into the fund; NLPI's is a **secondary** purchase of
assets from it.

## 6. What each exit looks like

**NLPI takes 12.6% of every exit, and SB2 keeps 87.4%.** How NLPI holds that 12.6%
depends on where the company sits, but what it receives does not:

| Portco domicile | How NLPI's 12.6% is held | At exit |
|---|---|---|
| India | shares held directly, onshore | NLPI is a selling shareholder, paid in India |
| Delaware, Singapore | a **put/call at the company level**, written into the SHA | the same 12.6%, delivered under the SHA |

So a single exit is always two cheques: **87.4% to SB2, 12.6% to NLPI.** SB2 keeps by far
the larger holding still to sell, and sells it out of Mauritius as a non-resident; NLPI's
slice is settled where the company sits. NLPF never receives anything from a buyer — it is
inside the fund, and is paid out of SB2's receipts.

The put/call is what makes this uniform. Without it, the offshore-domiciled positions would
pay NLPI nothing, NLPI's share of any single exit would depend on which company was selling,
and no single preference figure or sharing ratio would hold. With it, every number below is
a constant.

## 7. NLP's priority return

NLP's 1x comes back through two legs. Measured on NLPF's $3.5M they add to **10x** — the
whole cheque:

| Leg | Route | Multiple | Amount |
|---|---|---|---|
| The liquidation preference | SB2 → NLPF, in Mauritius | 8.74x | $30.59M |
| NLPI's own share sales | buyers → NLPI, at each company | 1.26x | $4.41M |
| **NLP's 1x** | | **10.00x** | **$35.00M** |

SB2 cannot grant a preference over shares it has already sold, so the preference covers only
its own 87.4% of the first $35M. Both legs are exhausted at the same moment, and NLP is
whole at exactly $35M of exits.

**Draft the preference as its formula, not as the multiple.** 8.74x is 87.4% of $35M divided
by $3.5M — it is a consequence of x2, and §11 notes that the exact x1 and x2 will move
before signing. The operative words should be:

> NLPF's Class B2 carries a liquidation preference equal to **$35M less NLPI's share of the
> proceeds of the same exits** — $30.59M at x2 = 12.6% — so that NLP's two vehicles together
> receive $35M and no more before the sharing ratio in §4 applies.

Stated that way it re-derives itself if x2 changes; stated as 8.74x it silently
over- or under-pays. Leaving it at the previous version's 9.86x while NLPI takes 12.6%, for
instance, would run the preference to $39.49M of exits — $4.49M past NLP's 1x, transferring
$3.85M out of Class A and the old LPs.

## 8. The distribution rule

At each exit, in order:

1. **The buyer pays NLPI 12.6% of the cheque**, directly, for the shares it sells. This is
   NLP's second leg and never enters the fund.
2. **SB2 pays 100% of its receipts to NLPF** under the preference, until $30.59M has been
   paid.
3. **Thereafter SB2 distributes its receipts** — Class A **35.93%**, Class B1 **62.36%**,
   Class B2 **1.72%**.

Step 3 is the §4 ratio expressed as shares of what the fund actually receives: 31.4 / 87.4,
54.5 / 87.4 and 1.5 / 87.4. In absolute terms every cheque after the preference splits
**Class A 31.4% · Class B1 54.5% · NLP 14.1%**, NLP's 14.1% arriving as 12.6% directly and
1.5% through Class B2.

A tranche that straddles the moment the preference is satisfied is split: the balance of the
$30.59M first, then step 3 on the remainder.

## 9. Worked example

The previous version's own exits: $20M in WheelsEye at $800M, then a $25M secondary in Niyo
at $500M (5% of the company), in tranches of $15M and $10M.

| | Cheque | → NLPI | → SB2 | → NLPF pref | Class B2 | Class A | Class B1 | pref left |
|---|---|---|---|---|---|---|---|---|
| WheelsEye · 2.5% of the company | $20.00M | $2.52M | $17.48M | $17.48M | — | — | — | $13.11M |
| Niyo · first $15M | $15.00M | $1.89M | $13.11M | $13.11M | — | — | — | **nil** |
| Niyo · next $10M | $10.00M | $1.26M | $8.74M | — | $0.15M | $3.14M | $5.45M | nil |

- On the first two exits every dollar goes to NLP: **$4.41M** to NLPI at the companies and
  **$30.59M** to NLPF under the preference. $35.00M — NLP's 1x, satisfied exactly.
- WheelsEye: NLPI sells 2.5% × 12.6% = **0.315%** of the company for $2.52M; SB2 sells
  2.185% for $17.48M.
- From the third tranche on, each cheque splits 31.4 / 54.5 / 14.1 in absolute terms.
- Totals on $45M: NLP $36.41M, Class A $3.14M, Class B1 $5.45M.

## 10. Exit conditions

- SB2 and NLP sell pro-rata at every exit — secondary, IPO, or post-IPO. Effectively a
  put/call across the two holdings.
- **The put/call has to be papered at each company.** For the India-domiciled portcos it
  supports the pro-rata undertaking between two registered shareholders. For the Delaware and
  Singapore entities it is also the means by which NLPI holds its 12.6% at all, so its
  enforceability there is load-bearing, not administrative.
- Each SHA amendment engages the other shareholders' ROFR, tag and drag rights, and IPO
  lock-ups will override the pro-rata undertaking for a period. Schedule 2 to list the
  consents required, per portco.
- The tax treatment of a settlement under the put/call — as against a share sale — needs to
  be confirmed per domicile, since it determines what NLPI actually nets.

## 11. Assumptions and open items

1. **Class A's ROC.** The $35M is paid to Class B holders, which completes their 1x. Class
   A's 2% of the remaining ROC — **$0.70M** — is not funded by it. Either gross the cheque
   up to $35.71M, or pay Class A $0.70M out of SB2's receipts ahead of the tail. **To be
   decided**; the illustration above assumes neither.
2. **Onshore tax.** $31.5M buys Indian portco shares from a Mauritius fund below carrying
   value: a fair-value pricing floor on the inbound leg, and capital gains withholding at
   the SB2 level. Assumed grossed up. The gross-up moves x2, and therefore §6 and §9.
3. **NLPF → NLPI.** Both are NLP, so moving the preference proceeds to India is an
   intra-group transfer — but it carries $30.59M of the $35M, so the route, the tax on each
   hop, and the alignment of the two vehicles' LP bases have to be papered. If the LP bases
   differ, the split between the legs stops being mechanics.
4. **The put/call's enforceability and tax treatment**, per domicile — Delaware and
   Singapore especially, where it is how NLPI holds its 12.6% rather than a convenience.
5. **Schedule 1** — per portco: domicile, SB2's holding, carrying value, and NLPI's 12.6%
   slice in shares and dollars, summing to $31.5M.
6. **Precision.** x1, x2 and NLP's 14.1% are illustrative to one decimal, and x1 + x2 does
   not currently equal 14.1% for that reason. Recompute all of them, and the ratios in §4,
   from the final cheque and NAV at signing.
7. **"mg"** in the portco list is not expanded anywhere.

## 12. Changelog against the previous version

| | Was | Now | Why |
|---|---|---|---|
| Post-ROC cap table | Class A 31.4% + Class B 69.6% | Class A 31.4% + Class B **68.6%** | The two must sum to 100%, and the tail (31.4 + 54.5 + 14.1) confirms 68.6%. |
| NLPI's slice of an exit cheque | 1.4% in the WheelsEye and first Niyo exits, 12% in the tail | **12.6%** throughout, per §6 | A shareholding cannot change between two tranches of the same sale. 1.4% is x1 — a percentage of Class B inside the fund, not of a portco position. The WheelsEye line computed "2.5% × x2_WE" and then printed 0.035%, which is 2.5% × 1.4%; at x2 it is 0.315%. |
| The preference | 10x, then ~10x (9.86x) on NLPF's $3.5M | **$35M less NLPI's share of the same exits — $30.59M, i.e. 8.74x** | 9.86x is 10x net of a **1.4%** pro-rata sale; NLPI sells **12.6%**, so the legs are 8.74x + 1.26x. Leaving it at 9.86x would run the preference to $39.49M of exits — $4.49M past NLP's 1x — and transfer $3.85M out of Class A and the old LPs. |
| Class B2's share of the tail | x1 = 1.4% of Class B, and separately 2% of absolute | **1.5% of absolute — 1.72% of SB2's receipts** | The two statements were inconsistent: 1.4% of Class B is 0.96% of absolute. 1.5% is what NLP's 14.1% requires alongside NLPI's 12.6%. |
| Niyo secondary | $25M at $500M described as 6% of the company | **5%** | $25M ÷ $500M. The document's own sub-figures (2.958% + 0.042% for $15M) already imply 5%. |
| SB2's retained block | not addressed | §6 | SB2 keeps 87.4% of every position and sells it out of Mauritius as a non-resident, alongside NLPI's 12.6%. |
| The put/call | flagged for Delaware, as an SHA amendment | §6 and §10 — the mechanism by which NLPI holds its 12.6% in the Delaware and Singapore entities | Without it those exits would pay NLPI nothing, and neither the preference nor the sharing ratios would be single numbers. With it every figure in the document is a constant. |
| NLPF → NLPI | "Open Question", asked twice | Item 3 in §11 | It is an intra-group transfer, not an economic mismatch — but it carries the bulk of the priority return. |
