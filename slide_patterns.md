# Slide Patterns for ESL Classroom Presentations

Implementation patterns for each slide type using **python-pptx** with the **Presentation.pptx** template.

All coordinates are for the template's standard 16:9 dimensions: **13.33" × 7.50"**.

---

## Template Reference (Presentation.pptx)

### Layout Index

| Index | Layout Name | Placeholders | Use For |
|-------|------------|-------------|---------|
| 0 | Title Slide | Center title + subtitle | Lesson title slide |
| 1 | Title and Content | Title + content area | Most content slides, exercises, warm-up, discussion |
| 2 | Section Header | Large title + body text | Section dividers between lesson phases |
| 3 | Two Content | Title + two columns | Matching exercises, grouped vocabulary |
| 4 | Comparison | Title + 2 headers + 2 content areas | Grammar comparison tables |
| 5 | Title Only | Title only, body area open | Complex custom layouts (grammar rules, exercises with word banks) |
| 6 | Blank | No placeholders | Fully custom slides (review/wrap-up with dark bg, breadcrumb) |
| 8 | Picture with Caption | Title left + picture right + text left | Single-focus vocabulary |

### Key Placeholder Positions

```
Layout 1 "Title and Content":
  Title:   (0.92", 0.40") → 11.50" × 1.45"
  Content: (0.92", 2.00") → 11.50" × 4.76"

Layout 3 "Two Content":
  Title:        (0.92", 0.40") → 11.50" × 1.45"
  Left column:  (0.92", 2.00") → 5.67" × 4.76"
  Right column: (6.75", 2.00") → 5.67" × 4.76"

Layout 5 "Title Only":
  Title: (0.92", 0.40") → 11.50" × 1.45"
  Body:  open canvas from y=2.00" downward
```

---

## Global Defaults

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ── Colours ─────────────────────────────────────────────
COLORS = {
    "primary":   RGBColor(0x0E, 0x28, 0x41),  # Dark navy (theme dk2)
    "accent":    RGBColor(0x15, 0x60, 0x82),  # Teal-blue (theme accent1)
    "accent2":   RGBColor(0xE9, 0x71, 0x32),  # Orange (theme accent2)
    "green":     RGBColor(0x19, 0x6B, 0x24),  # Green (theme accent3)
    "body":      RGBColor(0x2D, 0x2D, 0x2D),  # Near-black — body text
    "muted":     RGBColor(0x77, 0x77, 0x77),  # Gray — attribution, labels
    "white":     RGBColor(0xFF, 0xFF, 0xFF),
    "rule":      RGBColor(0xCC, 0xCC, 0xCC),  # Light gray — divider lines
    "highlight": RGBColor(0xFF, 0xF2, 0xCC),  # Yellow — word bank boxes
    "callout":   RGBColor(0xEB, 0xF3, 0xFA),  # Light blue — rule/objective boxes
}

# Grammar colour coding — default scheme, overridable per lesson
GRAMMAR = {
    "verb":        RGBColor(0xC0, 0x39, 0x2B),  # Red
    "noun":        RGBColor(0x2E, 0x75, 0xB6),  # Blue
    "adjective":   RGBColor(0x27, 0xAE, 0x60),  # Green
    "adverb":      RGBColor(0x8E, 0x44, 0xAD),  # Purple
    "preposition": RGBColor(0xE6, 0x7E, 0x22),  # Orange
}

# ── Fonts (from template theme) ─────────────────────────
FONT_TITLE = "Aptos Display"   # Theme major font (headings)
FONT_BODY  = "Aptos"           # Theme minor font (body text)

# Target sizes (NOT hard limits — content must fit, shrink if needed)
SIZE_TITLE       = Pt(32)
SIZE_SECTION     = Pt(26)
SIZE_BODY        = Pt(24)
SIZE_VOCAB       = Pt(36)
SIZE_EXERCISE    = Pt(24)
SIZE_INSTRUCTION = Pt(22)
SIZE_LABEL       = Pt(16)

# ── Layout constants ────────────────────────────────────
MARGIN    = Inches(0.92)
CONTENT_Y = Inches(2.0)    # Where body content starts (below title)
CONTENT_W = Inches(11.50)  # Full content width
CONTENT_H = Inches(4.76)   # Content area height
SLIDE_W   = Inches(13.33)
SLIDE_H   = Inches(7.50)


# ── Helper functions ────────────────────────────────────

