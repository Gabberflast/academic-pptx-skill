# ESL Classroom Presentations Skill for Claude

A Claude Skill for creating high-quality ESL (English as a Second Language) classroom presentations: grammar lessons, vocabulary introductions, reading/listening activities, speaking exercises, and review sessions for secondary school students.

## What It Does

This skill overrides Claude's default design-forward presentation style and replaces it with clarity-first standards appropriate for ESL classroom teaching. When active, Claude will:

- Structure the deck as a **PPP lesson flow** (Presentation → Practice → Production) by default, with warm-up and wrap-up bookends
- Write every slide title as a **clear purpose label** — learning target, exercise instruction, or content focus
- Apply the **lesson flow test**: slide titles read in sequence should tell the complete lesson progression
- Provide **one exercise or visual focus per slide** — fill-in-the-blank, matching, multiple choice, error correction, sentence frames, discussion prompts
- Apply **grammar colour coding** by part of speech (verbs = red, nouns = blue, adjectives = green, adverbs = purple, prepositions = orange)
- Apply **consistent text enhancement conventions**: bold for focus words, italics for supplementary info, underline for stress/pronunciation, ALL CAPS for rules and labels
- Use **TV-optimised font sizes** (32 pt titles, 24 pt body) designed for 35 students reading from up to 75" screens at the back of the room
- Enforce the **overriding rule**: content must never overflow a slide — font sizes are targets, not hard limits
- End on a **Review / Wrap-Up slide** with key takeaways and homework — no blank or decorative final slides

## Installation

1. Download this repository as a zip file (click **Code → Download ZIP** above)
2. In [claude.ai](https://claude.ai), go to **Customize → Skills**
3. Upload the zip file
4. Confirm the skill appears in your skills list and is toggled on

> **Requirement:** Code execution and file creation must be enabled in **Settings → Capabilities**.

## Usage

Just ask naturally:

- *"Make slides for my lesson on past simple regular verbs"*
- *"Create a vocabulary presentation about weather for A2 students"*
- *"Build a grammar lesson on comparatives and superlatives"*
- *"I need slides for a reading comprehension activity about travel"*
- *"Make an ESL lesson with fill-in-the-blank and matching exercises on present perfect"*

Claude will detect the ESL classroom context, load this skill automatically, and apply all guidelines before generating any slides. You do not need to give any special instructions.

All presentations are built on top of `Presentation.pptx`, which provides the master slide layouts, theme colours (Office), and fonts (Aptos). Claude uses **python-pptx** to generate slides from this template.

## File Structure

```
esl-classroom-pptx-skill/
├── Presentation.pptx         # Base template — master layouts, theme, fonts (REQUIRED)
├── SKILL.md                  # Entry point: routing logic, design standards, QA checklist
├── content_guidelines.md     # Lesson structure, slide sequence, text enhancement conventions
├── slide_patterns.md         # Per-slide-type implementation patterns with python-pptx code
└── README.md                 # This file
```

## Background

The guidelines in this skill draw on:
- PPP (Presentation, Practice, Production) methodology — standard ESL/EFL lesson structure
- Communicative Language Teaching (CLT) principles
- Task-Based Language Teaching (TBLT) for alternative lesson structures
- Classroom readability research for large-screen display at distance
- The original [Academic Presentations Skill](https://github.com/anthropics/academic-pptx-skill) architecture (adapted for classroom use)
- Community feedback on Claude's default presentation behaviour in educational contexts

## License

MIT — free to use, adapt, and share.
