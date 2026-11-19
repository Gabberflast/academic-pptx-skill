# Slide Patterns for Pitch Decks

How to build each section with `scripts/deck_kit.js` in pitch mode. A complete seed deck
using every pattern is in `examples/build_pitch_example.js`. The company and every
number in it and in the snippets below are invented.

Read [pitch_guidelines.md](pitch_guidelines.md) first for what belongs on each slide.

---

## Setup

```javascript
const { createDeck, NEEDS } = require("./deck_kit.js");

const deck = createDeck({
  mode: "pitch",
  title: "Ledgerline seed deck",
  author: "Ledgerline",
  colors: { accent: "2563EB" },   // the company's one brand colour
  // scheme: "emerald",           // or a named scheme (customization.md)
  // face: "Inter",               // their typeface, if it will be installed where the deck is opened
  // rules: "deck_rules.md",      // the founder's saved colours, limits and house rules
});

// ... slides ...

deck.save("ledgerline_seed.pptx");
```

Pitch mode differs from academic mode in three ways: larger type (titles 32 pt, body
24 pt), a tighter word limit (about 25 body words), and a `kicker` on every slide: the
small section label above the title. The linter uses the kicker to recognise sections,
so use the standard names: Problem, Solution, Traction, Why now, Market, Business
model, Competition, Team, The ask, Vision.

Every builder takes `notes:`. Write them: they are the founder's talk track.

Five builders cover a whole deck:

| Builder | Shape | Typical sections |
|---------|-------|------------------|
| `hero` | One huge number with its label | Problem, a single killer metric |
| `tiles` | Two to four side-by-side blocks | Solution steps, Market arithmetic, Business model |
| `result` | One chart or table, two takeaways | Traction, Competition |
| `statement` | A claim and up to three points | Why now, Vision, Go-to-market |
| `team`, `ask`, `pitchTitle` | Purpose-built | Team, The ask, Title |

---

## 1. Title

Company name and one line a stranger would understand. Fourteen words at most.

```javascript
deck.pitchTitle({
  company: "Ledgerline",
  oneLiner: "Insurance paperwork for independent clinics, done in minutes instead of days.",
  round: "Seed round · March 2026",
  contact: "maya@ledgerline.example",
  notes: "One breath: who we are and what we do.",
});
```

## 2. Problem

A person or business, what hurts, and how much. `hero` when one number tells it.

```javascript
deck.hero({
  kicker: "Problem",
  title: "Independent clinics lose two days a week to insurance approvals",
  number: "14 hrs",
  label: "per clinician, every week, on approval forms",
  support: "So clinics overhire billing staff or turn patients away.",
  cite: "Source: Ledgerline survey of 212 clinic managers, 2025",
  notes: "Make it one clinic manager's week. Then the number.",
});
```

No single number? Use `statement` with the customer's situation in two or three points.

## 3. Solution

What the product does, in three steps or fewer. No screenshots.

```javascript
deck.tiles({
  kicker: "Solution",
  title: "Ledgerline files and chases every approval automatically",
  numbered: true,
  tiles: [
    { label: "Reads the chart",   note: "Pulls diagnosis and history" },
    { label: "Files the form",    note: "In each insurer's own format" },
    { label: "Chases the answer", note: "Tracks status, appeals denials" },
  ],
  notes: "Three steps. Offer the live demo after the deck.",
});
```

## 4. Traction

One chart. The title states the growth with its time window; the latest value is
highlighted and called out.

```javascript
deck.result({
  kicker: "Traction",
  title: "Revenue has grown 22% a month for eight months, with no paid marketing",
  exhibit: {
    type: "bar",
    labels: ["Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb"],
    values: [11, 13, 16, 20, 24, 30, 36, 44],
    highlight: 7,
    axisTitle: "MRR ($k)",
    annotation: "$44k MRR in February",
  },
  takeaways: [{ label: "63 clinics", text: "paying" }, { label: "0", text: "churned since launch" }],
  cite: "Source: Ledgerline billing data, Jul 2025 – Feb 2026",
  notes: "Say the growth rate and the window together.",
});
```

Plot the metric per period (monthly revenue, weekly active users), not a cumulative
total, which rises even when growth has stopped. Before there is a curve to show, use
`tiles` with the real counts and say what each is:

```javascript
deck.tiles({
  kicker: "Traction",
  title: "Three clinics are paying for a pilot and 40 more have asked for one",
  tiles: [
    { value: "3",   label: "paid pilots",        note: "started May 2026" },
    { value: "40",  label: "on the waitlist",    note: "from two conference talks" },
    { value: "?",   label: "approvals filed a week", note: NEEDS("pilot usage from the founder") },
  ],
  cite: "Source: company records, June 2026",
  notes: "...",
});
```

## 5. Why now

What changed that makes this possible or urgent. Specific and checkable.

```javascript
deck.statement({
  kicker: "Why now",
  title: "A 2026 rule makes insurers accept electronic approvals for the first time",
  points: [
    "Until this year, most approvals had to go by fax or phone",
    "Language models can now read clinical notes reliably enough to file them",
  ],
  cite: "Source: <the rule, with its citation>",
  notes: "The bottleneck was never software; insurers would not accept electronic submissions.",
});
```

