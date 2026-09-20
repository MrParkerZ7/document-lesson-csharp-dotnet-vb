# Unit spec — lesson-04-linq-collections-functional.pdf

Built to `_standard.md`. Content module `0-script/lessons/lesson_04.py`. Samples
`lesson-04-linq-collections-functional/samples/`. Plan: `_curriculum.md` § "04 · Collections, LINQ & Functional C#".

## 1 · Purpose

Map a Java Streams / Kotlin collections / TypeScript array-method engineer onto .NET collections, LINQ, delegates and
expression trees, spending the words on what does not transfer: re-runnable deferred queries, read-only views that are
not immutable, nominal delegate types and `for`-loop closure capture, and lambdas that compile to data. The reader
builds the tool they already built once in another language — a query generator that turns a C# predicate into a
DynamoDB filter expression — runs MotorQuote dashboard queries over a deterministic quote book (illustrative rates,
labelled wherever a premium appears), and reads the same dashboard in Visual Basic query syntax, with the C# ports of
the VB-only clauses beside it.

**Tariff.** `L04.QuoteData/Rating.cs` implements the track's canonical tariff verbatim (`_curriculum.md` § "Canonical
tariff"): base rate by class 2.1 / 1.2 / 0.9 / 0.4 % of the sum insured (Class 3 is a rate, never a flat amount),
loadings added then applied (young driver +20 %, claims 0 / +10 / +25 %, commercial +25 % or +35 % over 3,000 cc),
no-claim ladder 0 / 20 / 25 / 30 / 40 / 50 % on claim-free licence years, stamp duty 0.4 %, VAT 7 % on net + duty,
`decimal.Round(…, 2, MidpointRounding.AwayFromZero)`. Three or more claims in five years is a **decision, not a
price**: this lesson teaches data, so `QuoteBook.Generate` marks the quote `QuoteStatus.Declined` with `Total` 0 and
no band (the curriculum's data-side convention; lesson 02 throws `QuoteDeclinedException` instead). No deliberate
variant. The rules keep this lesson's teaching shape — a list of named `Loading` delegates folded with `Aggregate` —
and panel 5.1's note says they are lesson 02's `switch` expressions re-expressed as values.

## 2 · Ownership & cadence

Owner **claude**, regenerable. Re-verify every November when a new .NET major ships: the operator arrivals in the §4
story, mapping 4.1 and timeline 4.2 (a .NET 11 LINQ addition belongs there; `Shuffle` and `InfiniteSequence` are cited
from their API pages because the .NET 10 what's-new page does not list them), the C# 14 span-binding paragraph in §7
(`MemoryExtensions.Contains`), and the C# / VB clause lists behind KPI "VB-only query clauses 6", the §8 story and
table 8.6. Re-verify the DynamoDB facts (IN list of 100 values, `contains` on strings, sets and lists, no `ends_with`,
filter applied after `Query` reads, 1 MB page limit, `#name` placeholders only required for reserved words and special
characters) when the AWS developer guide changes. Re-capture the output constants in `lesson_04.py`
(`OUT_COLLECTIONS`, `OUT_DASHBOARD`, `OUT_EXPRESSIONS`, `OUT_VB`, `OUT_TESTS`) whenever a sample's `Console.WriteLine`
or a test count changes; `DashboardTests.Dashboard_numbers_match_the_captured_lesson_output` fails first if the dataset
or a rating rule changes the dashboard figures.

## 3 · Structure

20 pages at the 2026-09-20 build. The Contents fills page 1 and §1 starts page 2 (a zero-height `break-before:page`
element before the §1 story keeps a stub of §1 from printing at the foot of page 1). A lesson-local `<style>` block
keeps every story and callout heading with its first line and every callout whole.

| § | Heading | Blocks |
|---|---|---|
| — | Contents | `toc` depth 2 (code panels, the twocol and two tables are listed through local `listed()` / `figure_heading()`) · lesson-local CSS block · page-break element |
| 1 | Why collections and LINQ decide how .NET code reads | story (3 ¶) · `kpi` 1.1 (5 tiles) · `legend` (C#, Java/Kotlin, architecture) · info callout "Before you start" (5 items — item 2 names the canonical tariff, item 3 the lesson-03 type-kind rule this dataset deliberately flattens) |
| 2 | The collection family — what to accept, store and return | story (4 ¶) · mermaid 2.1 classDiagram RL (two interface families, concrete types carry one member line each) · code 2.2 (collection expressions) · compare 2.3 (C# read-only views ↔ captured output part 2) · cards 2.4 in two bands of 3 (List · Dictionary/HashSet · arrays and spans / immutable · frozen · read-only wrappers; band 2 `toc: False`) · figure heading + table 2.5 (API-boundary type choice, 8 rows) |
| 3 | Deferred execution — a query is a recipe, not a result | story (4 ¶) · mermaid 3.1 sequenceDiagram (one query, four calls) · compare 3.2 (Java Stream reuse ↔ C# deferred region) · chart 3.3 bar (predicate calls) · compare 3.4 (C# captured variable ↔ C# list changed in foreach) · compare 3.5 (Kotlin `sequence {}` ↔ C# `yield return`) |
| 4 | The operator map — Streams, Kotlin and TypeScript in LINQ | story (3 ¶) · mapping 4.1 (19 rows; `CountBy`, `AggregateBy` and `MaxBy` are Trap, `Zip` is Renamed) · mermaid 4.2 timeline (2005 → 2025 arrivals, period labels are years) · code 4.3 (`AggregateBy`) · compare 4.4 (C# lookup vs dictionary ↔ captured output part 9) |
| 5 | Functional C# — delegates, closures and immutable records | story (4 ¶, incl. the `ImmutableArray` record-equality trap) · code 5.1 (rating rules as a list of delegates folded with `Aggregate`) · compare 5.2 (TypeScript `let`/`var` closures ↔ C# `for`/`foreach`) · compare 5.3 (C# nominal delegates ↔ C# shallow `with`) |
| 6 | Quote analytics — the dashboard habit in LINQ | story (3 ¶) · code 6.1 (premium bands: `CountBy`, then `BandOrder` walked so an empty band shows 0) · compare 6.2 (C# `LeftJoin` ↔ the query-syntax `join … into` / `DefaultIfEmpty` left join) · code 6.3 (captured dashboard output, excerpt from "top makes") · chartrow 6.4 bar (conversion rate by class) + 6.5 bar (quotes per premium band) |
| 7 | Expression trees — code as data, and a DynamoDB query generator | story (4 ¶) · mermaid 7.1 flowchart LR (one lambda, two destinations) · figure heading + twocol 7.2 (Func vs Expression) · code 7.3 (Func vs Expression, span binding, generated filter) · code 7.4 (captured output) · code 7.5 (translator switch, kept whole) · headingless story (a filter expression is not a query plan) · figure heading + table 7.6 (translation rules and refusals, 16 rows, one per passing test) + caption line · code 7.7 (two generator tests, may split) |
| 8 | Visual Basic LINQ — the richer query syntax | story (3 ¶) · compare 8.1 (C# ↔ VB conversion by class) · compare 8.2 (C# ↔ VB top makes) · compare 8.3 (C# `Summarise` port ↔ VB `Aggregate … Into`) · compare 8.4 (C# `Makes` + `Window` port ↔ VB `Distinct` / `Skip While` / `Take While`) · code 8.5 (captured VB output, excerpt from "accepted") · table 8.6 (operators with query syntax, 7 rows, plain-text outcomes) |
| 9 | Hands-on — build, test and run the lesson-04 samples | story (2 ¶, three exercises) · code 9.1 commands · code 9.2 captured `dotnet test` summary · chart 9.3 hbar (lines per project) · warn "Traps" (5) · ok checkpoint (6) · summary "Check yourself" (7) · footer (Next: lesson 05) |

Standard minimums as built: 9 numbered stories · 1 mapping · 2 card bands (3 cards each) · 4 mermaid in 4 families
(classDiagram, sequenceDiagram, timeline, flowchart) · 4 charts · 36 code panels (12 `code` + 12 `compare`) · C# ↔ VB
compares 8.1, 8.2, 8.3, 8.4 · Java/Kotlin/TypeScript ↔ C# compares 3.2, 3.5, 5.2 · 1 twocol · 3 tables besides the
mapping (2.5, 7.6, 8.6) · 25 distinct links.

## 4 · Derivation

- **KPI "One query, three passes — 482 calls"**, the §3 story, chart 3.3 and notes 3.2 / Traps — MEASURED: parsed at
  build from `OUT_COLLECTIONS` (a captured run of `L04.Collections`, part 4: `calls = 0`, `482`, `240`). The same
  arithmetic (240 + 2 + 240) is asserted by `DashboardTests.Three_passes_over_a_deferred_query_run_its_predicate_three_times`.
- **KPI "New in .NET 9 LINQ — 3"** — VERIFIED: What's new in .NET 9 libraries § LINQ (`CountBy`, `AggregateBy`,
  `Index`). That `CountBy` and `AggregateBy` are deferred (mapping 4.1, note 4.3) is MEASURED by
  `CountBy_and_AggregateBy_are_deferred_and_run_again_on_every_enumeration`.
- **KPI "VB-only query clauses — 6"**, the §8 story and table 8.6 — VERIFIED: the C# query keywords reference lists
  fourteen words, of which eight are clauses (`from`, `where`, `select`, `group`, `into`, `orderby`, `join`, `let`) and
  six are contextual (`in`, `on`, `equals`, `by`, `ascending`, `descending`); Introduction to LINQ in Visual Basic lists
  fourteen clauses (From, Select, Where, Order By, Join, Group By, Group Join, Aggregate, Let, Distinct, Skip, Skip While,
  Take, Take While), six of which have no C# query keyword: Aggregate, Distinct, Skip, Skip While, Take, Take While.
- **KPI "DynamoDB IN list ≤ 100"** — VERIFIED: DynamoDB condition and filter expressions ("The list can contain up to
  100 values"). The generator enforces the same cap (`MaxInValues`); `An_IN_list_of_exactly_100_values_is_accepted` and
  `An_IN_list_outside_1_to_100_values_is_refused` (0 and 101) make it MEASURED.
- **KPI "Lesson 04 samples"** and chart 9.3 — MEASURED at build: `loc()` over every `.cs` / `.vb` file per project
  (excluding `obj/` and `bin/`); 919 lines at this build (QuoteData 229, QuoteData.Tests 176, QueryGen.Tests 156,
  QueryGen 144, Collections 117, VbLinq 52, QuoteAnalytics 45). Test cases = `[Fact]` + `[InlineData(` per test file:
  24 + 19 = 43, equal to the captured `dotnet test` totals in `OUT_TESTS` (panel 9.2).
- **Charts 6.4 / 6.5**, notes 6.2 / 6.3 / 4.3 — MEASURED: parsed at build from `OUT_DASHBOARD` (a captured run of
  `L04.QuoteAnalytics` on the canonical tariff): conversion 40.7 / 59.3 / 59.3 / 75.9 %, bands 40 / 109 / 50 / 16 / 1,
  127 accepted of the 216 priced quotes, 21 pending, 24 declined (never priced), accepted premium by class
  136,262 / 169,483 / 174,299 / 130,512 THB. The dataset (`QuoteBook.Generate`) is deterministic; the acceptance
  gradient by class is built into `QuoteBook.StatusOf` on purpose, and the chart note says so. Premiums are
  illustrative. `Quote.Total` (the quoted premium, `Money`) matches the name lesson 11 uses; the no-claim rule uses
  licence years as a stand-in for claim-free years (the curriculum's own definition) and says so in a sample comment.
  Chart 6.5 bands the 216 priced quotes only, and its caption says where the 24 declined quotes went.
- **The tariff itself** — MEASURED against the curriculum's worked example:
  `DashboardTests.The_canonical_worked_example_prices_to_8_933_71` asserts base 11,550.00, net 8,316.00 and total
  8,933.71 THB for Class 1 / 550,000 / private / age 23 / 4 claim-free licence years;
  `The_tariff_declines_three_or_more_claims_instead_of_pricing_them` asserts that every declined quote has 3+ claims
  and `Total` 0 and that no priced quote has 3+ claims. Every other prose figure in the module that quotes a run
  (thresholds 123 / 67, `Count`/`FindAll` 127, the mermaid 3.1 result list, the premium-by-class pair in note 4.3, the
  top-makes ranking, the VB `Aggregate` triple and the tied window pair) is parsed out of the `OUT_*` captures in
  `blocks()`, so a re-tariff cannot leave prose behind.
- **Panels 2.2, 2.3, 3.4, 3.5, 4.4, 5.2, 5.3** notes quote `OUT_COLLECTIONS`; 2.3 and 4.4 print its parts 2 and 9 via
  `part()`. The synthesised type name `<>z__ReadOnlyArray`1` (2.2) is printed by the sample and labelled a compiler
  detail, not a contract. The `AsReadOnly()` cast claim (2.3, card 6, Traps) is asserted by
  `AsReadOnly_refuses_the_cast_back_to_List_that_the_interface_view_allows`; the record-equality claim (§5, card 4) by
  `A_record_holding_an_ImmutableArray_compares_the_array_reference`; the `MaxBy` claim (mapping 4.1) by
  `MaxBy_on_an_empty_sequence_returns_null_for_classes_and_throws_for_structs`.
- **Panels 6.3 and 8.5** are excerpts of the captured outputs (`from_line()` — from a starting line to the end, never
  edited); their headers say which lines are omitted.
- **Panel 6.1** — `Bands` returns a materialised `IReadOnlyList` and fills empty bands from `BandOrder`
  (`A_band_without_quotes_still_gets_a_row_with_zero`); the captured band counts are unchanged because every band has
  quotes in the dataset. **Compare 6.2** — the query-syntax and `LeftJoin` forms return the same sequence
  (`The_C_sharp_query_syntax_left_join_matches_LeftJoin`).
- **Compares 8.3 / 8.4** — the C# ports (`Summarise`, `Makes`, `Window`) reproduce the captured VB output: 127 accepted,
  610,555 THB, largest 12,182, the eight distinct makes, and the five window quotes Q-0139, Q-0219, Q-0005, Q-0015,
  Q-0175 between 8,600 and 8,900 THB (`The_C_sharp_ports_reproduce_the_captured_Visual_Basic_output`). The window
  bounds moved with the tariff so the slice still shows a stable-sort tie (Q-0139 and Q-0219 both 8,685.55), which is
  what note 8.4 is about.
- **Panel 7.4** is `OUT_EXPRESSIONS`, captured from `L04.QuoteAnalytics` (`binds to MemoryExtensions.Contains` on the
  .NET 10.0.401 SDK / C# 14; the `#n1` name is `Total`).
- **Timeline 4.2** — VERIFIED: The history of C# (C# 2 Nov 2005 iterators; C# 3 Nov 2007 query expressions, lambdas,
  expression trees; C# 12 Nov 2023 collection expressions; C# 14 Nov 2025 implicit span conversions); What's new in
  .NET 6 (Chunk, DistinctBy, MinBy, MaxBy), .NET 8 runtime (System.Collections.Frozen), .NET 9 libraries (CountBy,
  AggregateBy, Index), Join operations (.NET 10 LeftJoin, RightJoin), `Enumerable.Shuffle` and
  `Enumerable.InfiniteSequence` API pages (net-10.0 and net-11.0 only), System.Linq.AsyncEnumerable in .NET 10.
- **§7 story** — the compiler refuses statement lambdas (CS0834), `?.` (CS8072), switch expressions (CS8514),
  collection expressions (CS9175), tuple literals (CS8143) and `is` patterns (CS8122) inside an expression tree,
  checked by compiling each on the build SDK; an interpolated string compiles to `string.Format`
  (`An_interpolated_string_compiles_inside_an_expression_tree_as_string_Format`).
- **Table 7.6** — each row restates a passing test in `L04.QueryGen.Tests/DynamoFilterTests.cs`; a member is a stored
  attribute when its getter is compiler-generated (a field or auto-property, so a get-only auto-property translates and
  a hand-written getter such as `IsAccepted` is refused). The `ends_with` and list-`contains` rows follow the DynamoDB
  function list (`begins_with`, `contains`, `size`, `attribute_exists` …; `contains` accepts a string, a set or a list).
- **Table 8.6** — a rubric built from the two language references above (which operators have clause syntax), not a
  measurement.
- **CS0029** (5.3, §5 story) — checked by compiling the commented line on the build SDK; the sample keeps it commented
  so the project builds.

## 5 · Presentation

Format 00 via `brief_pdf.py`; code panels from `lesson_kit`. Local helpers in the module (kit requests):
`listed()` copies a panel heading onto the block for the Contents and, for a panel that is not kept whole, prints the
heading as a `.ct` line so the page marker does not make the panel unbreakable; `half()` drops the `samples/<Project>/`
prefix from a compare side's file caption so a half-width header shows the region name instead of an ellipsis;
`figure_heading()` gives the twocol and tables 2.5 / 7.6 a heading that travels with them; `part()` / `from_line()` cut
captured outputs; `test_cases()` counts test cases. Panels of ≤ 18 lines are kept whole by the kit: 7.3 is exactly 18
lines, so its position depends on the §7 story length (trimming or adding a line there can make it jump or split);
7.5 is kept, 7.7 may split. Mermaid 2.1 is `classDiagram` `direction RL` with `:::` classes (a `cssClass` line did not
apply to generic `~T~` classes; `direction TB` printed a taller figure and cost a page); 3.1 disables `mirrorActors`
and widens `actorMargin` so it prints short; 4.2 writes `C#` as `C#35;` (a bare `#` truncated timeline period labels),
uses years as period labels and sets `fontSize` 19px; 7.1 names lesson 09 through `ref(9)`. Table outcomes in 7.6 and
8.6 are plain text (`✓`, `✗ refused`, `VB clause`) so they do not reuse the colours of the Same / Renamed / Trap /
Estimate chips. Legend limited to three tags: a longer legend row does not wrap and widened the page, which made Edge
shrink every page of the PDF.

## 6 · Inputs

`roster.py`; samples `L04.QuoteData` (C# library: MotorQuote records, deterministic `QuoteBook`, `QuoteDashboard`
queries and the C# ports of the VB clauses, `Rating` rules as delegates), `L04.QueryGen` (C# library: `DynamoFilter`
expression → filter expression, no AWS SDK), `L04.Collections` (C# console: collection expressions, read-only vs
immutable, frozen table, deferred execution, iterators, closures, `with`, delegate types, missing keys),
`L04.QuoteAnalytics` (C# console: dashboard + expression experiments), `L04.VbLinq` (VB console: the dashboard in VB
query syntax), `L04.QueryGen.Tests` and `L04.QuoteData.Tests` (xUnit 2.9.3). Sources: Microsoft Learn — collection
expressions, the history of C#, What's new in .NET 6 / .NET 8 runtime / .NET 9 libraries, join operations,
`Enumerable.Shuffle` / `InfiniteSequence`, System.Linq.AsyncEnumerable breaking change, ref struct types, IList<T>,
introduction to LINQ queries, standard query operators, lambda expressions, expression trees, C# 14 overload
resolution with span parameters, CA1851, C# query keywords, Introduction to LINQ in Visual Basic, VB Aggregate clause;
AWS — DynamoDB condition and filter expressions, Query filter expressions, expression attribute names; Oracle —
java.util.stream.Stream (Java 21); Kotlin — sequences.

## 7 · Invariants

- Every figure in the dashboard charts and panels must match `DashboardTests.Dashboard_numbers_match_the_captured_lesson_output`;
  change the dataset or rules only together with that test and the captured constants.
- `Rating.cs` stays byte-for-byte the canonical tariff (`_curriculum.md` § "Canonical tariff"), and a decline stays a
  `QuoteStatus.Declined` rather than an exception. Any deliberate variant would need one sentence in the lesson naming
  the canonical tariff; there is none today. `The_canonical_worked_example_prices_to_8_933_71` is the guard.
- No premium, rate, loading, discount, stamp-duty or VAT figure is typed into `lesson_04.py`: every one is parsed from
  an `OUT_*` capture or from a sample region shown through `from_sample()`.
- Cross-lesson pointers must resolve. §1 item 4 and mapping 4.1 name only what the referenced lesson contains:
  lesson 05 owns `IAsyncEnumerable` and Task-based parallelism but **not** PLINQ, so the `parallelStream()` row
  explains `AsParallel()` itself and says the track does not cover it. §7 attributes `NotSupportedException` to this
  lesson's `DynamoFilter` and `InvalidOperationException` to EF Core, which lesson 09 pins in a test.
- `L04.QuoteAnalytics` must keep printing the `binds to` line; if a future compiler binds `shortlist.Contains` back to
  `Enumerable.Contains`, rewrite the §7 span paragraph rather than the capture.
- `DynamoFilter` stays free of the AWS SDK; tests compare expression text and placeholder maps only.
- The VB sample keeps using query clauses C# lacks (`Group By … Into`, `Aggregate`, `Distinct`, `Skip While`,
  `Take While`), and `QuoteDashboard` keeps the C# ports beside it, so compares 8.3 and 8.4 stay a real port.
- Region lines used in `compare()` stay ≤ 62 characters and in `code()` ≤ 100 (the build warns otherwise). Compare
  regions `left-join`, `left-join-query`, `summary` and `window` are laid out to fit; `Unset` is the short name of the
  `"(pending)"` placeholder for that reason.
- No employer, client or personal names; experience stays generic ("a few hundred dashboard queries for a BI tool",
  "a DynamoDB query auto-generator library").

## 8 · Known gaps

- ⚠ Output panels are pasted captures from the build machine (Windows, .NET 10.0.12 runtime); only the dashboard
  figures, the three-pass arithmetic and the C# ports are guarded by tests. The other captured lines
  (collection-expression type name, closure output, VB window query) would go stale silently if the samples' output
  changed.
- ⚠ Java, Kotlin and TypeScript comparison panels (3.2, 3.5, 5.2) and the Kotlin / Guava names in mapping 4.1 are not
  compiled or run.
- ⚠ The CS0029 claim and the six expression-tree compiler errors in the §7 story were checked by compiling scratch
  files, not by a repeatable build step.
- ⚠ `DynamoFilter` is a teaching translator: no `BETWEEN`, `attribute_exists`, `size`, list/set `contains`,
  projection or key-condition expressions, and it is never run against DynamoDB. Its "stored attribute" test (a
  compiler-generated getter) also refuses a property with a hand-written getter over a backing field.
- ⚠ The frozen-collection and `CountBy`/`AggregateBy` performance claims are qualitative (quoted from Microsoft Learn);
  the lesson ships no benchmark. The frozen-dictionary region is referenced by card 2.4 but not shown as a panel.
- ⚠ Some pages end 15–30 % empty where an unbreakable block (a card band, a kept panel, a chart row, a table) starts
  the next page: pages 5 (the widest gap, ≈ ⅓, before mermaid 3.1), 6, 10, 12, 13 and 14. Pagination was tuned by
  eye; a change to a story's length can move a panel.
- ⚠ The lesson asserts that the tariff it prices with is the one every other lesson prices with. That is enforced by
  `_curriculum.md`, not by anything this lesson can run: a sibling lesson drifting away from the canonical table would
  not fail a lesson-04 test.
- ⚠ The reader is told (§1 item 4) that this track does not cover PLINQ. If a later lesson adds it, mapping 4.1's
  `parallelStream()` row and that item should become a pointer again.
