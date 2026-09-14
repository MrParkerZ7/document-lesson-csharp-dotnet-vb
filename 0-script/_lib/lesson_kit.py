# -*- coding: utf-8 -*-
"""
lesson_kit.py — shared building blocks for the lesson PDFs.

Every lesson module (0-script/lessons/lesson_NN.py) returns a `brief_pdf` blocks list rendered
as PDF format 00 (full-spectrum). brief_pdf is a report renderer; a programming lesson also needs
things it does not ship, and they live here:

  * syntax-highlighted code panels (Pygments, inline styles — Edge prints with no stylesheet fetch)
  * C#-vs-VB (or Java-vs-C#) side-by-side panels
  * code pulled from the compiled samples by #region name, so a PDF can never show code that
    does not build — `verify_samples.py` builds exactly the files these panels read
  * the concept-mapping table ("you know X → in .NET it is Y") and the shared chip vocabulary
  * measured numbers (lines of code) computed from the samples at build time

Contract: 1-analysis/spec_lesson-pdfs/_standard.md
"""
from __future__ import annotations

import datetime as _dt
import pathlib
import re
import textwrap

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

from brief_pdf import esc, link, pill, tag  # noqa: F401  (re-exported for lesson modules)

REPO = pathlib.Path(__file__).resolve().parents[2]
BUILD_DATE = _dt.date.today()

# ── chip vocabulary — every lesson prints legend() in its first section ─────────────────────
SAME = pill("Same idea", "green")        # the concept transfers 1:1 from your stack
RENAMED = pill("Renamed", "sky")         # same concept, different name / syntax
DIFFERENT = pill("Different", "amber")   # a real behavioural difference to learn
TRAP = pill("Trap", "red")               # looks the same, behaves differently — bites migrants
VERIFIED = pill("Verified", "teal")      # fact checked against an official source (linked)
ESTIMATE = pill("Estimate", "slate")     # the author's judgement, not a measurement
MEASURED = pill("Measured", "indigo")    # computed from this repository at build time
KIND = {"same": SAME, "renamed": RENAMED, "different": DIFFERENT, "trap": TRAP}

T_CS = tag("C#", "violet")
T_VB = tag("VB", "blue")
T_JVM = tag("Java/Kotlin", "amber")
T_TS = tag("TypeScript", "sky")
T_PY = tag("Python", "teal")
T_RUNTIME = tag("runtime", "slate")
T_TOOLING = tag("tooling", "indigo")
T_CLOUD = tag("cloud", "rose")
T_LEGACY = tag("legacy", "navy")
T_ARCH = tag("architecture", "green")


def legend(*extra):
    """The KEY row. Pass the tags the lesson actually uses after the fixed status chips."""
    return {"type": "legend", "label": "KEY",
            "chips": [SAME, RENAMED, DIFFERENT, TRAP, VERIFIED, ESTIMATE, MEASURED, *extra]}


# ── code panels ────────────────────────────────────────────────────────────────────────────
LANG = {  # key -> (pygments lexer, header label, header colour)
    "csharp": ("csharp", "C#", "#6D28D9"),
    "vb": ("vbnet", "Visual Basic", "#1D4ED8"),
    "java": ("java", "Java — for comparison", "#B45309"),
    "kotlin": ("kotlin", "Kotlin — for comparison", "#9A3412"),
    "typescript": ("typescript", "TypeScript — for comparison", "#0369A1"),
    "python": ("python", "Python — for comparison", "#0F766E"),
    "xml": ("xml", "MSBuild / XML", "#334155"),
    "json": ("json", "JSON", "#334155"),
    "shell": ("bash", "Terminal", "#1F2937"),
    "yaml": ("yaml", "YAML", "#9D174D"),
    "terraform": ("terraform", "Terraform", "#5B21B6"),
    "sql": ("sql", "SQL", "#155E75"),
    "text": ("text", "Text", "#334155"),
}
EXT = {".cs": "csharp", ".vb": "vb", ".csproj": "xml", ".vbproj": "xml", ".props": "xml",
       ".targets": "xml", ".slnx": "xml", ".json": "json", ".java": "java", ".kt": "kotlin",
       ".ts": "typescript", ".py": "python", ".yml": "yaml", ".yaml": "yaml", ".tf": "terraform",
       ".sql": "sql", ".http": "text", ".feature": "text"}