def load_template(template_path="Presentation.pptx"):
    """Load template and remove the blank placeholder slide."""
    prs = Presentation(template_path)
    # Remove the existing blank slide(s)
    ns = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
    while len(prs.slides._sldIdLst):
        rId = prs.slides._sldIdLst[0].get(f'{ns}id')
        if rId:
            prs.part.drop_rel(rId)
        del prs.slides._sldIdLst[0]
    return prs


def add_run(paragraph, text, size=None, font=None, bold=False,
            italic=False, color=None, underline=False):
    """Add a formatted run to a paragraph."""
    run = paragraph.add_run()
    run.text = text
    if size:      run.font.size = size
    if font:      run.font.name = font
    if bold:      run.font.bold = True
    if italic:    run.font.italic = True
    if color:     run.font.color.rgb = color
    if underline: run.font.underline = True
    return run


def set_paragraph(paragraph, text, size=None, font=None, bold=False,
                  italic=False, color=None, alignment=None, space_after=None):
    """Configure a paragraph with uniform formatting."""
    paragraph.text = text
    paragraph.alignment = alignment
    if space_after is not None:
        paragraph.space_after = Pt(space_after)
    for run in paragraph.runs:
        if size:   run.font.size = size
        if font:   run.font.name = font
        if bold:   run.font.bold = bold
        if italic: run.font.italic = italic
        if color:  run.font.color.rgb = color


def add_textbox(slide, left, top, width, height, text="",
                size=SIZE_BODY, font=FONT_BODY, bold=False, italic=False,
                color=COLORS["body"], alignment=PP_ALIGN.LEFT,
                valign=MSO_ANCHOR.TOP, word_wrap=True):
    """Add a text box with consistent defaults."""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = word_wrap
    p = tf.paragraphs[0]
    p.text = text
    p.alignment = alignment
    for run in p.runs:
        run.font.size = size
        run.font.name = font
        run.font.bold = bold
        run.font.italic = italic
        run.font.color.rgb = color
    return txBox


def add_rounded_rect(slide, left, top, width, height,
                     fill_color=COLORS["callout"],
                     border_color=COLORS["accent"], border_pt=1.5):
    """Add a rounded rectangle (callout/highlight box)."""
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    ln = shape.line
    ln.color.rgb = border_color
    ln.width = Pt(border_pt)
    return shape


def set_slide_bg(slide, color):
    """Set solid background colour on a slide."""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color
```

**IMPORTANT: Font sizes above are TARGETS.** The overriding rule is that all content must fit on the slide without overflowing. Reduce sizes if needed; split to additional slides if content would become too small to read. The teacher's content always takes priority.

---

## 1. Title Slide

**Purpose:** Establish the lesson; tell students what today's class is about.
**Layout:** 0 — "Title Slide"

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])

# Title (placeholder 0 — centred)
title = slide.placeholders[0]
title.text = "Prepositions of Time: IN, ON, AT"
for run in title.text_frame.paragraphs[0].runs:
    run.font.size = Pt(40)
    run.font.bold = True

# Subtitle (placeholder 1) — objective + class info
subtitle = slide.placeholders[1]
tf = subtitle.text_frame
p = tf.paragraphs[0]
p.text = "Today: use IN, ON, and AT to talk about when things happen"
p.alignment = PP_ALIGN.CENTER
for run in p.runs:
    run.font.size = Pt(22)

p2 = tf.add_paragraph()
p2.text = "Wednesday, 4 March 2026  ·  S.1  ·  Period 3"
p2.alignment = PP_ALIGN.CENTER
for run in p2.runs:
    run.font.size = Pt(16)
    run.font.color.rgb = COLORS["muted"]
```

---

## 2. Learning Objective Slide

**Purpose:** "Today we will..." — give students a clear, measurable target.
**Layout:** 5 — "Title Only" (custom body with callout box)

```python
slide = prs.slides.add_slide(prs.slide_layouts[5])

# Title (placeholder 0)
slide.placeholders[0].text = "Today's Objective"

# Callout box with main objective
box = add_rounded_rect(slide,
    Inches(1.5), Inches(2.2), Inches(10.3), Inches(1.4),
    fill_color=COLORS["callout"], border_color=COLORS["accent"])

txBox = add_textbox(slide,
    Inches(1.8), Inches(2.35), Inches(9.7), Inches(1.1),
    text="Today we will use IN, ON, and AT to talk and write about when things happen.",
    size=SIZE_BODY, font=FONT_BODY, bold=True,
    color=COLORS["primary"], alignment=PP_ALIGN.CENTER)

# Sub-objectives
txBox2 = slide.shapes.add_textbox(Inches(1.5), Inches(4.0), Inches(10.3), Inches(2.5))
tf = txBox2.text_frame
tf.word_wrap = True

objectives = [
    "By the end of this lesson, you can:",
    "• Use IN with months, years, and seasons",
    "• Use ON with days and dates",
    "• Use AT with exact times",
    "• Choose the correct preposition in sentences",
]
for i, obj in enumerate(objectives):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.text = obj
    p.space_after = Pt(8)
    for run in p.runs:
        run.font.size = SIZE_BODY
        run.font.name = FONT_BODY
        run.font.color.rgb = COLORS["body"]
        if i == 0:
            run.font.bold = True
```

