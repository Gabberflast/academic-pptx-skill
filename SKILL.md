---
name: academic-pitch-pptx
description: "Build or improve argument-first slide decks in two modes. ACADEMIC: conference talks, seminar slides, thesis defenses, job talks, lab meetings, grant briefings, or turning a paper (PDF or LaTeX) into a talk. PITCH: startup fundraising decks for pre-seed, seed or Series A, demo day, accelerator applications, in the style investors such as YC, Sequoia and a16z ask for. Use it when the user says things like 'make slides for my paper', 'thesis defense deck', 'conference talk', 'pitch deck', 'investor deck', 'seed deck', 'demo day slides', or asks to review or fix such a deck. It governs content, structure and checking; it ships a slide-building kit, a deck linter, a paper extractor, and a deck_rules.md file that remembers the user's own colours and house rules. For the mechanics of .pptx files, also read the pptx skill."
license: MIT. See LICENSE.
---

# Academic and Pitch Decks

Both kinds of deck fail the same way: slides that name topics instead of making claims,
too much text in type too small to read, numbers nobody can trace. This skill treats a
deck as an argument. Every slide states one claim in its title and shows the evidence
for it, and a script checks the finished file.

It has three parts:

| Part | What it is |
|------|------------|
| Guidelines | What goes on the slides and in what order, per mode |
| `scripts/deck_kit.js` | Slide builders on top of PptxGenJS. Titles are measured, layout flows from them, fonts stay above the readable floor |
| `scripts/lint_deck.py` | Opens the finished `.pptx` and reports rule violations. `scripts/extract_paper.py` pulls talk material out of a paper |
| `deck_rules.md` | The user's own file: their colours, limits and house rules, layered on this baseline. `scripts/deck_rules.py` reads and updates it |

The pptx skill covers the file format itself (PptxGenJS API, editing existing files,
rendering to images). Read it as well. Where the two disagree on design, this skill wins:
these decks are judged on reasoning, and decoration competes with it.

## Step 1: Pick the mode

| The user has… | Mode | Read |
|---------------|------|------|
| A paper, study, thesis, dataset or grant; an audience that will evaluate reasoning | **academic** | [academic/content_guidelines.md](academic/content_guidelines.md), [academic/slide_patterns.md](academic/slide_patterns.md) |
| A paper (PDF or LaTeX) to turn into a talk | **academic**, starting from the paper | [academic/paper_to_deck.md](academic/paper_to_deck.md) first |
| A company raising money, a demo day slot, an accelerator application | **pitch** | [pitch/pitch_guidelines.md](pitch/pitch_guidelines.md), [pitch/slide_patterns.md](pitch/slide_patterns.md) |
| A public lecture, keynote or outreach talk | neither | Use the pptx skill's design-forward defaults; keep action titles |

A researcher pitching a spin-out to investors is in pitch mode. A founder presenting
results at a conference is in academic mode. The audience decides, not the presenter.

## Step 2: Load the user's rules, then ask the intake questions

Read [customization.md](customization.md) for the detail. In short:

1. **Look for `deck_rules.md`** among the attachments and in the user's working folder.
   If it exists, apply it without being asked and say in one line that you are using
   it. It outranks this skill's defaults; what the user asks for today outranks it.
2. **Ask, in one round, whatever is still open** (four questions at most; skip any the
   request, the attachments or the rules file already answer):
   - **Input material** — what to build from: a paper, an existing deck, data, notes,
     company material, or an interview. Ask them to attach it.
   - **Colour scheme** — the mode's default, a named scheme (`navy`, `crimson`,
     `forest`, `plum`, `slate`, `ink`, `emerald`, `violet`, `ember`, `midnight`), their
     own hex colours and typeface, or "match this deck" (attach a `.pptx`).
   - **The slot** — minutes and audience (academic); stage and read-ahead versus
     presented (pitch).
   - **House rules** — anything they always want, and whether to save these answers.
