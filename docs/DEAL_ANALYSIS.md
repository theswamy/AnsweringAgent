# SB2 / NLP secondary — analysis

Analysis of the transaction document (Google Doc `1vepHdrEY2IuuM9TjwH0ced5FOrRerA0ugtr0gxD8tFU`,
as revised 2026-08-27 — the liqpref restated from 10x to 9.86x). Section ids `[S1]`–`[S10]` refer to `deal_agent/document.py`, which
holds the document verbatim; every number below is computed by `deal_agent` and
covered by its tests.

```
python -m deal_agent report          # everything in this note, regenerated
python -m deal_agent ask "..."       # ask the agent
```

## 1. What the transaction is

NLP buys **$35M of exposure to SB2 from the existing Class B LPs at a 35% discount**,
takes its 1x back ahead of everyone, and then shares pari-passu `[S3]`. Because only
part of the cheque can move offshore-to-offshore, it arrives through two entities `[S5]`:

| Entity | Amount | What it buys | Where it sits |
|---|---|---|---|
| NLPF (Singapore feeder) | $3.5M (10%) | x1 = 1.4% of Class B, with a **9.86x liqpref** | Primary capital into SB2 Mauritius |
| NLPI (India fund) | $31.5M (90%) | x2 = 12.6% of SB2's stake in each portco | Direct onshore shareholdings |

So $3.5M is primary money into the fund and $31.5M is a secondary purchase of assets
*from* the fund. The pref on the feeder is not a return expectation — it is sized to the
whole NLP cheque and exists to route NLPI's onshore purchase price back through
Mauritius.

**NLP's 1x is settled through two legs.** Measured on the feeder's $3.5M, they add to
10x — the whole cheque:

| Leg | Route | Multiple | Amount |
|---|---|---|---|
| The liqpref | SB2 → NLPF, in Mauritius | 9.86x | $34.51M |
| Pro-rata share sales | buyers → NLPI, onshore in India | 0.14x | $0.49M |
| **NLP's 1x, settled** | | **10.00x** | **$35.00M** |

That is why the pref is 9.86x rather than a round 10x: SB2 cannot prefer what it no
longer owns, so the pref is the balance after NLPI's own pro-rata sales. Both legs run
out at the same moment, and NLP is whole at exactly $35M of exits.

The pref therefore moves with the size of the second leg:

```
pref = (1 − NLPI's pro-rata share of each exit) × $35M
```

`[S9]` derives 9.86 as (19.72 + 14.79) / 3.5, which reads as though it came out of the
two illustrative exits. It did not — the rule holds for any exit sequence. What those
exits do carry is a **1.4%** pro-rata sale, where `[S5]` says NLPI owns 12.6%; at 12.6%
the legs are 8.74x + 1.26x. That is F2, and it is the one number still to settle.

## 2. The document's arithmetic checks out

Recomputed from the fund's primitives — 2%/98% commitments, $35M of ROC still to
return, 30% carry above it — the headline figures are right:

| | Document | Recomputed |
|---|---|---|
| Profit above ROC | $325M | $325.00M |
| GP stake | "about $100M" | $102.05M (**31.40%** of profit) |
| LP profits | "about $225M" | $222.95M (**68.60%**) |
| LP NAV | "effectively $260M" | $257.25M |
| Cheque as % of LP | 13% | 13.61% |
| … grossed up for the 35% discount | 20% | 20.93% |
| … as % of all profit | 14.1% | 14.36% |
| Post-deal tail | 31.4 / 54.5 / 14.1 | closes to 100.0% |

Two structural points worth stating explicitly, because they are what make the
document's fixed ratios legitimate:

- With a single 1x hurdle and no catch-up tiers, the GP's share of profit is
  **31.40% at any profit level**. Quoting fixed ratios instead of a tiered waterfall
  changes nobody's economics.
- The secondary is sold out of Class B, so **Class A is not diluted**. NLP's 14.1%
  comes entirely out of Class B's 68.60%, leaving old LPs 54.5%. That is why `[S10]`
  can give Class A 31% of absolute while the fund only receives 88% of each cheque —
  31.4/87.4 = 35.9% of SB2's receipts.

