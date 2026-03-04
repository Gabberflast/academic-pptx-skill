---
name: esl-classroom-pptx
description: "Use this skill whenever the user wants to create or improve a presentation for an ESL (English as a Second Language) classroom context — grammar lessons, vocabulary presentations, reading/listening activities, speaking/discussion tasks, culture topics, review sessions, or any lesson where secondary school students will learn and practise English. Triggers include: 'ESL lesson', 'grammar presentation', 'vocabulary slides', 'classroom activity', 'English lesson', 'language class', 'teaching slides', 'EFL lesson'. Also triggers when the user asks to 'make slides for my lesson on X', 'create a presentation for teaching Y', 'build slides for my English class'. This skill governs CONTENT and STRUCTURE decisions. For the technical work of creating or editing the .pptx file itself, also read the pptx SKILL.md."
license: Proprietary. LICENSE.txt has complete terms
---

# ESL Classroom Presentations Skill

## How This Skill Works

This skill has two layers:

1. **This file** — governs content, lesson structure, and design standards for ESL classroom presentations. Read it fully before planning any slides.
2. **PPTX skill** — governs the technical implementation (creating, editing, and QA-ing the .pptx file). Read it too.

**Always read both before writing any code or creating any files.**

---

## Quick Reference

| Task | Guide |
|------|-------|
| Lesson structure, slide sequence, text/exercise rules, text enhancement conventions | [content_guidelines.md](content_guidelines.md) |
| Per-slide-type patterns (title, vocabulary, grammar, exercises, etc.) | [slide_patterns.md](slide_patterns.md) |
| Technical creation from scratch | PPTX skill → `pptxgenjs.md` |
| Technical editing of an existing file | PPTX skill → `editing.md` |

---

## Step 1: Identify Lesson Type

Before planning a single slide, determine which type applies.

### Grammar Lesson (default when unclear)

Use for: teaching verb tenses, sentence structure, parts of speech, word order, conditionals, reported speech, articles, prepositions, etc.

**Priority order: clear explanation → guided practice → free production → layout → aesthetics.**

### Vocabulary Lesson

Use for: introducing and practising new words/phrases around a theme (weather, food, travel, jobs, emotions, etc.).

### Skills Lesson

Use for: reading comprehension, listening activities, writing workshops, speaking/pronunciation practice.

### Culture / Topic Lesson

Use for: content-based lessons (festivals, countries, current events), visual-heavy, discussion-driven.

### Review / Test Prep

Use for: consolidation, mixed exercises, error correction, exam-format practice.

### Mixed

Use for: lessons combining multiple types. Common in real classrooms.

Follow [content_guidelines.md](content_guidelines.md) in full for all lesson types.

---

## Step 2: Plan the Deck Before Creating Any Slides

Produce a slide-by-slide outline (title, purpose, content type, exercise format if applicable) and confirm with the user if the deck is more than 10 slides or if the content is complex. Do not start building until the outline is agreed.

Use the **lesson flow test** during planning: read only the proposed slide titles in sequence. They must tell the complete lesson progression — from warm-up through new language input, practice, production, and review. If they don't, fix the outline before building.

---

## Step 3: Apply Design Standards

ESL classroom presentations use **clarity-first design** optimised for a large TV screen viewed by up to 35 students, including those at the back of the room.

### OVERRIDING RULE: Content Must Fit

**Font size guidelines throughout this skill are TARGETS, not hard limits.** The highest-priority rule is:

> All content the teacher requests must appear on the slide without overflowing, being cut off, or extending beyond slide boundaries.

If content won't fit at the target font size:
1. **First**: reduce font size (use judgment — going from 24 pt to 20 pt is acceptable)
2. **If still too small to read**: split the content across multiple slides
3. **Never**: let text overflow, get truncated, or extend beyond the slide edge

The teacher's content always takes priority over font size targets.

### Typography

Target sizes, optimised for a 75" TV viewed from the back of a classroom:

| Element | Target Size | Weight |
|---------|------------|--------|
| Slide title | 32 pt | Bold |
| Section header | 26 pt | Bold |
| Body / instructions | 24 pt | Regular |
| Key vocabulary words | 32–36 pt | Bold |
| Exercise content | 24–28 pt | Regular |
| Labels / attribution | 14–16 pt | Regular, muted color |

Single font face (Arial, Calibri, or Helvetica — confirm with user). Use size and weight for hierarchy — never multiple typefaces.

### Color

- White background for all content slides.
- Maximum three base colours: one primary, one accent, one for emphasis.
- **Grammar colour coding** is an additional layer on top of the base palette — see [content_guidelines.md §5](content_guidelines.md) for the full scheme.
- Use colour to **support learning** — highlight target structures, distinguish parts of speech — not for decoration.
- No decorative colour gradients or themed palettes unless explicitly requested.

### Layout

- Left-align all body text. Centre only slide titles if desired.
- Consistent grid: all text boxes align to the same margins (minimum 0.5" from slide edges).
- For vocabulary slides: image on the left, word/definition/example on the right.
- White space helps students focus — do not fill every inch.
- 16:9 widescreen is the default.

### What to Avoid

- **No decorative icons or clip art** — images must support vocabulary/concepts, not decorate.
- **No teacher narration on slides** — only include text students need to read or interact with (instructions, examples, exercises, key language).
- **No accent lines under titles** — use whitespace instead.
- **No full-bleed background images on content slides** — reserve for title/section dividers only if desired.

---

## Step 4: Build and QA

Follow the PPTX skill's QA procedure in full, including:
- Content QA via `markitdown`
- Visual QA via slide images (subagents if available)
- Fix-and-verify loop until a full pass reveals no new issues

**Additionally, run the ESL classroom checks:**

```
ESL Classroom QA Checklist:
□ Every slide has a clear purpose (learning target, instruction, content, or exercise)
□ Lesson flow test: slide titles tell the progression from warm-up to wrap-up
□ One exercise or visual focus per slide
□ Grammar colour coding is consistent throughout the deck (same colour = same part of speech)
□ Text enhancement conventions (bold, italic, underline, ALL CAPS) applied consistently per §5 rules
□ Written instructions are present on every exercise slide
□ Font sizes are readable on TV from back row (target ≥ 24 pt body)
□ No content overflows any slide — the overriding rule is satisfied
□ Images support vocabulary/concepts (not decorative)
□ Wrap-up slide is the last content slide (key takeaways + homework)
□ Section dividers or breadcrumb bar present for decks > 15 slides
□ Language level of instructions matches the students' proficiency
```

---

## Key Principles (Summary)

**Clear purpose per slide.** Every slide has one job: teach a point, present an exercise, model language, or review. If a slide is doing two things, split it.

**Slides carry the lesson.** ESL classroom slides are what students read and interact with. Text on the slide IS the learning content — instructions, examples, exercises, and key language. This is different from academic presentations where slides merely support the speaker.

**Content never overflows.** Font size targets exist for readability, but the overriding rule is that all requested content fits on the slide. Shrink or split as needed.

**Text enhancements are teaching tools.** Bold, italic, underline, ALL CAPS, and grammar colour coding all have specific pedagogical meanings (see content_guidelines.md §5). Apply them consistently and deliberately — never for decoration.

**One focus per slide.** One exercise, one grammar point, one vocabulary set, one reading passage. Keep it clean.

**Language must be level-appropriate.** Instructions and content match the students' English proficiency. Simpler structures and vocabulary for lower levels; more complex for higher levels.

---

## Dependencies

Same as PPTX skill:
- `pip install "markitdown[pptx]"` — text extraction
- `npm install -g pptxgenjs` — creating from scratch
- LibreOffice (`soffice`) — PDF conversion
- Poppler (`pdftoppm`) — PDF to images
