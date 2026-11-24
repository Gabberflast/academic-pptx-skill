#!/usr/bin/env python3
"""
extract_paper.py — pull the raw material for a talk out of a paper.

    python3 scripts/extract_paper.py paper.pdf --out paper_out
    python3 scripts/extract_paper.py main.tex  --out paper_out      # or a folder of .tex/.bib

Writes into the output folder:
    paper.json   title, abstract, sections, figure and table captions, the
                 reference list, sentences that carry numbers, and the full text
    outline.md   a worksheet to fill in before building any slide
    figures/     embedded images from a PDF (when pdfimages is installed)
    pages/       a render of each PDF page that carries a figure or table caption
                 (when pdftoppm is installed), for cropping vector figures

Everything here is a first pass by pattern matching. Section breaks, captions
and reference splits will sometimes be wrong: read paper.json against the paper
before relying on it. The script never invents content; a field it cannot find
is left empty.

Requires: pdftotext (poppler) or pypdf for PDFs. Nothing extra for LaTeX.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HEADINGS = (
    "abstract|introduction|background|motivation|related work|literature review|literature|"
    "prior work|data|data and methods|data and sample|sample|methods?|methodology|materials and methods|"
    "empirical strategy|identification|identification strategy|model|theory|theoretical framework|"
    "framework|experimental design|experiment|experiments|setup|approach|estimation|"
    "results?|main results|findings|evaluation|analysis|empirical results|robustness|robustness checks|"
    "mechanisms?|heterogeneity|discussion|limitations|implications|policy implications|"
    "conclusions?|concluding remarks|summary|future work|acknowledge?ments|references|bibliography|"
    "works cited|literature cited|appendix|online appendix|supplementary materials?"
)
NUMBERED = re.compile(r"^\s*((?:1\d|[1-9]|[IVX]{1,5})(?:\.[1-9]\d?)*)[.)]?\s+([A-Z][^\n]{2,90})$")
NAMED = re.compile(rf"^\s*({HEADINGS})\s*$", re.I)
REF_HEAD = re.compile(r"^\s*(?:\d{1,2}[.)]?\s+)?(references|bibliography|works cited|literature cited)\s*$", re.I)
AFTER_REFS = re.compile(r"^\s*(?:[A-Z]\.?\s+)?(appendix|online appendix|supplementary|supplemental)\b", re.I)
CAPTION = re.compile(r"^\s*(Figure|Fig\.|Table)\s*([A-Z]?\d+[a-z]?)\s*[.:|—–-]\s*(.*)$")
NUMBER_CUE = re.compile(
    r"\d\s*%|\bpercent(age)?\b|\bp\s*[<=>]\s*0?\.\d|\bCI\b|confidence interval|standard deviations?|\bSD\b|"
    r"\bN\s*=\s*\d|\bn\s*=\s*\d|\d(\.\d+)?\s*(×|x\b|times|-fold)|significant|\bR2\b|R-squared|\bF1\b|accuracy", re.I)


# ---------------------------------------------------------------- PDF


def pdf_pages(path):
    """Text of each page. Tries pdftotext, then pypdf."""
    if shutil.which("pdftotext"):
        try:
            raw = subprocess.run(["pdftotext", str(path), "-"], capture_output=True, text=True, check=True).stdout
            pages = raw.split("\f")
            if pages and not pages[-1].strip():
                pages = pages[:-1]
            if any(p.strip() for p in pages):
                return pages
        except Exception:
            pass
    try:
        from pypdf import PdfReader
    except ImportError:
        sys.exit("need pdftotext (poppler-utils) or pypdf to read a PDF")
    return [(pg.extract_text() or "") for pg in PdfReader(str(path)).pages]


def pdf_title(path, pages):
    try:
        from pypdf import PdfReader
        t = (PdfReader(str(path)).metadata or {}).get("/Title")
        if t and len(t.strip()) > 8 and not re.search(r"\.(pdf|docx?|tex|dvi)$|untitled|microsoft word", t, re.I):
            return t.strip()
    except Exception:
        pass
    lines = [ln.strip() for ln in (pages[0] if pages else "").split("\n")]
    block = []
    for ln in lines:
        if not ln:
            if block:
                break
            continue
        if re.search(r"arxiv|working paper|preprint|vol\.|doi:|https?://|^\d+$", ln, re.I) and not block:
            continue
        looks_like_names = (block and len(ln.split()) <= 5 and not re.search(r"[:?]", ln)
                            and all(w[:1].isupper() or w.lower() in ("and", "de", "van", "von", "&") for w in ln.split()))
        if looks_like_names:
            break
        block.append(ln)
        if len(block) == 3:
            break
    return " ".join(block)


def split_sections(pages):
    bare_number = re.compile(r"^\s*((?:1\d|[1-9]|[IVX]{1,5})(?:\.[1-9]\d?)*)\.?\s*$")
    sections, cur = [], None
    for pno, page in enumerate(pages, start=1):
        lines = page.split("\n")
        last_text = max((i for i, ln in enumerate(lines) if ln.strip()), default=-1)
        skip = set()
        for i, ln in enumerate(lines):
            if i in skip:
                continue
            head = None
            m = NUMBERED.match(ln)
            b = bare_number.match(ln)
            if m and len(m.group(2).split()) <= 12 and not m.group(2).rstrip().endswith((".", ",", ";")):
                head = (m.group(1), m.group(2).strip())
            elif NAMED.match(ln):
                head = ("", ln.strip())
            elif b and i != last_text:
                # pdftotext often puts "2" and "Data and Design" on separate lines
                j = next((k for k in range(i + 1, min(i + 4, len(lines))) if lines[k].strip()), None)
                if j is not None:
                    nxt = lines[j].strip()
                    if (nxt[:1].isupper() and len(nxt.split()) <= 10 and not re.search(r"[.,;:%)]$", nxt)
                            and not re.search(r"\d", nxt)):
                        head = (b.group(1), nxt)
                        skip.add(j)
            if head:
                cur = {"number": head[0], "heading": head[1], "page": pno, "text": ""}
                sections.append(cur)
            elif cur is not None:
                cur["text"] += ln + "\n"
    for s in sections:
        body = re.sub(r"\s+", " ", s["text"]).strip()
        s["words"] = len(body.split())
        s["text"] = body[:1500] + (" …" if len(body) > 1500 else "")
    return sections


def find_abstract(full):
    m = re.search(r"\babstract\b[\s.:—–-]*\n?(.{80,4000}?)(?=\n\s*(?:keywords?|jel\b|key words|1\.?\s+introduction|i\.\s+introduction|introduction\s*\n))",
                  full, re.I | re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


def find_captions(pages):
    figs, tabs = [], []
    for pno, page in enumerate(pages, start=1):
        lines = page.split("\n")
        for i, ln in enumerate(lines):
            m = CAPTION.match(ln)
            if not m:
                continue
            cap = [m.group(3).strip()]
            for nxt in lines[i + 1:i + 5]:
                if cap[-1].endswith(".") or not nxt.strip() or CAPTION.match(nxt):
                    break
                cap.append(nxt.strip())
            item = {"label": f"{'Table' if m.group(1) == 'Table' else 'Figure'} {m.group(2)}",
                    "caption": " ".join(cap)[:400], "page": pno}
            target = tabs if m.group(1) == "Table" else figs
            if not any(x["label"] == item["label"] for x in target):
                target.append(item)
    return figs, tabs


def split_references(pages):
    lines, started = [], False
    for page in pages:
        for ln in page.split("\n"):
            if not started:
                if REF_HEAD.match(ln):
                    started = True
                continue
            if AFTER_REFS.match(ln):
                return _group_refs(lines)
            lines.append(ln)
    return _group_refs(lines)


def _group_refs(lines):
    start = re.compile(r"^\s*(?:\[\d{1,3}\]|\d{1,3}\.\s|[A-Z][A-Za-z'’\-]+,\s+(?:[A-Z]\.|[A-Z][a-z]+)|[A-Z][A-Za-z'’\-]+\s+[A-Z]\.?,"
                       r"|(?:[A-Z]\.\s?){1,3}[A-Z][A-Za-z'’\-]+[,. ])")
    ended = re.compile(r"(?:(?:19|20)\d{2}[a-z]?|\d+\s*[–-]\s*\d+)\.\s*$")
    refs, cur = [], ""
    for ln in lines:
        s = ln.strip()
        if not s:
            if cur:
                refs.append(cur)
                cur = ""
            continue
        if re.fullmatch(r"\d{1,3}", s):          # page number
            continue
        if cur and (start.match(ln) or (ended.search(cur) and s[:1].isupper())):
            refs.append(cur)
            cur = s
        else:
            cur = (cur[:-1] + s) if cur.endswith("-") else (cur + " " + s if cur else s)
    if cur:
        refs.append(cur)
    return [r for r in (re.sub(r"\s+", " ", r).strip() for r in refs)
            if len(r) > 25 and re.search(r"(19|20)\d{2}", r)]


def key_numbers(pages, limit=60):
    out = []
    for pno, page in enumerate(pages, start=1):
        if REF_HEAD.search(page) and pno > len(pages) * 0.6:
            break
        text = re.sub(r"\s+", " ", page)
        for sent in re.split(r"(?<=[.!?])\s+(?=[A-Z(])", text):
            if 40 < len(sent) < 400 and NUMBER_CUE.search(sent):
                out.append({"page": pno, "sentence": sent.strip()})
                if len(out) >= limit:
                    return out
    return out


def pdf_images(path, out, caption_pages):
    made = {"figures": [], "pages": []}
    if shutil.which("pdfimages"):
        fdir = out / "figures"
        fdir.mkdir(exist_ok=True)
        subprocess.run(["pdfimages", "-png", str(path), str(fdir / "img")], capture_output=True)
        for f in sorted(fdir.glob("img-*.png")):
            if f.stat().st_size < 8000:          # logos, rules, glyph fragments
                f.unlink()
            else:
                made["figures"].append(str(f.relative_to(out)))
    if shutil.which("pdftoppm") and caption_pages:
        pdir = out / "pages"
        pdir.mkdir(exist_ok=True)
        for p in sorted(caption_pages):
            stem = pdir / f"page-{p:03d}"
            subprocess.run(["pdftoppm", "-r", "150", "-png", "-f", str(p), "-l", str(p), "-singlefile",
                            str(path), str(stem)], capture_output=True)
            if Path(str(stem) + ".png").exists():
                made["pages"].append(str(Path(str(stem) + ".png").relative_to(out)))
    return made


def from_pdf(path, out):
    pages = pdf_pages(path)
    full = "\n".join(pages)
    if len(full.split()) < 200:
        print("warning: very little text extracted — the PDF may be scanned; run OCR first", file=sys.stderr)
    figs, tabs = find_captions(pages)
    data = {
        "source": str(path), "kind": "pdf", "pages": len(pages),
        "title": pdf_title(path, pages), "abstract": find_abstract(full),
        "sections": split_sections(pages), "figures": figs, "tables": tabs,
        "references": split_references(pages), "key_numbers": key_numbers(pages),
    }
    data["files"] = pdf_images(path, out, {x["page"] for x in figs + tabs})
    data["text"] = full
    return data


# ---------------------------------------------------------------- LaTeX


def _braced(src, start):
    """Text of the {...} group that opens at src[start] == '{'."""
    depth, i = 0, start
    while i < len(src):
        if src[i] == "{" and (i == 0 or src[i - 1] != "\\"):
            depth += 1
        elif src[i] == "}" and src[i - 1] != "\\":
            depth -= 1
            if depth == 0:
                return src[start + 1:i]
        i += 1
    return src[start + 1:]


def _macro(src, name):
    out = []
    for m in re.finditer(rf"\\{name}\*?\s*(?:\[[^\]]*\])?\s*\{{", src):
        out.append((m.start(), _braced(src, m.end() - 1)))
    return out


def detex(s):
    s = re.sub(r"\\(?:cite[a-z]*|ref|eqref|label|autoref|cref)\*?(?:\[[^\]]*\])*\{[^}]*\}", "", s)
    s = re.sub(r"\\(?:textbf|textit|emph|texttt|textsc|underline|mbox|text)\{([^{}]*)\}", r"\1", s)
    s = re.sub(r"\\(?:begin|end)\{[^}]*\}(?:\[[^\]]*\])?", " ", s)
    s = s.replace("\\%", "%").replace("\\&", "&").replace("\\$", "$").replace("\\_", "_").replace("~", " ")
    s = s.replace("\\times", "×").replace("\\pm", "±").replace("\\leq", "≤").replace("\\geq", "≥")
    s = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?", " ", s)
    s = re.sub(r"[{}$]", "", s)
    return re.sub(r"\s+", " ", s).strip()


def read_tex(path):
    root = path if path.is_dir() else path.parent
    if path.is_dir():
        mains = [p for p in sorted(path.rglob("*.tex")) if "\\documentclass" in p.read_text(errors="ignore")]
        if not mains:
            sys.exit("no .tex file with \\documentclass found in that folder")
        path = mains[0]
    seen = set()

    def load(p):
        if p in seen or not p.exists():
            return ""
        seen.add(p)
        src = re.sub(r"(?<!\\)%.*", "", p.read_text(encoding="utf-8", errors="ignore"))

        def sub(m):
            child = root / m.group(1)
            return load(child if child.suffix else child.with_suffix(".tex"))
        return re.sub(r"\\(?:input|include)\{([^}]+)\}", sub, src)

    return load(path), root, path


def bib_entries(root, src):
    refs = []
    for bib in sorted(root.rglob("*.bib")):
        text = bib.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", text):
            if m.group(1).lower() in ("comment", "string", "preamble"):
                continue
            body = _braced(text, text.index("{", m.start()))
            f = {}
            for fm in re.finditer(r"(\w+)\s*=\s*(\{|\")", body):
                if fm.group(2) == "{":
                    val = _braced(body, fm.end() - 1)
                else:
                    end = body.find('"', fm.end())
                    val = body[fm.end():end]
                f[fm.group(1).lower()] = detex(val)
            if not f.get("author") and not f.get("title"):
                continue
            venue = f.get("journal") or f.get("booktitle") or f.get("publisher") or f.get("institution") or f.get("howpublished") or ""
            bits = [f"{f.get('author', '').replace(' and ', ', ')} ({f.get('year', 'n.d.')}).", f"{f.get('title', '')}."]
            if venue:
                tail = venue
                if f.get("volume"):
                    tail += f", {f['volume']}" + (f"({f['number']})" if f.get("number") else "")
                if f.get("pages"):
                    tail += f", {f['pages'].replace('--', '–')}"
                bits.append(tail + ".")
            refs.append({"key": m.group(2), "text": " ".join(b for b in bits if b.strip(". "))})
    if not refs:
        for m in re.finditer(r"\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}(.*?)(?=\\bibitem|\\end\{thebibliography\})", src, re.S):
            refs.append({"key": m.group(1), "text": detex(m.group(2))})
    cited = set()
    for m in re.finditer(r"\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]+)\}", src):
        cited |= {k.strip() for k in m.group(1).split(",")}
    for r in refs:
        r["cited_in_paper"] = r["key"] in cited
    return refs


def from_tex(path, out):
    src, root, main = read_tex(path)
    title = _macro(src, "title")
    am = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", src, re.S)
    heads = []
    for name, level in (("section", 1), ("subsection", 2)):
        heads += [(pos, level, detex(txt)) for pos, txt in _macro(src, name)]
    heads.sort()
    sections = []
    for i, (pos, level, head) in enumerate(heads):
        end = heads[i + 1][0] if i + 1 < len(heads) else len(src)
        body = detex(src[pos:end])
        body = body[len(head):].strip() if body.startswith(head) else body
        sections.append({"number": "", "heading": head, "level": level, "words": len(body.split()),
                         "text": body[:1500] + (" …" if len(body) > 1500 else "")})
    figs, tabs = [], []
    for env, target, word in (("figure", figs, "Figure"), ("table", tabs, "Table")):
        for i, m in enumerate(re.finditer(rf"\\begin\{{{env}\*?\}}(.*?)\\end\{{{env}\*?\}}", src, re.S), start=1):
            block = m.group(1)
            cap = _macro(block, "caption")
            files = re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", block)
            label = re.search(r"\\label\{([^}]+)\}", block)
            target.append({"label": f"{word} {i}", "tex_label": label.group(1) if label else "",
                           "caption": detex(cap[0][1])[:400] if cap else "", "files": files})
    refs = bib_entries(root, src)
    text = detex(src)
    sents = [{"sentence": s.strip()} for s in re.split(r"(?<=[.!?])\s+(?=[A-Z(])", text)
             if 40 < len(s) < 400 and NUMBER_CUE.search(s)][:60]
    return {
        "source": str(main), "kind": "latex", "title": detex(title[0][1]) if title else "",
        "abstract": detex(am.group(1)) if am else "", "sections": sections, "figures": figs, "tables": tabs,
        "references": [r["text"] for r in refs], "reference_keys": refs, "key_numbers": sents,
        "files": {"figures": sorted({f for x in figs for f in x["files"]}), "pages": []}, "text": text,
    }


# ---------------------------------------------------------------- worksheet


def worksheet(d):
    def rows(items, fmt):
        return "\n".join(fmt(x) for x in items) or "_(none found — check the paper)_"

    sec = rows(d["sections"], lambda s: f"- {s.get('number', '')} {s['heading']}".rstrip()
               + (f" (p. {s['page']})" if s.get("page") else "") + f" — {s['words']} words")
    fig = rows(d["figures"] + d["tables"], lambda f: f"| {f['label']} | {f['caption'][:90]} | "
               f"{f.get('page', '') or ', '.join(f.get('files', []))} | main / appendix / drop | rebuild / crop |")
    nums = rows(d["key_numbers"][:25], lambda k: f"- {k['sentence']}" + (f" (p. {k['page']})" if k.get("page") else ""))
    refs = rows(d["references"], lambda r: f"- [ ] {r}")
    return f"""# Talk worksheet — {d['title'] or '(title not found)'}

