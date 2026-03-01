# Academic Presentations Skill for Claude

A Claude Skill for creating high-quality academic presentations: conference talks, seminar slides, thesis defenses, and grant briefings.

## What It Does

This skill overrides Claude's default design-forward presentation style and replaces it with communication-first standards appropriate for academic and analytical contexts. When active, Claude will:

- Write every slide title as a **complete sentence stating the takeaway** ("action title"), not a topic label
- Structure the deck as a **logical argument** (situation → complication → resolution), not a collection of independent slides
- Apply the **ghost deck test**: the action titles alone, read in sequence, should tell the full story
- Place **one exhibit per results slide** and annotate the key finding directly on the chart
- Apply **citation standards**: in-text citations on every borrowed figure, a References slide at the end
- End on a **Conclusions slide** that stays on screen during Q&A — never on "Thank You" or a blank
- Apply minimal, communication-first design: white backgrounds, single sans-serif font, three colours maximum, no decorative icons

## Installation

1. Download this repository as a zip file (click **Code → Download ZIP** above)
2. In [claude.ai](https://claude.ai), go to **Customize → Skills**
3. Upload the zip file
4. Confirm the skill appears in your skills list and is toggled on

> **Requirement:** Code execution and file creation must be enabled in **Settings → Capabilities**.

## Usage

Just ask naturally:

- *"Make slides for my conference paper on X"*
- *"Build a deck for my thesis defense"*
- *"Create a seminar presentation about my research on Y"*

Claude will detect the academic context, load this skill automatically, and apply all guidelines before generating any slides. You do not need to give any special instructions.

This skill works alongside Anthropic's built-in PPTX skill, which handles the technical file generation. This skill handles content, argument structure, and design standards.

## File Structure

```
academic-pptx-skill/
├── SKILL.md                  # Entry point: routing logic and design standards
├── content_guidelines.md     # Argument structure, action titles, citations, deck architecture
├── slide_patterns.md         # Per-slide-type implementation patterns with PptxGenJS code
└── README.md                 # This file
```

## Background

The guidelines in this skill draw on:
- Barbara Minto's *Pyramid Principle* (structured argument, action titles)
- Naegle (2021), "Ten simple rules for effective presentation slides," *PLOS Computational Biology*
- Standard consulting and academic presentation practice (McKinsey, conference norms)
- Community feedback on Claude's default presentation behaviour in professional contexts

## License

MIT — free to use, adapt, and share.
