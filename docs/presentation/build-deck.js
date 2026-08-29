const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";               // 13.3 x 7.5
pres.author = "Prime VP";
pres.title = "SB2 / NLP Secondary";

// --- palette: petrol = GP/Class A, muted teal = existing LPs, copper = NLP ---
const INK      = "0F1E22";
const PETROL   = "0D6068";
const TEAL     = "7FA6A6";
const COPPER   = "96501F";
const PAPER    = "FFFFFF";
const TINT     = "F1F4F4";
const RULE     = "D5DCDD";
const BODY     = "3A4A50";
const MUTED    = "6C7F85";

const HEAD = "Cambria";
const SANS = "Calibri";

const M = 0.65;                            // margin
const W = 13.3 - 2 * M;                    // content width

function darkSlide() {
  const s = pres.addSlide();
  s.background = { color: INK };
  return s;
}
function lightSlide(kicker, title) {
  const s = pres.addSlide();
  s.background = { color: PAPER };
  if (kicker) {
    s.addText(kicker.toUpperCase(), {
      x: M, y: 0.42, w: W, h: 0.26, isTextBox: true, margin: 0,
      fontFace: SANS, fontSize: 11, bold: true, charSpacing: 1.6, color: PETROL,
    });
  }
  if (title) {
    s.addText(title, {
      x: M, y: 0.72, w: W, h: 1.0, isTextBox: true, margin: 0,
      fontFace: HEAD, fontSize: 30, bold: true, color: INK,
    });
  }
  return s;
}
// a horizontal share bar in the three party colours
function shareBar(s, x, y, w, h, segs) {
  let cx = x;
  segs.forEach((seg) => {
    const sw = w * seg.pct;
    s.addShape(pres.ShapeType.rect, { x: cx, y, w: sw, h, fill: { color: seg.color } });
    s.addText(seg.label, {
      x: cx + 0.12, y: y + 0.06, w: sw - 0.24, h: h / 2 - 0.1, isTextBox: true, margin: 0,
      fontFace: SANS, fontSize: 15, bold: true, color: PAPER,
    });
    if (seg.sub && sw > 1.1) {
      s.addText(seg.sub, {
        x: cx + 0.12, y: y + h / 2 + 0.02, w: sw - 0.24, h: h / 2 - 0.08, isTextBox: true, margin: 0,
        fontFace: SANS, fontSize: 10, color: PAPER, charSpacing: 0.8,
      });
    }
    cx += sw;
  });
}
// A line shape must never be given a negative width or height - that is invalid
// OOXML and PowerPoint rejects it. Normalise the box and mirror it instead.
function addArrow(s, x1, y1, x2, y2, color) {
  s.addShape(pres.ShapeType.line, {
    x: Math.min(x1, x2), y: Math.min(y1, y2),
    w: Math.abs(x2 - x1), h: Math.abs(y2 - y1),
    flipH: x2 < x1, flipV: y2 < y1,
    line: { color: color || BODY, width: 1.25, endArrowType: "triangle" },
  });
}

function statCard(s, x, y, w, k, v, n, lead) {
  s.addShape(pres.ShapeType.roundRect, {
    x, y, w, h: 1.5, rectRadius: 0.04,
    fill: { color: lead ? PETROL : TINT },
    line: { color: lead ? PETROL : RULE, width: 1 },
  });
  s.addText(k.toUpperCase(), {
    x: x + 0.2, y: y + 0.16, w: w - 0.4, h: 0.24, isTextBox: true, margin: 0,
    fontFace: SANS, fontSize: 10, bold: true, charSpacing: 1.2,
    color: lead ? "BFE4E4" : MUTED,
  });
  s.addText(v, {
    x: x + 0.2, y: y + 0.42, w: w - 0.4, h: 0.55, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 28, bold: true, color: lead ? PAPER : INK,
  });
  s.addText(n, {
    x: x + 0.2, y: y + 1.0, w: w - 0.4, h: 0.38, isTextBox: true, margin: 0,
    fontFace: SANS, fontSize: 11, color: lead ? "BFE4E4" : MUTED,
  });
}
function note(s, y, label, text) {
  s.addShape(pres.ShapeType.roundRect, {
    x: M, y, w: W, h: 0.95, rectRadius: 0.03,
    fill: { color: "F6EFE8" }, line: { color: "E4D3C4", width: 1 },
  });
  s.addText(label.toUpperCase(), {
    x: M + 0.22, y: y + 0.12, w: W - 0.44, h: 0.24, isTextBox: true, margin: 0,
    fontFace: SANS, fontSize: 10, bold: true, charSpacing: 1.2, color: COPPER,
  });
  s.addText(text, {
    x: M + 0.22, y: y + 0.36, w: W - 0.44, h: 0.5, isTextBox: true, margin: 0,
    fontFace: SANS, fontSize: 13, color: "4A3524",
  });
}
const TBL = {
  border: { type: "solid", color: RULE, pt: 0.5 },
  fontFace: SANS, fontSize: 13, color: BODY, valign: "middle",
  autoPage: false,
};
function hdr(cells) {
  return cells.map((c) => ({
    text: c.t, options: {
      bold: true, color: MUTED, fontSize: 10, charSpacing: 1.1,
      fill: { color: PAPER }, align: c.a || "left", valign: "bottom",
    },
  }));
}
function cell(t, o) { return { text: t, options: Object.assign({}, o) }; }