Fill this in before building a single slide. Source: `{d['source']}`.
Everything below was pulled out by pattern matching. Check it against the paper.

## 1. The slot

- Venue and audience:
- Minutes for the talk (excluding questions):
- Slide budget (at most one per minute):

## 2. The one claim

Write the single sentence this talk has to land. Not the topic — the claim.

>

The abstract, for reference:

> {d['abstract'] or '(abstract not found)'}

## 3. Ghost deck

Action titles only, in order. Read them aloud: do they make the argument without the slides?
Every number must come from the paper — give the page.

| # | Action title (a full sentence) | Exhibit | Source in paper |
|---|--------------------------------|---------|-----------------|
| 1 | (title slide: the claim as a statement or question) | — | — |
| 2 |  |  |  |
| 3 | (the research question, on its own slide) |  |  |
| 4 |  |  |  |
| … |  |  |  |
| n | Conclusions: 2–4 numbered takeaways | — | — |

## 4. What the paper contains

{sec}

## 5. Figures and tables — decide each one

Use at most one per slide. Rebuild from data where you can; crop from the page
render only when you cannot, and never show paper-sized labels.

| Exhibit | Caption | Page / file | Decision | How |
|---------|---------|-------------|----------|-----|
{fig}

## 6. Sentences that carry numbers

