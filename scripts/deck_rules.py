#!/usr/bin/env python3
"""
deck_rules.py — read and update deck_rules.md, the user's own rules for their decks.

deck_rules.md sits beside the user's work (their project folder or repository), not
inside this skill. It records what they want beyond the skill's baseline: their
colours and typeface, limits they prefer, checks to switch off, words to ban,
sections to require, and house rules written in plain sentences.

    python3 scripts/deck_rules.py init                       # create deck_rules.md here
    python3 scripts/deck_rules.py show   [--mode pitch]      # what applies right now
    python3 scripts/deck_rules.py add "Always put the lab logo on the title slide" --scope academic
    python3 scripts/deck_rules.py remove "lab logo"          # drop rules containing this text
    python3 scripts/deck_rules.py set accent 0F766E [--scope pitch]
    python3 scripts/deck_rules.py unset accent [--scope pitch]
    python3 scripts/deck_rules.py from-template brand.pptx   # read colours and fonts from a deck or .potx

All commands take --file PATH (default: ./deck_rules.md).

The kit (createDeck({ rules: "deck_rules.md" })) and the linter (--rules, or a
deck_rules.md beside the .pptx) read the Settings blocks. The written rules are
for the person or model building the deck; the linter prints them as a checklist.
"""

import argparse
import datetime
import re
import sys
import zipfile
from pathlib import Path

DEFAULT_FILE = "deck_rules.md"
SCOPES = ("all", "academic", "pitch")

# Settings the kit and linter understand. Anything else is kept but reported as unknown.
SETTINGS = {
    "scheme": "named colour scheme (see customization.md)",
    "primary": "hex colour for titles and dark slides",
    "accent": "hex colour for the focal data series, headers and section labels",
    "background": "hex colour of content slides",
    "body": "hex colour of body text",
    "face": "typeface, one for the whole deck",
    "footer": "short text at the bottom-left of every slide",
    "title_size": "title size in points",
    "body_size": "body size in points",
    "body_words": "body words per slide before the linter warns",
    "title_words": "title words before the linter warns",
    "body_min": "smallest body type the linter accepts, in points",
    "title_min": "smallest title type the linter accepts, in points",
    "max_slides": "presented slides before the linter warns",
    "minutes": "default talk length for the one-slide-per-minute check",
    "disable": "comma-separated linter rules to switch off",
    "banned_words": "comma-separated words or phrases the linter flags",
    "required_sections": "comma-separated section labels or title phrases that must appear",
}
LIST_KEYS = {"disable", "banned_words", "required_sections"}
COLOR_KEYS = {"primary", "accent", "background", "body"}
NUMBER_KEYS = {"title_size", "body_size", "body_words", "title_words", "body_min", "title_min", "max_slides", "minutes"}

# Checks that protect against invented or missing content. A rules file cannot switch these off.
LOCKED_RULES = {"PLACEHOLDER", "A-CITE-MISSING", "NUMBER-NOT-IN-SOURCE", "OFF-SLIDE"}

TEMPLATE = """# Deck rules

My own rules for decks built with the academic-pitch-pptx skill. They add to the
skill's baseline; where the two differ, these win. What I ask for in a
conversation wins over both.

They cannot switch off the checks that guard against invented content: unfilled
placeholders, citations with no reference, numbers that are not in the source.

## Settings

Read by the slide kit and the linter. One `key: value` per line. Delete a line
to go back to the skill's default.

```text
```

## Settings: academic

```text
```

## Settings: pitch

```text
```

## Rules

Read by whoever builds the deck. One rule per line, starting with `- [all]`,
`- [academic]` or `- [pitch]`.

"""

HEAD_RE = re.compile(r"^##\s+(.*?)\s*$")
KV_RE = re.compile(r"^\s*([A-Za-z_]+)\s*:\s*(.*?)\s*$")
RULE_RE = re.compile(r"^\s*[-*]\s+(?:\[(\w+)\]\s*)?(.*?)\s*$")
ADDED_RE = re.compile(r"\s*\(added \d{4}-\d{2}-\d{2}\)\s*$")


