# From Paper to Talk

A paper and a talk are different arguments. The paper is complete and defends every
flank; the talk makes one claim convincingly in the time available and sends people to
the paper for the rest. The failure to avoid is the paper read aloud: its section
headings as slide titles, its figures at paper size, its literature review in bullets.

Work through these steps in order. Do not open the slide builder until step 5.

---

## 1. Extract

```bash
python3 scripts/extract_paper.py paper.pdf --out paper_out      # or main.tex, or a LaTeX folder
```

This writes:

| File | Contents |
|------|----------|
| `paper_out/paper.json` | Title, abstract, sections, figure and table captions, the reference list, sentences that carry numbers, full text |
| `paper_out/outline.md` | A worksheet for steps 2–6 |
| `paper_out/figures/` | Images embedded in the PDF |
| `paper_out/pages/` | A render of each page that has a figure or table, for vector figures |

The extraction is pattern matching and will be wrong in places: a table row read as a
heading, two references merged, a caption cut short. Read the PDF itself as well (the
pdf-reading skill, or the Read tool with `pages`), and correct `paper.json` where it
matters. If the script reports very little text, the PDF is scanned; OCR it first.

LaTeX sources are better input than the PDF when the user has them: references come
straight from the `.bib` file and figures are the original files.

## 2. Ask about the slot

You need three things from the user, and none of them is in the paper:

- **Audience** — specialists in this topic, the wider field, or mixed?
- **Minutes** — for the talk itself, excluding questions.
- **Kind of talk** — conference session, seminar, job talk, defense, lab meeting.

If the user is not there to ask, assume a 15-minute conference talk to people in the
field, say so at the top of the outline, and carry on.

The slide budget is at most one presented slide per minute. The budgets-by-talk-type
table in `content_guidelines.md` gives the shape for each kind.

## 3. Find the one claim

Write a single sentence that the audience should be able to repeat tomorrow. It names
what was found, not what was studied.

| Topic (not a claim) | Claim |
|---------------------|-------|
| The long-run effects of tutoring | One year of tutoring in grade 6 raises graduation rates six years later |
| A new method for sparse retrieval | Learned sparse retrieval matches dense retrieval at a tenth of the index size |

The abstract usually contains it, buried mid-paragraph. A paper with three contributions
still gets one claim for a 15-minute talk; the other two become one slide near the end
("the paper also shows…") or go to the appendix.

Then choose the evidence: the two to four results without which the claim would not
stand. Everything else in the paper is appendix material, however much work it was.

## 4. Write the ghost deck

Fill in the table in `outline.md`: one row per slide, the action title as a full
sentence, the exhibit, and where in the paper the content comes from (page, table or
figure number). A typical 15-minute shape:

| # | Role | Comes from |
|---|------|------------|
| 1 | Title: the claim | — |
| 2 | What is known and what is missing | Introduction, first two paragraphs |
| 3 | The research question, alone | Introduction |
| 4 | Design: only what is needed to believe the result | Data / methods |
| 5–8 | One result per slide | The chosen results |
| 9 | What it means; the main limitation | Discussion |
| 10 | Conclusions | — |
| — | References, then appendix | Bibliography; robustness sections |

Read the titles top to bottom. Each should make the next feel like the natural
consequence. Show this outline to the user before building, since choosing which
results lead is a judgment about their work that they should get to overrule.

## 5. Decide each figure

For every figure and table you plan to use, pick one, in order of preference:

1. **Rebuild from data.** If the user has the data or the plotting script, redraw at
   presentation size: 16 pt labels, focal series in the accent colour, the rest grey,
   the key point annotated. Ask for the data; most authors have it to hand.
2. **Rebuild from the numbers in the paper.** A table of coefficients or a bar chart
   whose values are printed can be redrawn exactly from `paper.json`. Do not read
   values off a plot by eye; if the numbers are not printed, use option 3.
3. **Crop from the page render.** Last resort, for figures that cannot be rebuilt
   (micrographs, maps, complex multi-panel plots). Crop one panel, not the whole
   figure, enlarge it to fill the exhibit area, and add the call-out on the slide. The
   source line says where it came from: "Source: Rivera & Chen (2026), Fig. 2b".

A regression table never goes on a slide as-is. Show the coefficients that matter, as a
small table or a chart with intervals, and keep the full table as an appendix slide.

## 6. Carry the references, exactly

Tick the references in `outline.md` that a slide will cite. Copy each one character for
character from the paper's bibliography into `deck.references({ refs })`. Do not tidy
author lists or add missing page numbers from memory. If an entry in `paper.json` looks
truncated or merged, go back to the PDF for that entry.

A source that is not in the paper's bibliography (say, a newer paper the user wants to
mention) goes in only if you have opened it and can copy its citation.

## 7. Build, with notes

Build with `deck_kit.js` (see `slide_patterns.md`). For each slide write speaker notes:

- what to say, in two to four sentences, in spoken English rather than the paper's prose;
- where the numbers on the slide come from ("Table 2, column 3; p. 14");
- the line that leads to the next slide.

Derived numbers (a ratio of two estimates, a rounding) get their arithmetic in the
notes: "3.5× = 14 / 4, Table 3".

## 8. Build the Q&A appendix

Predict three to five questions and prepare one backup slide for each. Good places to
look in the paper: the robustness section, the limitations paragraph, footnotes that
begin "one concern is", referee-driven appendices. Common ones:

- Why this method and not the obvious alternative?
- Is the sample representative? What about attrition or selection?
- Does the result survive a different specification, bandwidth, or control set?
- How does this compare with a well-known earlier estimate?
- What is the mechanism?

## 9. Check against the paper

```bash
python3 scripts/lint_deck.py talk.pptx --mode academic --minutes 15 --source paper_out/paper.json
```

`--source` reports every number on a slide that does not appear in the paper's text.
Each report is one of three things:

- **A transcription error** — fix the slide.
- **A derived number** — put the arithmetic in that slide's speaker notes (the check
  then accepts it) and make sure the paper supports it.
- **A formatting difference** the check could not see through (the paper says
  "one-third", the slide says 33%) — confirm by hand.

The check does not look inside native charts, so compare chart values with the paper
yourself.

Then render the deck and look at every slide.

## 10. Tell the author what you decided

When you hand over the deck, say in a few lines: the claim you built the talk around,
which results lead and which went to the appendix, any figure you could not rebuild,
and any reference or number you could not confirm. These are the author's calls; make
them easy to overrule.