_FMT = HtmlFormatter(nowrap=True, noclasses=True, style="vs")

CSS = """
.codeblk { margin:8px 0 10px; }
.codeh { font-weight:700; font-size:10pt; color:#1A237E; margin:12px 0 4px; border-bottom:2px solid #C5CAE9;
         padding-bottom:2px; break-after:avoid; page-break-after:avoid; }
.code { border:1px solid #CBD5E1; border-radius:6px; overflow:hidden; background:#FBFCFE; }
.code.keep { break-inside:avoid; page-break-inside:avoid; }
.code .ch { display:flex; justify-content:space-between; align-items:center; gap:8px; padding:3px 9px;
            font-size:7.6pt; color:#fff; }
.code .ch .cl { font-weight:700; white-space:nowrap; }
.code .ch .cf { opacity:.92; font-family:Consolas,'Cascadia Mono',monospace; font-size:7.2pt;
                overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.code pre { margin:0; padding:6px 10px; font-family:Consolas,'Cascadia Mono','Courier New',monospace;
            font-size:7.9pt; line-height:1.32; white-space:pre-wrap; word-break:break-word; color:#111827; }
.cmp { display:grid; grid-template-columns:1fr 1fr; gap:8px; }
.cmp.keep { break-inside:avoid; page-break-inside:avoid; }
.cmp .code pre { font-size:7.3pt; }
.two, .three { break-inside:avoid; page-break-inside:avoid; }
.lnote { font-size:8.4pt; color:#374151; background:#F8FAFC; border-left:3px solid #C5CAE9;
         padding:5px 9px; border-radius:0 4px 4px 0; margin-top:5px; break-before:avoid; }
"""


def style_block():
    """Must be the FIRST block of every lesson — injects the code-panel stylesheet."""
    return {"type": "html", "_kind": "style", "html": "<style>%s</style>" % CSS}


def _width_warn(s, limit):
    """Warn (stderr) when a panel has lines wider than the standard allows — they wrap and look broken."""
    wide = [ln for ln in s["src"].splitlines() if len(ln) > limit]
    if wide:
        import sys
        print(f"  ! lesson_kit: panel {s.get('file') or s.get('label') or s['lang']!r} has {len(wide)} line(s) "
              f"wider than {limit} chars (widest {max(map(len, wide))})", file=sys.stderr)


def _highlight(src, lang):
    lexer = get_lexer_by_name(LANG[lang][0], stripnl=False, ensurenl=False)
    return highlight(src, lexer, _FMT).rstrip("\n")


def _panel(s, keep):
    _lex, default_label, accent = LANG[s["lang"]]
    n = s["src"].count("\n") + 1
    keep = (n <= 32) if keep is None else keep
    cf = f'<span class="cf">{esc(s["file"])}</span>' if s.get("file") else ""
    return (f'<div class="code{" keep" if keep else ""}"><div class="ch" style="background:{accent}">'
            f'<span class="cl">{esc(s.get("label") or default_label)}</span>{cf}</div>'
            f'<pre>{_highlight(s["src"], s["lang"])}</pre></div>')


_REGION_START = re.compile(r'^\s*#region\s+"?(.+?)"?\s*$', re.I)   # C# `#region x` · VB `#Region "x"`
_REGION_ANY_START = re.compile(r"^\s*#region\b", re.I)
_REGION_END = re.compile(r"^\s*#\s*end\s*region\b", re.I)          # C# `#endregion` · VB `#End Region`


