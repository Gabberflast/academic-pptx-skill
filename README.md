# Academic Presentations Skill for Gemini CLI

A Gemini skill for creating high-quality academic presentations: conference talks, seminar slides, thesis defenses, and grant briefings.

## What It Does

This skill overrides default design-forward presentation styles and replaces them with communication-first standards appropriate for academic and analytical contexts. When active, Gemini will:

- Write every slide title as a **complete sentence stating the takeaway** ("action title"), not a topic label.
- Structure the deck as a **logical argument** (situation → complication → resolution), not a collection of independent slides.
- Apply the **ghost deck test**: the action titles alone, read in sequence, should tell the full story.
- Place **one exhibit per results slide** and annotate the key finding directly on the chart.
- Apply **citation standards**: in-text citations on every borrowed figure, a References slide at the end.
- End on a **Conclusions slide** that stays on screen during Q&A — never on "Thank You" or a blank.
- Apply minimal, communication-first design: white backgrounds, single sans-serif font, three colours maximum, no decorative icons.

## Installation

To install this skill globally:

```bash
gemini skills install https://github.com/Andrei-WongE/academic-pptx-skill
```

To install it for the current workspace only:

```bash
gemini skills install https://github.com/Andrei-WongE/academic-pptx-skill --scope workspace
```

## Usage

Once installed, the skill is automatically discovered. You can trigger it naturally:

- *"Make slides for my conference paper on X"*
- *"Build a deck for my thesis defense"*
- *"Create a seminar presentation about my research on Y"*

Gemini will detect the academic context, load this skill, and apply all guidelines.

## File Structure

This repository follows the Gemini "multi-skill" pattern:

```
academic-pptx-skill/
├── skills/
│   └── academic-pptx/
│       ├── SKILL.md             # Entry point: routing logic and design standards
│       ├── content_guidelines.md # Argument structure, action titles, citations
│       └── slide_patterns.md     # Per-slide-type implementation patterns
├── README.md                    # This file
└── LICENSE                      # MIT License
```

## Background

The guidelines in this skill draw on:
- Barbara Minto's *Pyramid Principle* (structured argument, action titles)
- Naegle (2021), "Ten simple rules for effective presentation slides," *PLOS Computational Biology*
- Standard consulting and academic presentation practice (McKinsey, conference norms)
- Community feedback on AI's default presentation behaviour in professional contexts

## License

MIT — free to use, adapt, and share.
