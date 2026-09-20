# -*- coding: utf-8 -*-
"""Lesson 06 — VB.NET for Legacy Estates. Built to 1-analysis/spec_lesson-pdfs/_standard.md; unit spec
1-analysis/spec_lesson-pdfs/lesson-06-vbnet-legacy-estates.md."""
import math
import pathlib
import re

from lesson_kit import (DIFFERENT, MEASURED, REPO, TRAP, VERIFIED, T_ARCH, T_CS,
                        T_LEGACY, T_TOOLING, T_VB, code, compare, esc, from_sample, from_text, legend, link,
                        loc, mapping, pill, style_block)
from lessons.roster import meta, ref

# ── captured from real runs on the build machine (SDK 10.0.401, runtime 10.0.12, re-run 2026-09-20) ──────────────────
# The whole output of `dotnet run --project L06.ParityReport`, verbatim. Every parity figure in this lesson is parsed
# from this text (and each count is pinned by GridParityTests), so the printed panel and the prose cannot disagree.
REPORT = """\
Parity grid        50,176 quote requests
Faithful C# port   0 mismatches
Port variants, one change at a time:
  TruncatingCasts     22,520   44.9%
  HalfUpRounding      11,324   22.6%
  IntegerDivision      3,072    6.1%
  BirthdayAge          8,064   16.1%
  CaseSensitiveCodes  16,128   32.1%
  FiveElementTable     3,072    6.1%
  DecimalRates           304    0.6%
Worked example  CLASS1 550000 born 2002-06-15 start 2026-01-01 48m 0cl
  VB legacy 8933  C# port 8933  canonical 8933.71
Sample  class1 287500 born 2001-12-31 start 2026-01-01 18m 0cl
  VB legacy 4864  C# port 4864
First HalfUpRounding mismatch
  CLASS1 205000 born 2001-12-31 start 2026-01-01 6m 0cl: legacy 4625, port 3700
First DecimalRates mismatch
  CLASS2PLUS 487500 born 2001-12-31 start 2026-01-01 6m 0cl com 3001cc: legacy 8484, port 8485
"""
PARITY_CASES = int(re.search(r"Parity grid\s+([\d,]+) quote requests", REPORT).group(1).replace(",", ""))
PARITY = [(m.group(1), int(m.group(2).replace(",", "")))  # (PortChange, mismatches) — pinned by GridParityTests
          for m in re.finditer(r"^  (\w+?)\s+([\d,]+)\s+[\d.]+%$", REPORT, re.M)]
if len(PARITY) != 7 or "0 mismatches" not in REPORT:
    raise ValueError("REPORT no longer parses: expected 7 port variants and a faithful port with 0 mismatches")
VB_TEMPLATES = [("Library", 1), ("Console", 1), ("Tests", 5), ("WinForms", 3), ("WPF", 4), ("Web", 0),
                ("Worker", 0)]  # `dotnet new list --language VB`, grouped by tag

META = meta(
    6,
    subtitle="Read, run and retire Visual Basic .NET — the syntax map, the semantics that change numbers, "
             "VB ↔ C# interop and a parity-tested migration",
    objectives=[
        "Read production VB.NET fluently by mapping its keywords, operators and file options onto the C# and "
        "Java you already read",
        "Name the VB semantics that silently change results — Option Strict Off, banker's-rounding CInt, / on "
        "integers, DateDiff, Dim a(n), Option Compare Text — and reproduce each one deliberately in C#",
        "Call VB from C# and C# from VB, and design library APIs that survive the boundary (case-only names, "
        "ByRef, optional parameters)",
        "Choose a route per project — rewrite, re-platform, retarget or port — from what .NET 10 still supports "
        "for Visual Basic",
        f"Prove a C# port matches its VB original with VB characterization tests and a {PARITY_CASES:,}-case "
        "parity grid before switching traffic",
    ],
    maps_from="Maintaining legacy Java EE / JSP / Servlet applications you did not write, 100%-coverage test "
              "suites (the specification tests that characterization tests are the mirror image of), migration "
              "planning across a large multi-application estate, and Kotlin and Java sharing one Gradle build.",
)

L = "lesson-06-vbnet-legacy-estates/samples"
LEGACY = f"{L}/L06.LegacyRating/LegacyPremium.vb"
LEGACY_TESTS = f"{L}/L06.LegacyRating.Tests/LegacyPremiumCharacterizationTests.vb"
PORT = f"{L}/L06.ModernRating/PremiumCalculator.cs"
COMPAT = f"{L}/L06.ModernRating/VbCompat.cs"
ADAPTER = f"{L}/L06.Parity/LegacyAdapter.cs"
GRID = f"{L}/L06.Parity/QuoteGrid.cs"
PARITY_TESTS = f"{L}/L06.Parity.Tests/GridParityTests.cs"
PARTNER = f"{L}/L06.PartnerSdk/PartnerRateCard.cs"
SEM = f"{L}/L06.VbSemantics/Program.vb"
LOOSE = f"{L}/L06.VbSemantics/Loose.vb"
FORM = f"{L}/L06.WinFormsVb/QuoteForm.vb"
DESIGNER = f"{L}/L06.WinFormsVb/QuoteForm.Designer.vb"
PORTCHANGES = f"{L}/L06.Parity/NaivePort.cs"

# ── official sources ─────────────────────────────────────────────────────────────────────────
def nolink(text, url):
    """A source link that never breaks across lines: at a line end the renderer otherwise splits a long
    label at any character ('V / isual Basic language strategy')."""
    return '<span style="white-space:nowrap">' + link(text, url) + "</span>"


VBSTRAT = nolink("Visual Basic language strategy",
               "https://learn.microsoft.com/en-us/dotnet/visual-basic/getting-started/strategy")
VBNEW = nolink("What's new for Visual Basic", "https://learn.microsoft.com/en-us/dotnet/visual-basic/whats-new/")
VB5 = nolink("Visual Basic support planned for .NET 5.0",
           "https://devblogs.microsoft.com/vbteam/visual-basic-support-planned-for-net-5-0/")
WINFORMS5 = nolink("Visual Basic WinForms apps in .NET 5",
                 "https://devblogs.microsoft.com/dotnet/visual-basic-winforms-apps-in-net-5-and-visual-studio-16-8/")
RAZOR = nolink("Razor syntax reference", "https://learn.microsoft.com/en-us/aspnet/core/mvc/views/razor")
WEBFORMS = nolink("Migrate from ASP.NET Web Forms to Blazor",
                "https://learn.microsoft.com/en-us/dotnet/architecture/blazor-for-web-forms-developers/migration")
VB6 = nolink("Support Statement for Visual Basic 6.0",
           "https://learn.microsoft.com/en-us/previous-versions/visualstudio/visual-basic-6/visual-basic-6-support-policy")
CINT = nolink("Type conversion functions",
            "https://learn.microsoft.com/en-us/dotnet/visual-basic/language-reference/functions/type-conversion-functions")
MROUND = nolink("Math.Round", "https://learn.microsoft.com/en-us/dotnet/api/system.math.round")
DIV = nolink("/ operator",
           "https://learn.microsoft.com/en-us/dotnet/visual-basic/language-reference/operators/floating-point-division-operator")
DATEDIFF = nolink("DateAndTime.DateDiff",
                "https://learn.microsoft.com/en-us/dotnet/api/microsoft.visualbasic.dateandtime.datediff")
ARRAYS = nolink("Arrays in Visual Basic",
              "https://learn.microsoft.com/en-us/dotnet/visual-basic/programming-guide/language-features/arrays/")
COMPARE = nolink("Option Compare statement",
               "https://learn.microsoft.com/en-us/dotnet/visual-basic/language-reference/statements/option-compare-statement")
STRICT = nolink("Option Strict statement",
              "https://learn.microsoft.com/en-us/dotnet/visual-basic/language-reference/statements/option-strict-statement")
REMOVEINT = nolink("-removeintchecks",
                   "https://learn.microsoft.com/en-us/dotnet/visual-basic/reference/command-line-compiler/removeintchecks")
ANDOP = nolink("And operator",
             "https://learn.microsoft.com/en-us/dotnet/visual-basic/language-reference/operators/and-operator")
NOTHING = nolink("Nothing keyword", "https://learn.microsoft.com/en-us/dotnet/visual-basic/language-reference/nothing")
ONERROR = nolink("On Error statement",
               "https://learn.microsoft.com/en-us/dotnet/visual-basic/language-reference/statements/on-error-statement")
BYREF = nolink("Modifiable and nonmodifiable arguments",
             "https://learn.microsoft.com/en-us/dotnet/visual-basic/programming-guide/language-features/procedures/"
             "differences-between-modifiable-and-nonmodifiable-arguments")
BYVAL = nolink("Force an argument to be passed by value",
             "https://learn.microsoft.com/en-us/dotnet/visual-basic/programming-guide/language-features/procedures/"
             "how-to-force-an-argument-to-be-passed-by-value")
CLS = nolink("Language independence and the CLS", "https://learn.microsoft.com/en-us/dotnet/standard/language-independence")
STRANGLER = nolink("Strangler Fig pattern", "https://learn.microsoft.com/en-us/azure/architecture/patterns/strangler-fig")
ACL = nolink("Anti-corruption Layer pattern",
           "https://learn.microsoft.com/en-us/azure/architecture/patterns/anti-corruption-layer")
CODECONV = nolink("icsharpcode/CodeConverter", "https://github.com/icsharpcode/CodeConverter")
UA = nolink(".NET Upgrade Assistant overview",
          "https://learn.microsoft.com/en-us/dotnet/core/porting/upgrade-assistant-overview")
AWSX = nolink("Modernizing .NET with AWS Transform", "https://docs.aws.amazon.com/transform/latest/userguide/dotnet.html")

# Pygments' vbnet lexer has no token for VB 14 interpolated strings, so every `$"` prints inside a red
# error box. The code is valid (the samples compile); drop the box, keep the text. (same fix as lesson 01)
_ERROR_SPAN = re.compile(r'<span style="border: 1px solid #F00">(.*?)</span>', re.S)


def listed(block, heading):
    """Put a code()/compare() panel in the Contents at level 2 and clean VB highlighting (as lesson 01)."""
    block.update(heading=heading, toc=2)
    if "vb" in block.get("_langs", []):
        block["html"] = _ERROR_SPAN.sub(r"\1", block["html"])
    return block


def figure_heading(text):
    """A numbered heading for a block type that prints none of its own (twocol), kept with that block (as lesson 01)."""
    return {"type": "html", "html": f'<div class="figh"><h2>{esc(text)}</h2></div>', "heading": text,
            "toc": 2, "_keep_with_next": True}


def short(lnk, text):
    """The same (nowrap) link with a short label, for narrow table cells where a long label would overflow."""
    return re.sub(r">[^<]*</a>", ">" + esc(text) + "</a>", lnk, count=1)