---

## 3. Warm-Up / Do Now Slide

**Purpose:** Quick opener to get students thinking in English. Connects to today's topic.
**Layout:** 1 — "Title and Content"

```python
slide = prs.slides.add_slide(prs.slide_layouts[1])

# Title
slide.placeholders[0].text = "Warm-Up: When Is It?"

# Content — use the content placeholder
tf = slide.placeholders[1].text_frame
tf.word_wrap = True

set_paragraph(tf.paragraphs[0],
    "Answer these questions with your partner:",
    size=SIZE_BODY, font=FONT_BODY, bold=True,
    color=COLORS["body"], space_after=16)

questions = [
    "1. What month is your birthday?",
    "2. What day is our English class?",
    "3. What time does school start?",
]
for q in questions:
    p = tf.add_paragraph()
    set_paragraph(p, q,
        size=SIZE_BODY, font=FONT_BODY,
        color=COLORS["body"], space_after=12)
```

---

## 4. Vocabulary Slide (Single Focus)

**Purpose:** Introduce one word with image, definition, and example.
**Layout:** 8 — "Picture with Caption" (title + text left, picture right)

```python
slide = prs.slides.add_slide(prs.slide_layouts[8])

# Title (placeholder 0, left side)
slide.placeholders[0].text = "Weather Vocabulary"

# Picture placeholder (placeholder 1, right side at 5.67", 1.08")
# Insert image into the picture placeholder
pic_ph = slide.placeholders[1]
pic_ph.insert_picture(open("umbrella.png", "rb"))

# Text area (placeholder 2, left side below title)
tf = slide.placeholders[2].text_frame
tf.word_wrap = True

# Word — large
p = tf.paragraphs[0]
add_run(p, "umbrella", size=SIZE_VOCAB, font=FONT_BODY, bold=True, color=COLORS["primary"])

# Part of speech
p2 = tf.add_paragraph()
add_run(p2, "(noun)", size=Pt(18), font=FONT_BODY, italic=True, color=GRAMMAR["noun"])
p2.space_after = Pt(8)

# Definition
p3 = tf.add_paragraph()
add_run(p3, "A thing you hold over your head to stay dry when it rains.",
        size=Pt(20), font=FONT_BODY, color=COLORS["body"])
p3.space_after = Pt(12)

# Example with target word bolded
p4 = tf.add_paragraph()
add_run(p4, "Example: ", size=Pt(20), font=FONT_BODY, bold=True, color=COLORS["accent"])
add_run(p4, "Don't forget your ", size=Pt(20), font=FONT_BODY, color=COLORS["body"])
add_run(p4, "umbrella", size=Pt(20), font=FONT_BODY, bold=True, color=COLORS["body"])
add_run(p4, " — it's raining!", size=Pt(20), font=FONT_BODY, color=COLORS["body"])
```

---

## 5. Vocabulary Slide (Grouped)

**Purpose:** Present 4–6 thematically grouped words in two columns.
**Layout:** 3 — "Two Content"

```python
slide = prs.slides.add_slide(prs.slide_layouts[3])

# Title
slide.placeholders[0].text = "Weather Vocabulary"

# Left column (placeholder 1)
tf_left = slide.placeholders[1].text_frame
tf_left.word_wrap = True
words_left = [
    ("sunny", "bright, with lots of sun"),
    ("cloudy", "covered with clouds"),
    ("rainy", "raining, wet weather"),
]
for i, (word, defn) in enumerate(words_left):
    p = tf_left.paragraphs[0] if i == 0 else tf_left.add_paragraph()
    add_run(p, word, size=Pt(26), font=FONT_BODY, bold=True, color=COLORS["primary"])
    p.space_after = Pt(2)
    p2 = tf_left.add_paragraph()
    add_run(p2, defn, size=Pt(18), font=FONT_BODY, color=COLORS["body"])
    p2.space_after = Pt(16)

# Right column (placeholder 2)
tf_right = slide.placeholders[2].text_frame
tf_right.word_wrap = True
words_right = [
    ("windy", "strong wind blowing"),
    ("snowy", "snow falling from the sky"),
    ("foggy", "thick mist, hard to see"),
]
for i, (word, defn) in enumerate(words_right):
    p = tf_right.paragraphs[0] if i == 0 else tf_right.add_paragraph()
    add_run(p, word, size=Pt(26), font=FONT_BODY, bold=True, color=COLORS["primary"])
    p.space_after = Pt(2)
    p2 = tf_right.add_paragraph()
    add_run(p2, defn, size=Pt(18), font=FONT_BODY, color=COLORS["body"])
    p2.space_after = Pt(16)
```

