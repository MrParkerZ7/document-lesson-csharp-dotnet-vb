# -*- coding: utf-8 -*-
"""Lesson 04 — Collections, LINQ & Functional C#. Built to 1-analysis/spec_lesson-pdfs/_standard.md;
unit spec 1-analysis/spec_lesson-pdfs/lesson-04-linq-collections-functional.md."""
import re

from lesson_kit import (BUILD_DATE, DIFFERENT, MEASURED, REPO, RENAMED, SAME, TRAP, VERIFIED,
                        T_ARCH, T_CS, T_JVM, code, compare, esc,
                        from_sample, from_text, legend, link, loc, mapping, pill, style_block)
from lessons.roster import meta, ref

META = meta(
    4,
    subtitle="Java Streams, Kotlin collections and TypeScript array methods, re-mapped onto .NET collections, "
             "LINQ, delegates and expression trees",
    objectives=[
        "Choose the collection type to accept, store and return — IEnumerable, IReadOnlyList, immutable or "
        "frozen — and say what each one promises the caller",
        "Predict when a LINQ query runs, how many times it runs, and where to materialise it",
        "Translate Java Stream, Kotlin and TypeScript pipelines into LINQ, including the .NET 9 and .NET 10 "
        "operators",
        "Use delegates, closures and records functionally — and spot the capture and copy traps",
        "Explain Func versus Expression and build a small translator from a C# predicate to a DynamoDB "
        "filter expression",
        "Read Visual Basic query syntax (Group By … Into, Aggregate, Skip While) and port it to C#",
    ],
    maps_from="Java Streams and Collectors, Kotlin collections and sequences, TypeScript array methods, the "
              "dashboard queries you wrote for a BI tool, and a DynamoDB query auto-generator library you built "
              "for a serverless platform.",
)

L = "lesson-04-linq-collections-functional/samples"
COLL = f"{L}/L04.Collections/Program.cs"
DASH = f"{L}/L04.QuoteData/QuoteDashboard.cs"
RATING = f"{L}/L04.QuoteData/Rating.cs"
QGEN = f"{L}/L04.QueryGen/DynamoFilter.cs"
QGEN_T = f"{L}/L04.QueryGen.Tests/DynamoFilterTests.cs"
DATA_T = f"{L}/L04.QuoteData.Tests/DashboardTests.cs"
ANALYTICS = f"{L}/L04.QuoteAnalytics/Program.cs"
VB = f"{L}/L04.VbLinq/Program.vb"

COLLEXPR = link("Collection expressions",
                "https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/collection-expressions")
CSHIST = link("The history of C#", "https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-version-history")
NET8RT = link("What's new in .NET 8", "https://learn.microsoft.com/en-us/dotnet/core/whats-new/dotnet-8/runtime")
NET6 = link("What's new in .NET 6", "https://learn.microsoft.com/en-us/dotnet/core/whats-new/dotnet-6")
NET9LIB = link("What's new in .NET 9 libraries",
               "https://learn.microsoft.com/en-us/dotnet/core/whats-new/dotnet-9/libraries")
JOINS = link("Join operations", "https://learn.microsoft.com/en-us/dotnet/csharp/linq/standard-query-operators/join-operations")
ASYNCENUM = link("System.Linq.AsyncEnumerable in .NET 10",
                 "https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/10.0/asyncenumerable")
REFSTRUCT = link("ref struct types",
                 "https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/ref-struct")
ILIST = link("IList<T>", "https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.ilist-1")
LINQEXEC = link("Introduction to LINQ queries",
                "https://learn.microsoft.com/en-us/dotnet/csharp/linq/get-started/introduction-to-linq-queries")
SQO = link("Standard query operators", "https://learn.microsoft.com/en-us/dotnet/csharp/linq/standard-query-operators/")
LAMBDAS = link("Lambda expressions",
               "https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/lambda-expressions")
EXPTREES = link("Expression trees", "https://learn.microsoft.com/en-us/dotnet/csharp/advanced-topics/expression-trees/")
SPANBREAK = link("C# 14 overload resolution with span parameters",
                 "https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/10.0/csharp-overload-resolution")
DDBOPS = link("DynamoDB condition and filter expressions",
              "https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Expressions.OperatorsAndFunctions.html")
DDBFILTER = link("DynamoDB Query filter expressions",
                 "https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Query.FilterExpression.html")
DDBNAMES = link("DynamoDB expression attribute names",
                "https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Expressions.ExpressionAttributeNames.html")
VBLINQ = link("Introduction to LINQ in Visual Basic",
              "https://learn.microsoft.com/en-us/dotnet/visual-basic/programming-guide/language-features/linq/introduction-to-linq")
VBAGG = link("Aggregate clause",
             "https://learn.microsoft.com/en-us/dotnet/visual-basic/language-reference/queries/aggregate-clause")
CSQUERY = link("C# query keywords",
               "https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/query-keywords")
JSTREAM = link("java.util.stream.Stream",
               "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/stream/Stream.html")
KSEQ = link("Kotlin sequences", "https://kotlinlang.org/docs/sequences.html")
SHUFFLE = link("Enumerable.Shuffle",
               "https://learn.microsoft.com/en-us/dotnet/api/system.linq.enumerable.shuffle")
INFSEQ = link("Enumerable.InfiniteSequence",
              "https://learn.microsoft.com/en-us/dotnet/api/system.linq.enumerable.infinitesequence")
CA1851 = link("CA1851", "https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca1851")

# ── output captured from real runs of the samples on the build machine (Windows, .NET 10.0.12) ──────────
# DashboardTests.Dashboard_numbers_match_the_captured_lesson_output pins the dashboard figures below, so a
# change to the rating rules or the dataset fails a test before these panels go stale.
OUT_COLLECTIONS = """
1. collection expressions
  shortlist  Toyota, Honda, Isuzu, Toyota
  years      6 elements
  channels is a List<string>? False
  channels type <>z__ReadOnlyArray`1
2. read-only is not immutable
  view      3
  wrapper   3
  snapshot  2
  frozen    2
  after cast + Remove  2
3. frozen lookup table
  Class2Plus base rate  0.012
  classes with a rate   4
4. deferred execution
  declared          calls = 0
  three passes      calls = 482
  ToList + 3 reads  calls = 240
  (127 accepted, first Q-0002)
  > threshold, run 1  123
  > threshold, run 2  67
  InvalidOperationException
5. iterators
  iterator created
  (iterator body starts)
  renewal 2026-11-01
  renewal 2027-11-01
  renewal 2028-11-01
6. closures
  for      3,3,3
  foreach  0,1,2
7. with copies are shallow
  draft notes  created | renewal
  same list?   True
8. delegate types are nominal
  Count 127, FindAll 127
9. a key that is not there
  lookup     0 Tesla quotes
  dictionary KeyNotFoundException
"""

OUT_DASHBOARD = """
MotorQuote dashboard: 240 quotes, illustrative rates
declined, never priced         24 (3+ claims in 5 years)
conversion by coverage class   quoted accepted rate
  Class1                       54       22   40.7%
  Class2Plus                   54       32   59.3%
  Class3Plus                   54       32   59.3%
  Class3                       54       41   75.9%
premium bands, priced quotes
  < 3k        40
  3k-6k      109
  6k-9k       50
  9k-12k      16
  12k+         1
top makes, accepted quotes
  1. Toyota    27
  2. Honda     22
  3. MG        16
  4. Isuzu     15
  5. Nissan    14
accepted premium by class, THB
  Class1          136,262
  Class2Plus      169,483
  Class3Plus      174,299
  Class3          130,512
issuance       127 accepted, 21 pending
export batches 100 + 100 + 40
lookup         49 Toyota quotes
"""

OUT_EXPRESSIONS = """
compiled  Func`2  -> True
tree      Equal  -> (Convert(q.Coverage, Int32) == 0)
binds to  MemoryExtensions.Contains
FilterExpression  ((#n0 = :v0 AND #n1.#n2 >= :v1) AND begins_with(#n3.#n4, :v2))
Names             [#n0, Coverage], [#n1, Total], [#n2, Amount], [#n3, Vehicle], [#n4, Make]
Values            [:v0, Class1], [:v1, 15000], [:v2, To]
"""

OUT_VB = """
VB dashboard: 240 quotes, illustrative rates
conversion by coverage class   quoted accepted rate
  Class1                       54       22   40.7%
  Class2Plus                   54       32   59.3%
  Class3Plus                   54       32   59.3%
  Class3                       54       41   75.9%
top makes, accepted quotes
  1. Toyota    27
  2. Honda     22
  3. MG        16
  4. Isuzu     15
  5. Nissan    14
accepted       127 quotes, 610,555 THB, largest 12,182
makes          BYD,Ford,Honda,Isuzu,Mazda,MG,Nissan,Toyota
premiums from 8,600 to under 8,900 THB
  Q-0139   8,685.55
  Q-0219   8,685.55
  Q-0005   8,701.67
  Q-0015   8,862.81
  Q-0175   8,862.81
"""

OUT_TESTS = """
Passed!  - Failed: 0, Passed: 24, Skipped: 0, Total: 24 - L04.QueryGen.Tests.dll (net10.0)
Passed!  - Failed: 0, Passed: 19, Skipped: 0, Total: 19 - L04.QuoteData.Tests.dll (net10.0)
"""

# Pygments' vbnet lexer has no token for VB 14 interpolated strings, so every `$"` prints inside a red
# error box. The code is valid (the samples compile); drop the box, keep the text. (kit request)
_ERROR_SPAN = re.compile(r'<span style="border: 1px solid #F00">(.*?)</span>', re.S)


_CODEH_CSS = ("font-weight:700;font-size:10pt;color:#1A237E;margin:12px 0 4px;border-bottom:2px solid #C5CAE9;"
              "padding-bottom:2px;break-after:avoid;page-break-after:avoid;")


def listed(block, heading):
    """Copy a code panel's printed heading onto the block so the Contents lists it (kit request, as in 01).

    A listed block gets a Contents page marker, and brief_pdf makes a marker's host container
    break-inside:avoid unless the host's first child is a `.ct` heading line. That turned every listed
    panel unbreakable — a 32-line panel jumped whole and left 40% of a page empty. A panel that is NOT
    kept (`keep` False, or longer than the kit's keep limit) therefore prints its heading as a `.ct` line
    styled like `.codeh`, so the marker pins to the heading and the panel may split. (kit request)"""
    block.update(heading=heading, toc=2)
    if "vb" in block.get("_langs", []):
        block["html"] = _ERROR_SPAN.sub(r"\1", block["html"])
    html = block["html"]
    if 'class="code keep"' not in html and 'class="cmp keep"' not in html:
        block["html"] = html.replace('<div class="codeh">', f'<div class="ct" style="{_CODEH_CSS}">', 1)
    return block


def figure_heading(text):
    """A numbered heading for a block type that prints none of its own (twocol), kept with that block."""
    return {"type": "html", "html": f'<div class="figh"><h2>{esc(text)}</h2></div>', "heading": text,
            "toc": 2, "_keep_with_next": True}


def part(output, n):
    """The lines of a captured console output that belong to its numbered part `n.`, header included."""
    lines = output.strip("\n").splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.startswith(f"{n}. "))
    end = next((j for j in range(start + 1, len(lines)) if re.match(r"^\d+\. ", lines[j])), len(lines))
    return "\n".join(lines[start:end])


def from_line(output, first):
    """A captured output from the line that starts with `first` to the end — an excerpt, never an edit."""
    lines = output.strip("\n").splitlines()
    return "\n".join(lines[next(i for i, ln in enumerate(lines) if ln.startswith(first)):])


