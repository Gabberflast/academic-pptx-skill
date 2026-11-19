"use strict";
/**
 * Example: a seed pitch deck built with deck_kit.js.
 *
 * ALL CONTENT IS INVENTED for illustration — the company, the customers and
 * every number are made up. Do not reuse them.
 *
 * Run:  NODE_PATH=$(npm root -g) node examples/build_pitch_example.js [out.pptx] [deck_rules.md]
 */
const path = require("path");
const { createDeck } = require(path.join(__dirname, "..", "scripts", "deck_kit.js"));

const out = process.argv[2] || "pitch_example.pptx";
const deck = createDeck({
  mode: "pitch",
  title: "Ledgerline seed deck",
  author: "Ledgerline",
  rules: process.argv[3],   // optional: path to a deck_rules.md
});

deck.pitchTitle({
  company: "Ledgerline",
  oneLiner: "Insurance paperwork for independent clinics, done in minutes instead of days.",
  round: "Seed round · March 2026",
  contact: "maya@ledgerline.example",
  notes: "One breath: who we are and what we do. No backstory yet.",
});

deck.hero({
  kicker: "Problem",
  title: "Independent clinics lose two days a week to insurance approvals",
  number: "14 hrs",
  label: "per clinician, every week, on approval forms",
  support: "So clinics overhire billing staff or turn patients away.",
  cite: "Source: Ledgerline survey of 212 clinic managers, 2025",
  notes: "Make it a person's problem: a clinic manager with a fax machine and a phone queue. Then the number.",
});

deck.tiles({
  kicker: "Solution",
  title: "Ledgerline files and chases every approval automatically",
  numbered: true,
  tiles: [
    { label: "Reads the chart", note: "Pulls diagnosis and history" },
    { label: "Files the form", note: "In each insurer's own format" },
    { label: "Chases the answer", note: "Tracks status, appeals denials" },
  ],
  notes: "Three steps, no screenshots. Offer the live demo after the deck.",
});

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
  takeaways: [
    { label: "63 clinics", text: "paying" },
    { label: "0", text: "churned since launch" },
  ],
  cite: "Source: Ledgerline billing data, Jul 2025 – Feb 2026",
  notes: "Say the growth rate and the time window together. The curve is not perfectly smooth and that is fine.",
});

deck.statement({
  kicker: "Why now",
  title: "A 2026 rule makes insurers accept electronic approvals for the first time",
  points: [
    "Until this year, most approvals had to go by fax or phone",
    "Language models can now read clinical notes reliably enough to file them",
  ],
  cite: "Source: illustrative — replace with the actual rule citation",
  notes: "The insight: the bottleneck was never software, it was that insurers would not accept electronic submissions. That changed.",
});

deck.tiles({
  kicker: "Market",
  title: "38,000 independent clinics could pay us $4.2B a year",
  tiles: [
    { value: "38,000", label: "independent US clinics", note: "with 2–20 clinicians" },
    { value: "$110k", label: "per clinic, per year", note: "our current average contract" },
    { value: "$4.2B", label: "annual market", note: "38,000 × $110k, before hospitals" },
  ],
  cite: "Source: illustrative clinic count; contract value from Ledgerline billing data",
  notes: "Bottom-up: count of buyers times what they pay us today. Hospitals are upside, not in this number.",
});

deck.tiles({
  kicker: "Business model",
  title: "Clinics pay per clinician, and serving them costs a fifth of that",
  tiles: [
    { value: "$690", label: "per clinician, per month", note: "annual contracts" },
    { value: "81%", label: "gross margin", note: "after model and filing costs" },
    { value: "4 mo", label: "sales payback", note: "founder-led so far" },
  ],
  cite: "Source: Ledgerline billing and cost data, trailing six months",
  notes: "How we make money, in one line. Unit economics detail is in the appendix.",
});

deck.result({
  kicker: "Competition",
  title: "Billing firms are slow; clearinghouses stop at filing",
  exhibit: {
    type: "table",
    header: ["", "Ledgerline", "Billing firms", "Clearinghouses"],
    rows: [
      ["Time to file", "Minutes", "2–3 days", "Minutes"],
      ["Follows up and appeals", "Yes", "Yes", "No"],
      ["Cost per clinician / month", "$690", "$2,400", "$150"],
    ],
    highlightCol: 1,
  },
  cite: "Source: public price lists and customer interviews, 2025",
  notes: "Name the real alternatives, including doing nothing. Be fair to them — investors will check.",
});

deck.team({
  title: "We ran clinic billing and built insurer systems before starting Ledgerline",
  members: [
    { name: "Maya Okonkwo", role: "CEO", proof: ["Ran billing for a 40-clinic group", "Cut denials 31% in two years"] },
    { name: "Daniel Reyes", role: "CTO", proof: ["Built claims intake at a top-5 insurer", "System handled 2M claims a day"] },
  ],
  notes: "Why us: one of us lived the problem, the other built the system on the other side of it.",
});

deck.ask({
  title: "$3M takes us to 400 clinics and $3M in annual revenue",
  amount: "$3M",
  milestones: [
    { label: "Sales", text: "first four hires" },
    { label: "Product", text: "ten more insurers" },
    { label: "Result", text: "Series A ready in 18 months" },
  ],
  contact: "maya@ledgerline.example   ·   ledgerline.example",
  notes: "End here. Amount, what it buys, where it gets us. No valuation on the slide.",
});

deck.appendix({
  label: "Appendix — Retention",
  title: "Every 2025 clinic still pays, and each one keeps adding clinicians",
  bullets: [
    { label: "Logo retention", text: "100% across 63 clinics" },
    { label: "Net revenue retention", text: "128%, from added clinicians" },
  ],
  cite: "Source: Ledgerline billing data, Jul 2025 – Feb 2026",
  notes: "Backup for 'what does retention look like?'.",
});

deck.save(out);