---

## 6. Grammar Rule Slide

**Purpose:** Present a grammar rule clearly. Rule in a callout box, examples below with colour-coded elements.
**Layout:** 5 — "Title Only" (custom body with callout box + examples)

```python
slide = prs.slides.add_slide(prs.slide_layouts[5])

# Title
slide.placeholders[0].text = "Past Simple — Regular Verbs"

# Rule callout box
add_rounded_rect(slide,
    Inches(1.0), Inches(2.1), Inches(11.3), Inches(1.2),
    fill_color=COLORS["callout"], border_color=COLORS["accent"])

rule_box = slide.shapes.add_textbox(
    Inches(1.2), Inches(2.2), Inches(10.9), Inches(1.0))
tf = rule_box.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.alignment = PP_ALIGN.CENTER
add_run(p, "RULE: ", size=SIZE_BODY, font=FONT_BODY, bold=True, color=COLORS["primary"])
add_run(p, "Add ", size=SIZE_BODY, font=FONT_BODY, color=COLORS["primary"])
add_run(p, "-ed", size=Pt(26), font=FONT_BODY, bold=True, color=GRAMMAR["verb"])
add_run(p, " to the base form of the verb.", size=SIZE_BODY, font=FONT_BODY, color=COLORS["primary"])

# Examples header
add_textbox(slide,
    MARGIN, Inches(3.5), Inches(11.5), Inches(0.4),
    text="EXAMPLES", size=Pt(20), font=FONT_BODY,
    bold=True, color=COLORS["accent"])

# Examples with colour-coded verbs
examples_box = slide.shapes.add_textbox(
    Inches(1.3), Inches(4.0), Inches(10.7), Inches(3.0))
tf = examples_box.text_frame
tf.word_wrap = True

examples = [
    ("I ", "walked", " to school yesterday."),
    ("She ", "played", " football after class."),
    ("We ", "watched", " a film last night."),
    ("They ", "listened", " to music at the party."),
]
for i, (before, verb, after) in enumerate(examples):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.space_after = Pt(14)
    add_run(p, before, size=SIZE_BODY, font=FONT_BODY, color=COLORS["body"])
    add_run(p, verb, size=SIZE_BODY, font=FONT_BODY, bold=True, color=GRAMMAR["verb"])
    add_run(p, after, size=SIZE_BODY, font=FONT_BODY, color=COLORS["body"])
```

---

## 7. Fill-in-the-Blank Exercise

**Purpose:** Controlled practice. Students complete sentences with the target language.
**Layout:** 5 — "Title Only" (instruction + items + word bank)

```python
slide = prs.slides.add_slide(prs.slide_layouts[5])

# Title
slide.placeholders[0].text = "Fill in the Blank — Use the Past Simple"

# Instruction
add_textbox(slide,
    MARGIN, Inches(2.0), CONTENT_W, Inches(0.5),
    text="Write the correct past simple form of the verb in brackets.",
    size=SIZE_INSTRUCTION, font=FONT_BODY, italic=True, color=COLORS["body"])

# Exercise items
items_box = slide.shapes.add_textbox(
    Inches(1.2), Inches(2.7), Inches(11.0), Inches(3.2))
tf = items_box.text_frame
tf.word_wrap = True

items = [
    "1. I __________ (walk) to school yesterday.",
    "2. She __________ (play) tennis after class.",
    "3. They __________ (watch) TV last night.",
    "4. We __________ (listen) to the teacher carefully.",
    "5. He __________ (clean) his room on Saturday.",
]
for i, item in enumerate(items):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.space_after = Pt(12)
    add_run(p, item, size=SIZE_EXERCISE, font=FONT_BODY, color=COLORS["body"])

# Word bank
add_rounded_rect(slide,
    Inches(1.0), Inches(6.1), Inches(11.3), Inches(0.8),
    fill_color=COLORS["highlight"], border_color=RGBColor(0xE6, 0xC8, 0x00))

add_textbox(slide,
    Inches(1.2), Inches(6.2), Inches(10.9), Inches(0.6),
    text="WORD BANK:  walked  ·  played  ·  watched  ·  listened  ·  cleaned",
    size=Pt(20), font=FONT_BODY, bold=True,
    color=RGBColor(0x5A, 0x40, 0x00), alignment=PP_ALIGN.CENTER)
```

