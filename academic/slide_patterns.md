# Slide Patterns for Academic Presentations

How to build each slide type with `scripts/deck_kit.js`. A complete deck using every
pattern is in `examples/build_academic_example.js` (its content is invented).

The kit sits on PptxGenJS and assumes the 16:9 layout (10" × 5.625"). It measures each
title, starts the body where the title ends, keeps a 0.5" margin, numbers the slides and
names every text box so `scripts/lint_deck.py` can check the result.

---

## Setup

```javascript
const { createDeck, NEEDS } = require("./deck_kit.js");

const deck = createDeck({
  mode: "academic",
  title: "Tutoring effects persist to graduation",   // file metadata
  author: "A. Rivera, B. Chen",
  footer: "Rivera & Chen · SOLE 2026",                // optional, bottom-left of every slide
  // sections: ["Motivation", "Design", "Results", "Discussion"],   // breadcrumb, long talks only
  // scheme: "forest",                                              // a named scheme (customization.md)
  // colors: { primary: "4B2E83", accent: "85754D" },               // institution colours
  // face: "Calibri",                                               // one typeface throughout
  // rules: "deck_rules.md",                                        // the user's saved colours and limits
});

// ... slides ...

deck.save("talk.pptx");   // prints build warnings, then the lint command to run
```

Defaults: navy `1F4E79` titles, mid-blue `2E75B6` accent, near-black `2D2D2D` body,
`595959` for source lines, Arial. Sizes: title 26 pt (drops to 22 for a long one),
body 20, chart labels 16, source lines 13.

Every builder takes `notes:` (speaker notes) and most take `cite:` (the source line at
the bottom). Give both. The kit warns when notes are missing.

Bullets are an array of strings or `{ label, text }` objects. A label is set in bold as
a lead-in: `{ label: "Sample", text: "2,400 students" }` → **Sample:** 2,400 students.

---

## 1. Title slide

The title is the talk's claim as a statement or a question, not a topic.

```javascript
deck.titleSlide({
  title: "High-dosage tutoring in grade 6 raises graduation rates six years later",
  venue: "Society of Labor Economists  ·  May 2026",
  authors: "Ana Rivera¹  ·  Bo Chen²",
  affiliations: "¹ University of X   ² Institute of Y",
  notes: "Thank the chair. One sentence on what we did and found.",
});
```

No crests, logos or images unless the user asks for them.

## 2. Motivation

Situation and complication: what is known, what is missing, why it matters.

```javascript
deck.content({
  title: "Tutoring reliably raises test scores, but nobody knows whether the gains last",
  bullets: [
    { label: "Short run is settled", text: "scores rise 0.2–0.4 SD within a year (Park et al., 2021)" },
    { label: "Long run is not", text: "only two trials track students past grade 9 (Okafor & Lind, 2019)" },
    { label: "Stakes", text: "districts fund tutoring expecting lasting gains" },
  ],
  cite: "Park et al. (2021); Okafor & Lind (2019)",
  notes: "Say the sources aloud. The gap is persistence — that sets up the question.",
});
```

## 3. Research question

On its own slide, within the first three or four. The audience judges everything
afterwards against it.

```javascript
deck.question({
  title: "We ask: does grade 6 tutoring still matter at graduation?",
  question: "Do students randomly assigned to high-dosage math tutoring in grade 6 graduate high school at higher rates, and is the effect concentrated among students who started behind?",
  contribution: "first randomized cohort linked to graduation records six years on.",
  notes: "Pause. Read the question once, slowly.",
});
```

## 4. Methods

Only what the audience needs in order to believe the result. One or two slides; the
rest is appendix.

```javascript
deck.twoColumn({
  title: "A lottery for oversubscribed tutoring seats gives us random assignment",
  left:  { header: "Design",   bullets: [{ label: "Sample", text: "2,400 grade 6 students, 31 schools" },
                                          { label: "Assignment", text: "seat lottery, 1,150 treated" }] },
  right: { header: "Outcomes", bullets: [{ label: "Primary", text: "on-time graduation" },
                                          { label: "Split", text: "baseline math quartile" }] },
  cite: "Balance tests and attrition → Appendix A",
  notes: "Who, how assigned, what we measure. Balance is in Appendix A if asked.",
});
```

