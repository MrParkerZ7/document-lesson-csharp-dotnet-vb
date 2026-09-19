# Unit spec — lesson-02-csharp-language-essentials.pdf

Built to `_standard.md`. Content module `0-script/lessons/lesson_02.py`. Samples
`lesson-02-csharp-language-essentials/samples/`. Plan: `_curriculum.md` § "02 · C# Language Essentials".

## 1 · Purpose

Give a Kotlin / Java 21 / TypeScript architect the C# syntax they will read and review on day one — file shape and
file-based apps, built-in types and `decimal`, strings, rounding and culture, nullable reference types, switch
expressions and patterns, parameters, exceptions and `using` — with each construct mapped to the form they know, the
traps labelled, and the Visual Basic form shown beside it. Everything is taught through the MotorQuote rating rules
(illustrative rates, labelled as such wherever a premium appears).

## 2 · Ownership & cadence

Owner **claude**, regenerable. Re-verify every November, when a new C# version ships with the .NET major: the C# 14
facts (KPI 1.1, §4 story, table 2.6), the C# 15 preview sentence in §5 (closed hierarchies and unions — re-checked
against Microsoft Learn on 2026-09-20; rewrite it once C# 15 ships with .NET 11), the file-based-app directives in §2
(`#:include` needs SDK 10.0.300+), the pattern rubric 5.7 and the "Since" column of table 5.6. Re-capture the output
panels (9.2, 9.3) and the *Printed:* notes whenever a sample's `Console.WriteLine` changes; `blocks()` raises if the
test count drifts from the captured 9.3 run (`CAPTURED_TESTS = 31`).

## 3 · Structure

20 pages at the 2026-09-20 build. Page 1 holds only the title and Contents (a forced page break keeps the §1 heading
from being stranded at its foot).

