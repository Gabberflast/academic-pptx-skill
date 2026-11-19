# Academic Presentation Content Guidelines

## 1. Argument Structure

### Lead with the research question
State the central question or claim explicitly — in slides 2 or 3 at the latest. The audience needs it to evaluate everything that follows. Do not bury it.

### Use a proven narrative spine
Choose one and apply it consistently:

**Option A — Situation / Complication / Resolution (SCR)**
- Situation: what was known or established
- Complication: what was missing, broken, contested, or unexplained
- Resolution: what your work contributes

**Option B — Funnel + Answer**
- Broad context → specific gap → your approach → key findings → implications

**Option C — Answer First (for senior/time-pressured audiences)**
- Lead with the conclusion, then support it
- Useful for grant panels, advisory boards, and short talks where the audience may not stay for the full argument

### One argument per presentation
Researchers frequently try to present the whole paper. Resist this. Choose the claim that can be made convincingly in the available time. Everything else belongs in the appendix.

### Each slide has one job
Every slide should have a single, clearly defined role in the argument. If a slide is doing two things, split it.

### Flow test
After outlining, read slide titles in order. Each should make the next one feel like a natural consequence. If a slide feels disconnected or could appear anywhere in the sequence without loss, it is either misplaced or dispensable.

---

## 2. Action Titles

The most important formatting rule. Every content slide title must be a complete sentence stating the takeaway — the "so what" — not a topic label.

| Instead of (topic label) | Use (action title) |
|--------------------------|-------------------|
| Results | Treatment effect is significant across all three cohorts |
| Literature Review | Prior work leaves the causal mechanism unexplained |
| Data | Dataset covers 40 years of county-level panel data |
| Methodology | Regression discontinuity exploits a sharp funding threshold |
| Discussion | Effect persists after controlling for selection and attrition |

**Ghost deck test:** Read only the action titles in sequence. They should tell the complete argument. If they don't, the deck's logic needs repair — fix the titles and/or restructure before building.

**Title length:** One to two lines. If more is needed, the point is not sharp enough yet.

**Title font:** 22–26 pt, bold, left-aligned. A sentence-length title reads better from a fixed left edge than centred. Action titles must be immediately readable, including from the back of the room.

**Appendix slides use action titles too.** A backup slide titled "Robustness" answers nothing; "The effect is stable across bandwidths" answers the question you were asked.

---

## 3. Exhibit Discipline

### One exhibit per slide
One chart, table, diagram, equation block, or map per slide. If you need two charts to make a point, consider whether they are really one comparison (which can be combined) or two separate points (which need two slides).

### Every exhibit must earn its place
The exhibit must directly support the action title. Test: cover the exhibit and read the title — does the title still make sense without it? If yes, the exhibit isn't necessary. Cover the title and look at the exhibit — is the takeaway obvious? If not, you need a stronger annotation or a clearer action title.

### Annotate the key finding on the chart
Do not make the audience search. Mark the key data point, bar, line, or cell with:
- A call-out arrow or label
- A highlighted/shaded region
- A text annotation box ("↑ 23% above baseline")
- A different colour for the focal series

This is especially important for large rooms where the screen may be far away.

The most robust annotation is colour: draw the focal bar or line in the accent colour and everything else in grey, then add one call-out in words. In `deck_kit.js` that is `highlight:` plus `annotation:` on the exhibit.

### Self-sufficient slide test
Ask: could someone understand the key point from this slide without hearing the narration? If no, add an annotation. The slide will also be read as a handout or shared as a PDF; it should communicate without a presenter attached.

### Figure placement
Place figures on the **left side** of the slide. Interpretive bullets or discussion text go on the **right**. This matches natural left-to-right reading order: evidence first, interpretation second.

### Prefer graphs over tables for results
Tables require more cognitive load to parse quickly under time pressure. Use a graph when showing a trend, comparison, or distribution. Reserve tables for precise numerical comparisons where the exact values matter.

### Rebuild figures from your paper
Do not copy figures directly from a PDF. Paper figures are typically too small, use print-resolution fonts, and have captions that will not render well on screen. Rebuild them at presentation resolution with larger fonts (≥ 16 pt for axis labels).

### Equations, tables and diagrams
- **Equations:** one per slide, rendered large (as an image from LaTeX), with each symbol the audience needs defined in words beside it. Derivations go in the appendix.
- **Regression tables:** never paste the paper's table. Show the two or three coefficients the argument needs, or chart them with confidence intervals. Keep the full table as an appendix slide.
- **Diagrams** (design timelines, causal graphs, pipelines): count as the slide's one exhibit. Label every box in at least 16 pt.