## 5. Results

One finding, one exhibit, impossible to miss. The exhibit goes on the left, two or three
takeaways on the right.

```javascript
deck.result({
  title: "Tutored students graduate 9 points more often, and the lowest quartile gains most",
  exhibit: {
    type: "bar",
    labels: ["Q1 (lowest)", "Q2", "Q3", "Q4 (highest)"],
    values: [14, 10, 7, 4],
    highlight: 0,                                  // focal bar in the accent colour, the rest grey
    axisTitle: "Graduation effect (pp)",
    annotation: "Q1: +14 pp, 3.5× the Q4 effect",  // call-out placed above the chart
  },
  takeaways: [
    { label: "Average", text: "+9 pp (p < 0.01)" },
    { label: "Gradient", text: "effect falls with baseline score" },
    { label: "Precision", text: "95% CI [5, 13]" },
  ],
  cite: "Source: authors' calculations from district graduation records, N = 2,400",
  notes: "Point at the first bar before saying anything else.",
});
```

Exhibit types:

| `type` | Fields | Use for |
|--------|--------|---------|
| `"bar"` | `labels`, `values`, `highlight` (index), `axisTitle`, `horizontal`, `valueFormat` | Comparisons across groups |
| `"line"` | `labels`, `series: [{ name, values }]`, `highlight` (series name), `axisTitle` | Trends over time |
| `"image"` | `path`, `alt` | Anything drawn elsewhere: a matplotlib figure, a rendered equation, a diagram, a coefficient plot with error bars |
| `"table"` | `header`, `rows`, `highlightRow`, `highlightCol` | A few exact values; 24 cells at most |

Every type accepts `annotation`. A string is placed in a strip above the exhibit, where
it cannot cover data. `{ text, x, y }` places it at a fraction of the exhibit box, for
pointing at a specific feature; check the render when you use it.

**When to draw the figure yourself.** Native charts cover bars and lines. For error
bars, scatter plots, regression discontinuity plots, event studies, maps or any figure
where the call-out must point at a data coordinate, draw it in matplotlib at
presentation size and pass it as an image:

```python
import matplotlib.pyplot as plt
plt.rcParams.update({"font.size": 16, "font.family": "Arial", "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(figsize=(5.6, 3.4), dpi=200)            # the exhibit box, in inches
ax.errorbar(x, est, yerr=ci, fmt="o", color="#A6A6A6", capsize=4)
ax.errorbar(x[0], est[0], yerr=ci[0], fmt="o", color="#2E75B6", capsize=4)   # the focal estimate
ax.annotate("Q1: +14 pp", xy=(x[0], est[0]), xytext=(0.8, 16), arrowprops={"arrowstyle": "->"})
fig.savefig("fig_grad.png", bbox_inches="tight")
```

Use grey for everything except the series the title is about. Do not paste a figure cut
from the paper's PDF unless there is no way to rebuild it; if you must, say so in the
source line ("Source: Rivera & Chen (2026), Fig. 2").

## 6. Discussion

Interpret, connect back to the question, and name the main limitation before the
audience does.

```javascript
deck.content({
  title: "Lasting skill gains, not extra credits, appear to carry the effect",
  groups: [
    { header: "Interpretation",  bullets: ["Graduation effect disappears once grade 8 scores are held fixed (Appendix B)"] },
    { header: "Main limitation", bullets: [{ label: "External validity", text: "one urban district; lottery schools were oversubscribed" }] },
  ],
  notes: "State the limitation yourself.",
});
```

## 7. Conclusions

Two to four numbered takeaways, a contact line and a link. This is the last slide you
present and it stays up for the whole Q&A.

```javascript
deck.conclusions({
  takeaways: [
    { label: "Effects last", text: "a 9-point graduation gain six years after one year of tutoring." },
    { label: "Targeting matters", text: "students who start behind gain 3.5× as much." },
    { label: "Skills carry it", text: "test-score gains persist and account for the effect." },
  ],
  contact: "ana.rivera@university.edu   |   Working paper: university.edu/tutoring",
  // qr: "qr_paper.png",
  notes: "Stop here. 'I'll stop there — questions and feedback are very welcome.'",
});
```