---

## 8. Matching Exercise

**Purpose:** Students match items from two columns.
**Layout:** 3 — "Two Content"

```python
slide = prs.slides.add_slide(prs.slide_layouts[3])

# Title
slide.placeholders[0].text = "Match — Word to Definition"

# Left column (placeholder 1) — words
tf_left = slide.placeholders[1].text_frame
tf_left.word_wrap = True
left_items = ["1. sunny", "2. foggy", "3. windy", "4. stormy"]
for i, item in enumerate(left_items):
    p = tf_left.paragraphs[0] if i == 0 else tf_left.add_paragraph()
    p.space_after = Pt(16)
    add_run(p, item, size=SIZE_EXERCISE, font=FONT_BODY, bold=True, color=COLORS["body"])

# Right column (placeholder 2) — definitions (shuffled)
tf_right = slide.placeholders[2].text_frame
tf_right.word_wrap = True
right_items = [
    "a) strong wind blowing hard",
    "b) bright sky with lots of sun",
    "c) thick mist, hard to see far",
    "d) thunder, lightning, heavy rain",
]
for i, item in enumerate(right_items):
    p = tf_right.paragraphs[0] if i == 0 else tf_right.add_paragraph()
    p.space_after = Pt(16)
    add_run(p, item, size=SIZE_EXERCISE, font=FONT_BODY, color=COLORS["body"])
```

---

## 9. Multiple Choice Exercise

**Purpose:** Students choose the correct answer from options.
**Layout:** 1 — "Title and Content"

```python
slide = prs.slides.add_slide(prs.slide_layouts[1])

# Title
slide.placeholders[0].text = "Choose the Correct Answer"

# Content
tf = slide.placeholders[1].text_frame
tf.word_wrap = True

# Question
p = tf.paragraphs[0]
add_run(p, "She __________ to the park yesterday.",
        size=Pt(26), font=FONT_BODY, bold=True, color=COLORS["body"])
p.space_after = Pt(20)

# Options
options = ["A)  go", "B)  goes", "C)  went", "D)  going"]
for opt in options:
    p = tf.add_paragraph()
    p.space_after = Pt(14)
    label = opt[:2]
    text = opt[4:]
    add_run(p, label + "  ", size=SIZE_EXERCISE, font=FONT_BODY, bold=True, color=COLORS["accent"])
    add_run(p, text, size=SIZE_EXERCISE, font=FONT_BODY, color=COLORS["body"])
```

**For multiple questions per slide:** Reduce font size to fit. If more than 2 questions with 4 options each, split across slides.

---

## 10. Error Correction Exercise

**Purpose:** Students identify and fix mistakes. Builds accuracy and attention to form.
**Layout:** 5 — "Title Only" (items + optional hint box)

```python
slide = prs.slides.add_slide(prs.slide_layouts[5])

# Title
slide.placeholders[0].text = "Find and Fix the Mistakes"

# Instruction
add_textbox(slide,
    MARGIN, Inches(2.0), CONTENT_W, Inches(0.5),
    text="Each sentence has ONE mistake. Find it and write the correct sentence.",
    size=SIZE_INSTRUCTION, font=FONT_BODY, italic=True, color=COLORS["body"])

# Items
items_box = slide.shapes.add_textbox(
    Inches(1.2), Inches(2.7), Inches(11.0), Inches(3.2))
tf = items_box.text_frame
tf.word_wrap = True

sentences = [
    "1. She walkd to school yesterday.",
    "2. I did not played football last week.",
    "3. They was very happy at the party.",
    "4. He cleanned his room on Saturday.",
    "5. We didn't went to the cinema.",
]
for i, s in enumerate(sentences):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.space_after = Pt(14)
    add_run(p, s, size=SIZE_EXERCISE, font=FONT_BODY, color=COLORS["body"])

# Hint box (optional — for lower levels)
add_rounded_rect(slide,
    Inches(1.0), Inches(6.2), Inches(11.3), Inches(0.7),
    fill_color=COLORS["callout"], border_color=COLORS["accent"])
add_textbox(slide,
    Inches(1.2), Inches(6.3), Inches(10.9), Inches(0.5),
    text="HINT: Look for spelling, verb form, and auxiliary verb errors.",
    size=Pt(18), font=FONT_BODY, italic=True,
    color=COLORS["accent"], alignment=PP_ALIGN.CENTER)
```