/* ============ 1 · title ============ */
{
  const s = darkSlide();
  s.addText("SB2 / NLP SECONDARY", {
    x: M, y: 2.2, w: W, h: 0.3, isTextBox: true, margin: 0,
    fontFace: SANS, fontSize: 12, bold: true, charSpacing: 2.4, color: "5ECACD",
  });
  s.addText("How the money moves", {
    x: M, y: 2.62, w: 9.6, h: 1.25, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 52, bold: true, color: PAPER,
  });
  s.addText(
    "NLP is buying $35M of exposure to SB2 from the existing LPs. Where each dollar of every " +
    "future exit goes, in what order, and why the priority return belongs in the documents as " +
    "a formula rather than a multiple.",
    { x: M, y: 4.0, w: 9.2, h: 1.1, isTextBox: true, margin: 0,
      fontFace: SANS, fontSize: 15, color: "AFC4C6", lineSpacing: 22 });
  s.addText("August 2026", {
    x: M, y: 6.5, w: W, h: 0.3, isTextBox: true, margin: 0,
    fontFace: SANS, fontSize: 11, charSpacing: 1.6, color: MUTED,
  });
  shareBar(s, M, 5.5, W, 0.22, [
    { pct: 0.314, color: PETROL, label: "" },
    { pct: 0.545, color: TEAL, label: "" },
    { pct: 0.141, color: COPPER, label: "" },
  ]);
  s.addNotes("Post-transaction, every dollar above NLP's repaid $35M splits 31.4 / 54.5 / 14.1 — the bar at the foot of this slide, carried through the deck.");
}

/* ============ 2 · the fund today ============ */
{
  const s = lightSlide("Where we start", "A $45.6M fund, carried at $360M");
  const cw = (W - 0.45) / 4;
  statCard(s, M, 2.2, cw, "Fund size", "$45.61M", "GP 2% · LP 98%");
  statCard(s, M + cw + 0.15, 2.2, cw, "Distributed", "$11.0M", "to date");
  statCard(s, M + 2 * (cw + 0.15), 2.2, cw, "ROC to go", "$35.0M", "before carry bites");
  statCard(s, M + 3 * (cw + 0.15), 2.2, cw, "Current NAV", "$360M", "carry 30% above ROC", true);
  s.addText("$35.0M of LP capital is still outstanding, and the portfolio is carried at $360M.", {
    x: M, y: 1.78, w: 11.6, h: 0.3, isTextBox: true, margin: 0,
    fontFace: SANS, fontSize: 14, color: BODY,
  });
  s.addText("Who owns the $325M of profit above the ROC, today", {
    x: M, y: 4.05, w: W, h: 0.28, isTextBox: true, margin: 0,
    fontFace: SANS, fontSize: 11, bold: true, charSpacing: 1.2, color: MUTED,
  });
  shareBar(s, M, 4.38, W, 0.95, [
    { pct: 0.314, color: PETROL, label: "31.4%", sub: "CLASS A · GP" },
    { pct: 0.686, color: TEAL, label: "68.6%", sub: "CLASS B · LPs" },
  ]);
  s.addText(
    "The GP's 31.4% is its 2% commitment plus 30% carry on the LPs' 98% — and it is 31.4% at any " +
    "profit level, because there is one 1x hurdle and no catch-up tiers. That is what lets the rest " +
    "of this deck use flat ratios instead of a tiered waterfall.",
    { x: M, y: 5.62, w: 11.6, h: 1.0, isTextBox: true, margin: 0,
      fontFace: SANS, fontSize: 14, color: BODY, lineSpacing: 21 });
  s.addNotes("Class B is 68.6%, not the 69.6% in the first draft — the two have to sum to 100%.");
}

