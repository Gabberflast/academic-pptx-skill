# Slide Patterns for ESL Classroom Presentations

Implementation patterns for each slide type. Use with `pptxgenjs.md` for the technical API.

All coordinates assume `LAYOUT_16x9` (10" × 5.625"). Adjust proportionally for other layouts.

---

## Global Defaults

Apply these to every slide in an ESL classroom deck.

**IMPORTANT: Font sizes are TARGETS, not hard limits.** The overriding rule is that all content must fit on the slide without overflowing. Reduce sizes if needed to prevent overflow; split to additional slides if content would become too small to read. The teacher's content always takes priority.

```javascript
const COLORS = {
  bg:        "FFFFFF",   // White background
  primary:   "1F4E79",   // Dark navy — titles
  accent:    "2E75B6",   // Mid-blue — headers, highlights
  body:      "2D2D2D",   // Near-black — body text
  muted:     "777777",   // Gray — attribution, labels
  rule:      "CCCCCC",   // Light gray — divider lines
  highlight: "FFF2CC",   // Yellow — callout boxes (use sparingly)
  callout:   "EBF3FA",   // Light blue — rule boxes, objective boxes
};

// Grammar colour coding — default scheme, overridable per lesson
// Apply when teaching parts of speech or highlighting target structures
const GRAMMAR = {
  verb:        "C0392B",  // Red
  noun:        "2E75B6",  // Blue
  adjective:   "27AE60",  // Green
  adverb:      "8E44AD",  // Purple
  preposition: "E67E22",  // Orange
};

const FONTS = {
  face: "Arial",         // Single typeface throughout
  title: 32,             // Slide title: 32 pt target
  sectionHeader: 26,     // Within-slide section headers
  body: 24,              // Body text, instructions: 24 pt target
  vocab: 36,             // Key vocabulary words: prominent
  exercise: 24,          // Exercise content: 24 pt target
  label: 16,             // Labels, attribution
  instruction: 24,       // Written instructions on exercise slides
};

const MARGIN = 0.5;      // Minimum margin from slide edge (inches)
```

---

## 1. Title Slide

**Purpose:** Establish the lesson; tell students what today's class is about.

```javascript
// Dark background — one of the few places for it
slide.background = { color: COLORS.primary };

// Lesson topic — large and clear
slide.addText("Past Simple — Regular Verbs", {
  x: 0.7, y: 1.2, w: 8.6, h: 1.4,
  fontSize: 38, fontFace: FONTS.face, color: "FFFFFF",
  bold: true, align: "left", valign: "top"
});

// Learning objective preview
slide.addText("Today: talk about what you did last weekend using past simple verbs", {
  x: 0.7, y: 2.7, w: 8.6, h: 0.6,
  fontSize: 20, fontFace: FONTS.face, color: "A0BBDD",
  align: "left"
});

// Thin accent rule
slide.addShape(pres.shapes.RECTANGLE, {
  x: 0.7, y: 3.5, w: 2.0, h: 0.04,
  fill: { color: COLORS.accent }, line: { color: COLORS.accent }
});

// Date and class info
slide.addText("Monday, 3 March 2026  ·  Period 3  ·  Class 9B", {
  x: 0.7, y: 3.65, w: 8.6, h: 0.5,
  fontSize: 16, fontFace: FONTS.face, color: "CADCFC",
  align: "left"
});
```

**Do not include:** Decorative images, animated elements, institution crests unless requested.

---

## 2. Learning Objective Slide

**Purpose:** "Today we will..." — give students a clear, measurable target.

```javascript
// Title
slide.addText("Today's Objective", {
  x: MARGIN, y: 0.2, w: 9.0, h: 0.7,
  fontSize: FONTS.title, fontFace: FONTS.face, color: COLORS.primary, bold: true
});

// Divider
slide.addShape(pres.shapes.RECTANGLE, {
  x: MARGIN, y: 0.9, w: 9.0, h: 0.025, fill: { color: COLORS.rule }
});

// Main objective in a callout box
slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
  x: 1.0, y: 1.2, w: 8.0, h: 1.4,
  fill: { color: COLORS.callout }, line: { color: COLORS.accent, pt: 1.5 }, rectRadius: 0.1
});

slide.addText("Today we will use the past simple tense to talk and write about things we did in the past.", {
  x: 1.2, y: 1.35, w: 7.6, h: 1.1,
  fontSize: FONTS.body, fontFace: FONTS.face, color: COLORS.primary,
  bold: true, align: "center", valign: "middle"
});

// Sub-objectives
slide.addText([
  { text: "By the end of this lesson, you can:", options: { bold: true, breakLine: true } },
  { text: "Form regular past simple verbs (add -ed)", options: { breakLine: true } },
  { text: "Use past simple in sentences about last weekend", options: { breakLine: true } },
  { text: "Ask and answer questions using 'Did you...?'", options: { breakLine: true } },
], {
  x: 1.0, y: 2.9, w: 8.0, h: 2.2,
  fontSize: FONTS.body, fontFace: FONTS.face, color: COLORS.body,
  bullet: true, paraSpaceAfter: 10
});
```