---

## 11. Sentence Frame / Model Dialogue

**Purpose:** Provide structured language frames with highlighted blanks and a word bank.
**Layout:** 5 — "Title Only"

```python
slide = prs.slides.add_slide(prs.slide_layouts[5])

# Title
slide.placeholders[0].text = "Talking About Last Weekend"

# Instruction
add_textbox(slide,
    MARGIN, Inches(2.0), CONTENT_W, Inches(0.45),
    text="Use these sentence frames to tell your partner about your weekend.",
    size=SIZE_INSTRUCTION, font=FONT_BODY, italic=True, color=COLORS["body"])

# Sentence frames with accent-coloured blanks
frames_box = slide.shapes.add_textbox(
    Inches(1.2), Inches(2.7), Inches(10.9), Inches(2.5))
tf = frames_box.text_frame
tf.word_wrap = True

frames = [
    [("On Saturday, I ", None), ("______________", COLORS["accent"]),
     (" with my ", None), ("______________", COLORS["accent"]), (".", None)],
    [("It was really ", None), ("______________", COLORS["accent"]),
     (" because ", None), ("______________", COLORS["accent"]), (".", None)],
    [("On Sunday, I didn't ", None), ("______________", COLORS["accent"]),
     (". Instead, I ", None), ("______________", COLORS["accent"]), (".", None)],
]
for i, frame in enumerate(frames):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.space_after = Pt(16)
    for text, color in frame:
        add_run(p, text, size=SIZE_BODY, font=FONT_BODY,
                bold=color is not None, color=color or COLORS["body"])

# Word bank
add_rounded_rect(slide,
    Inches(1.0), Inches(5.5), Inches(11.3), Inches(1.3),
    fill_color=COLORS["highlight"], border_color=RGBColor(0xE6, 0xC8, 0x00))
add_textbox(slide,
    Inches(1.2), Inches(5.55), Inches(10.9), Inches(0.35),
    text="IDEAS", size=Pt(18), font=FONT_BODY, bold=True,
    color=RGBColor(0x5A, 0x40, 0x00))
add_textbox(slide,
    Inches(1.2), Inches(5.9), Inches(10.9), Inches(0.8),
    text="played football  ·  watched a film  ·  visited grandma  ·  cooked dinner  ·  stayed home  ·  fun  ·  boring  ·  exciting",
    size=Pt(18), font=FONT_BODY,
    color=RGBColor(0x5A, 0x40, 0x00), alignment=PP_ALIGN.CENTER)
```

---

## 12. Discussion Prompt Slide

**Purpose:** Set up pair/group discussion with a prompt and sentence starters.
**Layout:** 1 — "Title and Content"

```python
slide = prs.slides.add_slide(prs.slide_layouts[1])

# Title
slide.placeholders[0].text = "Pair Discussion — What Did You Do Last Weekend?"

# Content
tf = slide.placeholders[1].text_frame
tf.word_wrap = True

# Activity instruction
p = tf.paragraphs[0]
add_run(p, "With your partner: ", size=SIZE_BODY, font=FONT_BODY, bold=True, color=COLORS["body"])
add_run(p, "Ask and answer these questions. Use FULL SENTENCES.", size=SIZE_BODY, font=FONT_BODY, color=COLORS["body"])
p.space_after = Pt(16)

# Questions
questions = [
    "1. What did you do on Saturday?",
    "2. Did you go anywhere special?",
    "3. What was the best part of your weekend?",
]
for q in questions:
    p = tf.add_paragraph()
    p.space_after = Pt(12)
    add_run(p, q, size=SIZE_BODY, font=FONT_BODY, color=COLORS["body"])

# Sentence starters header
p = tf.add_paragraph()
p.space_after = Pt(8)
add_run(p, "SENTENCE STARTERS", size=Pt(20), font=FONT_BODY, bold=True, color=COLORS["accent"])

starters = [
    '"On Saturday, I ..."',
    '"Yes, I went to ... / No, I stayed ..."',
    '"The best part was ... because ..."',
]
for s in starters:
    p = tf.add_paragraph()
    p.space_after = Pt(6)
    add_run(p, s, size=Pt(22), font=FONT_BODY, italic=True, color=COLORS["body"])
```