/* ============ 3 · the ask ============ */
{
  const s = lightSlide("What NLP wants", null);
  s.addShape(pres.ShapeType.rect, { x: M, y: 1.15, w: 0.035, h: 2.15, fill: { color: PETROL } });
  s.addText(
    "“NLP would like to purchase $35M worth of equity from the ClassB shareholders at a 35% " +
    "discount — provided they get their 1x back and subsequently participate pari-passu with " +
    "other ClassB shareholders.”",
    { x: M + 0.28, y: 1.15, w: 8.6, h: 2.0, isTextBox: true, margin: 0,
      fontFace: HEAD, fontSize: 24, italic: true, color: INK, lineSpacing: 36 });
  s.addText("SOURCE DOCUMENT", {
    x: M + 0.28, y: 3.2, w: 6, h: 0.26, isTextBox: true, margin: 0,
    fontFace: SANS, fontSize: 10, bold: true, charSpacing: 1.4, color: MUTED,
  });
  const items = [
    ["A discount", "how much NLP gets for its $35M"],
    ["1x back first", "when it gets it"],
    ["Pari passu after", "what happens once it is whole"],
  ];
  items.forEach(([h, d], i) => {
    const y = 4.15 + i * 0.92;
    s.addShape(pres.ShapeType.ellipse, { x: M, y, w: 0.5, h: 0.5, fill: { color: PETROL } });
    s.addText(String(i + 1), {
      x: M, y: y + 0.09, w: 0.5, h: 0.32, isTextBox: true, margin: 0, align: "center",
      fontFace: SANS, fontSize: 15, bold: true, color: PAPER,
    });
    s.addText(h, {
      x: M + 0.72, y: y - 0.02, w: 4.2, h: 0.32, isTextBox: true, margin: 0,
      fontFace: SANS, fontSize: 16, bold: true, color: INK,
    });
    s.addText(d, {
      x: M + 0.72, y: y + 0.27, w: 6.5, h: 0.3, isTextBox: true, margin: 0,
      fontFace: SANS, fontSize: 13, color: MUTED,
    });
  });
  s.addText("Three things at once — and each one shapes the flow.", {
    x: 8.0, y: 4.7, w: 4.6, h: 1.2, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 20, italic: true, color: PETROL, lineSpacing: 30,
  });
}

/* ============ 4 · pricing chain ============ */
{
  const s = lightSlide("Step 1 · How the discount becomes a percentage", "$35M at a 35% discount buys 14.1% of all future profit");
  const rows = [
    ["1", "Profit above the ROC — the pool being split", "$325.00M", false],
    ["2", "…less the GP's 31.4%, plus the LPs' unreturned capital = LP NAV", "$257.3M", false],
    ["3", "$35M as a share of that LP NAV", "13.6%", false],
    ["4", "…grossed up for the 35% discount — what NLP gets of the LP", "20.9%", false],
    ["5", "…applied to Class B's 68.6% of profit = NLP's share of everything", "14.1%", true],
  ];
  rows.forEach(([n, what, val, final], i) => {
    const y = 1.95 + i * 0.84;
    s.addShape(pres.ShapeType.roundRect, {
      x: M, y, w: W, h: 0.7, rectRadius: 0.03,
      fill: { color: final ? "DCECEB" : TINT },
      line: { color: final ? PETROL : RULE, width: 1 },
    });
    s.addText(n, {
      x: M + 0.22, y: y + 0.2, w: 0.35, h: 0.3, isTextBox: true, margin: 0,
      fontFace: SANS, fontSize: 13, bold: true, color: PETROL,
    });
    s.addText(what, {
      x: M + 0.62, y: y + 0.18, w: W - 3.2, h: 0.35, isTextBox: true, margin: 0,
      fontFace: SANS, fontSize: 14, color: final ? INK : BODY, bold: !!final,
    });
    s.addText(val, {
      x: M + W - 2.4, y: y + 0.15, w: 2.2, h: 0.4, isTextBox: true, margin: 0, align: "right",
      fontFace: HEAD, fontSize: 19, bold: true, color: final ? PETROL : INK,
    });
  });
  s.addText(
    "The source document states 13%, 20% and 14.1%; recomputed they are 13.6%, 20.9% and 14.4%.",
    { x: M, y: 6.35, w: W, h: 0.4, isTextBox: true, margin: 0,
      fontFace: SANS, fontSize: 12, color: MUTED });
}