def snippet(relpath, region=None):
    """Text of a sample file (repo-relative path), or of one named #region inside it.

    Region directive lines are removed from the result and the block is dedented. A missing file
    or region raises — a lesson must fail to build rather than print code that is not in the
    samples."""
    path = REPO / relpath
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    if region is not None:
        start = next((i for i, ln in enumerate(lines)
                      if (m := _REGION_START.match(ln)) and m.group(1) == region), None)
        if start is None:
            raise KeyError(f"region {region!r} not found in {relpath}")
        depth, end = 0, None
        for j in range(start + 1, len(lines)):
            if _REGION_ANY_START.match(lines[j]):
                depth += 1
            elif _REGION_END.match(lines[j]):
                if depth == 0:
                    end = j
                    break
                depth -= 1
        if end is None:
            raise ValueError(f"region {region!r} in {relpath} is never closed")
        lines = lines[start + 1:end]
    lines = [ln for ln in lines if not (_REGION_ANY_START.match(ln) or _REGION_END.match(ln))]
    return textwrap.dedent("\n".join(lines)).strip("\n")


def from_sample(relpath, region=None, label=None):
    """A code source read from the compiled samples. `relpath` is repo-relative, forward slashes."""
    rp = pathlib.PurePosixPath(relpath)
    lang = EXT.get(rp.suffix.lower(), "text")
    parts = rp.parts[1:] if rp.parts and rp.parts[0].startswith("lesson-") else rp.parts
    shown = "/".join(parts) + (f"  ·  #region {region}" if region else "")
    return {"src": snippet(relpath, region), "lang": lang, "label": label, "file": shown}


def from_text(src, lang, label=None, file=None):
    """A code source written inline — only for comparison code in another language (Java, Kotlin,
    TypeScript, Python) or for terminal commands. C# and VB always come from_sample()."""
    return {"src": textwrap.dedent(src).strip("\n"), "lang": lang, "label": label, "file": file}


def code(s, *, heading=None, note=None, keep=None):
    """One code panel as an html block. `note` is raw html — the reading of the code."""
    _width_warn(s, 100)
    h = f'<div class="codeh">{esc(heading)}</div>' if heading else ""
    nt = f'<div class="lnote">{note}</div>' if note else ""
    return {"type": "html", "_kind": "code", "_langs": [s["lang"]],
            "html": f'<div class="codeblk">{h}{_panel(s, keep)}{nt}</div>'}


def compare(left, right, *, heading=None, note=None, keep=None):
    """Two code panels side by side (keep lines under ~62 characters so nothing wraps)."""
    _width_warn(left, 62)
    _width_warn(right, 62)
    n = max(left["src"].count("\n"), right["src"].count("\n")) + 1
    keep = (n <= 40) if keep is None else keep
    h = f'<div class="codeh">{esc(heading)}</div>' if heading else ""
    nt = f'<div class="lnote">{note}</div>' if note else ""
    return {"type": "html", "_kind": "compare", "_langs": [left["lang"], right["lang"]],
            "html": (f'<div class="codeblk">{h}<div class="cmp{" keep" if keep else ""}">'
                     f'{_panel(left, False)}{_panel(right, False)}</div>{nt}</div>')}


# ── tables & numbers ───────────────────────────────────────────────────────────────────────
def mapping(heading, rows, cols=("You already know", "In .NET", "Kind", "Watch for")):
    """Concept map. rows = [(known, dotnet, kind, watch_for)], kind in same|renamed|different|trap."""
    return {"type": "table", "_kind": "mapping", "heading": heading, "cols": list(cols),
            "rows": [[a, b, KIND[k], w] for a, b, k, w in rows]}


# ── lint — the minimums of _standard.md §3, checked before every render ─────────────────────
KNOWN_LANGS = {"java", "kotlin", "typescript", "python"}
_CLASSDEF_FAMILIES = {"flowchart", "graph", "stateDiagram", "stateDiagram-v2", "classDiagram"}