---

## 13. Comparison Table Slide

**Purpose:** Side-by-side comparison of grammar forms or vocabulary categories.
**Layout:** 5 — "Title Only" (custom table below title)

```python
from pptx.util import Inches, Pt

slide = prs.slides.add_slide(prs.slide_layouts[5])

# Title
slide.placeholders[0].text = "Present Simple vs. Present Continuous"

# Table
rows, cols = 5, 3
tbl_shape = slide.shapes.add_table(
    rows, cols, Inches(0.8), Inches(2.1), Inches(11.7), Inches(4.5))
table = tbl_shape.table

# Header row
headers = ["", "Present Simple", "Present Continuous"]
for j, h in enumerate(headers):
    cell = table.cell(0, j)
    cell.text = h
    for p in cell.text_frame.paragraphs:
        for run in p.runs:
            run.font.size = Pt(20)
            run.font.bold = True
            run.font.color.rgb = COLORS["white"]
    cell.fill.solid()
    cell.fill.fore_color.rgb = COLORS["primary"]

# Data rows
data = [
    ["Form", "subject + base verb\n(he/she/it + verb-s)", "subject + am/is/are\n+ verb-ing"],
    ["Use", "habits, routines,\ngeneral truths", "actions happening\nright now"],
    ["Signal words", "always, usually,\nevery day, often", "now, right now,\nat the moment"],
    ["Example", "I play football\nevery Saturday.", "I am playing football\nright now."],
]
for i, row_data in enumerate(data):
    for j, text in enumerate(row_data):
        cell = table.cell(i + 1, j)
        cell.text = text
        for p in cell.text_frame.paragraphs:
            for run in p.runs:
                run.font.size = Pt(20)
                run.font.name = FONT_BODY
                run.font.color.rgb = COLORS["body"]
                if j == 0:
                    run.font.bold = True
```

---

## 14. Reading / Listening Text Slide

**Purpose:** Display a passage for reading comprehension. Font shrinks as needed to fit.
**Layout:** 5 — "Title Only"

```python
slide = prs.slides.add_slide(prs.slide_layouts[5])

# Title
slide.placeholders[0].text = "Read the Text — Holiday Email"

# Reading focus instruction
add_textbox(slide,
    MARGIN, Inches(2.0), CONTENT_W, Inches(0.4),
    text="Read the email. Underline all past simple verbs.",
    size=Pt(20), font=FONT_BODY, bold=True, color=COLORS["accent"])

# Text passage box (lightly bordered)
add_rounded_rect(slide,
    Inches(0.8), Inches(2.6), Inches(11.7), Inches(4.2),
    fill_color=RGBColor(0xFA, 0xFA, 0xFA),
    border_color=COLORS["rule"], border_pt=1)

# Passage text — font adapts to content length
# Short: 22-24pt. Long: 18-20pt. Very long: 16pt or split slides.
passage = (
    "Hi Maria!\n\n"
    "I arrived in London last Tuesday. On Wednesday, I visited the British Museum "
    "and walked along the Thames. It was really beautiful!\n\n"
    "On Thursday, I tried fish and chips — I loved it! Yesterday, I shopped at "
    "Camden Market and bought some souvenirs.\n\n"
    "See you next week!\nAnna"
)
add_textbox(slide,
    Inches(1.1), Inches(2.8), Inches(11.1), Inches(3.8),
    text=passage, size=Pt(20), font=FONT_BODY, color=COLORS["body"])
```

**Critical:** Reading passages are the most common case where the overriding fit rule applies. Shrink font to fit. If text is too long even at 16 pt, split across slides with "continued" labels.

---

## 15. Review / Wrap-Up Slide

**Purpose:** Summarise key takeaways + homework. LAST content slide — stays on screen.
**Layout:** 6 — "Blank" (fully custom with dark background)