## 3. Where it does not close

Fourteen findings — twelve open (five high, four medium, three low) and two closed by
the 27 August revision, kept below as a record. The ones to settle first are set out
first. `python -m deal_agent findings` prints the whole register with live numbers and a
suggested fix for each.

### F2 — the same secondary splits two different ways

These are consecutive tranches of the one $25M Niyo sale, as the document sets them out:

| Tranche | To SB2 | To NLPI | NLPI's slice |
|---|---|---|---|
| a) first $15M `[S9]` | $14.79M | $0.21M | **1.4%** |
| b) next $10M `[S10]` | $8.80M | $1.20M | **12%** |

NLPI's shareholding cannot change between two tranches of the same sale. `[S5]` says it
owns 12.6%; the worked exits compute NLP's slice as "2.5% × x2_WE" and then print the
value of x1 = 1.4%, which is a percentage of Class B *inside* the fund, not of a portco
position. On the $20M WheelsEye exit the difference is $0.28M against $2.52M to NLPI.

And it sizes the pref, because the two legs must add to 10x:

| NLPI sells pro-rata | The two legs | Pref |
|---|---|---|
| 1.4% — the worked exits | 9.86x + 0.14x | $34.51M, as drafted |
| 12.6% — x2, per `[S5]` | **8.74x + 1.26x** | $30.59M |

Either way NLP is whole at exactly $35M. But leaving the pref at 9.86x while NLPI sells
12.6% keeps it running after NLP is already whole: it clears only at $39.49M of exits,
transferring **$3.85M** to NLP — $1.41M from Class A and $2.44M from the old LPs.

### F14 — the pref multiple should be drafted as a formula, not a number

9.86x is not an independently negotiated term — it is 10x less whatever NLPI's pro-rata
sales bring in. `[S6]` says the exact x1 and x2 will differ from the illustration, so
every change to them moves the multiple, as does any decision to bring more of NLPI's
recovery home directly (F8).

Draft it as an amount with its derivation — "$34.51M, being $35M less NLPI's onshore
percentage of it" — or as a cap on aggregate priority receipts across both NLP entities,
rather than as a hard multiple on the feeder's $3.5M.

### F4 — x1 appears in three different denominators

1.4% is defined as a share of Class B `[S5]`, used as a share of a portco cheque
`[S8][S9]`, and appears as 2% of absolute in the tail `[S10]`. These are three different
numbers. 1.4% of Class B is 0.96% of absolute, which puts NLP's total at 13.56%, not
14.1%. Fixing NLP's entitlement at 14.1% and NLPI's direct stake at 12.6% back-solves
the feeder to **1.5% of absolute ≈ 2.2% of Class B**.

### F8 — almost all of the 1x lands in the vehicle that funded a tenth of it

Asked twice by the document itself `[S8][S9]`: *"NLP_F then distributes pro-rata to NLP in
India — how does the NLPI fund receive its returns?"*

NLPF and NLPI are both NLP, so this is an intra-group transfer rather than an economic
mismatch. But it carries nearly all of the money home: NLPI funds **$31.5M** and receives
**$0.49M** of the first $35M — the other $34.51M arrives in Singapore. So the route has to
be papered rather than assumed: how value leaves NLPF, the tax on each hop, and whether
both vehicles carry the same LP base. If they do, this is mechanics for 99% of the
recovery. If they do not, the allocation between the two vehicles stops being mechanics.

It also interacts with F2: a larger pro-rata slice for NLPI brings more of the recovery
home directly — at 12.6% it receives $4.41M of the first $35M instead of $0.49M — so
settling F2 reduces what has to be repatriated at all.

### Closed by the 27 August revision

