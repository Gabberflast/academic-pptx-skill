#!/usr/bin/env python3
"""
End-to-end checks for the kit, the linter and the paper extractor.

    python3 tests/run_tests.py

Builds the two example decks (needs node + pptxgenjs), builds deliberately bad
decks with python-pptx, and asserts which rules fire. No test framework needed.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parent.parent
LINT = ROOT / "scripts" / "lint_deck.py"
EXTRACT = ROOT / "scripts" / "extract_paper.py"
PAPER = ROOT / "tests" / "fixtures" / "paper" / "main.tex"
passed = failed = 0


def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ok    {name}")
    else:
        failed += 1
        print(f"  FAIL  {name}  {detail}")


def lint(path, *args):
    r = subprocess.run([sys.executable, str(LINT), str(path), "--json", *args], capture_output=True, text=True)
    if not r.stdout.strip():
        raise RuntimeError(r.stderr)
    data = json.loads(r.stdout)
    data["exit"] = r.returncode
    data["rules"] = {f["rule"] for f in data["findings"]}
    data["error_rules"] = {f["rule"] for f in data["findings"] if f["level"] == "error"}
    return data


def node_env():
    env = dict(os.environ)
    if shutil.which("npm"):
        root = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()
        env["NODE_PATH"] = os.pathsep.join(filter(None, [root, env.get("NODE_PATH", "")]))
    return env


def build_example(script, out):
    r = subprocess.run(["node", str(ROOT / "examples" / script), str(out)], capture_output=True, text=True, env=node_env())
    return r.returncode == 0, r.stdout + r.stderr


def box(slide, text, x, y, w, h, pt, bold=False):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tb.text_frame.word_wrap = True
    run = tb.text_frame.paragraphs[0].add_run()
    run.text = text
    run.font.size = Pt(pt)
    run.font.bold = bold
    run.font.name = "Arial"
    return tb


def new_prs():
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(10), Inches(5.625)
    return prs, prs.slide_layouts[6]


def bad_academic(path):
    prs, blank = new_prs()
    s = prs.slides.add_slide(blank)
    box(s, "A study of tutoring", 0.5, 1.5, 9, 1, 32, True)
    s = prs.slides.add_slide(blank)                       # topic label + wall of text + tiny type
    box(s, "Results", 0.5, 0.3, 9, 0.6, 26, True)
    box(s, " ".join(["word"] * 80), 0.5, 1.2, 9, 3.5, 11)
    s = prs.slides.add_slide(blank)                       # citation with no reference, placeholder
    box(s, "Tutoring effects fade quickly in most earlier studies", 0.5, 0.3, 9, 0.9, 26, True)
    box(s, "Gains halve within two years (Nguyen et al., 2018). Effect size: [[NEEDS: pooled estimate]]", 0.5, 1.4, 9, 2, 20)
    s = prs.slides.add_slide(blank)
    box(s, "Thank you!", 0.5, 2.0, 9, 1, 40, True)
    prs.save(path)


def bad_pitch(path):
    prs, blank = new_prs()
    s = prs.slides.add_slide(blank)
    box(s, "Acme", 0.5, 1.5, 9, 1, 48, True)
    box(s, "AI for logistics", 0.5, 2.6, 9, 0.6, 28)
    s = prs.slides.add_slide(blank)
    box(s, "TRACTION", 0.5, 0.3, 9, 0.3, 14, True)
    box(s, "Customers love our revolutionary platform", 0.5, 0.7, 9, 0.9, 32, True)
    box(s, "Strong momentum across every segment", 0.5, 2.0, 9, 1, 24)
    s = prs.slides.add_slide(blank)
    box(s, "MARKET", 0.5, 0.3, 9, 0.3, 14, True)
    box(s, "Logistics is a massive market with no competitors", 0.5, 0.7, 9, 0.9, 32, True)
    box(s, "Usage is up 40% and growing", 0.5, 2.0, 9, 1, 24)
    s = prs.slides.add_slide(blank)
    box(s, "THE ASK", 0.5, 0.3, 9, 0.3, 14, True)
    box(s, "We are raising a seed round at a $20M valuation cap", 0.5, 0.7, 9, 0.9, 32, True)
    box(s, "Funds go to hiring and growth", 0.5, 2.0, 9, 1, 24)
    prs.save(path)


def main():
    tmp = Path(tempfile.mkdtemp(prefix="deck_tests_"))
    print(f"working in {tmp}")

    print("examples")
    if shutil.which("node"):
        ok, log = build_example("build_academic_example.js", tmp / "academic.pptx")
        check("academic example builds", ok, log[-300:])
        check("academic example builds without kit warnings", "build warning" not in log, log[-400:])
        if ok:
            a = lint(tmp / "academic.pptx", "--mode", "academic", "--minutes", "12")
            check("academic example has no errors", a["errors"] == 0, str(a["findings"]))
            check("academic example has no warnings", a["warnings"] == 0, str(a["findings"]))
            check("auto mode picks academic", lint(tmp / "academic.pptx")["mode"] == "academic")
            check("over budget at 5 minutes", "A-BUDGET" in lint(tmp / "academic.pptx", "--mode", "academic", "--minutes", "5")["error_rules"])
        ok, log = build_example("build_pitch_example.js", tmp / "pitch.pptx")
        check("pitch example builds", ok, log[-300:])
        check("pitch example builds without kit warnings", "build warning" not in log, log[-400:])
        if ok:
            p = lint(tmp / "pitch.pptx", "--mode", "pitch")
            check("pitch example has no errors", p["errors"] == 0, str(p["findings"]))
            check("pitch example has no warnings", p["warnings"] == 0, str(p["findings"]))
            check("auto mode picks pitch", lint(tmp / "pitch.pptx")["mode"] == "pitch")
            secs = {g["section"] for g in p["ghost_deck"]}
            check("pitch sections recognised", {"problem", "solution", "traction", "market", "team", "ask"} <= secs, str(secs))
    else:
        print("  skip  node not installed")

    print("bad academic deck")
    bad_academic(tmp / "bad_academic.pptx")
    b = lint(tmp / "bad_academic.pptx", "--mode", "academic")
    check("exit status 1", b["exit"] == 1)
    for rule in ("TITLE-LABEL", "WORDS", "FONT-SMALL", "PLACEHOLDER", "THANKS-SLIDE", "A-CONCLUSIONS", "A-REFERENCES"):
        check(f"flags {rule}", rule in b["error_rules"], str(sorted(b["rules"])))
    check("flags SLIDE-NUMBERS", "SLIDE-NUMBERS" in b["rules"])

    print("bad pitch deck")
    bad_pitch(tmp / "bad_pitch.pptx")
    b = lint(tmp / "bad_pitch.pptx", "--mode", "pitch")
    for rule in ("P-TRACTION-NUMBER", "P-BUZZWORDS", "P-NO-COMPETITION", "P-GROWTH-WINDOW", "P-MARKET-SIZE",
                 "P-ASK-TERMS", "P-SECTION-MISSING"):
        check(f"flags {rule}", rule in b["rules"], str(sorted(b["rules"])))

    print("paper extraction (LaTeX)")
    out = tmp / "paper_out"
    r = subprocess.run([sys.executable, str(EXTRACT), str(PAPER), "--out", str(out)], capture_output=True, text=True)
    check("extractor runs", r.returncode == 0, r.stderr[-300:])
    d = json.loads((out / "paper.json").read_text())
    check("title", d["title"].startswith("Does Tutoring Last?"), d["title"])
    check("abstract", "2,400 students" in d["abstract"])
    check("sections", [s["heading"] for s in d["sections"]][:3] == ["Introduction", "Data and Design", "Results"])
    check("figures and tables", len(d["figures"]) == 2 and len(d["tables"]) == 1)
    check("references from .bib", len(d["references"]) == 3 and "Okafor" in d["references"][0], str(d["references"]))
    check("uncited .bib entry is marked", [k["cited_in_paper"] for k in d["reference_keys"]] == [True, True, False])
    check("worksheet written", "Ghost deck" in (out / "outline.md").read_text())

    if (tmp / "academic.pptx").exists():
        print("number tracing")
        ok_src = lint(tmp / "academic.pptx", "--mode", "academic", "--source", str(out / "paper.json"))
        check("example numbers all found in the paper", "NUMBER-NOT-IN-SOURCE" not in ok_src["rules"], str(ok_src["findings"]))
        prs = Presentation(str(tmp / "academic.pptx"))
        for sh in prs.slides[4].shapes:
            if sh.has_text_frame:
                for para in sh.text_frame.paragraphs:
                    for run in para.runs:
                        run.text = run.text.replace("95% CI [5, 13]", "95% CI [5, 17.4]")
        prs.save(str(tmp / "tampered.pptx"))
        t = lint(tmp / "tampered.pptx", "--mode", "academic", "--source", str(out / "paper.json"))
        hit = [f for f in t["findings"] if f["rule"] == "NUMBER-NOT-IN-SOURCE"]
        check("a changed number is caught", len(hit) == 1 and hit[0]["slide"] == 5 and "17.4" in hit[0]["message"], str(hit))

    print(f"\n{passed} passed, {failed} failed")
    shutil.rmtree(tmp, ignore_errors=True)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
