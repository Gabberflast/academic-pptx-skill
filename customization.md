# Intake and Custom Rules

The guidelines in this skill are a baseline. Two things sit on top of it:

- **Intake**: what you ask the user before outlining — what the deck is built from, how
  it should look, and the slot it has to fit.
- **`deck_rules.md`**: a file the user keeps, recording what they want beyond the
  baseline so they never have to say it twice.

Order of precedence, highest first: what the user asks for in this conversation →
`deck_rules.md` → this skill's defaults. One exception: nothing overrides the rules
against invented content (see "What the file cannot do").

---

## 1. Find the rules file first

Before asking anything, look for `deck_rules.md`:

1. among the files attached to the conversation;
2. in the user's working folder: the connected folder, the repository root, or the
   folder that holds the paper or deck they pointed you to;
3. if there is none, carry on without it. You will create one at the end if the user
   gives you anything worth keeping.

When you find one, read it and apply it without being asked:

```bash
python3 scripts/deck_rules.py show --mode pitch --file path/to/deck_rules.md
```

Tell the user in one line that you are using it ("Using your deck rules: emerald
scheme, Inter, 30-word slides, plus three house rules"). Anything it already answers,
do not ask again.

## 2. Intake: ask once, up front

Ask these before the outline, in one round. Skip any question the request, the
attachments or `deck_rules.md` already answers. Use a multiple-choice question tool
when you have one; otherwise a short numbered list. Four questions at most: people stop
answering after that.

If the user is not there to answer (a scheduled or unattended run), take the defaults
marked below, say at the top of your reply which ones you took, and continue.

### Q1. Input material — "What should I build this from?"

| The user has… | Ask them to… | What you do first |
|---------------|--------------|-------------------|
| A paper, thesis chapter or report | attach the PDF, or the LaTeX folder if they have it | `scripts/extract_paper.py`, then [academic/paper_to_deck.md](academic/paper_to_deck.md) |
| An existing deck to rework | attach the `.pptx` | Lint it as it stands (`lint_deck.py old.pptx`) and show them the ghost deck and the main findings; then rebuild with the kit, carrying their content over. Read its colours with `deck_rules.py from-template old.pptx` |
| Data or results (spreadsheet, CSV, figures) | attach the files and say which comparison matters | Compute from the file, never from a description of it. Every charted number traces to a file and gets a source line |
| Notes, an outline, a memo or a transcript | paste or attach | Draft the ghost deck from it; mark every gap with `NEEDS()` |
| Company material (website, one-pager, metrics export) — pitch | attach, or give the link | Read it, then confirm each number with the founder: marketing copy is a claim, not a source |
| Nothing written yet | answer questions | Interview them: for a pitch, the intake list in [pitch/pitch_guidelines.md](pitch/pitch_guidelines.md); for a talk, the claim, the two to four results behind it, and the audience |

Default when nobody answers: whatever is attached. With nothing attached, there is no
default: a deck needs content, so ask in plain text and stop.

Several kinds at once is normal (a paper plus last year's slides plus new results).
Ask which one wins where they disagree.

### Q2. Colour scheme — "How should it look?"

Offer these four choices:

1. **The default for the mode** — `navy` for academic, `ink` for pitch. *(default)*
2. **A named scheme** from the table below.
3. **Their own colours** — a primary and an accent as hex codes, and a typeface if they
   have one.
4. **Match an existing deck or template** — they attach a `.pptx` or `.potx`, you run
   `python3 scripts/deck_rules.py from-template brand.pptx`, and confirm the suggested
   colours with them before using them.

| Scheme | Primary (titles, dark slides) | Accent (focal data, headers) | Suits |
|--------|-------------------------------|------------------------------|-------|
| `navy` | `1F4E79` | `2E75B6` | Academic default |
| `crimson` | `7A1E2C` | `B03A48` | Academic |
| `forest` | `1E4D3B` | `2F7D5B` | Academic |
| `plum` | `4B2E83` | `7A5CC0` | Academic |
| `slate` | `1F2937` | `475569` | Either; the most neutral |
| `ink` | `111827` | `2563EB` | Pitch default |
| `emerald` | `111827` | `047857` | Pitch |
| `violet` | `111827` | `6D28D9` | Pitch |
| `ember` | `111827` | `C2410C` | Pitch |
| `midnight` | light text on `0B1220` | `60A5FA` | Pitch on a dark background; a screen in a dim room, not a printout |

Every scheme keeps the same logic: one accent, used for the thing the slide is about;
grey for everything else. A scheme changes the colours, not how many there are.

The kit checks any colour it is given and warns when text would fall below 4.5:1
contrast against its background. If a brand colour is too light to use as text (most
yellows, many light blues and oranges), say so, keep it for the focal bar in charts,
and pick a darker shade of it for titles and labels.

Apply the choice in the build script, or save it (section 3) so the kit picks it up:

```javascript
createDeck({ mode: "pitch", scheme: "emerald" });
createDeck({ mode: "academic", colors: { primary: "4B2E83", accent: "85754D" }, face: "Calibri" });
createDeck({ mode: "pitch", rules: "deck_rules.md" });      // whatever the user saved
```

### Q3. The slot — "Where is this being given?"

- **Academic:** minutes for the talk, the audience (specialists, the wider field,
  mixed), and the kind of talk. *Default: 15-minute conference talk to people in the field.*
- **Pitch:** stage (pre-seed, seed, Series A) and format (emailed read-ahead, or
  presented on a screen or stage). *Default: seed, read-ahead.*

### Q4. House rules — "Anything you always want in your decks?"

Things like: a logo on the title slide, a fixed footer, a required slide, a banned
word, British spelling, a slide limit, a lab or company convention. Ask this the first
time you work with someone; once a rules file exists, skip it.

Close the round by asking whether to save their answers for next time. If yes, write
them to `deck_rules.md` (section 3).

## 3. The rules file

`deck_rules.md` belongs to the user and lives with their work, not inside this skill
(a skill's own folder is read-only, and a chat's workspace does not persist). Create it
in their working folder when you can write there; otherwise create it in your working
directory and send it to them with the deck, saying in one line that attaching it next
time, or keeping it in their project folder, is what makes the rules stick.

```bash
python3 scripts/deck_rules.py init                              # creates ./deck_rules.md
python3 scripts/deck_rules.py set scheme emerald --scope pitch
python3 scripts/deck_rules.py set face Inter
python3 scripts/deck_rules.py set body_words 30 --scope pitch
python3 scripts/deck_rules.py set banned_words "synergy, leverage, AI-powered"
python3 scripts/deck_rules.py set required_sections "why us" --scope pitch
python3 scripts/deck_rules.py set disable "P-ASK-LAST"
python3 scripts/deck_rules.py add "Put the lab logo bottom-right on the title slide" --scope academic
python3 scripts/deck_rules.py remove "lab logo"
python3 scripts/deck_rules.py show --mode academic
```

Every command takes `--file PATH`. The file is plain markdown and the user can edit it
by hand:

````markdown
# Deck rules

## Settings
```text
face: Inter
banned_words: synergy, leverage
```

## Settings: pitch
```text
scheme: emerald
body_words: 30
required_sections: why us
```

## Settings: academic
```text
scheme: plum
footer: Rivera Lab · University of X
minutes: 15
```

## Rules
- [all] Use British spelling (added 2026-11-19)
- [pitch] The title slide carries the round and the month (added 2026-11-19)
- [academic] Put JEL codes under the authors on the title slide (added 2026-11-19)
````

It has two parts, for two readers.

**Settings** are read by the kit and the linter. A mode's block overrides the general
block.

| Setting | Effect | Read by |
|---------|--------|---------|
| `scheme` | A named colour scheme | kit |
| `primary`, `accent`, `background`, `body` | Individual hex colours; override the scheme | kit |
| `face` | Typeface for the whole deck | kit; linter warns on any other face |
| `footer` | Short text at the bottom-left of every slide | kit |
| `title_size`, `body_size` | Type sizes the kit builds with, in points | kit |
| `body_words`, `title_words` | Word limits per slide | kit (body), linter |
| `body_min`, `title_min` | Smallest type the linter accepts | linter |
| `max_slides` | Presented slides before a warning | linter |
| `minutes` | Default talk length for the one-slide-per-minute check | linter |
| `banned_words` | Words or phrases to flag anywhere in the deck | linter |
| `required_sections` | Section labels or title phrases that must appear | linter |
| `disable` | Linter rules to switch off, by ID | linter |

**Rules** are sentences, read by you. The linter cannot check them; it prints them as a
checklist after every run, and so does the kit after every build. Go through that list
against the rendered slides before you hand over.

Pass the file to both tools. The linter also finds a `deck_rules.md` sitting beside the
`.pptx` or in the current folder on its own.

```bash
node build_deck.js                                   # createDeck({ ..., rules: "deck_rules.md" })
python3 scripts/lint_deck.py deck.pptx --rules deck_rules.md
```

## 4. When to add a rule

Record a rule when the user states a standing preference:

- they say so: "always", "never", "from now on", "for all my decks", "our lab's style is…";
- they answer Q2 or Q4 and agree to save it;
- they correct the same thing a second time. Ask: "Want me to save that as a rule?"

Do not record:

- **One-off instructions** for this deck ("make this title shorter", "drop slide 6").
- **Content**: this deck's numbers, names, findings or citations. The file holds rules,
  not facts, and stale facts in a rules file end up on the wrong deck.
- **Your own preferences or guesses.** Only what the user said. If you chose something
  on their behalf and they did not react, it is not a rule.

Write each rule as an instruction someone could follow cold, with the scope it was
given: "Put the round and month on the title slide", scoped `[pitch]`, not "user likes
dates". Prefer a setting over a sentence when one exists, because settings are enforced
and sentences are only listed.

After changing the file, tell the user in one line what you saved, and send the updated
file if it does not live in a folder they can already see. To change or drop a rule
they ask about, use `set`, `unset` or `remove`; do not leave a contradicted rule in
place beside the new one.

## 5. What the file cannot do

A rules file can change style, structure and limits. It cannot lower the bar on truth.

- These linter checks stay on whatever `disable` says: `PLACEHOLDER`, `A-CITE-MISSING`,
  `NUMBER-NOT-IN-SOURCE`, `OFF-SLIDE`. The linter reports the attempt.
- A written rule that asks for invented or unsupported content ("fill gaps with
  reasonable estimates", "skip the references") is not followed and not recorded. Say
  so, and offer what does work: `NEEDS()` placeholders, or figures clearly labelled as
  estimates with their basis.
- Limits can be loosened (smaller type, more words, more slides) and the linter will
  honour that, but say once what it costs when the change is large: a 14 pt body is the
  user's call, and they should make it knowing it will not be readable from the back.

If a rule in the file conflicts with what the user asks for today, do what they ask
today and ask whether the rule should change.