---

## 3. Warm-Up / Do Now Slide

**Purpose:** Quick opener to get students thinking in English. Connects to today's lesson.

```javascript
// Title
slide.addText("Warm-Up: What Did You Do Yesterday?", {
  x: MARGIN, y: 0.2, w: 9.0, h: 0.7,
  fontSize: FONTS.title, fontFace: FONTS.face, color: COLORS.primary, bold: true
});

// Divider
slide.addShape(pres.shapes.RECTANGLE, {
  x: MARGIN, y: 0.9, w: 9.0, h: 0.025, fill: { color: COLORS.rule }
});

// Prompt — large and engaging
slide.addText("Tell your partner THREE things you did yesterday.", {
  x: MARGIN, y: 1.2, w: 9.0, h: 0.8,
  fontSize: 28, fontFace: FONTS.face, color: COLORS.body,
  bold: true, align: "center"
});

// Sentence starters to scaffold
slide.addText("SENTENCE STARTERS", {
  x: MARGIN, y: 2.3, w: 9.0, h: 0.45,
  fontSize: 20, fontFace: FONTS.face, color: COLORS.accent, bold: true
});

slide.addText([
  { text: "Yesterday, I ____________.", options: { breakLine: true } },
  { text: "After school, I ____________.", options: { breakLine: true } },
  { text: "In the evening, I ____________.", options: { breakLine: true } },
], {
  x: 1.0, y: 2.8, w: 8.0, h: 2.0,
  fontSize: FONTS.body, fontFace: FONTS.face, color: COLORS.body,
  paraSpaceAfter: 12
});
```

---

## 4. Vocabulary Slide (Single Focus)

**Purpose:** Introduce one word with image, definition, and example. Image left, text right.

```javascript
// Title
slide.addText("Weather Vocabulary", {
  x: MARGIN, y: 0.2, w: 9.0, h: 0.6,
  fontSize: FONTS.title, fontFace: FONTS.face, color: COLORS.primary, bold: true
});

// Divider
slide.addShape(pres.shapes.RECTANGLE, {
  x: MARGIN, y: 0.8, w: 9.0, h: 0.025, fill: { color: COLORS.rule }
});

// IMAGE — left side (~40% of slide)
slide.addImage({
  path: "umbrella.png",
  x: MARGIN, y: 1.1, w: 3.8, h: 3.8,
  sizing: { type: "contain" }
});

// WORD — large, prominent
slide.addText("umbrella", {
  x: 4.8, y: 1.1, w: 4.7, h: 0.8,
  fontSize: FONTS.vocab, fontFace: FONTS.face, color: COLORS.primary,
  bold: true
});

// Part of speech
slide.addText("(noun)", {
  x: 4.8, y: 1.85, w: 4.7, h: 0.4,
  fontSize: 18, fontFace: FONTS.face, color: GRAMMAR.noun,  // Blue for nouns
  italics: true
});

// Definition
slide.addText("A thing you hold over your head to stay dry when it rains.", {
  x: 4.8, y: 2.3, w: 4.7, h: 0.8,
  fontSize: 22, fontFace: FONTS.face, color: COLORS.body
});

// Example sentence — with target word bolded
slide.addText([
  { text: "Example: ", options: { bold: true, color: COLORS.accent } },
  { text: "Don't forget your ", options: {} },
  { text: "umbrella", options: { bold: true } },
  { text: " — it's going to rain today!", options: {} },
], {
  x: 4.8, y: 3.2, w: 4.7, h: 0.8,
  fontSize: 22, fontFace: FONTS.face, color: COLORS.body
});
```

---

## 5. Vocabulary Slide (Grouped)

**Purpose:** Present 4–6 thematically grouped words. Good for review or when introducing a word set.

