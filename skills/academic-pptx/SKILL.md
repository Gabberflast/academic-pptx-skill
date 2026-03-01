---
name: academic-pptx
description: "Use this skill whenever the user wants to create or improve a presentation for an academic context — conference papers, seminar talks, thesis defenses, grant briefings, lab meetings, invited lectures, or any presentation where the audience will evaluate reasoning and evidence. Triggers include: 'conference talk', 'seminar slides', 'thesis defense', 'research presentation', 'academic deck', 'academic presentation'. Also triggers when the user asks to 'make slides' in combination with academic content (e.g., 'make slides for my paper on X', 'create a presentation for my dissertation defense', 'build a deck for my grant proposal'). This skill governs CONTENT and STRUCTURE decisions. For the technical work of creating or editing the .pptx file itself, also read the pptx SKILL.md."
license: MIT
---

# Academic Presentations Skill

## How This Skill Works

This skill has two layers:

1. **This file** — governs content, argument structure, and design standards for academic presentations. Read it fully before planning any slides.
2. **PPTX skill** — governs the technical implementation (creating, editing, and QA-ing the .pptx file). Read it too.

**Always read both before writing any code or creating any files.**

---

## Quick Reference

| Task | Guide |
|------|-------|
| Content planning, argument structure, slide-by-slide rules | [content_guidelines.md](content_guidelines.md) |
| Per-slide-type patterns (title, methods, results, etc.) | [slide_patterns.md](slide_patterns.md) |
| Technical creation from scratch | PPTX skill → `pptxgenjs.md` |
| Technical editing of an existing file | PPTX skill → `editing.md` |

---

## Step 1: Identify Presentation Type

Before planning a single slide, determine which mode applies.

### Structured Argument (default for academic work)

Use for: conference papers, seminar talks, thesis defenses, dissertation chapters, grant briefings, internal lab presentations, policy briefings, consulting-style research deliverables.

**Priority order: argument structure → data → layout → aesthetics.**

Follow [content_guidelines.md](content_guidelines.md) in full.

### Visual / Narrative

Use for: public engagement talks, science communication to non-specialist audiences, funding pitches to lay panels, event keynotes.

Follow the PPTX skill's design-forward guidelines. Argument structure still matters, but visual storytelling and emotional engagement take priority.

### When in doubt

Default to **Structured Argument**. If the user mentions a paper, a study, a dataset, a thesis, a grant, or a conference, they almost certainly want structured argument mode.

---

## Step 2: Plan the Deck Before Creating Any Slides

Produce a slide-by-slide outline (title, action title, exhibit type) and confirm with the user if the deck is more than 10 slides or if the content is complex. Do not start building until the outline is agreed.

Use the ghost deck test during planning: read only the proposed action titles in sequence. They must tell the complete argument. If they don't, fix the outline before building.

---

## Step 3: Apply Design Standards

Academic presentations use **communication-first design**. These rules override the PPTX skill's design-forward defaults.

### Color

- White background for all content slides.
- One sans-serif font throughout (Arial, Calibri, or Helvetica — confirm with user or match their institution's template if provided).
- Maximum three colors: one primary, one accent, one for emphasis or alerts. Default: dark navy primary (`1F4E79`), mid-blue accent (`2E75B6`), white or off-white background.
- No decorative color gradients, no themed color palettes unless the user explicitly requests them.
- Use color to **direct attention** — highlight the key finding on a chart, mark a callout box — not for decoration.

### Typography

| Element | Size | Weight |
|---------|------|--------|
| Action title | 24–28 pt | Bold |
| Section header | 20–22 pt | Bold |
| Body bullets | 20 pt | Regular |
| Chart labels / annotations | 16–18 pt | Regular |
| Source citations on slides | 12–14 pt | Regular, muted color |

Single font face. Use size and weight for hierarchy — never multiple typefaces.

### Layout

- Left-align all body text. Center only slide titles and axis labels.
- Consistent grid: all text boxes and figures align to the same margins (minimum 0.5" from slide edges).
- For result slides: figure on the left, interpretive bullets on the right. This matches natural left-to-right reading.
- White space is a signal of analytical clarity — do not fill every inch.
- 16:9 widescreen is the default. Confirm with the user if they know the venue's aspect ratio.

### Avoid (Academic-Specific)

- **No decorative icons** — icons in colored circles, stock images, clip art are inappropriate for analytical academic presentations.
- **No accent lines under titles** — use whitespace instead.
- **No color palettes chosen for aesthetic interest** — use institution colors or the minimal defaults above.
- **No full-bleed background images on content slides** — reserve for title/section dividers only if desired.
- **No text-heavy slides** — if the audience is reading, they are not listening. Maximum ~40 words of body text per content slide.

---

## Step 4: Build and QA

Follow the PPTX skill's QA procedure in full, including:
- Content QA via `markitdown`
- Visual QA via slide images (subagents if available)
- Fix-and-verify loop until a full pass reveals no new issues

**Additionally, run the academic-specific checks:**

```
Academic QA checklist:
□ Every content slide has an action title (complete sentence stating the takeaway)
□ Ghost deck test passes (action titles alone tell the full argument)
□ One exhibit per results slide; each exhibit has a "so what" annotation
□ Every borrowed figure or data point has an in-slide citation
□ A References slide exists at the end
□ Conclusions slide is the last non-appendix slide (not "Thank You" or a blank)
□ Contact information and/or QR code/link on the final slide
□ Font sizes are readable from the back of a room (≥ 20 pt body text)
□ No decorative elements that don't carry content
□ Section dividers or breadcrumb bar present for decks > 15 slides
```

---

## Key Principles (Summary)

**Action titles, not topic labels.** Every slide title is a complete sentence stating the takeaway. Reading titles alone should tell the whole argument (ghost deck test).

**One argument, made well.** Don't present your whole paper. Pick the claim that can be made convincingly in the allotted time. Everything else goes in the appendix.

**One insight per slide.** One exhibit per results slide. Highlight the key finding directly on the chart — don't make the audience hunt for it.

**Slides support speech; they don't replace it.** Body text is for orientation, not information transfer. The presenter carries the argument; the slide carries the evidence.

**Cite everything borrowed.** Academic integrity applies to slides. In-text citations on the slide, full references on the References slide.

**End on conclusions.** The conclusions slide stays on screen during Q&A. Never end on "Thank You" or a blank slide.

---

## Dependencies

Same as PPTX skill:
- `pip install "markitdown[pptx]"` — text extraction
- `npm install -g pptxgenjs` — creating from scratch
- LibreOffice (`soffice`) — PDF conversion
- Poppler (`pdftoppm`) — PDF to images