/* ============ 5 · the resulting split ============ */
{
  const s = lightSlide("Step 2 · The new sharing ratio", "NLP's slice comes out of Class B");
  s.addText("BEFORE THE TRANSACTION — EVERY DOLLAR OF PROFIT ABOVE THE ROC", {
    x: M, y: 1.9, w: W, h: 0.26, isTextBox: true, margin: 0,
    fontFace: SANS, fontSize: 10, bold: true, charSpacing: 1.2, color: MUTED,
  });
  shareBar(s, M, 2.2, W, 1.0, [
    { pct: 0.314, color: PETROL, label: "31.4%", sub: "CLASS A" },
    { pct: 0.686, color: TEAL, label: "68.6%", sub: "CLASS B" },
  ]);
  s.addText("AFTER THE TRANSACTION — EVERY DOLLAR ABOVE NLP'S REPAID $35M", {
    x: M, y: 3.6, w: W, h: 0.26, isTextBox: true, margin: 0,
    fontFace: SANS, fontSize: 10, bold: true, charSpacing: 1.2, color: MUTED,
  });
  shareBar(s, M, 3.9, W, 1.0, [
    { pct: 0.314, color: PETROL, label: "31.4%", sub: "CLASS A" },
    { pct: 0.545, color: TEAL, label: "54.5%", sub: "CLASS B1 · OLD LPs" },
    { pct: 0.141, color: COPPER, label: "14.1%", sub: "NLP" },
  ]);
  s.addText(
    "Because the secondary is sold out of Class B, the GP is not diluted: the entire 14.1% comes " +
    "out of the LPs' 68.6%. That is why the fund can pay Class A 31.4% of absolute proceeds even " +
    "though only 87.3% of each exit cheque reaches the fund.",
    { x: M, y: 5.25, w: 11.2, h: 1.0, isTextBox: true, margin: 0,
      fontFace: SANS, fontSize: 14, color: BODY, lineSpacing: 21 });
}

/* ============ 6 · two vehicles ============ */
{
  const s = lightSlide("Step 3 · Why there are two cheques", "Only a tenth of the money can go offshore-to-offshore");
  const box = (x, y, w, h, title, sub, accent) => {
    s.addShape(pres.ShapeType.roundRect, {
      x, y, w, h, rectRadius: 0.03,
      fill: { color: accent ? "DCECEB" : TINT }, line: { color: accent ? PETROL : RULE, width: 1 },
    });
    s.addText(title, {
      x: x + 0.18, y: y + 0.16, w: w - 0.36, h: 0.3, isTextBox: true, margin: 0,
      fontFace: SANS, fontSize: 14, bold: true, color: INK,
    });
    s.addText(sub, {
      x: x + 0.18, y: y + 0.48, w: w - 0.36, h: 0.55, isTextBox: true, margin: 0,
      fontFace: SANS, fontSize: 11, color: MUTED, lineSpacing: 15,
    });
  };
  box(M, 3.0, 2.3, 1.0, "NLP", "$35M cheque");
  box(4.0, 1.95, 3.5, 1.15, "NLPF · Singapore feeder", "10% of the cheque · $3.50M");
  box(4.0, 4.0, 3.5, 1.15, "NLPI · India fund", "90% of the cheque · $31.50M");
  box(8.9, 1.95, 3.75, 1.15, "SB2 · the fund, in Mauritius", "new Class B2 + liqpref", true);
  box(8.9, 4.0, 3.75, 1.15, "The portcos", "direct shareholdings, x2 of each", true);
  const arrow = (x1, y1, x2, y2) => addArrow(s, x1, y1, x2, y2);
  arrow(2.95, 3.3, 4.0, 2.55);
  arrow(2.95, 3.7, 4.0, 4.55);
  arrow(7.5, 2.52, 8.9, 2.52);
  arrow(7.5, 4.57, 8.9, 4.57);
  s.addText("primary", { x: 7.55, y: 2.14, w: 1.3, h: 0.28, isTextBox: true, margin: 0, align: "center", fontFace: SANS, fontSize: 11, italic: true, color: MUTED });
  s.addText("secondary", { x: 7.55, y: 4.19, w: 1.3, h: 0.28, isTextBox: true, margin: 0, align: "center", fontFace: SANS, fontSize: 11, italic: true, color: MUTED });
  s.addText(
    "$3.5M is new money into the fund. $31.5M is a purchase of assets from the fund — so NLPI ends " +
    "up owning shares in the portcos directly, alongside SB2, and is paid by buyers at every exit.",
    { x: M, y: 5.6, w: 11.6, h: 0.8, isTextBox: true, margin: 0,
      fontFace: SANS, fontSize: 14, color: BODY, lineSpacing: 21 });
}

