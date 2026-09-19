# -*- coding: utf-8 -*-
"""Lesson 03 — Types, OOP & Generics. Built to 1-analysis/spec_lesson-pdfs/_standard.md; shape follows lesson_01.py.
Unit spec: 1-analysis/spec_lesson-pdfs/lesson-03-types-oop-generics.md"""
import re

from lesson_kit import (DIFFERENT, ESTIMATE, MEASURED, RENAMED, REPO, SAME, TRAP, VERIFIED,
                        T_CS, T_RUNTIME, esc, from_sample, from_text,
                        legend, link, loc, mapping, style_block)
from lesson_kit import code as _kit_code, compare as _kit_compare
from lessons.roster import meta, ref

META = meta(
    3,
    subtitle="Classes, structs, records and enums · inheritance and interfaces · reified generics · "
             "C# 14 extension members and equality — for a Java/Kotlin architect",
    objectives=[
        "Choose class, struct, record, record struct or enum for each MotorQuote concept and state the memory "
        "and equality consequences",
        "Write properties, required and init members, primary constructors and C# 14 field-backed setters — "
        "and spot where Kotlin constructor habits mislead",
        "Predict virtual, non-virtual and hidden (new) calls, and use default and static abstract interface members",
        "Use reified generics, constraints, in/out variance and generic math where Java needs erasure workarounds",
        "Add C# 14 extension members and implement equality that holds up in a hash set",
        "Build a generic multi-format report framework in C# and extend it from Visual Basic",
    ],
    maps_from="Java and Kotlin object models (data classes, value classes, open, final and sealed hierarchies, "
              "interfaces with default methods), SOLID with DI-friendly constructors, Java's type erasure and "
              "wildcards, Kotlin's declaration-site variance and extension functions — and the multi-format "
              "(PDF / Excel / JSON) report framework you have designed before.",
)

L = "lesson-03-types-oop-generics/samples"
DOM = f"{L}/L03.Domain"
REP = f"{L}/L03.Reports"
TOUR = f"{L}/L03.TypesTour/Program.cs"
VB = f"{L}/L03.VbInterop/Program.vb"
PROJECTS = [("L03.Domain", "Domain"), ("L03.Reports", "Reports"), ("L03.TypesTour", "TypesTour"),
            ("L03.VbInterop", "VbInterop (VB)"), ("L03.Domain.Tests", "Domain.Tests"),
            ("L03.Reports.Tests", "Reports.Tests")]

CS14 = link("What's new in C# 14", "https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14")
CS15 = link("What's new in C# 15 (preview)", "https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-15")
HISTORY = link("C# version history", "https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-version-history")
EXT = link("extension member declarations",
           "https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/extension")
FIELD = link("the field keyword", "https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/field")
PRIMARY = link("primary constructors",
               "https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/tutorials/primary-constructors")
REQUIRED = link("required members",
                "https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/required")
RECORD = link("records", "https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/record")
STRUCT = link("structure types",
              "https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/struct")
STRUCTGUIDE = link("choosing between class and struct",
                   "https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/choosing-between-class-and-struct")
BOXING = link("boxing and unboxing",
              "https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/types/boxing-and-unboxing")
NEWOVERRIDE = link("versioning with override and new",
                   "https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/classes-and-structs/"
                   "versioning-with-the-override-and-new-keywords")
INTERFACE = link("interface members",
                 "https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/interface")
VARIANCE = link("covariance and contravariance in generics",
                "https://learn.microsoft.com/en-us/dotnet/standard/generics/covariance-and-contravariance")
GMATH = link("generic math", "https://learn.microsoft.com/en-us/dotnet/standard/generics/math")
EQUALITY = link("equality comparisons",
                "https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/expressions/equality")
VBNEW = link("What's new for Visual Basic", "https://learn.microsoft.com/en-us/dotnet/visual-basic/whats-new/")
VBSTRAT = link("Visual Basic language strategy",
               "https://learn.microsoft.com/en-us/dotnet/visual-basic/getting-started/strategy")

# ── captured from real runs on the build machine (x64, .NET 10.0.12) — see §8 ───────────────────────────
TOUR_OUT = """
    L03.TypesTour on .NET 10.0.12
    copy       copy.Count=1 list[0].Count=0
    default    default(Money).Currency is null: True
    size       Money=24 bytes, QuoteId=4, CoverageClass=4
    alloc      Money[]=24,024 MoneyClass[]=48,024 object[] of Money=48,024 bytes
    generated  class=3 struct=3 record=16 record struct=13 methods
    dispatch   asBase.Factor / asBase.Describe / asDerived.Describe:
    1.20
    young driver x1.20
    young driver (hidden copy)
    dim        IRateTable.BasePremium = 11,250.00 THB
    reified    QuoteId Q- Q-000000 | PolicyNumber P- P-00000000 | parsed Q-000042, Q-000043
    generics   List<int>=4,056 List<object>=32,056 ArrayList=32,056 bytes for 1,000 ints
    statics    Counter<QuoteId>.Hits=2 Counter<PolicyNumber>.Hits=1
    math       Sum<decimal>=6.50 Sum<Money>=1,500.00 THB
    variance   card renderer as IReportRenderer<QuoteReport>: # Motor quotes - 2026-10-01 (QuoteReport)
    extension  Class2Plus.Code=2+ Class3.CoversOwnDamage=False FromCode("3+")=Class3Plus
    enum       (CoverageClass)42 is defined: False
    equality   five==alsoFive / Equals / vinA==vinB / set.Contains / broken.Contains:
    False
    True
    True
    True
    False
    premium    net 11,475.00 THB, stamp duty 45.90 THB, VAT 806.46 THB, total 12,327.36 THB
    status     Q-000042 Accepted -> policy P-00000007; Expire() now throws (Accepted -> Expired)
    """
VB_OUT = """
    L03.VbInterop - Visual Basic using the lesson-03 C# types
    records    equal? True
    copy       equal? False
    operators  1,500.00 THB, same? True
    required   Q-000007 total 12,327.36 THB
    extension  get_Code(Class2Plus) = 2+
    dispatch   1.20 | young driver x1.20 | young driver (hidden copy)
    generics   Q-000042, Q-000043
    same CSV from C# and VB? True
    # Motor quotes - 2026-10-01
    Q-000042  Toyota Yaris   class 1        12,327.36 THB
    Q-000043  Isuzu D-Max    class 2+       15,319.23 THB
    2 quotes, total 27,646.59 THB
    """
# the date the C# 15 preview and Visual Basic "what's new" pages were last read — not the build date
CHECKED = "2026-09-20"

_VB_DISPATCH = next(ln.split(None, 1)[1] for ln in VB_OUT.strip().splitlines()
                    if ln.strip().startswith("dispatch"))
_VB_GENERICS = next(ln.split(None, 1)[1] for ln in VB_OUT.strip().splitlines()
                    if ln.strip().startswith("generics"))
_TOUR = dict(ln.strip().split(None, 1) for ln in TOUR_OUT.strip().splitlines()[1:] if "  " in ln.strip())


def _nums(key):
    """Integers after each `name=` in one line of the captured tour output, e.g. `Money[]=24,024`."""
    return [(k, int(v.replace(",", ""))) for k, v in re.findall(r"([\w<>\[\] ]+?)=([\d,]+)", _TOUR[key])]


ALLOC = [("Money[]", _nums("alloc")[0][1]), ("MoneyClass[]", _nums("alloc")[1][1]),
         ("boxed Money", _nums("alloc")[2][1])]
GENERATED = [(k.strip(), v) for k, v in _nums("generated")]
GENERIC_ALLOC = [("List<int>", _nums("generics")[0][1]), ("List<object>", _nums("generics")[1][1]),
                 ("ArrayList (.NET 1.x)", _nums("generics")[2][1])]
SIZES = {k.strip(" ,"): v for k, v in _nums("size")}

# Pygments' vbnet lexer has no token for VB 14 interpolated strings, so every `$"` prints inside a red
# error box. The code is valid (the samples compile); drop the box, keep the text. (same fix as lesson 01)
_ERROR_SPAN = re.compile(r'<span style="border: 1px solid #F00">(.*?)</span>', re.S)


_CODE_HEAD = re.compile(r'^<div class="codeblk">(<div class="codeh">.*?</div>)', re.S)


def _listed(block, heading):
    """Put a numbered code panel in the Contents at level 2 and clean VB highlighting (as lessons 01 and 06).

    brief_pdf makes a listed block's first container unbreakable unless that container opens with a
    `<div class="ct">` heading line (as a story does), so the heading is wrapped in one: a long panel can
    then split across pages as _standard.md §5 allows, and the Contents marker stays on the heading line.
    Short panels stay whole through lesson_kit's own `.keep` class. (kit request: do this in lesson_kit.)"""
    if heading:
        block.update(heading=heading, toc=2)
        block["html"] = _CODE_HEAD.sub(
            r'<div class="codeblk"><div class="ct" style="break-after:avoid;page-break-after:avoid">\1</div>',
            block["html"], count=1)
    if "vb" in block.get("_langs", []):
        block["html"] = _ERROR_SPAN.sub(r"\1", block["html"])
    return block


def code(s, *, heading=None, note=None, keep=None):
    return _listed(_kit_code(s, heading=heading, note=note, keep=keep), heading)


def compare(left, right, *, heading=None, note=None, keep=None):
    return _listed(_kit_compare(left, right, heading=heading, note=note, keep=keep), heading)


def nw(identifier_html):
    """An identifier that must not wrap inside itself, e.g. <code>IReportRenderer&lt;in TReport&gt;</code>."""
    return f'<code style="white-space:nowrap">{identifier_html}</code>'


def figure_heading(text):
    """A numbered heading for a block type that prints none of its own (threecol), kept with that block."""
    return {"type": "html", "html": f'<div class="figh"><h2>{esc(text)}</h2></div>', "heading": text,
            "toc": 2, "_keep_with_next": True}


def _sources(project):
    """Every .cs / .vb file of one sample project (repo-relative)."""
    root = REPO / L / project
    files = list(root.rglob("*.cs")) + list(root.rglob("*.vb"))
    return sorted(p.relative_to(REPO).as_posix() for p in files if not {"bin", "obj"} & set(p.parts))


def _test_cases_by_class():
    """[Fact] methods + [InlineData] rows per public test class — a MEASURED figure."""
    counts = {}
    for project in ("L03.Domain.Tests", "L03.Reports.Tests"):
        for rp in _sources(project):
            text = (REPO / rp).read_text(encoding="utf-8-sig")
            parts = re.split(r"^public class (\w+)", text, flags=re.M)
            for name, body in zip(parts[1::2], parts[2::2]):
                n = (len(re.findall(r"^\s*\[Fact\]", body, re.M))
                     + len(re.findall(r"^\s*\[InlineData\(", body, re.M)))
                counts[name] = counts.get(name, 0) + n
    return counts