## 8. References

After the conclusions, not presented. Pass the full list; the kit splits it across
slides rather than shrinking the type. Copy each entry from the paper's bibliography.

```javascript
deck.references({ refs: [
  "Okafor, N. & Lind, S. (2019). Following tutored students into high school. Journal of …, 12(3), 201–230.",
  "Park, J., Alvarez, M., & Stone, R. (2021). Short-run effects of high-dosage tutoring … , 44(1), 1–38.",
] });
```

## 9. Appendix

One backup slide per likely question. Label it and still give it an action title.
`appendix()` takes the same options as `content()` or, with an `exhibit`, `result()`.

```javascript
deck.appendix({
  label: "Appendix A — Balance and attrition",
  title: "Lottery winners and losers look alike at baseline, and attrition is balanced",
  exhibit: { type: "table", header: ["", "Tutored", "Control", "p-value"],
             rows: [["Baseline math (SD)", "−0.02", "0.01", "0.61"], ["Free lunch (%)", "71", "70", "0.74"]] },
  cite: "Source: authors' calculations from district enrollment records",
  notes: "Backup for 'is the lottery really random?'",
});
```

## 10. Long talks: dividers and breadcrumb

For more than about 15 presented slides, give the audience signposts. Use one or the
other, not both.

```javascript
deck.sectionDivider({ label: "Part 2", title: "Empirical strategy", notes: "..." });

// or: createDeck({ ..., sections: ["Motivation", "Design", "Results", "Discussion"] })
// then pass  section: "Results"  to each slide to show a breadcrumb above the title.
```

## 11. Anything else

```javascript
const { slide, top, bottom } = deck.blank({ title: "The estimating equation has one free parameter", notes: "..." });
slide.addImage({ path: "equation.png", x: 0.5, y: top, w: 9.0, h: 1.2, altText: "y = a + b·T + e" });
slide.addText("β is the effect of winning the lottery on graduation", {
  objectName: "dk-body", x: 0.5, y: top + 1.5, w: 9.0, h: 0.5, fontFace: "Arial", fontSize: 20, color: "2D2D2D", margin: 0,
});
```

Draw only between `top` and `bottom`. Name text boxes `dk-body`, `dk-cite`, `dk-annot`
or `dk-header` so the linter knows what they are.

---

## PptxGenJS pitfalls the kit works around

If you write raw PptxGenJS, watch for these:

- **Mixed-format bullets.** A bulleted paragraph made of two runs (bold lead + normal
  text) gets two conflicting sets of paragraph properties, and PowerPoint and
  LibreOffice disagree about whether the bullet shows. Use a bold lead with no bullet
  marker, or a bullet with a single run.
- **Fixed-height titles.** A title box sized for one line will overlap the body when the
  title wraps. Measure first, or use `deck.blank()`.
- **Default chart type sizes.** Axis labels, data labels and legends default to about
  12 pt. Set every `…FontSize` option explicitly to 16 or more.
- **Call-outs over charts.** A text box placed "over the tall bar" by eye will sit on
  the wrong bar after any data change. Put the call-out outside the plot area, or draw
  the figure in matplotlib and annotate in data coordinates.
- **`#` in colours.** PptxGenJS wants `"1F4E79"`, not `"#1F4E79"`; the wrong form can
  produce a file PowerPoint asks to repair.

---

## Before delivery

```
□ node build ran with no kit warnings (or each one was dealt with by cutting words)
□ lint_deck.py --mode academic --minutes N [--source paper.json] reports no errors
□ Ghost deck: the titles alone tell the argument
□ Research question on its own slide within the first four
□ Results: one exhibit each, focal series highlighted, call-out in words, source line
□ Every citation on a slide has a full reference; every reference was copied, not recalled
□ Conclusions is the last presented slide, with contact details; no "Thank you"
□ References and appendix sit behind the conclusions
□ Speaker notes on every slide
□ Rendered to images and every slide looked at
□ Runs one to two minutes under the slot when rehearsed aloud
```