```javascript
// Title
slide.addText("Weather Vocabulary", {
  x: MARGIN, y: 0.2, w: 9.0, h: 0.6,
  fontSize: FONTS.title, fontFace: FONTS.face, color: COLORS.primary, bold: true
});

// Divider
slide.addShape(pres.shapes.RECTANGLE, {
  x: MARGIN, y: 0.8, w: 9.0, h: 0.025, fill: { color: COLORS.rule }
});

// Words arranged in a 2-column grid
// Left column
const words = [
  { word: "sunny", def: "bright, with lots of sun", y: 1.1 },
  { word: "cloudy", def: "covered with clouds, gray sky", y: 2.2 },
  { word: "rainy", def: "raining, wet weather", y: 3.3 },
];

const wordsRight = [
  { word: "windy", def: "strong wind blowing", y: 1.1 },
  { word: "snowy", def: "snow falling from the sky", y: 2.2 },
  { word: "foggy", def: "thick mist, hard to see far", y: 3.3 },
];

// Left column words
words.forEach(w => {
  // Image placeholder
  slide.addImage({ path: `${w.word}.png`, x: MARGIN, y: w.y, w: 0.9, h: 0.9, sizing: { type: "contain" } });
  // Word
  slide.addText(w.word, {
    x: 1.6, y: w.y, w: 2.5, h: 0.45,
    fontSize: 26, fontFace: FONTS.face, color: COLORS.primary, bold: true
  });
  // Definition
  slide.addText(w.def, {
    x: 1.6, y: w.y + 0.45, w: 3.0, h: 0.45,
    fontSize: 18, fontFace: FONTS.face, color: COLORS.body
  });
});

// Right column words
wordsRight.forEach(w => {
  slide.addImage({ path: `${w.word}.png`, x: 5.2, y: w.y, w: 0.9, h: 0.9, sizing: { type: "contain" } });
  slide.addText(w.word, {
    x: 6.3, y: w.y, w: 2.5, h: 0.45,
    fontSize: 26, fontFace: FONTS.face, color: COLORS.primary, bold: true
  });
  slide.addText(w.def, {
    x: 6.3, y: w.y + 0.45, w: 3.2, h: 0.45,
    fontSize: 18, fontFace: FONTS.face, color: COLORS.body
  });
});
```

**Note:** If six words with definitions and images won't fit at these sizes, reduce definition font to 16 pt or split across two slides. Content must fit.

---

## 6. Grammar Rule Slide

**Purpose:** Present a grammar rule clearly. Rule in a callout box, examples below with colour-coded grammar elements.

```javascript
// Title
slide.addText("Past Simple — Regular Verbs", {
  x: MARGIN, y: 0.2, w: 9.0, h: 0.6,
  fontSize: FONTS.title, fontFace: FONTS.face, color: COLORS.primary, bold: true
});

// Divider
slide.addShape(pres.shapes.RECTANGLE, {
  x: MARGIN, y: 0.8, w: 9.0, h: 0.025, fill: { color: COLORS.rule }
});

// RULE — in a highlighted callout box
slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
  x: 0.8, y: 1.0, w: 8.4, h: 1.0,
  fill: { color: COLORS.callout }, line: { color: COLORS.accent, pt: 1.5 }, rectRadius: 0.1
});

slide.addText([
  { text: "RULE: ", options: { bold: true, fontSize: 24 } },
  { text: "Add ", options: { fontSize: 24 } },
  { text: "-ed", options: { bold: true, color: GRAMMAR.verb, fontSize: 26 } },
  { text: " to the base form of the verb to make the past simple.", options: { fontSize: 24 } },
], {
  x: 1.0, y: 1.1, w: 8.0, h: 0.8,
  fontFace: FONTS.face, color: COLORS.primary,
  align: "center", valign: "middle"
});

// Examples section header
slide.addText("EXAMPLES", {
  x: MARGIN, y: 2.2, w: 9.0, h: 0.4,
  fontSize: 20, fontFace: FONTS.face, color: COLORS.accent, bold: true
});

// Examples with colour-coded verbs (red = verb)
slide.addText([
  { text: "I ", options: {} },
  { text: "walked", options: { color: GRAMMAR.verb, bold: true } },
  { text: " to school yesterday.", options: { breakLine: true } },
  { text: "She ", options: {} },
  { text: "played", options: { color: GRAMMAR.verb, bold: true } },
  { text: " football after class.", options: { breakLine: true } },
  { text: "We ", options: {} },
  { text: "watched", options: { color: GRAMMAR.verb, bold: true } },
  { text: " a film last night.", options: { breakLine: true } },
  { text: "They ", options: {} },
  { text: "listened", options: { color: GRAMMAR.verb, bold: true } },
  { text: " to music at the party.", options: { breakLine: true } },
], {
  x: 1.0, y: 2.65, w: 8.0, h: 2.6,
  fontSize: FONTS.body, fontFace: FONTS.face, color: COLORS.body,
  paraSpaceAfter: 14
});
```