# Table 7.6 — every error id here must appear in VbCompilerTests.cs (checked in _vb_limits()), so the table cannot
# claim a compiler result the tests do not assert.
_VB_LIMITS = [
    ("Extension property · C# 14", "<code>CoverageClass.Class2Plus.Code</code>", "BC30456", "not a member",
     "<code>CoverageClassExtensions.get_Code(…)</code>"),
    ("Static extension member · C# 14", "<code>CoverageClass.FromCode(\"3+\")</code>", "BC30456", "not a member",
     "<code>CoverageClassExtensions.FromCode(\"3+\")</code>"),
    ("<code>required</code> member · C# 11", "<code>New Quote With {…}</code> without <code>.Premium</code>",
     "BC37321", "must be set", "Set every required member in <code>With { }</code> — VB enforces the contract"),
    ("<code>init</code> accessor · C# 9", "<code>Q.ValidUntil = R.StartDate</code>", "BC37311", "init-only",
     "Assign it inside <code>With { }</code>"),
    ("Default interface member · C# 8", "<code>New StandardRateTable().BasePremium(R)</code>", "BC30456",
     "not a member", "Call it through an <code>IRateTable</code> reference"),
    ("Default interface member · C# 8", "A VB class implementing <code>IRateTable</code> with only "
     "<code>BaseRate</code>", "BC30149", "must implement", "Write <code>BasePremium</code> in the VB class"),
    ("<code>with</code> expression · C# 9", "<code>R With {.Coverage = …}</code>", "BC30205", "syntax error",
     "Call the record's constructor"),
    ("Static abstract member · C# 11", "A VB <code>Structure</code> implementing <code>IIdentifier(Of T)</code>",
     "BC37315", "cannot implement", "Declare such types in C#"),
    ("Static abstract member · C# 11", "<code>T.Parse(text)</code> inside a VB generic method", "BC32098",
     "type parameter as qualifier", "Call a C# generic helper: <code>Ids.ParseAll(Of T)</code>"),
]


def _vb_limits():
    """Table 7.6 rows, after proving every error id is asserted by the compiler tests."""
    tests = (REPO / L / "L03.Reports.Tests" / "VbCompilerTests.cs").read_text(encoding="utf-8-sig")
    missing = sorted({row[2] for row in _VB_LIMITS} - set(re.findall(r'"(BC\d{5})"', tests)))
    if missing:
        raise ValueError(f"table 7.6 cites {missing}, which VbCompilerTests.cs does not assert")
    return [[feature, vb, f"<code>{err}</code> {what}", instead]
            for feature, vb, err, what, instead in _VB_LIMITS]


def _roslyn_version():
    """Microsoft.CodeAnalysis.VisualBasic version from the test project file — the compiler the tests run."""
    proj = (REPO / L / "L03.Reports.Tests" / "L03.Reports.Tests.csproj").read_text(encoding="utf-8-sig")
    return re.search(r'Include="Microsoft\.CodeAnalysis\.VisualBasic" Version="([^"]+)"', proj).group(1)