def _clean(key, value):
    value = value.strip().strip("\"'")
    if key in COLOR_KEYS:
        return value.lstrip("#").upper()
    if key in LIST_KEYS:
        return [v.strip().strip("\"'") for v in value.split(",") if v.strip()]
    if key in NUMBER_KEYS:
        try:
            n = float(value)
            return int(n) if n == int(n) else n
        except ValueError:
            return value
    return value


def parse(text):
    """Returns {"settings": {scope: {key: value}}, "rules": [(scope, text)]}."""
    settings = {s: {} for s in SCOPES}
    rules = []
    section = None
    fenced = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            fenced = not fenced
            continue
        h = None if fenced else HEAD_RE.match(line)
        if h:
            name = h.group(1).lower()
            if name.startswith("settings"):
                scope = name.split(":", 1)[1].strip() if ":" in name else "all"
                section = ("settings", scope if scope in SCOPES else "all")
            elif name.startswith("rules"):
                section = ("rules", None)
            else:
                section = None
            continue
        if not section or not line.strip():
            continue
        if section[0] == "settings":
            m = KV_RE.match(line)
            # inside the code block any key is read; outside it, only known ones (so prose is not misread)
            if m and m.group(2) and (fenced or m.group(1).lower() in SETTINGS):
                key = m.group(1).lower()
                settings[section[1]][key] = _clean(key, m.group(2))
        elif section[0] == "rules":
            m = RULE_RE.match(line)
            if m and m.group(2) and line.lstrip()[:1] in "-*":
                scope = (m.group(1) or "all").lower()
                rules.append((scope if scope in SCOPES else "all", ADDED_RE.sub("", m.group(2))))
    return {"settings": settings, "rules": rules}


def load_rules(path, mode=None):
    """
    What applies to one mode: general settings overlaid with that mode's settings.
    Returns {"path", "settings", "rules", "unknown", "locked"} or None when there is no file.
    """
    p = Path(path)
    if not p.is_file():
        return None
    data = parse(p.read_text(encoding="utf-8"))
    merged = dict(data["settings"]["all"])
    if mode in ("academic", "pitch"):
        merged.update(data["settings"][mode])
    rules = [t for scope, t in data["rules"] if scope == "all" or mode is None or scope == mode]
    disable = [d.upper() for d in merged.get("disable", [])]
    locked = [d for d in disable if d in LOCKED_RULES]
    merged["disable"] = [d for d in disable if d not in LOCKED_RULES]
    if not merged["disable"]:
        merged.pop("disable")
    return {"path": str(p), "settings": merged, "rules": rules,
            "unknown": sorted(k for k in merged if k not in SETTINGS), "locked": locked}


def find_rules(start):
    """deck_rules.md beside the given file or folder, else in the current folder."""
    start = Path(start)
    for folder in (start if start.is_dir() else start.parent, Path.cwd()):
        cand = folder / DEFAULT_FILE
        if cand.is_file():
            return cand
    return None


# ---------------------------------------------------------------- editing


def _read(path):
    p = Path(path)
    if not p.is_file():
        sys.exit(f"{p} not found. Create it with:  python3 scripts/deck_rules.py init --file {p}")
    return p.read_text(encoding="utf-8")


def _settings_heading(scope):
    return "## Settings" if scope == "all" else f"## Settings: {scope}"


def _set(text, scope, key, value):
    """Sets, replaces or (value=None) removes one key in the block for scope. Returns new text."""
    lines = text.splitlines()
    heading = _settings_heading(scope).lower()
    start = next((i for i, ln in enumerate(lines) if ln.strip().lower() == heading), None)
    if start is None:
        if value is None:
            return text
        rules_at = next((i for i, ln in enumerate(lines) if ln.strip().lower().startswith("## rules")), len(lines))
        lines[rules_at:rules_at] = [_settings_heading(scope), "", "```text", f"{key}: {value}", "```", ""]
        return "\n".join(lines) + "\n"
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    for i in range(start + 1, end):
        m = KV_RE.match(lines[i])
        if m and m.group(1).lower() == key:
            if value is None:
                del lines[i]
            else:
                lines[i] = f"{key}: {value}"
            return "\n".join(lines) + "\n"
    if value is None:
        return text
    fences = [i for i in range(start + 1, end) if lines[i].strip().startswith("```")]
    if len(fences) >= 2:
        lines.insert(fences[-1], f"{key}: {value}")
    else:
        lines[start + 1:start + 1] = ["", "```text", f"{key}: {value}", "```"]
    return "\n".join(lines) + "\n"


