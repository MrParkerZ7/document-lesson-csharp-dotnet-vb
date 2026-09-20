# -*- coding: utf-8 -*-
"""Lesson 02 — C# Language Essentials. Built to 1-analysis/spec_lesson-pdfs/_standard.md; shape follows
lesson_01.py. Unit spec: 1-analysis/spec_lesson-pdfs/lesson-02-csharp-language-essentials.md"""
import re

from lesson_kit import (REPO, DIFFERENT, ESTIMATE, MEASURED, RENAMED, SAME, TRAP, VERIFIED,
                        T_CS, T_JVM, T_TS, T_VB, code, compare, esc, from_sample, from_text, legend, link, loc,
                        mapping, snippet, style_block)
from lessons.roster import meta, ref

META = meta(
    2,
    subtitle="Syntax, types, nullability, pattern matching, methods and exceptions — read against Kotlin, "
             "Java 21 and TypeScript, with the Visual Basic form beside it",
    objectives=[
        "Read the shape of any modern C# file — file-scoped namespaces, global and implicit usings, top-level "
        "statements — and run a .NET 10 file-based app",
        "Choose decimal for money and name the culture and rounding rules that silently change a premium or a date",
        "Explain why C# nullable reference types are compile-time warnings, not Kotlin's type system, and "
        "where null still gets through",
        "Write switch expressions with relational, property, tuple and list patterns in place of Kotlin when "
        "and Java 21 switch",
        "Use named and optional arguments, params collections, ref/out/in, tuples, exception filters and using "
        "declarations — and recognise the same logic in Visual Basic",
    ],
    maps_from="Kotlin null safety, when expressions and data classes; Java 21 pattern switch, BigDecimal and "
              "try-with-resources; TypeScript destructuring, default and rest parameters — plus the habits of a "
              "motor-insurance rating engine where a rounding or culture bug changes what a customer pays.",
)

L = "lesson-02-csharp-language-essentials/samples"
SYN = f"{L}/L02.Syntax"
VBT = f"{L}/L02.SyntaxVb/Tour.vb"
RULES = f"{L}/L02.Rating/RatingRules.cs"
TESTS = [f"{L}/L02.Rating.Tests/RatingRulesTests.cs", f"{L}/L02.Rating.Tests/PremiumCalculatorTests.cs"]
FILE_APP = f"{L}/file-based/premium-check.cs"
CS_FILES = [f"{SYN}/{n}.cs" for n in ("Program", "GlobalUsings", "Resources", "TypesTour", "StringsTour",
                                       "NullsTour", "PatternsTour", "MethodsTour", "ErrorsTour")] + \
           [f"{L}/L02.Rating/{n}.cs" for n in ("Model", "RatingRules", "PremiumCalculator", "Examples")] + \
           TESTS + [FILE_APP]
VB_FILES = [f"{L}/L02.SyntaxVb/Program.vb", VBT]

CS14 = link("What's new in C# 14", "https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14")
CS13 = link("What's new in C# 13", "https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-13")
CS15 = link("What's new in C# 15", "https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-15")
HISTORY = link("The history of C#", "https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-version-history")
FILEAPPS = link("File-based apps", "https://learn.microsoft.com/en-us/dotnet/core/sdk/file-based-apps")
SDK = link(".NET project SDK overview", "https://learn.microsoft.com/en-us/dotnet/core/project-sdk/overview")
FLOAT = link("Floating-point numeric types",
             "https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/floating-point-numeric-types")
CHECKED = link("checked and unchecked",
               "https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/statements/checked-and-unchecked")
STRINGS = link("Best practices for comparing strings",
               "https://learn.microsoft.com/en-us/dotnet/standard/base-types/best-practices-strings")
ICU = link("Globalization and ICU", "https://learn.microsoft.com/en-us/dotnet/core/extensions/globalization-icu")
ROUND = link("Math.Round", "https://learn.microsoft.com/en-us/dotnet/api/system.math.round")
NRT = link("Nullable reference types",
           "https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/null-safety/nullable-reference-types")
JSONNULL = link("Respect nullable annotations",
                "https://learn.microsoft.com/en-us/dotnet/standard/serialization/system-text-json/nullable-annotations")
PATTERNS = link("Patterns", "https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/patterns")
EXC = link("Exception-handling statements",
           "https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/statements/exception-handling-statements")
CA2200 = link("CA2200", "https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca2200")
USING = link("using statement", "https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/statements/using")
DISPOSE = link("Implement a Dispose method",
               "https://learn.microsoft.com/en-us/dotnet/standard/garbage-collection/implementing-dispose")
VBIF = link("VB If operator", "https://learn.microsoft.com/en-us/dotnet/visual-basic/language-reference/operators/if-operator")
VBTRY = link("VB Try...Catch...Finally",
             "https://learn.microsoft.com/en-us/dotnet/visual-basic/language-reference/statements/try-catch-finally-statement")
VBINT = link("-removeintchecks",
             "https://learn.microsoft.com/en-us/dotnet/visual-basic/reference/command-line-compiler/removeintchecks")
JEP441 = link("JEP 441", "https://openjdk.org/jeps/441")
JEP440 = link("JEP 440", "https://openjdk.org/jeps/440")
KT22 = link("What's new in Kotlin 2.2", "https://kotlinlang.org/docs/whatsnew22.html")

# Pygments marks tokens it does not know with a red error box: VB 14 interpolated strings (`$"`) and the
# .NET 10 file-based-app directives (`#!`, `#:`). The code is valid (the samples compile); drop the box, keep
# the text. (kit request — as lesson 01, widened to every language)
_ERROR_SPAN = re.compile(r'<span style="border: 1px solid #F00">(.*?)</span>', re.S)

# Lesson-local print rules (kit request — as lesson 01): a callout heading never prints alone at a page foot,
# and the two tall diagram families are capped so they do not fill a page at full text width.
LOCAL_CSS = ("<style>.callout .ct { break-after:avoid; page-break-after:avoid; } "
             ".callout li:first-child { break-before:avoid; page-break-before:avoid; } "
             ".callout { break-inside:avoid; page-break-inside:avoid; } "
             ".story .ct { break-after:avoid; page-break-after:avoid; } "
             ".pgbrk { break-before:page; page-break-before:always; height:0; } "
             '.mmd svg[aria-roledescription="sequence"] { max-height:3.4in; } '
             '.mmd svg[aria-roledescription="stateDiagram"] { max-height:1.95in; } '
             '.mmd svg[aria-roledescription="flowchart-v2"] { max-height:3.6in; } '
             ".codeblk > .ct { break-after:avoid; page-break-after:avoid; } "
             "a.lnk, a { word-break:normal; overflow-wrap:break-word; }</style>")

_UNKEPT_HEAD = re.compile(r'^<div class="codeblk">(<div class="codeh">.*?</div>)', re.S)


def listed(block, heading):
    """lesson_kit code()/compare() blocks carry no `heading` key, so the Contents skipped every code panel.
    Copy the printed heading onto the block and opt it in at level 2 (kit request — as lesson 01).

    A listed block gets a Contents marker, and brief_pdf makes the marker's host break-inside:avoid unless
    the host opens with a `.ct` heading line — so a long panel built with keep=False still moved whole to the
    next page. For an unkept panel, wrap its heading in a `.ct` line: the marker is pinned to the heading and
    the panel may split as _standard.md §5 describes. Kept panels are left alone (kit request)."""
    block.update(heading=heading, toc=2)
    html = _ERROR_SPAN.sub(r"\1", block["html"])
    if 'class="code keep"' not in html and 'class="cmp keep"' not in html:
        html = _UNKEPT_HEAD.sub(r'<div class="codeblk"><div class="ct">\1</div>', html, count=1)
    block["html"] = html
    return block


def panel(src, heading, note, keep=None):
    return listed(code(src, heading=heading, note=note, keep=keep), heading)


def pair(left, right, heading, note, keep=None):
    return listed(compare(left, right, heading=heading, note=note, keep=keep), heading)


def figure_heading(text):
    """A numbered heading for a block type that prints none of its own (twocol), kept with that block."""
    return {"type": "html", "html": f'<div class="figh"><h2>{esc(text)}</h2></div>', "heading": text,
            "toc": 2, "_keep_with_next": True}


# ── helpers local to this lesson (MEASURED figures read from the samples at build time) ────────────
def region_loc(relpath, region):
    """Non-blank, non-comment lines inside one #region — the region-level twin of lesson_kit.loc()."""
    n = 0
    for ln in snippet(relpath, region).splitlines():
        s = ln.strip()
        if s and not s.startswith(("//", "'")):
            n += 1
    return n


def test_cases_by_rule(paths):
    """xUnit test cases per rule: [Fact] = 1, each [InlineData] = 1, [MemberData(nameof(X))] = rows of the
    TheoryData property X. Grouped by the test-method prefix before the first underscore."""
    rows, counts = {}, {}
    for rp in paths:
        lines = (REPO / rp).read_text(encoding="utf-8-sig").splitlines()
        current = None
        for ln in lines:
            m = re.search(r"TheoryData<.*>\s+(\w+)\s*=>", ln)
            if m:
                current, rows[m.group(1)] = m.group(1), 0
                continue
            if current and re.match(r"^\s*\{.*\},?\s*$", ln):
                rows[current] += 1
            elif current and ln.strip() == "};":
                current = None
        pending = 0
        for ln in lines:
            s = ln.strip()
            if s.startswith("[Fact"):
                pending += 1
            elif s.startswith("[InlineData("):
                pending += 1
            elif (m := re.match(r"\[MemberData\(nameof\((\w+)\)\)\]", s)):
                pending += rows[m.group(1)]
            elif (m := re.match(r"public (?:async Task|void) (\w+)\(", s)):
                if pending:
                    rule = m.group(1).split("_")[0]
                    counts[rule] = counts.get(rule, 0) + pending
                pending = 0
    return counts


def asserted_premium(relpath, region):
    """The worked example's figures, read from the Assert.Equal lines of the passing test."""
    vals = {}
    for m in re.finditer(r"Assert\.Equal\(([\d_.]+)m,\s*p\.(\w+)\)", snippet(relpath, region)):
        vals[m.group(2)] = float(m.group(1).replace("_", ""))
    return vals