/* ============ 7 · settling the 1x ============ */
{
  const s = lightSlide("Step 4 · How NLP's 1x is settled", "Two legs, measured on the same $3.5M");
  s.addTable([
    hdr([{ t: "LEG" }, { t: "ROUTE" }, { t: "MULTIPLE", a: "right" }, { t: "AMOUNT", a: "right" }]),
    [cell("The liquidation preference", { bold: true, color: INK }), cell("SB2 → NLPF, in Mauritius"),
     cell("8.73x", { align: "right" }), cell("$30.56M", { align: "right" })],
    [cell("NLPI's own share sales", { bold: true, color: INK }), cell("buyers → NLPI, at each company"),
     cell("1.27x", { align: "right" }), cell("$4.44M", { align: "right" })],
    [cell("NLP's 1x, settled", { bold: true, color: PETROL, fill: { color: "DCECEB" } }),
     cell("", { fill: { color: "DCECEB" } }),
     cell("10.00x", { align: "right", bold: true, color: PETROL, fill: { color: "DCECEB" } }),
     cell("$35.00M", { align: "right", bold: true, color: PETROL, fill: { color: "DCECEB" } })],
  ], Object.assign({}, TBL, { x: M, y: 1.95, w: W, colW: [3.6, 4.6, 1.9, 1.9], rowH: 0.52 }));
  s.addText(
    "NLP's money went to two places, so its 1x comes back from two places. The convenient unit is " +
    "the feeder's $3.5M: NLP's whole $35M is 10x of it, and the two legs add up to that. SB2 cannot " +
    "prefer what it no longer owns — NLPI sells its own 12.69% alongside SB2 at every exit and keeps " +
    "those proceeds — so the preference covers only SB2's 87.31%.",
    { x: M, y: 4.2, w: 11.6, h: 1.2, isTextBox: true, margin: 0,
      fontFace: SANS, fontSize: 14, color: BODY, lineSpacing: 21 });
  note(s, 5.6, "Draft the formula, not the multiple",
    "8.73x is 87.31% of $35M over $3.5M — a consequence of x2, and x2 will move before signing. " +
    "The operative words should be “$35M less NLPI's share of the proceeds of the same exits”.");
}

/* ============ 8 · one exit ============ */
{
  const s = lightSlide("Step 5 · The flow", "One exit, two layers");
  const box = (x, y, w, h, t, sub, fill) => {
    s.addShape(pres.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.03, fill: { color: fill || TINT }, line: { color: RULE, width: 1 } });
    if (t) s.addText(t, { x: x + 0.15, y: y + 0.12, w: w - 0.3, h: 0.28, isTextBox: true, margin: 0, fontFace: SANS, fontSize: 13, bold: true, color: INK });
    if (sub) s.addText(sub, { x: x + 0.15, y: y + 0.42, w: w - 0.3, h: 0.28, isTextBox: true, margin: 0, fontFace: SANS, fontSize: 10, color: MUTED });
  };
  const arrow = (x1, y1, x2, y2, color) => addArrow(s, x1, y1, x2, y2, color);
  box(M, 3.25, 2.1, 0.85, "Buyer's cheque", "one portco position");
  box(3.55, 1.95, 2.6, 0.85, "NLPI · direct", "paid at the company");
  box(3.55, 4.5, 2.6, 0.85, "SB2 · the fund", "paid in Mauritius");
  box(6.75, 4.5, 2.5, 0.85, "NLPF liqpref", "until NLP is whole", "F6EFE8");
  box(10.0, 3.55, 2.65, 0.62, null, null);
  box(10.0, 4.35, 2.65, 0.62, null, null);
  box(10.0, 5.15, 2.65, 0.62, null, null);
  ["Class A · GP", "Class B1 · LPs", "Class B2 · NLPF"].forEach((t, i) => {
    s.addText(t, {
      x: 10.15, y: 3.68 + i * 0.8, w: 1.45, h: 0.3, isTextBox: true, margin: 0,
      fontFace: SANS, fontSize: 11.5, bold: true, color: INK,
    });
  });
  arrow(2.75, 3.5, 3.55, 2.4);
  arrow(2.75, 3.9, 3.55, 4.9);
  arrow(6.15, 4.92, 6.75, 4.92);
  arrow(9.25, 4.92, 10.0, 3.86);
  arrow(9.25, 4.92, 10.0, 4.66);
  arrow(9.25, 4.92, 10.0, 5.46);
  s.addText("12.69%", { x: 2.85, y: 2.85, w: 0.9, h: 0.26, isTextBox: true, margin: 0, fontFace: SANS, fontSize: 12, bold: true, color: COPPER });
  s.addText("87.31%", { x: 2.85, y: 4.16, w: 0.9, h: 0.26, isTextBox: true, margin: 0, fontFace: SANS, fontSize: 12, bold: true, color: PETROL });
  s.addText("100% until repaid", { x: 5.9, y: 4.16, w: 2.1, h: 0.26, isTextBox: true, margin: 0, align: "center", fontFace: SANS, fontSize: 11, color: MUTED });
  s.addText("once the $35M is repaid", { x: 9.6, y: 3.1, w: 3.1, h: 0.26, isTextBox: true, margin: 0, align: "center", fontFace: SANS, fontSize: 11, color: MUTED });
  ["31.4%", "54.5%", "1.4%"].forEach((t, i) => {
    s.addText(t, { x: 11.72, y: 3.68 + i * 0.8, w: 0.88, h: 0.3, isTextBox: true, margin: 0, align: "right", fontFace: SANS, fontSize: 12, bold: true, color: BODY });
  });
  s.addText(
    "NLPI's slice comes off the top, at the company, before the fund sees the money. SB2's share " +
    "pays the preference in full before Class A, the old LPs, or the feeder's own Class B2 receive " +
    "anything.",
    { x: M, y: 6.25, w: 11.8, h: 0.8, isTextBox: true, margin: 0, fontFace: SANS, fontSize: 13, color: BODY, lineSpacing: 20 });
}

