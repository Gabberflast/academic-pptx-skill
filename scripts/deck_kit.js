"use strict";
/**
 * deck_kit.js — slide builders for argument-first decks (academic + pitch).
 *
 * Why this exists: hand-placed coordinates drift. A two-line title collides
 * with the body, a citation lands at 11 pt, slide 14 uses a different margin.
 * The kit measures the title, flows the rest of the slide from it, keeps every
 * font at or above the readable floor, and names each text box (dk-title,
 * dk-body, dk-cite, ...) so scripts/lint_deck.py can check the finished file.
 *
 * Usage:
 *   const { createDeck, NEEDS } = require("./deck_kit.js");
 *   const deck = createDeck({ mode: "academic", title: "...", author: "...",
 *                             scheme: "forest", rules: "deck_rules.md" });
 *   deck.titleSlide({ ... });
 *   deck.result({ ... });
 *   await deck.save("talk.pptx");
 *
 * Anything the kit does not cover: call deck.blank({ title }) to get
 * { slide, top, bottom } and use the PptxGenJS API directly inside that area.
 */

const fs = require("fs");
const PptxGenJS = require("pptxgenjs");

const W = 10;       // LAYOUT_16x9 width, inches
const H = 5.625;    // LAYOUT_16x9 height, inches
const M = 0.5;      // margin from every edge
const CW = W - 2 * M;

const THEMES = {
  academic: {
    face: "Arial",
    colors: {
      bg: "FFFFFF",
      primary: "1F4E79",      // titles, dark slides
      accent: "2E75B6",       // headers, focal data series
      body: "2D2D2D",
      muted: "595959",        // 7.0:1 on white (the usual 777777 is 4.48:1 and fails AA)
      neutral: "A6A6A6",      // non-focal data series
      grid: "E2E8F0",
      card: "F3F6FA",
      calloutFill: "FFF2CC",
      calloutLine: "E6C800",
      calloutText: "5C3D00",
      onDark: "FFFFFF",
      onDarkMuted: "C9DAEE",
    },
    size: { title: 26, titleMin: 22, header: 22, body: 20, label: 16, cite: 13, kicker: 14, hero: 72 },
    bodyWords: 40,
  },
  pitch: {
    face: "Arial",
    colors: {
      bg: "FFFFFF",
      primary: "111827",
      accent: "2563EB",       // replace with the company's one brand colour
      body: "1F2937",
      muted: "4B5563",
      neutral: "9CA3AF",
      grid: "E5E7EB",
      card: "F3F4F6",
      calloutFill: "FEF3C7",
      calloutLine: "F59E0B",
      calloutText: "78350F",
      onDark: "FFFFFF",
      onDarkMuted: "D1D5DB",
    },
    size: { title: 32, titleMin: 28, header: 24, body: 24, label: 18, cite: 13, kicker: 14, hero: 96 },
    bodyWords: 25,
  },
};

/**
 * Named colour schemes. Each works in either mode. Every text colour here is at
 * least 4.5:1 against its background. `midnight` is the one dark-background scheme.
 */
const SCHEMES = {
  navy: { primary: "1F4E79", accent: "2E75B6" },
  crimson: { primary: "7A1E2C", accent: "B03A48" },
  forest: { primary: "1E4D3B", accent: "2F7D5B" },
  plum: { primary: "4B2E83", accent: "7A5CC0" },
  slate: { primary: "1F2937", accent: "475569" },
  ink: { primary: "111827", accent: "2563EB" },
  emerald: { primary: "111827", accent: "047857" },
  violet: { primary: "111827", accent: "6D28D9" },
  ember: { primary: "111827", accent: "C2410C" },
  midnight: {
    bg: "0B1220", darkBg: "020617", primary: "F9FAFB", accent: "60A5FA", body: "E5E7EB",
    muted: "9CA3AF", neutral: "6B7280", grid: "1F2937", card: "1E293B",
    onDark: "FFFFFF", onDarkMuted: "CBD5E1",
  },
};

const RULE_SCOPES = ["all", "academic", "pitch"];
const RULE_LISTS = ["disable", "banned_words", "required_sections"];
const RULE_NUMBERS = ["title_size", "body_size", "body_words", "title_words", "body_min", "title_min", "max_slides", "minutes"];
const RULE_COLORS = ["primary", "accent", "background", "body"];

/**
 * Reads deck_rules.md (see scripts/deck_rules.py for the format).
 * Returns { settings, rules } for one mode, or null when the file does not exist.
 */