---

## 7. Fill-in-the-Blank Exercise

**Purpose:** Controlled practice. Students complete sentences with the target language.

```javascript
// Title with instruction
slide.addText("Fill in the Blank — Use the Past Simple", {
  x: MARGIN, y: 0.2, w: 9.0, h: 0.6,
  fontSize: FONTS.title, fontFace: FONTS.face, color: COLORS.primary, bold: true
});

// Divider
slide.addShape(pres.shapes.RECTANGLE, {
  x: MARGIN, y: 0.8, w: 9.0, h: 0.025, fill: { color: COLORS.rule }
});

// Instruction
slide.addText("Write the correct past simple form of the verb in brackets.", {
  x: MARGIN, y: 0.9, w: 9.0, h: 0.5,
  fontSize: 22, fontFace: FONTS.face, color: COLORS.body, italics: true
});

// Exercise items
slide.addText([
  { text: "1. I __________ (walk) to school yesterday.", options: { breakLine: true } },
  { text: "2. She __________ (play) tennis after class.", options: { breakLine: true } },
  { text: "3. They __________ (watch) TV last night.", options: { breakLine: true } },
  { text: "4. We __________ (listen) to the teacher carefully.", options: { breakLine: true } },
  { text: "5. He __________ (clean) his room on Saturday.", options: { breakLine: true } },
], {
  x: 0.8, y: 1.5, w: 8.4, h: 3.0,
  fontSize: FONTS.exercise, fontFace: FONTS.face, color: COLORS.body,
  paraSpaceAfter: 12
});

// Word bank (optional — helpful for lower levels)
slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
  x: 0.8, y: 4.6, w: 8.4, h: 0.7,
  fill: { color: COLORS.highlight }, line: { color: "E6C800", pt: 1 }, rectRadius: 0.06
});

slide.addText("WORD BANK: walked  ·  played  ·  watched  ·  listened  ·  cleaned", {
  x: 1.0, y: 4.65, w: 8.0, h: 0.6,
  fontSize: 20, fontFace: FONTS.face, color: "5A4000", bold: true,
  align: "center", valign: "middle"
});
```

---

## 8. Matching Exercise

**Purpose:** Students match items from two columns (word to definition, question to answer, etc.).

```javascript
// Title with instruction
slide.addText("Match — Connect the Word to the Definition", {
  x: MARGIN, y: 0.2, w: 9.0, h: 0.6,
  fontSize: FONTS.title, fontFace: FONTS.face, color: COLORS.primary, bold: true
});

// Divider
slide.addShape(pres.shapes.RECTANGLE, {
  x: MARGIN, y: 0.8, w: 9.0, h: 0.025, fill: { color: COLORS.rule }
});

// Instruction
slide.addText("Draw a line from each word on the left to its meaning on the right.", {
  x: MARGIN, y: 0.9, w: 9.0, h: 0.45,
  fontSize: 20, fontFace: FONTS.face, color: COLORS.body, italics: true
});

// Left column header
slide.addText("Word", {
  x: 0.8, y: 1.45, w: 3.5, h: 0.4,
  fontSize: 22, fontFace: FONTS.face, color: COLORS.accent, bold: true
});

// Right column header
slide.addText("Definition", {
  x: 5.5, y: 1.45, w: 4.0, h: 0.4,
  fontSize: 22, fontFace: FONTS.face, color: COLORS.accent, bold: true
});

// Left column — words (numbered)
const leftItems = ["1. sunny", "2. foggy", "3. windy", "4. stormy"];
slide.addText(leftItems.map(item => ({
  text: item, options: { breakLine: true, bold: true }
})), {
  x: 0.8, y: 1.9, w: 3.5, h: 3.0,
  fontSize: FONTS.exercise, fontFace: FONTS.face, color: COLORS.body,
  paraSpaceAfter: 16
});

// Right column — definitions (lettered, shuffled order)
const rightItems = [
  "a) strong wind blowing hard",
  "b) bright sky with lots of sun",
  "c) thick mist, hard to see far",
  "d) thunder, lightning, heavy rain"
];
slide.addText(rightItems.map(item => ({
  text: item, options: { breakLine: true }
})), {
  x: 5.5, y: 1.9, w: 4.0, h: 3.0,
  fontSize: FONTS.exercise, fontFace: FONTS.face, color: COLORS.body,
  paraSpaceAfter: 16
});
```

---

## 9. Multiple Choice Exercise

**Purpose:** Students choose the correct answer from options.