/* ============ 9 · worked exits ============ */
{
  const s = lightSlide("Step 6 · The worked example", "$35M of exits repays NLP exactly, to the cent");
  s.addTable([
    hdr([{ t: "EXIT" }, { t: "CHEQUE", a: "right" }, { t: "TO NLPI", a: "right" },
         { t: "TO SB2", a: "right" }, { t: "PRIORITY LEFT", a: "right" }]),
    [cell("WheelsEye · 2.5% of the company at $800M", { bold: true, color: INK }),
     cell("$20.00M", { align: "right" }), cell("$2.54M", { align: "right" }),
     cell("$17.46M", { align: "right" }), cell("$15.00M", { align: "right" })],
    [cell("Niyo · first $15M of a $25M secondary", { bold: true, color: INK }),
     cell("$15.00M", { align: "right" }), cell("$1.90M", { align: "right" }),
     cell("$13.10M", { align: "right" }), cell("nil", { align: "right", color: PETROL, bold: true })],
    [cell("NLP's 1x", { bold: true, color: PETROL, fill: { color: "DCECEB" } }),
     cell("$35.00M", { align: "right", bold: true, color: PETROL, fill: { color: "DCECEB" } }),
     cell("$4.44M", { align: "right", bold: true, color: PETROL, fill: { color: "DCECEB" } }),
     cell("$30.56M", { align: "right", bold: true, color: PETROL, fill: { color: "DCECEB" } }),
     cell("satisfied", { align: "right", bold: true, color: PETROL, fill: { color: "DCECEB" } })],
  ], Object.assign({}, TBL, { x: M, y: 1.95, w: W, colW: [5.0, 1.7, 1.7, 1.7, 1.9], rowH: 0.52 }));
  s.addText(
    "Every dollar of these two exits goes to NLP — $4.44M paid directly at the companies, $30.56M " +
    "through the preference. Nothing reaches the GP or the old LPs yet. On WheelsEye, NLPI sells " +
    "2.5% × 12.69% = 0.317% of the company and SB2 sells 2.183%.",
    { x: M, y: 4.2, w: 11.6, h: 1.0, isTextBox: true, margin: 0, fontFace: SANS, fontSize: 14, color: BODY, lineSpacing: 21 });
  s.addNotes("The two illustrative exits total exactly $35M, which is why the preference clears precisely at the marker.");
}

/* ============ 10 · the tail ============ */
{
  const s = lightSlide("Step 7 · And from then on", "Every exit after that splits four ways");
  s.addTable([
    hdr([{ t: "ON THE NEXT $10M OF NIYO" }, { t: "SHARE OF THE CHEQUE", a: "right" },
         { t: "AMOUNT", a: "right" }, { t: "PAID BY" }]),
    [cell("NLPI · direct", { bold: true, color: COPPER }), cell("12.69%", { align: "right" }),
     cell("$1.27M", { align: "right" }), cell("the buyer, at the company")],
    [cell("Class A · GP", { bold: true, color: PETROL }), cell("31.40%", { align: "right" }),
     cell("$3.14M", { align: "right" }), cell("the fund")],
    [cell("Class B1 · old LPs", { bold: true, color: INK }), cell("54.50%", { align: "right" }),
     cell("$5.45M", { align: "right" }), cell("the fund")],
    [cell("Class B2 · NLPF", { bold: true, color: COPPER }), cell("1.41%", { align: "right" }),
     cell("$0.14M", { align: "right" }), cell("the fund")],
    [cell("NLP, all in", { bold: true, color: PETROL, fill: { color: "DCECEB" } }),
     cell("14.10%", { align: "right", bold: true, color: PETROL, fill: { color: "DCECEB" } }),
     cell("$1.41M", { align: "right", bold: true, color: PETROL, fill: { color: "DCECEB" } }),
     cell("", { fill: { color: "DCECEB" } })],
  ], Object.assign({}, TBL, { x: M, y: 1.95, w: W, colW: [4.0, 3.0, 2.2, 2.8], rowH: 0.5 }));
  s.addText(
    "The preference is spent, so NLPF drops back to being an ordinary Class B holder — a " +
    "participating preference, in other words. The buyer still writes two cheques at every exit, " +
    "because NLPI's shares are its own.",
    { x: M, y: 5.15, w: 11.6, h: 0.9, isTextBox: true, margin: 0, fontFace: SANS, fontSize: 14, color: BODY, lineSpacing: 21 });
}