3. **Save standing preferences** to `deck_rules.md` with `scripts/deck_rules.py`
   (`set` for settings the tools enforce, `add` for rules written as sentences). Save
   only what the user stated as a lasting preference: not one-off edits, not this
   deck's content, not your own choices.

If nobody is there to answer, use the defaults in customization.md, say which you
took, and carry on.

## Step 3: Get the facts before the layout

A deck built on invented content is worse than no deck: the user may not notice a
plausible-looking number until someone in the audience does.

- **Never invent** a statistic, a result, a citation, a customer, a quote, a logo, a
  team credential or a market size. This holds even for a "draft".
- Every number on a slide comes from the user or from a source you have read. In
  academic mode, record where (page or table) in the speaker notes or the outline.
- Every reference comes from the paper's own bibliography or a source you have
  opened. If you cannot find the full reference, drop the citation and say so.
- When a fact is missing, ask for it. If the user is not there to ask, write
  `NEEDS("what is missing")` from the kit. It renders as `[[NEEDS: …]]`, the linter
  fails the deck while any remain, and you list them for the user at the end.
- Projections are labelled as projections. Illustrative figures are labelled illustrative.

For a paper: run `python3 scripts/extract_paper.py paper.pdf --out paper_out`, then work
from `paper_out/outline.md`. For a pitch: collect the facts listed under "Intake" in the
pitch guidelines.

## Step 4: Write the ghost deck and agree it

Before any slide exists, write the titles in order, each a full sentence stating that
slide's takeaway, with the exhibit each will carry. Read them top to bottom. If they do
not make the whole argument on their own, fix the outline; no layout will rescue it.

Show the user this outline and wait for agreement when the deck is more than 10 slides,
when you had to choose which results or which story to feature, or when facts are
missing. For a short deck with clear content, build it and show the outline alongside.

## Step 5: Build with the kit

Copy `scripts/deck_kit.js` next to your build script (or require it by path) and call
the slide builders: `content`, `twoColumn`, `result`, `question`, `conclusions`,
`references`, `appendix` for academic; `pitchTitle`, `statement`, `hero`, `tiles`,
`result`, `team`, `ask` for pitch. The pattern files show each one. Two complete,
runnable decks are in `examples/`.

```bash
NODE_PATH=$(npm root -g) node build_deck.js
```