```javascript
// Title with instruction
slide.addText("Choose the Correct Answer", {
  x: MARGIN, y: 0.2, w: 9.0, h: 0.6,
  fontSize: FONTS.title, fontFace: FONTS.face, color: COLORS.primary, bold: true
});

// Divider
slide.addShape(pres.shapes.RECTANGLE, {
  x: MARGIN, y: 0.8, w: 9.0, h: 0.025, fill: { color: COLORS.rule }
});

// Question
slide.addText("She __________ to the park yesterday.", {
  x: 0.8, y: 1.1, w: 8.4, h: 0.6,
  fontSize: 26, fontFace: FONTS.face, color: COLORS.body, bold: true
});

// Options — each in its own text box for clear separation
const options = [
  { label: "A)", text: "go", y: 2.0 },
  { label: "B)", text: "goes", y: 2.7 },
  { label: "C)", text: "went", y: 3.4 },
  { label: "D)", text: "going", y: 4.1 },
];

options.forEach(opt => {
  slide.addText([
    { text: opt.label + " ", options: { bold: true, color: COLORS.accent } },
    { text: opt.text, options: {} },
  ], {
    x: 1.5, y: opt.y, w: 7.0, h: 0.55,
    fontSize: FONTS.exercise, fontFace: FONTS.face, color: COLORS.body
  });
});
```

**For multiple questions per slide:** Stack questions vertically. Reduce font size if needed to fit — content must not overflow. If more than 2 questions with 4 options each, split across slides.

---

## 10. Error Correction Exercise

**Purpose:** Students identify and fix mistakes in sentences. Builds accuracy and attention to form.

```javascript
// Title with instruction
slide.addText("Find and Fix the Mistakes", {
  x: MARGIN, y: 0.2, w: 9.0, h: 0.6,
  fontSize: FONTS.title, fontFace: FONTS.face, color: COLORS.primary, bold: true
});

// Divider
slide.addShape(pres.shapes.RECTANGLE, {
  x: MARGIN, y: 0.8, w: 9.0, h: 0.025, fill: { color: COLORS.rule }
});

// Instruction
slide.addText("Each sentence has ONE mistake. Find it and write the correct sentence.", {
  x: MARGIN, y: 0.9, w: 9.0, h: 0.5,
  fontSize: 20, fontFace: FONTS.face, color: COLORS.body, italics: true
});

// Incorrect sentences — errors are shown as-is (students must find them)
slide.addText([
  { text: "1. She walkd to school yesterday.", options: { breakLine: true } },
  { text: "2. I did not played football last week.", options: { breakLine: true } },
  { text: "3. They was very happy at the party.", options: { breakLine: true } },
  { text: "4. He cleanned his room on Saturday.", options: { breakLine: true } },
  { text: "5. We didn't went to the cinema.", options: { breakLine: true } },
], {
  x: 0.8, y: 1.5, w: 8.4, h: 3.2,
  fontSize: FONTS.exercise, fontFace: FONTS.face, color: COLORS.body,
  paraSpaceAfter: 14
});

// Hint box (optional — for lower levels)
slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
  x: 0.8, y: 4.8, w: 8.4, h: 0.6,
  fill: { color: COLORS.callout }, line: { color: COLORS.accent, pt: 1 }, rectRadius: 0.06
});

slide.addText("HINT: Look for spelling, verb form, and auxiliary verb errors.", {
  x: 1.0, y: 4.85, w: 8.0, h: 0.5,
  fontSize: 18, fontFace: FONTS.face, color: COLORS.accent,
  align: "center", valign: "middle", italics: true
});
```

---

## 11. Sentence Frame / Model Dialogue

**Purpose:** Provide structured language frames students can use. Blanks are highlighted; word bank or prompts support production.