### Don't include exhibits you won't discuss
If you include it, discuss it. If you won't have time to discuss it, move it to the appendix.

---

## 4. Text Discipline

### Maximum body text: ~40 words per slide
If you find yourself writing more, either (a) the slide is doing too much and should be split, or (b) the material belongs in an appendix or handout.

### Bullets are orientation cues, not information transfer
Each bullet should contain one idea. Three to five bullets per slide is typical. More than five is a warning sign.

### Telegraphic language is acceptable
Omit articles and filler phrases where meaning is preserved.
- Instead of: "Our study found that the intervention reduced costs significantly."
- Use: "Intervention reduced costs by 23% (p < 0.01)"

### Body font: 20 pt minimum
This is a floor, not a target. If text must be smaller than 20 pt to fit on the slide, remove content until it fits at 20 pt.

### Use bold and italics sparingly
Bold for key terms on first introduction, for inline labels ("Note:", "Limitation:"), and for the focal finding. Italics for statistical notation, species names, book titles. Not for decoration.

---

## 5. Citations and Attribution

### Cite on the slide
Every claim, figure, or dataset that is not your own original work must be cited on the slide where it appears. Place the citation at the bottom of the slide in a smaller muted font (12–14 pt).

Use your field's standard format:
- Sciences / social sciences: (Author, Year) parenthetical
- Humanities: footnote-style or superscript number
- Be consistent throughout the deck

### Never invent a citation
Every reference on a slide must come from the paper's own bibliography or from a source you have opened and read. Copy it exactly; do not reconstruct author lists, years, journals or page numbers from memory. If you cannot find the full reference, remove the citation and tell the author it is missing. A plausible-looking reference that does not exist is the single most damaging error a deck can contain, and the audience most likely to spot it is the one in the room.

Use the same care for numbers: each one on a slide should be traceable to a page, table or figure in the source. `lint_deck.py --source` checks this mechanically.

### Oral attribution
Introduce sources verbally before the citation appears: "Smith and colleagues found in 2022 that…" — don't silently flash a parenthetical.

### Figures from published sources
- Attribution caption directly beneath the figure (e.g., "Source: Jones et al., 2021, Fig. 3")
- Full reference on the References slide
- Reproducing a figure from someone else's published paper may need the publisher's permission. Rules differ by publisher, licence and country, so check the journal's reuse policy rather than assuming. Rebuilding the chart from the underlying data, with attribution, avoids the question.

### References slide
A References slide lists the complete citation for every source cited in the deck, formatted consistently with your field's conventions. It sits **after** the conclusions slide and before the appendix: the order is Conclusions → References → Appendix. You do not present it; you stop on the conclusions slide and the references are there if someone asks. Split a long list across several slides rather than shrinking the type below 12 pt.

---

## 6. Deck Architecture

Required slides for a complete academic presentation, in order:

### Title slide
- Full presentation title (framed as a statement or question — not just a topic)
- Author name(s) and affiliations
- Conference / venue / event name
- Date

### Motivation / Context (1–2 slides)
- Why does this problem matter?
- Connect to a real gap, unresolved question, or consequential puzzle in the literature
- This is the "Situation" and "Complication" in the SCR framework

### Research Question or Hypothesis (1 slide)
- State it explicitly and precisely
- This slide must exist. Do not embed the research question in a motivation slide; give it its own slide so the audience can orient

### Methods (1–2 slides)
- Cover only what the audience needs to evaluate your findings
- Procedural detail that doesn't affect interpretability belongs in the appendix
- For quantitative work: identification strategy, sample, key variables
- For qualitative work: data sources, analytical approach, evidence standards

### Results (as many slides as needed, one finding per slide)
- One exhibit per slide
- Action title states the finding
- Key result annotated directly on the chart/table

### Discussion / Implications (1–2 slides)
- Interpret the findings
- Connect back to the research question from the opening
- Address the main limitation(s) directly — pre-empt the audience's objection

### Conclusions (1 slide)
- 2–4 bullet points restating the key takeaways
- **This slide stays on screen during Q&A. It is the last slide the audience sees.**
- Do NOT follow it with "Thank You" or a blank slide

### Contact / Next Steps (on the conclusions slide)
- Email address or affiliation URL
- QR code or shortened URL linking to slides, preprint, or working paper
- "Work in progress — feedback welcome" if appropriate

### References (after the conclusions; not presented)
- Complete citations for all sources cited in the deck

### Appendix (clearly labeled)
- Pre-built Q&A slides anticipating likely audience questions
- Methodological robustness checks and sensitivity analyses
- Additional data, figures, or tables that didn't fit the main narrative
- Detailed derivations or proofs
- Label each appendix slide clearly (e.g., "Appendix A: Robustness Checks")