def blocks():
    tests = _test_cases_by_class()
    total_tests = sum(tests.values())
    project_loc = [(label, loc(*_sources(name))) for name, label in PROJECTS]
    loc_all = sum(n for _, n in project_loc)
    loc_by = dict((name, n) for (name, _), (_, n) in zip(PROJECTS, project_loc))
    loc_libs = loc_by["L03.Domain"] + loc_by["L03.Reports"]
    loc_tests = loc_by["L03.Domain.Tests"] + loc_by["L03.Reports.Tests"]
    n_proj = len(list((REPO / L).glob("*/*.*proj")))
    ranked_tests = sorted(tests.items(), key=lambda kv: (-kv[1], kv[0]))
    rest = ranked_tests[5:]
    shown_tests = ranked_tests[:5] + ([(f"{len(rest)} other classes", sum(n for _, n in rest))] if rest else [])
    VB_LIMITS = _vb_limits()
    ROSLYN = _roslyn_version()

    return [
        style_block(),
        {"type": "toc", "heading": "▤ Contents", "depth": 2,
         "note": "Page numbers are resolved from the rendered PDF. Code panels are cut from the compiled samples."},
        # the Contents fills page 1: start §1 on page 2 instead of stranding its heading at the foot
        {"type": "html", "html": '<div style="height:0;break-before:page;page-break-before:always"></div>'},
        # a table or figure heading must not print alone at a page foot with its body on the next page, and a
        # callout heading must stay with its first item (kit request)
        # and the renderer's `word-break:break-all` on links splits link text mid-word (kit request)
        {"type": "html", "html": "<style>h2 { break-after:avoid; page-break-after:avoid; } "
                                 ".callout .ct { break-after:avoid; page-break-after:avoid; } "
                                 ".callout li:first-child { break-before:avoid; page-break-before:avoid; } "
                                 "body a.lnk, body a { word-break:normal; overflow-wrap:break-word; } "
                                 ".toc .tl1 { margin-top:2px; line-height:1.3; } "
                                 ".toc .tl2 { line-height:1.3; }</style>"},

        # ═══════════════════════════ 1 · WHY ═══════════════════════════
        {"type": "story", "heading": "1 · Why the type system is where Java instincts break",
         "html": (
             "<p><b>C#'s classes, interfaces and generics look like Java's, and three decisions underneath them are "
             "different enough to ship bugs.</b> Every C# type is a reference type or a value type, fixed at its "
             "declaration. Methods are non-virtual unless the base class says <code>virtual</code>. Generics are real "
             "types at run time. After " + ref(2) + " you can read most C#; these three are why code that reads "
             "right can still behave wrong.</p>"
             "<p><b>For an architect, the type system is the domain model.</b> In a Kotlin service you chose between "
             "a <code>data class</code>, a <code>value class</code>, an <code>open</code> class and a "
             "<code>sealed</code> hierarchy. C# offers <code>class</code>, <code>struct</code>, <code>record</code>, "
             "<code>record struct</code> and <code>enum</code>, and the choice decides allocation, copying and "
             "equality. This lesson makes that choice for every MotorQuote concept — <code>Money</code>, "
             "<code>QuoteId</code>, <code>Vehicle</code>, <code>Driver</code>, <code>Quote</code> — and measures "
             "what each choice costs.</p>"
             "<p><b>You already know OOP, SOLID and dependency injection, so the words go to the .NET shape.</b> The "
             "lesson ends by rebuilding a pattern you have designed before — a multi-format report framework for "
             "PDF, Excel and JSON output — as a generic strategy over a template-method base class, then extends it "
             "from Visual Basic, the way a modernisation estate mixes the two languages.</p>"
             "<p><b>Scope.</b> Nullability, pattern matching and <code>decimal</code> belong to " + ref(2) + "; "
             "collections and LINQ to " + ref(4) + "; DI lifetimes and container registration to " + ref(8) + ". "
             "Every feature here is C# 14, which shipped with .NET 10 in November 2025 " + VERIFIED + " ("
             + HISTORY + "); C# 15 preview features are labelled as preview.</p>")},

        {"type": "kpi", "heading": "1.1 · The numbers to leave this lesson with",
         "items": [
             {"label": "C# 14 · ships with .NET 10", "value": "Nov 2025", "tone": "teal",
              "sub": "verified · C# version history (§1)"},
             {"label": "Methods for two properties", "value": f"{GENERATED[2][1]} vs {GENERATED[0][1]}",
              "tone": "violet", "sub": "record vs class · reflection · measured"},
             {"label": "Money in memory", "value": f"{SIZES['Money']} bytes", "tone": "indigo",
              "sub": "Unsafe.SizeOf on x64 · measured"},
             {"label": "Lesson 03 tests", "value": f"{total_tests} cases", "tone": "navy",
              "sub": "xUnit facts + inline data · measured at build"},
             {"label": "Lesson 03 samples", "value": f"{loc_all:,} lines", "tone": "slate",
              "sub": f"C# + VB · {n_proj} projects · measured at build"}]},

        legend(T_CS, T_RUNTIME),

        {"type": "callout", "variant": "info", "heading": "ℹ Before you start",
         "items": [
             "<b>Read first:</b> " + ref(1) + " for value types and the runtime, and " + ref(2) + " for syntax, "
             "nullability, pattern matching and <code>decimal</code>.",
             "<b>You will build six projects:</b> <code>L03.Domain</code> (the MotorQuote types), "
             "<code>L03.Reports</code> (a generic report framework), two xUnit test projects, "
             "<code>L03.TypesTour</code> (a console that prints every measurement quoted here) and "
             "<code>L03.VbInterop</code> (Visual Basic using the C# types and extending the framework).",
             "<b>Premiums are illustrative, not a real tariff.</b> Base rates, loadings, stamp duty (0.4% of net) and "
             "VAT (7% of net plus duty) exist so the types have something real-shaped to compute.",
             "Facts that change with releases are marked " + VERIFIED + " and link to Microsoft Learn; judgements "
             "are marked " + ESTIMATE + "; figures computed from the samples are marked " + MEASURED + ". Byte "
             "counts come from one run of <code>L03.TypesTour</code> in a 64-bit process on .NET 10.0.12 — object "
             "sizes depend on the process architecture; the ratios are the point."]},

        # ═══════════════════════════ 2 · KINDS OF TYPE ═══════════════════════════
        {"type": "story", "heading": "2 · Five kinds of type — and where their bytes live",
         "html": (
             "<p><b>C# makes you choose reference or value semantics when you declare a type, not when you use "
             "it.</b> <code>class</code> and <code>record</code> are reference types: allocated on the heap, shared "
             "by reference, <code>null</code> by default. <code>struct</code>, <code>record struct</code> and "
             "<code>enum</code> are value types: stored inline in their variable, field or array slot, copied on "
             "every assignment, and all-zero by default. Java gives you that split only for its primitives, and "
             "Kotlin's <code>value class</code> wraps exactly one property. In C# any type you write can be a value "
             "type (" + STRUCT + ").</p>"
             f"<p><b>The difference is measurable.</b> A thousand <code>Money</code> values in an array are one "
             f"allocation of {ALLOC[0][1]:,} bytes. The same thousand amounts as class instances cost "
             f"{ALLOC[1][1]:,} bytes and 1,000 heap objects for the garbage collector to trace. Put the structs into "
             f"an <code>object[]</code> and you are back at {ALLOC[2][1]:,}: boxing copies each value into its own "
             "heap object (" + BOXING + ").</p>"
             "<p><b>Records are the compiler writing the members you used to generate.</b> A two-property "
             f"<code>record</code> compiles to {GENERATED[2][1]} methods — value <code>Equals</code>, "
             "<code>GetHashCode</code>, <code>==</code>, <code>ToString</code>, <code>Deconstruct</code> and the "
             f"clone behind <code>with</code> — against {GENERATED[0][1]} for the equivalent class "
             "(" + RECORD + "). It is Kotlin's "
             "<code>data class</code>, offered as a reference type and as a value type.</p>"
             "<p><b>Microsoft's struct guideline is strict, and <code>Money</code> breaks one rule on purpose.</b> "
             "The guideline says to avoid a struct unless the type is one logical value, under 16 bytes, immutable "
             "and rarely boxed (" + STRUCTGUIDE + "). <code>Money</code> is 24 bytes — a 16-byte <code>decimal</code> "
             "plus an 8-byte string reference — but it is immutable, compared constantly and stored in arrays of "
             "premium lines. That trade is a judgement (" + ESTIMATE + "): measure before you copy it.</p>")},

        {"type": "cards",
         "band": {"title": "2.1 · The five kinds, side by side", "note": "type-system view", "tone": "violet"},
         "cards": [
             {"num": 1, "title": "class — a reference type with identity", "tags": [T_CS], "pills": [DIFFERENT],
              "what": "Allocated on the heap, compared by reference, null by default.",
              "lines": [("JVM", "Any Java or Kotlin class — but open for inheritance until you write "
                                "<code>sealed</code>"),
                        ("Equality", "Reference, unless the type overloads <code>==</code> and <code>Equals</code>"),
                        ("Use for", "Entities with identity and a lifecycle (<code>Quote</code>) and services "
                                    "(<code>PremiumCalculator</code>)"),
                        ("Trap", "Kotlin classes are final by default; C# classes are not")]},
             {"num": 2, "title": "struct — a value type", "tags": [T_RUNTIME], "pills": [DIFFERENT],
              "what": "Stored inline, copied on every assignment, never null.",
              "lines": [("JVM", "Nothing user-defined in mainstream Java; the nearest thing is a primitive"),
                        ("Equality", "<code>Equals</code> compares fields through reflection; no <code>==</code> "
                                     "until you declare one"),
                        ("Use for", "Small immutable values on hot paths; interop buffers"),
                        ("Trap", "A mutable struct read from a <code>List&lt;T&gt;</code> is a copy — changes to it "
                                 "vanish (panel 2.4)")]}]},

        {"type": "cards", "toc": False,
         "band": {"title": "2.1 · The five kinds (continued)", "note": "type-system view", "tone": "violet"},
         "cards": [
             {"num": 3, "title": "record — a class whose data members the compiler writes", "tags": [T_CS],
              "pills": [SAME],
              "what": "Value equality, ToString, Deconstruct and non-destructive copy with <code>with</code>.",
              "lines": [("JVM", "Kotlin <code>data class</code> · Java <code>record</code> (C# records can inherit)"),
                        ("Generated", f"{GENERATED[2][1]} methods for two properties (chart 2.6)"),
                        ("Use for", "Requests, messages and report rows: data without identity"),
                        ("Trap", "A <code>List&lt;T&gt;</code> property compares by reference, not by contents")]},
             {"num": 4, "title": "record struct — a value type with record members", "tags": [T_CS],
              "pills": [DIFFERENT],
              "what": "<code>readonly record struct</code> is the immutable form, and the usual choice.",
              "lines": [("JVM", "Kotlin <code>value class</code>, without the one-property limit"),
                        ("Size", f"<code>Money</code> = {SIZES['Money']} bytes; <code>QuoteId</code> = {SIZES['QuoteId']} bytes "
                                 "(measured)"),
                        ("Use for", "Value objects: <code>Money</code>, <code>QuoteId</code>, "
                                    "<code>PolicyNumber</code>"),
                        ("Trap", "<code>default(Money)</code> runs no constructor: its <code>Currency</code> is null")]},
             {"num": 5, "title": "enum — named integers", "tags": [T_RUNTIME], "pills": [TRAP],
              "what": "Named constants over an integral type, <code>int</code> unless you say otherwise.",
              "lines": [("JVM", "Java and Kotlin enums are classes with fields and methods; C# enums are not"),
                        ("Size", f"<code>CoverageClass</code> = {SIZES['CoverageClass']} bytes (measured)"),
                        ("Behaviour", "Add members with a C# 14 extension block (§6)"),
                        ("Trap", "Any <code>int</code> converts: <code>(CoverageClass)42</code> is a legal value")]}]},

        {"type": "mermaid", "inline": True,
         "heading": "2.2 · Where the bytes live — three arrays of 1,000 amounts",
         "caption": "slate = variable · teal = values inline · indigo = heap objects · rose = boxes copied out of "
                    "a struct · bytes measured (chart 2.5)",
         "code": ('%%{init: {"themeVariables": {"fontSize": "14px"}, '
                  '"flowchart": {"nodeSpacing": 12, "rankSpacing": 44}}}%%\n'
                  "flowchart LR\n"
                  '  V1["local · Money[]"]:::loc\n'
                  '  V2["local · MoneyClass[]"]:::loc\n'
                  '  V3["local · object[]"]:::loc\n'
                  f'  V1 --> A1["Money[1000]: ONE object<br/>1,000 values inline<br/>{ALLOC[0][1]:,} bytes"]:::vty\n'
                  '  V2 --> A2["MoneyClass[1000]<br/>1,000 references"]:::obj\n'
                  f'  A2 --> O2["1,000 MoneyClass objects<br/>{ALLOC[1][1]:,} bytes with the array"]:::obj\n'
                  '  V3 --> A3["object[1000]<br/>1,000 references"]:::obj\n'
                  f'  A3 --> O3["1,000 boxes, each a copy<br/>{ALLOC[2][1]:,} bytes with the array"]:::bxd\n'
                  "  classDef vty fill:#ccfbf1,color:#1f2937,stroke:#0d9488;\n"
                  "  classDef loc fill:#e2e8f0,color:#1f2937,stroke:#475569;\n"
                  "  classDef obj fill:#c7d2fe,color:#1f2937,stroke:#6366f1;\n"
                  "  classDef bxd fill:#fce7f3,color:#1f2937,stroke:#be185d;\n")},

        code(from_sample(f"{DOM}/Money.cs", "money"),
             heading="2.3 · Money — a value object as a readonly record struct",
             note="<b>Read the declaration line first.</b> <code>readonly</code> makes every field immutable, "
                  "<code>record</code> generates value equality, <code>==</code>, <code>ToString</code> and "
                  "<code>Deconstruct</code> (<code>with</code> works on any struct), <code>struct</code> stores it "
                  "inline. Implementing <code>IAdditionOperators&lt;Money, Money, Money&gt;</code> declares "
                  "<code>+</code> as a static interface member — that is what lets the generic "
                  "<code>Totals.Sum</code> in §5 add money. Mixed currencies throw: a THB premium plus a USD fee "
                  "is a bug."),

        code(from_sample(TOUR, "copy-trap"),
             heading="2.4 · Two copies you did not ask for — a struct read from a list, and default(Money)",
             note="<b>Value semantics bite where Java has no value types.</b> <code>Tally</code> is a small mutable "
                  "struct. The list indexer returns a copy, so <code>copy.Add()</code> changes only the copy: the "
                  f"tour prints <code>{esc(_TOUR['copy'])}</code>. An array element is a variable, so the same call "
                  "on a <code>Tally[]</code> changes it in place (<code>CopySemanticsTests</code> asserts both). "
                  "<code>default(Money)</code> runs no constructor, so the non-nullable <code>Currency</code> is "
                  f"null (<code>{esc(_TOUR['default'])}</code>). Both are reasons to keep structs "
                  "<code>readonly</code>."),

        {"type": "chartrow", "charts": [
            {"heading": "2.5 · Bytes allocated for 1,000 amounts", "kind": "bar",
             "args": {"data": ALLOC, "ylabel": "bytes", "tone": "teal", "width": 390, "height": 220},
             "caption": "GC.GetAllocatedBytesForCurrentThread around each loop · L03.TypesTour · measured",
             "note": "<b>Value types halve the bytes and remove 1,000 objects.</b> The class array holds 1,000 "
                     "references to 1,000 separate objects; boxing turns the struct array back into exactly that "
                     "shape."},
            {"heading": "2.6 · Methods the compiler emits for two properties", "kind": "bar",
             "args": {"data": GENERATED, "ylabel": "methods + constructors", "tone": "violet", "width": 390,
                      "height": 220},
             "caption": "declared methods and constructors found by reflection · L03.TypesTour · measured",
             "note": f"<b>A record is a class plus {GENERATED[2][1] - GENERATED[0][1]} generated members.</b> "
                     "The record class needs three that a "
                     "record struct does not: a copy constructor, the compiler-named clone method behind "
                     "<code>with</code> (virtual unless the record is sealed) and <code>EqualityContract</code>, "
                     "which makes equality compare the run-time type."}]},

        {"type": "mermaid", "inline": True,
         "heading": "2.7 · Which kind of type? — the MotorQuote decisions",
         "caption": "amber = question · indigo = reference type · teal = value type · each answer names the "
                    "MotorQuote types that took that path",
         "code": ('%%{init: {"flowchart": {"nodeSpacing": 16, "rankSpacing": 34}}}%%\n'
                  "flowchart LR\n"
                  '  Q0{{"A fixed set of<br/>named codes?"}}:::q\n'
                  '  Q0 -- "yes" --> EN["enum + extension block<br/>CoverageClass · QuoteStatus"]:::vty\n'
                  '  Q0 -- "no" --> Q1{{"Identity, lifecycle<br/>or behaviour?"}}:::q\n'
                  '  Q1 -- "yes" --> CL["sealed class<br/>Quote · PremiumCalculator"]:::refv\n'
                  '  Q1 -- "no: data" --> Q2{{"One small immutable<br/>value, rarely boxed?"}}:::q\n'
                  '  Q2 -- "yes" --> RS["readonly record struct<br/>Money · QuoteId · PolicyNumber"]:::vty\n'
                  '  Q2 -- "no" --> RC["sealed record<br/>Vehicle · Driver · QuoteRequest"]:::refv\n'
                  "  classDef q fill:#fde68a,color:#1f2937,stroke:#d97706;\n"
                  "  classDef refv fill:#c7d2fe,color:#1f2937,stroke:#6366f1;\n"
                  "  classDef vty fill:#ccfbf1,color:#1f2937,stroke:#0d9488;\n")},

        mapping("2.8 · Concept map — Java, Kotlin and TypeScript types → C#", [
            ("Java class · Kotlin <code>open class</code>", "<code>class</code>", "different",
             "Open for inheritance by default (Kotlin: final); mark leaf classes <code>sealed</code>"),
            ("Java / Kotlin <code>final</code> class", "<code>sealed</code>", "renamed",
             "Not Kotlin's <code>sealed</code>: nothing about exhaustiveness"),
            ("Kotlin <code>sealed class</code> + exhaustive <code>when</code>",
             "no C# 14 equivalent; <code>closed</code> classes are in the C# 15 preview", "trap",
             "A C# 14 switch over a class hierarchy needs a default arm"),
            ("Kotlin <code>data class</code> · Java <code>record</code>", "<code>record</code>", "same",
             "<code>with</code> = <code>copy()</code>; equality also compares the run-time type"),
            ("Kotlin <code>value class</code> · Java primitives", "<code>readonly record struct</code>", "different",
             "Many fields allowed; copied on assignment; <code>default</code> skips the constructor"),
            ("Java enum · Kotlin <code>enum class</code>", "<code>enum</code> (named integers)", "trap",
             "No fields or methods; <code>(CoverageClass)42</code> is legal"),
            ("getters and setters · Lombok builders", "properties · <code>init</code> · <code>required</code>",
             "renamed", "Object initializers replace most builders"),
            ("Kotlin <code>class X(val a: A)</code>", "primary constructor <code>class X(A a)</code>", "trap",
             "Parameters, not properties — only records generate properties"),
            ("Kotlin <code>field</code> in a custom setter", "C# 14 <code>field</code> keyword", "same",
             "Guard a setter without declaring a backing field"),
            ("Java methods (virtual by default)", "non-virtual unless <code>virtual</code>", "trap",
             "A same-named method without <code>override</code> hides the base one (CS0114 · CS0108)"),
            ("Kotlin <code>open fun</code> · <code>override</code>", "<code>virtual</code> · <code>override</code>",
             "trap", "Leaving out <code>override</code> still compiles: the method hides the base one with warning "
             "CS0114, where Kotlin rejects it. Warnings as errors gives you Kotlin's rule"),
            ("Java interface <code>default</code> method", "default interface method", "different",
             "Callable only through the interface type, not the class"),
            ("Kotlin <code>companion object</code> · Java <code>static</code>",
             "<code>static</code> · <code>static abstract</code> in interfaces", "different",
             "Generic code can call <code>T.Parse</code> on a type parameter"),
            ("Type erasure · <code>Class&lt;T&gt;</code> tokens", "reified generics", "different",
             "<code>typeof(T)</code>, <code>default(T)</code>, statics per closed type, no boxing in "
             "<code>List&lt;int&gt;</code>"),
            ("Java <code>? extends</code> · <code>? super</code>",
             "<code>out</code> · <code>in</code> on interfaces and delegates", "different",
             "Declaration-site only; <code>List&lt;T&gt;</code> stays invariant"),
            ("Kotlin <code>out</code> · <code>in</code>", "<code>out</code> · <code>in</code>", "same",
             "Value-type arguments are always invariant"),
            ("Kotlin extension functions and properties", "C# 14 <code>extension</code> blocks", "same",
             "Declared in a static class; no state; VB cannot use the property syntax"),
            ("Kotlin <code>==</code> (calls <code>equals</code>)", "<code>==</code>: reference unless overloaded",
             "trap", "Records and <code>string</code> overload it; plain classes and boxes do not"),
            ("TypeScript structural typing", "nominal typing", "different",
             "Matching shape is not enough — the type must declare the interface"),
        ]),

        # ═══════════════════════════ 3 · MEMBERS ═══════════════════════════
        {"type": "story", "heading": "3 · Members — properties, construction and the C# 14 field keyword",
         "html": (
             "<p><b>Properties are the unit of state in C#, and the compiler writes most of them for you.</b> "
             "<code>{ get; set; }</code> is a Kotlin <code>var</code>; <code>{ get; init; }</code> (C# 9) can be "
             "set during construction and never again; <code>required</code> (C# 11) makes a missing member a "
             "compile error (" + REQUIRED + "); and the C# 14 <code>field</code> keyword lets a setter validate "
             "without a hand-declared backing field (" + FIELD + "). Hand-written getters and setters are a Java "
             "habit to drop.</p>"
             "<p><b>Construction is an object initializer checked by the compiler, not a builder.</b> "
             "<code>new Quote { Id = …, Request = …, Premium = … }</code> fails to compile if any "
             "<code>required</code> member is left out, so the Lombok <code>@Builder</code> and the Kotlin "
             "named-argument constructor both collapse into one checked expression. Copies of records use "
             "<code>with</code>.</p>"
             "<p><b>A primary constructor on a class is a parameter list, not a property list.</b> Kotlin's "
             "<code>class PremiumCalculator(private val rates: RateTable)</code> declares a property. C#'s "
             "<code>class PremiumCalculator(IRateTable rates)</code> (C# 12) declares a parameter that is in scope "
             "for the whole class, captured into a hidden field when a method uses it — and that field is "
             "assignable, not <code>readonly</code> (" + PRIMARY + "). Only <code>record</code> turns positional "
             "parameters into properties. It is still the idiomatic shape for a DI-constructed service.</p>"
             "<p><b>Statics sit on the type, as in Java.</b> Kotlin's <code>companion object</code> becomes "
             "<code>static</code> members; <code>const</code> versus <code>static readonly</code> is covered in "
             + ref(2) + ".</p>")},

        code(from_sample(f"{DOM}/Quote.cs", "quote-entity"),
             heading="3.1 · Quote — an entity with required members and a guarded status", keep=True,
             note="<b>Three member forms in twenty lines.</b> The three <code>required</code> properties must appear "
                  "in every <code>new Quote { … }</code>. <code>ValidUntil</code> is <code>init</code>: optional, "
                  "then frozen. <code>Status</code> uses <code>field</code> so the setter can check the move against "
                  "the lifecycle in diagram 3.2; the initializer <code>= QuoteStatus.Quoted</code> writes the backing "
                  "field directly and skips the check, which is why a new quote starts at <code>Quoted</code>. <code>Quote</code> is a <code>class</code>, not a record: two "
                  "quotes with equal data are still two quotes."),

        {"type": "mermaid", "inline": True,
         "heading": "3.2 · The quote lifecycle the Status setter enforces",
         "caption": "green = issues a policy · slate = terminal · any move not drawn throws InvalidOperationException "
                    "from the field-backed setter · QuoteStatus also has Draft, which this entity never uses: it "
                    "starts at Quoted",
         "code": ('%%{init: {"themeVariables": {"fontSize": "13px"}}}%%\n'
                  "stateDiagram-v2\n"
                  "  direction LR\n"
                  "  [*] --> Quoted : new Quote\n"
                  "  Quoted --> Accepted : Accept()\n"
                  "  Quoted --> Expired : Expire()\n"
                  "  Quoted --> Declined : Decline()\n"
                  "  Accepted --> [*] : policy issued\n"
                  "  Expired --> [*]\n"
                  "  Declined --> [*]\n"
                  "  classDef ok fill:#bbf7d0,color:#1f2937,stroke:#16a34a\n"
                  "  classDef stop fill:#e2e8f0,color:#1f2937,stroke:#475569\n"
                  "  class Accepted ok\n"
                  "  class Expired stop\n"
                  "  class Declined stop\n")},

        compare(from_text("""
            // named arguments: a parameter with no
            // default must be passed, or it won't compile
            fun quote(number: Int, req: QuoteRequest) =
                Quote(
                    id = QuoteId(number),
                    request = req,
                    premium = calculator().calculate(req),
                    validUntil = req.startDate, // has a default
                )
            """, "kotlin", file="the idea you already know"),
                from_sample(f"{DOM}/Samples.cs", "object-initializer"),
                heading="3.3 · Construction — Kotlin named arguments vs a C# object initializer",
                note="<b>" + RENAMED + " — the check moves from the constructor to the members.</b> Kotlin enforces "
                     "completeness through constructor parameters without defaults; C# marks the members "
                     "<code>required</code> and checks every <code>new Quote { … }</code>. Leave out "
                     "<code>Premium</code> and the build fails with CS9035. The initializer runs after the "
                     "constructor, which is why <code>init</code> accessors accept its assignments."),

        compare(from_text("""
            class PremiumCalculator(
                private val rates: RateTable,
                rules: List<RatingRule>,
            ) {
                // `val` makes a read-only property; a plain
                // parameter is visible to initializers only
                private val rules = rules.toList()

                fun calculate(request: QuoteRequest): Premium {
                    var net = rates.basePremium(request)
                    for (rule in rules) net *= rule.factor(request)
                    return Premium(net)
                }
            }
            """, "kotlin", file="the idea you already know"),
                from_sample(f"{DOM}/Rating.cs", "primary-ctor"),
                heading="3.4 · A DI-friendly service — Kotlin constructor vs C# primary constructor",
                note="<b>" + TRAP + " for Kotlin hands.</b> There is no <code>val</code> in a C# class's primary "
                     "constructor. <code>rates</code> is used inside a method, so the compiler stores it in a hidden "
                     "field that your own code could reassign; <code>rules</code> is used only in a field initializer, "
                     "so it is never stored at all. Copying <code>rules</code> into a <code>readonly</code> array is "
                     "the C# way to say <i>this dependency does not change</i>."),

        {"type": "table", "heading": "3.5 · Property forms — who can set the value, and when",
         "cols": ["Form", "Declaration", "Who can set it", "From your stack"],
         "rows": [
             ["Auto property", "<code>{ get; set; }</code>", "Anyone, at any time", "Kotlin <code>var</code>"],
             ["Get-only", "<code>{ get; }</code>", "The constructor only", "Kotlin <code>val</code> · Java final field"],
             ["Init-only · C# 9", "<code>{ get; init; }</code>", "Constructor or object initializer, then never",
              "Kotlin <code>val</code> set by named argument"],
             ["Required · C# 11", "<code>required … { get; init; }</code>",
              "Must be set in the initializer — a compile error otherwise", "Kotlin constructor parameter without a default"],
             ["Field-backed · C# 14", "<code>set =&gt; field = …</code>",
              "As the accessors allow; <code>field</code> is the compiler's backing field",
              "Kotlin <code>field</code> in a custom setter"],
             ["Computed", "<code>Money Total =&gt; …;</code>", "Nobody — evaluated on every read",
              "Kotlin <code>val total get() = …</code>"]]},

        # ═══════════════════════════ 4 · INHERITANCE ═══════════════════════════
        {"type": "story", "heading": "4 · Inheritance and interfaces — methods are non-virtual by default",
         "html": (
             "<p><b>In C#, a method can be overridden only if its base class declares it <code>virtual</code> or "
             "<code>abstract</code>.</b> In Java every instance method is virtual unless it is final, private or "
             "static; in Kotlin methods are final until marked <code>open</code>. So for methods C# is Kotlin's "
             + SAME + ", Java's " + TRAP + " — but C# <i>classes</i> are open by default, like Java and unlike "
             "Kotlin (" + NEWOVERRIDE + ").</p>"
             "<p><b>A derived method with the same signature and no <code>override</code> does not override — it "
             "hides.</b> The compiler warns — CS0114 when the base member is virtual, CS0108 when it is not — this "
             "repository turns the warning into an error, and <code>new</code> silences it by declaring the hiding "
             "intentional. Which method runs then depends on "
             "the <i>declared</i> type of the variable, not the object. You meet <code>new</code> in legacy code when "
             "a base library later added a member with a name a subclass already used; in new code it is almost "
             "always a mistake.</p>"
             "<p><b>Interfaces gained default methods and static abstract members, but never state.</b> A default "
             "interface method (C# 8) is reachable only through an interface-typed reference — "
             "<code>new StandardRateTable().BasePremium(…)</code> does not compile. A <code>static abstract</code> "
             "member (C# 11) is a contract on the type rather than the instance, resolved at compile time; it is "
             "what generic math and <code>T.Parse</code> in §5 are built on (" + INTERFACE + ").</p>"
             "<p><b>C# 14 has no closed hierarchies.</b> <code>sealed</code> means Java's <code>final</code>, not "
             "Kotlin's <code>sealed</code>, so a <code>switch</code> over subclasses cannot be proven exhaustive. The "
             "C# 15 preview adds a <code>closed</code> modifier for classes and union types for exactly this "
             "(" + CS15 + ", checked " + CHECKED + ") " + VERIFIED + "; until .NET 11 ships, keep a default arm. "
             "Enums are not covered: an enum switch keeps its default arm (§6).</p>")},

        compare(from_text("""
            abstract class RatingRule {
                abstract String name();

                BigDecimal factor(QuoteRequest r) { return ONE; }

                // every instance method is virtual in Java
                String describe(QuoteRequest r) {
                    return name() + " x" + factor(r);
                }
            }

            final class YoungDriverLoading extends RatingRule {
                String name() { return "young driver"; }

                @Override
                BigDecimal factor(QuoteRequest r) { /* 1.20 */ }

                // silently OVERRIDES describe(): @Override
                // is optional, the behaviour is not
                String describe(QuoteRequest r) {
                    return name() + " (hidden copy)";
                }
            }
            """, "java", file="the habit you bring"),
                from_sample(f"{DOM}/Rating.cs", "dispatch"),
                heading="4.1 · The same hierarchy — Java's virtual default vs C#'s non-virtual default",
                note="<b>Identical shape, different call.</b> In Java, <code>rule.describe(q)</code> on a "
                     "<code>RatingRule</code> variable runs the subclass method. In C#, <code>Describe</code> is not "
                     "virtual, so the subclass can only hide it with <code>new</code> — and a "
                     "<code>RatingRule</code>-typed variable still calls the base version. <code>Factor</code> "
                     "<i>is</i> virtual, so the base <code>Describe</code> picks up the derived 1.20."),

        compare(from_sample(TOUR, "dispatch-demo"),
                from_text("""
            1.20
            young driver x1.20
            young driver (hidden copy)
            """, "text", label="Output — L03.TypesTour", file="captured on the build machine"),
                heading="4.2 · One object, three calls",
                note="<b>One object, two answers to <code>Describe</code>.</b> The virtual <code>Factor</code> "
                     "follows the object; the non-virtual <code>Describe</code> follows the variable's declared "
                     "type. <code>DispatchTests</code> asserts all three lines, so a refactoring that adds "
                     "<code>virtual</code> fails a test instead of silently changing a premium description."),

        {"type": "mermaid", "inline": True,
         "heading": "4.3 · Which method runs? — rule.M() where rule is declared as the base type",
         "caption": "amber = question the compiler or runtime asks · slate = the declared type decides · "
                    "teal = the object's run-time type decides",
         "code": ('%%{init: {"flowchart": {"nodeSpacing": 18, "rankSpacing": 34}}}%%\n'
                  "flowchart LR\n"
                  '  C["rule.M(q)<br/>rule : RatingRule"]:::start --> V{{"M virtual or<br/>abstract in RatingRule?"}}:::q\n'
                  '  V -- "no" --> S["RatingRule.M runs<br/>e.g. Describe"]:::stat\n'
                  '  V -- "yes" --> O{{"Overridden between<br/>RatingRule and the object?"}}:::q\n'
                  '  O -- "yes" --> D["most derived override runs<br/>e.g. YoungDriverLoading.Factor"]:::dyn\n'
                  '  O -- "no · new is not an override" --> B["RatingRule.M runs"]:::stat\n'
                  "  classDef start fill:#c7d2fe,color:#1f2937,stroke:#6366f1;\n"
                  "  classDef q fill:#fde68a,color:#1f2937,stroke:#d97706;\n"
                  "  classDef stat fill:#e2e8f0,color:#1f2937,stroke:#475569;\n"
                  "  classDef dyn fill:#ccfbf1,color:#1f2937,stroke:#0d9488;\n")},

        code(from_sample(f"{DOM}/Rating.cs", "interfaces"),
             heading="4.4 · A default interface method on the rate table", keep=True,
             note="<b>" + DIFFERENT + " from Java defaults.</b> <code>StandardRateTable</code> implements only "
                  "<code>BaseRate</code>. It does not inherit <code>BasePremium</code>: the interface supplies the "
                  "body, so only an <code>IRateTable</code>-typed reference can call it (a Java class inherits its "
                  "default methods). <code>PremiumCalculator</code> takes an <code>IRateTable</code>, so the call "
                  "compiles; <code>L03.TypesTour</code> prints <code>11,250.00 THB</code> (450,000 × 2.5%), and "
                  "<code>DispatchTests</code> asserts the class has no such member. A Visual Basic class implementing "
                  "this interface must still write <code>BasePremium</code> itself (BC30149, table 7.6)."),

        code(from_sample(f"{DOM}/Identifiers.cs", "static-abstract"),
             heading="4.5 · Static abstract members — a contract on the type",
             note="<b>An interface that describes the type, not the instance.</b> Every "
                  "<code>IIdentifier&lt;TSelf&gt;</code> must offer a static <code>Prefix</code> and a static "
                  "<code>Parse</code>. Nothing can call them through an instance; generic code calls them through "
                  "the type parameter, as §5 shows. The self-referencing constraint "
                  "<code>where TSelf : IIdentifier&lt;TSelf&gt;</code> is the same F-bounded shape as Java's "
                  "<code>&lt;T extends Comparable&lt;T&gt;&gt;</code> bound or <code>Enum&lt;E extends "
                  "Enum&lt;E&gt;&gt;</code>."),

        {"type": "table", "heading": "4.6 · Inheritance keywords in the four languages you will read",
         "cols": ["Meaning", "Java", "Kotlin", "C#", "Visual Basic"],
         "rows": [
             ["Can be overridden", "(default)", "<code>open</code>", "<code>virtual</code>",
              "<code>Overridable</code>"],
             ["Overrides a base member", "<code>@Override</code> (optional)", "<code>override</code>",
              "<code>override</code>", "<code>Overrides</code>"],
             ["Must be overridden", "<code>abstract</code>", "<code>abstract</code>", "<code>abstract</code>",
              "<code>MustOverride</code>"],
             ["Abstract class", "<code>abstract class</code>", "<code>abstract class</code>",
              "<code>abstract class</code>", "<code>MustInherit Class</code>"],
             ["Cannot be inherited", "<code>final class</code>", "(default)", "<code>sealed</code>",
              "<code>NotInheritable</code>"],
             ["Stops further overriding", "<code>final</code> method", "<code>final override</code>",
              "<code>sealed override</code>", "<code>NotOverridable Overrides</code>"],
             ["Hides a base member", "—", "—", "<code>new</code>", "<code>Shadows</code>"],
             ["Inherit · implement", "<code>extends</code> · <code>implements</code>", "<code>:</code>",
              "<code>:</code>", "<code>Inherits</code> · <code>Implements</code>"],
             ["Call the base version", "<code>super.m()</code>", "<code>super.m()</code>", "<code>base.M()</code>",
              "<code>MyBase.M()</code>"]]},

        code(from_sample(VB, "vb-keywords"),
             heading="4.7 · The same rules in Visual Basic — what you will read in a legacy estate", keep=True,
             note="<b>" + RENAMED + " keyword for keyword, same dispatch.</b> This is panel 4.1's C# hierarchy "
                  "member for member, declared in the VB project. <code>MustInherit</code> and "
                  "<code>MustOverride</code> are <code>abstract</code>, <code>Overridable</code> is "
                  "<code>virtual</code>, <code>NotInheritable</code> is <code>sealed</code> and <code>Shadows</code> "
                  "is <code>new</code>. A VB method is non-virtual by default too, so <code>L03.VbInterop</code> "
                  f"prints <code>{esc(_VB_DISPATCH)}</code> (panel 8.3) — the same three answers as panel 4.2."),

        # ═══════════════════════════ 5 · GENERICS ═══════════════════════════
        {"type": "story", "heading": "5 · Generics — reified, constrained and variant",
         "html": (
             "<p><b>C# generics survive compilation.</b> <code>List&lt;int&gt;</code> and "
             "<code>List&lt;string&gt;</code> are different run-time types, and <code>List&lt;int&gt;</code> stores "
             "unboxed integers: 1,000 of them cost 4,056 bytes, against 32,056 for <code>List&lt;object&gt;</code> or "
             "the pre-generics <code>ArrayList</code> you still find in .NET Framework code (chart 5.1). Inside a "
             "generic method <code>typeof(T)</code> and <code>default(T)</code> always work, <code>new T()</code> "
             "works under a <code>where T : new()</code> constraint, and each closed type gets its own static "
             "fields. The Java workarounds for erasure — class tokens, "
             "<code>TypeReference</code> subclasses, <code>Supplier&lt;T&gt;</code> factories — have nothing to "
             "solve.</p>"
             "<p><b>Constraints are where the design lives.</b> " + nw("where T : IIdentifier&lt;T&gt;") + " lets "
             "<code>Ids.ParseAll&lt;T&gt;</code> call <code>T.Parse</code>, a static member — something no JVM "
             "generic can express. The same mechanism powers generic math: since .NET 7 and C# 11, operators are "
             "static abstract members of interfaces such as <code>IAdditionOperators</code> and "
             "<code>INumber&lt;T&gt;</code>, so one <code>Sum&lt;T&gt;</code> adds <code>decimal</code> and "
             "<code>Money</code> (" + GMATH + ").</p>"
             "<p><b>Variance is declared on the type, and only interfaces and delegates can have it.</b> "
             "<code>in</code> and <code>out</code> mean exactly what they mean in Kotlin (" + SAME + "). Java's "
             "use-site wildcards have no C# form (" + DIFFERENT + "): <code>List&lt;T&gt;</code> is a class and stays "
             "invariant, and variance never applies to value-type arguments, so an "
             "<code>IEnumerable&lt;int&gt;</code> is not an <code>IEnumerable&lt;object&gt;</code> "
             "(" + VARIANCE + ").</p>")},

        {"type": "chart", "heading": "5.1 · Bytes to store 1,000 integers — reified vs boxed collections",
         "kind": "bar",
         "args": {"data": GENERIC_ALLOC, "ylabel": "bytes", "tone": "indigo", "width": 760, "height": 170},
         "caption": "GC.GetAllocatedBytesForCurrentThread, capacity preset to 1,000 · L03.TypesTour · measured",
         "note": "<b>An eighth of the memory, and zero objects per element.</b> <code>List&lt;int&gt;</code> is one "
                 "list plus one <code>int[1000]</code>. <code>List&lt;object&gt;</code> — the shape every JVM "
                 "<code>List&lt;Integer&gt;</code> has — and the .NET 1.x <code>ArrayList</code> add a 24-byte box "
                 "per integer. When you port an <code>ArrayList</code>, the generic version is also the faster one."},

        compare(from_text("""
            // erasure: T does not exist at run time, so the
            // caller passes a class token and a parser
            static <T> List<T> parseAll(Class<T> type,
                    Function<String, T> parse, String... texts) {
                var ids = new ArrayList<T>(texts.length);
                for (var text : texts) {
                    ids.add(parse.apply(text));
                }
                return ids;
            }

            // T.parse(text), new T(), new T[n]: do not compile
            // List<Integer> holds one boxed Integer per element
            var ids = parseAll(QuoteId.class, QuoteId::parse,
                    "Q-000042", "Q-000043");
            """, "java", file="the erasure workaround"),
                from_sample(f"{DOM}/Identifiers.cs", "reified"),
                heading="5.2 · Parsing identifiers — Java's erasure workaround vs a reified type parameter",
                note="<b>The type argument carries the behaviour.</b> "
                     "<code>Ids.ParseAll&lt;QuoteId&gt;(\"Q-000042\", \"Q-000043\")</code> needs no token and no "
                     "lambda, because <code>IIdentifier&lt;T&gt;</code> promises a static <code>Parse</code>. "
                     "<code>Describe&lt;QuoteId&gt;()</code> prints <code>QuoteId Q- Q-000000</code>: the real type "
                     "name and a real <code>default(T)</code>. In the same run "
                     "<code>Counter&lt;QuoteId&gt;.Hits</code> is 2 while <code>Counter&lt;PolicyNumber&gt;.Hits</code> "
                     "is 1 — one static field per closed generic type."),

        compare(from_text("""
            // declaration-site variance: the same keywords
            interface ReportRenderer<in R : Report> {
                val format: String
                fun render(report: R): String
            }

            interface ReportSource<out R : Report> {
                fun load(): R
            }

            val card: ReportRenderer<QuoteReport> =
                SummaryCardRenderer()

            // Java writes the same idea at every use site:
            // void renderAll(ReportRenderer<? super QuoteReport> r)
            // ReportSource<? extends Report> s = quoteSource;
            """, "kotlin", file="the idea you already know"),
                from_sample(f"{REP}/Contracts.cs", "variance"),
                heading="5.3 · Variance on the report contracts — Kotlin vs C#",
                note="<b>" + SAME + " keywords, one C# restriction.</b> <code>SummaryCardRenderer</code> renders any "
                     "<code>Report</code>, so it can be used where an <code>IReportRenderer&lt;QuoteReport&gt;</code> "
                     "is expected — <code>VarianceTests</code> proves both directions. The compiler rejects "
                     "<code>in</code> or <code>out</code> on a class, and a <code>List&lt;QuoteReport&gt;</code> is "
                     "never a <code>List&lt;Report&gt;</code>."),

        code(from_sample(f"{DOM}/Totals.cs", "generic-math"),
             heading="5.4 · Generic math — one Sum for decimal and Money",
             note="<b>The constraint names an operator.</b> <code>IAdditionOperators&lt;T, T, T&gt;</code> declares "
                  "<code>static abstract T operator +</code>, so <code>total += item</code> compiles for any "
                  "<code>T</code> that implements it: <code>decimal</code> does since .NET 7, and <code>Money</code> "
                  "does because panel 2.3 declares it. <code>L03.TypesTour</code> prints <code>Sum&lt;decimal&gt;=6.50</code> "
                  "and <code>Sum&lt;Money&gt;=1,500.00 THB</code>."),

        {"type": "table", "heading": "5.5 · Constraints you will write and read",
         "cols": ["Constraint", "Means", "Nearest Java / Kotlin", "In the samples"],
         "rows": [
             ["<code>where T : class</code> · <code>struct</code>", "a reference type · a non-nullable value type",
              "no value-type generics on the JVM", "—"],
             ["<code>where T : notnull</code>", "any non-nullable type", "Kotlin <code>T : Any</code>", "—"],
             ["<code>where T : new()</code>", "has a public parameterless constructor, so <code>new T()</code> compiles",
              "a <code>Supplier&lt;T&gt;</code> parameter", "—"],
             ["<code>where T : Report</code>", "derives from a class", "<code>T extends Report</code>",
              nw("IReportRenderer&lt;in TReport&gt;")],
             ["<code>where T : IIdentifier&lt;T&gt;</code>",
              "implements an interface — here one with static abstract members",
              "F-bounded <code>T extends Comparable&lt;T&gt;</code>; no static calls", "<code>Ids.ParseAll&lt;T&gt;</code>"],
             [nw("where T : IAdditionOperators&lt;T,T,T&gt;"), "<code>+</code> is defined for T",
              "not expressible", "<code>Totals.Sum&lt;T&gt;</code>"],
             ["<code>where T : unmanaged</code>", "a value type with no references inside", "not expressible", "—"],
             ["<code>allows ref struct</code> · C# 13", "T may be a stack-only type such as <code>Span&lt;T&gt;</code>",
              "not applicable", "—"]]},

        code(from_sample(VB, "vb-generic"),
             heading="5.6 · The same constraint in Visual Basic — (Of T As …)",
             note="<b>" + RENAMED + " syntax, same reified generic.</b> <code>(Of T As IIdentifier(Of T))</code> is "
                  "C#'s " + nw("&lt;T&gt; where T : IIdentifier&lt;T&gt;") + "; several constraints go in braces, "
                  "<code>(Of T As {Class, New})</code>. VB can declare and call this method, but it cannot write "
                  "<code>T.Parse</code> on its own type parameter (BC32098, table 7.6), so it hands the static call "
                  "to the C# <code>Ids.ParseAll(Of T)</code>. <code>L03.VbInterop</code> prints "
                  f"<code>{esc(_VB_GENERICS)}</code>."),

        # ═══════════════════════════ 6 · EXTENSIONS & EQUALITY ═══════════════════════════
        {"type": "story", "heading": "6 · Extension members, equality and operators",
         "html": (
             "<p><b>C# 14 extension blocks are Kotlin extensions with a different wrapper.</b> Inside a static "
             "class, <code>extension(CoverageClass coverage) { … }</code> declares members that read as if "
             "<code>CoverageClass</code> had them: methods and properties, instance or static, and user-defined "
             "operators. There are no fields — extensions still hold no state (" + CS14 + " · " + EXT + "). "
             "Extension <i>indexers</i> arrive with the C# 15 preview (checked " + CHECKED + ") " + VERIFIED
             + ".</p>"
             "<p><b>For enums this is where behaviour goes.</b> Kotlin puts <code>code</code> and "
             "<code>fromCode</code> inside the <code>enum class</code>; a C# enum cannot hold members, so they live "
             "in an extension block. Classic <code>this</code>-parameter extension methods (panel 6.2) compile to "
             "the same IL, so existing libraries can move to the new syntax without breaking callers.</p>"
             "<p><b><code>==</code> means whatever the type says it means.</b> On a class it compares references "
             "unless the class overloads it — the opposite of Kotlin, where <code>==</code> calls "
             "<code>equals</code> (" + TRAP + "). Records and <code>string</code> overload it. A plain struct has no "
             "<code>==</code> at all until you declare one, and its default <code>Equals</code> compares fields "
             "through reflection. Two boxed <code>5</code>s typed as <code>object</code> are not <code>==</code> "
             "(" + EQUALITY + ").</p>"
             "<p><b><code>Equals</code> and <code>GetHashCode</code> are one contract — the same one as Java's.</b> "
             "Compare VINs case-insensitively but hash them case-sensitively and a <code>HashSet</code> loses them: "
             "<code>L03.TypesTour</code> prints <code>False</code> for exactly that bug. Operators are static methods "
             "with reserved names (<code>op_Addition</code>, <code>op_Equality</code>); define <code>==</code> and "
             "<code>!=</code> as a pair, and Visual Basic calls them like its own.</p>")},

        compare(from_text("""
            // Kotlin: an enum is a class and holds members
            enum class CoverageClass(val code: String) {
                CLASS_1("1"), CLASS_2_PLUS("2+"),
                CLASS_3_PLUS("3+"), CLASS_3("3");

                companion object {
                    fun fromCode(code: String) =
                        entries.first { it.code == code }
                }
            }

            // ...and extensions add more from outside
            val CoverageClass.coversOwnDamage: Boolean
                get() = this != CoverageClass.CLASS_3

            // CoverageClass.CLASS_2_PLUS.code       -> "2+"
            // CoverageClass.fromCode("3+")          -> CLASS_3_PLUS
            """, "kotlin", file="the idea you already know"),
                from_sample(f"{DOM}/Extensions.cs", "extension-block"),
                heading="6.1 · Behaviour for CoverageClass — Kotlin enum class vs a C# 14 extension block", keep=True,
                note="<b>Same call sites:</b> <code>CoverageClass.Class2Plus.Code</code> and "
                     "<code>CoverageClass.FromCode(\"3+\")</code>. The first block names its receiver "
                     "(<code>coverage</code>) and holds instance members; the second has no name and holds static "
                     "members that appear on the enum itself. The default arm is not decoration: an enum is an "
                     "integer, and <code>(CoverageClass)42</code> reaches it."),

        code(from_sample(f"{DOM}/Extensions.cs", "classic-extension"),
             heading="6.2 · A classic extension method — the form LINQ and services.AddX() use",
             note="<b>" + SAME + " idea as a Kotlin extension function, and the form most .NET code still uses.</b> "
                  "A <code>static</code> method in a <code>static</code> class whose first parameter carries "
                  "<code>this</code> reads as <code>driver.IsYoungOn(day)</code>; every LINQ operator and every "
                  "<code>services.AddX()</code> registration call is declared this way. It is visible only where its "
                  "namespace is imported, and it can add methods only — properties, static members and operators need "
                  "the C# 14 block of panel 6.1. <code>ExtensionTests</code> calls both forms."),

        compare(from_sample(f"{DOM}/Vin.cs", "equatable-class"),
                from_sample(f"{DOM}/Vin.cs", "equatable-record"),
                heading="6.3 · Case-insensitive VIN equality — by hand, and as a record",
                note="<b>The left is what legacy .NET code looks like; the right is what to write now.</b> Both "
                     "compare and hash with the same <code>OrdinalIgnoreCase</code> rule. A record lets you replace "
                     "just <code>Equals(VinRecord?)</code> and <code>GetHashCode</code>; the generated "
                     "<code>Equals(object)</code>, <code>==</code> and <code>!=</code> route through your version. "
                     "<code>EqualityTests</code> checks both types in a <code>HashSet</code>."),

        code(from_sample(TOUR, "boxing-equality"),
             heading="6.4 · Boxes, overloaded == and a broken hash code",
             note="<b>Output, in order:</b> <code>False</code>, <code>True</code>, <code>True</code>, <code>True</code>, "
                  "<code>False</code> (captured, §8). Two boxes of <code>5</code> are different objects, so "
                  "<code>==</code> on <code>object</code> is false while <code>Equals</code> is true. "
                  "<code>BrokenVin</code> is equal case-insensitively but hashes case-sensitively, so the set looks in "
                  "the wrong bucket and never finds the lower-case VIN."),

        # ═══════════════════════════ 7 · DESIGN + VB ═══════════════════════════
        {"type": "story", "heading": "7 · Design in C# — a multi-format report framework, extended from VB",
         "html": (
             "<p><b>This is the multi-format report framework you have built before, with the type system doing "
             "more of the work.</b> " + nw("IReportRenderer&lt;in TReport&gt;") + " is the strategy; "
             + nw("ReportRenderer&lt;TReport&gt;") + " is a template-method base class whose non-virtual "
             "<code>Render</code> fixes the skeleton; " + nw("ReportService&lt;TReport&gt;") + " picks a renderer "
             "by format name. The interface is the contract callers and the container see; the abstract class is "
             "optional shared skeleton an implementer may inherit — keep both, so a renderer that shares nothing "
             "can implement the interface directly. The sample renders text, CSV and JSON strings where production code would write PDF, "
             "Excel and JSON files — the shape does not change.</p>"
             "<p><b>SOLID transfers as-is (" + SAME + "); the .NET-specific parts are variance and the constructor "
             "shape.</b> A new format is a new class and no edits (open/closed). The service depends on "
             + nw("IEnumerable&lt;IReportRenderer&lt;TReport&gt;&gt;") + ", which the ASP.NET Core container "
             "fills with every registration of exactly that closed type, as Spring fills a "
             "<code>List&lt;ReportRenderer&gt;</code> — registration is " + ref(8) + ". Contravariance lets one "
             "<code>SummaryCardRenderer</code> serve every report type when you assign it, but the built-in "
             "container does not apply variance: register it under each " + nw("IReportRenderer&lt;X&gt;") + " you "
             "need. Because <code>Render</code> is not virtual, no subclass in either language can reorder or skip "
             "the header hook when called through " + nw("ReportRenderer&lt;TReport&gt;") + " — short of "
             "re-implementing the interface, which a code review should reject.</p>"
             "<p><b>Visual Basic can extend the framework, but it cannot declare the modern types it consumes.</b> "
             "<code>L03.VbInterop</code> inherits the C# generic base class, overrides its hooks, and produces CSV "
             "identical to the C# renderer's (<code>same CSV from C# and VB? True</code>). It constructs and compares "
             "C# records, uses their operators, and sets <code>required</code> and <code>init</code> members in a "
             "<code>With { }</code> initializer — Visual Basic 16.9 added init-only consumption (" + VBNEW + ", "
             "checked " + CHECKED + ") " + VERIFIED + ". It has no syntax to declare any of them, in line with Microsoft's consumption-only strategy for VB "
             "(" + VBSTRAT + "); the migration plan that follows from it is " + ref(6) + ".</p>"
             "<p><b>Pin the language boundary with a test, not a wiki page.</b> In a mixed estate the risk is a C# "
             "change that quietly makes a shared type unusable from VB. <code>VbCompilerTests</code> compiles Visual "
             "Basic snippets against the C# assemblies with Roslyn's VB compiler (package " + ROSLYN + ", the "
             "compiler line SDK 10.0.401 ships) and asserts the exact error id of every limit in table 7.6 "
             "(panel 7.7), and that the call-site workarounds compile.</p>")},

        {"type": "mermaid", "inline": True,
         "heading": "7.1 · The report framework — one C# contract, renderers in two languages",
         "caption": "interface and abstract base in L03.Reports · VbCsvRenderer lives in the Visual Basic project · "
                    "SummaryCardRenderer renders any Report and fits QuoteReport through contravariance",
         "code": ("classDiagram\n"
                  "  direction TB\n"
                  "  class ReportService~TReport~ {\n"
                  "    +Formats\n"
                  "    +Render(TReport, string) string\n"
                  "  }\n"
                  "  class IReportRenderer~TReport~ {\n"
                  "    <<interface>>\n"
                  "    +Format string\n"
                  "    +Render(TReport) string\n"
                  "  }\n"
                  "  class ReportRenderer~TReport~ {\n"
                  "    <<abstract>>\n"
                  "    +Render(TReport) string\n"
                  "    #WriteHeader(StringBuilder, TReport)\n"
                  "    #WriteBody(StringBuilder, TReport)*\n"
                  "  }\n"
                  "  class CsvRenderer\n"
                  "  class TextTableRenderer\n"
                  "  class JsonRenderer\n"
                  "  class SummaryCardRenderer\n"
                  "  class VbCsvRenderer {\n"
                  "    <<Visual Basic>>\n"
                  "  }\n"
                  "  ReportService o-- IReportRenderer : selects by Format\n"
                  "  IReportRenderer <|.. ReportRenderer\n"
                  "  ReportRenderer <|-- CsvRenderer : QuoteReport\n"
                  "  ReportRenderer <|-- TextTableRenderer : QuoteReport\n"
                  "  ReportRenderer <|-- JsonRenderer : QuoteReport\n"
                  "  ReportRenderer <|-- SummaryCardRenderer : Report\n"
                  "  ReportRenderer <|-- VbCsvRenderer : QuoteReport\n")},

        code(from_sample(f"{REP}/Renderers.cs", "renderer-base"),
             heading="7.2 · The template-method base class",
             note="<b>Three kinds of member, three promises.</b> <code>Render</code> is not virtual: every renderer "
                  "runs header, then body. <code>WriteHeader</code> is <code>virtual</code> with a default — CSV "
                  "replaces it, JSON empties it. <code>WriteBody</code> is <code>abstract</code>. "
                  "<code>Invariant($\"…\")</code> formats the date without the machine's culture, so a Thai-locale "
                  "server does not print a Buddhist-calendar year."),

        code(from_sample(f"{REP}/Renderers.cs", "strategy"),
             heading="7.3 · The strategy selector — DI-friendly and case-insensitive",
             note="<b>The constructor is the whole integration surface.</b> Tests pass renderers as a collection "
                  "expression; a DI container passes every registration of exactly "
                  + nw("IReportRenderer&lt;TReport&gt;") + ". The primary-constructor parameter is used "
                  "only by the field initializer, so it is never stored. An unknown format throws "
                  "<code>NotSupportedException</code> rather than returning an empty report."),

        compare(from_sample(f"{REP}/Renderers.cs", "csv-renderer"),
                from_sample(VB, "vb-csv"),
                heading="7.4 · The same CSV renderer in C# and in Visual Basic",
                note="<b>One base class, two languages, byte-identical output.</b> VB writes "
                     "<code>Inherits ReportRenderer(Of QuoteReport)</code> for <code>: ReportRenderer&lt;QuoteReport&gt;</code> "
                     "and <code>Protected Overrides Sub</code> for <code>protected override void</code>. The one real "
                     "difference is the class code: VB calls the extension property's generated "
                     "<code>get_Code(…)</code> method (table 7.6, row 1). VB is longer, not harder: every member and "
                     "loop ends on its own line (<code>End Sub</code>, <code>Next</code>) where C# uses braces or an "
                     "expression body."),

        code(from_sample(VB, "vb-consume"),
             heading="7.5 · What Visual Basic does with C# records, operators and required members",
             note="<b>Consumption works; declaration does not exist.</b> VB compares records with <code>=</code>, "
                  "because C# emitted <code>op_Equality</code>. It has no <code>with</code>, so the changed copy is "
                  "built by calling the constructor. VB also <i>enforces</i> the C# contract on "
                  "<code>required</code> and <code>init</code> members — the compiler errors are in table 7.6."),

        {"type": "table", "heading": "7.6 · What the Visual Basic compiler says — every row asserted by VbCompilerTests",
         "cols": ["C# feature", "Written in Visual Basic", "VB compiler", "What works instead"],
         "rows": VB_LIMITS},

        code(from_sample(f"{L}/L03.Reports.Tests/VbCompilerTests.cs", "vb-compiler-tests"),
             heading="7.7 · Pinning the boundary — Visual Basic compiled inside an xUnit test", keep=True,
             note="<b>Table 7.6 is test data, not recollection.</b> Each row compiles one VB statement with "
                  "<code>Option Strict On</code> against <code>L03.Domain</code> and asserts the complete set of error "
                  "ids, so a snippet that fails for any other reason fails the test. The declaration rows sit in a "
                  "second theory in the same file, beside one more VB fact: <code>Dim q</code> in a method with a "
                  "parameter <code>Q</code> is BC30734, because VB names are case-insensitive — see " + ref(6) + "."),

        figure_heading("7.8 · Declare, consume or work around — Visual Basic on modern C# types"),
        {"type": "threecol", "boxes": [
            {"heading": "Visual Basic declares", "tone": "teal",
             "items": ["Classes, structures and interfaces, with <code>In</code> / <code>Out</code> variance",
                       "<code>MustInherit</code> · <code>Overridable</code> · <code>Shadows</code> hierarchies",
                       "Operators and classic <code>&lt;Extension&gt;</code> methods",
                       "Generic types and methods: <code>(Of T As IIdentifier(Of T))</code>"]},
            {"heading": "Visual Basic only consumes", "tone": "indigo",
             "items": ["Records and record structs — construct, compare, no <code>with</code>",
                       "<code>init</code> and <code>required</code> members, inside "
                       "<code style=\"white-space:nowrap\">With { }</code>",
                       "Default interface methods, through the interface",
                       "Generic methods constrained on static abstract members"]},
            {"heading": "Visual Basic cannot reach as syntax", "tone": "rose",
             "items": ["C# 14 extension properties — call <code>get_Code(…)</code> instead",
                       "Static extension members on the extended type",
                       "<code>with</code> expressions",
                       "Calling <code>T.Parse</code> on its own type parameters"]}]},

        # ═══════════════════════════ 8 · HANDS-ON ═══════════════════════════
        {"type": "story", "heading": "8 · Hands-on — build, test and run the lesson-03 samples",
         "html": (
             "<p><b>Six projects, one command to prove them.</b> <code>verify_samples.py --only 3</code> builds the "
             "two libraries, runs both xUnit projects, and runs both consoles to completion. Every C# and VB panel in "
             "this PDF was cut from those files, and every byte count and method count came from the "
             "<code>L03.TypesTour</code> output below.</p>"
             "<p><b>Read the two outputs against the sections.</b> Lines 2 and 3 of the tour are panel 2.4; "
             "<code>alloc</code> and <code>generated</code> are charts 2.5 and 2.6; the three bare lines after "
             "<code>dispatch</code> are panel 4.2; the five after <code>equality</code> are panel 6.4. The VB output "
             "proves §4 and §7: VB's own hierarchy dispatched like C#'s, and VB compared C# records, set required "
             "members, called an extension property through its method and rendered the same CSV. What VB <i>cannot</i> do is proved by "
             "<code>VbCompilerTests</code> inside <code>L03.Reports.Tests</code> (7.7).</p>"
             "<p><b>Then break something on purpose.</b> Remove <code>virtual</code> from "
             "<code>RatingRule.Factor</code> and watch the build fail on CS0506; delete <code>Premium = …</code> "
             "from a <code>new Quote { … }</code> and read CS9035; make <code>BrokenVin</code> hash "
             "case-insensitively and watch <code>EqualityTests</code> fail its <code>False</code> assertion.</p>")},

        code(from_text("""
            # build, test and run all six lesson-03 projects
            python 0-script/verify_samples.py --only 3

            # the measurements quoted in this lesson
            dotnet run --project lesson-03-types-oop-generics/samples/L03.TypesTour -c Release

            # Visual Basic extending the C# report framework
            dotnet run --project lesson-03-types-oop-generics/samples/L03.VbInterop -c Release

            # the tests on their own
            dotnet test lesson-03-types-oop-generics/samples/L03.Domain.Tests
            dotnet test lesson-03-types-oop-generics/samples/L03.Reports.Tests
            """, "shell"), heading="8.1 · Commands",
             note="<b><code>verify_samples.py</code> is the proof; the two <code>dotnet run</code> lines reproduce "
                  "panels 8.2 and 8.3.</b> Run everything from the repository root, with SDK 10.0.401 or a later "
                  "10.0 feature band (<code>global.json</code>). <code>dotnet run</code> and <code>dotnet test</code> "
                  "restore and build what they need, so there is no separate restore step."),

        code(from_text(TOUR_OUT, "text", label="Output — L03.TypesTour", file="captured on the build machine"),
             heading="8.2 · What you should see — the C# tour", keep=True,
             note="<b>Only the first line should differ on your machine</b> — the runtime patch number. The byte "
                  "counts assume a 64-bit process; the rest is deterministic because the tour fixes the culture and "
                  "uses no clock or random numbers."),

        code(from_text(VB_OUT, "text", label="Output — L03.VbInterop", file="captured on the build machine"),
             heading="8.3 · What you should see — Visual Basic on the C# types",
             note="<b>The key line is <code>same CSV from C# and VB? True</code>.</b> "
                  f"<code>dispatch {esc(_VB_DISPATCH)}</code> is panel 4.2 again, from the VB hierarchy of panel 4.7: "
                  "<code>Overridable</code> follows the object, <code>Shadows</code> follows the declared type."),

        {"type": "chartrow", "charts": [
            {"heading": "8.4 · Code lines per sample project", "kind": "hbar",
             "args": {"data": project_loc, "tone": "navy", "width": 390, "labelw": 120},
             "caption": "non-blank, non-comment lines of .cs and .vb files · measured at build",
             "note": (f"<b>The two test projects hold {loc_tests} lines against {loc_libs} in the two libraries "
                      "they test.</b> Line counts are not coverage: nothing in this lesson measures which lines the "
                      "tests execute. " + ref(10) + " measures coverage and makes it a gate.")},
            {"heading": "8.5 · Test cases per test class", "kind": "hbar",
             "args": {"data": shown_tests, "tone": "teal", "width": 390, "labelw": 150},
             "caption": "[Fact] methods plus [InlineData] rows · the smallest classes combined · measured at build",
             "note": ("<b>Every item in the Traps callout below has a test that fails if the trap is removed</b> — "
                      "except exhaustiveness over a class hierarchy, which C# 14 cannot express. "
                      + (f"<code>VbCompilerTests</code> is the largest class ({tests['VbCompilerTests']} cases): the "
                         "boundary with Visual Basic is where a C# change breaks code the C# team never compiles."
                         if ranked_tests[0][0] == "VbCompilerTests" else
                         f"<code>{ranked_tests[0][0]}</code> is the largest class ({ranked_tests[0][1]} cases)."))}]},

        {"type": "callout", "variant": "warn", "heading": "⚠ Traps — they look right to a JVM engineer",
         "items": [
             "<b>Overriding without <code>virtual</code> and <code>override</code>.</b> A same-named method hides the "
             "base method (CS0114 when the base is virtual, CS0108 when it is not); calls through the base type still "
             "run the base code. Here the warning is an "
             "error; in many legacy solutions it is not.",
             "<b><code>==</code> on a class or on <code>object</code> compares references.</b> Two boxed "
             "<code>5</code>s are not <code>==</code>. Use <code>Equals</code>, a record, or an overloaded operator.",
             "<b>Structs are copied.</b> A struct read from a <code>List&lt;T&gt;</code> or a property is a copy, and "
             "<code>default(Money)</code> or <code>new Money[n]</code> runs no constructor — <code>Currency</code> is "
             "null even though its type says it cannot be.",
             "<b>A class's primary-constructor parameters are not <code>val</code>s.</b> They are captured, mutable "
             "and invisible as properties; copy them into <code>readonly</code> fields when that matters.",
             "<b>Enums are open integers and <code>sealed</code> means final.</b> Neither gives you Kotlin's "
             "exhaustive <code>when</code>. Keep a default arm on class-hierarchy switches until <code>closed</code> "
             "(C# 15 preview) ships; enum switches always need one."]},

        {"type": "callout", "variant": "ok", "heading": "✔ Checkpoint — you are ready for lesson 04 when",
         "items": [
             f"<code>python 0-script/verify_samples.py --only 3</code> reports {n_proj}/{n_proj} sample projects "
             "passed.",
             "You can place every MotorQuote type on diagram 2.7 and defend the choice in terms of chart 2.5.",
             "You can predict the three lines of panel 4.2 before running the tour, and say which keyword change "
             "would alter each.",
             "You can explain why <code>SummaryCardRenderer</code> fits <code>IReportRenderer&lt;QuoteReport&gt;</code> "
             "while a <code>List&lt;QuoteReport&gt;</code> never fits <code>List&lt;Report&gt;</code>.",
             "You can name the two C# 14 features Visual Basic can only reach through a workaround, and three older "
             "C# features it can consume but not declare."]},

        {"type": "callout", "variant": "summary", "heading": "🔍 Check yourself",
         "items": [
             "How many bytes did 1,000 <code>Money</code> values take as a <code>Money[]</code>, as class instances "
             "and as boxes — and why is a box no cheaper than a class?",
             "<code>RatingRule rule = new YoungDriverLoading();</code> — which <code>Describe</code> runs, and why does "
             "its text still contain the derived factor 1.20?",
             "What does <code>default(Money).Currency</code> return, and which constructor ran to produce it?",
             "Why is an <code>IReportRenderer&lt;Report&gt;</code> assignable to "
             "<code>IReportRenderer&lt;QuoteReport&gt;</code>, while <code>IEnumerable&lt;int&gt;</code> is not "
             "assignable to <code>IEnumerable&lt;object&gt;</code>?",
             "Which member kinds can a C# 14 extension block declare, which arrive in C# 15, and how does Visual Basic "
             "call the <code>Code</code> extension property?",
             "Why is <code>ReportRenderer&lt;TReport&gt;.Render</code> deliberately not virtual, and which call "
             "path could a subclass still use to skip the header?",
             "In <code>PremiumCalculator(IRateTable rates, IEnumerable&lt;RatingRule&gt; rules)</code>, which "
             "parameter does the compiler store, can the class reassign it, and why does the class copy "
             "<code>rules</code> into a <code>readonly</code> array?"]},

        {"type": "footer",
         "html": ("<b>Lesson 03 in one line:</b> choose reference or value semantics per type — "
                  "<b>class</b> for entities, <b>readonly record struct</b> for values, <b>record</b> for data — "
                  "remember that methods are non-virtual and generics are reified, and let Visual Basic consume what "
                  "it cannot declare. "
                  "<br/><b>Next:</b> " + ref(4) + " — collections, LINQ and the functional side of C#.")},
    ]