def _clean(block):
    if "vb" in block.get("_langs", []):
        block["html"] = _ERROR_SPAN.sub(r"\1", block["html"])
    return block


def pcode(s, heading, note, keep=None):
    """A listed code panel. A panel of more than 18 lines must be able to split across pages, but a block that
    is anchored in the Contents is made unbreakable by the renderer (brief_pdf._with_marker) — so a long panel
    is a small anchored heading block followed by an unlisted panel that carries no heading of its own."""
    if keep is None and s["src"].count("\n") + 1 > 18:
        return [{"type": "html", "html": f'<div class="codeh">{esc(heading)}</div>', "heading": heading, "toc": 2},
                _clean(code(s, note=note, keep=False))]
    return listed(code(s, heading=heading, note=note, keep=keep), heading)


def _flat(items):
    out = []
    for b in items:
        out.extend(b if isinstance(b, list) else [b])
    return out


def head_of(relpath, last_line_contains, where):
    """The top of a sample file down to the first line containing `last_line_contains` — still cut from the
    sample, so the panel cannot drift from the compiled code."""
    s = from_sample(relpath)
    lines = s["src"].splitlines()
    cut = next(i for i, ln in enumerate(lines) if last_line_contains in ln)
    s["src"] = "\n".join(lines[:cut + 1])
    s["file"] = f"{s['file']}  ·  {where}"
    return s


def pcompare(left, right, heading, note, keep=None):
    return listed(compare(left, right, heading=heading, note=note, keep=keep), heading)


def _pct(n):
    return f"{100 * n / PARITY_CASES:.1f}%"


def _sources(project):
    root = REPO / L / project
    return [p.relative_to(REPO).as_posix() for p in sorted(root.rglob("*")) if p.suffix in (".vb", ".cs")]


def _test_cases(relpath):
    """Test cases in one file: each [Fact]/<Fact> and each InlineData row — MEASURED."""
    text = (REPO / relpath).read_text(encoding="utf-8-sig")
    return len(re.findall(r"[\[<](?:Fact|InlineData)\b", text))


def _grid_dimensions():
    """Values per dimension of QuoteGrid, parsed from the C# source — MEASURED; product must equal the run."""
    text = (REPO / GRID).read_text(encoding="utf-8-sig")
    dims = {}
    for m in re.finditer(r"public static readonly \w+\[\] (\w+) =\s*\[(.*?)\];", text, re.S):
        depth, items = 0, 1
        for ch in m.group(2):
            if ch in "([":
                depth += 1
            elif ch in ")]":
                depth -= 1
            elif ch == "," and depth == 0:
                items += 1
        dims[m.group(1)] = items
    if math.prod(dims.values()) != PARITY_CASES:
        raise ValueError(f"QuoteGrid dimensions {dims} no longer multiply to the captured {PARITY_CASES} cases — "
                         "re-run L06.ParityReport and update PARITY")
    return dims


def _timeline_init():
    fills = ["#DBEAFE", "#E0E7FF", "#EDE9FE", "#CCFBF1", "#DCFCE7", "#FEF3C7", "#FCE7F3", "#E2E8F0"]
    tv = {f"cScale{i}": c for i, c in enumerate(fills)}
    tv.update({f"cScaleLabel{i}": "#1f2937" for i in range(len(fills))})
    tv.update({"primaryTextColor": "#1f2937", "fontSize": "16px"})
    body = ",".join(f'"{k}":"{v}"' for k, v in tv.items())
    return '%%{init: {"theme":"base","themeVariables": {' + body + '}}}%%\n'