---

## 7. Timing and Slot Management

### Slide budget
Maximum one slide per minute. Typical budgets:
- 10-minute talk: 8–10 content slides (title + references excluded)
- 15-minute talk: 12–14 content slides
- 20-minute talk: 15–18 content slides
- 45-minute seminar: 30–40 slides (with more time per slide for discussion)

### Practice rule
Rehearse out loud and to time. Target finishing **1–2 minutes under** the allotted time. Nerves and audience interactions reliably add time on the day. Exceeding the time limit at an academic conference is a significant professional misstep — sessions run to a strict schedule.

### Know what to cut
Identify in advance which slides to skip if time is running short. Mark them with a small indicator in the corner. Prioritise the research question, key result, and conclusions; methods and context are typically the first to compress.

### Budgets by talk type
| Talk | Length | Presented slides | What changes |
|------|--------|------------------|--------------|
| Lightning talk | 3–5 min | 3–5 | One result. No methods slide; one line of method on the result slide |
| Conference talk | 12–20 min | 10–18 | The default structure in section 6 |
| Lab meeting | 20–40 min | 10–20 | Lead with what you need from the room (feedback on X); unfinished results are fine if labelled |
| Seminar | 45–75 min | 30–45 | Section dividers or a breadcrumb; expect interruptions; more robustness in the main deck |
| Job talk | 45–60 min | 30–40 | Add a slide on your wider research agenda before the conclusions; assume a general audience in your field, not specialists in your topic |
| Thesis defense | 20–45 min | 20–35 | State the thesis's contributions as a numbered list early and return to the same list at the end; one section per chapter or paper |
| Grant briefing | 10–20 min | 8–15 | Answer first: what you will do, what it will show, why you, what it costs |

Check the budget mechanically with `lint_deck.py --minutes N`.

### Speaker notes
Write notes for every slide: the two to four sentences you will say, and the line that leads to the next slide. Notes are where the argument lives; the slide only has to carry the evidence. They are also what makes a 40-word slide possible.

### Slide numbers
Number every slide after the title. Questions arrive as "can you go back to slide 12?", and an unnumbered deck turns that into thirty seconds of scrolling.

### Q&A preparation
- Anticipate the 3–5 most likely questions
- Pre-build appendix slides for each
- Common questions: "Why not use X method?", "How does this compare to Y?", "What about the endogeneity concern?", "Is the sample representative?"

### End on the conclusions slide
When you say "I'll stop there," the conclusions slide should already be on screen. Invite questions: "Are there questions or feedback?" (not just "Any questions?" — the broader framing invites more substantive engagement).

---

## 8. International and Accessibility Considerations

### For international audiences
- Avoid idioms, colloquialisms, and culturally specific humour
- Define acronyms and abbreviations on first use, even obvious ones
- Speak more slowly than feels natural
- Use plain, direct sentence structures

### Accessibility basics
- Minimum 20 pt body text; 24 pt+ titles
- High contrast between text and background: at least 4.5:1 for anything under 24 pt. The common "muted grey" `#777777` on white is 4.48:1 and fails; use `#595959` or darker for citations and captions
- Do not rely on colour alone to convey meaning (use labels, patterns, or shapes as well)
- Provide alt text on figures if the slides will be circulated as a PDF

---

## 9. Common Mistakes

| Mistake | Fix |
|---------|-----|
| Topic labels as titles | Write action titles (complete sentence, states the takeaway) |
| Presenting the whole paper | Choose one argument; move the rest to the appendix |
| Reading the slides aloud | Slides carry evidence; the presenter carries the argument |
| Evidence without a "so what" | Annotate the key finding directly on the chart |
| Uncited borrowed figures | Cite on the slide; full reference on References slide |
| Body text < 20 pt | Remove content until it fits at 20 pt |
| Inconsistent formatting | One font, one citation style, consistent grid alignment |
| Slides you won't discuss | Move to appendix if you won't have time |
| Going over time | Rehearse under time; know what to cut |
| Ending on "Thank You" | End on conclusions slide; it stays up during Q&A |
| Burying the research question | State it explicitly, on its own slide, in slides 2–3 |
| No references slide | Always include one |
| A reference reconstructed from memory | Copy it from the paper's bibliography, or leave the citation out |
| Paper figure pasted in at paper size | Rebuild at presentation size with 16 pt+ labels |
| Unnumbered slides | Number every slide after the title |
| Light grey source lines | Darken to at least 4.5:1 contrast |
| References slide shown as the last slide | Stop on the conclusions; references and appendix sit behind it |
