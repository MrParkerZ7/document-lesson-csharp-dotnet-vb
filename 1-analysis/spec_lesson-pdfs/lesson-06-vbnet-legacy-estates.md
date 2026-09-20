# Unit spec — lesson-06-vbnet-legacy-estates.pdf

Built to `_standard.md`. Content module `0-script/lessons/lesson_06.py`. Samples
`lesson-06-vbnet-legacy-estates/samples/`. Plan: `_curriculum.md` § "06 · VB.NET for Legacy Estates".

## 1 · Purpose

Equip a Java EE / Kotlin / TypeScript architect to own a Visual Basic .NET estate without writing new VB: read VB
fluently (keywords, file options, events), name the VB semantics that silently change numbers when code is ported
(Option Strict Off, round-half-to-even `CInt`, `/` on integers, `DateDiff` year parts, `Dim a(n)`, Option Compare
Text, `And`, `ByRef` copy-back), cross the VB ↔ C# boundary safely, choose a route per project from what .NET 10
still supports for VB, and prove a C# port with VB characterization tests plus a boundary-value parity grid. All
premiums use the MotorQuote vocabulary and the track's **one canonical tariff** (`_curriculum.md`, "Canonical tariff"),
labelled **illustrative, not a real tariff**. The legacy VB keeps its own whole-baht Integer rounding on purpose (its
subject); its rate, loading, claims and no-claim values equal the canonical table.

## 2 · Ownership & cadence

Owner **claude**, regenerable. Re-verify when a new .NET major ships (November) or a new Visual Studio release
changes the "What's new for Visual Basic" page: the "current version" KPI (17.13 / Visual Studio 2026), the VB
template count of `dotnet new list --language VB` (captured in `VB_TEMPLATES`), the tooling card 6.5 (CodeConverter
release), the Upgrade Assistant / AWS Transform sentence in the §6 story and timeline 2.4. Re-capture panels 4.6, 5.4
and 8.2 whenever the samples' console output changes. The AWS Transform sentence in the §6 story (VB.NET listed as a
preview language) is re-checked against its docs page at the same time; tool status and requirements are owned by
lesson 12.

## 3 · Structure

17 A4 pages (the last holds only the closing callout).

