# Changelog

## Fork of gabberflast/academic-pptx-skill

### Added

- **Pitch mode.** `pitch/pitch_guidelines.md` (sections, order, stage differences,
  founder intake list, integrity rules) and `pitch/slide_patterns.md`, based on
  published guidance from Y Combinator, Sequoia and a16z.
- **`scripts/deck_kit.js`.** Slide builders for both modes on top of PptxGenJS.
  Measures titles and flows the layout from them, numbers slides, names every text box
  for the linter, and warns at build time about long titles, overfull bodies and
  missing notes. Never shrinks type to fit.
- **`scripts/lint_deck.py`.** Checks a finished `.pptx`: action titles, word limits,
  font floors (including inside charts and tables), contrast, overflow, exhibits per
  slide, source lines, placeholders, slide numbers, speaker notes; academic structure,
  citation-to-reference matching and time budget; pitch sections, traction, market,
  ask and wording. Text or JSON output, non-zero exit on errors.
- **`scripts/extract_paper.py`** and **`academic/paper_to_deck.md`.** PDF or LaTeX →
  title, abstract, sections, captions, references, number-bearing sentences, figure
  images and a worksheet; a ten-step workflow from paper to talk.
- **Number tracing.** `lint_deck.py --source paper.json` reports every number on a
  slide that is not in the paper.
- **`NEEDS()` placeholders** for missing facts, which the linter refuses to pass.
- **Examples and tests.** Two complete build scripts and `tests/run_tests.py`.
- Budgets by talk type (lightning talk, lab meeting, seminar, job talk, defense, grant
  briefing); guidance on equations, regression tables, speaker notes and slide numbers.

- **`deck_rules.md` and `scripts/deck_rules.py`.** A file the user keeps that layers
  their own settings (colours, typeface, footer, word and slide limits, banned words,
  required sections, linter rules to switch off) and written house rules on top of the
  baseline. The kit and the linter read it; the checks against invented content cannot
  be switched off.
- **Intake step** (`customization.md`): what to build from, colour scheme, slot and
  house rules, asked once up front and skipped where the rules file already answers.
- **Colour schemes.** Ten named schemes including one dark background; colours and
  fonts can be read from an existing `.pptx` or `.potx`; the kit warns when a colour
  would be unreadable as text.

### Fixed

- `SKILL.md` front matter said the licence was proprietary; the repository is MIT.
- `SKILL.md` said "no accent lines under titles" while every pattern drew one. The
  rule stands; the lines are gone.
- `SKILL.md` said to centre slide titles while every pattern left-aligned them.
  Titles are left-aligned.
- The guidelines put the References slide both "last before the appendix" and after a
  Conclusions slide that had to be "the last non-appendix slide". The order is now
  stated once: Conclusions (last presented) → References → Appendix.
- Pattern snippets broke the stated minimums: results bullets at 19 pt, the research
  question at 19 pt, chart call-outs at 14 pt, axis titles at 12 pt.
- The muted grey `777777` used for citations is 4.48:1 on white, under the 4.5:1 the
  guidelines ask for. Now `595959` (7.0:1).
- The bold-lead bullet pattern produced paragraphs with two conflicting property
  blocks, so bullets showed in one renderer and not another. Lists with bold leads are
  now set without markers.
- Title boxes had fixed heights, so two-line titles collided with the divider or body.
- The results call-out was positioned by hand over the chart and covered data. Call-outs
  now sit in their own strip above the exhibit unless placed explicitly.
- Example references contained errors (a real paper with the wrong year and journal),
  which modelled the mistake the skill warns against. Examples now use plainly invented
  studies, labelled as such.
- A typo in the title-slide example ("²aboratory") and a duplicated `breakLine` key.
- The note that reproducing published figures is "typically covered by fair use" is
  replaced with advice to check the publisher's reuse policy.

### Changed

- `content_guidelines.md` and `slide_patterns.md` moved into `academic/`.
- The skill is now named `academic-pitch-pptx`.