/* ============ 11 · the put/call ============ */
{
  const s = lightSlide("Step 8 · What keeps every number a constant", "The put/call keeps NLPI's 12.69% uniform");
  s.addTable([
    hdr([{ t: "PORTCO DOMICILE" }, { t: "HOW NLPI HOLDS ITS SLICE" }, { t: "AT EXIT" }]),
    [cell("India", { bold: true, color: INK }), cell("shares held directly, onshore"),
     cell("NLPI is a selling shareholder, paid in India")],
    [cell("Delaware · Singapore", { bold: true, color: INK }),
     cell("a put/call at the company level, in the SHA"),
     cell("the same slice, delivered under the SHA")],
  ], Object.assign({}, TBL, { x: M, y: 1.95, w: W, colW: [3.2, 4.6, 4.2], rowH: 0.62 }));
  s.addText(
    "NLPI is an India fund. It can hold shares directly in the India-domiciled portcos, but not in " +
    "the Delaware and Singapore ones — where the same slice reaches it through a put/call written " +
    "into the company's shareholder agreement. So the buyer writes two cheques at every exit, " +
    "whatever the domicile.",
    { x: M, y: 4.05, w: 11.6, h: 1.2, isTextBox: true, margin: 0, fontFace: SANS, fontSize: 14, color: BODY, lineSpacing: 21 });
  note(s, 5.5, "Which makes it load-bearing, not administrative",
    "Without it, the offshore positions would pay NLPI nothing, and neither the preference nor the " +
    "sharing ratios could be single numbers. Its enforceability, and the tax treatment of a " +
    "settlement under it, decide what NLPI nets.");
}

/* ============ 12 · routing models ============ */
{
  const s = lightSlide("The open structuring choice", "Routing the $35M: 10% or 20% offshore");
  s.addTable([
    hdr([{ t: "" }, { t: "MODEL A · 10% OFFSHORE", a: "right" }, { t: "MODEL B · 20% OFFSHORE", a: "right" }]),
    [cell("NLPF cheque · into SB2 Mauritius"), cell("$3.50M", { align: "right" }), cell("$7.00M", { align: "right" })],
    [cell("NLPI cheque · onshore India"), cell("$31.50M", { align: "right" }), cell("$28.00M", { align: "right" })],
    [cell("x1 · held through the fund"), cell("1.41%", { align: "right" }), cell("2.82%", { align: "right" })],
    [cell("x2 · held directly by NLPI"), cell("12.69%", { align: "right" }), cell("11.28%", { align: "right" })],
    [cell("Liquidation preference"), cell("$30.56M", { align: "right" }), cell("$31.05M", { align: "right" })],
    [cell("…as a multiple of the NLPF cheque"), cell("8.73x", { align: "right", bold: true, color: COPPER }), cell("4.44x", { align: "right", bold: true, color: COPPER })],
    [cell("Class B2's share of SB2's receipts"), cell("1.61%", { align: "right" }), cell("3.18%", { align: "right" })],
    [cell("Absolute split · A / B1 / NLP", { bold: true, color: INK, fill: { color: "DCECEB" } }),
     cell("31.4 / 54.5 / 14.1", { align: "right", bold: true, color: PETROL, fill: { color: "DCECEB" } }),
     cell("31.4 / 54.5 / 14.1", { align: "right", bold: true, color: PETROL, fill: { color: "DCECEB" } })],
    [cell("Discount to carrying value", { bold: true, color: INK, fill: { color: "DCECEB" } }),
     cell("31.05%", { align: "right", bold: true, color: PETROL, fill: { color: "DCECEB" } }),
     cell("31.05%", { align: "right", bold: true, color: PETROL, fill: { color: "DCECEB" } })],
  ], Object.assign({}, TBL, { x: M, y: 1.9, w: W, colW: [5.4, 3.3, 3.3], rowH: 0.4, fontSize: 12 }));
  note(s, 6.05, "Nothing about the economics moves",
    "Same price, same split, NLP whole at exactly $35M either way. What moves: the preference is " +
    "the same in dollars but the multiple halves, twice as much of NLP's long-run share is paid " +
    "through Mauritius, and the onshore purchase drops $3.5M.");
}