def blocks():
    projects = ["L06.LegacyRating", "L06.LegacyRating.Tests", "L06.ModernRating", "L06.Parity",
                "L06.Parity.Tests", "L06.ParityReport", "L06.PartnerSdk", "L06.VbSemantics", "L06.WinFormsVb"]
    loc_by = {p: loc(*_sources(p)) for p in projects}
    vb_lines = sum(n for p, n in loc_by.items() if any(s.endswith(".vb") for s in _sources(p)))
    cs_lines = sum(loc_by.values()) - vb_lines
    vb_tests, cs_tests = _test_cases(LEGACY_TESTS), _test_cases(PARITY_TESTS)
    if (vb_tests, cs_tests) != (11, 11):   # the break-it experiment in §8 was measured against 11 + 11 tests
        raise ValueError(f"test counts are now {vb_tests} VB / {cs_tests} C#; re-run the §8 break-it measurements")
    dims = _grid_dimensions()
    worst = max(PARITY, key=lambda r: r[1])
    mistakes = [r for r in PARITY if r[0] != "DecimalRates"]
    lo = min(n for _, n in mistakes)
    templates = sum(n for _, n in VB_TEMPLATES)
    n_proj = len(list((REPO / L).glob("*/*.*proj")))
    if n_proj != len(projects):
        raise ValueError(f"{n_proj} sample projects on disk, {len(projects)} listed in lesson_06.blocks()")
    kit = loc_by["L06.Parity"] + loc_by["L06.LegacyRating.Tests"] + loc_by["L06.Parity.Tests"]
    if kit <= loc_by["L06.LegacyRating"] + loc_by["L06.ModernRating"]:
        raise ValueError("chart 8.3 note says the parity kit and tests outweigh the rule and its port — no longer true")

    return _flat([
        style_block(),
        {"type": "toc", "heading": "▤ Contents", "depth": 2,
         "note": "Page numbers are resolved from the rendered PDF. VB and C# panels are cut from the compiled samples; "
                 "numbers marked measured come from real runs of those samples."},
        # a callout heading must not print alone at a page foot with its items on the next page (as lesson 01)
        {"type": "html", "html": "<style>.callout .ct { break-after:avoid; page-break-after:avoid; } "
                                 ".callout li:first-child { break-before:avoid; page-break-before:avoid; } "
                                 ".code:not(.keep) { overflow:visible; } "
                                 ".code pre { orphans:6; widows:6; }</style>"},

        # ═══════════════════════════ 1 · WHY ═══════════════════════════
        {"type": "story", "heading": "1 · Why Visual Basic is your problem, not your language",
         "html": (
             "<p><b>You will rarely write new Visual Basic, but you will own systems written in it.</b> Line-of-business "
             "estates built in the 2000s — quote engines, back-office Windows Forms tools, Web Forms portals — carry "
             "VB.NET beside C#. In a migration inventory they look exactly like the Java EE and JSP applications you "
             "have already maintained: the authors are gone, business rules sit inside event handlers, and there are "
             "no tests. The job is the same too: read it, keep it running, and plan its exit without changing a "
             "single premium.</p>"
             "<p><b>The language is stable by policy, so what you learn here will not go stale.</b> Microsoft's stated "
             "strategy is that Visual Basic keeps a stable design, adopts new runtime features <i>consumption-only</i>, "
             "will not be extended to new workloads, and keeps investing in core scenarios such as Windows Forms and "
             "libraries (" + VBSTRAT + "). The current version, Visual Basic 17.13, ships with Visual Studio 2026 "
             "and adds recognition of two runtime features rather than new syntax (" + VBNEW + ").</p>"
             "<p><b>The risk is not syntax, it is semantics.</b> VB reads like pseudocode, so a port to C# looks like "
             "typing. It is not: implicit conversions round half to even, <code>/</code> on integers returns a "
             "Double, <code>And</code> evaluates both sides, <code>DateDiff</code> subtracts year numbers, and string "
             "comparison can ignore case file by file. This lesson measures what each quirk does to real quotes: a "
             "line-by-line port that gets just one of them wrong changes between "
             f"{_pct(lo)} and {_pct(worst[1])} of {PARITY_CASES:,} premiums.</p>"
             "<p><b>It ends with a method, not a converter.</b> VB characterization tests (the golden-master technique) "
             "pin today's behaviour, a faithful C# port reproduces it on purpose, and a parity grid proves the two "
             "agree before traffic moves. They are the mirror image of the specification tests behind a "
             "100%-coverage standard: those say what the code should do, these say what it does.</p>")},

        {"type": "kpi", "heading": "1.1 · The numbers behind this lesson",
         "items": [
             {"label": "Visual Basic", "value": "17.13", "tone": "violet",
              "sub": "current version · Visual Studio 2026 · verified"},
             {"label": "VB templates", "value": str(templates), "tone": "blue",
              "sub": "SDK 10.0.401 · none for web or worker · measured"},
             {"label": "Parity grid", "value": f"{PARITY_CASES:,}", "tone": "teal",
              "sub": "quote requests · measured"},
             {"label": "Worst port mistake", "value": _pct(worst[1]), "tone": "red",
              "sub": "premiums changed by (int) casts · measured"},
             {"label": "Lesson 06 samples", "value": f"{vb_lines + cs_lines} lines", "tone": "navy",
              "sub": f"VB {vb_lines} · C# {cs_lines} · {n_proj} projects · measured"}]},

        legend(T_VB, T_CS, T_LEGACY, T_ARCH, T_TOOLING),

        {"type": "callout", "variant": "info", "heading": "ℹ Before you start",
         "items": [
             "You need " + ref(1) + " (the two .NETs, target frameworks, VB as a consumer of C# types) and "
             + ref(2) + " (<code>decimal</code>, nullability, exceptions). VB's <code>Async</code>/<code>Await</code> "
             "is covered in " + ref(5) + ".",
             "You will build nine projects: a legacy-style VB rating library with VB xUnit characterization tests, "
             "a faithful C# port, a parity kit with its xUnit tests and a console report, a C# partner SDK consumed "
             "by a VB console that demonstrates the traps, and a VB Windows Forms form that calls the C# port.",
             "Premiums use the MotorQuote running example on the track's one canonical tariff (curriculum, "
             "\"Canonical tariff\"): every rate, loading and discount is <b>illustrative, not a real tariff</b>. "
             "One deliberate variant: this lesson's legacy VB prices in whole baht with banker's rounding, "
             "so its worked example is 8,933 where the canonical decimal tariff gives 8,933.71 (§8.2).",
             "<code>L06.WinFormsVb</code> targets <code>net10.0-windows</code> and is build-only; every other sample "
             "targets plain <code>net10.0</code> with no Windows-only API (verified on Windows only)."]},

        # ═══════════════════════════ 2 · WHERE VB LIVES ═══════════════════════════
        {"type": "story", "heading": "2 · Where VB.NET lives — and what .NET 10 still runs",
         "html": (
             "<p><b>Most VB.NET you meet runs on .NET Framework, and its workload — not its language — decides its "
             "future.</b> Class libraries, console jobs and Windows Forms tools have a direct path to modern .NET. "
             "ASP.NET Web Forms has none: it is a .NET Framework technology, and Microsoft's migration guidance moves "
             "those pages to Blazor on ASP.NET Core (" + WEBFORMS + "). The porting map for <code>System.Web</code>, "
             "WCF and IIS belongs to " + ref(12) + ".</p>"
             "<p><b>On .NET 10, VB is first-class for libraries, console apps, tests and Windows desktop — and has no "
             "web or worker template.</b> The 2020 plan for .NET 5 listed class library, console, Windows Forms, WPF, worker "
             "service and ASP.NET Core Web API (" + VB5 + "), and the Windows Forms Application Framework arrived with "
             ".NET 5 (" + WINFORMS5 + "). "
             f"The SDK this track pins ships {templates} VB templates — libraries, console, three test frameworks, "
             "Windows Forms and WPF — and none for web or worker projects (measured with "
             "<code>dotnet new list --language VB</code>). This lesson builds no VB web project, so read the two "
             "zero bars as \"no template, not demonstrated here\", not as \"impossible\". Razor pages and Blazor components are C#: Razor syntax "
             "\"consists of Razor markup, C#, and HTML\" (" + RAZOR + "). The practical shape is a C# host calling VB "
             "libraries, which " + ref(8) + " builds.</p>"
             "<p><b>Visual Basic 6 is a different animal.</b> A <code>.vbp</code>/<code>.frm</code>/<code>.bas</code> "
             "project is COM-era VB6, not .NET. Its runtime is supported for the lifetime of supported Windows "
             "versions, but the VB6 IDE has been unsupported since 8 April 2008 (" + VB6 + "). There is no retarget, "
             "only a rewrite.</p>"
             "<p><b>So triage by workload first, language second.</b> A VB class library on <code>net48</code> is a "
             "retarget and a test run; a Web Forms page is a new UI, whatever language its code-behind uses.</p>")},

        {"type": "table", "heading": "2.1 · Visual Basic on .NET Framework and on .NET 10",
         "cols": ["Workload", "VB on .NET 10", "VB template in SDK 10.0.401", "Route"],
         "rows": [
             ["Class library", pill("Supported", "green"), "<code>classlib</code>",
              "Retarget to <code>net10.0</code>; port to C# when the code changes"],
             ["Console app", pill("Supported", "green"), "<code>console</code>", "Retarget"],
             ["Unit tests", pill("Supported", "green"),
              "<code>xunit</code> · <code>nunit</code> · <code>mstest</code> + 2 item templates",
              "Keep VB tests as the characterization suite until the port lands"],
             ["Windows Forms", pill("Supported · Windows", "green"),
              "<code>winforms</code> · <code>winformslib</code> · <code>winformscontrollib</code>",
              "Retarget to <code>net10.0-windows</code>; move rules out of handlers"],
             ["WPF", pill("Supported · Windows", "green"),
              "<code>wpf</code> + 3 library templates", "Retarget; port view-models to C# first"],
             ["Worker / Windows service", pill("Planned 2020 · no template", "amber"), "—",
              "Not demonstrated here — host in a C# worker, see " + ref(8) + "; keep VB libraries behind it"],
             ["ASP.NET Core Web API", pill("Planned 2020 · no template", "amber"), "—",
              "Not demonstrated here — C# host, VB libraries referenced as projects"],
             ["Web Forms · Razor · Blazor", pill("Not VB", "red"), "—",
              "Web Forms is Framework-only; Razor and Blazor are C# — re-platform the UI"],
             ["Visual Basic 6", pill("Not .NET", "red"), "—", "Rewrite from a behaviour specification"]]},

        {"type": "mermaid", "inline": True,
         "heading": "2.2 · Where each VB.NET workload goes on .NET 10",
         "caption": "grey = Framework workload with a direct path · amber = web-era Framework workload · rose = not .NET "
                    "at all · blue = stays VB on .NET 10 · violet = moves to C#",
         "code": ('%%{init: {"flowchart": {"nodeSpacing": 18, "rankSpacing": 40, "padding": 12, "subGraphTitleMargin": {"top": 4, "bottom": 10}}}}%%\n'
                  "flowchart LR\n"
                  '  subgraph FW[".NET Framework estate"]\n'
                  '    LIB["VB class library"]:::old\n'
                  '    CON["VB console or batch job"]:::old\n'
                  '    WF["VB WinForms or WPF app"]:::old\n'
                  '    SVC["VB Windows service"]:::old\n'
                  '    WEB["ASP.NET Web Forms"]:::web\n'
                  '    WCF["WCF service"]:::web\n'
                  '    V6["VB6 .vbp .frm (COM)"]:::bad\n'
                  "  end\n"
                  '  subgraph N10[".NET 10"]\n'
                  '    NLIB["VB library<br/>net10.0"]:::vb\n'
                  '    NCON["VB console<br/>net10.0"]:::vb\n'
                  '    NWF["VB WinForms or WPF<br/>net10.0-windows"]:::vb\n'
                  '    NWK["C# worker service<br/>calling VB libraries"]:::cs\n'
                  '    NUI["C# Blazor or Razor UI"]:::cs\n'
                  '    NAPI["C# API, gRPC or CoreWCF"]:::cs\n'
                  '    NEW["C# rewrite"]:::cs\n'
                  "  end\n"
                  '  LIB -- "retarget" --> NLIB\n'
                  '  CON -- "retarget" --> NCON\n'
                  '  WF -- "retarget" --> NWF\n'
                  '  SVC -- "re-host" --> NWK\n'
                  '  WEB -- "re-platform UI" --> NUI\n'
                  '  WCF -- "port" --> NAPI\n'
                  '  V6 -- "rewrite" --> NEW\n'
                  "  classDef old fill:#e2e8f0,color:#1f2937,stroke:#475569;\n"
                  "  classDef web fill:#fde68a,color:#1f2937,stroke:#d97706;\n"
                  "  classDef bad fill:#fce7f3,color:#1f2937,stroke:#be185d;\n"
                  "  classDef vb fill:#dbeafe,color:#1f2937,stroke:#1d4ed8;\n"
                  "  classDef cs fill:#ede9fe,color:#1f2937,stroke:#6d28d9;\n"
                  "  style FW fill:#f8fafc,color:#1f2937,stroke:#94a3b8\n"
                  "  style N10 fill:#f8fafc,color:#1f2937,stroke:#94a3b8\n")},

        {"type": "chart", "heading": "2.3 · VB templates shipped with the pinned SDK", "kind": "bar",
         "args": {"data": VB_TEMPLATES, "ylabel": "templates", "tone": "blue", "width": 560, "height": 210},
         "caption": "measured: dotnet new list --language VB on the build machine, SDK 10.0.401, grouped by workload · Tests = 3 project + 2 item templates",
         "note": "<b>The two zero bars are the policy made visible.</b> Web API and worker projects were on the 2020 "
                 "plan yet have no VB template, and the strategy rules out new workloads such as web front ends. When "
                 "a plan says \"modernise the VB web app\", read it as \"write a C# host\"."},

        {"type": "mermaid", "inline": True,
         "heading": "2.4 · Visual Basic .NET, release by release",
         "caption": "date a legacy file by the syntax it uses: If() means Visual Studio 2008 or later, $\"…\" and NameOf "
                    "2015 or later, tuples 2017 or later · from Microsoft's What's new for Visual Basic",
         "code": (_timeline_init() +
                  "timeline\n"
                  "  2002 to 2005 : VS .NET 2002 first VB .NET : VS 2005 My namespace\n"
                  "  2008 to 2012 : VS 2008 LINQ, XML literals, If() : VS 2010 implicit line continuation"
                  " : VS 2012 Async and Await\n"
                  "  2015 to 2017 : VS 2015 VB 14 NameOf, interpolation : VS 2017 VB 15 tuples\n"
                  "  2019 to 2026 : VS 2019 VB 16.0 runtime on .NET Core : VS 2019 16.9 reads init-only"
                  " : VS 2026 VB 17.13 unmanaged constraint\n")},

        # ═══════════════════════════ 3 · READING VB ═══════════════════════════
        {"type": "story", "heading": "3 · Reading VB fluently — a map from the C# and Java you already read",
         "html": (
             "<p><b>VB is C#'s semantics spelled in English keywords — until it is not.</b> Both compile to the same "
             "IL and share types, generics, exceptions, async and LINQ, so most of a VB file maps word for word: "
             "<code>Dim x As Integer</code> is <code>int x</code>, <code>Shared</code> is <code>static</code>, "
             "<code>Friend</code> is <code>internal</code>, <code>MustInherit</code> is <code>abstract</code>. Read "
             "the table once; the rows marked " + TRAP + " are the only real obstacles.</p>"
             "<p><b>It is line-oriented and case-insensitive.</b> A statement ends at the line break unless the line "
             "ends with a comma, an operator or an open parenthesis (implicit continuation, Visual Studio 2010) or with "
             "an explicit <code> _</code>. <code>premium</code> and <code>Premium</code> are the same identifier, "
             "which starts to matter the moment VB calls a C# library (§5).</p>"
             "<p><b>Four file options change meaning, not style.</b> <code>Option Explicit</code>, "
             "<code>Option Strict</code>, <code>Option Infer</code> and <code>Option Compare</code> sit at the top of a "
             "file and override the project. Visual Studio's initial default for Option Strict is Off "
             "(" + STRICT + "); this repository's <code>Directory.Build.props</code> turns it On. Always read the "
             "first lines of a legacy file before trusting what <code>=</code> or <code>/</code> does below them.</p>"
             "<p><b>Events are declared, not subscribed.</b> A form declares its controls <code>WithEvents</code>, and "
             "a handler method ends with <code>Handles QuoteButton.Click</code>. There is no <code>+=</code> anywhere, "
             "so finding \"who calls this\" means searching for <code>Handles</code> clauses.</p>")},

        mapping("3.1 · C# and Java → Visual Basic", [
            ("<code>int x = 0;</code>", "<code>Dim x As Integer = 0</code>", "renamed",
             "<code>Dim x = 0</code> infers the type when Option Infer is On"),
            ("<code>null</code>", "<code>Nothing</code>", "trap",
             "Nothing assigned to an Integer gives 0, and <code>\"\" = Nothing</code> is True (" + short(NOTHING, "Nothing") + ")"),
            ("<code>==</code> on references", "<code>Is</code> / <code>IsNot</code>", "renamed",
             "Use <code>Is Nothing</code>, never <code>= Nothing</code>. A type that overloads <code>=</code> "
             "(<code>String</code>, a C# record) compares by value with <code>=</code>, while <code>Is</code> "
             "compares identity; on a plain class <code>=</code> does not compile (BC30452) — " + ref(3)),
            ("<code>&amp;&amp;</code> / <code>||</code>", "<code>AndAlso</code> / <code>OrElse</code>", "renamed",
             "Only these short-circuit"),
            ("<code>&amp;</code> / <code>|</code> on booleans", "<code>And</code> / <code>Or</code>", "trap",
             "Legacy code uses them for logic; both sides always run (" + short(ANDOP, "And") + ")"),
            ("<code>c ? a : b</code>", "<code>If(c, a, b)</code>", "same",
             "<code>IIf(c, a, b)</code> is a function: both arms run and it returns Object"),
            ("<code>/</code> on integers", "<code>\\</code>", "trap",
             "VB <code>/</code> is floating-point division: integral operands give Double, Decimal stays Decimal ("
             + short(DIV, "/ operator") + ")"),
            ("<code>%</code>", "<code>Mod</code>", "renamed", "Same sign rules as C#"),
            ("<code>+</code> for strings", "<code>&amp;</code>", "trap",
             "With Option Strict Off, <code>\"42\" + 1</code> is 43 and <code>\"42\" &amp; 1</code> is \"421\""),
            ("<code>static</code>", "<code>Shared</code> · <code>Module</code>", "renamed",
             "A Module's members are callable unqualified from anywhere in the project"),
            ("<code>internal</code> · <code>protected internal</code>", "<code>Friend</code> · <code>Protected Friend</code>",
             "renamed", "—"),
            ("<code>abstract</code> · <code>sealed</code> · <code>virtual</code>",
             "<code>MustInherit</code> · <code>NotInheritable</code> · <code>Overridable</code>", "renamed",
             "Methods are non-virtual by default in both — " + ref(3)),
            ("<code>new</code> (hiding)", "<code>Shadows</code>", "different", "Shadows hides by name, every overload"),
            ("<code>this</code> · <code>base</code>", "<code>Me</code> · <code>MyBase</code> · <code>MyClass</code>",
             "different", "<code>MyClass</code> calls this class's version even when overridden"),
            ("<code>(int)x</code> · <code>x as T</code>",
             "<code>CInt(x)</code> · <code>TryCast</code> · <code>DirectCast</code> · <code>CType</code>", "trap",
             "<code>CInt</code> rounds half to even; the C# cast truncates (" + short(CINT, "CInt") + ")"),
            ("<code>new decimal[6]</code>", "<code>Dim ncb(5) As Decimal</code>", "trap",
             "The number is the upper bound: six elements (" + short(ARRAYS, "arrays") + ")"),
            ("<code>Array.Resize</code>", "<code>ReDim Preserve</code>", "renamed", "Allocates a new array every time"),
            ("<code>button.Click += OnClick</code>", "<code>WithEvents</code> + <code>Handles</code> · <code>AddHandler</code>",
             "different", "Wiring is declared on the field and the method"),
            ("<code>ref</code> · <code>out</code>", "<code>ByRef</code>", "trap",
             "A property passed ByRef is written back; the default is ByVal (" + short(BYREF, "ByRef") + ")"),
            ("<code>catch (E e) when (…)</code>", "<code>Catch e As E When …</code>", "same",
             "<code>On Error GoTo</code> and <code>Resume Next</code> still compile (" + short(ONERROR, "On Error") + ")"),
            ("<code>using System;</code>", "<code>Imports System</code>", "renamed",
             "Projects add further imports in the <code>.vbproj</code>"),
            ("<code>CompareInfo.Compare(a, b, IgnoreCase | …)</code>", "<code>Option Compare Text</code> + <code>=</code>",
             "trap", "One file-level line changes every <code>=</code> and <code>Select Case</code> on strings. "
                     "<code>OrdinalIgnoreCase</code> is not the same rule: culture, width and kana differ (§4.8)"),
            ("<code>new Foo { X = 1 }</code>", "<code>New Foo With {.X = 1}</code> · <code>With obj … End With</code>",
             "different", "Inside a With block a leading <code>.</code> binds to the block's object; nested "
                          "blocks hide which object a line writes"),
            ("<code>void M()</code> · <code>T M()</code>", "<code>Sub</code> · <code>Function … As T</code>", "renamed",
             "<code>Return x</code> works in both; legacy code assigns the value to the function's own name"),
        ], cols=("C# / Java", "Visual Basic", "Kind", "Watch for")),

        {"type": "cards",
         "band": {"title": "3.2 · Six VB constructs with no direct C# spelling", "note": "reading view", "tone": "blue"},
         "cards": [
             {"num": 1, "title": "Module", "tags": [T_VB], "pills": [DIFFERENT],
              "what": "A type whose members are all <code>Shared</code> and visible to the whole project unqualified.",
              "lines": [("C#", "<code>static class</code> plus <code>using static</code>"),
                        ("Trap", "A bare <code>CalcPremium(…)</code> call hides which file owns the rule"),
                        ("Port", "A static class — C# already calls a Module's members as static members")]},
             {"num": 2, "title": "WithEvents and Handles", "tags": [T_VB], "pills": [DIFFERENT],
              "what": "Event wiring declared on the field and on the handler method.",
              "lines": [("C#", "<code>+=</code> in the constructor or <code>InitializeComponent</code>"),
                        ("Trap", "Handlers look unreferenced; search for <code>Handles X.Click</code>"),
                        ("Port", "Regenerate designer wiring, then review every handler for business rules")]},
             ]},
        {"type": "cards", "toc": False,
         "band": {"title": "3.2 · Six VB constructs (continued)", "note": "reading view", "tone": "blue"},
         "cards": [
             {"num": 3, "title": "The My namespace", "tags": [T_VB, T_LEGACY], "pills": [DIFFERENT],
              "what": "Generated shortcuts to the application, computer, settings and resources, per project type.",
              "lines": [("C#", "<code>Environment</code>, <code>Application</code>, configuration — no single equivalent"),
                        ("On .NET", "A VB console on .NET 10 has no <code>My.Computer</code>: BC30456 (§5.4)"),
                        ("Port", "Replace call by call; <code>My.Settings</code> becomes configuration — " + ref(8))]},
             {"num": 4, "title": "On Error GoTo and Resume Next", "tags": [T_VB, T_LEGACY], "pills": [TRAP],
              "what": "Unstructured error handling: jump to a label, or ignore the error and carry on.",
              "lines": [("C#", "None; Resume Next behaves like an empty catch around every statement"),
                        ("Measured", "Err.Number 11 is set, execution continues, the result stays 0"),
                        ("Port", "Characterize first — the swallowed errors are behaviour callers rely on")]},
             ]},
        {"type": "cards", "toc": False,
         "band": {"title": "3.2 · Six VB constructs (continued)", "note": "reading view", "tone": "blue"},
         "cards": [
             {"num": 5, "title": "ByRef that accepts a property", "tags": [T_VB, T_CS], "pills": [TRAP],
              "what": "VB reads the property, passes a temporary, and writes the result back.",
              "lines": [("C#", "<code>ref</code> never accepts a property (a compile error)"),
                        ("Measured", "<code>AddFee(line.Total)</code> changes it; <code>AddFee((line.Total))</code> does not"),
                        ("Port", "Spell it out: copy to a local, pass <code>ref</code>, assign back")]},
             {"num": 6, "title": "Option Compare Text", "tags": [T_VB], "pills": [TRAP],
              "what": "A file-level switch: string <code>=</code> and <code>Select Case</code> ignore case, using "
                      "the current culture (" + COMPARE + ").",
              "lines": [("C#", "A <code>StringComparison</code> or <code>CompareOptions</code> on every call"),
                        ("Measured", "<code>\"CLASS1\" = \"class1\"</code> is False in one file and True in the next"),
                        ("Port", "One named helper, <code>VbCompat.TextEquals</code>, not scattered <code>ToUpper()</code>")]}]},

        pcode(from_sample(DESIGNER, "withevents"),
             heading="3.3 · The declaring end — controls declared WithEvents in the designer file",
             note="<b>This is where the events are wired, and no <code>+=</code> appears.</b> A field declared "
                  "<code>Friend WithEvents</code> can be the target of a <code>Handles</code> clause anywhere in the "
                  "class. The form designer owns and rewrites this file, so business logic never belongs in it."),

        pcode(from_sample(FORM, "handles-click"),
             heading="3.4 · The handling end — most of your VB reading skills in one method",
             note="<b>Read it line by line.</b> <code>Handles QuoteButton.Click</code> subscribes to the control "
                  "declared above; the trailing <code> _</code> continues the declaration. <code>Sub</code> is a "
                  "method that returns nothing (<code>Function … As T</code> returns a value). "
                  "<code>New QuoteRequest(…)</code> constructs a <i>C#</i> record, mixing positional and named "
                  "arguments (<code>LicenceMonths:=120</code>). <code>Decimal?</code> is the C# <code>decimal?</code> "
                  "the port returns, and <code>If(…)</code> is the ternary. The form stays VB; the rating rule has "
                  "already moved to C#."),

        # ═══════════════════════════ 4 · SEMANTICS ═══════════════════════════
        {"type": "story", "heading": "4 · Semantics that bite — where a line-by-line port changes numbers",
         "html": (
             "<p><b>Option Strict Off is where most legacy surprises live.</b> With it off, VB converts silently between "
             "strings, numbers and dates and resolves members at run time (late binding) (" + STRICT + "). The rating "
             "module in this lesson opens with <code>Option Strict Off</code> and <code>Option Compare Text</code> "
             "(panel 4.1): two lines that decide how every expression below them behaves. A file option overrides the project, so a "
             "solution-wide Strict On does not make every file strict — the sample <code>Loose.vb</code> compiles "
             "loosely inside a strict project.</p>"
             "<p><b>Conversions to integers round half to even.</b> <code>CInt</code>, <code>CLng</code> and every "
             "implicit Double-to-Integer conversion round a fraction of exactly .5 to the nearest even integer: 2.5 "
             "becomes 2 and 3.5 becomes 4 (" + CINT + "). A C# <code>(int)</code> cast truncates, while "
             "<code>Math.Round</code> defaults to the same round-half-to-even rule (" + MROUND + "). The Java instinct, "
             "round half up, is wrong for both.</p>"
             "<p><b><code>/</code> is floating-point division, not integer division.</b> In VB, <code>18 / 12</code> is "
             "1.5 for any two integral operands (" + DIV + "); assign it to an Integer and banker's rounding stores "
             "2, so an 18-month licence counts as two years. Integer division is <code>\\</code>. A C# port that writes "
             "<code>months / 12</code> gets 1.</p>"
             "<p><b>Five more quirks change results.</b> <code>DateDiff(DateInterval.Year, …)</code> uses only the year "
             "parts, so a driver born on 31 December is a year older on 1 January (" + DATEDIFF + "). "
             "<code>Dim ncb(5)</code> declares an upper bound, giving six slots (" + ARRAYS + "). Option Compare Text "
             "makes string <code>=</code> ignore case (" + COMPARE + "). <code>And</code>/<code>Or</code> evaluate "
             "both operands (" + ANDOP + ") — harmless in arithmetic, fatal when the right side dereferences something "
             "the left side just checked. And integer arithmetic is <i>checked</i>: unless a project passes "
             "<code>-removeintchecks</code> (" + REMOVEINT + "), <code>Integer.MaxValue + 1</code> throws "
             "<code>OverflowException</code>, where C# wraps silently unless the code says <code>checked</code>. It is "
             "the one VB default stricter than C#, and " + ref(2) + " §8.3 measures both sides. A port written "
             "without <code>checked</code> drops a guard nobody wrote down, which is why <code>VbCompat.CInt</code> "
             "in panel 4.8 wraps its conversions in <code>checked(…)</code>.</p>")},

        pcode(head_of(LEGACY, "Dim base As Integer", "top of file"),
             heading="4.1 · The top of a legacy file — two option lines and an implicit conversion",
             note="<b>Read the first two lines before anything else.</b> <code>Option Strict Off</code> lets "
                  "<code>Dim base As Integer = sumInsured * rate</code> compile: a Decimal times a Double, stored "
                  "in an Integer with no cast in sight. <code>Option Compare Text</code> is why <code>Case "
                  "\"CLASS1\"</code> also matches <code>\"class1\"</code>. The <code>-1</code> after "
                  "<code>Return</code> is the \"declined\" sentinel that §5.1 wraps in an adapter; §7.1 and §7.2 "
                  "put the rest of this function beside its C# port."),

        pcode(from_sample(LOOSE, "late-binding"),
             heading="4.2 · Loose on purpose — a file that opts out of Option Strict",
             note="<b>This compiles inside a project whose default is Option Strict On.</b> <code>card</code> is an "
                  "<code>Object</code>, so <code>LoadingFor(2)</code> is bound at run time and a misspelt member "
                  "(<code>Discount</code>) fails only when that line runs, with <code>MissingMemberException</code>. "
                  "<code>+</code> on a string and a number converts the string; <code>&amp;</code> concatenates."),

        pcode(from_sample(LOOSE, "on-error"),
             heading="4.3 · On Error Resume Next — the error that never happened",
             note="<b>The division by zero raised, and nothing stopped.</b> <code>Resume Next</code> continues at "
                  "the next statement after every error, so <code>ratio</code> keeps its default 0 and only "
                  "<code>Err.Number</code> (11, division by zero) records that anything went wrong; "
                  "<code>On Error GoTo 0</code> switches the handling off again. Replace it with "
                  "<code>Try</code>/<code>Catch</code> only after a test has pinned the 0."),

        pcode(from_sample(SEM, "and-andalso"),
             heading="4.4 · And, AndAlso, IIf and If() — which right-hand sides run",
             note="<b>Count the calls, not the result.</b> All four print the same answer, but <code>And</code> and "
                  "<code>IIf</code> run <code>Touch()</code> anyway. In legacy code the right-hand side is often "
                  "<code>policy.Holder.Age &gt; 25</code> after a null check — with <code>And</code> that throws."),

        pcode(from_sample(SEM, "arrays-division"),
             heading="4.5 · Upper bounds, the two divisions and checked arithmetic",
             note="<b><code>Dim ncb(5)</code> has Length 6.</b> <code>ReDim Preserve ncb(7)</code> copies into a new "
                  "array of 8. <code>/</code> gives 1.5 and <code>CInt</code> of it gives 2; <code>\\</code> gives 1. "
                  "<code>CInt(11 / 12)</code> is 1 — VB rounds to nearest, it never truncates. "
                  "<code>Integer.MaxValue + 1</code> throws where the same C# line would wrap to "
                  "<code>-2147483648</code>."),

        pcompare(from_text("""
            And        right side ran 1x
            AndAlso    right side ran 0x
            IIf        right side ran 1x -> none
            If()       right side ran 0x -> none
            Dim ncb(5)          Length 6
            ReDim Preserve (7)  Length 8
            18 / 12 = 1.5   18 \\ 12 = 1
            18 Mod 12 = 6
            CInt(18 / 12) = 2   CInt(11 / 12) = 1
            Integer.MaxValue + 1  OverflowException
            0.5  CInt 0  Fix 0  Math.Round 0  AwayFromZero 1
            1.5  CInt 2  Fix 1  Math.Round 2  AwayFromZero 2
            2.5  CInt 2  Fix 2  Math.Round 2  AwayFromZero 3
            3.5  CInt 4  Fix 3  Math.Round 4  AwayFromZero 4
            reason = ""            True
            reason Is Nothing      True
            """, "text", label="Output — L06.VbSemantics (1/2)", file="captured on the build machine"),
                from_text("""
            Integer = Nothing      0
            "CLASS1" = "class1"    False
            AddFee(line.Total)     1000 -> 1035
            AddFee((line.Total))   1035 -> 1035
            card.LoadingFor(2)     0.25
            late bound LoadingFor(2)  0.25
            late bound Discount       MissingMemberException
            "42" + 1  = 43      "42" & 1  = 421
            "CLASS1" = "class1"     True
            DateDiff(Year, 31 Dec 2001, 1 Jan 2026)  25
            Dim years As Integer = 11 / 12           1
            On Error Resume Next   Err.Number 11, ratio 0
            """, "text", label="Output — L06.VbSemantics (2/2)", file="captured on the build machine"),
                heading="4.6 · What the VB console prints on .NET 10",
                note="<b>Every line is a trap you can now name.</b> <code>\"CLASS1\" = \"class1\"</code> is False in "
                     "<code>Program.vb</code> (Option Compare Binary) and True in <code>Loose.vb</code> (Text). The "
                     "driver born on 31 December 2001 is 24 on 1 January 2026, but <code>DateDiff</code> says 25. "
                     "<code>On Error Resume Next</code> swallowed a division by zero and left the result at 0, while "
                     "<code>Integer.MaxValue + 1</code> did not wrap: VB threw <code>OverflowException</code>."),

        {"type": "chart", "heading": "4.7 · Four midpoints, three rounding rules", "kind": "grouped_bar",
         "args": {"categories": ["0.5", "1.5", "2.5", "3.5"],
                  "series": [("CInt / Math.Round (to even)", [0, 2, 2, 4]),
                             ("Fix (truncate, like a C# cast)", [0, 1, 2, 3]),
                             ("AwayFromZero (Java HALF_UP)", [1, 2, 3, 4])],
                  "ylabel": "result", "width": 620, "height": 220},
         "caption": "measured: L06.VbSemantics output in 4.6 · C# (int) and Java HALF_UP columns named by the rule they share",
         "note": "<b>No midpoint gets the same answer from all three rules.</b> Banker's rounding matches half-up "
                 "only at 1.5 and 3.5, and matches truncation only at 0.5 and 2.5, so whichever rule a port "
                 "reaches for, half of these inputs change. A premium rule that rounds a base, then a loading, "
                 "then a tax compounds the difference — which is why §7 finds whole-baht mismatches in thousands "
                 "of quotes."},

        pcompare(from_text("""
            // What a Java-minded port reaches for, line by line
            int base = (int) (sumInsured * rate);    // truncates
            long half = Math.round(2.5);             // 3: half up
            int years = licenceMonths / 12;          // 18 -> 1

            int age = Period.between(dob, start)     // birthdays
                            .getYears();

            boolean same = code.equals("CLASS1");    // exact case

            BigDecimal vat = gross.multiply(VAT_RATE)
                .setScale(0, RoundingMode.HALF_UP);  // half up

            int total = net + duty;                  // wraps silently
            """, "java", file="the instincts you bring"),
                from_sample(COMPAT, "vb-compat"),
                heading="4.8 · Java instincts vs the VB semantics a faithful port must keep",
                note="<b>Every Java line is reasonable and every one changes a premium or a guard.</b> The C# port "
                     "does not sprinkle <code>MidpointRounding.ToEven</code> and year subtraction through the rule; it "
                     "names each legacy semantic once in <code>VbCompat</code>, so a reviewer sees exactly which quirks "
                     "are being preserved — and later, which one is being retired. The <code>checked(…)</code> around "
                     "each cast keeps VB's overflow guard: an out-of-range <code>CInt</code> throws in VB, while an "
                     "unchecked C# cast does not, and Java's <code>int</code> arithmetic wraps silently."),

        # ═══════════════════════════ 5 · INTEROP ═══════════════════════════
        {"type": "story", "heading": "5 · VB ↔ C# interop — one runtime, two compilers' rules",
         "html": (
             "<p><b>Crossing the boundary needs no bridge, but each compiler reads the same metadata its own way.</b> "
             "You have met this shape calling Kotlin from Java: a Kotlin top-level function or <code>object</code> "
             "member is a static method to Java, and <code>@JvmOverloads</code> exists because Java ignores Kotlin's "
             "default values. Here a VB <code>Module</code>'s members are static members to C#, a VB "
             "<code>Optional ByVal</code> parameter is a C# optional parameter, and <code>ByRef</code> is "
             "<code>ref</code>. In the other direction VB consumes C# records, <code>decimal?</code>, "
             "<code>DateOnly</code> and generics unchanged — the form in §3.4 builds a C# record with named "
             "arguments. The VB runtime library, <code>Microsoft.VisualBasic</code>, is part of .NET 10 too, so C# "
             "code can call <code>DateAndTime.DateDiff</code> as easily as VB does.</p>"
             "<p><b>Case-only names break Visual Basic.</b> Think of a Kotlin API that compiles cleanly but is "
             "awkward from Java until you add <code>@JvmName</code>: C# happily compiles a class with a "
             "<code>Loading</code> property and a <code>loading(int)</code> method, and VB cannot tell them apart "
             "and refuses any use of either (BC31429 in §5.4). The Common Language Specification says identifiers "
             "must differ by more than case, and <code>[assembly: CLSCompliant(true)]</code> makes the C# compiler "
             "warn with CS3005 (" + CLS + "). It is the compiler-enforced version of keeping a Kotlin API "
             "Java-friendly. If VB code consumes your library — in an estate it usually does — mark the assembly "
             "CLS-compliant and let warnings-as-errors gate it.</p>"
             "<p><b>ByRef writes properties back, and you have no JVM habit for it.</b> Neither Java nor Kotlin "
             "can pass a variable by reference, so <code>ref</code> and <code>ByRef</code> are new to you. VB lets you "
             "pass a property to a <code>ByRef</code> (or C# <code>ref</code>) parameter: it passes a temporary and "
             "assigns the result back to the property, so <code>AddFee(line.Total)</code> changes "
             "<code>line.Total</code>. Wrapping the argument in parentheses forces a copy that is discarded ("
             + short(BYVAL, "forcing by value") + "). C# does not accept a property as a <code>ref</code> argument "
             "at all, so a port has to write the copy-back explicitly — or better, return the new value. One more "
             "asymmetry: an <code>Optional ByRef</code> VB parameter is <i>required</i> from C#, which is why the "
             "adapter below passes <code>declineReason</code> every time.</p>"
             "<p><b>Sentinels need an adapter.</b> Legacy VB APIs return <code>-1</code> for \"declined\" and report "
             "reasons through <code>ByRef</code> strings. Wrap them once, in C#, in a method with a modern shape "
             "(<code>decimal?</code> and an <code>out</code> reason), and the rest of the new code never learns the "
             "old conventions — the Anti-corruption Layer pattern (" + short(ACL, "Microsoft Learn") + ") at the size "
             "of one class.</p>")},

        pcode(from_sample(ADAPTER, "call-vb"),
             heading="5.1 · C# calling a VB Module — the adapter at the seam",
             note="<b>No interop layer, just a call.</b> <code>LegacyPremium</code> is a VB <code>Module</code>, so C# "
                  "calls it like a static class. The VB <code>Optional ByVal commercial</code> stays optional, but "
                  "<code>Optional ByRef declineReason</code> arrives as a required C# <code>ref</code> parameter (leave "
                  "it out and the compiler reports CS7036), passed here by name. <code>-1</code> becomes "
                  "<code>null</code> at this one place."),

        pcode(from_sample(PARTNER, "partner-sdk"),
             heading="5.2 · A partner's C# SDK — valid C#, awkward VB",
             note="<b>Two members differ only by case.</b> C# compiles this without a warning because the assembly does "
                  "not claim CLS compliance. <code>AddFee</code> takes <code>ref</code> plus an optional fee — "
                  "legal from both languages, with different meanings for a property argument."),

        pcode(from_sample(SEM, "byref-property"),
             heading="5.3 · The VB caller — copy-back through ByRef, and the escape hatch",
             note="<b>The parentheses are the whole difference.</b> The first call passes <code>line.Total</code> by "
                  "reference and the property becomes 1035; the second passes a copy and it stays 1035 (captured "
                  "output in §4.6). <code>New QuoteLine With {.Total = 1000D}</code> on the first line is VB's "
                  "object initializer, the C# <code>new QuoteLine { Total = 1000m }</code>; the same keyword also "
                  "opens a <code>With line … End With</code> block. The case-collision call is compiled only with <code>SHOW_CASE_COLLISION</code>, "
                  "so the sample builds; <code>LoadingFor</code> is the name a partner should have shipped."),

        pcode(from_text("""
            $ dotnet build L06.VbSemantics -p:DefineConstants=SHOW_CASE_COLLISION=True
            Program.vb(97,27): error BC31429: 'loading' is ambiguous because multiple kinds
                of members with this name exist in class 'PartnerRateCard'.
            Build FAILED.

            $ dotnet build L06.VbSemantics -p:DefineConstants=SHOW_MY_COMPUTER=True
            Program.vb(107,27): error BC30456: 'Computer' is not a member of 'L06.VbSemantics.My'.
            Build FAILED.
            """, "shell", file="captured on the build machine · long lines wrapped for print"),
             heading="5.4 · Two compile errors worth recognising",
             note="<b>VB reports the lower-case name even though the code says <code>card.Loading</code></b> — the "
                  "compiler is case-insensitive, so both members answer to either spelling. The second error is the "
                  "<code>My</code> namespace: a .NET 10 VB console gets no <code>My.Computer</code>, so code that "
                  "leaned on it needs replacing before or during a retarget."),

        figure_heading("5.5 · Interop rules at the boundary"),
        {"type": "table",
         "cols": ["Feature", "C# library, VB caller", "VB library, C# caller", "Design rule"],
         "rows": [
             ["Static members", "<code>static class</code> reads like a Module", "A <code>Module</code>'s members are static",
              "Qualify calls in VB to keep ownership visible"],
             ["Optional parameters", "Optional in VB (<code>AddFee(x)</code> omits the fee)",
              "Optional ByVal is optional in C#; <code>Optional ByRef</code> is required (CS7036)",
              "Keep optional parameters ByVal if C# will call you"],
             ["By reference", "<code>ref</code>/<code>out</code> → ByRef; properties copied back",
              "ByRef → <code>ref</code>; C# must pass a variable", "Return a record or tuple instead"],
             ["Case-only names", "Unusable (BC31429)", "VB names are case-insensitive by design",
              "<code>[assembly: CLSCompliant(true)]</code> on shared C# libraries"],
             ["Records, init-only", "Consumed; VB 16.9 reads init-only (" + short(VBNEW, "VB 16.9") + "); "
              "<code>=</code> compares records by value", "VB cannot declare records",
              "Keep shared models in C#"],
             ["Events", "<code>WithEvents</code> + <code>Handles</code>, or <code>AddHandler</code>",
              "<code>+=</code> on a VB <code>Event</code>", "Same CLR event underneath"],
             ["Sentinels", "—", "<code>-1</code>, empty strings, <code>ByRef</code> reasons",
              "One C# adapter converts them to <code>null</code> and <code>out</code>"],
             ["String equality", "Culture-aware only if you ask", "Depends on each file's Option Compare",
              "Name the rule once (<code>VbCompat.TextEquals</code>)"],
             ["VB runtime", "Built in", "<code>Microsoft.VisualBasic</code> ships with .NET 10 — callable from C#",
              "Use it as a test oracle for kept quirks (7.6)"]]},

        # ═══════════════════════════ 6 · MIGRATION ═══════════════════════════
        {"type": "story", "heading": "6 · Migration strategy — characterize, strangle, retarget, port",
         "html": (
             "<p><b>Start with tests that describe what the code does, not what it should do.</b> Characterization "
             "tests (golden-master tests) are the opposite of the specification tests behind a 100%-coverage "
             "standard: they call the legacy code and pin its current output, quirks included. The VB tests below assert that an 18-month licence counts as two years "
             "and that a driver born on 31 December is a year older than one born a day later. They are written in VB, "
             "against the VB project, before any port, so they stay valid on both sides of every later change.</p>"
             "<p><b>Strangle by project, not by file.</b> A VB project calls a C# library with no bridge — " + ref(1) + " "
             "showed it — so the unit of migration is the project: retarget a VB library to <code>net10.0</code>, let C# reference "
             "it, then replace it with a C# port behind the same call site. The Strangler Fig pattern's façade "
             "(" + short(STRANGLER, "Microsoft Learn") + ") is, inside one process, a project reference plus an adapter; across web estates it is "
             "a reverse proxy — " + ref(12) + ".</p>"
             "<p><b>Pick the route by workload.</b> Libraries and console jobs retarget, then are ported when they "
             "change. Windows Forms retargets to <code>net10.0-windows</code> after the rules move out of handlers — "
             "the sample form already calls the C# port. Web Forms needs a new C# UI. VB6 needs a rewrite.</p>"
             "<p><b>A converter's output is a draft until the grid passes.</b> ICSharpCode CodeConverter converts VB "
             "to C# (and back) with "
             "Roslyn and says VB → C# quality is much higher than the reverse (" + CODECONV + "). Microsoft's own "
             "tooling is changing: .NET Upgrade Assistant is officially deprecated in favour of the GitHub Copilot "
             "modernization agent (" + UA + "), and AWS Transform for .NET lists VB.NET as a preview language ("
             + short(AWSX, "AWS Transform docs") + ") — " + ref(12) + " compares those tools and their requirements. Whichever tool writes the "
             "C#, the evidence that no premium moved is the same: characterization tests green on the VB, zero "
             "mismatches on the grid.</p>")},

        pcode(from_sample(LEGACY_TESTS, "pin-quirks"),
             heading="6.1 · Characterization tests in VB — pinning the quirks on purpose",
             note="<b>These tests would fail code review as specifications, and that is the point.</b> They assert what "
                  "production does today: cover codes ignore case and spaces, <code>DateDiff</code> ages a 31 December "
                  "birthday early, 18 months rounds to two years, seven claim-free years reuse the sixth slot, and any "
                  "claim removes the no-claim discount. xUnit attributes look the same in VB, in angle brackets."),

        {"type": "mermaid", "inline": True,
         "heading": "6.2 · Choosing a route for one VB project",
         "caption": "amber = question · blue = stays VB for now · violet = ends in C# · rose = rewrite · "
                    "every route that ends in C# passes through characterization and parity tests",
         "code": ("flowchart LR\n"
                  '  S["One project<br/>from the inventory"]:::start --> Q1{"VB6?<br/>.vbp .frm .bas"}:::q\n'
                  '  Q1 -- "yes" --> R1["Rewrite in C#<br/>from a behaviour spec"]:::bad\n'
                  '  Q1 -- "no, VB.NET" --> Q2{"Workload?"}:::q\n'
                  '  Q2 -- "Web Forms or WCF" --> R2["New C# UI or service<br/>VB libraries behind it"]:::cs\n'
                  '  Q2 -- "WinForms or WPF" --> R3["Rules to C# first<br/>retarget net10.0-windows"]:::vb\n'
                  '  Q2 -- "library or console" --> Q3{"Changes often?"}:::q\n'
                  '  Q3 -- "yes" --> R4["Characterize, port,<br/>prove parity, switch"]:::cs\n'
                  '  Q3 -- "no" --> R5["Retarget net10.0<br/>leave in VB"]:::vb\n'
                  "  classDef start fill:#c7d2fe,color:#1f2937,stroke:#6366f1;\n"
                  "  classDef q fill:#fde68a,color:#1f2937,stroke:#d97706;\n"
                  "  classDef bad fill:#fce7f3,color:#1f2937,stroke:#be185d;\n"
                  "  classDef vb fill:#dbeafe,color:#1f2937,stroke:#1d4ed8;\n"
                  "  classDef cs fill:#ede9fe,color:#1f2937,stroke:#6d28d9;\n")},

        {"type": "mermaid", "inline": True,
         "heading": "6.3 · The life of one project in the migration",
         "caption": "blue = VB still serves traffic · violet = C# serves traffic · the back-edge is the normal case, "
                    "not a failure",
         "code": ("stateDiagram-v2\n"
                  "  direction TB\n"
                  '  state "VB still serves traffic" as VBS {\n'
                  "    direction LR\n"
                  "    [*] --> Inventoried\n"
                  "    Inventoried --> Characterized: VB tests\n"
                  "    Characterized --> Retargeted: net10.0\n"
                  "    Retargeted --> Ported: C#35; port\n"
                  "    Ported --> Characterized: mismatch\n"
                  "    Ported --> Proven: 0 mismatches\n"
                  "  }\n"
                  '  state "C#35; serves traffic" as CSS {\n'
                  "    direction LR\n"
                  "    Switched --> Retired: VB deleted\n"
                  "  }\n"
                  "  [*] --> VBS\n"
                  "  VBS --> CSS: callers move\n"
                  "  CSS --> [*]\n"
                  "  classDef vb fill:#dbeafe,color:#1f2937,stroke:#1d4ed8\n"
                  "  classDef cs fill:#ede9fe,color:#1f2937,stroke:#6d28d9\n"
                  "  class Inventoried,Characterized,Retargeted,Ported,Proven vb\n"
                  "  class Switched,Retired cs\n")},

        {"type": "mermaid", "inline": True,
         "heading": "6.4 · One quote through the strangler — VB screen, C# rule, VB oracle",
         "caption": "steps 1-4 = the production path once the screen calls the port · steps 5-6 = the parity run in CI, "
                    "before callers switch",
         "code": ('%%{init: {"theme":"base","themeVariables": {"actorBkg":"#E0E7FF","actorBorder":"#4338CA",'
                  '"actorTextColor":"#1f2937","noteBkgColor":"#FEF3C7","noteTextColor":"#1f2937",'
                  '"signalTextColor":"#1f2937","signalColor":"#475569","sequenceNumberColor":"#ffffff"},"sequence": {"mirrorActors": false, "messageMargin": 26}}}%%\n'
                  "sequenceDiagram\n"
                  "  autonumber\n"
                  "  participant U as Underwriter\n"
                  "  participant F as QuoteForm, VB\n"
                  "  participant P as PremiumCalculator, C#35;\n"
                  "  participant L as LegacyPremium, VB\n"
                  "  participant G as Parity tests, C#35;\n"
                  "  U->>F: click Quote\n"
                  "  F->>P: Calculate(QuoteRequest)\n"
                  "  P-->>F: decimal? premium\n"
                  "  F-->>U: premium or Declined\n"
                  "  Note over P,G: in CI, before any caller switches\n"
                  "  G->>L: CalcPremium for each grid case\n"
                  "  G->>P: Calculate, same case\n"
                  "  Note over L,G: compare every premium, pin the mismatch counts\n")},

        {"type": "cards",
         "band": {"title": "6.5 · Migration tooling this lesson owns, checked in September 2026", "note": "tooling view",
                  "tone": "teal"},
         "cards": [
             {"num": 7, "title": "ICSharpCode CodeConverter", "tags": [T_TOOLING], "pills": [pill("VB ↔ C#", "green"), VERIFIED],
              "what": "Open-source Roslyn converter that uses full project context.",
              "lines": [("Ships as", "Visual Studio extension, <code>codeconv</code> dotnet tool, web snippet converter, NuGet library"),
                        ("Release", "v10.0.1 on 1 March 2026; since v10.0.0 <code>codeconv</code> needs .NET 10, and it still needs Visual Studio 2026 installed"),
                        ("Framework", "The command line dropped .NET Framework projects in v10; the extension still converts them"),
                        ("Gate", "Its output is a draft until the characterization tests and the parity grid pass")]},
             {"num": 8, "title": "Characterization and parity tests", "tags": [T_ARCH], "pills": [pill("Your gate", "indigo"), MEASURED],
              "what": "Tests that pin the legacy output and compare the port over a grid of inputs.",
              "lines": [("Cost", f"{loc_by['L06.LegacyRating.Tests'] + loc_by['L06.Parity'] + loc_by['L06.Parity.Tests']} "
                                 "lines in this lesson; each <code>dotnet test</code> run took under a second here"),
                        ("Finds", f"All 6 injected port mistakes, each in ≥ {lo:,} of {PARITY_CASES:,} quotes"),
                        ("Why", "The only tool on this page that knows your business rules")]}]},

        figure_heading("6.6 · Convert with a tool, or rewrite by hand?"),
        {"type": "twocol", "boxes": [
            {"heading": "Convert mechanically, then prove parity", "tone": "teal",
             "items": ["Class libraries of pure calculation with characterization tests around them",
                       "Large volumes, where reviewing converted code beats retyping it",
                       "Code whose structure you want to keep recognisable in history and blame",
                       "Always followed by the parity grid — accuracy is measured on your quotes, not assumed"]},
            {"heading": "Rewrite by hand, from pinned behaviour", "tone": "rose",
             "items": ["Windows Forms handlers that mix UI, SQL and business rules — extract the rules first",
                       "Code built on <code>On Error Resume Next</code> or late binding",
                       "Web Forms pages: there is no .NET 10 target to convert them to",
                       "Visual Basic 6: COM-era code with no .NET project to convert"]}]},

        # ═══════════════════════════ 7 · PARITY ═══════════════════════════
        {"type": "story", "heading": "7 · Parity testing — prove the port before anyone switches",
         "html": (
             "<p><b>A parity grid runs old and new code over every combination of the inputs a rule reads, and demands "
             "identical outputs.</b> It is the characterization test scaled up: instead of choosing twenty cases, "
             "enumerate each dimension — cover code with its casing, sum insured, birth date against start date, "
             "licence months, claims, commercial use and engine size — and take the Cartesian product. Here that is "
             f"{PARITY_CASES:,} quote requests, and the console report compares the faithful port and seven "
             "one-change variants against the VB original in under a second on the build machine (0.8 s for the "
             "whole run, start-up included).</p>"
             "<p><b>Choose values at the edge of each quirk, not at random.</b> Sums insured that land on .5 after the "
             "rate, birth dates on 31 December and 1 January, 6, 18, 30 and 42 months (half a licence year, where "
             "the rounding rules part), 60 and 90 months (the sixth table slot), 3,000 and 3,001 cc "
             "(the commercial engine-size step), three claims (declined) and codes in mixed case. A grid built that "
             f"way caught all six injected port mistakes; each changed between {_pct(lo)} and {_pct(worst[1])} of "
             "premiums. A twenty-case suite picked by hand has to be lucky.</p>"
             "<p><b>The same grid puts a size on a fix.</b> The team wants decimal rates instead of Double, surely a "
             f"pure improvement. Injected as its own change it altered {dict(PARITY)['DecimalRates']} of "
             f"{PARITY_CASES:,} premiums ({_pct(dict(PARITY)['DecimalRates'])}): <code>0.35</code> has no exact binary "
             "form, so the first mismatch prices <code>5,850 × 0.35</code> as 2,047.4999… in Double (legacy rounds it "
             "down to 2,047), while Decimal holds exactly 2,047.5 and rounds half to even up to 2,048. The fix is "
             "correct and it still moves prices, so it ships on its own, with that number attached. The birthday "
             f"rule is larger: a correct age changes {_pct(dict(PARITY)['BirthdayAge'])} of quotes, so it is a "
             "pricing decision for the business, not a refactoring. Reshaping the port's flat "
             "<code>QuoteRequest</code>, which mirrors the legacy signature, into the running example's "
             "<code>Vehicle</code>, <code>Driver</code> and <code>Money</code> types is another later, separately "
             "gated step under this same grid.</p>"
             "<p><b>Compare results, not implementations.</b> The runner counts \"both declined\" as a match and an "
             "exception as a mismatch, and the xUnit theory pins every count, so a number printed in this lesson "
             "fails the build if the samples drift from it.</p>")},

        pcompare(from_sample(LEGACY, "legacy-loadings"), from_sample(PORT, "port-loadings"),
                heading="7.1 · The same loadings in the VB original and the faithful C# port",
                note="<b>Line for line, on purpose.</b> VB's implicit <code>Integer = Double</code> conversion becomes "
                     "an explicit <code>VbCompat.CInt</code>; <code>licenceMonths / 12</code> becomes "
                     "<code>CInt(LicenceMonths / 12.0)</code>; <code>DateDiff</code> becomes "
                     "<code>DateDiffYears</code>. The values are the canonical tariff's: +20% under 25, +10% or +25% "
                     "for one or two claims, three declined, +25% commercial or +35% above 3,000 cc. The port is "
                     "uglier than a rewrite would be — that is the price of zero mismatches, paid once and refactored "
                     "later under the same grid. Every rate is illustrative, not a real tariff."),

        pcompare(from_sample(LEGACY, "legacy-discount-total"), from_sample(PORT, "port-discount-total"),
                heading="7.2 · The discount table and the total — VB original and C# port",
                note="<b><code>Dim ncb(5)</code> becomes a six-element array literal, spelled out.</b> The "
                     "claim-free years are the licence years when there are no claims and 0 otherwise; the "
                     "<code>If claimFreeYears &gt; 5</code> clamp becomes <code>Math.Min</code>, and every Decimal or "
                     "Double converted to Integer (<code>discount</code>, <code>duty</code>) goes through "
                     "<code>VbCompat.CInt</code> because VB rounds those to even. The VAT line needs no helper: "
                     "<code>Math.Round</code> already rounds to even in both languages."),

        pcode(from_sample(PORTCHANGES, "port-changes"),
             heading="7.3 · The injected changes — one enum member, one line of the port",
             note="<b>Six are plausible mistakes and one is a planned improvement.</b> Each member changes exactly "
                  "one line of the faithful port when <code>NaivePort</code> runs it, and each comment names the "
                  "VB semantic it forgets; <code>None</code> is the faithful port. Chart 7.7 counts how many "
                  "premiums each member moves, and the parity theory in 7.5 pins those counts."),

        pcode(from_sample(GRID, "grid"),
             heading="7.4 · The grid — boundary values, multiplied out",
             note=f"<b>{' × '.join(str(v) for v in dims.values())} = {PARITY_CASES:,} cases.</b> Each array holds the "
                  "values where a quirk changes behaviour: <code>\"Class1\"</code> for Option Compare Text, 31 December "
                  "2001 for <code>DateDiff</code>, 6/18/30/42 months for half-year rounding, 60 and 90 months for the "
                  "six-slot table, 3,000 and 3,001 cc for the commercial step, three claims and <code>CLASS4</code> so "
                  "declines are compared too."),

        pcode(from_sample(PARITY_TESTS, "parity-tests"),
             heading="7.5 · The parity gate in xUnit",
             note="<b>Two assertions carry the migration.</b> The faithful port must produce zero mismatches over the "
                  "whole grid. The theory then pins how many premiums each alternative would change — "
                  f"<code>DecimalRates</code> at {dict(PARITY)['DecimalRates']}, not 0 — so a later refactoring that "
                  "alters a single quote fails CI. A third test ties the legacy to the canonical tariff: the worked "
                  "example prices 8,933.71 THB in decimal and 8,933 in whole baht."),

        pcode(from_sample(PARITY_TESTS, "vb-runtime"),
              heading="7.6 · Checking VbCompat against the Visual Basic runtime",
              note="<b>The oracle for a quirk is the VB runtime itself, and C# can call it.</b> "
                   "<code>Microsoft.VisualBasic</code> ships with .NET 10, so a C# test can put "
                   "<code>Conversions.ToInteger</code>, <code>DateAndTime.DateDiff</code> and "
                   "<code>Operators.CompareString(…, TextCompare: true)</code> beside each <code>VbCompat</code> "
                   "helper. Production code stays on <code>VbCompat</code>, whose names say which quirk is kept; the "
                   "runtime is the test's witness, not a dependency of the port."),

        {"type": "chartrow", "charts": [
            {"heading": "7.7 · Premiums changed by one port change", "kind": "hbar",
             "args": {"data": sorted(PARITY, key=lambda r: -r[1]), "tone": "red", "width": 390, "labelw": 132},
             "caption": f"measured: L06.ParityReport, {PARITY_CASES:,} requests per variant",
             "note": "<b>Every mistake is loud on a boundary grid; the planned fix is quiet, not silent.</b> "
                     "Truncating casts and case-sensitive codes change the most quotes; the quietest mistakes, integer "
                     f"division and a five-element table, still change {dict(PARITY)['IntegerDivision']:,} each. "
                     f"<code>DecimalRates</code> changed {dict(PARITY)['DecimalRates']} — small enough that a "
                     "hand-picked suite would miss it, and still real prices."},
            {"heading": "7.8 · Values per grid dimension", "kind": "bar",
             "args": {"data": [("Cover", dims["CoverCodes"]), ("Sum", dims["SumsInsured"]),
                               ("Born", dims["BirthDates"]), ("Start", dims["StartDates"]),
                               ("Months", dims["LicenceMonths"]), ("Claims", dims["Claims"]),
                               ("Com.", dims["Commercial"]), ("cc", dims["EngineCc"])],
                      "ylabel": "values", "tone": "teal", "width": 390, "height": 220},
             "caption": "measured: parsed from QuoteGrid.cs at build time; the product is checked against the run",
             "note": f"<b>Three dimensions are the widest.</b> Sums insured ({dims['SumsInsured']}), cover codes "
                     f"({dims['CoverCodes']}) and licence months ({dims['LicenceMonths']}) multiply to "
                     f"{dims['SumsInsured'] * dims['CoverCodes'] * dims['LicenceMonths']}; the other five add a "
                     f"factor of {PARITY_CASES // (dims['SumsInsured'] * dims['CoverCodes'] * dims['LicenceMonths'])}. "
                     "Doubling any one dimension doubles the grid, so add a value only where a rule changes "
                     "behaviour — the run stays under a second."}]},

        # ═══════════════════════════ 8 · HANDS-ON ═══════════════════════════
        {"type": "story", "heading": "8 · Hands-on — run the estate in miniature",
         "html": (
             "<p><b>Nine projects model one migration from end to end.</b> <code>L06.LegacyRating</code> is the VB rule "
             "and <code>L06.LegacyRating.Tests</code> pins it. <code>L06.ModernRating</code> is the faithful C# port, "
             "<code>L06.Parity</code> holds the grid, the adapter and the injected variants, "
             "<code>L06.Parity.Tests</code> gates them, and <code>L06.ParityReport</code> prints the numbers used in §7. "
             "<code>L06.PartnerSdk</code> and <code>L06.VbSemantics</code> demonstrate the traps, and "
             "<code>L06.WinFormsVb</code> is the VB screen that already calls C#.</p>"
             "<p><b>Work in the order a real migration does.</b> Run the VB characterization tests, then the parity "
             "tests, then the report. Only when all three agree with the numbers in this lesson is the estate in a "
             "known state.</p>"
             "<p><b>Then break it on purpose, twice, and read what fails.</b> Make <code>VbCompat.CInt(double)</code> "
             f"a plain <code>(int)</code> cast: on the build machine 7 of the {cs_tests} parity tests failed, including "
             "the VB-runtime check in 7.6, and the faithful-port test named its first case — <code>CLASS1 205000 … 6m "
             "0cl com 3000cc: legacy 5781, port 5780</code>. Put the cast back, then change <code>Option Compare "
             "Text</code> to <code>Binary</code> at the top of "
             f"<code>LegacyPremium.vb</code>: 3 of the {vb_tests} VB characterization tests failed, every one of them a "
             "lower- or mixed-case cover code. That is the division of labour you want — the VB tests guard the legacy "
             "behaviour, the grid guards the port — and neither needed a debugger.</p>")},

        pcode(from_text("""
            # build, test and run every lesson-06 sample (the .NET 10 SDK must be on PATH)
            python 0-script/verify_samples.py --only 6

            # the pieces one at a time
            cd lesson-06-vbnet-legacy-estates/samples
            dotnet test L06.LegacyRating.Tests       # VB characterization tests
            dotnet test L06.Parity.Tests             # C# parity gate
            dotnet run --project L06.ParityReport    # the numbers in section 7
            dotnet run --project L06.VbSemantics     # the traps in section 4

            # reproduce the two compile errors from section 5.4
            dotnet build L06.VbSemantics -p:DefineConstants=SHOW_CASE_COLLISION=True
            dotnet build L06.VbSemantics -p:DefineConstants=SHOW_MY_COMPUTER=True
            """, "shell"), heading="8.1 · Commands",
             note="<b>Run the VB tests before the C# ones.</b> The characterization suite is the specification the "
                  "parity gate relies on; if it fails, the legacy rule changed and every number in §7 is suspect. "
                  "The two <code>-p:DefineConstants</code> builds are meant to fail — they reproduce §5.4."),

        pcode(from_text(REPORT, "text", label="Output — L06.ParityReport", file="captured on the build machine"),
             heading="8.2 · What you should see",
             note="<b>Two lines are worth checking by hand</b> (canonical illustrative tariff). The worked example is "
                  "550,000 × 2.1% = 11,550, +20% for age 23 = 13,860, −40% for four claim-free years = net 8,316.00, "
                  "stamp duty 33.26, VAT 584.45, total <b>8,933.71</b> in decimal; the legacy prices the same quote at "
                  "8,933 because it rounds every step to whole baht. The <code>class1</code> sample: 287,500 × 2.1% = "
                  "6,037.5, which banker's rounding keeps as 6,038; 18 months counts as 2 licence years (1.5 rounds "
                  "to even), so the discount is 25% of 6,038 = 1,509.5, stored as 1,510; net 4,528, duty 18, VAT 318, "
                  "total 4,864 — the mixed-case code costs nothing, and the faithful port agrees to the baht. In the "
                  "first half-up mismatch the licence is 6 months, half a year: banker's rounding stores 0 years and "
                  "no discount (4,625), half-up stores 1 year and a 20% discount (3,700)."),

        {"type": "chartrow", "charts": [
            {"heading": "8.3 · Lines of code by migration role", "kind": "hbar",
             "args": {"data": [("VB rule", loc_by["L06.LegacyRating"]),
                               ("VB char. tests", loc_by["L06.LegacyRating.Tests"]),
                               ("C# port", loc_by["L06.ModernRating"]),
                               ("Parity kit + report", loc_by["L06.Parity"] + loc_by["L06.ParityReport"]),
                               ("C# parity tests", loc_by["L06.Parity.Tests"]),
                               ("Trap demos", loc_by["L06.VbSemantics"] + loc_by["L06.PartnerSdk"]),
                               ("VB screen", loc_by["L06.WinFormsVb"])],
                      "tone": "navy", "width": 390, "labelw": 150},
             "caption": "non-blank, non-comment lines, grouped by role · measured at build time",
             "note": "<b>The port is not the big part.</b> The parity kit and the two test projects together are "
                     "larger than the VB rule and its C# port combined — the realistic ratio when the goal is zero "
                     "changed premiums."},
            {"heading": "8.4 · Sample code by language", "kind": "donut",
             "args": {"data": [("Visual Basic", vb_lines), ("C#", cs_lines)], "center": f"{vb_lines + cs_lines}",
                      "sub": "lines", "width": 390, "height": 200, "thickness": 32},
             "caption": "measured: projects with .vb files counted as Visual Basic",
             "note": f"<b>A migration repository is bilingual by design.</b> VB is still "
                     f"{100 * vb_lines / (vb_lines + cs_lines):.0f}% of the sample code: the rule, its tests, the trap "
                     f"demos and the screen stay VB until parity is proven and callers move. {vb_tests} VB test cases "
                     f"and {cs_tests} C# test cases run side by side in one build."}]},

        {"type": "callout", "variant": "warn", "heading": "⚠ Traps — what looks right to a Java, TypeScript or Python engineer",
         "items": [
             f"<b><code>(int)x</code> for <code>CInt(x)</code>.</b> CInt rounds half to even; the cast truncates. On the "
             f"grid this one change moved {_pct(dict(PARITY)['TruncatingCasts'])} of premiums.",
             f"<b><code>months / 12</code> on integers.</b> VB's <code>/</code> returns Double and the Integer "
             f"assignment rounds; C# integer division truncates — {_pct(dict(PARITY)['IntegerDivision'])} of premiums.",
             "<b>Trusting the project's Option Strict.</b> A file-level <code>Option Strict Off</code> or "
             "<code>Option Compare Text</code> overrides it for that file.",
             f"<b>Porting <code>Dim ncb(5)</code> as <code>new decimal[5]</code>.</b> It compiles, passes every test "
             f"below five claim-free years, and throws for {_pct(dict(PARITY)['FiveElementTable'])} of the grid.",
             f"<b>Fixing while porting.</b> A correct age calculation changed {_pct(dict(PARITY)['BirthdayAge'])} of "
             f"premiums, and even the \"obvious\" Decimal-for-Double swap changed {_pct(dict(PARITY)['DecimalRates'])}. "
             "Port the quirk, pin it, and change it in a separate, signed-off release."]},

        {"type": "callout", "variant": "ok", "heading": "✔ Checkpoint — you are ready for lesson 07 when",
         "items": [
             f"<code>python 0-script/verify_samples.py --only 6</code> reports {n_proj}/{n_proj} passed, including {vb_tests} VB "
             f"characterization cases and {cs_tests} C# parity cases.",
             "You can read <code>LegacyPremium.vb</code> top to bottom (panels 4.1, 7.1 and 7.2) and point at the line "
             "each of the six port mistakes would change (7.3).",
             "You can explain why <code>AddFee(line.Total)</code> and <code>AddFee((line.Total))</code> behave "
             "differently, and write the C# equivalent of each.",
             "Given a VB project from an inventory, you can place it on diagram 6.2 and defend the route."]},

        {"type": "callout", "variant": "summary", "heading": "🔍 Check yourself",
         "items": [
             "What does <code>CInt(2.5)</code> return, what does C# <code>(int)2.5</code> return, and which "
             "<code>MidpointRounding</code> value makes <code>Math.Round</code> match VB?",
             "What does <code>Dim years As Integer = 18 / 12</code> store, and which two VB rules produce that value?",
             "Why can VB not call a C# class with both <code>Loading</code> and <code>loading()</code>, and which "
             "attribute makes C# warn?",
             "Which VB workloads have templates in the .NET 10 SDK, and how do you put a VB rating library behind a "
             "web API?",
             "What separates a characterization test from a parity grid, and why did the decimal-rates change belong "
             "in its own release?",
             "What does Microsoft mean by a consumption-only strategy for Visual Basic?",
             "<code>LegacyPremium.vb</code> starts with <code>Option Compare Text</code>: what does its "
             "<code>Select Case</code> do with <code>\"  class1 \"</code>, and which helper reproduces that in the C# "
             "port?"]},

        {"type": "footer",
         "html": ("<b>Lesson 06 in one line:</b> VB.NET reads like C# in English keywords, but Option Strict Off, "
                  "round-half-to-even conversions, <code>/</code>, <code>DateDiff</code>, <code>Dim a(n)</code> and "
                  "Option Compare Text change numbers — so characterize the VB, port it faithfully, and let a parity "
                  "grid decide when callers switch. "
                  "<br/><b>Next:</b> " + ref(7) + " — how solutions, MSBuild and mono-repos hold C# and VB projects "
                  "in one build.")},
    ])