```python
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(slide, COLORS["primary"])

# "What We Learned Today" header
add_textbox(slide,
    MARGIN, Inches(0.4), Inches(11.5), Inches(0.6),
    text="What We Learned Today", size=SIZE_BODY, font=FONT_TITLE,
    bold=True, color=RGBColor(0xA0, 0xBB, 0xDD))

# Accent rule
slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE, MARGIN, Inches(1.05), Inches(11.5), Pt(3)
).fill.solid()
slide.shapes[-1].fill.fore_color.rgb = COLORS["accent"]
slide.shapes[-1].line.fill.background()

# Key takeaways
takeaways_box = slide.shapes.add_textbox(
    MARGIN, Inches(1.3), Inches(11.5), Inches(3.5))
tf = takeaways_box.text_frame
tf.word_wrap = True

takeaways = [
    ("1. Regular past simple: ", "add -ed (walk → walked, play → played)"),
    ("2. Negative: ", "didn't + base form (NOT didn't walked)"),
    ("3. Questions: ", "Did + subject + base form (NOT Did you played?)"),
]
for i, (label, detail) in enumerate(takeaways):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.space_after = Pt(18)
    add_run(p, label, size=Pt(22), font=FONT_BODY, bold=True, color=COLORS["white"])
    add_run(p, detail, size=Pt(22), font=FONT_BODY, color=COLORS["white"])

# Homework section
add_textbox(slide,
    MARGIN, Inches(5.2), Inches(11.5), Inches(0.4),
    text="HOMEWORK", size=Pt(20), font=FONT_BODY,
    bold=True, color=RGBColor(0xA0, 0xBB, 0xDD))

add_textbox(slide,
    MARGIN, Inches(5.65), Inches(11.5), Inches(1.0),
    text="Workbook p. 34, exercises 1–3. Write 5 sentences about your last holiday.",
    size=Pt(20), font=FONT_BODY, color=RGBColor(0xCA, 0xDC, 0xFC))
```

**Do not follow this slide** with "Goodbye", a blank slide, or anything else. It stays on screen.

---

## 16. Section Divider

**Purpose:** Orient students when the lesson moves to a new phase. Use for decks > 15 slides.
**Layout:** 2 — "Section Header"

```python
slide = prs.slides.add_slide(prs.slide_layouts[2])

# Title (large, central)
slide.placeholders[0].text = "Time to Practise!"

# Body text (below title)
slide.placeholders[1].text = "Let's use IN, ON, and AT in exercises."
```

For a dark-background divider, use Layout 6 "Blank" with `set_slide_bg()` and custom text boxes instead.

---

## 17. Breadcrumb Bar (optional, for longer lessons)

A persistent header strip showing the current lesson phase. Add to content slides for decks > 15 slides.

```python
def add_breadcrumb(slide, current_phase):
    """Add a breadcrumb bar to the top of a slide."""
    phases = ["Warm-Up", "New Language", "Practice", "Production", "Review"]

    bar_y = Inches(0)
    bar_h = Inches(0.3)
    phase_w = SLIDE_W / len(phases)

    # Background strip
    bg_bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), bar_y, SLIDE_W, bar_h)
    bg_bar.fill.solid()
    bg_bar.fill.fore_color.rgb = RGBColor(0xF0, 0xF4, 0xF8)
    bg_bar.line.fill.background()

    for i, phase in enumerate(phases):
        is_active = (phase == current_phase)
        tb = slide.shapes.add_textbox(
            int(i * phase_w), bar_y, int(phase_w), bar_h)
        p = tb.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        add_run(p, phase, size=Pt(10), font=FONT_BODY,
                bold=is_active,
                color=COLORS["accent"] if is_active else COLORS["muted"])

        if is_active:
            indicator = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                int(i * phase_w + phase_w * 0.1),
                bar_y + bar_h - Pt(4),
                int(phase_w * 0.8),
                Pt(4))
            indicator.fill.solid()
            indicator.fill.fore_color.rgb = COLORS["accent"]
            indicator.line.fill.background()
```

---

## Quick Checks Before Use

```
□ Template loaded: Presentation.pptx used as base (not blank Presentation())
□ Blank placeholder slide removed before adding content
□ Title slide: lesson topic, date, learning objective, class info
□ Every slide: clear purpose title using the correct layout
□ Lesson flow test: titles tell the progression warm-up → input → practice → production → review
□ Exercise slides: written instructions present
□ Vocabulary slides: word + definition + example sentence (image if available)
□ Grammar slides: rule in callout box, colour-coded examples
□ Grammar colours: consistent throughout (verbs=red, nouns=blue, adj=green, adv=purple, prep=orange)
□ Text enhancements: bold/italic/underline/caps used per content_guidelines.md §5 consistently
□ Content fits: no text overflows any slide (font sizes are targets, not limits)
□ Word banks: included on exercise slides for A1–A2 levels
□ Wrap-up slide: last content slide, key takeaways + homework
□ No decorative images — every image supports learning
□ Saved as .pptx with descriptive filename
```
