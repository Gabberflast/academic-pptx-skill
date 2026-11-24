"use strict";
/**
 * Example: a 12-minute conference talk built with deck_kit.js.
 *
 * ALL CONTENT IS INVENTED for illustration — the study, the numbers and the
 * references do not exist. Do not reuse them.
 *
 * Run:  NODE_PATH=$(npm root -g) node examples/build_academic_example.js [out.pptx] [deck_rules.md]
 */
const path = require("path");
const { createDeck } = require(path.join(__dirname, "..", "scripts", "deck_kit.js"));

const out = process.argv[2] || "academic_example.pptx";
const deck = createDeck({
  mode: "academic",
  title: "Tutoring effects persist to graduation",
  author: "A. Rivera, B. Chen",
  footer: "Rivera & Chen · Example Conference 2026",
  rules: process.argv[3],   // optional: path to a deck_rules.md
});

deck.titleSlide({
  title: "High-dosage tutoring in grade 6 raises graduation rates six years later",
  venue: "Example Conference on Education Policy  ·  March 2026",
  authors: "Ana Rivera¹  ·  Bo Chen²",
  affiliations: "¹ Example University   ² Sample Institute",
  notes: "Thank the chair. One sentence: we followed a randomized tutoring cohort to graduation, and the effect did not fade.",
});

deck.content({
  title: "Tutoring reliably raises test scores, but nobody knows whether the gains last",
  bullets: [
    { label: "Short run is settled", text: "scores rise 0.2–0.4 SD within a year (Park et al., 2021)" },
    { label: "Long run is not", text: "only two trials track students past grade 9 (Okafor & Lind, 2019)" },
    { label: "Stakes", text: "districts fund tutoring expecting lasting gains" },
  ],
  cite: "Park et al. (2021); Okafor & Lind (2019)",
  notes: "Situation, then complication. Say the sources aloud: 'Park and colleagues showed in 2021 that...'. The gap is persistence — that sets up the question on the next slide.",
});

deck.question({
  title: "We ask: does grade 6 tutoring still matter at graduation?",
  question: "Do students randomly assigned to high-dosage math tutoring in grade 6 graduate high school at higher rates, and is the effect concentrated among students who started behind?",
  contribution: "first randomized cohort linked to graduation records six years on.",
  notes: "Pause here. This is the slide the audience uses to judge everything that follows. Read the question once, slowly.",
});

deck.twoColumn({
  title: "A lottery for oversubscribed tutoring seats gives us random assignment",
  left: {
    header: "Design",
    bullets: [
      { label: "Sample", text: "2,400 grade 6 students, 31 schools" },
      { label: "Assignment", text: "seat lottery, 1,150 treated" },
    ],
  },
  right: {
    header: "Outcomes",
    bullets: [
      { label: "Primary", text: "on-time graduation" },
      { label: "Split", text: "baseline math quartile" },
    ],
  },
  cite: "Balance tests and attrition → Appendix A",
  notes: "Only what they need to trust the result: who, how assigned, what we measure. Balance and attrition are in Appendix A if asked.",
});

deck.result({
  title: "Tutored students graduate 9 points more often, and the lowest quartile gains most",
  exhibit: {
    type: "bar",
    labels: ["Q1 (lowest)", "Q2", "Q3", "Q4 (highest)"],
    values: [14, 10, 7, 4],
    highlight: 0,
    axisTitle: "Graduation effect (pp)",
    annotation: "Q1: +14 pp, 3.5× the Q4 effect",
  },
  takeaways: [
    { label: "Average", text: "+9 pp (p < 0.01)" },
    { label: "Gradient", text: "effect falls with baseline score" },
    { label: "Precision", text: "95% CI [5, 13]" },
  ],
  cite: "Source: authors' calculations from district graduation records, N = 2,400",
  notes: "Point at the first bar before saying anything else. Then the average, then the gradient. Do not read the confidence interval aloud unless asked.",
});

deck.result({
  title: "The gap opens in grade 7 and never closes",
  exhibit: {
    type: "line",
    labels: ["G6", "G7", "G8", "G9", "G10", "G11", "G12"],
    series: [
      { name: "Tutored", values: [0.0, 0.28, 0.27, 0.25, 0.24, 0.24, 0.23] },
      { name: "Control", values: [0.0, 0.02, 0.01, 0.0, 0.01, 0.0, 0.0] },
    ],
    highlight: "Tutored",
    axisTitle: "Math score (SD)",
    annotation: "Fade-out is under 20% after six years",
  },
  takeaways: [
    { label: "Jump", text: "0.28 SD after one year" },
    { label: "Fade", text: "only 0.05 SD lost by grade 12" },
  ],
  cite: "Source: authors' calculations from state assessment records",
  notes: "This answers the persistence question directly. The usual pattern is that half the gain is gone in two years; here less than a fifth is gone in six.",
});

deck.content({
  title: "Lasting skill gains, not extra credits, appear to carry the effect",
  groups: [
    {
      header: "Interpretation",
      bullets: ["Graduation effect disappears once grade 8 scores are held fixed (Appendix B)"],
    },
    {
      header: "Main limitation",
      bullets: [{ label: "External validity", text: "one urban district; lottery schools were oversubscribed" }],
    },
  ],
  notes: "State the limitation yourself before someone else does. Mediation analysis is in Appendix B.",
});

deck.conclusions({
  takeaways: [
    { label: "Effects last", text: "a 9-point graduation gain six years after one year of tutoring." },
    { label: "Targeting matters", text: "students who start behind gain 3.5× as much." },
    { label: "Skills carry it", text: "test-score gains persist and account for the effect." },
  ],
  contact: "ana.rivera@example.edu   |   Working paper: example.edu/tutoring",
  notes: "Stop here and leave this up for the whole Q&A. 'I'll stop there — questions and feedback are very welcome.'",
});

deck.references({
  refs: [
    "Okafor, N. & Lind, S. (2019). Following tutored students into high school. Journal of Example Studies, 12(3), 201–230.",
    "Park, J., Alvarez, M., & Stone, R. (2021). Short-run effects of high-dosage tutoring: a meta-analysis. Review of Example Research, 44(1), 1–38.",
    "Rivera, A. & Chen, B. (2026). Does tutoring last? Evidence from a seat lottery. Working paper.",
  ],
});

deck.appendix({
  label: "Appendix A — Balance and attrition",
  title: "Lottery winners and losers look alike at baseline, and attrition is balanced",
  exhibit: {
    type: "table",
    header: ["", "Tutored", "Control", "p-value"],
    rows: [
      ["Baseline math (SD)", "−0.02", "0.01", "0.61"],
      ["Free lunch (%)", "71", "70", "0.74"],
      ["Missing at G12 (%)", "11", "12", "0.48"],
    ],
  },
  cite: "Source: authors' calculations from district enrollment records",
  notes: "Backup for 'is the lottery really random?' and 'what about attrition?'.",
});

deck.appendix({
  label: "Appendix B — Mediation",
  title: "Holding grade 8 scores fixed removes the graduation effect",
  bullets: [
    { label: "Unadjusted", text: "+9 pp" },
    { label: "Adjusted for grade 8 score", text: "+1 pp (not significant)" },
    { label: "Adjusted for credits earned", text: "+8 pp" },
  ],
  cite: "Source: authors' calculations",
  notes: "Backup for 'what is the mechanism?'. Mediation is descriptive, not causal — say so.",
});

deck.save(out);