| § | Heading | Blocks |
|---|---|---|
| — | Contents | `toc` depth 2 · html style block (callout heading keep-with-items; unbreakable panels cannot leave a 2-line tail — `orphans`/`widows` 6 on code) |
| 1 | Why Visual Basic is your problem, not your language | story · `kpi` 1.1 (5 tiles: VB 17.13, 14 VB templates, 50,176 grid, 44.9 % worst mistake, 655 sample lines) · `legend` (VB, C#, legacy, architecture, tooling) · info callout "Before you start" (4; item 3 names the canonical tariff, the one deliberate variant - whole-baht Integer rounding, worked example 8,933 against the canonical 8,933.71 - and "illustrative, not a real tariff") |
| 2 | Where VB.NET lives — and what .NET 10 still runs | story · table 2.1 (9 workloads; the two web-era rows say "not demonstrated here — host in C#") · mermaid 2.2 flowchart LR (7 Framework workloads → .NET 10 route) · chart 2.3 bar (VB templates by workload) · mermaid 2.4 timeline (4 eras; the caption says to date a legacy file by its syntax) |
| 3 | Reading VB fluently — a map from the C# and Java you already read | story · mapping 3.1 (24 rows, incl. `With` and `Sub`/`Function`; the `==` row names BC30452 and points to lesson 03 §7.5) · cards 3.2 (6 constructs in three bands of 2) · code 3.3 (`WithEvents` declarations in the designer file) · code 3.4 (the `Handles` handler) |
| 4 | Semantics that bite — where a line-by-line port changes numbers | story · code 4.1 (top of `LegacyPremium.vb`, cut from the sample down to the implicit Integer conversion) · code 4.2 (`Loose.vb` late binding) · code 4.3 (`On Error Resume Next`) · code 4.4 (`And`/`AndAlso`/`IIf`/`If()`) · code 4.5 (upper bounds, `/` vs `\`, checked `Integer.MaxValue + 1`) · compare 4.6 (captured `L06.VbSemantics` output, two halves) · chart 4.7 grouped bar (three rounding rules at four midpoints) · compare 4.8 (Java instincts ↔ C# `VbCompat`) |
| 5 | VB ↔ C# interop — one runtime, two compilers' rules | story (each paragraph opens from the Kotlin ↔ Java equivalent) · code 5.1 (C# adapter calling a VB `Module`) · code 5.2 (partner C# SDK with a case-only collision) · code 5.3 (VB `ByRef` property copy-back, `With {…}` initializer) · code 5.4 (captured BC31429 / BC30456) · table 5.5 (9 interop rules, the records row says VB 16.9 reads init-only and compares records by value; heading kept with the table) |
| 6 | Migration strategy — characterize, strangle, retarget, port | story · code 6.1 (VB xUnit characterization tests) · mermaid 6.2 flowchart LR (route per project) · mermaid 6.3 stateDiagram-v2 (two composite states: VB serves traffic / C# serves traffic) · mermaid 6.4 sequenceDiagram (VB screen → C# rule, parity block in CI) · cards 6.5 (CodeConverter · characterization and parity tests) · twocol 6.6 (convert vs rewrite) |
| 7 | Parity testing — prove the port before anyone switches | story · compare 7.1 (VB loadings ↔ C# port loadings) · compare 7.2 (VB discount table and total ↔ C# port) · code 7.3 (the `PortChange` enum) · code 7.4 (`QuoteGrid`) · code 7.5 (parity gate: faithful port, worked example 8,933.71 / 8,933, theory of pinned counts) · code 7.6 (`VbCompat` checked against `Microsoft.VisualBasic`) · chartrow 7.7 hbar (premiums changed per port change) + 7.8 bar (values per grid dimension) |
| 8 | Hands-on — run the estate in miniature | story (incl. two break-it exercises) · code 8.1 commands · code 8.2 (captured `L06.ParityReport` output, with a hand-check of the worked example, the `class1` sample and the first half-up mismatch) · chartrow 8.3 hbar (LOC by migration role) + 8.4 donut (VB vs C# LOC) · warn "Traps" (5) · ok checkpoint (4) · summary "Check yourself" (7) · footer (Next: lesson 07) |

Counts checked by `lint_blocks`: 8 numbered stories · 1 mapping · 4 cards bands (2 cards each, so ≤ 3) · 5 mermaid
(flowchart ×2, timeline, stateDiagram-v2, sequenceDiagram) · 6 charts · 22 code panels (18 `code` + 4 `compare`) ·
C# ↔ VB compare 7.1 and 7.2 · Java ↔ C# compare 4.8 · twocol 6.6 · 2 extra tables (2.1, 5.5) · 25 distinct links.

Boundary with lesson 12: this lesson names the .NET Upgrade Assistant deprecation and AWS Transform's VB.NET preview in
one sentence with `ref(12)`; the tool comparison, requirements and status live only in lesson 12 § 7.

## 4 · Derivation

- **KPI "Visual Basic 17.13"** — VERIFIED: "What's new for Visual Basic" lists *Visual Basic 17.13 / Visual Studio
  2026* as the current version; 17.13 recognizes the `unmanaged` constraint and `OverloadResolutionPriorityAttribute`
  (the "two runtime features" in the §1 story).
- **KPI "VB templates 14"**, chart 2.3, table 2.1 template column — MEASURED: `dotnet new list --language VB` on the
  build machine with SDK 10.0.401 (classlib, console, mstest + mstest-class, nunit + nunit-test, xunit, winforms,
  winformslib, winformscontrollib, wpf, wpflib, wpfcustomcontrollib, wpfusercontrollib), stored as the
  `VB_TEMPLATES` constant grouped by workload; Web and Worker are 0.
- **KPI "Parity grid 50,176"**, chart 7.7, KPI "Worst port mistake 44.9%", the 6.1 %–44.9 % range in §1
  and §7, the per-change percentages in the Traps callout — MEASURED: output of `L06.ParityReport`, stored verbatim as
  the module's `REPORT` constant (the same text is panel 8.2) and parsed into `PARITY`; every count is pinned by the
  `GridMeasuresEveryPortChange` theory, so the samples fail if they drift. Captured 2026-09-20: faithful port 0
  mismatches; TruncatingCasts 22,520 · CaseSensitiveCodes 16,128 · HalfUpRounding 11,324 · BirthdayAge 8,064 ·
  IntegerDivision 3,072 · FiveElementTable 3,072 · DecimalRates 304.
- **Chart 7.8 and the note of 7.4 (7 × 8 × 4 × 2 × 7 × 4 × 2 × 2 = cover codes · sums insured · birth dates · start dates · licence months · claims 0-3 · commercial · engine cc)** — MEASURED: `_grid_dimensions()` parses the
  array literals of `QuoteGrid.cs` at build time and raises if their product differs from `PARITY_CASES`.
- **KPI "Lesson 06 samples 655 lines (VB 291 · C# 364 · 9 projects)"**, chart 8.3, chart 8.4, card 8 "Cost" —
  MEASURED with `loc()` over every `.vb`/`.cs` file per project; projects containing `.vb` files count as VB. Chart
  8.3 groups projects by role (VB rule; VB characterization tests; C# port; parity kit + report; C# parity tests;
  trap demos = `L06.VbSemantics` + `L06.PartnerSdk`; VB screen). The module raises if the project count on disk is
  not 9 or if the parity kit + tests stop outweighing the rule + port (the claim in note 8.3).
- **Test-case counts (11 VB, 11 C#)** in note 8.4 and the checkpoint — MEASURED by `_test_cases()` (each
  `[Fact]`/`<Fact>` and each `InlineData` row); they equal the `dotnet test` totals on the build machine.
- **Chart 4.7** — MEASURED: the `CInt` / `Fix` / `AwayFromZero` columns of the `L06.VbSemantics` rounding lines
  (panel 4.6); the C# `(int)` and Java `HALF_UP` series names are labelled as "named by the rule they share".
- **Panels 4.6, 8.2** — captured from real runs of `L06.VbSemantics` and `L06.ParityReport` (Windows 11, SDK
  10.0.401, runtime 10.0.12; re-captured 2026-09-20 after the canonical-tariff alignment). **Panel 5.4** — captured from
  `dotnet build L06.VbSemantics -p:DefineConstants=SHOW_CASE_COLLISION=True` / `SHOW_MY_COMPUTER=True`, long
  lines wrapped for print (stated in the panel header). The reported positions are `Program.vb(97,27)` and `Program.vb(107,27)` (re-measured 2026-09-20; nothing in the module checks them, so re-capture on any `Program.vb` edit). `_MyType="Empty"` was confirmed in `FinalDefineConstants`
  with and without the override, so BC30456 is not an artefact of replacing `DefineConstants`.
- **Canonical tariff (added 2026-09-20)** — the legacy `LegacyPremium.CalcPremium`, its C# port and the grid use the
  curriculum's table: Class 1 2.1 % · Class 2 Plus 1.2 % · Class 3 Plus 0.9 % · Class 3 0.4 %; young driver +20 %
  (age < 25 by `DateDiff` year parts in the legacy, by birthday in `CanonicalTariff`); claims 0 → +0 %, 1 → +10 %,
  2 → +25 %, 3 or more → declined (`-1` and the reason "3+ claims in 5 years"); commercial +25 % or +35 % above 3,000 cc;
  no-claim ladder 0/20/25/30/40/50 % by claim-free years (licence years when there are no claims); stamp duty 0.4 %,
  VAT 7 %. The signature dropped `claimFreeYears` (derived from `licenceMonths`) and gained `engineCc`; the old
  1,000 floor and the "licence under two years" loading are gone. The deliberate variant: every step rounds to whole
  baht in `Integer` (banker's), so the legacy prices the worked example at **8,933** where `CanonicalTariff.Total` gives
  **8,933.71** — pinned by `WorkedExampleIsTheCanonicalTotalInWholeBaht`, and stated in one sentence in "Before you
  start", note 7.5 and the 8.2 hand-check. The worked example inputs: CLASS1, 550,000, born 2002-06-15, start
  2026-01-01, 48 months, 0 claims: base 11,550 · +20 % = 13,860 · −40 % = net 8,316.00 · duty 33.26 · VAT 584.45.
- **Hand-checks in note 8.2** — arithmetic, each confirmed against the report: `class1 287500`, born 2001-12-31, 18 m,
  0 claims: base 6,037.5 → 6,038 (banker's), licence 1.5 yr → 2 (25 %), discount 1,509.5 → 1,510, net 4,528, duty 18,
  VAT 318, total 4,864, and the port agrees. First HalfUpRounding mismatch: `CLASS1 205000` 6 m → licence 0.5 yr;
  banker's stores 0 years (no discount, 4,625), half-up stores 1 year (20 % discount, 3,700).
- **DecimalRates story (7)** — MEASURED: `5,850 × 0.35` is 2,047.4999999999998 in `Double` (legacy rounds down to
  2,047) and exactly 2,047.5 in `Decimal` (rounds half to even up to 2,048), first mismatch `CLASS2PLUS 487500 … 6m 0cl
  com 3001cc: legacy 8484, port 8485`; 304 of 50,176 = 0.6 %. The story therefore says the "obvious" decimal fix still
  moves prices, so it ships on its own.
- **§8 break-it figures** — MEASURED on the build machine by editing and restoring the samples: `VbCompat.CInt(double)`
  as a plain cast → 7 of the 11 parity tests failed, first faithful-port mismatch `CLASS1 205000 born 2001-12-31 start
  2026-01-01 6m 0cl com 3000cc: legacy 5781, port 5780`; `Option Compare Binary` in `LegacyPremium.vb` → 3 of the 11
  VB characterization tests failed (the `class1` row and the `class1` / `  Class1 ` cases). The module raises if the
  test counts stop being 11 + 11, because these figures were measured against that suite.
- **Overflow (§4 story, panels 4.5 and 4.6)** — MEASURED: `Integer.MaxValue + 1` throws `OverflowException` in the VB
  sample; the `checked(…)` around `VbCompat.CInt` is the C# counterpart. The paragraph links `-removeintchecks`
  (Microsoft Learn) and points to lesson 02 §8.3, which does measure both sides.
- **Table 2.1 support column, diagram 2.2, §2 story** — VERIFIED (web and worker rows: no template MEASURED; "not demonstrated here" because no VB web project is built): VB strategy (no new workloads; Windows Forms and
  libraries are core scenarios); .NET 5 VB plan of 11 Mar 2020 (class library, console, Windows Forms, WPF, worker
  service, ASP.NET Core Web API); VB WinForms Application Framework in .NET 5 (23 Nov 2020); Razor syntax "consists
  of Razor markup, C#, and HTML"; Web Forms → Blazor migration guidance; VB6 runtime supported for the lifetime of
  supported Windows, VB6 IDE unsupported since 8 Apr 2008.
- **Timeline 2.4** — VERIFIED from "What's new for Visual Basic" (VS .NET 2002 first VB .NET; VS 2005 `My`; VS 2008
  LINQ, XML literals, `If` operator; VS 2010 implicit line continuation; VS 2012 Async/Await; VS 2015 VB 14 NameOf and
  interpolation; VS 2017 VB 15 tuples; VS 2019 VB 16.0 first .NET Core-focused version, VB 16.9 init-only consumption;
  VS 2026 VB 17.13 `unmanaged` constraint).
- **Mapping 3.1 and §4 story semantics** — VERIFIED: type conversion functions (fraction exactly .5 → nearest even;
  `Fix`/`Int` truncate); `Math.Round` rounds midpoints to even by default; `/` widens integral operands to `Double` (Single gives Single, Decimal gives Decimal);
  `DateDiff` Year interval uses year parts only; array declarations give the highest index; Option Compare Text is
  case-insensitive by locale (`VbCompat.TextEquals`, not `OrdinalIgnoreCase`), default Binary; `And` always evaluates both operands; `"" = Nothing` is True and
  `Is Nothing` is the recommended test; the VB Defaults initial Option Strict is Off; `On Error` still compiles
  (structured handling recommended); properties are modifiable ByRef arguments and parentheses force ByVal.
- **§5 CLS paragraph** — VERIFIED: identifiers must differ by more than case (language independence / CLS page).
  CS3005 MEASURED: adding `[assembly: System.CLSCompliant(true)]` to `L06.PartnerSdk` (temporarily, then restored)
  produced `error CS3005: Identifier 'PartnerRateCard.loading(int)' differing only in case is not CLS-compliant`
  — an error because the repo treats warnings as errors.
- **Cards 6.5 and the §6 tooling sentence** — VERIFIED 2026-09-16 (AWS Transform re-checked 2026-09-20): CodeConverter GitHub releases (v10.0.1 published 1 Mar 2026; v10.0.0: .NET 10
  required for `codeconv`, .NET Framework support dropped in the command line, the VS extension still converts it;
  README: VB → C# quality much higher than C# → VB, `codeconv` still needs VS 2026 18.0+); Upgrade Assistant overview
  (C# and VB projects; include note "officially deprecated", use the GitHub Copilot modernization agent); GitHub
  Copilot upgrade FAQ (ms.date 2026-07-07: Copilot Free from VS 2026 18.1, internet required, local Git repository,
  working branch with one commit per task, C# and Visual Basic, targets .NET 8 or later, suggestions not guaranteed
  to follow best practices). Card 8 figures are MEASURED (LOC, grid, `dotnet test` durations under 1 s).

## 5 · Presentation

Format 00 via `brief_pdf.py`; code panels from `lesson_kit`, listed in the Contents at level 2 through the module's
`listed()` helper (as lesson 01), which also strips Pygments' red error boxes around VB `$"` interpolated strings.
A panel of more than 18 lines is emitted by `pcode()` as **two blocks** — a small Contents-anchored `.codeh` heading and
an unlisted panel — because the renderer makes every anchored block `break-inside:avoid`, which stopped 17 panels from
ever splitting (the earlier build left page 13 36 % empty); five panels are split this way (4.1, 6.1, 7.4, 7.5, 7.6).
A module style rule (`.code:not(.keep){overflow:visible}` and `.code pre{orphans:6;widows:6}`) lets them split
without a 2-line tail. Compare panels stay whole (≤ 24 lines). Source links are `nolink()` spans (`white-space:nowrap`)
so a long label moves to the next line instead of breaking mid-word; `short()` keeps the same link with a short
label for narrow table cells.
Diagram 2.2 is `flowchart LR` with two subgraphs and no subgraph `direction`, tightened with
`nodeSpacing 18 · rankSpacing 40 · padding 12`; its caption names the grey nodes. Timeline 2.4 groups eight releases
into four eras at `fontSize 16px`. Diagram 6.2 is `flowchart LR` (TB filled a page). Diagram 6.3 uses two composite
states joined by one transition and the repo's language colours (blue = VB, violet = C#, as 2.2, 6.2 and the tags).
Sequence 6.4 writes `C#35;` for `#` in participant names, uses `mirrorActors: false`, and follows the §6 story that
defines the strangler and the parity run. The 3.2 deck is split 2 + 2 + 2 and the 6.5 deck is one band of 2; table
5.5's heading is a separate `_keep_with_next` block. Compare sides ≤ 62 characters, code panels ≤ 100 (no
`lesson_kit` width warnings; the discount region of `LegacyPremium.vb` and `PremiumCalculator.cs` is formatted one
statement per line so 7.2 fits).
Visual QA (2026-09-20, after the final build of the cross-review fixes): all five sheets and the full-size pages 1, 2,
4–16 were inspected (page 3, the 2.2 diagram and 2.3 chart, is unchanged from the previous pass). Measured with
PyMuPDF at 36 dpi, the largest interior blank run per page is 20.7 % (page 3: diagram 2.2 and chart 2.3, the 2.4
timeline needs 40 %), 16.2 % (page 15), 10.9 % (page 11), 9.3 % (page 2) and 5.9 % (page 14); no other page exceeds
4 %; page 17 (last) carries only the closing callout. Every captured panel was diffed against a fresh run: 4.6 and 8.2
match `L06.VbSemantics` and `L06.ParityReport` character for character.

## 6 · Inputs

`roster.py`; repo `global.json`, `Directory.Build.props`; samples:
- `L06.LegacyRating` (VB library, `Option Strict Off` + `Option Compare Text`, Double rates, `-1` sentinel, `ByRef`
  reason, `Dim ncb(5)`) and `L06.LegacyRating.Tests` (VB xUnit v2 characterization tests, 11 cases)
- `L06.ModernRating` (C# faithful port: `QuoteRequest` record, `PremiumCalculator`, `VbCompat`)
- `L06.Parity` (C# `QuoteGrid`, `LegacyAdapter`, `CanonicalTariff` — the decimal reference implementation of the canonical
  tariff —, `NaivePort` with 7 injected changes — the `PortChange` enum is region `port-changes` —, `ParityRunner`),
  `L06.Parity.Tests` (C# xUnit v2, 11 cases incl. the worked-example test and the VB-runtime oracle), `L06.ParityReport` (C# console)
- `L06.PartnerSdk` (C# library with a case-only collision, the canonical claims loadings 0.10 / 0.25 and a `ref` + optional method), `L06.VbSemantics` (VB
  console demonstrating the traps; `Loose.vb` opts out of Option Strict)
- `L06.WinFormsVb` (VB Windows Forms, `net10.0-windows`, `WinExe`, build-only, calls the C# port)

Sources (all linked in the PDF):
- Microsoft Learn — Visual Basic language strategy · What's new for Visual Basic · Razor syntax reference · Migrate
  from ASP.NET Web Forms to Blazor · Support Statement for Visual Basic 6.0 · Type conversion functions · Math.Round ·
  / operator · DateAndTime.DateDiff · Arrays in Visual Basic · Option Compare statement · Option Strict statement ·
  And operator · Nothing keyword · On Error statement · Differences between modifiable and nonmodifiable arguments ·
  Force an argument to be passed by value · Language independence and the CLS · Strangler Fig pattern ·
  Anti-corruption Layer pattern · .NET Upgrade Assistant overview · GitHub Copilot upgrade for .NET FAQ
- .NET Blog — Visual Basic support planned for .NET 5.0 · Visual Basic WinForms apps in .NET 5 and Visual Studio 16.8
- GitHub — icsharpcode/CodeConverter (README, releases, changelog)

## 7 · Invariants

- Every premium, loading and total is **illustrative, not a real tariff**, and equals the canonical tariff
  (`_curriculum.md`); the "Before you start" callout says so and names the one deliberate variant (whole-baht Integer
  rounding in the legacy). None of the pre-2026-09-20 values (rates 0.018 / 0.020 / 0.022 / 0.025, flat 1,800 / 2,400
  Class 3, 0.15 per claim, 0.05 or 0.10 per licence year, `Math.Ceiling` on duty, the old worked-example totals, the
  94,080-case grid) may reappear.
- `GridMeasuresEveryPortChange` pins every count in `PARITY`; `WorkedExampleIsTheCanonicalTotalInWholeBaht` ties the legacy to the canonical 8,933.71; `FaithfulPortMatchesLegacyOnEveryGridCase` must stay
  at 0 mismatches; `VbCompatAgreesWithTheVisualBasicRuntime` keeps `VbCompat` honest against `Microsoft.VisualBasic`.
- `QuoteGrid` array literals stay one-per-field (`public static readonly T[] Name = [ … ];`) so `_grid_dimensions()`
  can parse them; their product must equal `PARITY_CASES`.
- `LegacyPremium.vb` keeps `Option Strict Off` and `Option Compare Text` at the top — sections 4, 6 and 8 depend on
  them; `L06.VbSemantics` keeps the case-collision and `My.Computer` lines behind `#If` so the sample builds.
- The C# port reproduces quirks through named `VbCompat` helpers, never inline.
- Boundaries: runtime/TFMs → lesson 01; `decimal`, nullability → 02; VB `Async`/`Await` → 05; solutions and mixed
  C#/VB builds → 07; ASP.NET Core host for VB libraries → 08; System.Web/WCF/IIS porting map, upgrade tooling
  (Upgrade Assistant, Copilot app modernization, AWS Transform) and upgrade at estate scale → 12. Each gets one sentence and `ref(n)`.
- No employer, client or personal names; experience is referenced generically (Java EE / JSP maintenance, 100%-coverage
  test suites, a large multi-application estate, Kotlin and Java in one Gradle build). Golden-master and strangler-fig
  are named as techniques, not as the reader's history.
- The port's flat `QuoteRequest` mirrors the legacy signature; §7 says the reshape into the running example's
  `Vehicle` / `Driver` / `Money` is a later, separately gated step. Every premium shown is labelled illustrative.

## 8 · Known gaps

- ⚠ `VB_TEMPLATES` and `REPORT` (hence `PARITY`) are constants captured from runs, not recomputed at build; `PARITY` is guarded by the
  pinned theory, `VB_TEMPLATES` is not (re-run `dotnet new list --language VB` when the SDK in `global.json` moves).
- ⚠ Panels 4.6, 5.4 and 8.2 are pasted output; re-capture them if the samples' output changes. The compile-error
  line/column numbers in 5.4 depend on `Program.vb` line positions.
- ⚠ The §8 break-it results (7 of 11, 3 of 11) were measured by hand-editing and restoring the samples; no automated
  check reproduces them.
- ⚠ `L06.WinFormsVb` is build-only; the form was never run interactively.
- ⚠ No VB web project is built here, so the web and worker template gap is stated as "no template, not demonstrated".
- ⚠ `CS7036` for an omitted `Optional ByRef` argument was reproduced once with a scratch C# project referencing the
  built `L06.LegacyRating.dll`; the committed adapter passes the argument, so no sample keeps that result current.
- ⚠ Only verified on Windows; the non-Windows samples target plain `net10.0` but were not run on Linux or macOS.
- ⚠ The CodeConverter card states what its README and changelog say; the converter itself was not run on the samples
  (its command line needs Visual Studio 2026 installed).
- ⚠ The committed `L06.PartnerSdk` deliberately does not set `CLSCompliant(true)` (it must build), so CS3005 was
  reproduced by a temporary edit only; no automated check keeps that result current.
- ⚠ Inline Java panel 4.8 is not compiled.
- ⚠ The legacy `CalcPremium` reads the young-driver age from `DateDiff` year parts (a deliberate quirk), so it differs
  from the canonical tariff's birthday age for a driver born late in a year; the grid measures that as `BirthdayAge`
  (8,064 premiums) and the parity gate treats the legacy behaviour, not the canonical one, as the spec for the port.
