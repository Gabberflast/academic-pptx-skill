#!/usr/bin/env python3
"""
lint_deck.py — check a finished .pptx against the academic or pitch rules.

    python3 scripts/lint_deck.py talk.pptx --mode academic --minutes 15
    python3 scripts/lint_deck.py talk.pptx --mode academic --source paper_out/paper.json
    python3 scripts/lint_deck.py deck.pptx --mode pitch
    python3 scripts/lint_deck.py deck.pptx --rules deck_rules.md   # the user's own rules
    python3 scripts/lint_deck.py deck.pptx --ghost          # titles only
    python3 scripts/lint_deck.py deck.pptx --json

Exit status: 0 = no errors, 1 = errors (or warnings with --strict), 2 = could not read the file.

What it can check: form. Titles that are topic labels, overfull slides, small
type, low contrast, missing slides, citations with no reference, numbers that
are not in the source paper, unfilled placeholders, text running off the slide.

What it cannot check: whether the argument is right. It prints the ghost deck
(the titles in order) so that a reader can judge that part.

Works best on decks built with scripts/deck_kit.js, whose text boxes are named
(dk-title, dk-body, dk-cite, ...). On any other .pptx it falls back to
position and size heuristics, so expect a few misclassified boxes there.

A deck_rules.md beside the .pptx or in the current folder is picked up
automatically (see scripts/deck_rules.py); --no-rules ignores it. It can change
limits, add banned words and required sections, and switch checks off, except
the ones that guard against invented content.

Requires: python-pptx
"""

import argparse
import json
import math
import re
import subprocess
import sys
from pathlib import Path

try:
    from pptx import Presentation
    from pptx.enum.shapes import MSO_SHAPE_TYPE, PP_PLACEHOLDER
    from pptx.util import Emu
except ImportError:  # pragma: no cover
    sys.stderr.write("lint_deck.py needs python-pptx:  pip install python-pptx\n")
    sys.exit(2)

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from deck_rules import find_rules, load_rules
except ImportError:  # the linter still works alone, without custom rules
    find_rules = load_rules = None

EMU_IN = 914400.0

# ---------------------------------------------------------------- vocab

TOPIC_LABELS = {
    "introduction", "intro", "background", "motivation", "context", "overview", "outline", "agenda",
    "literature review", "related work", "prior work", "data", "dataset", "methods", "method",
    "methodology", "approach", "model", "empirical strategy", "identification", "results",
    "main results", "findings", "analysis", "discussion", "implications", "limitations",
    "robustness", "robustness checks", "future work", "next steps", "summary", "conclusion",
    "conclusions", "problem", "the problem", "solution", "the solution", "product", "demo",
    "how it works", "traction", "growth", "metrics", "market", "market size", "opportunity",
    "the opportunity", "business model", "pricing", "competition", "competitors", "landscape",
    "go to market", "go-to-market", "team", "the team", "our team", "ask", "the ask", "financials",
    "roadmap", "vision", "why now", "why us",
}

AUX = set("is are was were be been being has have had do does did can could will would should "
          "may might must cannot can't won't doesn't don't didn't isn't aren't wasn't weren't".split())

_VERB_BASES = (
    "raise rise fall increase decrease reduce improve grow show find suggest explain predict cause "
    "drive lead make give take need lose win pay cost save cut double triple outperform beat exceed "
    "persist remain stay hold depend vary differ match support confirm reject fail pass work solve "
    "replace remove add enable allow let require use reach hit cover exploit identify estimate "
    "measure track follow open close start stop begin end turn become get go come run scale sell "
    "buy want ask answer test compare converge diverge dominate account carry yield produce "
    "generate create build ship file chase serve charge earn spend return own know think see leave "
    "keep bring put set appear seem matter last fade shrink expand concentrate extend generalize "
    "apply imply mean indicate demonstrate reveal prove provide offer deliver handle force accept "
    "choose prefer forecast underperform lag move shift change affect help hurt protect prevent "
    "limit constrain correlate respond react adopt switch churn retain convert sign disappear "
    "emerge decline rebound recover stall accelerate slow narrow widen close peak fund back "
    "capture unlock link learn train eliminate lower lift boost halve trail offset survive reverse "
    "arise stem rest hinge rely give lack contain include exclude span combine separate isolate "
    "recover treat assign randomize graduate gain love like trust hate wait waste struggle "
    "spend rely prefer demand complain abandon renew expand refer recommend process automate "
    "connect reconcile underwrite lend borrow invest hire"
).split()
_IRREGULAR = ("grew grown fell fallen rose risen lost won paid made gave took taken found led held "
              "kept left built sold bought went gone came ran became got saw seen knew thought "
              "brought shown meant spent began begun drove driven chose chosen gave given").split()


def _inflect(base):
    out = {base, base + "s", base + "ed"}
    if base.endswith("e"):
        out |= {base + "d"}
    if base.endswith(("s", "sh", "ch", "x", "z")):
        out |= {base + "es"}
    if base.endswith("y") and base[-2:-1] not in "aeiou":
        out |= {base[:-1] + "ies", base[:-1] + "ied"}
    return out


VERBS = set(_IRREGULAR)
for _b in _VERB_BASES:
    VERBS |= _inflect(_b)

BUZZWORDS = [
    "revolutionary", "revolutionize", "disruptive", "disrupt", "game-changing", "game changer",
    "world-class", "best-in-class", "best in class", "cutting-edge", "cutting edge",
    "next-generation", "next generation", "state-of-the-art", "synergy", "synergies", "paradigm",
    "seamless", "seamlessly", "innovative", "groundbreaking", "unparalleled", "industry-leading",
    "leading provider", "one-stop", "holistic", "turnkey", "robust solution", "ai-powered",
    "unique", "massive market", "huge market",
]

PITCH_SECTIONS = {
    "problem": ["problem", "pain"],
    "solution": ["solution", "product", "how it works", "what we do"],
    "traction": ["traction", "growth", "metrics", "momentum", "revenue", "users", "customers"],
    "why now": ["why now", "insight", "why it works", "timing", "secret"],
    "market": ["market", "opportunity", "tam"],
    "business model": ["business model", "model", "pricing", "how we make money", "unit economics"],
    "competition": ["competition", "competitors", "alternatives", "landscape", "why we win"],
    "team": ["team", "founders", "who we are"],
    "ask": ["ask", "the ask", "raise", "raising", "round", "funding", "use of funds"],
    "vision": ["vision", "future", "where this goes"],
}