def cmd_init(a):
    p = Path(a.file)
    if p.exists():
        sys.exit(f"{p} already exists")
    p.write_text(TEMPLATE, encoding="utf-8")
    print(f"created {p}")


def cmd_add(a):
    text = _read(a.file)
    rule = " ".join(a.text.split())
    existing = [t.lower() for s, t in parse(text)["rules"] if s == a.scope]
    if rule.lower() in existing:
        print("already recorded")
        return
    if not re.search(r"(?m)^##\s+Rules", text):
        text = text.rstrip("\n") + "\n\n## Rules\n\n"
    text = text.rstrip("\n")
    gap = "\n" if text.splitlines()[-1].lstrip()[:1] in ("-", "*") else "\n\n"
    text += f"{gap}- [{a.scope}] {rule} (added {datetime.date.today().isoformat()})\n"
    Path(a.file).write_text(text, encoding="utf-8")
    print(f"recorded for {a.scope}: {rule}")


def cmd_remove(a):
    text = _read(a.file)
    needle = a.text.lower()
    out, dropped, in_rules = [], [], False
    for ln in text.splitlines():
        h = HEAD_RE.match(ln)
        if h:
            in_rules = h.group(1).lower().startswith("rules")
        if in_rules and ln.lstrip()[:1] in ("-", "*") and needle in ln.lower():
            dropped.append(ln.strip())
            continue
        out.append(ln)
    if not dropped:
        sys.exit("no rule contains that text")
    Path(a.file).write_text("\n".join(out) + "\n", encoding="utf-8")
    for d in dropped:
        print(f"removed: {d}")


def cmd_set(a):
    key = a.key.lower()
    if key not in SETTINGS:
        sys.exit(f"unknown setting '{key}'. Known: {', '.join(sorted(SETTINGS))}")
    value = " ".join(a.value)
    if key in COLOR_KEYS:
        value = value.lstrip("#").upper()
        if not re.fullmatch(r"[0-9A-F]{6}", value):
            sys.exit(f"{key} needs a six-digit hex colour, e.g. 0F766E")
    if key in NUMBER_KEYS and not re.fullmatch(r"\d+(\.\d+)?", value):
        sys.exit(f"{key} needs a number")
    if key == "disable":
        asked = [v.strip().upper() for v in value.split(",") if v.strip()]
        blocked = [v for v in asked if v in LOCKED_RULES]
        if blocked:
            print(f"not switched off (these guard against invented content): {', '.join(blocked)}")
        value = ", ".join(v for v in asked if v not in LOCKED_RULES)
        if not value:
            return
    Path(a.file).write_text(_set(_read(a.file), a.scope, key, value), encoding="utf-8")
    print(f"{a.scope}: {key} = {value}")


def cmd_unset(a):
    Path(a.file).write_text(_set(_read(a.file), a.scope, a.key.lower(), None), encoding="utf-8")
    print(f"{a.scope}: {a.key.lower()} back to the default")


def describe(rules, mode):
    out = [f"{rules['path']}" + (f" — {mode} mode" if mode else " — all modes")]
    s = rules["settings"]
    if s:
        out.append("settings:")
        for k in sorted(s):
            v = ", ".join(map(str, s[k])) if isinstance(s[k], list) else s[k]
            out.append(f"  {k}: {v}" + ("   (not a known setting — ignored)" if k in rules["unknown"] else ""))
    else:
        out.append("settings: none (skill defaults apply)")
    if rules["locked"]:
        out.append(f"cannot be switched off: {', '.join(rules['locked'])}")
    out.append("written rules:" if rules["rules"] else "written rules: none")
    out += [f"  - {r}" for r in rules["rules"]]
    return "\n".join(out)