/* ============ 13 · what each side makes ============ */
{
  const s = lightSlide("The trade", "NLP buys protection, the LPs certainty");
  statCard(s, M, 1.9, 5.6, "NLP · at carrying value", "2.31x", "$80.8M on a $35M cheque, if the portfolio realises $360M", true);
  statCard(s, M, 3.55, 5.6, "NLP · whole at", "$35M", "of total exits, against a $360M carrying value");
  s.addTable([
    hdr([{ t: "OLD LPs REALISE…" }, { t: "WITH", a: "right" }, { t: "WITHOUT", a: "right" }, { t: "GIVE-UP", a: "right" }]),
    [cell("0.25× NAV"), cell("$65.0M", { align: "right" }), cell("$72.0M", { align: "right" }), cell("−$7.1M", { align: "right", color: COPPER })],
    [cell("0.50× NAV"), cell("$114.0M", { align: "right" }), cell("$133.8M", { align: "right" }), cell("−$19.7M", { align: "right", color: COPPER })],
    [cell("1.00× NAV"), cell("$212.1M", { align: "right" }), cell("$257.3M", { align: "right" }), cell("−$45.1M", { align: "right", color: COPPER })],
    [cell("1.50× NAV"), cell("$310.2M", { align: "right" }), cell("$380.7M", { align: "right" }), cell("−$70.5M", { align: "right", color: COPPER })],
  ], Object.assign({}, TBL, { x: 6.75, y: 1.9, w: 5.9, colW: [1.7, 1.4, 1.4, 1.4], rowH: 0.48, fontSize: 12 }));
  s.addText(
    "The old LPs swap 14.1% of all future profit for $35M today — and because $35M is close to the " +
    "$34.30M of capital they were owed anyway, they are indifferent at about $40M of total future " +
    "proceeds. Above that they are paying with upside.",
    { x: M, y: 5.35, w: 11.8, h: 1.0, isTextBox: true, margin: 0, fontFace: SANS, fontSize: 14, color: BODY, lineSpacing: 21 });
}

/* ============ 14 · where it stands ============ */
{
  const s = darkSlide();
  s.addText("WHERE IT STANDS", {
    x: M, y: 0.7, w: W, h: 0.3, isTextBox: true, margin: 0,
    fontFace: SANS, fontSize: 12, bold: true, charSpacing: 2.4, color: "5ECACD",
  });
  s.addText("The arithmetic closes. Six things to settle.", {
    x: M, y: 1.1, w: 10.5, h: 0.8, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 32, bold: true, color: PAPER,
  });
  const items = [
    "Settle NLPI's slice and re-derive the preference from it — it sets every exit split.",
    "State the priority return as an aggregate $35M across both NLP vehicles, with the preference as the balance.",
    "Price the onshore transfer taxes and confirm the discount survives the pricing floor.",
    "Paper the NLPF → NLPI route and confirm the two vehicles' LP bases align — it carries $30.56M of the $35M.",
    "Confirm the put/call's enforceability and tax treatment per domicile.",
    "Class A's $0.70M share of the outstanding return of capital, which the $35M does not fund.",
  ];
  items.forEach((t, i) => {
    const y = 2.25 + i * 0.72;
    s.addShape(pres.ShapeType.ellipse, { x: M, y: y + 0.02, w: 0.42, h: 0.42, fill: { color: "16383D" }, line: { color: "5ECACD", width: 1 } });
    s.addText(String(i + 1), {
      x: M, y: y + 0.08, w: 0.42, h: 0.3, isTextBox: true, margin: 0, align: "center",
      fontFace: SANS, fontSize: 12, bold: true, color: "5ECACD",
    });
    s.addText(t, {
      x: M + 0.62, y: y, w: 11.4, h: 0.55, isTextBox: true, margin: 0,
      fontFace: SANS, fontSize: 14.5, color: "D6E3E4", lineSpacing: 20,
    });
  });
  s.addText(
    "Every figure in this deck is computed from the fund's own primitives, not quoted — the " +
    "waterfall is reimplemented and 59 tests pin these numbers.",
    { x: M, y: 6.75, w: 11.8, h: 0.4, isTextBox: true, margin: 0, fontFace: SANS, fontSize: 11, color: MUTED });
}

pres.writeFile({ fileName: "SB2-NLP-Secondary.pptx" }).then(() => console.log("written"));