NOT_SURNAMES = set(
    "January February March April May June July August September October November December Jan Feb "
    "Mar Apr Jun Jul Aug Sep Sept Oct Nov Dec Spring Summer Fall Autumn Winter Conference Workshop "
    "Symposium Meeting Seminar Congress University Institute Appendix Figure Fig Table Panel "
    "Section Chapter In Since By Until From During After Before Through Between Around Circa Early "
    "Late Mid Year Grade Class Series Version Copyright Wave Round Cohort Census Survey Q1 Q2 Q3 Q4 "
    "FY Act Data Source Sources The And Of For".split())

FLOORS = {  # group: (error below, warn below), in points
    "academic": {"title": (20, 22), "body": (18, 20), "secondary": (14, 16), "fine": (12, 12)},
    "pitch": {"title": (24, 28), "body": (18, 22), "secondary": (14, 16), "fine": (12, 12)},
}
WORD_LIMITS = {"academic": (40, 60), "pitch": (25, 40)}   # (warn above, error above)
TITLE_WORDS = {"academic": 20, "pitch": 14}

ROLE_GROUP = {
    "title": "title", "body": "body", "question": "body", "header": "body",
    "tile": "secondary", "member": "secondary", "annot": "secondary", "support": "secondary",
    "hero": None, "company": None,
    "cite": "fine", "footer": "fine", "kicker": "fine", "breadcrumb": "fine", "contact": "fine",
    "refs": "fine", "venue": "fine", "authors": "fine", "slidenum": None,
}
BODY_ROLES = {"body", "question", "header", "tile", "member", "support"}

# ---------------------------------------------------------------- model


class Text:
    def __init__(self):
        self.name = ""
        self.role = ""
        self.x = self.y = self.w = self.h = 0.0
        self.text = ""
        self.paras = []          # [(text, max_pt or None, bold)]
        self.sizes = []          # explicit run sizes in pt
        self.unknown_sizes = 0
        self.fonts = set()
        self.colors = set()
        self.fill = None         # solid fill hex of the shape itself
        self.autofit = False

    @property
    def words(self):
        if self.role == "member":   # name and role lines are labels, not reading text
            return sum(len(p[0].split()) for p in self.paras[2:])
        return len(self.text.split())

    @property
    def min_pt(self):
        return min(self.sizes) if self.sizes else None

    @property
    def max_pt(self):
        return max(self.sizes) if self.sizes else None


class Slide:
    def __init__(self, n):
        self.n = n
        self.texts = []
        self.charts = []         # dicts: x, y, w, h, min_pt
        self.tables = []         # dicts: x, y, w, h, cells, min_pt, text
        self.pictures = []       # dicts: x, y, w, h, alt
        self.bg = "FFFFFF"
        self.notes = ""
        self.kind = "content"
        self.section = None
        self.has_slidenum = False

    def by_role(self, *roles):
        return [t for t in self.texts if t.role in roles]

    @property
    def title(self):
        t = self.by_role("title")
        return t[0].text.strip() if t else ""

    @property
    def kicker(self):
        t = self.by_role("kicker")
        return t[0].text.strip() if t else ""

    @property
    def body_words(self):
        return sum(t.words for t in self.texts if t.role in BODY_ROLES)

    @property
    def all_text(self):
        parts = [t.text for t in self.texts if t.role != "slidenum"]
        parts += [t["text"] for t in self.tables]
        return "\n".join(parts)

    def exhibits(self, slide_area):
        big = [p for p in self.pictures if p["w"] * p["h"] >= 0.10 * slide_area]
        return self.charts + self.tables + big


class Finding:
    ORDER = {"error": 0, "warning": 1, "note": 2}

    def __init__(self, level, rule, slide, msg, fix=""):
        self.level, self.rule, self.slide, self.msg, self.fix = level, rule, slide, msg, fix

    def as_dict(self):
        return {"level": self.level, "rule": self.rule, "slide": self.slide,
                "message": self.msg, "fix": self.fix}


# ---------------------------------------------------------------- reading the file


def _inch(v):
    return (v or 0) / EMU_IN


def _rgb(color):
    try:
        if color is not None and color.type is not None and color.rgb is not None:
            return str(color.rgb).upper()
    except Exception:
        pass
    return None


def _solid_fill(fill):
    try:
        if fill.type == 1:  # MSO_FILL.SOLID
            return _rgb(fill.fore_color)
    except Exception:
        pass
    return None


def _iter_shapes(shapes):
    for sh in shapes:
        if sh.shape_type == MSO_SHAPE_TYPE.GROUP:
            yield from _iter_shapes(sh.shapes)
        else:
            yield sh


def _read_text(sh):
    t = Text()
    t.name = sh.name or ""
    t.x, t.y, t.w, t.h = _inch(sh.left), _inch(sh.top), _inch(sh.width), _inch(sh.height)
    tf = sh.text_frame
    t.text = tf.text
    xml = sh._element.xml
    t.autofit = "normAutofit" in xml or "spAutoFit" in xml
    t.fill = _solid_fill(sh.fill) if hasattr(sh, "fill") else None
    for p in tf.paragraphs:
        ptxt = "".join(r.text for r in p.runs)
        if not ptxt.strip():
            continue
        sizes, bold = [], False
        for r in p.runs:
            if not r.text.strip():
                continue
            if r.font.size is not None:
                sizes.append(r.font.size.pt)
                t.sizes.append(r.font.size.pt)
            else:
                t.unknown_sizes += 1
            if r.font.name:
                t.fonts.add(r.font.name)
            c = _rgb(r.font.color)
            if c:
                t.colors.add(c)
            bold = bold or bool(r.font.bold)
        t.paras.append((ptxt, max(sizes) if sizes else None, bold))
    return t


def _chart_min_pt(sh):
    try:
        blob = sh.chart.part.blob.decode("utf-8", "ignore")
        sizes = [int(s) / 100 for s in re.findall(r'\bsz="(\d{3,5})"', blob)]
        return min(sizes) if sizes else None
    except Exception:
        return None