def cmd_show(a):
    r = load_rules(a.file, a.mode)
    if r is None:
        sys.exit(f"{a.file} not found")
    print(describe(r, a.mode))


def read_template(path):
    """Theme colours and fonts from a .pptx or .potx."""
    with zipfile.ZipFile(path) as z:
        names = sorted(n for n in z.namelist() if re.match(r"ppt/theme/theme\d*\.xml$", n))
        if not names:
            raise ValueError("no theme found in that file")
        xml = z.read(names[0]).decode("utf-8", "ignore")
    colors = {}
    for tag in ("dk1", "lt1", "dk2", "lt2", "accent1", "accent2", "accent3", "accent4", "accent5", "accent6"):
        m = re.search(rf"<a:{tag}>(.*?)</a:{tag}>", xml, re.S)
        if not m:
            continue
        c = re.search(r'<a:srgbClr val="([0-9A-Fa-f]{6})"', m.group(1)) or re.search(r'lastClr="([0-9A-Fa-f]{6})"', m.group(1))
        if c:
            colors[tag] = c.group(1).upper()
    fonts = {}
    for tag in ("majorFont", "minorFont"):
        m = re.search(rf"<a:{tag}>.*?<a:latin typeface=\"([^\"]*)\"", xml, re.S)
        if m and m.group(1):
            fonts[tag] = m.group(1)
    return colors, fonts


def _lum(h):
    def ch(v):
        v /= 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a, b):
    hi, lo = sorted((_lum(a), _lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def cmd_from_template(a):
    try:
        colors, fonts = read_template(a.template)
    except Exception as e:
        sys.exit(f"could not read {a.template}: {e}")
    print(f"theme colours in {a.template}:")
    for k, v in colors.items():
        print(f"  {k:<8} #{v}   contrast on white {contrast(v, 'FFFFFF'):.1f}:1")
    for k, v in fonts.items():
        print(f"  {k:<8} {v}")
    usable = [colors[k] for k in ("dk2", "accent1", "accent2", "accent3", "accent4", "accent5", "accent6")
              if k in colors and contrast(colors[k], "FFFFFF") >= 4.5]
    primary = colors.get("dk2") if colors.get("dk2") in usable else (usable[0] if usable else None)
    accent = next((c for c in usable if c != primary), None)
    print("\nsuggested settings (confirm with the user before saving):")
    if primary:
        print(f"  python3 scripts/deck_rules.py set primary {primary}")
    if accent:
        print(f"  python3 scripts/deck_rules.py set accent {accent}")
    face = fonts.get("minorFont") or fonts.get("majorFont")
    if face:
        print(f"  python3 scripts/deck_rules.py set face \"{face}\"")
    if not usable:
        print("  none of the theme colours is dark enough for text on white (4.5:1); ask for a darker brand colour")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Read and update deck_rules.md.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name, fn, **kw):
        sp = sub.add_parser(name, **kw)
        sp.add_argument("--file", default=DEFAULT_FILE)
        sp.set_defaults(fn=fn)
        return sp

    add("init", cmd_init, help="create deck_rules.md")
    sp = add("show", cmd_show, help="print what applies")
    sp.add_argument("--mode", choices=["academic", "pitch"])
    sp = add("add", cmd_add, help="record a written rule")
    sp.add_argument("text")
    sp.add_argument("--scope", choices=SCOPES, default="all")
    sp = add("remove", cmd_remove, help="drop written rules containing some text")
    sp.add_argument("text")
    sp = add("set", cmd_set, help="set a setting")
    sp.add_argument("key")
    sp.add_argument("value", nargs="+")
    sp.add_argument("--scope", choices=SCOPES, default="all")
    sp = add("unset", cmd_unset, help="remove a setting")
    sp.add_argument("key")
    sp.add_argument("--scope", choices=SCOPES, default="all")
    sp = add("from-template", cmd_from_template, help="read colours and fonts from a .pptx or .potx")
    sp.add_argument("template")
    a = ap.parse_args(argv)
    a.fn(a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