def half(sample):
    """A compare() side whose caption drops the `samples/<Project>/` prefix. A half-width panel header cuts a
    long caption with an ellipsis, and the region name at its end is the part a reader needs. The code itself
    is untouched: it is still the sample's region."""
    return dict(sample, file=re.sub(r"^samples/[^/]+/", "", sample["file"]))


def captured(text, label, file="captured on the build machine"):
    return from_text(text, "text", label=label, file=file)


def test_cases(relpath):
    """[Fact] methods plus one case per [InlineData] row — the count `dotnet test` reports. MEASURED."""
    src = (REPO / relpath).read_text(encoding="utf-8-sig")
    return src.count("[Fact]") + src.count("[InlineData(")


def blocks():
    calls = {k: int(v) for k, v in re.findall(r"^\s+(declared|three passes|ToList \+ 3 reads)\s+calls = (\d+)",
                                              OUT_COLLECTIONS, re.M)}
    conversion = [(c, int(q), int(a), float(r)) for c, q, a, r in
                  re.findall(r"^\s+(Class\w+)\s+(\d+)\s+(\d+)\s+([\d.]+)%", OUT_DASHBOARD, re.M)]
    bands = [(b, int(n)) for b, n in re.findall(r"^\s+(< 3k|3k-6k|6k-9k|9k-12k|12k\+)\s+(\d+)$", OUT_DASHBOARD, re.M)]
    accepted = sum(a for _c, _q, a, _r in conversion)
    quoted = sum(q for _c, q, _a, _r in conversion)
    pending = int(re.search(r"(\d+) pending", OUT_DASHBOARD).group(1))
    declined = int(re.search(r"declined, never priced\s+(\d+)", OUT_DASHBOARD).group(1))
    priced = sum(n for _b, n in bands)
    # every prose figure below is read back out of a captured run, so a re-tariff cannot leave prose behind
    thresh = [int(n) for n in re.findall(r"^\s+> threshold, run \d\s+(\d+)", OUT_COLLECTIONS, re.M)]
    nominal = int(re.search(r"Count (\d+), FindAll", OUT_COLLECTIONS).group(1))
    prem_by_class = dict(re.findall(r"^\s+(Class\w+)\s+([\d,]+)$", OUT_DASHBOARD, re.M))
    makes = re.findall(r"^\s+\d\. (\w+)\s+(\d+)$", OUT_DASHBOARD, re.M)
    makes_sentence = ", ".join(f"{m} {n}" for m, n in makes[:-1]) + f" and {makes[-1][0]} {makes[-1][1]}"
    vb_sum = re.search(r"accepted\s+(\d+) quotes, ([\d,]+) THB, largest ([\d,]+)", OUT_VB).groups()
    vb_window = re.findall(r"^\s+(Q-\d+)\s+([\d,.]+)$", OUT_VB, re.M)
    # the first premium the window prints twice, and the two quote ids that share it — stable-sort evidence
    tie_amount = next(a for i, (_q, a) in enumerate(vb_window) if a == vb_window[i + 1][1])
    tie_ids = [q for q, a in vb_window if a == tie_amount]

    projects = sorted(p for p in (REPO / L).glob("*/*.*proj"))
    loc_by_project = []
    for p in projects:
        srcs = [f.relative_to(REPO).as_posix() for f in p.parent.rglob("*")
                if f.suffix in (".cs", ".vb") and not ({"obj", "bin"} & set(f.parts))]
        loc_by_project.append((p.stem.removeprefix("L04."), loc(*srcs)))
    loc_total = sum(n for _p, n in loc_by_project)
    tests_qgen, tests_data = test_cases(QGEN_T), test_cases(DATA_T)
    tests_total = tests_qgen + tests_data
    n_proj = len(projects)
    loc_vb_queries = loc(VB)
    sizes = dict(loc_by_project)
    biggest = max(loc_by_project, key=lambda x: x[1])
    loc_tests = sizes["QueryGen.Tests"] + sizes["QuoteData.Tests"]
    loc_libs = sizes["QueryGen"] + sizes["QuoteData"]

    family_cards = [
        {"num": 1, "title": "List<T> — the default mutable list", "tags": [T_CS, T_JVM], "pills": [SAME],
         "what": "A growable array: O(1) index, amortised O(1) append.",
         "lines": [("Java", "<code>ArrayList&lt;E&gt;</code>"),
                   ("Kotlin", "<code>MutableList</code> / <code>ArrayList</code>"),
                   ("TS", "<code>Array&lt;T&gt;</code>"),
                   ("Watch", "Adding inside <code>foreach</code> throws <code>InvalidOperationException</code> "
                             "(3.4) — Java's <code>ConcurrentModificationException</code>")]},
        {"num": 2, "title": "Dictionary<TKey,TValue> and HashSet<T>", "tags": [T_CS], "pills": [TRAP],
         "what": "Hash map and hash set; iteration order is not part of the contract.",
         "lines": [("Java", "<code>HashMap</code> · <code>HashSet</code>"),
                   ("Kotlin", "<code>mutableMapOf</code> · <code>mutableSetOf</code>"),
                   ("Trap", "<code>dict[key]</code> on a missing key <b>throws</b> "
                            "<code>KeyNotFoundException</code> (4.4); Kotlin <code>map[key]</code> and Java "
                            "<code>get</code> return null — use <code>TryGetValue</code>"),
                   ("Ordered", "<code>OrderedDictionary&lt;TKey,TValue&gt;</code> is generic since .NET 9 "
                               "(" + NET9LIB + ")")]},
        {"num": 3, "title": "Arrays, Span<T> and ReadOnlySpan<T>", "tags": [T_CS], "pills": [DIFFERENT],
         "what": "Fixed-length arrays, and a stack-only window over an array, a string or stack memory.",
         "lines": [("Java", "<code>T[]</code> · a <code>ByteBuffer</code> slice"),
                   ("Span", "A <code>ref struct</code>: it cannot be a class field, be boxed or be captured by "
                            "a lambda (" + REFSTRUCT + ")"),
                   ("Use when", "Parsing and hot loops; not in domain models or LINQ pipelines"),
                   ("C# 14", "Arrays convert to spans implicitly — which changed LINQ overload binding (7.4)")]},
        {"num": 4, "title": "Immutable collections", "tags": [T_CS], "pills": [DIFFERENT],
         "what": "<code>ImmutableArray&lt;T&gt;</code>, <code>ImmutableList&lt;T&gt;</code>, "
                 "<code>ImmutableDictionary</code> — every change returns a new instance.",
         "lines": [("Java", "<code>List.copyOf</code> and Guava <code>ImmutableList</code> are unmodifiable: "
                             "<code>add</code> throws, where <code>ImmutableList.Add</code> returns a new list"),
                   ("Kotlin", "<code>kotlinx.collections.immutable</code> persistent collections: <code>add</code> returns a new one"),
                   ("Use when", "A snapshot shared across requests or threads"),
                   ("Trap", "A record compares an <code>ImmutableArray&lt;T&gt;</code> by array reference, "
                            "not by elements (5)"),
                   ("Sample", "<code>ToImmutableArray()</code> kept 2 items after the source list grew (2.3)")]},
        {"num": 5, "title": "Frozen collections (.NET 8)", "tags": [T_CS, T_ARCH], "pills": [DIFFERENT],
         "what": "<code>FrozenDictionary</code> and <code>FrozenSet</code>: pay once at creation, read faster "
                 "for the life of the process.",
         "lines": [("Java", "<code>Map.copyOf</code> · Guava <code>ImmutableMap</code> — immutable snapshots"),
                   ("Use when", "Start-up lookup tables read on every request: base rates by class, partner "
                                "endpoints, feature flags"),
                   ("Avoid", "Anything rebuilt per request — creation is the expensive part"),
                   ("Sample", "<code>baseRates</code> in <code>L04.Collections</code> is a "
                              "<code>FrozenDictionary&lt;CoverageClass, decimal&gt;</code> · " + NET8RT)]},
        {"num": 6, "title": "Read-only interfaces and wrappers", "tags": [T_CS, T_JVM], "pills": [TRAP],
         "what": "<code>IReadOnlyList&lt;T&gt;</code>, <code>AsReadOnly()</code>, <code>ReadOnlySet&lt;T&gt;</code> "
                 "(.NET 9) — views over data someone else can still change.",
         "lines": [("Kotlin", "<code>List&lt;T&gt;</code> over a <code>MutableList</code> — the same view "
                              "semantics"),
                   ("Java", "<code>Collections.unmodifiableList</code> — a view that throws on write"),
                   ("Trap", "A cast of the <code>IReadOnlyList&lt;T&gt;</code> view back to "
                            "<code>List&lt;T&gt;</code> compiles and mutates (2.3); the "
                            "<code>AsReadOnly()</code> wrapper refuses that cast"),
                   ("Trap", "<code>IList&lt;T&gt;</code> does not extend <code>IReadOnlyList&lt;T&gt;</code> "
                            "(" + ILIST + ")")]}]

    return [
        style_block(),
        {"type": "toc", "heading": "▤ Contents", "depth": 2,
         "note": "Page numbers are resolved from the rendered PDF. Code panels are cut from the compiled samples."},
        # a callout heading must not print alone at a page foot with its items on the next page (kit request)
        {"type": "html", "html": "<style>.callout { break-inside:avoid; page-break-inside:avoid; } "
                                 ".callout .ct { break-after:avoid; page-break-after:avoid; } "
                                 ".callout li:first-child { break-before:avoid; page-break-before:avoid; } "
                                 ".story .ct { break-after:avoid; page-break-after:avoid; } "
                                 ".story .ct + p { break-before:avoid; page-break-before:avoid; }</style>"},

        # ═══════════════════════════ 1 · WHY ═══════════════════════════
        # the 46-entry Contents fills page 1: start section 1 on page 2 instead of leaving a stub of it at the foot
        {"type": "html", "html": '<div style="break-before:page;page-break-before:always;height:0"></div>'},
        {"type": "story", "heading": "1 · Why collections and LINQ decide how .NET code reads",
         "html": (
             "<p><b>Most business C# is collection code: load some records, filter, group, aggregate, map to a "
             "response — and LINQ is the vocabulary every reviewer expects you to read at a glance.</b> You "
             "already think in pipelines: Java Streams and Collectors in Spring services, Kotlin collection "
             "operators, TypeScript array methods in NestJS and React, and a few hundred dashboard queries for a "
             "BI tool. Most operators map one-to-one. This lesson spends its words on the ones that do not.</p>"
             "<p><b>Three things do not transfer, and they are where production bugs come from.</b> A LINQ query "
             "over <code>IEnumerable&lt;T&gt;</code> is re-runnable and lazy, so it silently runs again every "
             "time it is enumerated. A lambda can compile to executable code <i>or</i> to a data structure a "
             "provider translates to SQL or a DynamoDB expression, depending only on the parameter type. And "
             "collection interfaces make promises — read-only, immutable, frozen — that are easy to confuse.</p>"
             "<p><b>You will build the tool you already built once in another language: a query generator.</b> "
             "The samples turn a C# predicate into a DynamoDB filter expression with <code>#name</code> and "
             "<code>:value</code> placeholders, run MotorQuote dashboard queries over a deterministic quote book, "
             "and repeat the dashboard in Visual Basic query syntax — the form you will meet in older estates.</p>")},

        {"type": "kpi", "heading": "1.1 · The numbers to leave this lesson with",
         "items": [
             {"label": "One query, three passes", "value": f"{calls['three passes']} calls", "tone": "red",
              "sub": "predicate calls over 240 quotes · measured"},
             {"label": "New in .NET 9 LINQ", "value": "3", "tone": "teal",
              "sub": "CountBy · AggregateBy · Index · verified"},
             {"label": "VB-only query clauses", "value": "6", "tone": "violet",
              "sub": "no C# query keyword · verified"},
             {"label": "DynamoDB IN list", "value": "≤ 100", "tone": "amber",
              "sub": "values per IN operator · verified"},
             {"label": "Lesson 04 samples", "value": f"{loc_total} lines", "tone": "navy",
              "sub": f"{n_proj} projects · {tests_total} tests · measured"}]},

        legend(T_CS, T_JVM, T_ARCH),

        {"type": "callout", "variant": "info", "heading": "ℹ Before you start",
         "items": [
             "<b>You need " + ref(2) + " and " + ref(3) + ".</b> Records, <code>with</code>, generics and "
             "extension methods are used here without explanation; LINQ operators <i>are</i> extension methods "
             "on <code>IEnumerable&lt;T&gt;</code>.",
             "<b>You will build seven projects.</b> <code>L04.QuoteData</code> (MotorQuote records, a "
             "deterministic 240-quote book, dashboard queries, rating rules as functions), "
             "<code>L04.QueryGen</code> (expression tree → DynamoDB filter), two C# consoles "
             "(<code>L04.Collections</code>, <code>L04.QuoteAnalytics</code>), a VB console "
             "(<code>L04.VbLinq</code>) and two xUnit projects. The rating rules are the track's one illustrative "
             "tariff — the same base rates, loadings, no-claim ladder and rounding every lesson that prices a "
             "MotorQuote quote uses, so the figures here and in " + ref(2) + " agree.",
             "<b>The dataset is an analytics row, not the " + ref(3) + " entity.</b> Every query here is a read, so "
             "<code>Quote</code> is a <code>record</code> and <code>QuoteId</code> / <code>PolicyNumber</code> are "
             "flattened to <code>string</code> — the shape a dashboard row and a DynamoDB item actually have. "
             + ref(3) + " owns the type-kind decision itself (an entity with identity is a <code>sealed class</code>; "
             "an id is a <code>readonly record struct</code>), and this lesson does not overturn it.",
             "<b>Not here:</b> <code>IAsyncEnumerable&lt;T&gt;</code> is " + ref(5) + "; how EF Core "
             "translates <code>IQueryable</code> to SQL is " + ref(9) + "; VB language semantics in depth are "
             + ref(6) + ".",
             "Facts that change with releases are marked " + VERIFIED + " and link to the source; figures computed "
             "from the samples are " + MEASURED + "; Java, Kotlin and TypeScript panels are for comparison and "
             "are not compiled."]},

        # ═══════════════════════════ 2 · COLLECTIONS ═══════════════════════════
        {"type": "story", "heading": "2 · The collection family — what to accept, store and return",
         "html": (
             "<p><b>Pick a collection type by the promise it makes to the caller, not by the data it holds.</b> "
             "<code>IEnumerable&lt;T&gt;</code> promises only that you can iterate — perhaps lazily, perhaps "
             "expensively. <code>IReadOnlyList&lt;T&gt;</code> promises a count and an indexer over data that "
             "already exists. <code>ImmutableArray&lt;T&gt;</code> and <code>FrozenDictionary&lt;TKey,TValue&gt;</code> "
             "promise that nothing will change. Kotlin's read-only <code>List&lt;T&gt;</code> is the "
             "<code>IReadOnlyList&lt;T&gt;</code> idea; Java has no read-only interface, only wrappers that "
             "throw.</p>"
             "<p><b>Read-only is a view; immutable is a guarantee.</b> In 2.3 one list is exposed four ways and "
             "then grows. The interface view and the <code>AsReadOnly()</code> wrapper see the new item; the "
             "immutable and frozen copies do not. A caller holding the <code>IReadOnlyList&lt;T&gt;</code> view "
             "can even cast it back to <code>List&lt;T&gt;</code> and remove an item — it compiles. The "
             "<code>AsReadOnly()</code> wrapper is a different type, so that cast fails; it still cannot stop the "
             "owner's changes.</p>"
             "<p><b>The two interface families are separate.</b> <code>IList&lt;T&gt;</code> extends "
             "<code>ICollection&lt;T&gt;</code> and <code>IEnumerable&lt;T&gt;</code> only — not "
             "<code>IReadOnlyList&lt;T&gt;</code> (" + ILIST + "). Concrete types such as <code>List&lt;T&gt;</code>, "
             "arrays and <code>ImmutableArray&lt;T&gt;</code> implement both, so a method that asks for "
             "<code>IReadOnlyList&lt;T&gt;</code> accepts all of them.</p>"
             "<p><b>Collection expressions are one literal syntax for all of them.</b> C# 12 (November 2023, "
             + CSHIST + ") added <code>[a, b, .. rest]</code>, which converts to arrays, spans, "
             "<code>List&lt;T&gt;</code>, immutable types and the collection interfaces. For an interface target "
             "the compiler chooses the concrete type (" + COLLEXPR + "): the sample's "
             "<code>IReadOnlyList&lt;string&gt;</code> is <i>not</i> a <code>List&lt;string&gt;</code>.</p>")},

        {"type": "mermaid", "inline": True,
         "heading": "2.1 · Two interface families — what each type promises",
         "caption": "indigo = interfaces · green = concrete types · solid arrow = extends · dotted arrow = implements · "
                    "IList<T> and IReadOnlyList<T> are unrelated · arrays and AsReadOnly() wrappers implement both "
                    "families too",
         "code": ("classDiagram\n"
                  "  direction RL\n"
                  "  class IEnumerable~T~:::iface {\n    <<interface>>\n    GetEnumerator()\n  }\n"
                  "  class IReadOnlyCollection~T~:::iface {\n    <<interface>>\n    Count\n  }\n"
                  "  class IReadOnlyList~T~:::iface {\n    <<interface>>\n    this[i] get\n  }\n"
                  "  class ICollection~T~:::iface {\n    <<interface>>\n    Add() Remove() Clear()\n  }\n"
                  "  class IList~T~:::iface {\n    <<interface>>\n    this[i] get set\n    Insert() RemoveAt()\n  }\n"
                  "  class List~T~:::impl {\n    Add() changes it in place\n  }\n"
                  "  class ImmutableArray~T~:::impl {\n    Add() returns a new array\n  }\n"
                  "  IReadOnlyCollection~T~ --|> IEnumerable~T~\n"
                  "  IReadOnlyList~T~ --|> IReadOnlyCollection~T~\n"
                  "  ICollection~T~ --|> IEnumerable~T~\n"
                  "  IList~T~ --|> ICollection~T~\n"
                  "  List~T~ ..|> IReadOnlyList~T~\n"
                  "  List~T~ ..|> IList~T~\n"
                  "  ImmutableArray~T~ ..|> IReadOnlyList~T~\n"
                  "  ImmutableArray~T~ ..|> IList~T~\n"
                  "  classDef iface fill:#e0e7ff,color:#1f2937,stroke:#6366f1\n"
                  "  classDef impl fill:#dcfce7,color:#1f2937,stroke:#16a34a\n")},

        listed(code(from_sample(COLL, "collection-expressions"),
                    heading="2.2 · Collection expressions — one literal for every target",
                    note="<b>The spread <code>..</code> inlines any enumerable, including a LINQ query.</b> "
                         "The output is <code>Toyota, Honda, Isuzu, Toyota</code> and <code>6 elements</code>. "
                         "The last two lines print <code>False</code> and <code>&lt;&gt;z__ReadOnlyArray`1</code>: for an "
                         "<code>IReadOnlyList&lt;T&gt;</code> target this compiler synthesised its own read-only "
                         "type, so a caller cannot cast it to <code>List&lt;T&gt;</code> and add. The type name "
                         "is a compiler detail, not a contract. Unlike a LINQ query, a collection expression is "
                         "always evaluated into memory immediately (" + COLLEXPR + ")."),
               "2.2 · Collection expressions — one literal for every target"),

        listed(compare(half(from_sample(COLL, "readonly-views", label="C# · four views")),
                       captured(part(OUT_COLLECTIONS, 2), "Output · part 2", file="L04.Collections, captured"),
                       heading="2.3 · Read-only is not immutable",
                       note="<b>Only the copies are safe from the owner.</b> <code>view</code> is the same "
                            "object as <code>classes</code>, and <code>AsReadOnly()</code> wraps it live, so both "
                            "report 3 after the <code>Add</code>. <code>ToImmutableArray()</code> and "
                            "<code>ToFrozenSet()</code> copied, so they report 2. The last line shows why "
                            "“read-only” is a courtesy: the cast back to <code>List&lt;string&gt;</code> removed "
                            "an item through the view. The same cast on <code>wrapper</code> would throw "
                            "<code>InvalidCastException</code>, but the wrapper still shows every later change. "
                            "Return <code>IReadOnlyList&lt;T&gt;</code> from APIs, but hand out an immutable "
                            "copy when the caller must not see — or cause — changes."),
               "2.3 · Read-only is not immutable"),

        {"type": "cards",
         "band": {"title": "2.4 · The collection family, mapped from your stack", "note": "types you will review",
                  "tone": "violet"},
         "cards": family_cards[:3]},
        {"type": "cards", "toc": False,
         "band": {"title": "2.4 · The collection family (continued)", "note": "types you will review",
                  "tone": "violet"},
         "cards": family_cards[3:]},

        figure_heading("2.5 · Choosing the type at an API boundary"),
        {"type": "table",
         "cols": ["Position", "Use", "Why", "Habit it replaces"],
         "rows": [
             ["Parameter you only iterate", "<code>IEnumerable&lt;T&gt;</code>",
              "Accepts arrays, lists and queries; enumerate it <b>once</b>", "<code>Iterable&lt;T&gt;</code>"],
             ["Parameter you count or index", "<code>IReadOnlyList&lt;T&gt;</code>",
              "No defensive copy, no second enumeration", "Kotlin <code>List&lt;T&gt;</code>"],
             ["Result of a query method", "<code>IReadOnlyList&lt;T&gt;</code>, materialised",
              "The caller cannot re-run your query by accident (3.2)", "<code>stream().toList()</code>"],
             ["A lazy stream you produce", "<code>IEnumerable&lt;T&gt;</code> iterator; "
              "<code>IAsyncEnumerable&lt;T&gt;</code> for I/O — " + ref(5),
              "Say it is lazy in the name or the doc comment", "Kotlin <code>Sequence</code> · <code>Flow</code>"],
             ["Snapshot shared across requests", "<code>ImmutableArray&lt;T&gt;</code>, "
              "<code>ImmutableDictionary</code>", "Changes return a new instance", "Guava immutable collections"],
             ["Built once, read on every request", "<code>FrozenDictionary</code>, <code>FrozenSet</code>",
              "Read-optimised; creation costs more", "a <code>static final Map</code>"],
             ["Private working state", "<code>List&lt;T&gt;</code>, <code>Dictionary&lt;TKey,TValue&gt;</code>",
              "Fastest to fill; never exposed", "<code>ArrayList</code>, <code>HashMap</code>"],
             ["Hot loop over a buffer", "<code>Span&lt;T&gt;</code>, <code>ReadOnlySpan&lt;T&gt;</code>",
              "No allocation; stack-only", "<code>ByteBuffer</code>"]]},

        # ═══════════════════════════ 3 · DEFERRED EXECUTION ═══════════════════════════
        {"type": "story", "heading": "3 · Deferred execution — a query is a recipe, not a result",
         "html": (
             "<p><b>A LINQ query over <code>IEnumerable&lt;T&gt;</code> runs every time you enumerate it, and "
             "nothing stops you enumerating it twice.</b> A Java <code>Stream</code> should be operated on only "
             "once and may throw <code>IllegalStateException</code> when reused (" + JSTREAM + "). Kotlin sequences "
             "can be iterated many times (" + KSEQ + "), and LINQ follows Kotlin: reuse is legal, silent and "
             "re-executes every step. In the sample a <code>Count()</code>, a <code>First()</code> and a "
             "<code>foreach</code> over one query called its predicate <b>" + str(calls["three passes"]) + "</b> "
             "times for 240 quotes; <code>ToList()</code> once, then three reads, called it "
             + str(calls["ToList + 3 reads"]) + " times.</p>"
             "<p><b>Materialise at the boundary.</b> <code>ToList</code>, <code>ToArray</code>, "
             "<code>ToDictionary</code> and <code>ToLookup</code> execute immediately and keep the results; "
             "<code>Count</code>, <code>First</code> and <code>Sum</code> execute immediately and keep nothing; "
             "<code>Where</code> and <code>Select</code> are deferred and streaming; <code>GroupBy</code> and "
             "<code>OrderBy</code> are deferred but read the whole source each time they run (" + LINQEXEC + "). "
             "A repository or service method that returns a deferred query hands its cost — and, with EF Core, "
             "its open context — to every caller; " + ref(9) + " covers that case.</p>"
             "<p><b>Deferred also means late.</b> A query reads captured variables and the source collection "
             "when it is enumerated, not when it is written: raising a threshold after declaring the query "
             "changed its count from " + str(thresh[0]) + " to " + str(thresh[1]) + ". Changing a "
             "<code>List&lt;T&gt;</code> while a <code>foreach</code> "
             "walks it throws <code>InvalidOperationException</code>, as Java throws "
             "<code>ConcurrentModificationException</code>.</p>"
             "<p><b><code>yield return</code> is how you write your own lazy sequence.</b> The compiler rewrites "
             "the method into a state machine whose body does not start until the first <code>MoveNext</code> — "
             "the output prints <i>iterator created</i> before <i>(iterator body starts)</i>. Kotlin's "
             "<code>sequence { yield(x) }</code> is the same idea with a different keyword.</p>")},

        {"type": "mermaid", "inline": True,
         "heading": "3.1 · What runs when — one query, four calls",
         "caption": "the predicate count after each step is the sample's measured output · ToList is the only "
                    "call whose result is kept · colours only separate the actors (indigo) from the summary "
                    "note (amber)",
         "code": ('%%{init: {"theme":"base","themeVariables": {"actorBkg":"#e0e7ff","actorBorder":"#6366f1",'
                  '"actorTextColor":"#1f2937","noteBkgColor":"#fef3c7","noteTextColor":"#1f2937",'
                  '"noteBorderColor":"#d97706","signalColor":"#334155","signalTextColor":"#1f2937",'
                  '"loopTextColor":"#1f2937","labelBoxBkgColor":"#ccfbf1","labelTextColor":"#1f2937"},'
                  '"sequence": {"mirrorActors": false, "messageMargin": 16, "boxMargin": 4, "noteMargin": 4, '
                  '"actorMargin": 190, "width": 170}}}%%\n'
                  "sequenceDiagram\n"
                  "  participant C as Your code\n"
                  "  participant Q as quotes.Where(Counted)\n"
                  "  participant P as Counted(q)\n"
                  "  C->>Q: declare · nothing runs, calls = 0\n"
                  "  C->>Q: Count()\n"
                  "  Q->>P: 240 calls\n"
                  "  C->>Q: First()\n"
                  "  Q->>P: 2 calls, stops at Q-0002\n"
                  "  C->>Q: foreach\n"
                  "  Q->>P: 240 calls again\n"
                  "  Note over C,P: 482 calls, and no result was kept\n"
                  "  C->>Q: ToList()\n"
                  "  Q->>P: 240 calls, once\n"
                  f"  Q-->>C: List of {accepted} quotes · reads call nothing\n")},

        listed(compare(from_text("""
            // a Stream is single-use: reuse throws
            int[] calls = {0};  // lambdas capture effectively final
            Stream<Quote> accepted = quotes.stream()
                .filter(q -> { calls[0]++; return q.isAccepted(); });

            long count = accepted.count();      // runs the pipeline
            accepted.findFirst();
            // IllegalStateException: stream has already
            // been operated upon or closed

            // to read results more than once, collect first
            List<Quote> list = quotes.stream()
                .filter(Quote::isAccepted)
                .toList();
            """, "java", file="the habit you bring"),
                       half(from_sample(COLL, "deferred")),
                       heading="3.2 · Reusing a query — Java Streams vs LINQ",
                       note="<b>Java fails loudly on reuse; C# re-runs quietly.</b> Both pipelines are lazy, but "
                            "a LINQ query is an <code>IEnumerable&lt;T&gt;</code> that starts over on every "
                            "enumeration. The C# panel printed <code>calls = 0</code>, then "
                            f"<code>calls = {calls['three passes']}</code>, then "
                            f"<code>calls = {calls['ToList + 3 reads']}</code>. Against a database or a remote "
                            "API, “quietly re-runs” means three round trips. Analyzer rule CA1851 flags possible "
                            "multiple enumeration, but it is off by default (" + CA1851 + ")."),
               "3.2 · Reusing a query — Java Streams vs LINQ"),

        {"type": "chart", "heading": "3.3 · Predicate calls for the same three reads",
         "kind": "bar",
         "args": {"data": [("declared, not run", calls["declared"]), ("Count + First + foreach", calls["three passes"]),
                           ("ToList, then 3 reads", calls["ToList + 3 reads"])],
                  "ylabel": "predicate calls", "tone": "red", "width": 620, "height": 150},
         "caption": "calls counted by the sample over the 240-quote book · measured from a real run",
         "note": f"<b>Materialising turns three passes into one.</b> {calls['three passes']} = 240 for "
                 "<code>Count</code> + 2 for <code>First</code>, which stops at Q-0002, + 240 for the "
                 "<code>foreach</code>. " + MEASURED + " from <code>L04.Collections</code>, and asserted by a test "
                 "in <code>L04.QuoteData.Tests</code>."},

        listed(compare(half(from_sample(COLL, "captured", label="C# · captured")),
                       half(from_sample(COLL, "modified", label="C# · changed list")),
                       heading="3.4 · Deferred means late: captured variables and changing sources",
                       note="<b>The lambda captured the variable <code>threshold</code>, not its value.</b> The "
                            f"same query printed <code>{thresh[0]}</code>, then <code>{thresh[1]}</code> after the "
                            "assignment. On the "
                            "right, <code>Add</code> during enumeration prints "
                            "<code>InvalidOperationException</code>: <code>List&lt;T&gt;</code> enumerators check a "
                            "version number, like Java's fail-fast iterators. Iterate a copy "
                            "(<code>queue.ToList()</code>) when the loop must change the source."),
               "3.4 · Deferred means late: captured variables and changing sources"),

        listed(compare(from_text("""
            fun renewals(inception: LocalDate) = sequence {
                println("  (sequence body starts)")
                var d = inception
                while (true) {
                    yield(d)
                    d = d.plusYears(1)
                }
            }

            val renewals = renewals(LocalDate.of(2026, 11, 1))
            println("  sequence created")
            renewals.take(3).forEach { println("  renewal $it") }
            """, "kotlin", file="sequence builder"),
                       half(from_sample(COLL, "yield")),
                       heading="3.5 · Writing a lazy sequence — Kotlin sequence {} vs C# yield return",
                       note="<b>Same model, different keyword.</b> Both produce an infinite, lazy sequence of "
                            "renewal dates, and <code>Take(3)</code> stops it after three. The C# run printed "
                            "<code>iterator created</code> <i>before</i> <code>(iterator body starts)</code>: "
                            "calling <code>Renewals</code> only builds the state machine. A consequence to "
                            "remember — argument checks at the top of an iterator method also run late, on the "
                            "first <code>MoveNext</code>, not at the call."),
               "3.5 · Writing a lazy sequence — Kotlin sequence {} vs C# yield return"),

        # ═══════════════════════════ 4 · OPERATOR MAP ═══════════════════════════
        {"type": "story", "heading": "4 · The operator map — Streams, Kotlin and TypeScript in LINQ",
         "html": (
             "<p><b>Most of LINQ is the pipeline you know under SQL-flavoured names.</b> <code>filter</code> is "
             "<code>Where</code>, <code>map</code> is <code>Select</code>, <code>flatMap</code> is "
             "<code>SelectMany</code>, <code>reduce</code>/<code>fold</code> is <code>Aggregate</code>. The query "
             "syntax (<code>from q in quotes where … select …</code>) compiles to the same method calls, and it "
             "covers only a handful of operators — everything else must be written as a method call "
             "(" + SQO + "). Most C# teams write method syntax and keep query syntax for joins and nested "
             "<code>from</code> clauses; 6.2 shows the same left join in both forms.</p>"
             "<p><b>Most operators added since .NET 6 are ones Kotlin had first — and code you review may "
             "predate them.</b> .NET 6 added <code>Chunk</code>, <code>DistinctBy</code>, <code>MinBy</code> and "
             "<code>MaxBy</code> (" + NET6 + "). .NET 9 added <code>CountBy</code> and <code>AggregateBy</code>, "
             "which aggregate by key without allocating the groups <code>GroupBy</code> builds, and "
             "<code>Index</code> (" + NET9LIB + "); like every LINQ operator that returns a sequence they are "
             "deferred. .NET 10 added <code>LeftJoin</code> and <code>RightJoin</code> — SQL's joins, not "
             "Kotlin's — replacing the <code>GroupJoin</code> + <code>DefaultIfEmpty</code> idiom; neither has "
             "query syntax (" + JOINS + "). It also added <code>Shuffle</code> and "
             "<code>InfiniteSequence</code> (" + SHUFFLE + " · " + INFSEQ + ") and ships "
             "<code>System.Linq.AsyncEnumerable</code> in the platform, replacing the community "
             "<code>System.Linq.Async</code> package (" + ASYNCENUM + ") — " + ref(5) + ".</p>"
             "<p><b>Know which operators execute now and which fail on a missing key.</b> <code>ToLookup</code> "
             "runs immediately and <code>GroupBy</code> is deferred — the test "
             "<code>GroupBy_is_deferred_and_ToLookup_is_immediate</code> counts the key selector at 0, 240 and "
             "720. A lookup returns an empty group for a key it has never seen; a dictionary indexer throws.</p>")},

        mapping("4.1 · Concept map — pipelines you know → LINQ", [
            ("<code>filter</code> · <code>arr.filter</code>", "<code>Where</code>", "renamed",
             "Deferred and streaming"),
            ("<code>map</code> · <code>arr.map</code>", "<code>Select</code>", "renamed",
             "<code>Select((x, i) =&gt; …)</code> passes the index"),
            ("<code>flatMap</code>", "<code>SelectMany</code>", "renamed", "Also a second <code>from</code> in query syntax"),
            ("<code>reduce</code> / <code>fold</code>", "<code>Aggregate</code>", "renamed",
             "Without a seed it throws on an empty sequence"),
            ("<code>Collectors.groupingBy</code> · Kotlin <code>groupBy</code>", "<code>GroupBy</code> / "
             "<code>ToLookup</code>", "trap",
             "<code>GroupBy</code> is deferred and regroups on every enumeration; Kotlin's <code>groupBy</code> "
             "returns a map immediately — that is <code>ToLookup</code>"),
            ("<code>groupingBy(counting())</code> · Kotlin <code>eachCount()</code>", "<code>CountBy</code> (.NET 9)",
             "trap", "Deferred: it recounts on every enumeration and yields pairs, not a map — add "
             "<code>ToDictionary()</code> where Kotlin gave you a <code>Map</code>; no row for an absent key"),
            ("Kotlin <code>groupingBy { }.fold</code>", "<code>AggregateBy</code> (.NET&nbsp;9)", "trap",
             "Deferred like <code>CountBy</code>: one accumulator per key, no intermediate groups, rebuilt on "
             "every enumeration; Kotlin's <code>fold</code> returns a <code>Map</code> at once"),
            ("Kotlin <code>withIndex()</code> · <code>arr.entries()</code>", "<code>Index()</code> (.NET 9)",
             "renamed", "Yields <code>(Index, Item)</code> tuples"),
            ("Kotlin <code>chunked(n)</code>", "<code>Chunk(n)</code> (.NET 6)", "renamed",
             "Each chunk is an array; the last one holds the remainder"),
            ("Kotlin <code>distinctBy</code>", "<code>DistinctBy</code> (.NET 6)", "same",
             "Compares by a key without sorting; older code emulates it with <code>GroupBy</code> + "
             "<code>First</code>"),
            ("Kotlin <code>maxByOrNull</code>", "<code>MaxBy</code> (.NET 6)", "trap",
             "On an empty sequence <code>MaxBy</code> returns null only for reference types; for structs "
             "(including <code>CountBy</code>'s <code>KeyValuePair</code> rows) it throws "
             "<code>InvalidOperationException</code>"),
            ("Kotlin <code>zip</code> · Guava <code>Streams.zip</code>", "<code>Zip</code>", "renamed",
             "Stops at the shorter sequence; the overload without a result selector yields tuples"),
            ("<code>Collectors.toMap</code> · Kotlin <code>associateBy</code>", "<code>ToDictionary</code>", "trap",
             "Duplicate keys throw <code>ArgumentException</code>, as <code>toMap</code> throws "
             "<code>IllegalStateException</code>; Kotlin's <code>associateBy</code> keeps the last one"),
            ("<code>map.get(key)</code> returning null", "<code>dict[key]</code> · <code>lookup[key]</code>", "trap",
             "The dictionary indexer throws <code>KeyNotFoundException</code>; a lookup returns an empty group"),
            ("SQL <code>LEFT JOIN</code>", "<code>LeftJoin</code> (.NET 10)", "different",
             "Before .NET 10: <code>GroupJoin</code> + <code>SelectMany</code> + <code>DefaultIfEmpty</code>"),
            ("Stream single use", "Re-enumerable <code>IEnumerable&lt;T&gt;</code>", "trap",
             "Every enumeration re-runs the whole pipeline (3.2)"),
            ("<code>toList()</code> · spread into an array", "<code>ToList()</code> · <code>ToArray()</code>",
             "same", "The point where the query actually runs"),
            ("Kotlin <code>sequence { yield() }</code>", "<code>yield return</code>", "renamed",
             "The method body starts on the first <code>MoveNext</code>"),
            ("<code>parallelStream()</code>", "PLINQ <code>AsParallel()</code>", "different",
             "<code>AsParallel()</code> partitions an <i>in-memory</i> sequence across the thread pool, and "
             "<code>AsOrdered()</code> buys the original order back at a cost. This track does not cover PLINQ; "
             + ref(5) + " covers Task-based parallelism (<code>Task.WhenAll</code>, "
             "<code>Parallel.ForEachAsync</code>), which is what I/O-bound fan-out needs instead"),
        ]),

        {"type": "mermaid", "inline": True,
         "heading": "4.2 · When each feature arrived — dating the LINQ in a codebase",
         "caption": "language features and library operators by release year · C# 12 shipped with .NET 8 and "
                    "C# 14 with .NET 10 · colours only separate the releases · verified against the C# history, "
                    "the .NET what's-new pages and the API reference",
         "code": ('%%{init: {"theme":"base","themeVariables": {"cScale0":"#e0e7ff","cScale1":"#e2e8f0",'
                  '"cScale2":"#fde68a","cScale3":"#ccfbf1","cScale4":"#fce7f3","cScale5":"#dcfce7",'
                  '"cScaleLabel0":"#1f2937","cScaleLabel1":"#1f2937","cScaleLabel2":"#1f2937",'
                  '"cScaleLabel3":"#1f2937","cScaleLabel4":"#1f2937","cScaleLabel5":"#1f2937",'
                  '"fontSize":"19px"}}}%%\n'
                  "timeline\n"
                  "  2005 : C#35; 2 · iterators\n"
                  "  2007 : C#35; 3 · LINQ : lambdas and expression trees\n"
                  "  2021 : .NET 6 · Chunk : DistinctBy, MinBy, MaxBy\n"
                  "  2023 : .NET 8 · frozen collections : C#35; 12 · collection expressions\n"
                  "  2024 : .NET 9 · CountBy : AggregateBy, Index\n"
                  "  2025 : .NET 10 · LeftJoin : Shuffle, AsyncEnumerable : C#35; 14 · span conversions\n")},

        listed(code(from_sample(DASH, "net9-additions"),
                    heading="4.3 · AggregateBy — a fold per key without building groups",
                    note="<b>This is Kotlin's <code>groupingBy { }.fold</code>.</b> One pass keeps one running "
                         "total per coverage class; <code>GroupBy</code> would first collect every quote into a "
                         "group and then sum each group. The dashboard prints <code>Class1 "
                         + prem_by_class["Class1"] + "</code> … <code>Class3 " + prem_by_class["Class3"]
                         + "</code> THB (the canonical tariff, illustrative). Like <code>CountBy</code> it "
                         "returns a deferred sequence of <code>KeyValuePair</code>s that is rebuilt on every "
                         "enumeration (the test <code>CountBy_and_AggregateBy_are_deferred…</code> counts it), "
                         "so sort explicitly when order matters and add <code>ToList()</code> or "
                         "<code>ToDictionary()</code> to keep the result."),
               "4.3 · AggregateBy — a fold per key without building groups"),

        listed(compare(half(from_sample(COLL, "missing-key", label="C# · missing key")),
                       captured(part(OUT_COLLECTIONS, 9), "Output · part 9", file="L04.Collections, captured"),
                       heading="4.4 · A key that is not there — lookup vs dictionary",
                       note="<b>Two grouped structures, two answers to a missing key.</b> The "
                            "<code>ILookup</code> from <code>ToLookup</code> returns an empty sequence for "
                            "<code>Tesla</code>; the dictionary built from <code>CountBy</code> throws "
                            "<code>KeyNotFoundException</code>. Kotlin and Java return null from "
                            "<code>map[key]</code>/<code>get</code>, so ported code that null-checks the result "
                            "crashes instead. Use <code>TryGetValue</code> or <code>GetValueOrDefault</code>."),
               "4.4 · A key that is not there — lookup vs dictionary"),

        # ═══════════════════════════ 5 · FUNCTIONAL C# ═══════════════════════════
        {"type": "story", "heading": "5 · Functional C# — delegates, closures and immutable records",
         "html": (
             "<p><b>A C# lambda becomes a delegate, and delegate types are nominal, not structural.</b> In Kotlin "
             "and TypeScript any function with the right shape fits a function type. In C#, "
             "<code>Func&lt;Quote, bool&gt;</code> and <code>Predicate&lt;Quote&gt;</code> have the same shape and "
             "still do not convert — the compiler reports CS0029, and the sample converts through "
             "<code>.Invoke</code> instead. Use <code>Func</code> and <code>Action</code> everywhere, and declare "
             "a named delegate only where the name documents intent, as <code>Loading</code> does below "
             "(" + LAMBDAS + ").</p>"
             "<p><b>Rules as values is the functional shape of a rating engine.</b> Each loading rule is a named "
             "function in a list, and the total loading is a fold of those rules into one number, which the base "
             "premium is then multiplied by: no mutable state, same input, same output. That is what makes the "
             "rules trivially testable — the young-driver theory asserts a pure function — and easy to reorder or "
             "extend. Because the loadings are <i>added</i> before they are applied, the order of the list cannot "
             "change the answer, which is a property worth having in a tariff.</p>"
             "<p><b>Closures capture variables, not values — and C#'s two loops differ.</b> A <code>for</code> "
             "loop has one loop variable shared by every lambda created in it, so three lambdas print "
             "<code>3,3,3</code>; a <code>foreach</code> gets a fresh variable per iteration and prints "
             "<code>0,1,2</code>. TypeScript's <code>for (let …)</code> creates a fresh binding per iteration, so "
             "the TypeScript habit is exactly wrong for a C# <code>for</code> loop. A <code>static</code> lambda "
             "cannot capture at all, which makes the intent explicit.</p>"
             "<p><b>Immutability comes from records and <code>with</code> — shallow, like Kotlin's "
             "<code>copy()</code>.</b> <code>with</code> copies the reference to a <code>List&lt;string&gt;</code>, "
             "so the renewal and the draft share one list. A record meant to be a value can hold an "
             "<code>ImmutableArray&lt;T&gt;</code> or another immutable collection, which stops the mutation "
             "— but not the surprise in equality: record equality compares an <code>ImmutableArray&lt;T&gt;</code> "
             "by its array reference, so two records with the same elements in separate arrays are "
             "<i>not</i> equal (the test <code>A_record_holding_an_ImmutableArray…</code> proves it). Override "
             "<code>Equals</code> with <code>SequenceEqual</code> when a record must compare by content. "
             "Records themselves are " + ref(3) + ".</p>")},

        listed(code(from_sample(RATING, "rules-as-functions"),
                    heading="5.1 · Rating rules as a list of functions, folded with Aggregate",
                    note="<b>Read the fold as <code>rules.fold(0m) { loading, rule -&gt; loading + rule(r) }</code>.</b> "
                         "<code>Loading</code> is a named delegate type; each tuple pairs a rule name with a "
                         "lambda. The collection expression builds an <code>IReadOnlyList</code> of tuples. "
                         "Adding a fleet-size rule is one more line, and every rule can be tested alone: "
                         "<code>Rating.Rules.Single(r =&gt; r.Name == \"young driver\").Rate</code>. These are the "
                         "rules " + ref(2) + " wrote as <code>switch</code> expressions, re-expressed as values — "
                         "the track's one illustrative tariff, not a real one; three claims in five years is a "
                         "decline rather than a loading, which section 6 counts as a "
                         "<code>QuoteStatus</code>."),
               "5.1 · Rating rules as a list of functions, folded with Aggregate"),

        listed(compare(from_text("""
            const byLet: Array<() => number> = [];
            for (let i = 0; i < 3; i++)
              byLet.push(() => i);     // a fresh i per pass

            const byVar: Array<() => number> = [];
            for (var j = 0; j < 3; j++)
              byVar.push(() => j);     // ONE j, shared by all

            const run = (fs: Array<() => number>) =>
              fs.map(f => f()).join(",");

            console.log(run(byLet));   // 0,1,2
            console.log(run(byVar));   // 3,3,3
            """, "typescript", file="closures in loops"),
                       half(from_sample(COLL, "closures")),
                       heading="5.2 · Closures in loops — TypeScript let vs C# for",
                       note="<b>C#'s <code>for</code> behaves like TypeScript's <code>var</code>, not like "
                            "<code>let</code>.</b> The C# run printed <code>for 3,3,3</code> and "
                            "<code>foreach 0,1,2</code>. This bites in exactly the code you write in fan-out "
                            "loops: building a list of tasks or callbacks with an index. Copy the loop variable "
                            "into a local inside the body, or use <code>foreach</code> over a range."),
               "5.2 · Closures in loops — TypeScript let vs C# for"),

        listed(compare(half(from_sample(COLL, "delegate-types")), half(from_sample(COLL, "with-shallow")),
                       heading="5.3 · Delegates are nominal; with copies are shallow",
                       note="<b>Two small surprises for a Kotlin engineer.</b> Left: the commented line does not "
                            "compile (CS0029, checked on the build SDK); <code>isAccepted.Invoke</code> is a method "
                            "group that converts to any compatible delegate type. Both counts print "
                            + str(nominal) + ". Right: "
                            "the run printed <code>draft notes created | renewal</code> and "
                            "<code>same list? True</code> — changing the renewal's notes changed the draft's."),
               "5.3 · Delegates are nominal; with copies are shallow"),

        # ═══════════════════════════ 6 · QUOTE ANALYTICS ═══════════════════════════
        {"type": "story", "heading": "6 · Quote analytics — the dashboard habit in LINQ",
         "html": (
             "<p><b>A dashboard query is group, aggregate, order, project — whether it feeds a BI tool or a "
             "LINQ pipeline.</b> You have written a few hundred of them in SQL for a BI dashboard. Written in "
             "LINQ they are type-checked, refactorable with the domain model and unit-testable against a fixed "
             "dataset. <code>QuoteBook.Generate()</code> produces the same 240 MotorQuote quotes on every machine "
             "— vehicles, drivers, coverage classes and statuses derived arithmetically from the index — so every "
             "number below is reproducible.</p>"
             "<p><b>Prefer <code>CountBy</code> and <code>AggregateBy</code> when you need one number per "
             "key.</b> <code>GroupBy</code> is right when you need the members of each group or several "
             "aggregates at once, as the conversion query does (code in 8.1). <code>CountBy</code> emits no row "
             "for a key that has no items, so a dashboard that must show zero rows walks a fixed list and looks "
             "each key up — <code>BandOrder</code> in 6.1.</p>"
             "<p><b>Pin the numbers with a test.</b> <code>Dashboard_numbers_match_the_captured_lesson_output</code> "
             f"asserts the accepted counts, bands, top makes, premium totals and the {pending} policies still "
             "pending issuance. A changed rating rule fails a test before a chart silently changes — the "
             "discipline of a query review, enforced by <code>dotnet test</code>.</p>")},

        listed(code(from_sample(DASH, "premium-bands"),
                    heading="6.1 · Premium bands — a switch expression inside CountBy",
                    note="<b>The band is a pure function of the premium, so counting stays one line.</b> "
                         "<code>BandOf</code> uses relational patterns from " + ref(2) + "; <code>CountBy</code> "
                         "counts per band in one pass, and <code>ToDictionary()</code> keeps the counts. A band "
                         "with no quotes has no key, so <code>Bands</code> walks <code>BandOrder</code> and "
                         "<code>GetValueOrDefault</code> supplies the 0 — the test "
                         "<code>A_band_without_quotes_still_gets_a_row_with_zero</code> proves it. The method "
                         "returns a materialised list, the rule from 2.5."),
               "6.1 · Premium bands — a switch expression inside CountBy"),

        listed(compare(half(from_sample(DASH, "left-join", label="C# · LeftJoin, .NET 10")),
                       half(from_sample(DASH, "left-join-query", label="C# · query syntax")),
                       heading="6.2 · Issuance — LeftJoin, and the query-syntax left join it replaces",
                       note="<b>Both keep every accepted quote; a missing policy arrives as "
                            "<code>null</code>.</b> On the left, <code>LeftJoin</code> says it in one call. On the "
                            "right, <code>join … into issued</code> followed by "
                            "<code>from p in issued.DefaultIfEmpty()</code> is the query-syntax shape of a left "
                            "join — the <code>GroupJoin</code> + <code>DefaultIfEmpty</code> idiom you will meet in "
                            "code written before .NET 10 (" + JOINS + "). The selector's second parameter is "
                            "nullable either way, so "
                            f"<code>p?.PolicyNumber ?? Unset</code> is required, not defensive. The run reports "
                            f"{accepted} accepted and {pending} pending, and the test "
                            "<code>The_C_sharp_query_syntax_left_join_matches_LeftJoin</code> asserts the two "
                            "return the same sequence."),
               "6.2 · Issuance — LeftJoin, and the query-syntax left join it replaces"),

        listed(code(captured(from_line(OUT_DASHBOARD, "top makes"),
                             "Output — L04.QuoteAnalytics, after the conversion and band lines charted in 6.4–6.5"),
                    heading="6.3 · What the dashboard prints",
                    note="<b>Every figure here except the batch sizes and the lookup count is asserted by a "
                         "test.</b> The premiums come from the track's canonical tariff, which is illustrative. "
                         f"The ranking is {makes_sentence}; ties are still possible on another dataset, so the "
                         "query adds <code>ThenBy(kv =&gt; kv.Key)</code> to order them by name (code in 8.2). "
                         "<code>Chunk(100)</code> split the book into export batches of 100 + 100 + 40."),
               "6.3 · What the dashboard prints"),

        {"type": "chartrow", "charts": [
            {"heading": "6.4 · Conversion rate by coverage class", "kind": "bar",
             "args": {"data": [(c, r) for c, _q, _a, r in conversion], "ylabel": "% of quotes accepted",
                      "tone": "teal", "width": 390, "height": 210},
             "caption": "accepted ÷ quoted per class · the query is shown in 8.1 · measured from the sample's dashboard output",
             "note": f"<b>Acceptance rises as cover gets cheaper — {conversion[0][3]:.1f}% for Class 1 to "
                     f"{conversion[-1][3]:.1f}% for Class 3.</b> The dataset builds that gradient in on purpose, "
                     f"so the query has something to find: {accepted} of {quoted} quotes accepted overall. "
                     + MEASURED + ", illustrative data."},
            {"heading": "6.5 · Quotes per premium band", "kind": "bar",
             "args": {"data": bands, "ylabel": "quotes", "tone": "indigo", "width": 390, "height": 210},
             "caption": f"the {priced} priced quotes by total premium band, THB · the {declined} declined quotes "
                       "have no premium to band · measured from the sample's dashboard output",
             "note": f"<b>The 6k–9k band holds {dict(bands)['6k-9k']} quotes; &lt; 3k holds "
                     f"{dict(bands)['< 3k']}.</b> Band edges are business choices, so the chart is only as "
                     f"meaningful as <code>BandOf</code>. The bars sum to {priced}, not {priced + declined} — the "
                     "test <code>Bands_account_for_every_priced_quote</code> checks that no <i>priced</i> quote "
                     "falls outside a band. " + MEASURED + ", illustrative data."}]},

        # ═══════════════════════════ 7 · EXPRESSION TREES ═══════════════════════════
        {"type": "story", "heading": "7 · Expression trees — code as data, and a DynamoDB query generator",
         "html": (
             "<p><b>The same lambda compiles either to executable code or to a data structure, depending only "
             "on the type it is assigned to.</b> Assigned to <code>Func&lt;Quote, bool&gt;</code> it becomes a "
             "delegate. Assigned to <code>Expression&lt;Func&lt;Quote, bool&gt;&gt;</code> the compiler emits code "
             "that builds a tree of nodes describing it (" + EXPTREES + "). <code>IQueryable&lt;T&gt;</code> "
             "operators take expressions, which is how EF Core turns a C# predicate into SQL — " + ref(9) + ".</p>"
             "<p><b>A query generator is a translator over that tree.</b> You built a DynamoDB query "
             "auto-generator before; in C# the compiler hands you the parsed predicate, and the library is one "
             "recursive switch over node shapes. <code>&amp;&amp;</code>, <code>||</code> and <code>!</code> become "
             "<code>AND</code>, <code>OR</code> and <code>NOT</code>; comparisons become comparators; "
             "<code>StartsWith</code> becomes <code>begins_with</code>; <code>Contains</code> becomes "
             "<code>contains</code> or <code>IN</code>. Every value goes through a <code>:value</code> placeholder, "
             "which DynamoDB always requires; every attribute goes through a <code>#name</code> placeholder, "
             "which DynamoDB requires only for reserved words and names with special characters — using it "
             "everywhere keeps the generator safe (" + DDBNAMES + " · " + DDBOPS + ").</p>"
             "<p><b>Compile time accepts what translation rejects.</b> Any expression lambda that type-checks "
             "compiles, but a translator — yours or EF Core's — supports a subset. The computed property "
             "<code>IsAccepted</code> and a call to <code>ToUpperInvariant</code> both compile and both fail at "
             "translation, each with its own exception: <code>DynamoFilter</code> throws "
             "<code>NotSupportedException</code> naming the node it met, while EF Core throws "
             "<code>InvalidOperationException</code> (“The LINQ expression … could not be translated”) — "
             + ref(9) + " pins that type in a test. The compiler itself refuses statement lambdas, <code>?.</code>, switch expressions, "
             "collection expressions, tuple literals and <code>is</code> patterns inside an expression tree; an "
             "interpolated string compiles, to a <code>string.Format</code> call that few providers can "
             "translate.</p>"
             "<p><b>C# 14 changed what <code>array.Contains(x)</code> binds to inside an expression.</b> With the "
             "new implicit span conversions it binds to <code>MemoryExtensions.Contains</code>, a "
             "<code>ReadOnlySpan&lt;T&gt;</code> method (7.4), and such trees throw when compiled with "
             "interpretation (" + SPANBREAK + "). The translator unwraps the conversion; for a provider you do "
             "not own, call <code>Enumerable.Contains</code> explicitly or cast to "
             "<code>IEnumerable&lt;T&gt;</code>.</p>")},
        {"type": "mermaid", "inline": True,
         "heading": "7.1 · One lambda, two destinations",
         "caption": "indigo = your source · green = code · amber = data the compiler builds · teal = a translator · "
                    "rose = outside this process",
         "code": ("flowchart LR\n"
                  '  SRC["q => q.Coverage == Class1"]:::src\n'
                  '  SRC -- "assigned to Func" --> DEL["Delegate<br/>compiled IL"]:::code\n'
                  '  DEL --> OBJ["LINQ to Objects<br/>runs in this process"]:::code\n'
                  '  SRC -- "assigned to Expression" --> TREE["Expression tree<br/>BinaryExpression, MemberExpression"]:::data\n'
                  '  TREE -- "Compile()" --> DEL\n'
                  '  TREE --> EF["EF Core provider<br/>SQL · ' + ref(9) + '"]:::prov\n'
                  '  TREE --> GEN["DynamoFilter.From<br/>expression + names + values"]:::prov\n'
                  '  EF --> DB["Relational database"]:::ext\n'
                  '  GEN --> DDB["DynamoDB Query or Scan<br/>FilterExpression"]:::ext\n'
                  "  classDef src fill:#c7d2fe,color:#1f2937,stroke:#6366f1;\n"
                  "  classDef code fill:#bbf7d0,color:#1f2937,stroke:#16a34a;\n"
                  "  classDef data fill:#fde68a,color:#1f2937,stroke:#d97706;\n"
                  "  classDef prov fill:#ccfbf1,color:#1f2937,stroke:#0d9488;\n"
                  "  classDef ext fill:#fce7f3,color:#1f2937,stroke:#be185d;\n")},

        figure_heading("7.2 · Func<T,bool> or Expression<Func<T,bool>>?"),
        {"type": "twocol", "boxes": [
            {"heading": "Func<T, bool> — a delegate", "tone": "green",
             "items": ["Compiled IL; call it directly",
                       "Used by <code>Enumerable</code> (LINQ to Objects)",
                       "Any statement lambda, <code>?.</code>, switch expression or local function is allowed",
                       "Opaque to a provider: it cannot be translated to SQL or a filter",
                       "Choose it for in-memory rules — the rating rules in 5.1"]},
            {"heading": "Expression<Func<T, bool>> — a tree", "tone": "amber",
             "items": ["Data: nodes you can walk, rewrite or translate",
                       "Used by <code>Queryable</code> — EF Core, your own generator",
                       "Expression lambdas only; newer syntax is refused by the compiler",
                       "Every provider supports a subset — unsupported calls fail at run time",
                       "Choose it when the predicate must run somewhere else: SQL, DynamoDB, a search index"]}]},

        listed(code(from_sample(ANALYTICS, "expression-demo"),
                    heading="7.3 · Func vs Expression, a span surprise, and a generated filter",
                    note="<b>Three experiments in one region.</b> The first pair declares the same lambda twice. "
                         "The second shows what C# 14 binds <code>shortlist.Contains</code> to. The third hands a "
                         "predicate with a captured <code>minPremium</code> to the generator. The output follows "
                         "in 7.4."),
               "7.3 · Func vs Expression, a span surprise, and a generated filter"),

        listed(code(captured(OUT_EXPRESSIONS, "Output — L04.QuoteAnalytics (expression part)"),
                    heading="7.4 · What the expression experiments print",
                    note="<b>Read the second line slowly.</b> The tree shows the enum comparison as "
                         "<code>Convert(q.Coverage, Int32) == 0</code> — the compiler lowered it, which is why the "
                         "translator strips <code>Convert</code> nodes and maps the number back to "
                         "<code>Class1</code>. The captured <code>minPremium</code> arrives as the value 15000, "
                         "evaluated when the filter was built. Five name placeholders cover one top-level attribute "
                         "and two nested paths."),
               "7.4 · What the expression experiments print"),

        listed(code(from_sample(QGEN, "translate"), keep=True,
                    heading="7.5 · The translator — pattern matching is the visitor",
                    note="<b>One switch expression replaces a visitor class hierarchy.</b> Property patterns "
                         "match node shapes (<code>BinaryExpression { NodeType: ExpressionType.AndAlso }</code>), "
                         "and anything unmatched throws. <code>DynamoFilter.From&lt;T&gt;</code> calls "
                         "<code>Condition(predicate.Body)</code> and returns the text with its name and value "
                         "maps. Bare boolean members become <code>= :v</code>, because DynamoDB cannot use a "
                         "Boolean attribute on its own as a condition (" + DDBOPS + "). A member counts as a "
                         "stored attribute when it is a field or an auto-property, so a hand-written getter such "
                         "as <code>IsAccepted</code> is refused as computed C#."),
               "7.5 · The translator — pattern matching is the visitor"),

        {"type": "story",
         "html": ("<p><b>A filter expression is not a query plan.</b> DynamoDB applies a filter after "
                  "<code>Query</code> has read the items, so the read capacity consumed is the same with or "
                  "without it, and the 1 MB page limit applies before filtering (" + DDBFILTER + "). Generate "
                  "filters for the residual conditions; design partition and sort keys for the access "
                  "pattern.</p>")},

        figure_heading("7.6 · What the generator translates — each row is a passing test"),
        {"type": "table",
         "cols": ["C# predicate", "Filter expression", "Result"],
         "rows": [
             ["<code>q.QuoteId == \"Q-0001\"</code>", "<code>#n0 = :v0</code>", "<b>✓</b> translated"],
             ["<code>r.Year &lt; 2020</code> … <code>&gt;=</code>, <code>!=</code>",
              "<code>&lt;</code> <code>&lt;=</code> <code>&gt;</code> <code>&gt;=</code> <code>=</code> "
              "<code>&lt;&gt;</code>", "<b>✓</b> translated"],
             ["<code>2020 &lt; r.Year</code>", "<code>#n0 &gt; :v0</code> — constant moved right",
              "<b>✓</b> translated"],
             ["<code>(a || b) &amp;&amp; !(c)</code>", "<code>((… OR …) AND NOT (…))</code>",
              "<b>✓</b> translated"],
             ["<code>q.Vehicle.Make.StartsWith(\"To\")</code>", "<code>begins_with(#n0.#n1, :v0)</code>",
              "<b>✓</b> translated"],
             ["<code>q.Vehicle.Model.Contains(\"Revo\")</code>", "<code>contains(#n0.#n1, :v0)</code>",
              "<b>✓</b> translated"],
             ["<code>makes.Contains(q.Vehicle.Make)</code>", "<code>#n0.#n1 IN (:v0, :v1)</code>",
              "<b>✓</b> translated"],
             ["<code>makes.Contains(…)</code> with 0 or 101 values", "— (DynamoDB: 1 to 100 values)",
              "<b>✗</b> refused"],
             ["<code>q.Coverage == CoverageClass.Class3Plus</code>", "value <code>Class3Plus</code>, not 2",
              "<b>✓</b> translated"],
             ["<code>r.Start &gt;= from</code> (a <code>DateOnly</code>)", "value <code>2026-11-01</code>",
              "<b>✓</b> translated"],
             ["<code>s.Make == \"Toyota\"</code> (a get-only auto-property)", "<code>#n0 = :v0</code>",
              "<b>✓</b> translated"],
             ["a captured local changed after <code>From</code>", "keeps the value read at translation",
              "by design"],
             ["<code>q.IsAccepted</code> (computed property)", "—", "<b>✗</b> refused"],
             ["<code>Make.ToUpperInvariant() == \"TOYOTA\"</code>", "—",
              "<b>✗</b> refused"],
             ["<code>q.Vehicle.Make.EndsWith(\"a\")</code>", "— (DynamoDB has no <code>ends_with</code>)",
              "<b>✗</b> refused"],
             ["<code>r.Tags.Contains(\"fleet\")</code> (a list attribute)",
              "— (DynamoDB <code>contains</code> supports lists; this translator does not map it)",
              "<b>✗</b> refused"]]},
        {"type": "html", "html": ("<div class=\"lnote\"><code>q</code> is a <code>Quote</code>; <code>r</code> is "
                                  "the test file's own <code>Row(Id, Renewal, Year, Start, Tags)</code> record and "
                                  "<code>s</code> its <code>Stored</code> class. Every row is a test in "
                                  "<code>DynamoFilterTests.cs</code>; <b>✗ refused</b> means the translator throws "
                                  "<code>NotSupportedException</code>.</div>")},

        listed(code(from_sample(QGEN_T, "tests"), keep=False,
                    heading="7.7 · Testing the generator, including what it refuses",
                    note="<b>Test the translator's contract, not DynamoDB.</b> No AWS SDK and no table: the "
                         "tests compare expression text and placeholder maps. The first test here pins a subtle "
                         "rule — a captured variable is read when <code>From</code> runs, so a filter built "
                         "earlier keeps the old value. The second proves a predicate can compile and still be "
                         f"untranslatable. The project holds {tests_qgen} test cases, covering every row of 7.6. "
                         + MEASURED + "."),
               "7.7 · Testing the generator, including what it refuses"),

        # ═══════════════════════════ 8 · VB LINQ ═══════════════════════════
        {"type": "story", "heading": "8 · Visual Basic LINQ — the richer query syntax",
         "html": (
             "<p><b>Visual Basic spells more of LINQ as clauses than C# does.</b> The C# language reference lists "
             "eight clause keywords — <code>from</code>, <code>where</code>, <code>select</code>, "
             "<code>group</code>, <code>into</code>, <code>orderby</code>, <code>join</code>, <code>let</code> — "
             "plus six contextual words that only work inside them (<code>in</code>, <code>on</code>, "
             "<code>equals</code>, <code>by</code>, <code>ascending</code>, <code>descending</code>) "
             "(" + CSQUERY + "). Visual Basic has fourteen query clauses; six of them have no C# query keyword: "
             "<code>Aggregate</code>, <code>Distinct</code>, <code>Skip</code>, <code>Skip While</code>, "
             "<code>Take</code> and <code>Take While</code> (" + VBLINQ + "). A VB estate's queries read like SQL, "
             "and many never call a LINQ method by name.</p>"
             "<p><b>Underneath it is the same LINQ.</b> The clauses compile to the same <code>Enumerable</code> "
             "calls, deferred and immediate execution work the same way, and the VB console prints the same "
             "conversion and top-makes figures as the C# dashboard. An <code>Aggregate</code> clause that "
             "<i>begins</i> a query runs immediately and returns one value, or one object with a property per "
             "aggregate function; inside a <code>From</code> query it adds per-row aggregates and the query stays "
             "deferred (" + VBAGG + ").</p>"
             "<p><b>Porting VB queries to C# is mechanical but not keyword-for-keyword.</b> <code>Group By … "
             "Into Quoted = Count()</code> becomes <code>GroupBy</code> plus a <code>Select</code> (8.1); "
             "<code>Aggregate … Into</code>, <code>Distinct</code>, <code>Skip While</code> and "
             "<code>Take While</code> become method calls (8.3, 8.4); anonymous types become records or "
             "tuples when they cross a method boundary. Plan the port of a whole VB estate with " + ref(6) + ".</p>")},

        listed(compare(half(from_sample(DASH, "conversion", label="C# · methods")),
                       half(from_sample(VB, "conversion", label="VB · Group By")),
                       heading="8.1 · Conversion by class — C# methods vs VB Group By … Into",
                       note="<b>VB names the aggregates inside the grouping clause.</b> "
                            "<code>Count(q.IsAccepted)</code> is VB's conditional count; C# writes "
                            "<code>g.Count(q =&gt; q.IsAccepted)</code> inside a <code>Select</code>. The VB query "
                            "has no <code>ToList</code>, so it stays deferred until the <code>For Each</code> that "
                            "prints it — the C# method materialises before returning."),
               "8.1 · Conversion by class — C# methods vs VB Group By … Into"),

        listed(compare(half(from_sample(DASH, "top-makes", label="C# · CountBy")),
                       half(from_sample(VB, "top-makes", label="VB · Group By")),
                       heading="8.2 · Top makes — CountBy and Index vs a five-line VB query",
                       note="<b>The same ranking, two idioms.</b> C# uses the .NET 9 <code>CountBy</code> and "
                            "<code>Index</code> to count and number in the pipeline; VB groups, orders by the named "
                            "aggregate and <code>Take 5</code>, and numbers the rows in the loop that prints them. "
                            f"Both print {makes_sentence}."),
               "8.2 · Top makes — CountBy and Index vs a five-line VB query"),

        listed(compare(half(from_sample(DASH, "summary", label="C# · port")),
                       half(from_sample(VB, "aggregate", label="VB · Aggregate")),
                       heading="8.3 · Aggregate … Into — a clause C# does not have",
                       note="<b>VB's <code>Aggregate</code> runs immediately and returns one object.</b> It "
                            "returned <code>Policies</code>, <code>Premium</code> and <code>Largest</code> "
                            f"properties: <code>{vb_sum[0]} quotes, {vb_sum[1]} THB, largest {vb_sum[2]}</code>. "
                            "C# has no such "
                            "clause: the port materialises the amounts once with <code>ToList</code> and reads "
                            "<code>Count</code>, <code>Sum</code> and <code>Max</code> from the list."),
               "8.3 · Aggregate … Into — a clause C# does not have"),

        listed(compare(half(from_sample(DASH, "window", label="C# · port")),
                       half(from_sample(VB, "distinct-skip-while", label="VB · Skip While")),
                       heading="8.4 · Distinct, Skip While and Take While — clauses C# spells as methods",
                       note="<b>Both cut the same window from the premium-ordered book.</b> "
                            f"<code>OrderBy</code> is stable, so the two quotes tied at {tie_amount} keep their "
                            f"book order ({tie_ids[0]}, then {tie_ids[1]}) in C# and in VB. <code>Distinct</code> "
                            "and "
                            "<code>Order</code> give the eight makes. The test <code>The_C_sharp_ports_reproduce_the_captured_"
                            "Visual_Basic_output</code> asserts both ports against the figures the VB console "
                            "printed."),
               "8.4 · Distinct, Skip While and Take While — clauses C# spells as methods"),

        listed(code(captured(from_line(OUT_VB, "accepted"),
                             "Output — L04.VbLinq, after the conversion and top-makes lines"),
                    heading="8.5 · What the VB console prints",
                    note="<b>The conversion and top-makes lines, not repeated here, match the C# dashboard "
                         "figure for figure:</b> same "
                         "records, same dataset, a different query language on the same runtime."),
               "8.5 · What the VB console prints"),

        {"type": "table", "heading": "8.6 · Which operators have query syntax",
         "cols": ["Operator", "C#", "Visual Basic", "Syntax"],
         "rows": [
             ["Where · Select · OrderBy", "<code>where</code> · <code>select</code> · <code>orderby</code>",
              "<code>Where</code> · <code>Select</code> · <code>Order By</code>", "<b>✓</b> both"],
             ["GroupBy · Join · Let", "<code>group … by … into</code> · <code>join … on … equals</code> · <code>let</code>",
              "<code>Group By … Into</code> · <code>Join … On … Equals</code> · <code>Let</code>", "<b>✓</b> both"],
             ["Count or Sum per group", "<code>g.Count()</code> inside <code>select</code>",
              "<code>Into Quoted = Count()</code>", "VB&nbsp;clause"],
             ["Distinct · Skip · Take", "<code>.Distinct()</code> · <code>.Skip(n)</code> · <code>.Take(n)</code>",
              "<code>Distinct</code> · <code>Skip n</code> · <code>Take n</code>", "VB&nbsp;clause"],
             ["SkipWhile · TakeWhile", "<code>.SkipWhile(…)</code> · <code>.TakeWhile(…)</code>",
              "<code>Skip While</code> · <code>Take While</code>", "VB&nbsp;clause"],
             ["Aggregate a whole source", "<code>quotes.Count(…)</code>, <code>.Sum(…)</code>, <code>.Max(…)</code>",
              "<code>Aggregate q In quotes Into Count(), Sum(…)</code>", "VB&nbsp;clause"],
             ["CountBy · AggregateBy · LeftJoin", "<code>.CountBy(q =&gt; …)</code>",
              "<code>.CountBy(Function(q) …)</code>", "methods"]]},

        # ═══════════════════════════ 9 · HANDS-ON ═══════════════════════════
        {"type": "story", "heading": "9 · Hands-on — build, test and run the lesson-04 samples",
         "html": (
             f"<p><b>{n_proj} projects, one command; the {tests_total} tests are the safety net.</b> "
             f"{tests_qgen} pin the generator's translation rules and refusals; {tests_data} pin the dataset, the "
             "dashboard figures, the C# ports of the VB queries, the pure rating rule, the "
             "deferred-versus-immediate behaviour of 3.3 and section 4, and the collection and record claims "
             "made in sections 2, 4 and 5 — so a changed rule fails a test before a captured panel here goes "
             "stale.</p>"
             "<p><b>Try three changes, then run the tests.</b> In <code>GroupBy_is_deferred_and_ToLookup_is_immediate</code> "
             "swap <code>GroupBy</code> and <code>ToLookup</code> and read which assertion fails; in the "
             "<code>readonly-views</code> region (2.3) add a second <code>classes.Add(\"Class3Plus\")</code> and "
             "predict which of the four counts change before you run <code>L04.Collections</code>; teach "
             "<code>DynamoFilter</code> to emit <code>BETWEEN</code> for <code>r.Year &gt;= 2020 &amp;&amp; "
             "r.Year &lt;= 2024</code> — DynamoDB has it (" + DDBOPS + ") — and add the test.</p>")},

        listed(code(from_text("""
            # build, test and run every lesson-04 project
            python 0-script/verify_samples.py --only 4

            # or one at a time, from the repository root
            dotnet run  --project lesson-04-linq-collections-functional/samples/L04.Collections
            dotnet run  --project lesson-04-linq-collections-functional/samples/L04.QuoteAnalytics
            dotnet run  --project lesson-04-linq-collections-functional/samples/L04.VbLinq
            dotnet test lesson-04-linq-collections-functional/samples/L04.QueryGen.Tests
            dotnet test lesson-04-linq-collections-functional/samples/L04.QuoteData.Tests
            """, "shell"), heading="9.1 · Commands",
                    note=f"<b><code>verify_samples.py</code> must end with {n_proj}/{n_proj} sample projects passed.</b> "
                         "The consoles need no input, network or database and exit within seconds."),
               "9.1 · Commands"),

        listed(code(captured(OUT_TESTS, "Output — dotnet test, durations omitted"),
                    heading="9.2 · What the tests report",
                    note=f"<b>{tests_total} tests pass: {tests_qgen} in the generator project and {tests_data} in "
                         "the data project.</b> " + MEASURED + " from the two test files, and matching this run. "
                         "If a rating rule or the dataset changes, "
                         "<code>Dashboard_numbers_match_the_captured_lesson_output</code> fails first — re-capture "
                         "the panels that quote those figures (3.3, 6.3 to 6.5)."),
               "9.2 · What the tests report"),

        {"type": "chart", "heading": "9.3 · Where the lesson-04 code lives",
         "kind": "hbar",
         "args": {"data": sorted(loc_by_project, key=lambda x: -x[1]), "tone": "navy", "width": 620,
                  "labelw": 150},
         "caption": "non-blank, non-comment lines of C# and VB per sample project · measured when this PDF was built",
         "note": (f"<b>The largest project is {biggest[0]} ({biggest[1]} lines); the whole VB dashboard console "
                  f"is {loc_vb_queries}.</b> The two test projects hold {loc_tests} lines and {tests_total} test "
                  f"cases against {loc_libs} lines in the two libraries they test. " + MEASURED + " with "
                  "<code>loc()</code>; line count is a size signal, not a quality score.")},

        {"type": "callout", "variant": "warn", "heading": "⚠ Traps",
         "items": [
             "<b>“A pipeline runs once.”</b> A Java stream does; a LINQ query over <code>IEnumerable&lt;T&gt;</code> "
             f"re-runs on every enumeration — {calls['three passes']} predicate calls for three reads in 3.3. "
             "Materialise with <code>ToList</code> before reading twice, and return materialised results from "
             "services.",
             "<b>“Read-only means nobody can change it.”</b> <code>IReadOnlyList&lt;T&gt;</code> and "
             "<code>AsReadOnly()</code> are views: the owner can still add, and a caller holding the "
             "<code>IReadOnlyList&lt;T&gt;</code> can cast it back to <code>List&lt;T&gt;</code> (2.3); the "
             "<code>AsReadOnly()</code> wrapper blocks that cast but not the owner's changes. Hand out "
             "<code>ImmutableArray&lt;T&gt;</code> or a frozen copy when that matters — and a record compares an "
             "<code>ImmutableArray&lt;T&gt;</code> by reference (5).",
             "<b>“Loop variables are captured per iteration.”</b> True for <code>foreach</code> and for "
             "TypeScript's <code>let</code>, false for a C# <code>for</code> loop: <code>3,3,3</code> in 5.2.",
             "<b>“It compiled, so the provider can run it.”</b> An expression tree type-checks C#, not the "
             "provider's subset: computed properties and unknown methods fail at translation (7.6), and in C# 14 "
             "<code>array.Contains</code> binds to a span method that interpreters reject.",
             "<b>“map[key] returns null.”</b> A <code>Dictionary</code> indexer throws "
             "<code>KeyNotFoundException</code> (4.4) and <code>ToDictionary</code> throws on duplicate keys "
             "(4.1)."]},

        {"type": "callout", "variant": "ok", "heading": "✔ Checkpoint — you are ready for lesson 05 when",
         "items": [
             f"<code>python 0-script/verify_samples.py --only 4</code> reports {n_proj}/{n_proj} passed on your "
             "machine.",
"Given a method that returns <code>IEnumerable&lt;T&gt;</code>, you can say whether it is a query or "
             "data, and how many times a caller's code will run it.",
             "You can choose the parameter and return type of a repository method from table 2.5 and say what "
             "each one promises its caller.",
             "You can rewrite a Kotlin <code>groupBy</code> + <code>mapValues { it.value.size }</code> as "
             "<code>CountBy(…).ToDictionary()</code>, and a <code>GroupJoin</code>/<code>DefaultIfEmpty</code> "
             "left join as <code>LeftJoin</code>.",
             "You can extend <code>DynamoFilter</code> with a new operator and a test, and say which predicates "
             "it must refuse.",
             "You can read a VB <code>Group By … Into</code> or <code>Aggregate … Into</code> query aloud as C#."]},

        {"type": "callout", "variant": "summary", "heading": "🔍 Check yourself",
         "items": [
             "A query <code>quotes.Where(p)</code> is counted, then its first item is read, then it is looped "
             "over. How many times does <code>p</code> run for 240 quotes whose second item is the first match, and "
             "which of <code>GroupBy</code> and <code>ToLookup</code> would have run immediately instead?",
             "A service returns <code>classes.AsReadOnly()</code>. Can a caller see a later change, and can it "
             "cast the result back to <code>List&lt;T&gt;</code>? What do you return when the caller must not "
             "see changes?",
             "Why does a <code>for</code> loop that adds <code>() =&gt; i</code> three times print "
             "<code>3,3,3</code>, and what prints <code>0,1,2</code>?",
             "What is the difference between <code>Func&lt;Quote, bool&gt;</code> and "
             "<code>Expression&lt;Func&lt;Quote, bool&gt;&gt;</code> for the same lambda, and which one can EF Core "
             "translate?",
             "Why does a DynamoDB filter expression not reduce the read capacity a <code>Query</code> consumes?",
             "What does <code>shortlist.Contains(q.Vehicle.Make)</code> bind to inside an expression tree under "
             "C# 14, and how do you keep a provider working?",
             "When does a VB <code>Aggregate</code> clause run immediately, and what C# does "
             "<code>Skip While</code> become?"]},

        {"type": "footer",
         "html": ("<b>Lesson 04 in one line:</b> choose collections by the promise they make — read-only is a view, "
                  "immutable is a guarantee; a LINQ query is a re-runnable recipe, so materialise at boundaries; "
                  "delegates are nominal and <code>for</code> loops share their variable; the same lambda is code "
                  "for <code>Enumerable</code> and data for <code>Queryable</code>, which is how you build a query "
                  "generator; and Visual Basic says more of it in clauses. "
                  "<br/><b>Next:</b> " + ref(5) + " — <code>Task</code>, <code>async</code>/<code>await</code>, "
                  "cancellation and channels for fan-out to rating partners.")},
    ]