```javascript
// Title
slide.addText("Talking About Last Weekend", {
  x: MARGIN, y: 0.2, w: 9.0, h: 0.6,
  fontSize: FONTS.title, fontFace: FONTS.face, color: COLORS.primary, bold: true
});

// Divider
slide.addShape(pres.shapes.RECTANGLE, {
  x: MARGIN, y: 0.8, w: 9.0, h: 0.025, fill: { color: COLORS.rule }
});

// Instruction
slide.addText("Use these sentence frames to tell your partner about your weekend.", {
  x: MARGIN, y: 0.9, w: 9.0, h: 0.45,
  fontSize: 20, fontFace: FONTS.face, color: COLORS.body, italics: true
});

// Sentence frames — blanks highlighted with underline and accent colour
slide.addText([
  { text: "On Saturday, I ", options: {} },
  { text: "______________", options: { color: COLORS.accent, bold: true } },
  { text: " with my ", options: {} },
  { text: "______________", options: { color: COLORS.accent, bold: true } },
  { text: ".", options: { breakLine: true } },
  { text: "", options: { breakLine: true } },
  { text: "It was really ", options: {} },
  { text: "______________", options: { color: COLORS.accent, bold: true } },
  { text: " because ", options: {} },
  { text: "______________", options: { color: COLORS.accent, bold: true } },
  { text: ".", options: { breakLine: true } },
  { text: "", options: { breakLine: true } },
  { text: "On Sunday, I didn't ", options: {} },
  { text: "______________", options: { color: COLORS.accent, bold: true } },
  { text: ". Instead, I ", options: {} },
  { text: "______________", options: { color: COLORS.accent, bold: true } },
  { text: ".", options: { breakLine: true } },
], {
  x: 0.8, y: 1.4, w: 8.4, h: 2.2,
  fontSize: FONTS.body, fontFace: FONTS.face, color: COLORS.body,
  paraSpaceAfter: 8
});

// Word bank / prompt ideas
slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
  x: 0.8, y: 3.8, w: 8.4, h: 1.4,
  fill: { color: COLORS.highlight }, line: { color: "E6C800", pt: 1 }, rectRadius: 0.06
});

slide.addText("IDEAS", {
  x: 1.0, y: 3.85, w: 8.0, h: 0.35,
  fontSize: 18, fontFace: FONTS.face, color: "5A4000", bold: true
});

slide.addText("played football  ·  watched a film  ·  visited my grandmother  ·  cooked dinner  ·  stayed home  ·  went shopping  ·  fun  ·  boring  ·  exciting  ·  relaxing", {
  x: 1.0, y: 4.2, w: 8.0, h: 0.85,
  fontSize: 18, fontFace: FONTS.face, color: "5A4000",
  align: "center", valign: "top"
});
```

---

## 12. Discussion Prompt Slide

**Purpose:** Set up pair/group discussion with a prompt and sentence starters.

```javascript
// Title
slide.addText("Pair Discussion — What Did You Do Last Weekend?", {
  x: MARGIN, y: 0.2, w: 9.0, h: 0.6,
  fontSize: FONTS.title, fontFace: FONTS.face, color: COLORS.primary, bold: true
});

// Divider
slide.addShape(pres.shapes.RECTANGLE, {
  x: MARGIN, y: 0.8, w: 9.0, h: 0.025, fill: { color: COLORS.rule }
});

// Activity instruction
slide.addText([
  { text: "With your partner: ", options: { bold: true } },
  { text: "Ask and answer these questions. Use FULL SENTENCES.", options: {} },
], {
  x: MARGIN, y: 1.0, w: 9.0, h: 0.5,
  fontSize: 22, fontFace: FONTS.face, color: COLORS.body
});

// Discussion questions
slide.addText([
  { text: "1. What did you do on Saturday?", options: { breakLine: true } },
  { text: "2. Did you go anywhere special?", options: { breakLine: true } },
  { text: "3. What was the best part of your weekend?", options: { breakLine: true } },
], {
  x: 0.8, y: 1.7, w: 8.4, h: 1.6,
  fontSize: FONTS.body, fontFace: FONTS.face, color: COLORS.body,
  paraSpaceAfter: 12
});

// Sentence starters
slide.addText("SENTENCE STARTERS", {
  x: MARGIN, y: 3.4, w: 9.0, h: 0.4,
  fontSize: 20, fontFace: FONTS.face, color: COLORS.accent, bold: true
});

slide.addText([
  { text: "\"On Saturday, I ...\"", options: { breakLine: true } },
  { text: "\"Yes, I went to ... / No, I stayed ...\"", options: { breakLine: true } },
  { text: "\"The best part was ... because ...\"", options: { breakLine: true } },
], {
  x: 1.0, y: 3.8, w: 8.0, h: 1.5,
  fontSize: 22, fontFace: FONTS.face, color: COLORS.body,
  italics: true, paraSpaceAfter: 8
});
```

---

## 13. Comparison Table Slide

**Purpose:** Side-by-side comparison of grammar forms, vocabulary categories, or other paired concepts.

