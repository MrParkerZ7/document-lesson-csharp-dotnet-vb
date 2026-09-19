# Unit spec — lesson-03-types-oop-generics.pdf

Built to `_standard.md`. Content module `0-script/lessons/lesson_03.py`. Samples
`lesson-03-types-oop-generics/samples/`. Plan: `_curriculum.md` § "03 · Types, OOP & Generics".

## 1 · Purpose

Give a Java / Kotlin architect the .NET shape of the type system they already design with: the five kinds of type
and what each costs in memory and equality, properties and construction (`init`, `required`, primary constructors,
the C# 14 `field` keyword), non-virtual-by-default dispatch and `new` hiding, default and static abstract interface
members, reified generics with constraints, variance and generic math, C# 14 extension members, equality and
operators — then the same ideas as architecture: a generic multi-format report framework extended from Visual
Basic, with the C#/VB language boundary pinned by compiler tests. All premiums use the MotorQuote rules and are
labelled illustrative, not a real tariff.

## 2 · Ownership & cadence

Owner **claude**, regenerable. Re-verify every November (a new C# ships with each .NET major): the C# 15 preview
statements (union types, `closed` hierarchies, extension indexers — expected to ship with .NET 11), the KPI tile
"C# 14 · ships with .NET 10", and the Visual Basic "What's new" list behind table 7.6. The module's `CHECKED` date
(now 2026-09-20) is the day the C# 15 and Visual Basic "What's new" pages were last read; it is printed beside the
VERIFIED chips in §4, §6 and §7 and must move only when someone re-reads those pages. Bump
`Microsoft.CodeAnalysis.VisualBasic` in `L03.Reports.Tests` when the pinned SDK moves to a new Roslyn line, and
re-run `VbCompilerTests`. Re-capture `TOUR_OUT` / `VB_OUT` whenever a console sample's output changes.

## 3 · Structure

| § | Heading | Blocks |
|---|---|---|
| — | Contents | `toc` depth 2 (fills page 1) · html style (keep `h2` and callout headings with their content, links break at word boundaries, compact Contents lines) · an empty block with `break-before:page` so §1 starts on page 2 |
| 1 | Why the type system is where Java instincts break | story (4 ¶, scope boundaries to 02/04/08, C# 14 date with VERIFIED + link) · `kpi` 1.1 (5 tiles) · `legend(T_CS, T_RUNTIME)` · info callout "Before you start" (4, one explains the VERIFIED / ESTIMATE / MEASURED chips) |
| 2 | Five kinds of type — and where their bytes live | story (4 ¶) · cards 2.1 (2 cards: class, struct) + "(continued)" band (3 cards: record, record struct, enum; `toc: False`) · mermaid 2.2 flowchart (three arrays of 1,000 amounts) · code 2.3 (`Money`) · code 2.4 (`TypesTour#copy-trap`: a struct read from a list, `default(Money)`) · chartrow 2.5 bar (bytes for 1,000 amounts) + 2.6 bar (methods emitted) · mermaid 2.7 flowchart (which kind of type — MotorQuote decisions) · mapping 2.8 (19 rows) |
| 3 | Members — properties, construction and the C# 14 field keyword | story (4 ¶) · code 3.1 (`Quote`: required, init, `field`) · mermaid 3.2 stateDiagram-v2 (quote lifecycle, starts at `Quoted`) · compare 3.3 (Kotlin named arguments ↔ C# object initializer, `Samples.cs#object-initializer`) · compare 3.4 (Kotlin constructor ↔ C# primary constructor) · table 3.5 (6 property forms) |
| 4 | Inheritance and interfaces — methods are non-virtual by default | story (4 ¶) · compare 4.1 (Java ↔ C# rule hierarchy) · compare 4.2 (C# calls ↔ captured output) · mermaid 4.3 flowchart (which method runs) · code 4.4 (default interface method) · code 4.5 (static abstract members) · table 4.6 (inheritance keywords: Java, Kotlin, C#, VB — 9 rows) · code 4.7 (the same hierarchy in VB, member for member) |
| 5 | Generics — reified, constrained and variant | story (3 ¶) · chart 5.1 bar (bytes to store 1,000 ints) · compare 5.2 (Java erasure workaround ↔ C# `T.Parse`) · compare 5.3 (Kotlin ↔ C# variance) · code 5.4 (generic math `Sum`) · table 5.5 (8 constraints) · code 5.6 (`(Of T As …)` in VB, `Program.vb#vb-generic`) |
| 6 | Extension members, equality and operators | story (4 ¶) · compare 6.1 (Kotlin enum class ↔ C# 14 extension block) · code 6.2 (classic `this`-parameter extension, `Extensions.cs#classic-extension`) · compare 6.3 (hand-written `IEquatable` ↔ record with replaced equality) · code 6.4 (boxes, `==`, broken hash code) |
| 7 | Design in C# — a multi-format report framework, extended from VB | story (4 ¶) · mermaid 7.1 classDiagram TB · code 7.2 (template-method base) · code 7.3 (strategy selector) · compare 7.4 (`Renderers.cs#csv-renderer` ↔ `Program.vb#vb-csv`) · code 7.5 (VB consuming records, operators, required) · table 7.6 (9 rows: what the VB compiler says) · code 7.7 (`VbCompilerTests` region) · figure heading 7.8 + threecol (VB declares / consumes / cannot reach) |
| 8 | Hands-on — build, test and run the lesson-03 samples | story (3 ¶) · code 8.1 commands (with a note) · code 8.2 (captured C# tour) · code 8.3 (captured VB output) · chartrow 8.4 hbar (lines per project) + 8.5 hbar (test cases per class) · warn "Traps" (5) · ok checkpoint (5) · summary "Check yourself" (7) · footer (Next: lesson 04) |

Every numbered `code()` / `compare()` panel is listed in the Contents at level 2 (the lesson wraps the kit helpers,
as lessons 01 and 06 do). Counts checked by `lint_blocks`: 8 numbered stories · 1 mapping (2.8) · 2 cards bands (≤ 3
cards each) · 5 mermaid (flowchart ×3, stateDiagram-v2, classDiagram) · 5 charts (2.5, 2.6, 5.1, 8.4, 8.5) · 26 code
blocks (17 `code` + 9 `compare`) · C# ↔ VB compare 7.4 · Java/Kotlin ↔ C# compares 3.3, 3.4, 4.1, 5.2, 5.3, 6.1 ·
threecol 7.8 · 4 extra tables (3.5, 4.6, 5.5, 7.6) · 18 distinct links. Rendered length: 22 pages (page 22 holds
Check yourself and the footer).

## 4 · Derivation

- **KPI "C# 14 · ships with .NET 10 — Nov 2025"** — VERIFIED: The history of C# ("C# version 14 · Released November
  2025") and What's new in C# 14 ("C# 14 is supported on .NET 10"); the §1 story cites the history page with a
  VERIFIED chip, and the tile says "verified · C# version history".
- **KPI "Methods for two properties — 16 vs 3"** — MEASURED: the `generated` line of `TOUR_OUT` (record vs class).
- **KPI "Money in memory 24 bytes"**, card sizes (`Money` 24, `QuoteId` 4, `CoverageClass` 4), charts 2.5, 2.6, 5.1,
  mermaid 2.2 byte labels, and the byte / method counts in the §2 and §5 stories — MEASURED: parsed at import from
  `TOUR_OUT` (the `size`, `alloc`, `generated` and `generics` lines), which is the captured output of
  `dotnet run -c Release` of `L03.TypesTour` on the build machine (Windows 11 x64, SDK 10.0.401, runtime 10.0.12).
  The tour measures with `Unsafe.SizeOf<T>`, `GC.GetAllocatedBytesForCurrentThread` around each loop, and reflection
  over declared methods + constructors. Because the charts are parsed from the same text as panel 8.2, they cannot
  disagree with it. `TOUR_OUT` and `VB_OUT` were compared against a fresh run of both consoles on 2026-09-20: identical.
- **KPI "Lesson 03 tests"** and chart 8.5 — MEASURED at build by `_test_cases_by_class()`: `[Fact]` = 1, each
  `[InlineData(` = 1, grouped by `public class`. The build-time total (71) equals `dotnet test -c Release` on the
  build machine: 42 in `L03.Domain.Tests` + 29 in `L03.Reports.Tests`. Chart 8.5 shows the five largest classes
  and combines the rest into one "N other classes" bar (said in its caption).
- **KPI "Lesson 03 samples"**, chart 8.4 and its note — `loc()` over every `.cs` / `.vb` file per project (MEASURED);
  the note's two totals are the two test projects (471 lines at the last build) vs the two libraries they test (403).
  The note states that line counts are not coverage and points to lesson 10, which measures coverage.
- **Table 7.6** — MEASURED by compilation: every row is an `InlineData` case in
  `L03.Reports.Tests/VbCompilerTests.cs`, which compiles Visual Basic (`Option Strict On`) against the lesson
  assemblies with `Microsoft.CodeAnalysis.VisualBasic` 5.9.0 and asserts the exact set of error ids. The
  "What works instead" column is compiled for the call-site rows by `Its_workaround_compiles` (`get_Code`, static
  `FromCode`, the interface-typed call, the constructor copy) and by `L03.VbInterop` itself (required + init members
  in `With { }`, `Ids.ParseAll(Of T)`); the two declaration workarounds (write the member in VB, declare the type in
  C#) are advice, not compiled. `_vb_limits()` raises at build if the table cites an error id the test
  file does not contain. The same ids were first observed with the SDK 10.0.401 compiler itself (a `dotnet build` of
  a throw-away VB project on the build machine). The Roslyn version in the §7 story is read from the test `.csproj`.
- **Panel 4.7 and the VB half of panel 8.3** — the VB `RatingRule` / `YoungDriverLoading` hierarchy in
  `Program.vb#vb-keywords` mirrors `Rating.cs#dispatch` member for member (same `Factor(r As QuoteRequest)`, same
  age rule, same `Describe`/`Shadows`), so the printed `dispatch 1.20 | young driver x1.20 | young driver (hidden
  copy)` is the same three answers as panel 4.2. The earlier lines-of-code comparison chart (7.7) was dropped:
  a 2–4 line difference is within line-wrapping noise and the panels are now identical in behaviour, so the chart added
  nothing a measurement could support.
- **Panel 4.2 output, panel 8.2, panel 8.3, and "prints …" statements in notes 4.4, 4.7, 5.2, 5.4, 5.6, 6.4** —
  captured from real runs of `L03.TypesTour` and `L03.VbInterop` (Release) on the build machine; both samples fix the
  culture to invariant and use no clock or randomness.
- **Premium figures** (11,475.00 net · 45.90 stamp duty · 806.46 VAT · 12,327.36 total; 15,319.23; 27,646.59) —
  computed by the samples and asserted in `PremiumTests` / `ReportServiceTests`; illustrative rates, labelled so in
  "Before you start".
- **Compiler diagnostics quoted in prose** — VERIFIED against "Versioning with the Override and New Keywords" and
  reproduced with a throw-away C# project against SDK 10.0.401: leaving out `override` on a matching member of a
  *virtual* base member compiles with warning CS0114 and hides the base member (CS0108 is the same warning for a
  *non-virtual* base member); the lesson names both ids and says Kotlin rejects the omission (table 2.8, story §4,
  Traps). CS0506 (override of a non-virtual member) and CS9035 (a `new Quote { … }` without `Premium`) in the §8
  "break something" paragraph were observed by compiling a throw-away C# project against `L03.Domain`.
- **Default interface members** — VERIFIED: Microsoft Learn ("the class doesn't inherit members from its interfaces";
  default members are reachable only through an interface-typed reference). `DispatchTests` asserts the class has no
  such member; a Visual Basic class must implement the member itself (BC30149, table 7.6).
- **Dependency injection and variance (§7 story, 7.3 note)** — the built-in .NET container resolves the exact closed
  service type only, so a renderer registered as `IReportRenderer<Report>` is not injected into
  `ReportService<QuoteReport>`; the lesson says to register it under each closed type and defers containers to
  lesson 08.
- **Version / feature facts** — VERIFIED (all linked in the PDF): `init` and records C# 9; record structs C# 10;
  `with` works on every struct since C# 10 (`record` adds equality, `==`, `ToString`, `Deconstruct`); `required`,
  static abstract members and generic math C# 11 / .NET 7; primary constructors C# 12 (parameters, not members;
  assignable; stored only when used in a member); `allows ref struct` C# 13; extension members (methods, properties,
  static members, operators) and `field` C# 14; extension indexers, union types and `closed` hierarchies in the C# 15
  preview (`closed` applies to classes, not enums — an enum switch always keeps its default arm); variance only on
  interfaces and delegates and never for value-type arguments; record value equality compares members with their own
  `Equals` (a `List<T>` member compares by reference); a sealed record's clone method is not virtual; the struct
  guideline's four conditions (single value, under 16 bytes, immutable, rarely boxed); Visual Basic 16.9 consumes
  init-only properties; VB's consumption-only strategy. The C# 15 and Visual Basic pages were re-read on 2026-09-20
  (`CHECKED`).
- **Test-backed claims** — each trap in the Traps callout except exhaustiveness over a class hierarchy (C# 14
  cannot express it) has a test that fails if the trap is removed: `DispatchTests` (hiding, default interface member
  not inherited), `CopySemanticsTests` and `MoneyTests` (struct copies, `default(Money)`, boxes), `EqualityTests`,
  `PrimaryConstructorTests` (reflection: one mutable compiler-generated field for `rates`, no field for the
  enumerable `rules`, no properties), `ExtensionTests` (an enum is open).
- **No rubric charts** — the lesson has none; table 7.6 replaced an earlier VB heatmap so every "cannot"
  claim is backed by a compiler test.

## 5 · Presentation

Format 00 via `brief_pdf.py`; code panels from `lesson_kit`, wrapped locally so each numbered panel is listed in the
Contents and VB interpolated strings lose Pygments' red error box. Mermaid 2.2 is a subgraph-free `flowchart LR`
(mermaid ignores `direction` inside a subgraph whose nodes link outside it, which scrambled the first layout) with a
distinct slate fill for the local variables; 2.7 and 4.3 keep the type names in the leaf nodes and short edge labels,
which puts their text at 7.8 pt and 7.3 pt (measured with pymupdf; the body is 8.2 pt); 7.1 is `classDiagram` with
`direction TB` (LR rendered the class boxes too small). Mermaid `classDef` names avoid the renderer's CSS class names
— `val` and `box` shrank node text to the KPI-value / box styles, so the lesson uses `vty`, `bxd`, `refv`, `obj`,
`q`, `start`, `stat`, `dyn`, `loc`, `ok`, `stop`. An html style block keeps `h2` headings (tables, figures) and
callout headings with their content and lets link text break at word boundaries (the renderer's `break-all` split
`(What's new …)` mid-word); long generic identifiers are wrapped in a local `nw()` helper (`white-space:nowrap`).

Pagination: an empty `break-before:page` block after the Contents starts §1 on page 2, so its heading is not stranded
at the foot of page 1. Panels 3.1, 4.4, 4.7, 6.1, 7.7 and 8.2 pass `keep=True`, so they are not cut mid-declaration
even though they are longer than the kit's keep threshold. The price is foot gaps of at most about a quarter of a page
(the largest: page 20, where panel 8.3 jumps, 24 %; then pages 9, 6 and 14, 13–18 %). Panel 7.2 and table 4.6 still
continue on the next page (2.8 too, with its header repeated); keeping 7.2 and 7.6 whole as well pushed the lesson to
23 pages. The 2.3 note, the 2.2 caption and the 2.4 note are worded so 2.4's note does not split across pages 4–5. The
two long region names in compare headers were shortened (`Extensions.cs`, region `vb-csv`) so no header truncates.
Compare sides ≤ 62 characters, code panels ≤ 100 (no width warnings).

## 6 · Inputs

`roster.py`; repo `global.json`, `Directory.Build.props`. Samples:

- `L03.Domain` — C# library: `Money` (readonly record struct + `IAdditionOperators`), `QuoteId` / `PolicyNumber`
  (static abstract `IIdentifier<TSelf>`), `Ids` (reified generic parsing), `Vehicle` / `Driver` / `QuoteRequest` /
  `Premium` / `Policy` records, `Quote` (required / init / `field`), `IRateTable` (default interface method),
  `RatingRule` hierarchy (virtual vs hidden), `PremiumCalculator` (primary constructor), `Extensions.cs`
  (`CoverageClassExtensions`: C# 14 extension blocks; `DriverExtensions`: a classic extension method), `Vin` /
  `VinRecord` / `BrokenVin` (equality), `Totals.Sum` (generic math), `Samples`.
- `L03.Reports` — C# library: `Report` / `QuoteReport`, `IReportRenderer<in T>`, `IReportSource<out T>`,
  `ReportRenderer<T>` (template method), CSV / text / JSON / summary-card renderers, `ReportService<T>`.
- `L03.Domain.Tests` (xUnit v2, 42 cases) and `L03.Reports.Tests` (xUnit v2 + `Microsoft.CodeAnalysis.VisualBasic`
  5.9.0, 29 cases including `VbCompilerTests`).
- `L03.TypesTour` — C# console printing every measurement (including the `Tally` struct behind panel 2.4);
  `L03.VbInterop` — VB console consuming the records, operators and required members, a VB
  `MustInherit`/`Shadows` hierarchy that mirrors the C# one, a VB generic method, and `VbCsvRenderer` inheriting the C#
  generic base class.

Sources (all linked in the PDF):
- What's new in C# 14 — https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14
- What's new in C# 15 (preview) — https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-15
- The history of C# — https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-version-history
- Extension member declarations — https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/extension
- The `field` keyword — https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/field
- Primary constructors — https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/tutorials/primary-constructors
- `required` modifier — https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/required
- Records — https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/record
- Structure types — https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/struct
- Choosing between class and struct — https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/choosing-between-class-and-struct
- Boxing and unboxing — https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/types/boxing-and-unboxing
- Versioning with override and new — https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/classes-and-structs/versioning-with-the-override-and-new-keywords
- `interface` keyword — https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/interface
- Covariance and contravariance in generics — https://learn.microsoft.com/en-us/dotnet/standard/generics/covariance-and-contravariance
- Generic math — https://learn.microsoft.com/en-us/dotnet/standard/generics/math
- Equality comparisons — https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/expressions/equality
- What's new for Visual Basic — https://learn.microsoft.com/en-us/dotnet/visual-basic/whats-new/
- Visual Basic language strategy — https://learn.microsoft.com/en-us/dotnet/visual-basic/getting-started/strategy
- Roslyn VB compiler package — https://www.nuget.org/packages/Microsoft.CodeAnalysis.VisualBasic (not linked in the PDF)

## 7 · Invariants

- Every premium is illustrative, not a real tariff; the lesson says so before the first figure.
- `TOUR_OUT` is the single source for the byte and method figures: charts 2.5 / 2.6 / 5.1, diagram 2.2, the cards and
  the KPI tiles parse it, so re-capturing the tour output updates all of them together.
- Table 7.6 may only cite error ids asserted in `VbCompilerTests.cs` (enforced by `_vb_limits()` at build).
- `VbCompilerTests` asserts the complete error set of each snippet and that the call-site workarounds compile, so a snippet
  that breaks for another reason fails the test instead of silently passing.
- `DispatchTests` asserts the three lines of panel 4.2 and that a class does not inherit a default interface member;
  `PrimaryConstructorTests` asserts the capture behaviour panel 3.4 describes; `EqualityTests` asserts the
  broken-hash `False`; `ReportServiceTests` asserts the CSV that `L03.VbInterop` compares with its VB renderer.
- Boundaries: syntax, nullability, patterns and `decimal` → 02; collections/LINQ → 04; DI lifetimes and container
  registration → 08; test frameworks and coverage gates → 10; VB semantics and migration → 06. Each gets one
  sentence and `ref(n)`.
- No employer, client or personal names; experience is referenced generically ("the multi-format report framework
  you have built before").

## 8 · Known gaps

- ⚠ Byte counts are from one 64-bit run on .NET 10.0.12; a 32-bit process or a future runtime can report different
  object sizes (the ratios are the point, as the lesson says).
- ⚠ `TOUR_OUT` and `VB_OUT` are pasted text; if a console's output changes, re-capture them — the build does not
  re-run the consoles.
- ⚠ `VbCompilerTests` uses the NuGet build of Roslyn 5.9.0 (5.9.0-1.26357.3), while SDK 10.0.401 carries a later
  5.9.0 build (5.9.0-1.26423.113); the error ids were cross-checked with the SDK compiler once, by hand.
- ⚠ C# 15 statements describe a preview; union types, `closed` and extension indexers can
  change before .NET 11 ships (re-read on Microsoft Learn on 2026-09-20; the page was last updated 2026-09-14).
- ⚠ CS0506, CS0114 and CS9035 (the hiding rule and the "break something on purpose" paragraph) were checked by hand
  and are not asserted by a test; the hiding behaviour itself is (`DispatchTests`).
- ⚠ The claim that the built-in DI container ignores variance rests on a probe run during review, not on a sample
  in this lesson (lesson 08 owns container behaviour).
- ⚠ Inline Java and Kotlin panels (3.3, 4.1, 5.2, 5.3, 6.1) are not compiled.
- ⚠ Panel 7.2 (a long panel), table 4.6 (two rows) and the concept map 2.8 continue on the next page; page 20 ends
  about a quarter empty because kept panel 8.3 jumps.
- ⚠ §7 spends about two and a half pages on the Visual Basic boundary (7.4–7.8) although lesson 06 owns VB
  semantics; table 7.6 is the single place that lists each limit, the notes point to it instead of repeating it.