| § | Heading | Blocks |
|---|---|---|
| — | Contents | `toc` depth 2 (code panels and the twocol are listed through local `listed()` / `figure_heading()` helpers) · lesson-local CSS block · page break |
| 1 | Why this lesson — the syntax you will review tomorrow | story (3 ¶) · `kpi` 1.1 (5 tiles) · `legend` (C#, VB, Java/Kotlin, TypeScript) · info callout "Before you start" (4 items) |
| 2 | The shape of a C# file | story (3 ¶) · mapping 2.1 (15 rows) · compare 2.2 (Kotlin `main` ↔ C# top-level statements) · compare 2.3 (C# `GlobalUsings.cs` ↔ C# `Resources.cs`, a whole file with a file-scoped namespace and no `using` lines) · code 2.4 (the file-based app, whole file) · mermaid 2.5 flowchart LR (project build vs file-based run) · table 2.6 (C# version · release · syntax in this lesson · where it is shown, 9 rows) |
| 3 | Types and values — decimal, strings and culture | story (3 ¶) · compare 3.1 (Java `BigDecimal` ↔ C# `decimal`) · compare 3.2 (Java `setScale` modes ↔ `RatingRules.Round`) · code 3.3 (aliases, `var`, `const`) with the overflow region · cards 3.4 (3 cards) + "3.4 · … (continued)" (3 cards, `toc: False`) · code 3.5 (interpolation, verbatim, raw strings) · code 3.6 (culture traps) |
| 4 | Nullability — annotations, not a type system | story (4 ¶) · compare 4.1 (Kotlin ↔ C# null operators) · code 4.2 (what survives to run time) · mermaid 4.3 stateDiagram-v2 (null-state) · figure heading 4.4 + twocol (Kotlin guarantees vs C# promises) |
| 5 | Control flow and pattern matching | story (3 ¶) · compare 5.1 (Kotlin `when` ↔ switch expression) · compare 5.2 (C# ↔ C#: `BaseRate` ↔ the `(CoverageClass)7` enum trap) · code 5.3 (property + tuple patterns in the rules) · code 5.4 (type/property/declaration patterns, kept whole) · code 5.5 (list patterns) · table 5.6 (pattern kinds by version, 8 rows) · chart 5.7 heatmap (pattern rubric, 5 languages, cell 36) |
| 6 | Methods and parameters | story (3 ¶) · table 6.1 (parameter passing, 7 rows) · compare 6.2 (TypeScript ↔ C# declarations) · code 6.3 (calls, deconstruction, `out var`, C# 14 lambda) |
| 7 | Exceptions and resources | story (3 ¶) · compare 7.1 (Java try-with-resources ↔ C# `using` + filter) · code 7.2 (filter order) · mermaid 7.3 sequenceDiagram (two-pass handling) |
| 8 | Visual Basic alongside | story (3 ¶) · compare 8.1 (C# switch ↔ VB `Select Case`) · compare 8.2 (C# `using var` + filter ↔ VB `Using … End Using` + `Catch … When`) · compare 8.3 (C# unchecked overflow ↔ VB checked-by-default) · table 8.4 (this lesson's C# in VB, 11 rows) |
| 9 | Hands-on — run the tour, the tests and the file-based app | story (3 ¶) · code 9.1 commands · compare 9.2 (captured: C# tour first part ↔ VB tour) · code 9.3 (captured terminal: test run + both file-based runs) · code 9.4 (`PremiumCalculator.Calculate`) · chart 9.5 waterfall (worked example) · chartrow 9.6 grouped bar (C# vs VB lines per region pair) + 9.7 hbar (test cases per tested member) · warn "Traps" (5) · ok checkpoint (4) · summary "Check yourself" (7) · footer (Next: lesson 03) |

Standard minimums as built: 9 numbered stories · 1 mapping · 2 card bands (3 cards each) · 3 mermaid in 3 families
(flowchart, stateDiagram-v2, sequenceDiagram) · 4 charts (heatmap, waterfall, grouped bar, hbar) · 26 code panels
(13 `code` + 13 `compare`) · C# ↔ VB compares 8.1, 8.2, 8.3 (plus the captured-output pair 9.2) · Java / Kotlin /
TypeScript ↔ C# compares 2.2, 3.1, 3.2, 4.1, 5.1, 6.2, 7.1 · 1 twocol · 4 tables besides the mapping (2.6, 5.6, 6.1,
8.4) · 24 distinct links.

## 4 · Derivation

- **KPI "C# 14 · Nov 2025"** — VERIFIED: What's new in C# 14 ("supported on .NET 10") and The history of C#
  ("Released November 2025").
- **KPI "decimal digits 28–29"** and card 2 (16 bytes) — VERIFIED: Floating-point numeric types (float ~6–9 digits, 4
  bytes; double ~15–17, 8 bytes; decimal 28–29, 16 bytes).
- **KPI "Pattern kinds 10"** — VERIFIED: the Patterns reference lists declaration, type, constant, relational,
  logical, property, positional, `var`, discard and list patterns.
- **KPI "Rating test cases"**, chart 9.7 and the "12 of the 31" in note 5.3 — MEASURED at build by
  `test_cases_by_rule()`: `[Fact]` = 1, each `[InlineData]` = 1, `[MemberData(nameof(X))]` = the `{ … },` rows of
  TheoryData property `X`, grouped by the test-method prefix before the first underscore (31 at this build, equal to
  the `dotnet test` totals; per member: AgeLoading 8, BaseRate 5, NoClaimBonus 5, ClaimsLoading 4, UseLoading 3,
  Calculate 2, AgeOn 2, Round 1, TryCalculate 1).
- **KPI "Lesson 02 samples"** — `loc()` over the 16 C# source files (9 in L02.Syntax, 4 in L02.Rating, 2 test files,
  the file-based app) and the 2 VB files: 545 + 149 = 694 lines at this build (MEASURED).
- **Mermaid 2.5** — the "9 .cs files" node label is counted at build from `samples/L02.Syntax/*.cs`; the generated
  file is `<ProjectName>.GlobalUsings.g.cs` (`L02.Syntax.GlobalUsings.g.cs`, confirmed on disk under
  `.build/artifacts/obj/L02.Syntax/debug/`).
- **Table 2.6** — release dates VERIFIED against The history of C# (6 Jul 2015 · 7.0 Mar 2017 to 7.3 May 2018 · 8 Sep
  2019 · 9 Nov 2020 · 10 Nov 2021 · 11 Nov 2022 · 12 Nov 2023 · 13 Nov 2024 · 14 Nov 2025); the "Shown in" column is
  a hand-maintained cross-reference to the panels that use each feature.
- **Table 5.6 "Since" column** — VERIFIED against the version history (constant, declaration and `var` patterns C# 7.0;
  switch expressions, property, positional/tuple patterns and the discard arm C# 8; type-only, relational and logical
  patterns C# 9; extended property patterns C# 10; list patterns C# 11).
- **Chart 5.7 heatmap** — a rubric (yes / some / —) labelled ESTIMATE and "a rubric, not a benchmark" in its caption.
  Facts behind it: JEP 441 (Java 21 pattern switch: `when` guards, `case null`, exhaustiveness for sealed types and
  enums) and JEP 440 (record patterns); Kotlin 2.2.0 (23 Jun 2025) made guard conditions in `when` stable; C# enum
  switches are never proven exhaustive.
- **Rounding (3.2, Traps item 4)** — VERIFIED: `Math.Round(decimal, int)` rounds midpoints to even by default (Math.Round
  reference); MEASURED by the passing test `Round_is_half_away_from_zero_not_bankers` (2.345m → 2.34 by default, 2.35
  with `MidpointRounding.AwayFromZero`); the Java `setScale` results are language facts, not compiled.
- **Chart 9.5 waterfall** — MEASURED: the seven figures are parsed at build by `asserted_premium()` from the
  `Assert.Equal(…m, p.X)` lines of region `worked-example` in `PremiumCalculatorTests.cs`, a passing test (base
  11,550.00 · loadings 2,310.00 · no-claim bonus 4,158.00 · net 9,702.00 · stamp duty 38.81 · VAT 681.86 · total
  10,422.67). The note gives the exact figures; the axis labels are abbreviated by `chart_svg`.
- **Chart 9.6** — MEASURED: `region_loc()` (non-blank, non-comment lines) over five region pairs holding the same
  statements (`TypesTour#money`↔`Tour.vb#money`, `NullsTour#nulls`↔`#nulls`, `RatingRules#age-loading`↔`#select-case`,
  `MethodsTour#declarations`↔`#methods`, `ErrorsTour#resources`↔`#errors`); at this build C#/VB 14/13, 10/12, 8/14,
  15/19, 13/11. The note names the pairs with the largest and smallest VB−C# difference at build time and explains each
  from the fixed `VB_REASON` table. VB is drawn first, so it takes the chart palette's blue, the colour of the VB panel
  header; C# takes teal (the kit's `grouped_bar` takes no colour argument).
- **Captured output** (Windows 11 x64, SDK 10.0.401, 2026-09-16, re-run 2026-09-20 with identical output apart from
  durations): panel 9.2 from `dotnet run` of `L02.Syntax` and `L02.SyntaxVb`; panel 9.3 from `dotnet test … --tl:on`
  (the terminal-logger form an interactive terminal prints — ANSI colour codes and the restore, build and xUnit
  progress lines are left out, as the panel says) and from `dotnet premium-check.cs` / `dotnet premium-check.cs -- 3`;
  the classic `Passed! - Failed: 0, Passed: 31` line quoted in the 9.3 note is the redirected-output form of the same
  run (seen again on 2026-09-20). Every *Printed:* note in §3–§8 quotes the same runs (the tour sets
  `CultureInfo.CurrentCulture` to invariant — a demo choice explained in note 2.2 — and `premium-check.cs` passes the
  invariant culture to each call, so it prints the same digits on any machine).
- **Measured by compiling on the build machine** (quoted in prose): the constant `int.MaxValue + 1` is error CS0220 in
  C# and `Integer.MaxValue + 1` is error BC30439 in VB, so the wrap and the `OverflowException` come only from the
  non-constant `big + 1` of the samples (§3 story, 8.3, Check yourself 2); a decimal attribute argument such as
  `[InlineData(24, 0.20m)]` → error CS0182; inside this repository a file-based app turned an unused variable into
  error CS0219 and `throw e;` into error CA2200 (inherited `TreatWarningsAsErrors`), and its build output went to
  `.build/artifacts/bin/debug/` (the repository's `UseArtifactsOutput`), not the per-user temp cache; the SDK-written
  `L02.Syntax.GlobalUsings.g.cs` contains the seven implicit namespaces plus `System.Globalization` from the project's
  `<Using>` item; `note!.Length` silences CS8602 for that expression only.
- **Verified statements in prose** (all linked in the PDF): file-based apps — `dotnet app.cs` / `dotnet run app.cs`,
  directives `#:package` `#:project` `#:property` `#:sdk` plus `#:include` from SDK 10.0.300, Native AOT publish by
  default (the sample sets `PublishAot=false`), inherited `Directory.Build.props`, `dotnet project convert`; the seven
  implicit usings of `Microsoft.NET.Sdk`; unchecked non-constant integral arithmetic by default and `decimal` throwing
  in both contexts; default string comparison modes and CA1307/CA1309/CA1310 being enabled only through `AnalysisMode
  All`; ICU on Windows since .NET 5; nullable reference types as a compile-time-only feature; `RespectNullableAnnotations`
  (.NET 9, opt-in, explicit nulls on non-generic members only); C# 14 null-conditional assignment (`++`/`--` excluded)
  and modifiers on untyped lambda parameters; C# 13 `params` collections; C# 15 preview closed hierarchies and unions
  with exhaustive switches; CA2200 enabled by default as a warning in .NET 10; exception filters evaluated before
  unwinding; `using` declarations disposed at the end of scope; the dispose pattern for unsealed types; VB `If()`
  short-circuits where `IIf` does not; VB checks integer overflow unless `-removeintchecks`.

## 5 · Presentation

Format 00 via `brief_pdf.py`; code panels from `lesson_kit`. Local helpers in the module (kit requests, as lesson 01):
`listed()` copies a panel's heading onto its block so the Contents lists it, and strips Pygments' red error boxes —
around VB `$"` interpolated strings and around the `#!` / `#:` file-based-app directives; `panel()` / `pair()` wrap
`code()` / `compare()` with it; `figure_heading()` gives the twocol a numbered, kept-with-next heading. A lesson-local
style block keeps callouts unbroken and their headings with their first item, keeps a story heading with its text,
defines the page break after the Contents, caps diagram heights (sequence 3.4 in, state 1.95 in, flowchart 3.6 in) so
the diagrams stay legible without filling a page, and lets a link wrap only at word boundaries (the renderer default
`word-break:break-all` cut link labels such as "Math.Round" in the middle of a word).

Chips: `legend()` lists C#, VB, Java/Kotlin and TypeScript, all of which appear on a card. Status chips follow the
lesson's own text — the optional-argument row, the switch row and card 5 are DIFFERENT because the lesson calls the
difference a trap. Notes put a chip after the bold clause it labels (never inside a sentence). ESTIMATE labels the
rubric 5.7; MEASURED labels notes 9.5, 9.6 and 9.7.

Pagination decisions (from visual QA): the mapping opens §2 so its rows fill the pages around it; the two money compares
precede the card bands in §3; the type-card deck is two bands of three; the breakable parameter table 6.1 precedes the
long calls panel 6.3; panel 5.4 is kept whole (as a split panel it left a three-line tail at the top of the next page);
the version history is a table (2.6) because a mermaid timeline rendered too small to read; diagram 2.5 is a 4-column
`flowchart LR` with compact spacing. Measured on the rasterized pages, the largest bottom gaps at this build are page 4
22 % (diagram 2.5 cannot fit below the file-based-app panel), page 11 22 %, page 9 19 %, page 7 18 % and page 15 17 %
(diagram 7.3 jumps whole); every other page is under 10 % and none reaches a third. The §4 and §7 stories continue onto
the next page. Compare sides ≤ 62 characters and code panels ≤ 100 (no `lesson_kit` width warnings).

## 6 · Inputs

`roster.py`; repo `global.json`, `Directory.Build.props`; samples:

| Project / file | Kind | Regions shown |
|---|---|---|
| `L02.Rating` | C# library: `Model.cs` (MotorQuote nouns), `RatingRules.cs`, `PremiumCalculator.cs`, `Examples.cs` | `age-loading`, `base-rate`, `round`, `rules`, `calculate` (`constants` and `try-calculate` exist and are exercised, not printed) |
| `L02.Rating.Tests` | xUnit v2 (`dotnet new xunit`), 31 cases | `worked-example` (read by chart 9.5, not printed) |
| `L02.Syntax` | C# console tour: `Program.cs`, `GlobalUsings.cs`, `Resources.cs`, `TypesTour.cs`, `StringsTour.cs`, `NullsTour.cs`, `PatternsTour.cs`, `MethodsTour.cs`, `ErrorsTour.cs` | `top-level`, whole `GlobalUsings.cs`, `file-scoped`, `numbers`, `overflow`, `money`, `strings`, `comparison`, `nulls`, `runtime`, `patterns`, `enum-trap`, `list-patterns`, `declarations`, `calls`, `resources`, `filter-order` (`throw-expressions` and `await-using` are exercised, not printed) |
| `L02.SyntaxVb` | VB console tour: `Program.vb`, `Tour.vb` | `select-case`, `errors`, `overflow` (chart 9.6 also reads `money`, `nulls`, `methods`) |
| `file-based/premium-check.cs` | .NET 10 file-based app, `#:project` → `L02.Rating` | whole file |

Sources (all linked in the PDF):
- Microsoft Learn — What's new in C# 13 · What's new in C# 14 · What's new in C# 15 · The history of C# · File-based
  apps (learn.microsoft.com/en-us/dotnet/core/sdk/file-based-apps) · .NET project SDK overview · Floating-point numeric
  types · checked and unchecked · Best practices for comparing strings · Globalization and ICU · Math.Round · Nullable
  reference types · Respect nullable annotations (System.Text.Json) · Patterns · Exception-handling statements · CA2200 ·
  using statement · Implement a Dispose method · VB If operator · VB Try…Catch…Finally · VB -removeintchecks
- OpenJDK — JEP 441 (pattern matching for switch, JDK 21) · JEP 440 (record patterns, JDK 21)
- Kotlin — What's new in Kotlin 2.2 (guard conditions in `when` stable)

## 7 · Invariants

- Every rate, loading and total is labelled **illustrative, not a real tariff** wherever a premium appears (§1 story,
  §9 story, chart 9.5 caption, `RatingRules.cs` and `Model.cs` comments).
- The worked example (10,422.67 THB) is asserted component by component in `Calculate_matches_the_worked_example`;
  chart 9.5 reads those assertions, so the chart cannot drift from the tested code.
- Test-method names start with the rule under test (`AgeLoading_…`, `Calculate_…`); every TheoryData row stays on its
  own `{ …, … },` line — `test_cases_by_rule()` depends on both.
- `CAPTURED_TESTS` equals the measured test count, or the build fails and panel 9.3 must be re-captured.
- The VB tour keeps demonstrating the reversed overflow default (it throws where the C# tour wraps), and both tours keep
  printing the lines quoted in 9.2 and in the *Printed:* notes. The C# and VB region pairs behind chart 9.6 keep holding
  the same statements.
- `premium-check.cs` keeps LF line endings and no BOM (it starts with a shebang).
- Section numbers used in table 2.6's "Shown in" column and in cross-references (card 1 → 3.3, card 6 → 3.6, the 2.4
  note → 5.5, 3.2 → 9.4, 8.2 → 7.2, the §7 story → 2.3, the §1 story → table 2.6) match the headings.
- Boundaries: records/classes/generics → lesson 03; LINQ, lambdas, collections → 04; async → 05; VB semantics in depth
  → 06; test frameworks and xUnit v3 → 10. Each gets one sentence and `ref(n)` here. The **dispose pattern** is given here
  (one sentence in the §7 story, linked to Microsoft Learn) because lesson 03 does not cover it.
- No employer, client or personal names; experience is referenced generically ("~30 external partners").

## 8 · Known gaps

- ⚠ `verify_samples.py` only discovers `.csproj` / `.vbproj`: the file-based app is **not** built or run by the gate.
  It was run by hand on the build machine (both invocations in 9.3, re-run 2026-09-20).
- ⚠ Output panels and *Printed:* notes are pasted text; only the test count is guarded. Durations in 9.3 (1.0 s,
  0.9 s, 2.1 s) vary per run.
- ⚠ The culture outputs (`FİLE`, `1/10/2569`, the soft-hyphen `IndexOf`) depend on the ICU data of the machine; a
  container in globalization-invariant mode prints different results, and the lesson does not demonstrate that
  (lesson 12 owns containers).
- ⚠ KPI "Pattern kinds 10" counts the Patterns reference's summary list; the same page also documents parenthesized
  patterns and the C# 15 preview closed-hierarchy and union patterns in their own sections.
- ⚠ Rubric 5.7 is a judgement on the "some" cells (e.g. Java record patterns counted as partial property patterns); it
  is labelled ESTIMATE and a rubric, not a benchmark.
- ⚠ Pagination depends on block order, the CSS caps and the forced break after the Contents; editing text in §2, §3 or
  §5 can move a gap or split a panel — re-run visual QA after any content change. Panels 3.6, 4.2, 5.3, 6.3 and 7.2
  (longer than 18 lines, not kept) may split across pages.
- ⚠ Table 2.6's "Shown in" column and the section cross-references are maintained by hand and must follow any
  renumbering.
- ⚠ Inline Kotlin, Java and TypeScript panels are not compiled.