## 6. Market

Bottom-up, with the arithmetic on the slide: buyers × annual price = market.

```javascript
deck.tiles({
  kicker: "Market",
  title: "38,000 independent clinics could pay us $4.2B a year",
  tiles: [
    { value: "38,000", label: "independent US clinics", note: "with 2–20 clinicians" },
    { value: "$110k",  label: "per clinic, per year",   note: "our current average contract" },
    { value: "$4.2B",  label: "annual market",          note: "38,000 × $110k, before hospitals" },
  ],
  cite: "Source: <who counted the clinics, year>; contract value from company billing data",
  notes: "Count of buyers times what they pay us today. Hospitals are upside.",
});
```

## 7. Business model

Who pays, how much, and what it costs to serve them.

```javascript
deck.tiles({
  kicker: "Business model",
  title: "Clinics pay per clinician, and serving them costs a fifth of that",
  tiles: [
    { value: "$690", label: "per clinician, per month", note: "annual contracts" },
    { value: "81%",  label: "gross margin",             note: "after model and filing costs" },
    { value: "4 mo", label: "sales payback",            note: "founder-led so far" },
  ],
  cite: "Source: company billing and cost data, trailing six months",
  notes: "...",
});
```

## 8. Competition

A small table of the real alternatives on the two or three dimensions customers care
about. Your column is highlighted. Include a row where someone else is better.

```javascript
deck.result({
  kicker: "Competition",
  title: "Billing firms are slow; clearinghouses stop at filing",
  exhibit: {
    type: "table",
    header: ["", "Ledgerline", "Billing firms", "Clearinghouses"],
    rows: [
      ["Time to file",               "Minutes", "2–3 days", "Minutes"],
      ["Follows up and appeals",     "Yes",     "Yes",      "No"],
      ["Cost per clinician / month", "$690",    "$2,400",   "$150"],
    ],
    highlightCol: 1,
  },
  cite: "Source: public price lists and customer interviews, 2025",
  notes: "Be fair to them. Clearinghouses are cheaper; say why that is not the comparison.",
});
```

## 9. Team

Founders only. One or two proof lines each, with a number in at least one.

```javascript
deck.team({
  title: "We ran clinic billing and built insurer systems before starting Ledgerline",
  members: [
    { name: "Maya Okonkwo", role: "CEO", proof: ["Ran billing for a 40-clinic group", "Cut denials 31% in two years"] },
    { name: "Daniel Reyes", role: "CTO", proof: ["Built claims intake at a top-5 insurer", "System handled 2M claims a day"] },
  ],
  notes: "One of us lived the problem; the other built the system on the other side of it.",
});
```

`photo: "maya.jpg"` adds a headshot. Use only photos the founders supply.

## 10. The ask

Amount, what it buys, where that gets the company. No valuation, cap or discount. This
is the last slide before the appendix and stays on screen.

```javascript
deck.ask({
  title: "$3M takes us to 400 clinics and $3M in annual revenue",
  amount: "$3M",
  milestones: [
    { label: "Sales",   text: "first four hires" },
    { label: "Product", text: "ten more insurers" },
    { label: "Result",  text: "Series A ready in 18 months" },
  ],
  contact: "maya@ledgerline.example   ·   ledgerline.example",
  notes: "End here.",
});
```

## 11. Vision (optional)

```javascript
deck.statement({
  kicker: "Vision",
  title: "Approvals are the wedge; in five years we run the clinic's whole revenue cycle",
  points: ["Next: claims and denials", "Then: patient billing"],
  notes: "Why the wedge is narrow on purpose, and what it opens.",
});
```

## 12. Appendix

Same builders with a label. Not presented; ready for questions.

```javascript
deck.appendix({
  label: "Appendix — Retention",
  title: "Every 2025 clinic still pays, and each one keeps adding clinicians",
  bullets: [
    { label: "Logo retention", text: "100% across 63 clinics" },
    { label: "Net revenue retention", text: "128%, from added clinicians" },
  ],
  cite: "Source: company billing data, Jul 2025 – Feb 2026",
  notes: "Backup for 'what does retention look like?'",
});
```

---

## A stage (demo day) version

Same sections, less on each slide. Swap `tiles` and `statement` slides for `hero` where
one number or phrase can carry the point, drop the supporting line, and put everything
you removed into the speaker notes. Two sections can share a slide (market and business
model; competition and why now) when the slot is two or three minutes.

---

## Before delivery

```
□ node build ran with no kit warnings
□ lint_deck.py --mode pitch reports no errors, and no [[NEEDS]] remain
□ Ghost deck: the titles alone make the case for the company
□ Title slide: name and one line a stranger would understand
□ Every number has a unit, a time window and a source the founder can back
□ Traction chart: per-period metric, latest value highlighted
□ Market: buyers × price shown
□ Competition: real alternatives, at least one row where they win
□ Team: founders only, a quantified proof line each
□ The ask: amount, use, milestone; no terms; last slide before the appendix
□ 10–12 slides before the appendix
□ Rendered to images and every slide looked at
□ The founder has confirmed every figure, name and logo
```
