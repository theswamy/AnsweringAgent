# SB2 / NLP Secondary — Principles of the Transaction

**Version 2 · 27 August 2026.** Same economics as the previous version. What changed is
the arithmetic that was inconsistent and the way the liquidation preference is expressed.
Every figure here is computed from the fund's own primitives; the changelog at the end
lists each change and why.

One assumption is called out up front because everything downstream depends on it —
**§6, which shares NLPI actually holds.** Correct that section and the rest re-derives.

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
| **NLPF** — Singapore feeder | $3.5M (10%) | new **Class B2** units in SB2 Mauritius | 1.4% | $5.04M | 30.6% |
| **NLPI** — India fund | $31.5M (90%) | shares in the portcos, directly | 12.6% | $45.36M | 30.6% |

Both vehicles are priced identically per unit of economics, and 1.4% + 12.6% = NLP's 14%.
NLPF's money is **primary** capital into the fund; NLPI's is a **secondary** purchase of
assets from it.

## 6. What each exit looks like

*This is the section to check first.*

Base case: **NLPI holds 12.6% of every position, and SB2 keeps the other 87.4%.** SB2's
block remains with the Mauritius entity — it has by far the larger holding still to sell —
so a single exit is two sales, in two jurisdictions, at the same price:

| | Sells | Paid | Jurisdiction |
|---|---|---|---|
| SB2 | 87.4% of the position | into the fund, in Mauritius | non-resident seller |
| NLPI | 12.6% of the position | directly to NLPI, in India | resident seller |

NLPF never receives anything from a buyer. It is inside the fund, and is paid out of SB2's
receipts.

**The exception, where it applies.** Where NLPI cannot hold a position directly — the
Delaware-domiciled companies, or any portco whose transfer does not complete — SB2 retains
100% of it and receives 100% of that cheque. Let **θ** be the share of NAV in which NLPI
does hold a slice; its stake in those positions is then **12.6% / θ**, so that it still
averages 12.6% of the portfolio. Schedule 1 must state θ per portco. §8 sets out the rule
that keeps the economics exact whatever θ turns out to be.

## 7. NLP's priority return

NLP's 1x comes back through two legs. Measured on NLPF's $3.5M they add to **10x** — the
whole cheque:

| Leg | Route | Multiple | Amount |
|---|---|---|---|
| The liquidation preference | SB2 → NLPF, in Mauritius | 8.74x | $30.59M |
| Pro-rata share sales | buyers → NLPI, in India | 1.26x | $4.41M |
| **NLP's 1x** | | **10.00x** | **$35.00M** |

SB2 cannot grant a preference over shares it has already sold, so the preference covers
only its own 87.4%. Both legs are exhausted at the same moment, and NLP is whole at
exactly $35M of exits.

**The preference is drafted as an entitlement, not as a multiple.** Stating it as 8.74x
fixes the wrong variable: the multiple depends on the final x1 and x2, on θ, and on where
the cheques happen to fall. On the illustration in §9 it works out at 8.74x only because
the first two exits total exactly $35M; had the priority been satisfied part-way through a
cheque it would read differently, with identical economics. So:

> **NLP's Aggregate Entitlement** is 100% of the first $35M of all distributions, and 14.1%
> of every dollar thereafter, measured across NLPF and NLPI together. NLPI's receipts from
> its own share sales count towards it. NLPF's Class B2 preference is the balance.

## 8. The distribution rule

At each exit, in order:

1. **The buyer pays NLPI directly** for the shares it sells — 12.6% of the cheque in the
   base case, 12.6%/θ where the exception in §6 applies, nil where NLPI holds nothing.
   This counts towards NLP's Aggregate Entitlement.
2. **SB2 pays NLPF the Top-Up** out of its own receipts: the amount required to bring NLP's
   cumulative receipts up to its cumulative Aggregate Entitlement. While the $35M priority
   is unsatisfied this absorbs 100% of SB2's receipts. The Top-Up is never negative.
3. **SB2 distributes the balance** — Class A **36.6%**, Class B1 **63.4%** (being 31.4 and
   54.5 of the absolute cheque).

Class A therefore receives exactly 31.4% and Class B1 exactly 54.5% of every dollar above
the priority, whatever the mix of exits — which a fixed preference multiple cannot deliver.

**One cap is required.** Where θ < 89.4%, NLPI's stake in the positions it does hold
(12.6%/θ) exceeds NLP's 14.1% tail share, so on those exits NLPI collects more than NLP is
entitled to, and a Top-Up can only stop, not reverse. Left alone, the split becomes
order-dependent: on a full realisation of the portfolio, selling the NLPI-held positions
last leaves NLP $9.8M ahead of its entitlement, out of Class A and the old LPs. So:

> **NLPI sells, in each exit, the lesser of (i) its pro-rata shareholding and (ii) the
> amount that keeps NLP's cumulative receipts equal to its Aggregate Entitlement**, keeping
> the shares it does not sell for a later exit.

With that cap every ordering lands on 31.4 / 54.5 / 14.1 exactly. In the base case (θ =
100%, stake 12.6% < 14.1%) the cap never binds.

## 9. Worked example

Two exits, as in the previous version: $20M in WheelsEye at $800M, then a $25M secondary in
Niyo at $500M (5% of the company), in tranches of $15M and $10M. Base case, θ = 100%.

| | Cheque | → NLPI | → SB2 | of which pref | Class B2 | Class A | Class B1 | priority left |
|---|---|---|---|---|---|---|---|---|
| WheelsEye · 2.5% of the company | $20.00M | $2.52M | $17.48M | $17.48M | — | — | — | $15.00M |
| Niyo · first $15M | $15.00M | $1.89M | $13.11M | $13.11M | — | — | — | **nil** |
| Niyo · next $10M | $10.00M | $1.26M | $8.74M | — | $0.15M | $3.14M | $5.45M | nil |

- On the first two exits every dollar goes to NLP: $4.41M directly to NLPI and $30.59M to
  NLPF under the preference. **$35.00M — NLP's 1x, satisfied exactly.**
- WheelsEye: NLPI sells 2.5% × 12.6% = **0.315%** of the company for $2.52M; SB2 sells
  2.185% for $17.48M.
- From the third tranche on, each cheque splits 31.4 / 54.5 / 14.1 in absolute terms —
  NLP's 14.1% arriving as $1.26M directly plus a $0.15M Class B2 Top-Up.
- Totals on $45M: NLP $36.41M, Class A $3.14M, Class B1 $5.45M.

## 10. Exit conditions

- SB2 and NLP sell pro-rata at every exit — secondary, IPO, or post-IPO — subject to the cap
  in §8. Effectively a put/call across the two holdings.
- Delaware-domiciled companies: amend the SHA to carry the put/call. The India-domiciled
  companies need the equivalent, and both engage other shareholders' ROFR, tag and drag
  rights, and IPO lock-ups. Schedule 2 to list the consents required, per portco.

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
4. **Schedule 1** — per portco: SB2's holding, carrying value, θ, and NLPI's 12.6% slice in
   shares and dollars, summing to $31.5M.
5. **Precision.** 14.1%, 12.6% and 1.4% are illustrative to one decimal. Recompute all of
   them, and the ratios in §4, from the final cheque and NAV at signing.
6. **"mg"** in the portco list is not expanded anywhere.

## 12. Changelog against the previous version

| | Was | Now | Why |
|---|---|---|---|
| Post-ROC cap table | Class A 31.4% + Class B 69.6% | Class A 31.4% + Class B **68.6%** | The two must sum to 100%, and the tail (31.4 + 54.5 + 14.1) confirms 68.6%. |
| NLPI's slice of an exit cheque | 1.4% in the WheelsEye and first Niyo exits, 12% in the tail | **12.6%** throughout, per §6 | A shareholding cannot change between two tranches of the same sale. 1.4% is x1 — a percentage of Class B inside the fund, not of a portco position. The WheelsEye line computed "2.5% × x2_WE" and then printed 0.035%, which is 2.5% × 1.4%; at x2 it is 0.315%. |
| The preference | 10x, then ~10x (9.86x) on NLPF's $3.5M | An **Aggregate Entitlement** of $35M then 14.1%, with the preference as the balance — **8.74x** on the illustration | 9.86x was 10x net of a 1.4% pro-rata sale. At 12.6% the legs are 8.74x + 1.26x. More to the point, no fixed multiple survives a change in x2, in θ, or in where the cheques fall; leaving it at 9.86x while NLPI sells 12.6% would run the preference $4.49M past NLP's 1x and transfer $3.85M from Class A and the old LPs. |
| Class B2's entitlement | x1 = 1.4% of Class B, and separately 2% of absolute in the tail | The **Top-Up** in §8 — a make-whole interest | The two statements are inconsistent (1.4% of Class B is 0.96% of absolute), and a fixed percentage cannot absorb the timing differences the two-vehicle structure creates. |
| Niyo secondary | $25M at $500M described as 6% of the company | **5%** | $25M ÷ $500M. The document's own sub-figures (2.958% + 0.042% for $15M) already imply 5%. |
| SB2's retained block | not addressed | §6 | SB2 keeps 87.4% of every position and sells it in Mauritius; the exception where NLPI holds nothing is parameterised as θ. |
| Ordering | not addressed | The cap in §8 | Without it the split between NLP, Class A and Class B1 depends on the order the positions are sold in. |
| NLPF → NLPI | "Open Question", asked twice | Item 3 in §11 | It is an intra-group transfer, not an economic mismatch — but it carries the bulk of the priority return. |
