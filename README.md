# Academic Presentations Skill for Gemini CLI

A Gemini skill for creating high-quality academic presentations: conference talks, seminar slides, thesis defenses, and grant briefings.

## Quick Install

To install this skill for Gemini CLI:

```bash
gemini skills install https://github.com/Andrei-WongE/academic-pptx-skill
```

## Features

This skill overrides default design-forward presentation styles and replaces them with communication-first standards appropriate for academic and analytical contexts:

- **Action Titles**: Every slide title is a complete sentence stating the takeaway.
- **Logical Argument**: Deck structure follows a proven narrative spine (Situation → Complication → Resolution).
- **Ghost Deck Test**: The argument must hold together when reading only the slide titles.
- **Exhibit Discipline**: One exhibit per results slide with "so what" annotations.
- **Academic Citations**: In-slide citations and a full References slide at the end.
- **Strategic Conclusions**: The deck ends on a Conclusions slide that stays visible during Q&A.

## Platform Compatibility

This repository is optimized for dual-platform use:

### Gemini CLI (Recommended)
Follow the installation command above. The `gemini/SKILL.md` and `gemini/references/` folder provide immediate, native compatibility with Gemini CLI's skill system.

### Claude Code
The original structure is preserved in the `claude/` directory (flat structure with `SKILL.md` and supporting files) for users who prefer the legacy layout.

## Usage

Once installed, the skill is automatically discovered. You can trigger it naturally:

- *"Make slides for my conference paper on X"*
- *"Build a deck for my thesis defense"*
- *"Create a seminar presentation about my research on Y"*

Gemini will detect the academic context, load this skill, and apply all guidelines.

## Development & Structure

```
academic-pptx-skill/
├── README.md
├── gemini/
│   ├── SKILL.md             # Core methodology + metadata
│   └── references/          # Supporting guidelines and patterns
│       ├── content_guidelines.md
│       └── slide_patterns.md
└── claude/                  # Original Claude Code version (flat)
    ├── SKILL.md
    ├── content_guidelines.md
    └── slide_patterns.md
```

## License

MIT — free to use, adapt, and share.