**F3 — the marker is now exact.** Before the revision, `[S9]` declared the pref satisfied
after SB2 had received $19.72M + $14.79M = $34.51M against a $35M pref — $0.49M short.
Resizing to 9.86x makes it exact: the pref is exhausted to the cent, NLPI's pro-rata
sales have brought in the other $0.49M, and NLP has been repaid exactly $35.00M across
both entities. What survives is which pro-rata percentage the second leg carries, which
is F2.

**F5 — "the first 35M" is now measured across both entities.** The open question was
whether NLPI's own sale proceeds counted towards NLP's first $35M. The two-leg sizing
answers it: they do, and the pref is the balance. What is left is which pro-rata
percentage the second leg carries (F2), and saying the aggregate $35M cap explicitly so
the netting cannot be applied twice in the drafting. One drafting point remains — state the
priority return as an aggregate $35M across NLPF and NLPI, with the pref expressed as
the balance after NLPI's onshore receipts, so the netting is explicit and cannot be
applied twice. Netting it twice would leave NLP $0.48M short of its 1x and start the
tail early.

### The rest

| | |
|---|---|
| **F7** | The 9.86x pref is a **$34.51M senior claim funded with $3.5M**, ranking ahead of both existing classes, and it is participating — `[S10]` leaves Class B2 sharing in the tail after repayment. Needs to be stated as such, and consented to. |
| **F10** | $31.5M buys Indian portco shares from a Mauritius fund at a discount to carrying value. Fair-value pricing floor on the inbound leg, capital-gains withholding at the SB2 level, and `[S6]` only *assumes* the leakage is grossed up — yet that gross-up determines x2, and therefore every exit split. |
| **F9** | The pro-rata exit undertaking `[S7]` needs SHA amendments at the India-domiciled portcos too, not only the Delaware ones, and engages other shareholders' ROFR / tag / drag rights and IPO lock-ups. |
| **F6** | `[S6]` assumes both classes are "whole", but the $35M that makes that true is paid to Class B. Class A's 2% of the remaining ROC — $0.70M — has no source. |
| **F1** | `[S2]`'s post-ROC cap table sums to 101%: Class B should be 68.6%, not 69.6%. |
| **F11 / F12** | Rounding gaps of 0.2–0.9pp carried into the operative ratios; "mg" is never expanded and no per-portco position schedule ties x2 to the $31.5M. |

## 4. What the deal is worth to each side

NLP is repaid first, so it is whole as long as the remaining portfolio returns $35M
against a $360M carrying value, and makes **2.31x** if it returns all of it.

For the old LPs the trade is **liquidity, not upside**. They swap 14.1% of all future
profit for $35M today — and because $35M is close to the $34.30M of ROC they were owed
anyway, indifference sits at roughly **$40M of total future proceeds**. Above that they
are paying with upside:

| Realisation | Class B1 with the deal | Without | Give-up |
|---|---|---|---|
| 0.25× NAV ($90M) | $65.0M | $72.0M | −$7.1M |
| 0.50× NAV ($180M) | $114.0M | $133.8M | −$19.7M |
| 1.00× NAV ($360M) | $212.1M | $257.3M | −$45.1M |
| 1.50× NAV ($540M) | $310.2M | $380.7M | −$70.5M |

That is the 35% discount doing exactly what it is meant to do, and immediate 1x DPI
is a defensible thing to buy. But it should go to the LPs framed as the price of
de-risking, with this table attached — not as a neutral restructuring.

## 5. What to fix before papering

1. **Settle NLPI's pro-rata slice — 1.4% or 12.6% — and re-derive the pref multiple from
   it (F2, F4, F14).** It sets every exit split and the pref together.
2. State the priority return as an aggregate $35M across both NLP vehicles, with the pref
   drafted as the balance after NLPI's own sales (F5, F14).
3. Price the onshore transfer taxes and confirm the discount survives the pricing floor,
   then re-derive x1 and x2 from the grossed-up cheque (F10).
4. Paper the NLPF → NLPI route and its tax treatment, and confirm the two vehicles' LP
   bases align (F8).
5. Attach a per-portco schedule — holding, carrying value, the 12.6% slice in shares
   and dollars, summing to $31.5M (F12).