def load(path):
    prs = Presentation(str(path))
    W, H = _inch(prs.slide_width), _inch(prs.slide_height)
    slides = []
    for i, ps in enumerate(prs.slides, start=1):
        s = Slide(i)
        try:
            bg = _solid_fill(ps.background.fill)
            if bg:
                s.bg = bg
        except Exception:
            pass
        try:
            if ps.has_notes_slide:
                s.notes = ps.notes_slide.notes_text_frame.text.strip()
        except Exception:
            pass
        for sh in _iter_shapes(ps.shapes):
            box = dict(x=_inch(sh.left), y=_inch(sh.top), w=_inch(sh.width), h=_inch(sh.height))
            xml_has_num = 'type="slidenum"' in sh._element.xml
            if xml_has_num:
                s.has_slidenum = True
            if getattr(sh, "has_chart", False) and sh.has_chart:
                box["min_pt"] = _chart_min_pt(sh)
                s.charts.append(box)
            elif getattr(sh, "has_table", False) and sh.has_table:
                cells, sizes, txt = 0, [], []
                for row in sh.table.rows:
                    for cell in row.cells:
                        cells += 1
                        txt.append(cell.text_frame.text)
                        for p in cell.text_frame.paragraphs:
                            for r in p.runs:
                                if r.font.size is not None and r.text.strip():
                                    sizes.append(r.font.size.pt)
                box.update(cells=cells, min_pt=min(sizes) if sizes else None, text="\n".join(txt))
                s.tables.append(box)
            elif sh.shape_type == MSO_SHAPE_TYPE.PICTURE:
                alt = ""
                m = re.search(r'descr="([^"]*)"', sh._element.xml)
                if m:
                    alt = m.group(1)
                box["alt"] = alt
                s.pictures.append(box)
            elif getattr(sh, "has_text_frame", False) and sh.has_text_frame and sh.text_frame.text.strip():
                t = _read_text(sh)
                if xml_has_num:
                    t.role = "slidenum"
                elif sh.is_placeholder:
                    try:
                        ph = sh.placeholder_format.type
                        if ph in (PP_PLACEHOLDER.TITLE, PP_PLACEHOLDER.CENTER_TITLE):
                            t.role = "title"
                        elif ph in (PP_PLACEHOLDER.FOOTER, PP_PLACEHOLDER.DATE):
                            t.role = "footer"
                        elif ph == PP_PLACEHOLDER.SLIDE_NUMBER:
                            t.role = "slidenum"
                            s.has_slidenum = True
                    except Exception:
                        pass
                s.texts.append(t)
        slides.append(s)
    return slides, W, H


# ---------------------------------------------------------------- classification


def assign_roles(s, H):
    """Name-based for deck_kit decks, positional heuristics for everything else."""
    for t in s.texts:
        if t.role:
            continue
        if t.name.startswith("dk-"):
            t.role = t.name[3:].split("-")[0]
    untagged = [t for t in s.texts if not t.role]
    if not untagged:
        return
    for t in untagged:
        if re.fullmatch(r"\s*\d{1,3}\s*", t.text) and t.y > 0.8 * H:
            t.role = "slidenum"
            s.has_slidenum = True
        elif t.y > 0.84 * H and (t.max_pt or 99) <= 14:
            t.role = "cite" if t.words > 2 else "footer"
    rest = [t for t in s.texts if not t.role]
    if not s.by_role("title"):
        top = [t for t in rest if t.y < 0.42 * H and (t.max_pt or 24) >= 18 and t.words >= 1]
        if top:
            biggest = max(t.max_pt or 24 for t in top)
            cand = sorted((t for t in top if (t.max_pt or 24) >= biggest - 0.5), key=lambda t: t.y)
            cand[0].role = "title"
    title = s.by_role("title")
    for t in [t for t in s.texts if not t.role]:
        if title and t.y < title[0].y and t.words <= 4 and (t.max_pt or 12) <= 16:
            t.role = "kicker"
        else:
            t.role = "body"


THANKS_RE = re.compile(r"^\s*(thank\s*you|thanks|questions\s*\??|any questions\s*\??|q\s*&\s*a|q\s*and\s*a)\b", re.I)


def assign_kinds(slides, slide_area):
    in_appendix = False
    for s in slides:
        head = f"{s.kicker} {s.title}".strip().lower()
        title = s.title.lower()
        if s.n == 1:
            s.kind = "title"
        elif re.match(r"^(appendix|backup|back-up|supplement)", head) or in_appendix and not re.match(
                r"^(references|bibliography)", title):
            s.kind = "appendix"
            in_appendix = True
        elif re.match(r"^(references?|bibliography|works cited|sources)\b", title) or s.by_role("refs"):
            s.kind = "references"
        elif THANKS_RE.match(s.title) or (not s.title and THANKS_RE.match(s.all_text)):
            s.kind = "thanks"
        elif re.match(r"^(conclusions?|summary|key takeaways|takeaways|in sum)\b", head):
            s.kind = "conclusions"
        elif s.body_words == 0 and not s.exhibits(slide_area) and not s.by_role("hero"):
            s.kind = "divider"
        else:
            s.kind = "content"


def assign_sections(slides):
    """Pitch sections: from the kicker when there is one, otherwise from words in the title."""
    for s in slides:
        if s.kind in ("title", "appendix", "references"):
            continue
        probe = s.kicker.lower() if s.kicker else ""
        found = None
        if probe:
            for sec, keys in PITCH_SECTIONS.items():
                if any(probe == k or probe.startswith(k) or k in probe for k in keys):
                    found = sec
                    break
        if not found:
            t = s.title.lower()
            for sec, keys in PITCH_SECTIONS.items():
                if any(re.search(rf"\b{re.escape(k)}\b", t) for k in keys[:2]):
                    found = sec
                    break
            if not found and re.search(r"\b(raising|we are raising|seed round|\$\d[\d.,]*\s*[mk]\b.*\b(raise|round))", t):
                found = "ask"
        s.section = found