```javascript
// Title
slide.addText("Present Simple vs. Present Continuous", {
  x: MARGIN, y: 0.2, w: 9.0, h: 0.6,
  fontSize: FONTS.title, fontFace: FONTS.face, color: COLORS.primary, bold: true
});

// Divider
slide.addShape(pres.shapes.RECTANGLE, {
  x: MARGIN, y: 0.8, w: 9.0, h: 0.025, fill: { color: COLORS.rule }
});

// Table
const tableRows = [
  [
    { text: "", options: { bold: true, fill: { color: COLORS.primary }, color: "FFFFFF", fontSize: 20 } },
    { text: "Present Simple", options: { bold: true, fill: { color: COLORS.primary }, color: "FFFFFF", fontSize: 20 } },
    { text: "Present Continuous", options: { bold: true, fill: { color: COLORS.primary }, color: "FFFFFF", fontSize: 20 } },
  ],
  [
    { text: "Form", options: { bold: true, fontSize: 20 } },
    { text: "subject + base verb\n(he/she/it + verb-s)", options: { fontSize: 20 } },
    { text: "subject + am/is/are + verb-ing", options: { fontSize: 20 } },
  ],
  [
    { text: "Use", options: { bold: true, fontSize: 20 } },
    { text: "habits, routines,\ngeneral truths", options: { fontSize: 20 } },
    { text: "actions happening\nright now", options: { fontSize: 20 } },
  ],
  [
    { text: "Signal words", options: { bold: true, fontSize: 20 } },
    { text: "always, usually,\nevery day, often", options: { fontSize: 20 } },
    { text: "now, right now,\nat the moment, today", options: { fontSize: 20 } },
  ],
  [
    { text: "Example", options: { bold: true, fontSize: 20 } },
    { text: "I play football\nevery Saturday.", options: { fontSize: 20 } },
    { text: "I am playing football\nright now.", options: { fontSize: 20 } },
  ],
];

slide.addTable(tableRows, {
  x: 0.5, y: 1.0, w: 9.0,
  colW: [1.5, 3.75, 3.75],
  border: { color: COLORS.rule, pt: 1 },
  rowH: [0.5, 0.7, 0.7, 0.7, 0.7],
  fontFace: FONTS.face,
  color: COLORS.body,
  valign: "middle",
  margin: [4, 8, 4, 8],
});
```

**Note:** Adjust `rowH` and `fontSize` if content is longer. Tables with many rows may need smaller text — content must fit.

---

## 14. Reading / Listening Text Slide

**Purpose:** Display a passage for reading comprehension or a transcript for listening activities. Font shrinks as needed to fit.

```javascript
// Title
slide.addText("Read the Text — Holiday Email", {
  x: MARGIN, y: 0.2, w: 9.0, h: 0.6,
  fontSize: FONTS.title, fontFace: FONTS.face, color: COLORS.primary, bold: true
});

// Divider
slide.addShape(pres.shapes.RECTANGLE, {
  x: MARGIN, y: 0.8, w: 9.0, h: 0.025, fill: { color: COLORS.rule }
});

// Reading focus instruction
slide.addText("Read the email. Underline all past simple verbs.", {
  x: MARGIN, y: 0.9, w: 9.0, h: 0.4,
  fontSize: 20, fontFace: FONTS.face, color: COLORS.accent, bold: true
});

// Text passage — in a lightly bordered box
slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
  x: 0.6, y: 1.4, w: 8.8, h: 3.8,
  fill: { color: "FAFAFA" }, line: { color: COLORS.rule, pt: 1 }, rectRadius: 0.08
});

// Passage text — font size adapts to content length
// For short passages: 22-24 pt. For longer passages: reduce to 18-20 pt.
// The overriding rule: all text must fit without overflow.
slide.addText(
  "Hi Maria!\n\n" +
  "I arrived in London last Tuesday. On Wednesday, I visited the British Museum " +
  "and walked along the Thames. It was really beautiful! On Thursday, I tried " +
  "fish and chips for the first time — I loved it!\n\n" +
  "Yesterday, I shopped at Camden Market and bought some souvenirs. " +
  "Tomorrow I want to see Buckingham Palace.\n\n" +
  "See you next week!\nAnna", {
  x: 0.8, y: 1.55, w: 8.4, h: 3.5,
  fontSize: 20, fontFace: FONTS.face, color: COLORS.body,
  valign: "top", paraSpaceAfter: 6
});
```

**Critical:** Reading passages are the most common case where the overriding fit rule applies. Shrink font to fit the full text. If the passage is too long for one slide even at 16 pt, split across slides with clear "continued" labels.

---

## 15. Review / Wrap-Up Slide

**Purpose:** Summarise key takeaways. This is the LAST content slide — stays on screen as students pack up.