# why VB needs more (or fewer) lines for each region pair — quoted by chart 9.6's note
VB_REASON = {
    "money": "the statements match one for one",
    "nulls": "VB has no <code>??=</code> and no <code>?.</code> on the left of an assignment",
    "branching": "every <code>Select Case</code> arm takes two lines, a <code>Case</code> and a "
                 "<code>Return</code>, and the block needs <code>End Select</code> and <code>End Function</code>",
    "methods": "VB spells <code>Optional</code>, <code>ParamArray</code>, <code>ByRef</code> and "
               "<code>End Function</code>",
    "resources": "VB closes its blocks with <code>End Try</code> and <code>End Using</code> where C# spends "
                 "four lines on braces",
}


# the test count in the captured terminal output of panel 9.3 — re-capture the panel when this changes
CAPTURED_TESTS = 31


def blocks():
    loc_cs, loc_vb = loc(*CS_FILES), loc(*VB_FILES)
    tests = test_cases_by_rule(TESTS)
    n_tests = sum(tests.values())
    if n_tests != CAPTURED_TESTS:
        raise ValueError(f"the samples now hold {n_tests} test cases but panel 9.3 shows a captured run of "
                         f"{CAPTURED_TESTS}: re-run dotnet test and re-capture 9.3")
    n_proj = len(list((REPO / L).glob("*/*.*proj")))
    p = asserted_premium(TESTS[1], "worked-example")
    pairs = [("money", f"{SYN}/TypesTour.cs", "money", "money"),
             ("nulls", f"{SYN}/NullsTour.cs", "nulls", "nulls"),
             ("branching", RULES, "age-loading", "select-case"),
             ("methods", f"{SYN}/MethodsTour.cs", "declarations", "methods"),
             ("resources", f"{SYN}/ErrorsTour.cs", "resources", "errors")]
    cs_lines = [region_loc(cs, r) for _, cs, r, _v in pairs]
    vb_lines = [region_loc(VBT, v) for *_x, v in pairs]
    extra = [(v - c, name, c, v) for (name, *_r), c, v in zip(pairs, cs_lines, vb_lines)]
    top, low = max(extra), min(extra)
    n_syntax_cs = len(list((REPO / SYN).glob("*.cs")))

    type_cards = [
        {"num": 1, "title": "int · long · short · byte", "tags": [T_CS, T_JVM, T_VB], "pills": [SAME],
         "what": "Fixed-size integers, each an alias of a System struct (<code>int</code> = "
                 "<code>System.Int32</code>).",
         "lines": [("Kotlin", "Int, Long — the same sizes"),
                   ("Differs", "<code>byte</code> is unsigned (Java's is signed; C# has <code>sbyte</code>); "
                               "<code>uint</code> and <code>ulong</code> exist"),
                   ("Overflow", "Wraps silently unless <code>checked</code> — 3.3; VB throws by default — 8.3"),
                   ("Literal", "<code>1_200</code> · <code>9_000_000_000L</code> · <code>0xFF</code>")]},
        {"num": 2, "title": "decimal — the money type", "tags": [T_CS], "pills": [DIFFERENT],
         "what": "128-bit base-10 with a scale: 0.1 is exact, and operators work.",
         "lines": [("Java", "BigDecimal — but a struct, with <code>+ - * /</code> and an <code>m</code> suffix"),
                   ("Range", "28–29 significant digits · 16 bytes · overflow always throws"),
                   ("Scale", "Keeps trailing zeros: 550000m × 0.021m prints <code>11550.000</code>"),
                   ("Trap", "Not a valid attribute argument — xUnit data needs a workaround, §9")]},
        {"num": 3, "title": "double · float", "tags": [T_CS, T_JVM], "pills": [SAME],
         "what": "IEEE 754 binary floating point, exactly as on the JVM.",
         "lines": [("Measured", "Adding 0.1 ten times prints <code>0.9999999999999999</code>"),
                   ("Mixing", "No implicit conversion to or from <code>decimal</code> — cast, visibly"),
                   ("Use for", "Ratios, telemetry, scores — never a premium")]},
        {"num": 4, "title": "string", "tags": [T_CS, T_JVM], "pills": [DIFFERENT],
         "what": "Immutable UTF-16 text; alias of <code>System.String</code>.",
         "lines": [("Java", "<code>==</code> compares content in C#, not references"),
                   ("Culture", "<code>IndexOf(string)</code>, <code>StartsWith(string)</code> and "
                               "<code>Compare</code> are culture-sensitive by default"),
                   ("Literals", "<code>$\"…\"</code> interpolation · <code>@\"C:\\x\"</code> verbatim · "
                                "<code>\"\"\"…\"\"\"</code> raw (C# 11)")]},
        {"num": 5, "title": "bool · char", "tags": [T_CS, T_TS], "pills": [DIFFERENT],
         "what": "True/false, and one UTF-16 code unit.",
         "lines": [("TS", "No truthiness: <code>if (count)</code> does not compile"),
                   ("Java", "boolean and char — identical semantics")]},
        {"num": 6, "title": "DateOnly · DateTime · DateTimeOffset", "tags": [T_CS, T_JVM], "pills": [TRAP],
         "what": "A calendar date, a date and time, and a date and time with a UTC offset.",
         "lines": [("Java", "LocalDate · LocalDateTime · OffsetDateTime"),
                   ("Trap", "<code>th-TH</code> formats the Buddhist-era year: 1 Oct 2026 → "
                            "<code>1/10/2569</code> (measured, 3.6)"),
                   ("Rule", "Persist ISO 8601 with <code>CultureInfo.InvariantCulture</code>")]}]

    return [
        style_block(),
        {"type": "toc", "heading": "▤ Contents", "depth": 2,
         "note": "Page numbers are resolved from the rendered PDF. Every C# and VB panel is cut from a sample "
                 "that builds, tests and runs on the .NET 10 SDK."},
        {"type": "html", "html": LOCAL_CSS},
        # the Contents fills page 1: start §1 on a fresh page instead of stranding its heading at the foot
        {"type": "html", "html": '<div class="pgbrk"></div>'},

        # ═══════════════════════════ 1 · OPENER ═══════════════════════════
        {"type": "story", "heading": "1 · Why this lesson — the syntax you will review tomorrow",
         "html": (
             "<p><b>You already think in every idea this lesson covers; what you lack is the C# spelling and the "
             "places where the spelling lies.</b> Null safety, pattern matching, value objects for money, "
             "resource scopes and exception handling are things you have shipped in Kotlin, Java and TypeScript. "
             "C# has all of them — several with the same symbols — and a few of those identical-looking symbols "
             "mean something different. A reviewer who reads <code>string?</code> as Kotlin's "
             "<code>String?</code>, or <code>!</code> as <code>!!</code>, approves code that fails in "
             "production.</p>"
             "<p><b>The language moved fast, so the age of the syntax dates the code.</b> The C# in a 2016 "
             "service and in a .NET 10 service can look like two languages: top-level statements, file-scoped "
             "namespaces, switch expressions, nullable reference types, raw strings and list patterns all arrived "
             "between C# 6 (2015) and C# 14 (November 2025, with .NET 10). This lesson teaches the current "
             "form and names the version of each feature (table 2.6, dated from " + HISTORY + "), so you can "
             "read an older estate too.</p>"
             "<p><b>Everything is taught through a rating engine, because that is where syntax bugs cost "
             "money.</b> The samples calculate a motor premium — base rate by coverage class, loadings for young "
             "drivers, claims and commercial use, a no-claim bonus, stamp duty and VAT. The rates are "
             "<b>illustrative, not a real tariff</b> — and they are the one tariff the whole track prices with, so "
             "the totals in §9 recur in every later lesson. A culture that swaps a decimal separator, a rounding mode "
             "that moves a satang, a year printed in the Buddhist era: each one is demonstrated by a sample that "
             "ran, not described.</p>")},

        {"type": "kpi", "heading": "1.1 · The numbers to leave this lesson with",
         "items": [
             {"label": "C# 14", "value": "Nov 2025", "tone": "violet",
              "sub": "ships with .NET 10 · verified"},
             {"label": "decimal digits", "value": "28–29", "tone": "teal",
              "sub": "significant · 16 bytes, base 10 · verified"},
             {"label": "Pattern kinds", "value": "10", "tone": "indigo",
              "sub": "listed in the C# reference · verified"},
             {"label": "Rating test cases", "value": str(n_tests), "tone": "green",
              "sub": "xUnit, all passing · measured at build"},
             {"label": "Lesson 02 samples", "value": f"{loc_cs + loc_vb} lines", "tone": "navy",
              "sub": f"{loc_cs} C# + {loc_vb} VB · measured"}]},

        legend(T_CS, T_VB, T_JVM, T_TS),

        {"type": "callout", "variant": "info", "heading": "ℹ Before you start",
         "items": [
             "<b>Prerequisite:</b> " + ref(1) + " — the .NET 10 SDK first on PATH, and the idea that C# and VB "
             "compile to the same IL. <code>dotnet --list-sdks</code> must list 10.0.401 or a later 10.0 SDK.",
             "<b>You will build:</b> <code>L02.Rating</code> (a C# library with the rating rules), "
             "<code>L02.Rating.Tests</code> (" + str(n_tests) + " xUnit test cases), <code>L02.Syntax</code> "
             "and <code>L02.SyntaxVb</code> (the same language tour in C# and Visual Basic), and a .NET 10 "
             "file-based app with no project file.",
             "<b>Not here:</b> classes, records and generics are " + ref(3) + "; LINQ and lambdas " + ref(4)
             + "; async " + ref(5) + "; VB semantics in depth " + ref(6) + ". Where a sample uses one of them, "
             "read it as vocabulary.",
             "Facts that change between releases are marked " + VERIFIED + " and linked; figures computed from "
             "the samples are " + MEASURED + "; judgement calls are " + ESTIMATE + ". Kotlin, Java and "
             "TypeScript panels are for comparison and are not compiled."]},

        # ═══════════════════════════ 2 · THE SHAPE OF A FILE ═══════════════════════════
        {"type": "story", "heading": "2 · The shape of a C# file",
         "html": (
             "<p><b>A modern C# file has less ceremony than a Java file and roughly as little as a Kotlin "
             "file.</b> One file per project may hold <i>top-level statements</i> — that file is the entry point, "
             "with no class and no <code>Main</code>. Every other file starts with a <i>file-scoped "
             "namespace</i> (<code>namespace L02.Syntax;</code>, C# 10), so the type body is not indented "
             "inside braces. A namespace is a naming convention the compiler does not tie to folders — Java "
             "expects a package's classes in a matching directory; C# does not.</p>"
             "<p><b>Most imports are not in the file at all.</b> With <code>ImplicitUsings</code> on, the SDK "
             "generates <code>global using</code> directives for <code>System</code>, "
             "<code>System.Collections.Generic</code>, <code>System.IO</code>, <code>System.Linq</code>, "
             "<code>System.Net.Http</code>, <code>System.Threading</code> and <code>System.Threading.Tasks</code>; "
             "a project adds its own with a <code>&lt;Using&gt;</code> item or a <code>global using</code> line "
             "(" + SDK + "). When a reviewed file uses <code>CultureInfo</code> with no import in sight, the "
             "import is in a generated <code>&lt;ProjectName&gt;.GlobalUsings.g.cs</code> under <code>obj</code> "
             "— here <code>L02.Syntax.GlobalUsings.g.cs</code> in "
             "<code>.build/artifacts/obj/L02.Syntax/debug/</code>.</p>"
             "<p><b>.NET 10 adds file-based apps: one <code>.cs</code> file, no project.</b> "
             "<code>dotnet app.cs</code> (or <code>dotnet run app.cs</code>) generates a virtual project, builds "
             "it and runs it. <code>#:package</code>, <code>#:project</code>, <code>#:property</code> and "
             "<code>#:sdk</code> directives replace the project file — SDK 10.0.300 added <code>#:include</code> "
             "for extra source files — and <code>dotnet project convert</code> turns the file into a real "
             "project when it grows (" + FILEAPPS + "). It is the .NET answer to a Python or Kotlin script, "
             "with one trap: it inherits every <code>Directory.Build.props</code> above it. Inside this "
             "repository an unused variable in a file-based app became build error CS0219, and its build output "
             "moved into <code>.build/artifacts/</code>.</p>")},

        mapping("2.1 · Syntax map — Kotlin, Java and TypeScript → C#", [
            ("<code>package</code> + folders", "<code>namespace X;</code> (file-scoped)", "renamed",
             "Not tied to folders; matching them is convention only"),
            ("<code>fun main()</code> · <code>static void main</code>", "Top-level statements", "same",
             "One file per project; the compiler generates the class"),
            ("<code>import</code>", "<code>using</code> · <code>global using</code> · implicit usings", "renamed",
             "<code>using</code> also means dispose — two unrelated uses of one keyword"),
            ("Kotlin <code>val</code> · Java <code>final var</code>", "<code>var</code> (mutable) · "
             "<code>const</code> · <code>readonly</code> field", "trap",
             "No <code>val</code>: a run-time value cannot be held in a read-only local; <code>var</code> "
             "is only inference"),
            ("<code>BigDecimal</code>", "<code>decimal</code> (struct, literal <code>0.07m</code>)", "different",
             "Operators work; 28–29 digits, not arbitrary precision"),
            ("Kotlin <code>\"$x\"</code> · TS <code>`${x}`</code>", "<code>$\"{x:N2}\"</code> · raw "
             "<code>\"\"\"</code> literals", "renamed",
             "A format specifier and the current culture apply inside the hole"),
            ("Java <code>==</code> on String (reference)", "<code>==</code> compares string content", "different",
             "<code>==</code> is ordinal; <code>IndexOf(string)</code>, <code>StartsWith</code>, "
             "<code>Compare</code> are linguistic"),
            ("Kotlin <code>String?</code>", "<code>string?</code> (nullable reference type)", "trap",
             "Compile-time warnings only — nothing checks at run time"),
            ("<code>?.</code> <code>?:</code> <code>!!</code>", "<code>?.</code> <code>??</code> "
             "<code>??=</code> <code>!</code>", "trap", "<code>!</code> never throws; <code>!!</code> does"),
            ("Kotlin <code>when</code> · Java 21 <code>switch</code>", "<code>switch</code> expression + patterns",
             "different", "Enum switches still need <code>_</code>: an enum is an int"),
            ("Kotlin default + named args", "Optional + named arguments", "different",
             "The default value is compiled into the caller"),
            ("<code>vararg</code> · <code>...rest</code>", "<code>params</code> any collection (C# 13)", "renamed",
             "<code>params ReadOnlySpan&lt;T&gt;</code> avoids the array"),
            ("<code>Pair</code> · destructuring", "Value tuples <code>(decimal Bonus, string Reason)</code>",
             "renamed", "Element names vanish at run time: reflection sees <code>Item1</code>, <code>Item2</code>"),
            ("Checked exceptions, <code>throws</code>", "Unchecked only, <code>catch … when</code>", "different",
             "A filter runs before inner <code>finally</code> blocks"),
            ("try-with-resources · Kotlin <code>use</code>", "<code>using var</code> · <code>await using</code>",
             "renamed", "Disposed at the end of the scope, in reverse order"),
        ]),

        pair(from_text("""
            // Main.kt: package, imports, a top-level main()
            package motorquote.syntax

            import java.util.Locale

            fun main() {
                Locale.setDefault(Locale.ROOT)
                println("L02 - Kotlin in MotorQuote terms")
                TypesTour.run()
                StringsTour.run()
                NullsTour.run()
                PatternsTour.run()
                MethodsTour.run()
                ErrorsTour.run()
            }
            // Kotlin still emits a class (MainKt) around main
            """, "kotlin", file="the idea you already know"),
             from_sample(f"{SYN}/Program.cs", "top-level"),
             "2.2 · An entry point — Kotlin main() vs C# top-level statements",
             "<b>The same idea with less text</b> (" + SAME + "). The C# file has no <code>using</code> lines "
             "because <code>GlobalUsings.cs</code> and the SDK supply them. Top-level code may use "
             "<code>await</code>, <code>args</code> and <code>return</code>; the compiler generates the class and "
             "entry-point method around it. Only one file in a project may do this. The first statement pins the "
             "current culture to invariant so that every captured output in this lesson is reproducible — a demo "
             "choice: a service passes a culture or format provider to each call instead of relying on a "
             "process-wide default (§3)."),

        pair(from_sample(f"{SYN}/GlobalUsings.cs"), from_sample(f"{SYN}/Resources.cs", "file-scoped"),
             "2.3 · Two more files — global usings, and a namespace with no imports",
             "<b>Imports live in one place.</b> <code>GlobalUsings.cs</code> is the whole file: two lines "
             "that reach every file of <code>L02.Syntax</code>, including <code>Program.cs</code>. "
             "<code>Resources.cs</code> is also the whole file: <code>namespace L02.Syntax;</code> ends in a "
             "semicolon and covers everything below it, and <code>IDisposable</code>, <code>ValueTask</code> "
             "and <code>Console</code> need no <code>using</code> line because the SDK's implicit usings bring "
             "in <code>System</code> and <code>System.Threading.Tasks</code>. The two types are the resources "
             "section 7 disposes."),

        panel(from_sample(FILE_APP),
              "2.4 · A file-based app — the whole program, no project file",
              "<b>Directives first, code after.</b> <code>#:project</code> references the rating library exactly "
              "as a <code>&lt;ProjectReference&gt;</code> would; <code>#:property</code> sets an MSBuild property — "
              "here <code>PublishAot=false</code> turns off the Native AOT publish that file-based apps default "
              "to. <code>args is [var first, ..]</code> is a "
              "list pattern — 5.5. The app passes the invariant culture to each call, the per-call form, so "
              "<code>dotnet premium-check.cs</code> printed <code>total 8,933.71 THB (net 8,316.00)</code> and "
              "<code>dotnet premium-check.cs -- 3</code> printed <code>declined: 3+ claims in 5 years</code> "
              "whatever the machine's culture."),

        {"type": "mermaid", "inline": True,
         "heading": "2.5 · What the compiler is given — a project build and a file-based run",
         "caption": "indigo = your source · slate = generated by the SDK · amber = inherited build settings · "
                    "teal = the compiler · green = output · dotted arrow = imported by MSBuild",
         "code": ('%%{init: {"flowchart": {"rankSpacing": 38, "nodeSpacing": 22}}}%%\n'
                  "flowchart LR\n"
                  '  E["Directory.Build.props<br/>net10.0 · nullable<br/>warnings as errors"]:::cfg\n'
                  '  F["premium-check.cs<br/>#: directives + code"]:::src\n'
                  f'  A["L02.Syntax.csproj<br/>{n_syntax_cs} .cs files + SDK-written<br/>'
                  'L02.Syntax.GlobalUsings.g.cs"]:::src\n'
                  '  V["virtual project<br/>premium-check.cs.csproj"]:::gen\n'
                  '  R["Roslyn<br/>C# 14 compiler"]:::tool\n'
                  '  O["assembly with a<br/>generated Main"]:::out\n'
                  "  E -.-> A\n"
                  "  E -.-> V\n"
                  "  F --> V\n"
                  "  A --> R\n"
                  "  V --> R\n"
                  "  R --> O\n"
                  "  classDef src fill:#c7d2fe,color:#1f2937,stroke:#6366f1;\n"
                  "  classDef gen fill:#e2e8f0,color:#1f2937,stroke:#475569;\n"
                  "  classDef cfg fill:#fde68a,color:#1f2937,stroke:#d97706;\n"
                  "  classDef tool fill:#ccfbf1,color:#1f2937,stroke:#0d9488;\n"
                  "  classDef out fill:#bbf7d0,color:#1f2937,stroke:#16a34a;\n")},

        {"type": "table", "heading": "2.6 · Date a codebase by its syntax — this lesson's C# by version",
         "cols": ["C# · released", "Syntax you meet in this lesson", "Shown in"],
         "rows": [
             ["<b>6</b> · Jul 2015", "<code>$\"…\"</code> interpolation · <code>?.</code> · <code>nameof</code> · "
                                     "exception filters", "3.5 · 4.1 · 4.2 · 7.1"],
             ["<b>7.0–7.3</b> · 2017–18", "tuples and deconstruction · <code>out var</code> · <code>throw</code> "
                                         "expressions · declaration patterns · <code>1_200</code> · "
                                         "<code>in</code> parameters", "3.3 · 5.1 · 5.4 · 6.2 · 6.3"],
             ["<b>8</b> · Sep 2019", "nullable reference types · switch expressions · property and tuple "
                                     "patterns · <code>??=</code> · <code>using</code> declarations · static local "
                                     "functions", "§4 · 5.1 · 5.3 · 6.3 · 7.1 · 7.2"],
             ["<b>9</b> · Nov 2020", "top-level statements · relational and logical patterns "
                                     "(<code>&lt; 25</code>, <code>or</code>, <code>not</code>)", "2.2 · 5.1 · 5.3"],
             ["<b>10</b> · Nov 2021", "file-scoped namespaces · <code>global using</code> · extended property "
                                      "patterns", "2.3 · 5.4"],
             ["<b>11</b> · Nov 2022", "raw string literals · list patterns", "3.5 · 5.5"],
             ["<b>12</b> · Nov 2023", "collection expressions <code>[…]</code> · primary constructors", "2.3 · 5.5"],
             ["<b>13</b> · Nov 2024", "<code>params</code> collections", "6.2"],
             ["<b>14</b> · Nov 2025", "null-conditional assignment · modifiers on untyped lambda parameters",
              "4.1 · 6.3"]]},

        # ═══════════════════════════ 3 · TYPES AND VALUES ═══════════════════════════
        {"type": "story", "heading": "3 · Types and values — decimal, strings and culture",
         "html": (
             "<p><b>The built-in types are the JVM's with better names, plus one that matters to you: "
             "<code>decimal</code>.</b> <code>int</code> is an alias for <code>System.Int32</code> — a struct, so "
             "<code>List&lt;int&gt;</code> holds raw integers and there is no <code>Integer</code> wrapper to "
             "unbox. <code>decimal</code> is a 16-byte base-10 number with 28–29 significant digits (" + FLOAT
             + "): a value type with literals and operators, where Java makes you call "
             "<code>BigDecimal.multiply</code>. It represents 0.1 exactly; <code>double</code> does not, and the "
             "two never convert implicitly. Rounding is a default too: <code>Math.Round</code> sends a midpoint "
             "to the even neighbour unless you pass a <code>MidpointRounding</code> (" + ROUND + "), where "
             "<code>BigDecimal.setScale</code> makes you name a mode.</p>"
             "<p><b>Integer overflow is silent by default.</b> Non-constant integral arithmetic runs in an "
             "<code>unchecked</code> context unless the <code>CheckForOverflowUnderflow</code> option is set, so "
             "with <code>int big = int.MaxValue</code>, <code>big + 1</code> wraps as in Java; "
             "<code>checked(…)</code> turns it into an <code>OverflowException</code>. The constant "
             "<code>int.MaxValue + 1</code> written directly does not compile at all (CS0220): constant "
             "expressions are checked. <code>decimal</code> throws on overflow in both contexts (" + CHECKED
             + "). Visual Basic makes the opposite default choice — 8.3.</p>"
             "<p><b>Strings are where a rating service quietly breaks.</b> Interpolated strings format numbers "
             "and dates with the <i>current culture</i>: the same premium prints as <code>8,933.71</code> or "
             "<code>8.933,71</code>, and a JSON payload built by interpolation changes shape. "
             "<code>IndexOf(string)</code>, <code>StartsWith(string)</code> and <code>Compare</code> are "
             "linguistic by default, while <code>==</code>, <code>Equals</code> and <code>Contains</code> are "
             "ordinal (" + STRINGS + "); since .NET 5 the linguistic rules come from ICU on current Windows as "
             "well as on Linux (" + ICU + "). And <code>th-TH</code> formats dates in the Thai Buddhist "
             "calendar — 2026 prints as 2569.</p>")},

        pair(from_text("""
            // Java: BigDecimal is a class — no literals, no operators
            BigDecimal sumInsured = new BigDecimal("550000");
            BigDecimal rate = new BigDecimal("0.021");
            BigDecimal basePremium = sumInsured.multiply(rate);

            double d = 0;
            BigDecimal m = BigDecimal.ZERO;
            for (int i = 0; i < 10; i++) {
                d += 0.1;
                m = m.add(new BigDecimal("0.1"));
            }
            System.out.println(d);             // 0.9999999999999999
            System.out.println(m);             // 1.0

            // no implicit double -> BigDecimal either
            BigDecimal vat = basePremium.multiply(
                BigDecimal.valueOf(0.07));
            """, "java", file="the idea you already know"),
             from_sample(f"{SYN}/TypesTour.cs", "money"),
             "3.1 · Money — Java BigDecimal vs C# decimal",
             "<b>The same precision rule with far less ceremony</b> (" + SAME + "). <code>decimal</code> is a "
             "value type with a literal suffix (<code>m</code>) and ordinary operators. The sample printed "
             "<code>11550.000 808.50000</code>: a decimal keeps the scale of its operands, like "
             "<code>BigDecimal</code>. Format with <code>:N2</code> or round explicitly before you show or store "
             "a premium."),

        pair(from_text("""
            // Java: BigDecimal makes you name the mode
            BigDecimal duty = new BigDecimal("2.345");
            duty.setScale(2, RoundingMode.HALF_UP);    // 2.35
            duty.setScale(2, RoundingMode.HALF_EVEN);  // 2.34
            duty.setScale(2);  // ArithmeticException: rounding needed

            // Math.round on a double: ties go toward +infinity
            Math.round(2.5);                           // 3
            """, "java", file="the idea you already know"),
             from_sample(RULES, "round"),
             "3.2 · Rounding — Java's explicit mode vs C#'s silent default",
             "<b>The C# default is the one a Java engineer does not expect</b> (" + TRAP + "). "
             "<code>Math.Round</code> without a mode is banker's rounding, <code>MidpointRounding.ToEven</code> "
             "(" + ROUND + "): a satang at the midpoint goes to the even digit, so a premium can come out one "
             "satang lower than a HALF_UP system computes. The rating library states its rule in one place, and "
             "the passing test <code>Round_is_half_away_from_zero_not_bankers</code> asserts both results. "
             "Calculate (9.4) rounds every step through it."),

        panel(from_sample(f"{SYN}/TypesTour.cs", "numbers"),
              "3.3 · Aliases, var, const and overflow",
              "<b>Printed:</b> <code>System.Int32 1200 2024 2</code>, then <code>-2147483648</code> for "
              "<code>big + 1</code>, then <code>checked: OverflowException</code>. <code>var</code> is inference, "
              "not immutability — the variable can be reassigned. A <code>const</code> is copied into every "
              "assembly that reads it, so change a public <code>const</code> and its callers keep the old value "
              "until they are rebuilt; use <code>static readonly</code> for values that may change."),

        {"type": "cards",
         "band": {"title": "3.4 · The built-in types you will use every day", "note": "value view", "tone": "violet"},
         "cards": type_cards[:3]},
        {"type": "cards", "toc": False,
         "band": {"title": "3.4 · The built-in types (continued)", "note": "value view", "tone": "violet"},
         "cards": type_cards[3:]},

        panel(from_sample(f"{SYN}/StringsTour.cs", "strings"),
              "3.5 · Interpolation, verbatim and raw string literals",
              "<b>The culture is part of the output.</b> The same interpolation printed "
              "<code>Toyota total 8,933.71 THB</code> with the invariant culture and "
              "<code>Toyota total 8.933,71 THB</code> through <code>string.Create(de, …)</code>. The raw literal "
              "needs no escaped quotes; <code>$$</code> makes <code>{{ }}</code> the hole marker so single braces "
              "stay literal JSON. Build real JSON with <code>System.Text.Json</code>, not interpolation."),

        panel(from_sample(f"{SYN}/StringsTour.cs", "comparison"),
              "3.6 · Comparison and culture — the traps with measured output",
              "<b>Printed:</b> <code>FİLE</code>, <code>True</code>, <code>0</code>, <code>-1</code>, "
              "<code>True</code>, <code>1/10/2569</code>, <code>2026-10-01</code>. The linguistic "
              "<code>IndexOf</code> found <code>\"MQTH\"</code> inside a partner code that contains an invisible "
              "soft hyphen; the ordinal search did not. For identifiers, keys and protocol text, pass "
              "<code>StringComparison.Ordinal</code> or <code>OrdinalIgnoreCase</code> every time. Analyzers "
              "CA1307, CA1309 and CA1310 find the call sites that do not, but they are off by default — Microsoft "
              "documents turning them on with <code>AnalysisMode All</code>."),

        # ═══════════════════════════ 4 · NULLABILITY ═══════════════════════════
        {"type": "story", "heading": "4 · Nullability — annotations, not a type system",
         "html": (
             "<p><b>C# nullable reference types look like Kotlin's null safety and are enforced like TypeScript's "
             "<code>strictNullChecks</code>: by the compiler only.</b> With <code>&lt;Nullable&gt;enable</code> "
             "(set by current templates, and in this repository), <code>string</code> means “should not be null” "
             "and <code>string?</code> means “may be null”. The compiler tracks a <i>null-state</i> — not-null or "
             "maybe-null — through assignments and checks, and warns. The runtime behaviour of the program is "
             "unchanged: <code>string</code> and <code>string?</code> are both <code>System.String</code> "
             "(" + NRT + ").</p>"
             "<p><b>Value types are different: <code>int?</code> is a real type.</b> It compiles to "
             "<code>Nullable&lt;int&gt;</code>, a struct with <code>HasValue</code> and <code>Value</code>, and "
             "boxing a null <code>int?</code> gives a null reference. So the same <code>?</code> is a run-time "
             "wrapper on a value type and a compile-time comment on a reference type.</p>"
             "<p><b>Null still gets in wherever the compiler cannot see.</b> <code>!</code> — the null-forgiving "
             "operator — only silences the warning for that one expression (the variable stays maybe-null); "
             "unlike Kotlin's <code>!!</code> it never throws. Deserializers "
             "and reflection ignore annotations: <code>System.Text.Json</code> stores a JSON <code>null</code> "
             "into a non-nullable property unless you opt in to <code>RespectNullableAnnotations</code>, which "
             "arrived in .NET 9 and is off by default (" + JSONNULL + "). For a quote API fed by ~30 external "
             "partners, validate at the boundary and treat annotations as documentation that the compiler "
             "checks.</p>"
             "<p><b>C# 14 closes one ergonomic gap.</b> <code>?.</code> may now appear on the left of an "
             "assignment: <code>draft?.Note = …</code> assigns only when <code>draft</code> is not null, and the "
             "right side is not evaluated otherwise; compound assignment works, <code>++</code> and "
             "<code>--</code> do not (" + CS14 + ").</p>")},

        pair(from_text("""
            val note: String? = lookUpNote("Q-0002")  // maybe-null
            val length = note?.length ?: 0             // ?. then ?:
            val shown = note ?: "no note"              // no ??=
            println("$shown ($length)")

            val sure = lookUpNote("Q-0001")!!          // THROWS if null
            println(sure.uppercase())

            val draft: QuoteDraft? = findDraft("Q-0001")
            draft?.note = "young driver"           // safe-call assign
            draft?.let { it.loading += BigDecimal("0.20") }
            println("${draft?.note} ${draft?.loading}")
            """, "kotlin", file="the idea you already know"),
             from_sample(f"{SYN}/NullsTour.cs", "nulls"),
             "4.1 · The null operators — Kotlin vs C#",
             "<b><code>?.</code> is the same</b> (" + SAME + "), <b><code>??</code> is Elvis renamed</b> ("
             + RENAMED + ")<b>, and <code>!</code> is a trap</b> (" + TRAP + "). "
             "<code>??=</code> assigns only when null and has no Kotlin twin; C# 14's "
             "<code>draft?.Note = …</code> matches Kotlin's safe-call assignment. Kotlin's <code>!!</code> is a "
             "run-time check that throws; C#'s <code>!</code> emits nothing. The sample printed "
             "<code>no note (0)</code>, <code>RENEWAL</code> and <code>young driver 0.20</code>."),

        panel(from_sample(f"{SYN}/NullsTour.cs", "runtime"),
              "4.2 · What survives to run time",
              "<b>Printed:</b> <code>True</code>, <code>0</code>, <code>True</code>, <code>True</code>, "
              "<code>True</code>, then <code>RespectNullableAnnotations: JsonException</code>. The non-nullable "
              "<code>Name</code> held <code>null</code> after default deserialization, with no warning anywhere "
              "in the code. The option covers explicit <code>null</code> values on non-generic members only — a "
              "missing property still leaves the default."),

        {"type": "mermaid", "inline": True,
         "heading": "4.3 · Null-state analysis — what the compiler tracks for one variable",
         "caption": "amber = maybe-null · green = not-null · red = the diagnostic you get · note!.Length silences "
                    "the warning for that expression only, the variable stays maybe-null · the analysis does not "
                    "look inside the methods you call",
         "code": ("stateDiagram-v2\n"
                  "  direction LR\n"
                  "  state \"maybe-null\" as Maybe\n"
                  "  state \"not-null\" as NotNull\n"
                  "  state \"CS8602 warning, an error in this repo\" as Warn\n"
                  "  [*] --> Maybe: string? note = LookUpNote()\n"
                  "  [*] --> NotNull: string s = a literal\n"
                  "  Maybe --> NotNull: null check, ??= or a not-null value\n"
                  "  NotNull --> Maybe: assigned a string? value\n"
                  "  Maybe --> Warn: note.Length\n"
                  "  Warn --> NotNull: assumed not-null after it\n"
                  "  classDef maybe fill:#fde68a,color:#1f2937,stroke:#d97706\n"
                  "  classDef ok fill:#bbf7d0,color:#1f2937,stroke:#16a34a\n"
                  "  classDef warn fill:#fee2e2,color:#1f2937,stroke:#dc2626\n"
                  "  class Maybe maybe\n"
                  "  class NotNull ok\n"
                  "  class Warn warn\n")},

        figure_heading("4.4 · Kotlin guarantees vs C# promises"),
        {"type": "twocol", "boxes": [
            {"heading": "Kotlin guarantees — at run time too", "tone": "amber",
             "items": ["<code>String</code> and <code>String?</code> are different types to the compiler",
                       "The hole: Java platform types (<code>String!</code>), the twin of C#'s oblivious "
                       "libraries",
                       "<code>!!</code> throws <code>NullPointerException</code> at that line",
                       "Parameters of public functions get generated null checks"]},
            {"heading": "C# promises — at compile time only", "tone": "violet",
             "items": ["<code>string</code> and <code>string?</code> are the same <code>System.String</code>",
                       "Unannotated libraries are “oblivious” — no warnings either way",
                       "<code>!</code> suppresses a warning and generates no code",
                       "Guard public entry points yourself: <code>ArgumentNullException.ThrowIfNull(x)</code>"]}]},

        # ═══════════════════════════ 5 · PATTERNS ═══════════════════════════
        {"type": "story", "heading": "5 · Control flow and pattern matching",
         "html": (
             "<p><b>The switch expression is Kotlin's <code>when</code> with a richer pattern language.</b> An "
             "input goes on the left, arms are <code>pattern =&gt; value</code>, the first match wins, and the "
             "whole thing is an expression. Patterns compose: relational (<code>&lt; 25</code>), logical "
             "(<code>3 or 4</code>, <code>is not null</code>), property (<code>{ LicenceYears: &gt;= 5 }</code>), "
             "positional and tuple (<code>(Commercial, &gt; 3_000)</code>) and list patterns "
             "(<code>[\"RATE\", var cls, ..]</code>) — the reference lists ten kinds (" + PATTERNS + ").</p>"
             "<p><b>This is the rating-rule notation you want.</b> A tariff table maps almost line for line onto "
             "arms, and the samples' age, claims, no-claim-bonus and commercial-use rules are each one switch. "
             "Java 21 finalised pattern switch with <code>when</code> guards (" + JEP441 + ") and record patterns "
             "(" + JEP440 + "); Kotlin 2.2 made guard conditions in <code>when</code> stable (" + KT22 + "). C# "
             "goes further on property, relational and list patterns.</p>"
             "<p><b>The trap is exhaustiveness.</b> Kotlin proves a <code>when</code> over an enum complete. A C# "
             "enum is an integer with names: <code>(CoverageClass)7</code> compiles, so a switch over an enum "
             "without a discard arm draws a compiler warning — an error in this repository — and would throw "
             "<code>SwitchExpressionException</code> at run time. Every rule therefore ends in <code>_</code>, "
             "and the useful decision is what the discard does: return a default, or throw. C# 15, in preview "
             "with .NET 11, adds <code>closed</code> class hierarchies and <code>union</code> types whose switches "
             "the compiler does prove complete (" + CS15 + "); enums stay open.</p>")},

        pair(from_text("""
            fun ageLoading(age: Int): BigDecimal = when {
                age < 18 -> error("under 18")    // throws
                age < 25 -> BigDecimal("0.20")   // young driver
                else -> BigDecimal.ZERO
            }

            // with a subject, a range reads like a tariff row:
            // when (age) { in 18..24 -> BigDecimal("0.20") ... }
            """, "kotlin", file="the idea you already know"),
             from_sample(RULES, "age-loading"),
             "5.1 · A rating rule — Kotlin when vs a C# switch expression",
             "<b>The same shape</b> (" + SAME + "). Relational patterns (C# 9) replace the repeated "
             "<code>age &lt;</code>, and <code>throw</code> is allowed as an arm because it is an expression. Arms "
             "are checked top to bottom, so <code>&lt; 25</code> only ever sees an age of 18 or more; the compiler "
             "reports an arm that can never match."),

        pair(from_sample(RULES, "base-rate"), from_sample(f"{SYN}/PatternsTour.cs", "enum-trap"),
             "5.2 · The enum trap — a complete switch that still needs its discard arm",
             "<b>Four named values, five arms</b> (" + TRAP + "). <code>BaseRate</code> covers every "
             "<code>CoverageClass</code>, yet <code>(CoverageClass)7</code> compiles because an enum is an "
             "<code>int</code> with names. Without the <code>_</code> arm the compiler warns (an error in this "
             "repository) and the switch would throw <code>SwitchExpressionException</code>; with it, the rule "
             "chooses its own exception. <b>Printed:</b> <code>False</code>, then "
             "<code>discard arm hit: coverage</code>. Validate input with <code>Enum.IsDefined</code> before it "
             "reaches a rule."),

        panel(from_sample(RULES, "rules"),
              "5.3 · Property and tuple patterns in the rating rules",
              "<b>Three rules, three pattern styles.</b> <code>NoClaimBonus</code> tests a record's properties, "
              "<code>UseLoading</code> switches on a tuple of two values, and <code>ClaimsLoading</code> declines "
              "by throwing a domain exception. Tested by "
              + str(tests.get("NoClaimBonus", 0) + tests.get("UseLoading", 0) + tests.get("ClaimsLoading", 0))
              + " of the " + str(n_tests) + " test cases."),

        panel(from_sample(f"{SYN}/PatternsTour.cs", "patterns"),
              "5.4 · Type, property and declaration patterns on an object",
              "<b>Printed:</b> <code>heavy commercial</code>, then <code>recent or not a vehicle</code>. "
              "<code>SumInsured.Amount: &gt; 2_000_000m</code> is an <i>extended property pattern</i> (C# 10) "
              "with a decimal constant. <code>input is Vehicle { Year: &lt; 2010 } old</code> tests the type and a "
              "property, then binds the narrowed variable — the smart cast you know from Kotlin, with the variable "
              "named explicitly.", keep=True),

        panel(from_sample(f"{SYN}/PatternsTour.cs", "list-patterns"),
              "5.5 · List patterns — parsing a partner rate file",
              "<b>Printed:</b> <code>Class1 at 2.1%</code>, <code>rate line without a percent</code>, "
              "<code>Class2Plus at 1.2% (+1 field)</code>, <code>end of file</code>. <code>..</code> is a slice and "
              "<code>.. var rest</code> captures it. The array itself is a collection expression (C# 12) — "
              + ref(4) + " covers collections."),

        {"type": "table", "heading": "5.6 · Pattern kinds — the C# form, its version and your nearest equivalent",
         "cols": ["Pattern", "C# form", "Since", "Kotlin 2 · Java 21"],
         "rows": [
             ["Constant", "<code>0 =&gt; 0m, 1 =&gt; 0.10m</code>", "C# 7.0",
              "<code>0 -&gt;</code> · <code>case 0 -&gt;</code>"],
             ["Declaration / type", "<code>input is Vehicle v</code> · <code>Vehicle =&gt; …</code>",
              "C# 7.0 · type-only C# 9", "<code>is Vehicle</code> smart cast · <code>case Vehicle v</code>"],
             ["Property", "<code>{ LicenceYears: &gt;= 5 }</code> · <code>{ A.B: 0 }</code>", "C# 8 · extended C# 10",
              "none · record pattern (positional only)"],
             ["Positional / tuple", "<code>(VehicleUse.Commercial, &gt; 3_000)</code>", "C# 8",
              "none · <code>case Vehicle(var use, var cc)</code>"],
             ["Relational", "<code>&lt; 25 =&gt; 0.20m</code>", "C# 9",
              "<code>in 18..24 -&gt;</code> · a <code>when</code> guard"],
             ["Logical", "<code>3 or 4</code> · <code>is not null</code>", "C# 9",
              "<code>3, 4 -&gt;</code> · <code>case 3, 4 -&gt;</code>"],
             ["List and slice", "<code>[\"RATE\", var cls, ..]</code>", "C# 11", "none · none"],
             ["var and discard", "<code>var (x, y)</code> · <code>_ =&gt; 0m</code>", "C# 7.0 · discard arm C# 8",
              "<code>else -&gt;</code> · <code>default -&gt;</code>"]]},

        {"type": "chart", "heading": "5.7 · Pattern-matching support across the languages you read",
         "kind": "heatmap",
         "args": {"rows": ["Switch as an expression", "Type test and bind", "Relational or range arms",
                           "Property patterns", "List patterns", "and / or / not", "Guard clauses",
                           "Checked exhaustiveness"],
                  "cols": ["C#", "VB", "Java", "Kotlin", "TS"],
                  "matrix": [[2, 0, 2, 2, 0], [2, 1, 2, 2, 1], [2, 2, 1, 2, 0], [2, 0, 1, 0, 1],
                             [2, 0, 0, 0, 0], [2, 1, 1, 1, 0], [2, 0, 2, 2, 0], [1, 0, 2, 2, 1]],
                  "cell": 36, "tone": "indigo", "fmt": lambda v: {2: "yes", 1: "some", 0: "—"}[int(v)]},
         "caption": "C# 14 · VB · Java 21 · Kotlin 2.2 · TypeScript 5 · yes = first-class syntax · some = a subset, "
                    "a statement form or an idiom · — = none · a rubric, not a benchmark",
         "note": "<b>C# has the widest pattern language; Java and Kotlin have the stronger exhaustiveness "
                 "check.</b> C#'s “some” is the enum gap: a switch over an enum is never proven complete. VB's "
                 "<code>Select Case</code> handles ranges well and little else. TypeScript's “some” is narrowing "
                 "on <code>instanceof</code> or a discriminant property, plus the <code>never</code> "
                 "exhaustiveness idiom. The cell values are the author's judgement (" + ESTIMATE + ")."},

        # ═══════════════════════════ 6 · METHODS ═══════════════════════════
        {"type": "story", "heading": "6 · Methods and parameters",
         "html": (
             "<p><b>C# method syntax is a superset of what Kotlin and TypeScript give you.</b> Named and optional "
             "arguments work as in Kotlin; <code>params</code> is varargs, and since C# 13 it accepts any "
             "collection type, including <code>ReadOnlySpan&lt;T&gt;</code>, so a call no longer has to allocate "
             "an array (" + CS13 + "). Expression-bodied members (<code>=&gt;</code>) are Kotlin's "
             "single-expression functions. Local functions can be <code>static</code>, which makes the compiler "
             "refuse any accidental capture.</p>"
             "<p><b>C# can pass by reference, and for <code>ref</code> and <code>out</code> the call site has to "
             "say so</b> (<code>in</code> may be omitted). <code>ref</code> lets the "
             "callee write to the caller's variable, <code>out</code> requires the callee to assign it, and "
             "<code>in</code> passes a read-only reference. Neither Java nor Kotlin nor TypeScript has these; you "
             "will meet them in the <code>TryParse</code> pattern everywhere in the base library and in "
             "performance-sensitive code. Value tuples give you multiple return values with named elements and "
             "deconstruction — the answer to Kotlin's <code>Pair</code> and TypeScript's tuple types.</p>"
             "<p><b>Two versioning traps sit in the signature.</b> An optional parameter's default is copied into "
             "the <i>caller</i> at compile time, like a <code>const</code>: change it in a library and existing "
             "callers keep the old value until they recompile. And tuple element names do not exist at run time, "
             "so a public API that returns <code>(decimal, string)</code> is weaker than one that returns a small "
             "record — " + ref(3) + ".</p>")},

        {"type": "table", "heading": "6.1 · Parameter passing at a glance",
         "cols": ["Form", "What the callee gets", "Caller writes", "Nearest in your stack"],
         "rows": [
             ["(none) value type", "A copy of the value", "<code>Discount(13_860m)</code>", "Java primitives"],
             ["(none) reference type", "A copy of the reference", "<code>Calculate(request)</code>",
              "Java / Kotlin / TS objects"],
             ["<code>ref</code>", "An alias of the caller's variable", "<code>ref premium</code>",
              "none — return the value or use a holder"],
             ["<code>out</code>", "An alias it must assign", "<code>out var claims</code>",
              "none — return a <code>Pair</code> or tuple"],
             ["<code>in</code>", "A read-only alias (avoids copying a large struct)", "optional <code>in</code>",
              "none"],
             ["<code>params</code>", "Any collection type (C# 13)", "<code>Sum(8_316m, 33.26m)</code>",
              "<code>vararg</code> · <code>...rest</code>"],
             ["optional", "The default, compiled into the caller", "omit it, or name the next one",
              "Kotlin and TS defaults, resolved in the callee"]]},

        pair(from_text("""
            // TypeScript: defaults, rest parameters, tuples
            function discount(amount: number, rate = 0.3,
                              roundUp = false): number {
              return roundUp ? Math.ceil(amount * rate)
                             : amount * rate;
            }

            function sum(...parts: number[]): number {
              return parts.reduce((a, b) => a + b, 0);
            }

            function bonus(d: Driver): [bonus: number, reason: string] {
              return d.claimsLast5Years === 0
                ? [noClaimBonus(d), "claim-free"]
                : [0, "has claims"];
            }

            // no by-reference parameters in TypeScript:
            // return the new value instead
            function load(premium: number, rate: number): number {
              return premium + premium * rate;
            }
            """, "typescript", file="the idea you already know"),
             from_sample(f"{SYN}/MethodsTour.cs", "declarations"),
             "6.2 · Declaring methods — TypeScript vs C#",
             "<b>Defaults, rest and tuples are renamed</b> (" + RENAMED + ")<b>; <code>ref</code> and "
             "<code>in</code> are different</b> (" + DIFFERENT + "). <code>params ReadOnlySpan&lt;decimal&gt;</code> takes arguments like "
             "<code>...parts</code> without allocating an array. <code>Load</code> changes the caller's variable "
             "in place — something TypeScript can only simulate by returning a value."),

        panel(from_sample(f"{SYN}/MethodsTour.cs", "calls"),
              "6.3 · Calling them — named arguments, deconstruction, out var and a C# 14 lambda",
              "<b>Printed:</b> <code>claims 2</code>, then "
              "<code>5,544.00 2,772.00 8,933.71 0.40 claim-free 13,860.00</code>, then <code>parsed 2.1</code>. "
              "Named arguments may skip optional parameters and change order. <code>ref</code> is repeated at the "
              "call site so a reviewer sees the write. The figures are the worked example's discount, its "
              "young-driver loading and its total (9.5); <code>roundUp</code> is there to show an optional "
              "<code>bool</code>, not because the tariff rounds up — it rounds half away from zero (3.2). C# 14 "
              "lets a lambda declare <code>out result</code> without spelling its type; lambdas and delegates "
              "belong to " + ref(4) + "."),

        # ═══════════════════════════ 7 · EXCEPTIONS AND RESOURCES ═══════════════════════════
        {"type": "story", "heading": "7 · Exceptions and resources",
         "html": (
             "<p><b>Every .NET exception is unchecked, so the signature tells you nothing.</b> There is no "
             "<code>throws</code> clause; a method that can decline a quote documents it with an XML "
             "<code>&lt;exception&gt;</code> tag and a test. Rethrow with <code>throw;</code> — "
             "<code>throw e;</code> restarts the stack trace, and analyzer rule " + CA2200 + ", on as a warning "
             "by default, made it a build error in this repository. <code>throw</code> is also an expression, "
             "so it fits on the right of <code>??</code>, in a conditional, or as a switch arm (" + EXC + ").</p>"
             "<p><b>Exception filters decide before anything unwinds.</b> <code>catch (E e) when (…)</code> "
             "evaluates its condition while the throwing frames are still on the stack — before any inner "
             "<code>finally</code> runs. A filter that returns <code>false</code> leaves the exception and its "
             "stack trace untouched, which makes <code>when (Log(e))</code> a way to log without catching. The "
             "sample proves the order; the sequence diagram shows why.</p>"
             "<p><b><code>using</code> is try-with-resources without the block.</b> A <i>using declaration</i> "
             "(<code>using var x = …;</code>, C# 8) disposes at the end of the enclosing scope, and several "
             "declarations dispose in reverse order. <code>await using</code> does the same for "
             "<code>IAsyncDisposable</code> — a partner connection, a database transaction (" + USING + "). "
             "To write a disposable type, a <code>sealed</code> class needs only a public <code>Dispose()</code>, "
             "as <code>AuditScope</code> in 2.3 shows; an unsealed class follows the dispose pattern — a "
             "<code>protected virtual Dispose(bool)</code> that subclasses override — and needs a finalizer only "
             "when it holds an unmanaged handle directly (" + DISPOSE + ").</p>")},

        pair(from_text("""
            // Java: try-with-resources + a checked exception
            try (var audit = new AuditScope("audit");
                 var trace = new AuditScope("trace")) {
                var request = Examples.youngDriver(3);
                var premium = calculator.calculate(request);
                System.out.println(premium.total());
            } catch (QuoteDeclinedException e) {
                if (!e.getReason().contains("claims")) {
                    throw e;               // no filter: rethrow
                }
                System.out.println("declined: " + e.getReason());
            }
            // trace, then audit, are closed after the try
            """, "java", file="the idea you already know"),
             from_sample(f"{SYN}/ErrorsTour.cs", "resources"),
             "7.1 · Resources and filtered catch — Java vs C#",
             "<b>Renamed, with one real difference</b> (" + RENAMED + "). The Java resources close when the "
             "<code>try</code> "
             "block ends; the C# using declarations live until the end of the method. The filter replaces "
             "catch-check-rethrow. Printed: <code>declined: 3+ claims in 5 years</code>, <code>dispose trace</code>, "
             "<code>dispose audit</code>."),

        panel(from_sample(f"{SYN}/ErrorsTour.cs", "filter-order"),
              "7.2 · When does a filter run? Proven by the sample",
              "<b>Printed, in this order:</b> <code>filter sees QuoteDeclinedException</code>, "
              "<code>inner finally</code>, <code>catch block</code>. The filter ran while <code>Rate()</code> was "
              "still on the stack; only after it returned <code>true</code> did the runtime unwind — running the "
              "inner <code>finally</code> — and enter the catch block."),

        {"type": "mermaid", "inline": True,
         "heading": "7.3 · Two-pass exception handling",
         "caption": "pass 1 searches for a handler and runs filters with the stack intact · pass 2 unwinds, runs "
                    "finally blocks, then the catch block",
         "code": ('%%{init: {"theme":"base","themeVariables": {"actorBkg":"#e0e7ff","actorBorder":"#4f46e5",'
                  '"actorTextColor":"#1f2937","noteBkgColor":"#fef3c7","noteBorderColor":"#d97706",'
                  '"noteTextColor":"#1f2937","signalColor":"#334155","signalTextColor":"#1f2937",'
                  '"sequenceNumberColor":"#ffffff","fontSize":"15px"},'
                  '"sequence": {"messageMargin": 22, "boxMargin": 6, "noteMargin": 10, "actorMargin": 70}}}%%\n'
                  "sequenceDiagram\n"
                  "  autonumber\n"
                  "  participant F as FilterOrder: catch when\n"
                  "  participant R as Rate: try finally\n"
                  "  participant CLR as .NET runtime\n"
                  "  F->>R: Rate()\n"
                  "  R->>CLR: throw QuoteDeclinedException\n"
                  "  Note over R,CLR: pass 1 - find a handler, nothing unwound yet\n"
                  "  CLR->>F: evaluate when (Log(e))\n"
                  "  F-->>CLR: true\n"
                  "  Note over R,CLR: pass 2 - unwind the stack\n"
                  "  CLR->>R: run the inner finally\n"
                  "  CLR->>F: run the catch block\n")},

        # ═══════════════════════════ 8 · VB ALONGSIDE ═══════════════════════════
        {"type": "story", "heading": "8 · Visual Basic alongside",
         "html": (
             "<p><b>The C# language tour has a Visual Basic twin, and it reads like a verbose cousin rather than a "
             "stranger.</b> The twin covers types, nulls, branching, methods and errors — strings and culture are "
             "left out because they are the same framework calls. <code>Dim x As Decimal</code> declares, "
             "<code>Nothing</code> is null, <code>If(a, b)</code> is <code>??</code> and <code>If(c, a, b)</code> "
             "is the conditional operator — both short-circuit, unlike the legacy <code>IIf</code> function that "
             "evaluates all its arguments (" + VBIF + "). <code>Select Case</code> handles ranges "
             "(<code>Case 18 To 24</code>, <code>Case Is &lt; 18</code>); <code>Using … End Using</code> and "
             "<code>Catch … When</code> are the same resource scope and exception filter (" + VBTRY + ").</p>"
             "<p><b>What VB lacks is the post-2015 syntax.</b> No nullable reference annotations "
             "(<code>String</code> is simply nullable), no switch expression or property and list patterns, no "
             "<code>??=</code>, no <code>?.</code> on the left of an assignment, no tuple deconstruction. The VB "
             "code reaches the same results with <code>If … Is Nothing</code> and statements — which is why a "
             "migration estate's VB rating code is longer, not wrong.</p>"
             "<p><b>One default is reversed, and it changes behaviour.</b> VB checks integer overflow unless "
             "compiled with <code>-removeintchecks</code> (" + VBINT + "): the same <code>big + 1</code> that "
             "wraps silently in C# threw <code>OverflowException</code> in <code>L02.SyntaxVb</code> (8.3). "
             "Porting VB arithmetic to C# without <code>checked</code> removes a guard nobody wrote down. The "
             "rest of VB's semantics are the subject of " + ref(6) + ".</p>")},

        pair(from_sample(RULES, "age-loading"), from_sample(VBT, "select-case"),
             "8.1 · The age loading — C# switch expression vs VB Select Case",
             "<b>Same band, same result.</b> <code>Select Case</code> is a statement, not an expression, so each "
             "arm is a <code>Case</code> line plus a <code>Return</code> or a <code>Throw</code>; "
             "<code>Case Is &lt; 18</code> is its relational pattern and <code>Case 18 To 24</code> its range form "
             "— the same rule the C# switch writes as <code>&lt; 25</code> below a <code>&lt; 18</code> arm. The VB "
             "run printed <code>age 23 loading 0.2</code>."),

        pair(from_sample(f"{SYN}/ErrorsTour.cs", "resources"), from_sample(VBT, "errors"),
             "8.2 · Resources and a filtered catch — C# using var vs VB Using … End Using",
             "<b>A VB <code>Using</code> is a block, like Java's try-with-resources.</b> One statement declares "
             "both resources and disposes them in reverse order at <code>End Using</code>, where the C# using "
             "declarations live to the end of the method. <code>Catch … When</code> is the same filter, "
             "evaluated before anything unwinds (7.2). VB printed the C# lines of 7.1: "
             "<code>declined: 3+ claims in 5 years</code>, <code>dispose trace</code>, <code>dispose audit</code>."),

        pair(from_sample(f"{SYN}/TypesTour.cs", "overflow"), from_sample(VBT, "overflow"),
             "8.3 · Overflow — the one default VB reverses",
             "<b>The same <code>big + 1</code>, two behaviours</b> (" + TRAP + "). C# printed "
             "<code>-2147483648</code>; VB threw and printed <code>VB: OverflowException without checked</code>. "
             "Neither compiler accepts the constant form: written directly, <code>int.MaxValue + 1</code> is error "
             "CS0220 and <code>Integer.MaxValue + 1</code> is error BC30439 (both measured on the build machine)."),

        {"type": "table", "heading": "8.4 · This lesson's C# in Visual Basic",
         "cols": ["C#", "Visual Basic", "Watch for"],
         "rows": [
             ["<code>string?</code> · <code>int?</code>", "<code>String</code> · <code>Integer?</code>",
              "VB has no nullable reference annotations"],
             ["<code>null</code> · <code>is null</code> · <code>is not null</code>",
              "<code>Nothing</code> · <code>Is Nothing</code> · <code>IsNot Nothing</code>",
              "<code>Nothing</code> assigned to <code>Integer</code> means 0"],
             ["<code>a ?? b</code> · <code>c ? a : b</code>", "<code>If(a, b)</code> · <code>If(c, a, b)</code>",
              "Never <code>IIf</code>: it evaluates both branches"],
             ["<code>0.07m</code> · <code>(decimal)0.07</code>", "<code>0.07D</code> · <code>CDec(0.07)</code>",
              "VB's <code>D</code> suffix is Decimal, C#'s <code>d</code> is double — C# money needs "
              "<code>m</code>; Option Strict On makes VB write <code>CDec</code>"],
             ["Unchecked <code>int</code> arithmetic", "Checked by default", "Porting to C# drops the guard"],
             ["<code>switch</code> expression + patterns", "<code>Select Case</code> with <code>Case Is</code> and "
              "<code>To</code>", "A statement — no property or list patterns"],
             ["<code>x is Vehicle v</code>", "<code>TypeOf x Is Vehicle</code> + <code>DirectCast</code>",
              "Two steps: test, then cast"],
             ["<code>Discount(x, roundUp: true)</code>", "<code>Discount(x, roundUp:=True)</code>",
              "<code>:=</code> for named arguments"],
             ["<code>ref premium</code> at the call", "<code>ByRef</code> in the declaration only",
              "A VB call site does not show the write"],
             ["<code>using var a = …;</code>", "<code>Using a As New …</code> … <code>End Using</code>",
              "Several resources in one <code>Using</code>, disposed in reverse"],
             ["<code>catch (E e) when (…)</code>", "<code>Catch e As E When …</code>", "Same two-pass semantics"]]},

        # ═══════════════════════════ 9 · HANDS-ON ═══════════════════════════
        {"type": "story", "heading": "9 · Hands-on — run the tour, the tests and the file-based app",
         "html": (
             "<p><b>" + str(n_proj) + " projects and one file, all run from the repository root.</b> The tour "
             "prints in both languages, the rating rules meet their " + str(n_tests) + " test cases, and "
             "<code>premium-check.cs</code> runs with no project file at all.</p>"
             "<p><b>The tests met a decimal trap of their own.</b> An attribute argument must be a constant of an "
             "attribute parameter type, and <code>decimal</code> is not one: <code>[InlineData(24, 0.20m)]</code> "
             "fails with CS0182. The tests use <code>TheoryData&lt;int, decimal&gt;</code> for decimal data, "
             "integer percentages where that reads better, and ISO date strings parsed with the invariant culture "
             "for <code>DateOnly</code>. xUnit itself is the subject of " + ref(10) + ".</p>"
             "<p><b>The worked example is the number to check your reading against.</b> A 2024 private car "
             "insured for 550,000 THB, Class 1, a 23-year-old driver with four claim-free licence years, starting "
             "1 October 2026: " + f"{p['Base']:,.2f}" + " base, +20% young-driver loading, −40% no-claim bonus, "
             "0.4% stamp duty and 7% VAT — <b>" + f"{p['Total']:,.2f}" + " THB, illustrative, not a real "
             "tariff</b>.</p>"
             "<p><b>It is also the number to carry forward.</b> Every lesson of this track prices with this one "
             "tariff — the base rate per coverage class, the young-driver, claims and commercial-use loadings, the "
             "no-claim ladder of 0/20/25/30/40/50% by claim-free licence year, and the two rounded taxes — so a "
             "quote you re-rate in a later lesson comes out at the same satang. A lesson that varies it on purpose "
             "says so and names it: the legacy rounding and typing quirks of " + ref(6) + " are the deliberate "
             "case. The decline at three claims in five years is part of the tariff too; here it is a "
             "<code>QuoteDeclinedException</code> (§7), and a lesson that teaches data instead of exceptions "
             "records it as a declined status.</p>")},

        panel(from_text("""
            # from the repository root, .NET 10 SDK first on PATH
            dotnet run --project lesson-02-csharp-language-essentials/samples/L02.Syntax
            dotnet run --project lesson-02-csharp-language-essentials/samples/L02.SyntaxVb
            dotnet test lesson-02-csharp-language-essentials/samples/L02.Rating.Tests
            python 0-script/verify_samples.py --only 2    # every project: build, test, run
            # the file-based app: no project file, arguments after --
            cd lesson-02-csharp-language-essentials/samples/file-based
            dotnet premium-check.cs
            dotnet premium-check.cs -- 3
            """, "shell"),
              "9.1 · Commands",
              "<b>No separate restore or build step:</b> <code>dotnet run</code> and <code>dotnet test</code> "
              "restore and build first. Everything after <code>--</code> goes to the app as <code>args</code>. "
              "<code>verify_samples.py</code> covers the projects, not the file-based app."),

        pair(from_text(r"""
            L02.Syntax - C# in MotorQuote terms

            [types]
            System.Int32 1200 2024 2
            -2147483648
            checked: OverflowException
            0.9999999999999999
            1.0
            11550.000 808.50000

            [strings]
            Toyota total 8,933.71 THB
            Toyota total 8.933,71 THB
            C:\quotes\2026\Q-0001.json
            { "make": "Toyota", "total": 8933.71 }
            FİLE
            True
            0
            -1
            True
            1/10/2569
            2026-10-01
            """, "text", label="Output — L02.Syntax (first part)", file="captured on the build machine"),
             from_text("""
            L02.SyntaxVb - the same tour in Visual Basic

            [types]
            System.Int32 1200 2024 2
            VB: OverflowException without checked
            0.9999999999999999
            1.0
            11550.000 808.50000

            [nulls]
            no note (0)
            RENEWAL
            young driver 0.2
            0

            [patterns]
            age 23 loading 0.2
            Toyota 1200 cc

            [methods]
            5,544.00 8,933.71 0.40 claim-free 13,860.00

            [errors]
            declined: 3+ claims in 5 years
            dispose trace
            dispose audit
            """, "text", label="Output — L02.SyntaxVb", file="captured on the build machine"),
             "9.2 · What you should see — the C# and VB tours",
             "<b>Compare the line after <code>System.Int32 1200 2024 2</code> in each.</b> C# wrapped to "
             "<code>-2147483648</code>; VB threw. The double error, the decimal scale and the dispose order match "
             "across the two languages because both compile to the same runtime types — "
             "<code>System.Double</code>, <code>System.Decimal</code>, <code>IDisposable</code>; only the no-claim "
             "bonus and the declined quote come from the shared C# <code>L02.Rating</code> library. VB prints "
             "<code>0.2</code> where C# "
             "prints <code>0.20</code> because its literal <code>0.2D</code> has one decimal place. The rest of the "
             "C# tour is quoted as <i>Printed</i> under each panel in §4–§7, and it ends with "
             "<code>async dispose partner connection</code> because the <code>await using</code> declaration lives "
             "until <code>RunAsync</code> returns."),

        panel(from_text("""
            > dotnet test lesson-02-csharp-language-essentials/samples/L02.Rating.Tests
            # restore, build and xUnit progress lines left out
              L02.Rating.Tests test net10.0 succeeded (2.1s)
            Test summary: total: 31, failed: 0, succeeded: 31, skipped: 0, duration: 2.1s
            Build succeeded in 3.1s

            > cd lesson-02-csharp-language-essentials/samples/file-based
            > dotnet premium-check.cs
            total 8,933.71 THB (net 8,316.00)
            > dotnet premium-check.cs -- 3
            declined: 3+ claims in 5 years
            """, "text", label="Terminal — the test run and the file-based app", file="captured on the build machine"),
              "9.3 · The test run and the file-based app",
              "<b>" + str(CAPTURED_TESTS) + " test cases, all green, and the same total from a file with no "
              "project.</b> In an interactive terminal the .NET 10 SDK prints this compact <i>terminal logger</i> "
              "summary; redirected output falls back to the classic <code>Passed! - Failed: 0, Passed: 31</code> "
              "line. The file-based app calls the same <code>L02.Rating</code> library through "
              "<code>#:project</code>, so its " + f"{p['Total']:,.2f}" + " THB matches the worked example to the "
              "satang."),

        panel(from_sample(f"{L}/L02.Rating/PremiumCalculator.cs", "calculate"),
              "9.4 · The premium calculation — the code behind the worked example",
              "<b>The order of the statements is the tariff.</b> The rule names need no class prefix because the "
              "file opens with <code>using static L02.Rating.RatingRules;</code> (C# 6). Every money step goes "
              "through <code>Round</code> (3.2) before the next step reads it; the no-claim bonus applies to base "
              "plus loadings, and VAT to net plus stamp duty. <code>var (vehicle, driver, coverage, start) = "
              "request</code> deconstructs the record — records themselves are " + ref(3) + "."),

        {"type": "chart", "heading": f"9.5 · The worked example — how {p['Total']:,.2f} THB is built",
         "kind": "waterfall",
         "args": {"steps": [("Base", p["Base"]), ("Loadings", p["Loadings"]), ("NCB", -p["Discount"]),
                            ("Net", None), ("Stamp duty", p["StampDuty"]), ("VAT", p["Vat"]), ("Total", None)],
                  "ylabel": "THB", "width": 620, "height": 190},
         "caption": "illustrative tariff, not a real one · each figure read at build time from the Assert lines "
                    "of the passing test Calculate_matches_the_worked_example · measured",
         "note": "<b>The no-claim bonus outweighs the young-driver loading.</b> Base " + f"{p['Base']:,.2f}"
                 + ", +" + f"{p['Loadings']:,.2f}" + " for age 23, then −" + f"{p['Discount']:,.2f}"
                 + " for four claim-free years, because the bonus applies to base plus loadings: net "
                 + f"{p['Net']:,.2f}" + ". Stamp duty (" + f"{p['StampDuty']:,.2f}" + ") is barely visible; VAT ("
                 + f"{p['Vat']:,.2f}" + ") is charged on net plus duty, for a total of " + f"{p['Total']:,.2f}"
                 + ". The order of the rounding steps is part of the rule, and the test pins every one ("
                 + MEASURED + ")."},

        {"type": "chartrow", "charts": [
            {"heading": "9.6 · The same behaviour, C# vs VB lines", "kind": "grouped_bar",
             "args": {"categories": [c[0] for c in pairs],
                      "series": [("VB", vb_lines), ("C#", cs_lines)], "width": 390, "height": 190},
             "caption": "non-blank, non-comment lines in matching #region pairs · measured at build",
             "note": (f"<b>VB's biggest overhead is {top[1]}: {top[3]} lines against {top[2]}, because "
                      f"{VB_REASON[top[1]]}.</b> At the other end, {low[1]} takes {low[3]} VB lines against "
                      f"{low[2]} in C# — {VB_REASON[low[1]]}. " + MEASURED + "; a verbosity count, not a "
                      "quality score.")},
            {"heading": "9.7 · Test cases per tested member", "kind": "hbar",
             "args": {"data": sorted(tests.items(), key=lambda kv: -kv[1]), "width": 390, "labelw": 100,
                      "tone": "green"},
             "caption": "[Fact] = 1 · [InlineData] or TheoryData row = 1 · counted at build",
             "note": "<b>The banded rules carry most of the cases.</b> Each age-band edge is a case: a "
                     "<code>&lt;</code> typed as <code>&lt;=</code> changes a premium. " + MEASURED + "."}]},

        {"type": "callout", "variant": "warn", "heading": "⚠ Traps — they look right to a JVM, Kotlin or TypeScript engineer",
         "items": [
             "<b><code>!</code> is not <code>!!</code>.</b> It silences a warning and generates nothing; a null "
             "that arrives from JSON, reflection or an unannotated library flows on until something dereferences "
             "it far away.",
             "<b><code>var</code> is not <code>val</code>.</b> No local can hold a run-time value read-only: "
             "<code>const</code> takes only constants, <code>var</code> only infers the type.",
             "<b>Culture leaks into strings and dates.</b> <code>IndexOf(string)</code> matched across a soft "
             "hyphen, <code>th-TH</code> printed 2569, <code>de-DE</code> put a comma in a premium: use "
             "<code>StringComparison.Ordinal</code> for identifiers, the invariant culture for stored data.",
             "<b><code>Math.Round</code> rounds half to even by default.</b> <code>Math.Round(2.345m, 2)</code> "
             "is 2.34 (" + ROUND + "), asserted by a passing test (3.2). State the <code>MidpointRounding</code> "
             "of every premium calculation.",
             "<b>An enum is an int.</b> <code>(CoverageClass)7</code> compiles: every enum switch needs "
             "<code>_</code>, and input parsing needs <code>Enum.IsDefined</code>."]},

        {"type": "callout", "variant": "ok", "heading": "✔ Checkpoint — you are ready for lesson 03 when",
         "items": [
             f"<code>python 0-script/verify_samples.py --only 2</code> reports {n_proj}/{n_proj} sample projects "
             f"passed on your machine, with {n_tests} test cases green, and "
             f"<code>dotnet premium-check.cs</code> prints the {p['Total']:,.2f} THB total.",
             "You can explain every line of output in 9.2 — especially <code>0.9999999999999999</code>, "
             "<code>11550.000</code>, <code>FİLE</code> and <code>2569</code>.",
             "You can rewrite a Kotlin <code>when</code> as a C# switch expression with relational, property "
             "and tuple patterns, and say what its discard arm does.",
             "You can read the VB <code>Select Case</code>, <code>If()</code>, <code>Using</code> and "
             "<code>Catch … When</code> versions of the same rules."]},

        {"type": "callout", "variant": "summary", "heading": "🔍 Check yourself",
         "items": [
             "Why does declaring a property as non-nullable <code>string</code> not stop "
             "<code>System.Text.Json</code> from storing null in it, and what .NET 9 option changes that?",
             "With <code>int big = int.MaxValue</code>, what does <code>big + 1</code> evaluate to in C# and in "
             "Visual Basic with default settings — and why does <code>int.MaxValue + 1</code> written directly "
             "not compile?",
             "Which of <code>==</code>, <code>Contains(string)</code> and <code>IndexOf(string)</code> is "
             "culture-sensitive by default?",
             "A switch expression over <code>CoverageClass</code> handles all four named values. Why does the "
             "compiler still want a <code>_</code> arm?",
             "In <code>catch (Exception e) when (Log(e))</code>, does <code>Log</code> run before or after the "
             "<code>finally</code> blocks of the method that threw?",
             "A library changes an optional default from <code>0.40m</code> to <code>0.30m</code>. What does a "
             "caller that omits it pass until rebuilt, and why?",
             "Which settings does a file-based app inside this repository inherit, and from which file?"]},

        {"type": "footer",
         "html": ("<b>Lesson 02 in one line:</b> C# spells your Kotlin, Java and TypeScript habits with less "
                  "ceremony — but <code>string?</code> is only a warning, <code>!</code> never throws, "
                  "<code>decimal</code> is the money type, culture and banker's rounding are defaults you must "
                  "override, and an enum switch always needs <code>_</code>. "
                  "<br/><b>Next:</b> " + ref(3) + " — classes, structs and records, and the generics that "
                  "type erasure never gave you.")},
    ]