function loadRules(file, mode) {
  if (!file || !fs.existsSync(file)) return null;
  const settings = { all: {}, academic: {}, pitch: {} };
  const rules = [];
  let section = null;
  let fenced = false;
  const known = RULE_LISTS.concat(RULE_NUMBERS, RULE_COLORS, ["scheme", "face", "footer"]);
  fs.readFileSync(file, "utf8").split(/\r?\n/).forEach((line) => {
    if (line.trim().startsWith("```")) { fenced = !fenced; return; }
    const h = fenced ? null : line.match(/^##\s+(.*?)\s*$/);
    if (h) {
      const name = h[1].toLowerCase();
      if (name.startsWith("settings")) {
        const scope = name.includes(":") ? name.split(":")[1].trim() : "all";
        section = { kind: "settings", scope: RULE_SCOPES.includes(scope) ? scope : "all" };
      } else if (name.startsWith("rules")) {
        section = { kind: "rules" };
      } else {
        section = null;
      }
      return;
    }
    if (!section || !line.trim()) return;
    if (section.kind === "settings") {
      const m = line.match(/^\s*([A-Za-z_]+)\s*:\s*(.*?)\s*$/);
      if (!m || !m[2]) return;
      const key = m[1].toLowerCase();
      if (!fenced && !known.includes(key)) return;   // prose outside the code block
      let value = m[2].replace(/^["']|["']$/g, "");
      if (RULE_COLORS.includes(key)) value = value.replace(/^#/, "").toUpperCase();
      else if (RULE_LISTS.includes(key)) value = value.split(",").map((v) => v.trim()).filter(Boolean);
      else if (RULE_NUMBERS.includes(key) && !Number.isNaN(Number(value))) value = Number(value);
      settings[section.scope][key] = value;
    } else {
      const m = line.match(/^\s*[-*]\s+(?:\[(\w+)\]\s*)?(.*?)\s*$/);
      if (!m || !m[2]) return;
      const scope = RULE_SCOPES.includes((m[1] || "all").toLowerCase()) ? (m[1] || "all").toLowerCase() : "all";
      rules.push({ scope, text: m[2].replace(/\s*\(added \d{4}-\d{2}-\d{2}\)\s*$/, "") });
    }
  });
  return {
    file,
    settings: Object.assign({}, settings.all, settings[mode] || {}),
    rules: rules.filter((r) => r.scope === "all" || r.scope === mode).map((r) => r.text),
  };
}

function luminance(hex) {
  const ch = (i) => {
    const v = parseInt(hex.slice(i, i + 2), 16) / 255;
    return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
  };
  return 0.2126 * ch(0) + 0.7152 * ch(2) + 0.0722 * ch(4);
}

function contrast(a, b) {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
}

/** Marks a fact you do not have. The linter fails the deck until every one is replaced. */
function NEEDS(what) {
  return `[[NEEDS: ${what}]]`;
}

// ---------- text measurement (estimates, tuned on Arial; slightly conservative) ----------

function charsPerLine(widthIn, pt, bold) {
  return Math.max(1, Math.floor((widthIn * 72) / (pt * (bold ? 0.52 : 0.48))));
}

function estLines(text, widthIn, pt, bold) {
  const cpl = charsPerLine(widthIn, pt, bold);
  return String(text)
    .split("\n")
    .reduce((n, line) => n + Math.max(1, Math.ceil((line.length * 1.04) / cpl)), 0);
}

function lineHeight(pt) {
  return (pt * 1.2) / 72;
}

function words(text) {
  return String(text).trim().split(/\s+/).filter(Boolean).length;
}

function imageSize(path) {
  // PNG, JPEG and GIF headers only; returns null when unknown.
  try {
    const b = fs.readFileSync(path);
    if (b.length > 24 && b.toString("ascii", 1, 4) === "PNG") {
      return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
    }
    if (b.toString("ascii", 0, 3) === "GIF") {
      return { w: b.readUInt16LE(6), h: b.readUInt16LE(8) };
    }
    if (b[0] === 0xff && b[1] === 0xd8) {
      let i = 2;
      while (i < b.length - 9) {
        if (b[i] !== 0xff) { i += 1; continue; }
        const marker = b[i + 1];
        const len = b.readUInt16BE(i + 2);
        if (marker >= 0xc0 && marker <= 0xcf && ![0xc4, 0xc8, 0xcc].includes(marker)) {
          return { h: b.readUInt16BE(i + 5), w: b.readUInt16BE(i + 7) };
        }
        i += 2 + len;
      }
    }
  } catch (e) { /* fall through */ }
  return null;
}

// ---------- deck ----------

class Deck {
  /**
   * opts: mode, title, author, footer, sections,
   *       scheme  — a name from SCHEMES,
   *       colors  — individual overrides, e.g. { accent: "0F766E" },
   *       face    — typeface,
   *       rules   — path to the user's deck_rules.md.
   * Order of precedence: these arguments, then deck_rules.md, then the mode's defaults.
   */
  constructor(opts = {}) {
    this.mode = opts.mode === "pitch" ? "pitch" : "academic";
    const base = THEMES[this.mode];
    this.warnings = [];
    this.count = 0;
    this.rules = loadRules(opts.rules, this.mode);
    if (opts.rules && !this.rules) this.warnings.push(`deck: rules file not found: ${opts.rules}`);
    const set = this.rules ? this.rules.settings : {};

    const schemeName = opts.scheme || set.scheme;
    if (schemeName && !SCHEMES[schemeName]) {
      this.warnings.push(`deck: unknown colour scheme "${schemeName}" (have: ${Object.keys(SCHEMES).join(", ")})`);
    }
    const fromRules = {};
    if (set.primary) fromRules.primary = set.primary;
    if (set.accent) fromRules.accent = set.accent;
    if (set.background) fromRules.bg = set.background;
    if (set.body) fromRules.body = set.body;
    const explicit = {};
    Object.entries(opts.colors || {}).forEach(([k, v]) => { explicit[k] = String(v).replace(/^#/, "").toUpperCase(); });
    const colors = Object.assign({}, base.colors, SCHEMES[schemeName] || {}, fromRules, explicit);
    if (!colors.darkBg) colors.darkBg = luminance(colors.primary) < 0.2 ? colors.primary : "111827";

    const size = Object.assign({}, base.size);
    if (set.title_size) { size.title = set.title_size; size.titleMin = Math.min(size.titleMin, set.title_size); }
    if (set.body_size) size.body = set.body_size;
    Object.assign(size, opts.size || {});

    this.t = {
      face: opts.face || set.face || base.face,
      colors,
      size,
      bodyWords: set.body_words || base.bodyWords,
    };
    this._checkColors();

    this.pres = new PptxGenJS();
    this.pres.layout = "LAYOUT_16x9";
    if (opts.title) this.pres.title = opts.title;
    if (opts.author) this.pres.author = opts.author;
    this.footer = opts.footer || set.footer || "";   // e.g. "Smith & Doe · SOLE 2025"
    this.sections = opts.sections || null;           // breadcrumb labels for long talks
  }

  /** A colour the audience cannot read is not a style choice. */
  _checkColors() {
    const c = this.t.colors;
    const need = [
      ["title colour", c.primary, c.bg, 4.5], ["accent colour", c.accent, c.bg, 4.5],
      ["body colour", c.body, c.bg, 7], ["source-line colour", c.muted, c.bg, 4.5],
      ["text on dark slides", c.onDark, c.darkBg, 7],
    ];
    need.forEach(([what, fg, bg, min]) => {
      if (!/^[0-9A-F]{6}$/i.test(fg) || !/^[0-9A-F]{6}$/i.test(bg)) {
        this.warnings.push(`deck: ${what} "${fg}" on "${bg}" is not a six-digit hex colour`);
      } else if (contrast(fg, bg) < min) {
        this.warnings.push(`deck: ${what} #${fg} on #${bg} is ${contrast(fg, bg).toFixed(1)}:1 — below ${min}:1, pick a darker shade`);
      }
    });
  }

  // ----- primitives -----

  _warn(msg) {
    this.warnings.push(`slide ${this.count}: ${msg}`);
  }

  _slide({ dark = false, numbered = true, notes, section } = {}) {
    const slide = this.pres.addSlide();
    this.count += 1;
    const c = this.t.colors;
    slide.background = { color: dark ? c.darkBg : c.bg };
    if (numbered) {
      slide.slideNumber = {
        x: W - M - 0.6, y: H - 0.42, w: 0.6, h: 0.3,
        fontFace: this.t.face, fontSize: 12, color: dark ? c.onDarkMuted : c.muted, align: "right",
      };
      if (this.footer) {
        slide.addText(this.footer, {
          objectName: "dk-footer", x: M, y: H - 0.42, w: 5.5, h: 0.3,
          fontFace: this.t.face, fontSize: 12, color: dark ? c.onDarkMuted : c.muted, margin: 0,
        });
      }
    }
    let top = 0.35;
    if (!dark && this.sections && section) top = this._breadcrumb(slide, section);
    if (notes) slide.addNotes(notes);
    else if (numbered) this._warn("no speaker notes");
    return { slide, top };
  }

  _breadcrumb(slide, current) {
    const c = this.t.colors;
    const parts = [];
    this.sections.forEach((s, i) => {
      const on = s === current;
      parts.push({ text: s, options: { bold: on, color: on ? c.accent : c.muted } });
      if (i < this.sections.length - 1) parts.push({ text: "   ›   ", options: { color: c.neutral } });
    });
    slide.addText(parts, {
      objectName: "dk-breadcrumb", x: M, y: 0.18, w: CW, h: 0.26,
      fontFace: this.t.face, fontSize: 12, margin: 0, valign: "middle",
    });
    return 0.55;
  }

  _kicker(slide, text, y, dark) {
    const c = this.t.colors;
    slide.addText(String(text).toUpperCase(), {
      objectName: "dk-kicker", x: M, y, w: CW, h: 0.28,
      fontFace: this.t.face, fontSize: this.t.size.kicker, bold: true, charSpacing: 1.5,
      color: dark ? c.onDarkMuted : c.accent, margin: 0, valign: "middle",
    });
    return y + 0.34;
  }

  /** Places the action title and returns the y where content may start. */
  _title(slide, text, y, { dark = false, w = CW, max, min } = {}) {
    const c = this.t.colors;
    const hi = max || this.t.size.title;
    const lo = min || this.t.size.titleMin;
    let pt = hi;
    while (pt > lo && estLines(text, w, pt, true) > 2) pt -= 1;
    const lines = estLines(text, w, pt, true);
    if (lines > 2) this._warn(`title runs to ~${lines} lines at ${pt} pt — sharpen the claim`);
    const h = lines * lineHeight(pt) + 0.08;
    slide.addText(text, {
      objectName: "dk-title", x: M, y, w, h,
      fontFace: this.t.face, fontSize: pt, bold: true, color: dark ? c.onDark : c.primary,
      align: "left", valign: "top", margin: 0,
    });
    return y + h + 0.22;
  }

  _cite(slide, text, dark) {
    const c = this.t.colors;
    slide.addText(text, {
      objectName: "dk-cite", x: M, y: H - 0.78, w: CW, h: 0.3,
      fontFace: this.t.face, fontSize: this.t.size.cite, color: dark ? c.onDarkMuted : c.muted,
      align: "left", valign: "bottom", margin: 0,
    });
  }

  /** Lowest y that body content may reach on this slide. */
  _floor(hasCite) {
    return H - (hasCite ? 0.86 : 0.5);
  }

  /**
   * bullets: array of
   *   "plain text"
   *   { label: "Bold lead", text: "rest of the line" }
   *   { text: "...", sub: ["second-level", ...] }
   *
   * A list whose items have bold leads is set without bullet markers: the lead
   * already marks each item. (PptxGenJS also writes conflicting paragraph
   * properties when a bulleted paragraph has more than one run, and PowerPoint
   * and LibreOffice then disagree about whether the bullet shows.)
   */
  _bullets(slide, bullets, box, { pt, dark = false, marker = true, name = "dk-body", gap } = {}) {
    const c = this.t.colors;
    const size = pt || this.t.size.body;
    const color = dark ? c.onDark : c.body;
    const hasLead = (list) => list.some((b) => typeof b !== "string" && (b.label || hasLead(b.sub || [])));
    const mark = marker && !hasLead(bullets);
    const runs = [];
    let est = 0;
    let wordCount = 0;
    const after = gap === undefined ? Math.round(size * 0.55) : gap;
    const push = (item, level) => {
      const o = typeof item === "string" ? { text: item } : item;
      const lead = o.label ? (/[:.?!—–-]$/.test(o.label.trim()) ? `${o.label} ` : `${o.label}: `) : "";
      const full = lead + (o.text || "");
      wordCount += words(full);
      const indentIn = (mark ? 0.3 : 0) + level * 0.3;
      est += estLines(full, box.w - indentIn, size, false) * lineHeight(size) + after / 72;
      const para = { breakLine: true, paraSpaceAfter: after };
      if (mark) para.bullet = { indent: 18 };
      if (level) para.indentLevel = level;
      if (lead) {
        runs.push({ text: lead, options: Object.assign({}, para, { bold: true, breakLine: false }) });
        runs.push({ text: o.text || "", options: Object.assign({}, para) });
      } else {
        runs.push({ text: o.text || "", options: para });
      }
      (o.sub || []).forEach((s) => push(s, level + 1));
    };
    bullets.forEach((b) => push(b, 0));
    if (runs.length) runs[runs.length - 1].options.breakLine = false;
    if (est > box.h + 0.05) {
      this._warn(`body needs ~${est.toFixed(1)}" but has ${box.h.toFixed(1)}" — cut words or split the slide; do not shrink the font`);
    }
    slide.addText(runs, {
      objectName: name, x: box.x, y: box.y, w: box.w, h: box.h,
      fontFace: this.t.face, fontSize: size, color, align: "left", valign: "top", margin: 0,
    });
    return { height: est, words: wordCount };
  }

  _checkWords(n) {
    if (n > this.t.bodyWords) {
      this._warn(`${n} body words (limit ${this.t.bodyWords}) — the audience will read instead of listen`);
    }
  }

  _callout(slide, text, x, y, wMax) {
    const c = this.t.colors;
    const pt = this.t.size.label;
    const w = Math.min(wMax, (text.length * pt * 0.56) / 72 + 0.3);
    const h = estLines(text, w - 0.2, pt, true) * lineHeight(pt) + 0.14;
    slide.addText(text, {
      objectName: "dk-annot", shape: this.pres.shapes.ROUNDED_RECTANGLE, rectRadius: 0.05,
      x, y, w, h, fill: { color: c.calloutFill }, line: { color: c.calloutLine, width: 1 },
      fontFace: this.t.face, fontSize: pt, bold: true, color: c.calloutText,
      align: "center", valign: "middle", margin: 4,
    });
    return h;
  }

  _calloutHeight(text, wMax) {
    const pt = this.t.size.label;
    const w = Math.min(wMax, (text.length * pt * 0.56) / 72 + 0.3);
    return estLines(text, w - 0.2, pt, true) * lineHeight(pt) + 0.14;
  }

  /**
   * exhibit:
   *   { type: "bar",  labels, values, highlight: index, axisTitle, valueFormat }
   *   { type: "line", labels, series: [{ name, values }], highlight: "name", axisTitle }
   *   { type: "image", path, alt }          // matplotlib PNG, rendered equation, diagram
   *   { type: "table", header: [...], rows: [[...]], highlightRow, highlightCol }
   * Any exhibit may add  annotation: "text"  (placed above it) or
   * annotation: { text, x, y }  (x, y as fractions of the exhibit box, for pointing at a feature).
   */
  _exhibit(slide, ex, outer) {
    // A callout with no explicit position gets its own strip above the exhibit,
    // so it can never cover a bar, a line or a data label.
    const note = ex.annotation
      ? (typeof ex.annotation === "string" ? { text: ex.annotation } : ex.annotation) : null;
    const floating = note && note.x !== undefined && note.y !== undefined;
    let box = outer;
    if (note && !floating) {
      const strip = this._calloutHeight(note.text, outer.w * 0.9) + 0.1;
      this._callout(slide, note.text, outer.x, outer.y, outer.w * 0.9);
      box = { x: outer.x, y: outer.y + strip, w: outer.w, h: outer.h - strip };
    }
    const c = this.t.colors;
    const face = this.t.face;
    const pt = this.t.size.label;
    const axis = {
      catAxisLabelFontFace: face, valAxisLabelFontFace: face,
      catAxisLabelFontSize: pt, valAxisLabelFontSize: pt,
      catAxisLabelColor: c.body, valAxisLabelColor: c.muted,
      valGridLine: { color: c.grid, size: 0.5 }, catGridLine: { style: "none" },
    };
    if (ex.axisTitle) {
      Object.assign(axis, {
        showValAxisTitle: true, valAxisTitle: ex.axisTitle, valAxisTitleFontFace: face,
        valAxisTitleFontSize: pt, valAxisTitleColor: c.muted,
      });
    }
    if (ex.type === "bar") {
      const focal = ex.highlight;
      const colors = ex.values.map((_, i) => (focal === undefined || i === focal ? c.accent : c.neutral));
      slide.addChart(this.pres.charts.BAR, [{ name: ex.name || "Series", labels: ex.labels, values: ex.values }],
        Object.assign({
          x: box.x, y: box.y, w: box.w, h: box.h, barDir: ex.horizontal ? "bar" : "col",
          chartColors: colors, barGapWidthPct: 60, showLegend: false,
          showValue: true, dataLabelFontFace: face, dataLabelFontSize: pt, dataLabelColor: c.body,
          dataLabelFormatCode: ex.valueFormat || "General", dataLabelPosition: "outEnd",
        }, axis));
    } else if (ex.type === "line") {
      const colors = ex.series.map((s) => (!ex.highlight || s.name === ex.highlight ? c.accent : c.neutral));
      slide.addChart(this.pres.charts.LINE,
        ex.series.map((s) => ({ name: s.name, labels: ex.labels, values: s.values })),
        Object.assign({
          x: box.x, y: box.y, w: box.w, h: box.h, chartColors: colors, lineSize: 3,
          lineDataSymbolSize: 7, showLegend: ex.series.length > 1, legendPos: "b",
          dataLabelFontFace: face, dataLabelFontSize: pt,
          legendFontFace: face, legendFontSize: pt, legendColor: c.body,
        }, axis));
    } else if (ex.type === "image") {
      const dim = imageSize(ex.path);
      let w = box.w, h = box.h, x = box.x, y = box.y;
      if (dim) {
        const r = dim.w / dim.h;
        if (w / h > r) { w = h * r; } else { h = w / r; y = box.y + (box.h - h) / 2; }
      }
      slide.addImage({ path: ex.path, x, y, w, h, altText: ex.alt || "" });
      if (!ex.alt) this._warn("image exhibit has no alt text");
    } else if (ex.type === "table") {
      const head = (ex.header || []).map((t) => ({
        text: String(t), options: { bold: true, color: c.primary, fill: { color: c.card } },
      }));
      const rows = ex.rows.map((r, ri) => r.map((cell, ci) => {
        const on = ri === ex.highlightRow || ci === ex.highlightCol;
        return { text: String(cell), options: on ? { bold: true, color: c.accent } : {} };
      }));
      const all = head.length ? [head].concat(rows) : rows;
      if (all.length * all[0].length > 24) this._warn("table has more than 24 cells — chart it or move detail to the appendix");
      slide.addTable(all, {
        x: box.x, y: box.y, w: box.w, fontFace: face, fontSize: pt, color: c.body,
        border: { type: "solid", pt: 0.5, color: c.grid }, valign: "middle", margin: [4, 6, 4, 6],
      });
    } else {
      throw new Error(`unknown exhibit type: ${ex.type}`);
    }
    if (floating) {
      // x and y are fractions of the exhibit box; check the render for overlap.
      this._callout(slide, note.text, box.x + note.x * box.w, box.y + note.y * box.h, box.w * 0.7);
    }
  }

  _head(o, kickerDefault) {
    const dark = !!o.dark;
    const { slide, top } = this._slide({ dark, notes: o.notes, section: o.section });
    let y = top;
    const kicker = o.kicker || kickerDefault;
    if (kicker) y = this._kicker(slide, kicker, y, dark);
    y = this._title(slide, o.title, y, { dark });
    if (o.cite) this._cite(slide, o.cite, dark);
    return { slide, top: y, bottom: this._floor(!!o.cite), dark };
  }

  // ----- shared slide types -----

  /** Empty slide with a measured title; draw between top and bottom yourself. */
  blank(o) {
    return this._head(o);
  }

  /** Text slide. Give `bullets`, or `groups: [{ header, bullets }]` for 2 stacked blocks. */
  content(o) {
    const { slide, top, bottom, dark } = this._head(o);
    const c = this.t.colors;
    let y = top;
    let total = 0;
    const groups = o.groups || [{ bullets: o.bullets || [] }];
    const anyLead = groups.some((g) => g.bullets.some((b) => typeof b !== "string" && b.label));
    const marker = o.marker !== false && !anyLead;
    groups.forEach((g, gi) => {
      if (g.header) {
        slide.addText(g.header, {
          objectName: "dk-header", x: M, y, w: CW, h: 0.38, fontFace: this.t.face,
          fontSize: this.t.size.header, bold: true, color: dark ? c.onDarkMuted : c.accent, margin: 0,
        });
        y += 0.46;
      }
      const remaining = groups.length - gi;
      const h = (bottom - y) / remaining - (remaining > 1 ? 0.5 : 0);
      const r = this._bullets(slide, g.bullets, { x: M, y, w: CW, h: Math.max(h, 0.4) },
        { dark, marker });
      total += r.words;
      y += Math.min(r.height, Math.max(h, 0.4)) + 0.2;
    });
    this._checkWords(total);
    return slide;
  }

  /** Two columns, each { header, bullets }. */
  twoColumn(o) {
    const { slide, top, bottom } = this._head(o);
    const c = this.t.colors;
    const gap = 0.5;
    const w = (CW - gap) / 2;
    let total = 0;
    const marker = ![o.left, o.right].some((col) => col.bullets.some((b) => typeof b !== "string" && b.label));
    [o.left, o.right].forEach((col, i) => {
      const x = M + i * (w + gap);
      let y = top;
      if (col.header) {
        slide.addText(col.header, {
          objectName: "dk-header", x, y, w, h: 0.38, fontFace: this.t.face,
          fontSize: this.t.size.header, bold: true, color: c.accent, margin: 0,
        });
        y += 0.46;
      }
      total += this._bullets(slide, col.bullets, { x, y, w, h: bottom - y }, { marker }).words;
    });
    this._checkWords(total);
    return slide;
  }

  /** One exhibit on the left, 2–3 takeaways on the right. One finding per slide. */
  result(o) {
    const { slide, top, bottom } = this._head(o);
    const takeaways = o.takeaways || [];
    const figW = takeaways.length ? 5.6 : CW;
    this._exhibit(slide, o.exhibit, { x: M, y: top, w: figW, h: bottom - top });
    if (takeaways.length) {
      const x = M + figW + 0.3;
      const r = this._bullets(slide, takeaways, { x, y: top + 0.1, w: W - M - x, h: bottom - top - 0.1 });
      this._checkWords(r.words);
    }
    if (!o.cite) this._warn("exhibit has no source line (own data? write \"Source: authors' calculations\")");
    return slide;
  }

  /** Clearly labelled backup slide. Same options as content() or result(). */
  appendix(o) {
    const label = o.label || "Appendix";
    const withKicker = Object.assign({}, o, { kicker: label });
    return o.exhibit ? this.result(withKicker) : this.content(withKicker);
  }

  /** Dark divider that orients the audience at the start of a part. */
  sectionDivider({ label, title, notes }) {
    const { slide } = this._slide({ dark: true, notes, numbered: true });
    if (label) this._kicker(slide, label, 2.0, true);
    slide.addText(title, {
      objectName: "dk-title", x: M, y: 2.35, w: CW, h: 1.0, fontFace: this.t.face, fontSize: 36,
      bold: true, color: this.t.colors.onDark, margin: 0, valign: "top",
    });
    return slide;
  }

  // ----- academic slide types -----

  titleSlide({ title, venue, authors, affiliations, notes }) {
    const { slide } = this._slide({ dark: true, numbered: false, notes });
    const c = this.t.colors;
    const y = this._title(slide, title, 1.3, { dark: true, w: 8.6, max: 34, min: 26 });
    if (venue) {
      slide.addText(venue, {
        objectName: "dk-venue", x: M, y: y + 0.1, w: 8.6, h: 0.36, fontFace: this.t.face,
        fontSize: 16, color: c.onDarkMuted, margin: 0,
      });
    }
    const who = [authors, affiliations].filter(Boolean).join("\n");
    if (who) {
      slide.addText(who, {
        objectName: "dk-authors", x: M, y: H - 1.45, w: 8.6, h: 0.9, fontFace: this.t.face,
        fontSize: 16, color: c.onDark, margin: 0, valign: "bottom",
      });
    }
    return slide;
  }

  /** The research question on its own slide, with the contribution beneath it. */
  question({ title, question, contribution, notes, section }) {
    const { slide, top, bottom } = this._head({ title, notes, section });
    const c = this.t.colors;
    const pt = this.t.size.body + 2;
    const h = Math.max(1.1, estLines(question, CW - 0.6, pt, false) * lineHeight(pt) + 0.4);
    slide.addText(question, {
      objectName: "dk-question", shape: this.pres.shapes.RECTANGLE, x: M, y: top, w: CW, h,
      fill: { color: c.card }, line: { color: c.accent, width: 1.25 },
      fontFace: this.t.face, fontSize: pt, color: c.primary, align: "left", valign: "middle", margin: 14,
    });
    if (contribution) {
      const r = this._bullets(slide, [{ label: "Contribution", text: contribution }],
        { x: M, y: top + h + 0.3, w: CW, h: bottom - top - h - 0.3 }, { marker: false });
      this._checkWords(r.words + words(question));
    }
    return slide;
  }

  /**
   * Last presented slide. Stays up for the whole Q&A.
   * takeaways: [{ label, text }]   contact: "email  |  paper link"   qr: path to PNG
   */
  conclusions({ takeaways, contact, qr, notes, title }) {
    const { slide } = this._slide({ dark: true, notes });
    const c = this.t.colors;
    let y = this._kicker(slide, "Conclusions", 0.35, true);
    if (title) y = this._title(slide, title, y, { dark: true });
    const numbered = takeaways.map((t, i) => (typeof t === "string"
      ? { text: `${i + 1}. ${t}` } : { label: `${i + 1}. ${t.label}`, text: t.text }));
    const r = this._bullets(slide, numbered, { x: M, y: y + 0.1, w: CW, h: H - 1.3 - y },
      { dark: true, marker: false, gap: 16 });
    this._checkWords(r.words);
    if (contact) {
      slide.addText(contact, {
        objectName: "dk-contact", x: M, y: H - 0.95, w: qr ? 7.6 : CW - 0.8, h: 0.36,
        fontFace: this.t.face, fontSize: 16, color: c.onDarkMuted, margin: 0, valign: "middle",
      });
    } else {
      this._warn("conclusions slide has no contact line or paper link");
    }
    if (qr) slide.addImage({ path: qr, x: W - M - 1.1, y: H - 1.75, w: 1.1, h: 1.1, altText: "QR code linking to the paper" });
    return slide;
  }

  /** Full citations. Splits across slides automatically; never shrinks below 13 pt. */
  references({ refs, title = "References" }) {
    const pt = this.t.size.cite;
    const room = H - 1.55;
    const pages = [[]];
    let used = 0;
    refs.forEach((r) => {
      const h = estLines(r, CW, pt, false) * lineHeight(pt) + 0.12;
      if (used + h > room && pages[pages.length - 1].length) { pages.push([]); used = 0; }
      pages[pages.length - 1].push(r);
      used += h;
    });
    pages.forEach((page, i) => {
      const { slide } = this._slide({ notes: "Reference list. Not presented; shown on request." });
      const label = pages.length > 1 ? `${title} (${i + 1}/${pages.length})` : title;
      slide.addText(label, {
        objectName: "dk-title", x: M, y: 0.35, w: CW, h: 0.5, fontFace: this.t.face, fontSize: 24,
        bold: true, color: this.t.colors.primary, margin: 0,
      });
      slide.addText(page.map((r, j) => ({ text: r, options: { breakLine: j < page.length - 1, paraSpaceAfter: 8 } })), {
        objectName: "dk-refs", x: M, y: 1.0, w: CW, h: room, fontFace: this.t.face, fontSize: pt,
        color: this.t.colors.body, margin: 0, valign: "top",
      });
    });
  }

  // ----- pitch slide types -----

  /** Company name and a one-line description. The only section that is always one slide. */
  pitchTitle({ company, oneLiner, round, contact, notes }) {
    const { slide } = this._slide({ dark: true, numbered: false, notes });
    const c = this.t.colors;
    if (words(oneLiner) > 14) this._warn("one-liner is over 14 words — say what you do in one breath");
    slide.addText(company, {
      objectName: "dk-company", x: M, y: 1.45, w: CW, h: 1.0, fontFace: this.t.face, fontSize: 54,
      bold: true, color: c.onDark, margin: 0, valign: "bottom",
    });
    slide.addText(oneLiner, {
      objectName: "dk-title", x: M, y: 2.6, w: CW, h: 1.1, fontFace: this.t.face, fontSize: 28,
      color: c.onDark, margin: 0, valign: "top",
    });
    const foot = [round, contact].filter(Boolean).join("   ·   ");
    if (foot) {
      slide.addText(foot, {
        objectName: "dk-contact", x: M, y: H - 0.95, w: CW, h: 0.36, fontFace: this.t.face,
        fontSize: 16, color: c.onDarkMuted, margin: 0,
      });
    }
    return slide;
  }

  /** A claim and up to three short supporting points. */
  statement(o) {
    const pts = o.points || [];
    if (pts.length > 3) this._warn("more than three supporting points — one idea per slide");
    return this.content(Object.assign({}, o, { bullets: pts, marker: pts.length > 1 }));
  }

  /** One number the investor should remember, with the label that makes it mean something. */
  hero({ kicker, title, number, label, support, cite, notes }) {
    const { slide, top, bottom } = this._head({ kicker, title, cite, notes });
    const c = this.t.colors;
    const pt = String(number).length > 7 ? 72 : this.t.size.hero;
    const nh = lineHeight(pt) + 0.05;
    slide.addText(String(number), {
      objectName: "dk-hero", x: M, y: top, w: CW, h: nh, fontFace: this.t.face, fontSize: pt,
      bold: true, color: c.accent, margin: 0, valign: "middle",
    });
    const lh = estLines(label, CW, this.t.size.body, true) * lineHeight(this.t.size.body) + 0.1;
    slide.addText(label, {
      objectName: "dk-body", x: M, y: top + nh + 0.05, w: CW, h: lh, fontFace: this.t.face,
      fontSize: this.t.size.body, bold: true, color: c.body, margin: 0, valign: "top",
    });
    if (support) {
      const sy = top + nh + 0.05 + lh + 0.08;
      const sh = estLines(support, CW, this.t.size.label + 2, false) * lineHeight(this.t.size.label + 2);
      if (sy + sh > bottom + 0.1) this._warn("hero slide is overfull — shorten the label or drop the support line");
      slide.addText(support, {
        objectName: "dk-support", x: M, y: sy, w: CW, h: Math.max(0.4, bottom - sy),
        fontFace: this.t.face, fontSize: this.t.size.label + 2, color: c.muted, margin: 0, valign: "top",
      });
    }
    this._checkWords(words(label) + words(support || ""));
    return slide;
  }

  /**
   * 2–4 side-by-side tiles: market sizing steps, business model, how it works, use of funds.
   * tiles: [{ value: "$4.2B", label: "US clinics", note: "38k clinics × $110k/yr" }]
   */
  tiles({ kicker, title, tiles, numbered = false, cite, notes }) {
    const { slide, top, bottom } = this._head({ kicker, title, cite, notes });
    const c = this.t.colors;
    const n = tiles.length;
    if (n < 2 || n > 4) this._warn("tiles work with 2–4 items");
    const gap = 0.3;
    const w = (CW - gap * (n - 1)) / n;
    const h = Math.min(bottom - top, 3.0);
    const valuePt = n >= 4 ? 30 : 38;
    const labelPt = this.t.size.label + 2;
    const notePt = this.t.size.label;
    let total = 0;
    tiles.forEach((tile, i) => {
      const x = M + i * (w + gap);
      const value = numbered ? String(i + 1) : tile.value;
      total += words(tile.label || "") + words(tile.note || "");
      const runs = [];
      if (value !== undefined) {
        runs.push({ text: String(value), options: { fontSize: valuePt, bold: true, color: c.accent, breakLine: true, paraSpaceAfter: 6 } });
      }
      runs.push({ text: tile.label || "", options: { fontSize: labelPt, bold: true, color: c.body, breakLine: !!tile.note, paraSpaceAfter: 6 } });
      if (tile.note) runs.push({ text: tile.note, options: { fontSize: notePt, color: c.muted } });
      const need = (value !== undefined ? lineHeight(valuePt) : 0)
        + estLines(tile.label || "", w - 0.4, labelPt, true) * lineHeight(labelPt)
        + (tile.note ? estLines(tile.note, w - 0.4, notePt, false) * lineHeight(notePt) : 0) + 0.55;
      if (need > h) this._warn(`tile ${i + 1} text needs ~${need.toFixed(1)}" but the tile is ${h.toFixed(1)}" tall — shorten it`);
      slide.addText(runs, {
        objectName: "dk-tile", shape: this.pres.shapes.RECTANGLE, x, y: top, w, h,
        fill: { color: c.card }, line: { color: c.card, width: 0 },
        fontFace: this.t.face, align: "left", valign: "top", margin: 14,
      });
    });
    this._checkWords(total);
    return slide;
  }

  /** Founders only. proof: one quantified line each — what they built, shipped, sold or published. */
  team({ kicker = "Team", title, members, cite, notes }) {
    const { slide, top, bottom } = this._head({ kicker, title, cite, notes });
    const c = this.t.colors;
    const n = members.length;
    if (n > 4) this._warn("more than four people on the team slide — founders only");
    const gap = 0.35;
    const w = (CW - gap * (n - 1)) / n;
    let total = 0;
    members.forEach((m, i) => {
      const x = M + i * (w + gap);
      let y = top;
      if (m.photo) {
        slide.addImage({ path: m.photo, x, y, w: 1.1, h: 1.1, altText: `Photo of ${m.name}` });
        y += 1.25;
      }
      const proof = [].concat(m.proof || []);
      if (!proof.some((p) => /\d/.test(p))) this._warn(`${m.name}: no number in the proof line — quantify a past win`);
      total += proof.reduce((s, p) => s + words(p), 0);
      const runs = [
        { text: m.name, options: { fontSize: this.t.size.header, bold: true, color: c.primary, breakLine: true } },
        { text: m.role, options: { fontSize: this.t.size.label, color: c.accent, bold: true, breakLine: true, paraSpaceAfter: 8 } },
      ];
      proof.forEach((p, j) => runs.push({
        text: p, options: { fontSize: this.t.size.label + 2, color: c.body, breakLine: j < proof.length - 1, paraSpaceAfter: 6 },
      }));
      slide.addText(runs, {
        objectName: "dk-member", x, y, w, h: bottom - y, fontFace: this.t.face, margin: 0, valign: "top",
      });
    });
    this._checkWords(total);
    return slide;
  }

  /** How much, and what it buys. No valuation, cap or other terms on the slide. */
  ask({ kicker = "The ask", title, amount, milestones, contact, notes }) {
    const { slide, top, bottom } = this._head({ kicker, title, notes });
    const c = this.t.colors;
    if (/valuation|pre-money|post-money|\bcap\b/i.test([title].concat(milestones || []).join(" "))) {
      this._warn("fundraising terms on the ask slide — keep valuation and cap for the conversation");
    }
    slide.addText(String(amount), {
      objectName: "dk-hero", x: M, y: top, w: 3.6, h: 1.3, fontFace: this.t.face, fontSize: 60,
      bold: true, color: c.accent, margin: 0, valign: "top",
    });
    const r = this._bullets(slide, milestones || [], { x: M + 3.9, y: top + 0.05, w: CW - 3.9, h: bottom - top - 0.6 });
    this._checkWords(r.words);
    if (contact) {
      slide.addText(contact, {
        objectName: "dk-contact", x: M, y: bottom - 0.4, w: CW - 0.8, h: 0.36, fontFace: this.t.face,
        fontSize: 16, color: c.muted, margin: 0, valign: "middle",
      });
    } else {
      this._warn("ask slide has no contact line");
    }
    return slide;
  }

  // ----- output -----

  async save(path) {
    await this.pres.writeFile({ fileName: path });
    const out = [`wrote ${path} (${this.count} slides, ${this.mode} mode)`];
    if (this.warnings.length) {
      out.push(`${this.warnings.length} build warning(s):`);
      this.warnings.forEach((w) => out.push(`  - ${w}`));
    }
    if (this.rules && this.rules.rules.length) {
      out.push(`house rules from ${this.rules.file} — confirm the deck follows each:`);
      this.rules.rules.forEach((r) => out.push(`  □ ${r}`));
    }
    out.push(`next: python3 scripts/lint_deck.py ${path} --mode ${this.mode}${this.rules ? ` --rules ${this.rules.file}` : ""}`);
    console.log(out.join("\n"));
    return this.warnings;
  }
}

function createDeck(opts) {
  return new Deck(opts);
}

module.exports = { createDeck, NEEDS, THEMES, SCHEMES, loadRules, contrast, estLines, words };