```javascript
// Dark background — mirrors title slide (bookend structure)
slide.background = { color: COLORS.primary };

// "What We Learned Today" label
slide.addText("What We Learned Today", {
  x: MARGIN, y: 0.25, w: 9.0, h: 0.5,
  fontSize: 24, fontFace: FONTS.face, color: "A0BBDD", bold: true, align: "left"
});

// Accent rule
slide.addShape(pres.shapes.RECTANGLE, {
  x: MARGIN, y: 0.8, w: 9.0, h: 0.04, fill: { color: COLORS.accent }
});

// Key takeaways
slide.addText([
  { text: "1. Past simple regular verbs: ", options: { bold: true, breakLine: false } },
  { text: "add -ed to the base form (walk → walked, play → played)", options: { breakLine: true, breakLine: true } },
  { text: "2. Negative: ", options: { bold: true, breakLine: false } },
  { text: "didn't + base form (She didn't walk — NOT She didn't walked)", options: { breakLine: true, breakLine: true } },
  { text: "3. Questions: ", options: { bold: true, breakLine: false } },
  { text: "Did + subject + base form (Did you play? — NOT Did you played?)", options: { breakLine: true } },
], {
  x: MARGIN, y: 1.0, w: 9.0, h: 2.8,
  fontSize: 22, fontFace: FONTS.face, color: "FFFFFF",
  paraSpaceAfter: 18
});

// Homework
slide.addText("HOMEWORK", {
  x: MARGIN, y: 3.9, w: 9.0, h: 0.4,
  fontSize: 20, fontFace: FONTS.face, color: "A0BBDD", bold: true
});

slide.addText("Workbook page 34, exercises 1–3. Write 5 sentences about your last holiday using past simple.", {
  x: MARGIN, y: 4.3, w: 9.0, h: 0.8,
  fontSize: 20, fontFace: FONTS.face, color: "CADCFC"
});
```

**Do not follow this slide** with "Goodbye", a blank slide, or any other slide. This stays on screen.

---

## 16. Section Divider

**Purpose:** Orient students when the lesson moves to a new phase. Use for decks > 15 slides.

```javascript
// Dark treatment
slide.background = { color: "1A3A5C" };

// Phase label
slide.addText("Practice", {
  x: MARGIN, y: 1.8, w: 9.0, h: 0.4,
  fontSize: 16, fontFace: FONTS.face, color: "7BAFD4", bold: false, align: "left"
});

// Section title
slide.addText("Time to Practise!", {
  x: MARGIN, y: 2.2, w: 9.0, h: 1.0,
  fontSize: 36, fontFace: FONTS.face, color: "FFFFFF", bold: true, align: "left"
});

// Accent rule
slide.addShape(pres.shapes.RECTANGLE, {
  x: MARGIN, y: 3.3, w: 2.5, h: 0.06, fill: { color: COLORS.accent }
});
```

---

## 17. Breadcrumb Bar (optional, for longer lessons)

A persistent header strip showing the current lesson phase. Add to every content slide for decks > 15 slides.

```javascript
const phases = ["Warm-Up", "New Language", "Practice", "Production", "Review"];
const currentPhase = "Practice";  // Changes per slide

const barY = 0.0;
const barH = 0.28;

// Background bar
slide.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: barY, w: 10, h: barH,
  fill: { color: "F0F4F8" }, line: { color: "F0F4F8" }
});

// Phase labels
const phaseW = 10 / phases.length;
phases.forEach((phase, i) => {
  const isActive = phase === currentPhase;
  slide.addText(phase, {
    x: i * phaseW, y: barY, w: phaseW, h: barH,
    fontSize: 10, fontFace: FONTS.face,
    color: isActive ? COLORS.accent : COLORS.muted,
    bold: isActive,
    align: "center", valign: "middle"
  });
  if (isActive) {
    slide.addShape(pres.shapes.RECTANGLE, {
      x: i * phaseW + phaseW * 0.1, y: barY + barH - 0.04, w: phaseW * 0.8, h: 0.04,
      fill: { color: COLORS.accent }
    });
  }
});

// Shift all other content down by barH to avoid collision
```

---

## Quick Checks Before Use

```
□ Title slide: lesson topic, date, learning objective, class info
□ Every slide: clear purpose title
□ Lesson flow test: titles tell the progression from warm-up → input → practice → production → review
□ Exercise slides: written instructions present
□ Vocabulary slides: image + word + definition + example sentence
□ Grammar slides: rule in callout box, colour-coded examples
□ Grammar colours: consistent throughout (verbs = red, nouns = blue, etc.)
□ Text enhancements: bold/italic/underline/caps used per §5 conventions consistently
□ Content fits: no text overflows any slide
□ Font sizes: target ≥ 24 pt body, reduced only when content requires it
□ Word banks: included on exercise slides for A1–A2 levels
□ Wrap-up slide: last content slide, key takeaways + homework
□ No decorative images — every image supports learning
```