Candidates for results slides. Copy numbers from here, not from memory.

{nums}

## 7. References — tick only the ones a slide will cite

Copy them exactly. Do not add a reference that is not in this list unless you
have the source in front of you.

{refs}

## 8. Likely questions → appendix slides

List three to five questions this audience will ask, and the backup slide for each.

1.
2.
3.
"""


def main(argv=None):
    ap = argparse.ArgumentParser(description="Extract talk material from a paper (PDF or LaTeX).")
    ap.add_argument("paper", help="a .pdf, a .tex file, or a folder of LaTeX sources")
    ap.add_argument("--out", default="paper_out", help="output folder (default: paper_out)")
    a = ap.parse_args(argv)
    src = Path(a.paper)
    if not src.exists():
        sys.exit(f"not found: {src}")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    data = from_pdf(src, out) if src.suffix.lower() == ".pdf" else from_tex(src, out)
    (out / "paper.json").write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "outline.md").write_text(worksheet(data), encoding="utf-8")
    print(f"title:      {data['title'] or '(not found)'}")
    print(f"abstract:   {'found' if data['abstract'] else 'NOT FOUND'}")
    print(f"sections:   {len(data['sections'])}")
    print(f"figures:    {len(data['figures'])}   tables: {len(data['tables'])}")
    print(f"references: {len(data['references'])}")
    print(f"numbers:    {len(data['key_numbers'])} sentences")
    print(f"wrote {out / 'paper.json'} and {out / 'outline.md'}")
    for k, v in data["files"].items():
        if v and data["kind"] == "pdf":
            print(f"            {len(v)} file(s) in {out / k}/")
    empty = [k for k in ("title", "abstract", "sections", "references") if not data[k]]
    if empty:
        print(f"check by hand: could not find {', '.join(empty)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