def _strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from _strings(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            yield from _strings(v)


def mermaid_family(code_text):
    for ln in code_text.splitlines():
        s = ln.strip()
        if s and not s.startswith("%%"):
            return s.split()[0]
    return ""


def lint_blocks(blocks):
    """Return a list of violations of the lesson standard (empty list = compliant)."""
    errs = []
    if not blocks or blocks[0].get("_kind") != "style":
        errs.append("block 0 must be style_block()")
    if len(blocks) < 2 or blocks[1].get("type") != "toc":
        errs.append("block 1 must be the toc block")
    if not blocks or blocks[-1].get("type") != "footer":
        errs.append("the last block must be the footer")

    stories = [b for b in blocks if b.get("type") == "story" and re.match(r"^\d+ · ", b.get("heading") or "")]
    mermaids = [b for b in blocks if b.get("type") == "mermaid"]
    families = {mermaid_family(b.get("code", "")) for b in mermaids}
    charts = sum(1 for b in blocks if b.get("type") == "chart") + sum(
        len(b.get("charts", [])) for b in blocks if b.get("type") == "chartrow")
    panels = sum(1 for b in blocks if b.get("_kind") == "code") + 2 * sum(
        1 for b in blocks if b.get("_kind") == "compare")
    compares = [b.get("_langs", []) for b in blocks if b.get("_kind") == "compare"]
    variants = {b.get("variant") for b in blocks if b.get("type") == "callout"}
    hrefs = set()
    for s in _strings(blocks):
        hrefs.update(re.findall(r'class="lnk" href="([^"]+)"', s))

    need = [
        (len(stories) >= 6, f"numbered story sections: {len(stories)} (need 6)"),
        (any(b.get("_kind") == "mapping" for b in blocks), "no mapping() concept table"),
        (any(b.get("type") == "cards" for b in blocks), "no cards section"),
        (len(mermaids) >= 3, f"mermaid diagrams: {len(mermaids)} (need 3)"),
        (len(families) >= 2, f"mermaid families: {sorted(families)} (need 2 different)"),
        (charts >= 3, f"charts: {charts} (need 3)"),
        (panels >= 6, f"code panels: {panels} (need 6)"),
        (any(set(c) == {"csharp", "vb"} for c in compares), "no C# <-> VB compare()"),
        (any(c and c[0] in KNOWN_LANGS and c[1] == "csharp" for c in compares),
         "no Java/Kotlin/TypeScript/Python <-> C# compare()"),
        (any(b.get("type") in ("twocol", "threecol") for b in blocks), "no twocol/threecol"),
        (any(b.get("type") == "table" and b.get("_kind") != "mapping" for b in blocks),
         "no table besides the mapping table"),
        (len(hrefs) >= 4, f"distinct source links: {len(hrefs)} (need 4)"),
        ({"warn", "ok", "summary"} <= variants, f"callouts present: {sorted(v for v in variants if v)} "
                                               "(need warn, ok, summary)"),
    ]
    errs += [msg for ok, msg in need if not ok]

    for b in blocks:
        if b.get("type") == "cards":
            for c in b.get("cards", []):
                for label, _v in c.get("lines", []):
                    if len(label) > 9:
                        errs.append(f"card {c.get('title')!r}: line label {label!r} is longer than 9 chars")
        if b.get("type") == "mermaid":
            fam = mermaid_family(b.get("code", ""))
            if "classDef" in b.get("code", "") and fam not in _CLASSDEF_FAMILIES:
                errs.append(f"mermaid {b.get('heading')!r}: classDef is not supported in a {fam} diagram")
            for ln in b.get("code", "").splitlines():
                if "classDef" in ln and "color:" not in ln:
                    errs.append(f"mermaid {b.get('heading')!r}: classDef without color: {ln.strip()[:60]}")
        if b.get("type") in ("chart", "chartrow"):
            for c in ([b] if b["type"] == "chart" else b.get("charts", [])):
                if not c.get("note"):
                    errs.append(f"chart {c.get('heading')!r} has no note")
    return errs


def loc(*relpaths):
    """Non-blank, non-comment, non-region lines across sample files — a MEASURED figure."""
    total = 0
    for rp in relpaths:
        for ln in (REPO / rp).read_text(encoding="utf-8-sig").splitlines():
            s = ln.strip()
            if (not s or s.startswith(("//", "'", "<!--")) or s.upper().startswith("REM ")
                    or _REGION_ANY_START.match(s) or _REGION_END.match(s)):
                continue
            total += 1
    return total


def days_until(year, month, day):
    """Whole days from the build date to a calendar date (negative once it has passed)."""
    return (_dt.date(year, month, day) - BUILD_DATE).days