Pass the user's choices to `createDeck`: `scheme: "emerald"`, `colors: { accent:
"0F766E" }`, `face: "Inter"`, and `rules: "deck_rules.md"` when that file exists. The
kit warns if a colour would be unreadable as text.

The kit prints warnings as it builds (title too long, body over the word limit, text
that will not fit). Treat each as a prompt to cut words. It never shrinks type to make
content fit, and neither should you.

Write speaker notes for every slide: what to say in two to four sentences, and the
transition to the next slide. Slides carry the evidence; notes carry the argument.

For a layout the kit lacks, call `deck.blank({ title })` and draw between the returned
`top` and `bottom` with PptxGenJS directly. Name your text boxes (`objectName:
"dk-body"`, `"dk-cite"`, `"dk-annot"`) so the linter can classify them.

## Step 6: Lint, then look

```bash
python3 scripts/lint_deck.py deck.pptx --mode academic --minutes 15 --source paper_out/paper.json
python3 scripts/lint_deck.py deck.pptx --mode pitch --rules deck_rules.md
```

With a rules file, the linter applies the user's limits, banned words and required
sections, and prints their written rules as a checklist. It cannot check those
sentences; you do, against the rendered slides.

Fix every error. Read every warning and either fix it or be able to say why it does not
apply. The linter exits non-zero while errors remain.

| It catches | Examples |
|------------|----------|
| Titles that are not claims | "Results", "Our Team", titles with no verb |
| Overfull slides | more than 40 body words (academic) or 25 (pitch); text that overflows its box |
| Unreadable type | body under 20 pt, chart labels under 16 pt, grey-on-white below 4.5:1 contrast |
| Broken structure | no research question early, no conclusions slide, a "Thank you" slide, slides over the time budget, pitch sections missing |
| Untraceable content | a citation with no reference, a number that is not in the paper, an unfilled `[[NEEDS]]` |
| Pitch habits | traction with no number, growth with no time window, "no competitors", buzzwords, valuation on the ask slide |
| The user's own rules | a banned word, a missing required section, the wrong typeface, more slides than their limit |

The linter checks form. It cannot tell whether the argument is sound or whether a slide
looks right, so after it passes:

1. Read the ghost deck it prints. Does the argument hold?
2. Render the deck to images (pptx skill: `soffice` then `pdftoppm`) and look at every
   slide for overlap, clipped text and awkward gaps. Fix, rebuild, lint again.

## Step 7: Hand over

Send the `.pptx`. In one or two lines tell the user: the claim the deck makes, any
`NEEDS` items or warnings left open, and anything you chose on their behalf (which
results made the main deck, what went to the appendix).

If you created or changed `deck_rules.md`, say what you saved and send the file too,
unless it already lives in a folder the user can see. Attaching it next time, or
keeping it in their project folder, is what carries the rules forward.

## Design standards

Communication first, in both modes. Colour directs attention to the finding; it is not
decoration.

| | Academic | Pitch |
|---|----------|-------|
| Title | Full-sentence claim, 22–26 pt bold, left-aligned, two lines at most | Full-sentence claim, 28–32 pt bold, left-aligned, 14 words at most |
| Section label | Only for Conclusions and Appendix | On every slide, above the title (PROBLEM, TRACTION, …) so a skimming investor can find the slide they want |
| Body | 20 pt minimum, about 40 words | 24 pt, about 25 words |
| Chart labels | 16 pt minimum | 16 pt minimum |
| Source line | On every slide with borrowed content or an exhibit, 12–14 pt | On every slide with a number that is not obviously the company's own |
| Colour | Navy, one accent, grey for non-focal data | Near-black, the company's one brand colour, grey for non-focal data |
| Background | White; dark only for title, dividers, conclusions | White; dark only for the title slide |
| Typeface | One sans-serif | One sans-serif |
| Slide numbers | Always | Always |
| Last slide shown | Conclusions, left up during questions | The ask, left up during questions |

Avoid in both: decorative icons and stock photos, rules under titles, gradients,
centred body text, "Thank you" slides, screenshots with unreadable text, and anything
on the slide the speaker will not talk about.

The table is the baseline. A user's colour scheme, typeface and limits from intake or
`deck_rules.md` replace the matching rows; the content rules do not change, and the
checks against invented content cannot be switched off.

## Other output formats

The kit and the linter work on `.pptx`. If the deck is being built somewhere else (a
slides artifact, Google Slides, Keynote, Beamer), the guidelines still apply in full:
ghost deck first, action titles, one exhibit per slide, word limits, traceable numbers.
Apply the checklist at the end of each pattern file by hand.

## Files

| File | Read it when |
|------|--------------|
| [customization.md](customization.md) | Starting any deck: finding `deck_rules.md`, the intake questions, colour schemes, when and how to save a rule |
| [academic/content_guidelines.md](academic/content_guidelines.md) | Planning any academic deck: argument, titles, exhibits, citations, timing |
| [academic/slide_patterns.md](academic/slide_patterns.md) | Building academic slides with the kit |
| [academic/paper_to_deck.md](academic/paper_to_deck.md) | The starting point is a paper |
| [pitch/pitch_guidelines.md](pitch/pitch_guidelines.md) | Planning any pitch deck: sections, order, what investors look for, intake |
| [pitch/slide_patterns.md](pitch/slide_patterns.md) | Building pitch slides with the kit |
| `examples/build_academic_example.js`, `examples/build_pitch_example.js` | You want a complete working build script to adapt (content is invented) |

## Dependencies

- Node with `pptxgenjs` (`npm install -g pptxgenjs`) for the kit
- Python with `python-pptx` for the linter
- `pdftotext` / `pdfimages` / `pdftoppm` (poppler) or `pypdf` for the paper extractor
- LibreOffice (`soffice`) to render slides for the visual check