def detect_mode(slides):
    text = "\n".join(s.all_text for s in slides).lower()
    pitch = sum(k in text for k in ("traction", "raising", "the ask", "seed", "mrr", "arr", "investors"))
    acad = sum(k in text for k in ("et al", "references", "appendix", "hypothes", "p <", "university"))
    return "pitch" if pitch > acad else "academic"


# ---------------------------------------------------------------- helpers


def title_verdict(title):
    """'label' = topic label, 'weak' = no verb found, 'ok' = reads as a claim."""
    clean = re.sub(r"[^\w\s'%$-]", " ", title).strip().lower()
    toks = clean.split()
    if not toks:
        return "label"
    if clean in TOPIC_LABELS or re.sub(r"^(the|our)\s+", "", clean) in TOPIC_LABELS:
        return "label"
    if len(toks) <= 3:
        return "label"
    if title.strip().endswith("?"):
        return "ok"
    if any(t in AUX or t in VERBS for t in toks):
        return "ok"
    if any(len(t) > 4 and t.endswith("ed") for t in toks):
        return "ok"
    return "weak"


def _lum(hexcolor):
    def ch(v):
        v = v / 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (int(hexcolor[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a, b):
    la, lb = _lum(a), _lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def est_height(t):
    """Rough height the text needs, in inches. None when sizes are unknown."""
    total = 0.0
    for text, pt, bold in t.paras:
        if pt is None:
            return None
        cpl = max(1, int((t.w * 72) / (pt * (0.52 if bold else 0.48))))
        lines = sum(max(1, math.ceil(len(line) / cpl)) for line in text.split("\n"))
        total += lines * pt * 1.2 / 72
    return total


CITE_RE = re.compile(
    r"\b([A-Z][A-Za-z'’\-]+)(?:\s+et\s+al\.?|\s*(?:&|and)\s+[A-Z][A-Za-z'’\-]+)?,?\s*\(?((?:19|20)\d{2})[a-z]?\)?")


def find_citations(text):
    out = set()
    for m in CITE_RE.finditer(text):
        name, year = m.group(1), m.group(2)
        if name in NOT_SURNAMES or len(name) < 2:
            continue
        out.add((name, year))
    return out


NUM_RE = re.compile(r"(?<![\w.])[-−–]?\$?(\d[\d,]*(?:\.\d+)?)(%|×|x\b|pp\b)?")


def numbers_in(text):
    """Numbers worth tracing: anything with a decimal, a unit, or at least two digits."""
    text = CITE_RE.sub(" ", text)
    text = re.sub(r"\b(19|20)\d{2}\b", " ", text)                   # bare years
    text = re.sub(r"(?m)^\s*\d{1,2}[.)]\s", " ", text)               # list numbering
    out = set()
    for m in NUM_RE.finditer(text):
        raw, unit = m.group(1), m.group(2) or ""
        digits = raw.replace(",", "")
        if "." in digits or unit or len(digits) >= 2:
            out.add((digits, unit))
    return out


def number_in_source(digits, unit, source):
    forms = {digits}
    try:
        v = float(digits)
        forms.add(f"{v:,.0f}" if v == int(v) else digits)
        if unit == "%":
            forms.add(f"{v / 100:.2f}".rstrip("0").rstrip("."))
            forms.add(f"{v / 100:.3f}".rstrip("0").rstrip("."))
            forms.add((f"{v / 100:.2f}").lstrip("0"))
        if digits.startswith("0."):
            forms.add(digits[1:])
    except ValueError:
        pass
    for f in forms:
        if not f:
            continue
        if re.search(rf"(?<![\d.]){re.escape(f)}(?!\d|\.\d)", source):
            return True
    return False


def load_source(path):
    p = Path(path)
    if p.suffix.lower() == ".json":
        data = json.loads(p.read_text(encoding="utf-8"))
        return data.get("text") or json.dumps(data)
    if p.suffix.lower() == ".pdf":
        try:
            return subprocess.run(["pdftotext", "-layout", str(p), "-"], capture_output=True,
                                  text=True, check=True).stdout
        except Exception:
            from pypdf import PdfReader
            return "\n".join((pg.extract_text() or "") for pg in PdfReader(str(p)).pages)
    return p.read_text(encoding="utf-8", errors="ignore")


PLACEHOLDER_RE = re.compile(r"\[\[|\]\]|\bNEEDS:|\bTODO\b|\bTBD\b|\bTK\b|lorem ipsum|\bX{2,}\b|\$X\b|\bXX%|\[(insert|your|company|name|date|number)[^\]]*\]", re.I)

# ---------------------------------------------------------------- rules


def lint(slides, W, H, mode, minutes=None, source=None, require_notes=False, rules=None):
    F = []
    area = W * H
    cfg = (rules or {}).get("settings", {})

    def add(level, rule, slide, msg, fix=""):
        F.append(Finding(level, rule, slide, msg, fix))

    presented = [s for s in slides if s.kind not in ("appendix", "references")]
    claim_slides = [s for s in slides if s.kind in ("content", "appendix")]
    warn_w, err_w = WORD_LIMITS[mode]
    if isinstance(cfg.get("body_words"), (int, float)):
        warn_w = int(cfg["body_words"])
        err_w = max(err_w, int(round(warn_w * 1.5)))
    title_words = int(cfg["title_words"]) if isinstance(cfg.get("title_words"), (int, float)) else TITLE_WORDS[mode]
    floors = dict(FLOORS[mode])
    for key, group in (("body_min", "body"), ("title_min", "title")):
        if isinstance(cfg.get(key), (int, float)):
            floors[group] = (cfg[key] - 2, cfg[key])
    if minutes is None and isinstance(cfg.get("minutes"), (int, float)):
        minutes = cfg["minutes"]
    max_slides = cfg.get("max_slides") if isinstance(cfg.get("max_slides"), (int, float)) else None

    # ---- every slide
    inherit = 0
    for s in slides:
        text = s.all_text
        m = PLACEHOLDER_RE.search(text)
        if m:
            add("error", "PLACEHOLDER", s.n, f"unfilled placeholder: “{text[max(0, m.start() - 20):m.end() + 30].strip()}”",
                "Get the real value from the author or cut the line. Never invent it.")

        # titles
        if s.kind in ("content", "appendix"):
            if not s.title:
                add("error", "TITLE-MISSING", s.n, "no title found",
                    "Every content slide needs an action title: a full sentence stating the takeaway.")
            else:
                v = title_verdict(s.title)
                if v == "label":
                    add("error", "TITLE-LABEL", s.n, f"title is a topic label: “{s.title}”",
                        "Rewrite as a sentence that states the takeaway, e.g. “Results” → “Treatment raises earnings 18%”.")
                elif v == "weak":
                    add("warning", "TITLE-NO-VERB", s.n, f"title may not state a claim (no verb found): “{s.title}”",
                        "An action title says what is true, not what the slide is about.")
                if len(s.title.split()) > title_words:
                    add("warning", "TITLE-LONG", s.n, f"title is {len(s.title.split())} words",
                        f"Keep it under {title_words} words; if it will not fit in two lines the point is not sharp yet.")

        # words
        if s.kind in ("content", "conclusions"):
            n = s.body_words
            if n > err_w:
                add("error", "WORDS", s.n, f"{n} words of body text (limit {warn_w})",
                    "Split the slide or move detail to the appendix or speaker notes.")
            elif n > warn_w:
                add("warning", "WORDS", s.n, f"{n} words of body text (limit {warn_w})",
                    "Cut to what the audience must read; say the rest aloud.")

        # type size, contrast, overflow, bounds
        for t in s.texts:
            group = ROLE_GROUP.get(t.role, "body")
            if t.unknown_sizes and not t.sizes:
                inherit += 1
            if group and t.min_pt is not None:
                err_below, warn_below = floors[group]
                if s.kind in ("references",) and group == "body":
                    err_below, warn_below = floors["fine"]
                if t.min_pt < err_below:
                    add("error", "FONT-SMALL", s.n, f"{t.role} text at {t.min_pt:g} pt (minimum {warn_below}): “{t.text.strip()[:50]}”",
                        "Remove content until it fits at the minimum size. Do not shrink type to fit.")
                elif t.min_pt < warn_below:
                    add("warning", "FONT-SMALL", s.n, f"{t.role} text at {t.min_pt:g} pt (target {warn_below}+): “{t.text.strip()[:50]}”",
                        "Type this small is hard to read from the back of a room.")
            bg = t.fill or s.bg
            for c in t.colors:
                ratio = contrast(c, bg)
                need = 3.0 if (t.max_pt or 12) >= 24 else 4.5
                if ratio < need:
                    add("warning", "CONTRAST", s.n, f"{t.role} text #{c} on #{bg} has contrast {ratio:.1f}:1 (need {need}:1)",
                        "Darken the text. Light grey on white disappears on a projector.")
            if t.role != "slidenum":
                if t.x < -0.02 or t.y < -0.02 or t.x + t.w > W + 0.02 or t.y + t.h > H + 0.02:
                    add("error", "OFF-SLIDE", s.n, f"{t.role} box extends past the slide edge: “{t.text.strip()[:40]}”")
                need = est_height(t)
                if need is not None and not t.autofit and need > t.h * 1.25 + 0.15:
                    add("warning", "OVERFLOW", s.n, f"{t.role} text probably overflows its box (needs ~{need:.1f}\", box is {t.h:.1f}\"): “{t.text.strip()[:40]}”",
                        "Render the slide and look. Cut words or split the slide.")
        for ex in s.charts + s.tables:
            if ex.get("min_pt") is not None and ex["min_pt"] < floors["secondary"][0]:
                add("warning", "EXHIBIT-FONT", s.n, f"chart or table text at {ex['min_pt']:g} pt (target {floors['secondary'][1]}+)",
                    "Rebuild the exhibit at presentation size; paper-sized labels are unreadable on screen.")
        for ex in s.charts + s.tables + s.pictures:
            if ex["x"] < -0.02 or ex["y"] < -0.02 or ex["x"] + ex["w"] > W + 0.02 or ex["y"] + ex["h"] > H + 0.02:
                add("error", "OFF-SLIDE", s.n, "an exhibit extends past the slide edge")

        # exhibits
        ex = s.exhibits(area)
        if s.kind == "content" and len(ex) > 1:
            add("warning", "EXHIBITS", s.n, f"{len(ex)} exhibits on one slide",
                "One exhibit per slide. Two charts are either one comparison (combine them) or two points (two slides).")
        if s.kind in ("content", "appendix") and ex and not s.by_role("cite"):
            add("warning", "EXHIBIT-SOURCE", s.n, "exhibit has no source line",
                "Add one at the bottom, e.g. “Source: authors' calculations from …” or “Source: company billing data, Jan–Jun 2026”.")
        if s.kind == "content" and s.charts and not s.by_role("annot"):
            inside = [t for t in s.by_role("body") if t.words <= 8 and any(
                c["x"] <= t.x <= c["x"] + c["w"] and c["y"] <= t.y <= c["y"] + c["h"] for c in s.charts)]
            if not inside:
                add("warning", "ANNOTATE", s.n, "chart has no call-out marking the key finding",
                    "Label the focal bar, point or region so the audience does not have to hunt for it.")
        for t in s.tables:
            if t["cells"] > 24 and s.kind == "content":
                add("warning", "TABLE-DENSE", s.n, f"table has {t['cells']} cells",
                    "Chart the comparison, or keep only the rows the argument needs and move the rest to the appendix.")
        for p in s.pictures:
            if p["w"] * p["h"] >= 0.10 * area and not p["alt"]:
                add("note", "ALT-TEXT", s.n, "figure has no alt text", "Add alt text if the slides will be shared as a file.")

        if s.kind == "thanks":
            add("error" if mode == "academic" else "warning", "THANKS-SLIDE", s.n, f"“{(s.title or s.all_text).strip()[:30]}” slide",
                "Delete it. End on the conclusions slide (academic) or the ask (pitch) and leave that up during questions.")

    if inherit:
        add("note", "FONT-INHERITED", 0, f"{inherit} text box(es) take their font size from the template, so their size was not checked")

    faces = set()
    for s in slides:
        for t in s.texts:
            faces |= t.fonts
    want_face = cfg.get("face")
    if want_face and faces - {want_face}:
        add("warning", "R-FACE", 0, f"typeface(s) other than {want_face} in use: {', '.join(sorted(faces - {want_face}))}",
            f"deck_rules.md sets the typeface to {want_face}.")
    elif len(faces) > (1 if mode == "academic" else 2):
        add("warning", "FONTS", 0, f"{len(faces)} typefaces in use: {', '.join(sorted(faces))}",
            "Use one typeface; build hierarchy with size and weight.")

    numbered = [s for s in slides if s.kind in ("content", "conclusions", "appendix")]
    missing_num = [s.n for s in numbered if not s.has_slidenum]
    if numbered and len(missing_num) > len(numbered) / 2:
        add("warning" if mode == "academic" else "note", "SLIDE-NUMBERS", 0, "slides are not numbered",
            "Number them: “can you go back to slide 12?” is how questions get asked.")

    no_notes = [s.n for s in presented if s.kind in ("content", "conclusions") and not s.notes]
    if no_notes:
        add("warning" if require_notes else "note", "NOTES", 0,
            f"no speaker notes on slide(s) {', '.join(map(str, no_notes))}",
            "Notes carry the argument the slide leaves out: what to say, and the transition to the next slide.")

    if source is not None:
        for s in slides:
            if s.kind in ("title", "references", "divider"):
                continue
            missing = []
            for digits, unit in sorted(numbers_in(s.all_text)):
                if number_in_source(digits, unit, source):
                    continue
                if re.search(rf"(?<![\d.]){re.escape(digits)}(?!\d)", s.notes):
                    continue  # derivation explained in the notes
                missing.append(digits + unit)
            if missing:
                add("warning", "NUMBER-NOT-IN-SOURCE", s.n, f"not found in the source: {', '.join(missing)}",
                    "Check each against the paper. If it is derived (a ratio, a rounding), say how in the speaker notes; if it is wrong, fix it.")

    # ---- the user's own rules (deck_rules.md)
    for phrase in cfg.get("banned_words", []) or []:
        pat = re.compile(rf"(?<!\w){re.escape(phrase)}(?!\w)", re.I)
        for s in slides:
            if s.kind != "references" and pat.search(s.all_text):
                add("warning", "R-BANNED-WORD", s.n, f"“{phrase}” is on the banned list in deck_rules.md",
                    "Reword the slide without it.")
    for phrase in cfg.get("required_sections", []) or []:
        low = phrase.lower()
        if not any(low in s.kicker.lower() or low in s.title.lower() or low == (s.section or "") for s in slides):
            add("warning", "R-SECTION-MISSING", 0, f"deck_rules.md requires a “{phrase}” slide and none was found",
                "Add the slide, with that phrase in its section label or title.")
    if max_slides is not None and mode == "academic":
        main = [s for s in presented if s.kind in ("content", "conclusions", "divider")]
        if len(main) > max_slides:
            add("warning", "R-MAX-SLIDES", 0, f"{len(main)} presented slides; deck_rules.md sets a maximum of {max_slides:g}",
                "Move the extra slides to the appendix.")

    if mode == "academic":
        _academic(slides, presented, add, minutes)
    else:
        _pitch(slides, presented, add, max_slides)

    off = set(cfg.get("disable", []) or [])
    suppressed = [f for f in F if f.rule in off]
    F = [f for f in F if f.rule not in off]
    if rules is not None:
        rules["suppressed"] = len(suppressed)
    F.sort(key=lambda f: (Finding.ORDER[f.level], f.slide, f.rule))
    return F


def _academic(slides, presented, add, minutes):
    kinds = [s.kind for s in slides]

    # research question early
    early = [s for s in presented if 2 <= s.n <= 4]
    if early and not any(s.by_role("question") or "?" in s.title or re.search(
            r"\b(question|we ask|we test|we study|hypothes|this paper|this talk)\b", s.title + " " + s.all_text, re.I)
            for s in early):
        add("warning", "A-QUESTION", 0, "no research question or central claim found in slides 2–4",
            "State it explicitly, on its own slide, before any method or result.")

    # conclusions last
    concl = [s for s in slides if s.kind == "conclusions"]
    if not concl:
        add("error", "A-CONCLUSIONS", 0, "no conclusions slide",
            "Add one with 2–4 numbered takeaways and contact details. It is the last slide you present.")
    else:
        last = concl[-1]
        after = [s.n for s in slides if s.n > last.n and s.kind in ("content", "divider", "thanks")]
        if after:
            add("error", "A-CONCLUSIONS-LAST", last.n, f"slide(s) {', '.join(map(str, after))} come after the conclusions",
                "Only References and Appendix may follow the conclusions slide.")
        if not re.search(r"@|\bhttps?://|\bwww\.|\.[a-z]{2,4}/|\.(edu|org|com|io)\b", last.all_text, re.I):
            add("note", "A-CONTACT", last.n, "no email or link on the conclusions slide",
                "Add an email and a link or QR code to the paper.")

    # citations
    cited = {}
    for s in slides:
        if s.kind in ("references", "title"):
            continue
        body = "\n".join(t.text for t in s.texts if t.role not in ("footer", "slidenum", "venue", "authors", "contact"))
        for c in find_citations(body):
            cited.setdefault(c, s.n)
    refs = [s for s in slides if s.kind == "references"]
    ref_paras = []
    for s in refs:
        for t in s.texts:
            if t.role in ("title", "footer", "slidenum"):
                continue
            ref_paras += [p[0] for p in t.paras]
    if cited and not refs:
        add("error", "A-REFERENCES", 0, f"{len(cited)} in-slide citation(s) but no References slide",
            "Add a References slide after the conclusions with the full citation for each.")
    elif not refs:
        add("warning", "A-REFERENCES", 0, "no References slide",
            "If nothing is borrowed, fine. Otherwise cite on the slide and list the full reference at the end.")
    else:
        for (name, year), n in sorted(cited.items(), key=lambda kv: kv[1]):
            if not any(name in p and year in p for p in ref_paras):
                add("error", "A-CITE-MISSING", n, f"“{name} ({year})” is cited but is not in References",
                    "Add the full reference from the paper's bibliography. If you cannot find the source, remove the citation — never invent one.")
        for p in ref_paras:
            m = re.match(r"\s*([A-Z][A-Za-z'’\-]+)", p)
            y = re.search(r"\((?:19|20)\d{2}[a-z]?\)|\b(?:19|20)\d{2}\b", p)
            if m and y:
                year = re.search(r"\d{4}", y.group(0)).group(0)
                if (m.group(1), year) not in cited:
                    add("note", "A-REF-UNCITED", refs[0].n, f"“{m.group(1)} ({year})” is listed but never cited on a slide",
                        "Fine for your own paper; otherwise cite it where it is used or drop it.")

    # time budget
    main = [s for s in presented if s.kind in ("content", "conclusions", "divider")]
    if minutes:
        if len(main) > minutes:
            add("error", "A-BUDGET", 0, f"{len(main)} presented slides for a {minutes}-minute slot",
                f"At most one slide per minute. Move {len(main) - int(minutes)} slide(s) to the appendix.")
        elif len(main) < 0.4 * minutes:
            add("note", "A-BUDGET", 0, f"only {len(main)} presented slides for {minutes} minutes",
                "Fine for a discussion-heavy seminar; otherwise check the pacing.")
    if len(main) > 15 and "divider" not in kinds and not any(s.by_role("breadcrumb") for s in slides):
        add("note", "A-NAVIGATION", 0, f"{len(main)} slides with no section dividers or breadcrumb",
            "Give a long talk signposts so the audience knows where they are.")


def _pitch(slides, presented, add, max_slides=None):
    main = [s for s in presented if s.kind != "title"]
    soft = max_slides if max_slides is not None else 15
    hard = math.ceil(soft * 4 / 3)
    if len(main) > hard:
        add("error", "P-LENGTH", 0, f"{len(main)} slides before the appendix (limit {soft:g})",
            "A seed deck is about 10–12 slides. Keep one slide per section and move the rest to the appendix.")
    elif len(main) > soft:
        add("warning", "P-LENGTH", 0, f"{len(main)} slides before the appendix (limit {soft:g})",
            "Aim for 10–12. Each section is one slide, rarely more than three.")

    by_sec = {}
    for s in main:
        if s.section:
            by_sec.setdefault(s.section, []).append(s)
    for sec, level in (("problem", "warning"), ("solution", "warning"), ("market", "warning"),
                       ("business model", "warning"), ("team", "warning"), ("ask", "warning"),
                       ("traction", "note"), ("why now", "note"), ("competition", "note")):
        if sec not in by_sec:
            hint = {
                "traction": "If you have any numbers at all, show them early. If not, show the insight that makes this work.",
                "why now": "Say what changed that makes this possible or urgent today.",
                "competition": "Name the real alternatives, including doing nothing.",
            }.get(sec, f"Add a slide with the section label “{sec.title()}” above its title.")
            add(level, "P-SECTION-MISSING", 0, f"no {sec} slide found", hint)
    for sec, ss in by_sec.items():
        if len(ss) > 3:
            add("warning", "P-SECTION-LONG", ss[0].n, f"{len(ss)} slides in the {sec} section", "Keep each section to one slide where possible, three at most.")

    first = slides[0]
    if len(first.all_text.split()) > 30:
        add("warning", "P-ONE-LINER", 1, f"title slide has {len(first.all_text.split())} words",
            "Company name and one line saying what you do. Nothing else.")

    for s in by_sec.get("traction", []):
        if not re.search(r"\d", s.all_text) and not s.charts:
            add("error", "P-TRACTION-NUMBER", s.n, "traction slide has no numbers",
                "Traction is a number with a unit and a time window. If there is none yet, do not call the slide traction.")
    for s in by_sec.get("market", []):
        if not re.search(r"[$€£]\s*\d|\d\s*(billion|million|bn|mm|[bmk])\b", s.all_text, re.I):
            add("warning", "P-MARKET-SIZE", s.n, "market slide has no size", "Show the bottom-up arithmetic: number of buyers × what each pays per year.")
        elif not re.search(r"[×x*]|\bper\b|\beach\b", s.all_text, re.I):
            add("note", "P-MARKET-BOTTOM-UP", s.n, "market size shown without the arithmetic behind it",
                "Investors trust buyers × price more than a top-down industry figure.")
    for s in by_sec.get("team", []):
        if re.search(r"\badvis(or|er)s?\b", s.all_text, re.I):
            add("note", "P-TEAM-ADVISORS", s.n, "advisors on the team slide", "Keep the slide to founders; advisors read as padding.")
        if not re.search(r"\d", " ".join(t.text for t in s.texts if t.role not in ("title", "kicker", "slidenum"))):
            add("note", "P-TEAM-PROOF", s.n, "no numbers on the team slide", "Quantify past wins: revenue grown, users served, systems shipped.")
    asks = by_sec.get("ask", [])
    for s in asks:
        if not re.search(r"[$€£]\s*\d", s.all_text):
            add("warning", "P-ASK-AMOUNT", s.n, "ask slide does not state an amount", "Say how much you are raising and what it gets you to.")
        if re.search(r"valuation|pre-money|post-money|\bcap\b|\bdiscount\b", s.all_text, re.I):
            add("warning", "P-ASK-TERMS", s.n, "fundraising terms on the ask slide", "Leave valuation, cap and discount for the conversation.")
    if asks and main and main[-1].section != "ask":
        add("note", "P-ASK-LAST", asks[-1].n, "the ask is not the last slide before the appendix", "End on the ask and leave it up.")

    growth_window = re.compile(r"\b(mom|yoy|wow|qoq|month|monthly|week|weekly|year|annual|annually|quarter|quarterly|"
                               r"since|in \d+|over \d+|last \d+|per (day|week|month|year))", re.I)
    for s in main:
        text = s.all_text
        low = text.lower()
        hits = sorted({b for b in BUZZWORDS if re.search(rf"\b{re.escape(b)}\b", low)})
        if hits:
            add("warning", "P-BUZZWORDS", s.n, f"empty adjectives: {', '.join(hits)}", "Replace each with the number or fact it stands in for.")
        if re.search(r"\bno (direct )?(competitors?|competition)\b", low):
            add("warning", "P-NO-COMPETITION", s.n, "claims there is no competition", "There is always an alternative, even if it is a spreadsheet. Name it and say why you win.")
        if re.search(r"\d\s*%", text) and re.search(r"\b(grow|growth|grew|growing|increase|increased|up)\b", low) and not growth_window.search(low):
            add("warning", "P-GROWTH-WINDOW", s.n, "growth figure with no time window", "“40% growth” means nothing without “per month” or “year over year”.")


# ---------------------------------------------------------------- output


def ghost_deck(slides):
    lines = []
    for s in slides:
        tag = {"title": "title", "references": "refs", "appendix": "appx", "conclusions": "concl",
               "divider": "part", "thanks": "!!"}.get(s.kind, "")
        label = s.title or (s.all_text.strip().split("\n")[0][:70] if s.all_text.strip() else "(no text)")
        if s.kind == "conclusions" and s.kicker and not s.by_role("title"):
            label = "Conclusions: " + " / ".join(p[0].strip() for t in s.by_role("body") for p in t.paras)[:150]
        sec = f" <{s.section}>" if s.section else ""
        lines.append(f"  {s.n:>2}  {('[' + tag + ']') if tag else '':<8}{label}{sec}")
    return "\n".join(lines)


def rules_summary(rules):
    """Lines describing what deck_rules.md changed, and the written rules to check by hand."""
    if not rules:
        return []
    out = [f"CUSTOM RULES — {rules['path']}"]
    shown = {k: v for k, v in rules["settings"].items() if k not in rules["unknown"]}
    if shown:
        out.append("  settings: " + "; ".join(
            f"{k} = {', '.join(map(str, v)) if isinstance(v, list) else v}" for k, v in sorted(shown.items())))
    if rules["settings"].get("disable"):
        out.append(f"  switched off: {', '.join(rules['settings']['disable'])} ({rules.get('suppressed', 0)} finding(s) hidden)")
    if rules["locked"]:
        out.append(f"  NOT switched off (they guard against invented content): {', '.join(rules['locked'])}")
    if rules["unknown"]:
        out.append(f"  ignored, not a known setting: {', '.join(rules['unknown'])}")
    if rules["rules"]:
        out.append("  written rules — the linter cannot check these; confirm each by hand:")
        out += [f"    □ {r}" for r in rules["rules"]]
    out.append("")
    return out


def report(path, mode, slides, findings, rules=None):
    counts = {k: sum(1 for s in slides if s.kind == k) for k in ("appendix", "references")}
    shown = len(slides) - counts["appendix"] - counts["references"]
    out = [f"{path} — {mode} mode — {len(slides)} slides "
           f"({shown} presented, {counts['references']} references, {counts['appendix']} appendix)", "",
           "GHOST DECK — read the titles in order. Do they make the whole argument on their own?",
           ghost_deck(slides), ""]
    out += rules_summary(rules)
    n = {lvl: sum(1 for f in findings if f.level == lvl) for lvl in ("error", "warning", "note")}
    out.append(f"FINDINGS — {n['error']} error(s), {n['warning']} warning(s), {n['note']} note(s)")
    for f in findings:
        where = f"slide {f.slide}" if f.slide else "deck"
        out.append(f"  {f.level.upper():<7} {where:<9} {f.rule}: {f.msg}")
        if f.fix:
            out.append(f"  {'':<17} fix: {f.fix}")
    out.append("")
    out.append("RESULT: " + ("FAIL — fix the errors and run again" if n["error"] else
                             "PASS — no errors" + (" (review the warnings)" if n["warning"] else "")))
    out.append("This checks form only. Now render the slides and look at them.")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Check a .pptx against academic or pitch deck rules.")
    ap.add_argument("pptx")
    ap.add_argument("--mode", choices=["academic", "pitch", "auto"], default="auto")
    ap.add_argument("--minutes", type=float, help="talk length; enforces one slide per minute (academic)")
    ap.add_argument("--source", help="paper.json from extract_paper.py, or a .pdf/.txt/.tex; every number on a slide must appear in it")
    ap.add_argument("--require-notes", action="store_true", help="treat missing speaker notes as a warning")
    ap.add_argument("--rules", help="the user's deck_rules.md (default: one beside the .pptx or in the current folder)")
    ap.add_argument("--no-rules", action="store_true", help="ignore any deck_rules.md")
    ap.add_argument("--strict", action="store_true", help="exit 1 on warnings as well as errors")
    ap.add_argument("--ghost", action="store_true", help="print only the titles in order")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    a = ap.parse_args(argv)

    try:
        slides, W, H = load(a.pptx)
    except Exception as e:
        sys.stderr.write(f"could not read {a.pptx}: {e}\n")
        return 2
    if not slides:
        sys.stderr.write("the deck has no slides\n")
        return 2
    for s in slides:
        assign_roles(s, H)
    assign_kinds(slides, W * H)
    mode = detect_mode(slides) if a.mode == "auto" else a.mode
    if mode == "pitch":
        assign_sections(slides)
    if a.ghost:
        print(ghost_deck(slides))
        return 0
    source = None
    if a.source:
        try:
            source = load_source(a.source)
        except Exception as e:
            sys.stderr.write(f"could not read source {a.source}: {e}\n")
            return 2
    rules = None
    if not a.no_rules and load_rules is not None:
        rules_path = a.rules or find_rules(a.pptx)
        if a.rules and not Path(a.rules).is_file():
            sys.stderr.write(f"rules file not found: {a.rules}\n")
            return 2
        if rules_path:
            rules = load_rules(rules_path, mode)
    findings = lint(slides, W, H, mode, minutes=a.minutes, source=source, require_notes=a.require_notes, rules=rules)
    errors = sum(1 for f in findings if f.level == "error")
    warnings = sum(1 for f in findings if f.level == "warning")
    if a.json:
        print(json.dumps({
            "file": a.pptx, "mode": mode, "slides": len(slides), "errors": errors, "warnings": warnings,
            "ghost_deck": [{"slide": s.n, "kind": s.kind, "section": s.section, "title": s.title} for s in slides],
            "rules": rules,
            "findings": [f.as_dict() for f in findings]}, indent=2))
    else:
        print(report(a.pptx, mode, slides, findings, rules))
    return 1 if errors or (a.strict and warnings) else 0


if __name__ == "__main__":
    sys.exit(main())
