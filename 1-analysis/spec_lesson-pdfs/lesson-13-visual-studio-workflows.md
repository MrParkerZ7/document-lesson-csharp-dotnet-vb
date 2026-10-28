# Unit spec — lesson-13-visual-studio-workflows.pdf

Built to `_standard.md`. Content module `0-script/lessons/lesson_13.py`. Samples
`lesson-13-visual-studio-workflows/samples/`. A **companion** lesson (added 2026-09-20, phase E · Tooling, 5 h): read
after lesson 07 or whenever the team lives in the IDE; no lesson is a hard prerequisite except 01 and 07.

## 1 · Purpose

Teach a JVM / TypeScript / Python architect whose team uses Visual Studio Professional what the IDE adds to the CLI-first
track, and — the lesson's rule — why it never replaces it: the solution and project files are the source of truth, so
Build-in-Visual-Studio and `dotnet build` agree, and every setting worth sharing lives in a file (`.vsconfig`, `.slnx`,
`launchSettings.json`, `.runsettings`, `.editorconfig`). IDE behaviour cannot be run by a script, so every claim about it
is **VERIFIED** against an official page read on **2026-09-21** (constant `VERIFIED_ON`) and linked beside it; the samples
prove only the parts that are code and files. No price appears anywhere.

## 2 · Ownership & cadence

Owner **claude**, regenerable. Rebuild when `lesson_13.py`, the samples, `lesson_kit.py` or the renderer change; re-run
`samples/tools/capture.py` after any sample edit (it regenerates `measurements.json`). Re-verify the linked pages when a
new Visual Studio release ships (the KPI tile names 18.10.1, the current Stable release on 2026-09-21) and at the November
.NET major.

## 3 · Structure

20 pages at the 2026-09-21 build (fix pass after review). The review's additions were paid for by cutting the
installer-commands panel, the legacy-estate table, the tool/CLI table, the edit-while-running state diagram and the traits
donut. Contents on page 1 (code panels are deliberately **not** listed; the Contents note says so).

| § | Heading | Blocks |
|---|---|---|
| 1 | Why an IDE, when the CLI builds everything | story (3 ¶; the rule names three kinds of difference: a workload, an SDK, or a file only the command line reads — `Directory.Build.rsp` and `Directory.Solution.props/.targets`, worded as lesson 07 §4.5) · kpi 1.1 (5 tiles) · legend (tooling tag only) · info callout "Before you start" · mermaid 1.2 flowchart, top-down (IDE-only box, files, command-line-only box, the two front ends, MSBuild) · table 1.3 (IDE vs CLI, 6 rows, preceded by a `_keep_with_next` spacer) · mapping 1.4 (9 rows) |
| 2 | The editions | story (3 ¶) · mermaid 2.1 flowchart (edition decision; Q2 = "a tool the comparison page marks Enterprise-only") · cards 2.2 (Community / Professional / Enterprise) · chartrow 2.3 heatmap (14 Enterprise-only rows + code coverage × three editions) + 2.4 hbar (the 14 by section of the page) |
| 3 | Install, workloads and .vsconfig | story (3 ¶, incl. the SDK trap from the IDE side and `modify`, not `update`) · code 3.1 `.vsconfig` |
| 4 | Solutions and projects in the IDE | story (3 ¶) · compare 4.1 (C# `record struct` ↔ VB `Structure`, `MoneyDisplay`) · code 4.2 `L13.slnx` · table 4.3 (open code / add a package / one version list: Solution Explorer, NuGet manager, CLI) |
| 5 | The inner loop: debugging | story (3 ¶) · code 5.1 `launchSettings.json` · mermaid 5.2 sequence (F5) · table 5.3 (breakpoint kinds) · code 5.4 `BatchLoop` · 5.5 `BatchResult` · 5.6 `ClaimsLoading` · table 5.7 (window or setting per question, incl. Source Link and pinned data tips) · table 5.8 (Hot Reload and Edit and Continue limits, from the Roslyn supported-edits list) · table 5.9 (attach to a process) |
| 6 | Testing in the IDE | story (3 ¶) · code 6.1 `.runsettings` · 6.2 test `.csproj` · compare 6.3 (Kotlin Gradle `tasks.test` ↔ C# `TestsRunSettings`) · code 6.4 worked-example test · table 6.5 (Test Explorer ↔ CLI ↔ lesson 10) · note with the trait counts (14 + 3 + 1 = 18) |
| 7 | Code quality and AI assistance | story (3 ¶) · code 7.1 `.editorconfig` · table 7.2 (where a style setting lives; the IDE-style row says "only with `EnforceCodeStyleInBuild`") · code 7.3 `samples/Directory.Build.props` |
| 8 | Performance and diagnostics | story (3 ¶) · code 8.1 `Measure` · 8.2 `HeavyVersion` · 8.3 `PresizedVersion` · chartrow 8.4 hbar (bytes above the pricing floor, Release) + 8.5 hbar (calls to `Price`, one measured pass) |
| 9 | Legacy estates in the IDE | story (3 ¶, ends with a visible "Not covered here, and why" paragraph) |
| 10 | Other editors | story (2 ¶) · table 10.1 (vendor facts verified; the last column is the ESTIMATE) |
| 11 | Hands-on | story with a 4-step numbered list · table 11.1 (five questions: the profile, the IDE feature, the CLI route, the measured answer) · code 11.2 captured terminal · table 11.3 (files Visual Studio reads and who else reads them) · chart 11.4 hbar (lines per settings file) · threecol 11.5 · warn "Traps" (5) · ok "Checkpoint" (4) · summary "Check yourself" (7) · footer (no "Next": points back to lessons 07/10 and the official docs) |

Minimums as built: 11 numbered stories · 1 mapping · 1 card band (3 cards) · 3 mermaid (flowchart ×2, sequence) · 5 charts
(one heatmap, four hbar; four of them in two chartrows) · 15 `code` + 2 `compare` panels · C# ↔ VB compare (4.1) · Kotlin ↔ C#
compare (6.3) · 1 threecol · 11 tables besides the mapping · 47 distinct official links.

## 4 · Derivation

- **KPI row.** "18.10.1" (current Stable, 2026-09-15) and "18.0.0" (first 2026 release, 2025-11-11) — VERIFIED, release
  history re-read 2026-09-21. "4 projects", "18 tests" (14 Tariff · 3 Batch · 1 Environment) and "12 files" (8 settings
  files + 4 project files) — MEASURED: project files read from disk; test counts from `dotnet test --filter Category=…`;
  settings files from `capture.py`'s list plus the repository root's `global.json` and `Directory.Build.props`, each file's
  line count read from disk at build time.
- **Chart 2.3 (rubric, not a benchmark).** Every row is read from the comparison page itself: each cell carries an accessible
  label ("feature available" / "feature not available"); 14 rows have the two lower editions "not available" and Enterprise
  "available" (Live Dependency Validation, Architectural Layer Diagrams, Architecture Validation, Code Clone, IntelliTrace,
  Code Map debugger integration, .NET Memory Dump Analysis, Snapshot Debugger, Time Travel Debugging, Live Unit Testing,
  IntelliTest, Microsoft Fakes, Embedded Assemblies, and Tier Interaction Profiling — the one row stated as text); Code
  Coverage is "available" in all three. **Chart 2.4** counts those 14 by the page's own section (5 debugging and
  diagnostics, 4 IDE and architecture, 3 testing, 1 performance hub, 1 cross-platform). The Learn coverage page says
  Enterprise-only in Visual Studio 2022 and earlier; that stays in the text.
- **Table 5.8.** Follows the Roslyn "Supported Edits in Edit and Continue and Hot Reload" list: `using` (16.10), attributes
  and parameter rename (17.0), deleting non-field members and namespace declarations (17.3), renaming non-field members and
  changing parameter or return types (17.4) are supported; interfaces, new abstract/virtual/override members, destructors,
  deleting a type, and catch/finally blocks holding the active statement are not; VB `On Error`, `Aggregate`, `Group By`,
  `Join`, `Group Join` are not. The older table on the "supported code changes" page still lists renames, attributes and
  `using` as unsupported and points to the Roslyn list for .NET 6+; the lesson says so.
- **Charts 8.4 / 8.5.** `L13.PerfLab` reads `GC.GetAllocatedBytesForCurrentThread` around each version after a warm-up, in a
  **Release** build (`capture.py` builds and runs `-c Release`): floor 39,680 B · heavy 142,832 B · builder 76,272 B ·
  pre-sized 70,328 B for 236 quotes; calls to `Price` 236 / 472 / 236 / 236 in one measured pass (the counter is reset after
  the warm-up). Bytes above the floor (103,152 / 36,592 / 30,648) and the ratio 3.4× are computed in the module. A Debug
  build prints other absolute figures (floor 107,928, heavy 279,328, builder 144,520, pre-sized 138,576 — also captured by
  `capture.py`), so every figure names Release. The profiler was **not** run: the note that a whole-program profile would
  total 472 / 944 calls (warm-up included) is labelled ESTIMATE.
- **Panel 7.3 and table 7.2.** `samples/Directory.Build.props` imports the repository's file by hand (`GetPathOfFileAbove`;
  MSBuild reads only the nearest one) and sets `EnforceCodeStyleInBuild`. `capture.py`'s `style_probe` writes a
  block-scoped-namespace file, builds twice and deletes it: with the property the build fails with **IDE0161**, with
  `-p:EnforceCodeStyleInBuild=false` it succeeds (MEASURED). This mirrors lesson 07 §7.3.
- **Panel 11.2 and table 11.1** are captured from real runs by `capture.py` (`--show 47` → declined in `ClaimsLoading`;
  `-lp "Show quote 137"` → Class2Plus, sum insured 640000.00, loadings 10%, no-claim 0%, net 8448.00, total 9075.52 THB;
  batch → 236 quoted, declined 47 / 108 / 169 / 230, gross 1458887.59 THB); the terminal shows the two header lines once.
  The tariff is the canonical one (`_curriculum.md`); the worked example prices to net 8,316.00 + stamp duty 33.26 + VAT
  584.45 = **8,933.71 THB** in the C# and the VB console and in the test asserting it.
- **Guided session.** The program is correct and its 18 tests pass; each question names its launch **profile** (`Batch` for
  1–4: the two Show profiles start `Program.Show` and never reach `QuoteBatch.Run`), the IDE feature, the CLI route and the
  measured answer. The breakpoint or tracepoint sits on the first line inside the `try` (marked in the `BatchLoop` region),
  after `request` is assigned. The IDE steps are labelled ESTIMATE (unrun: no Visual Studio on the build machine).
- **Code panels** come from regions in the samples: `MoneyDisplay` (C# + VB), `BatchLoop`, `BatchResult`, `ClaimsLoading`,
  `TestsRunSettings`, `TestsWorkedExample`, `Measure`, `HeavyVersion`, `PresizedVersion`, and whole files (`.vsconfig`,
  `L13.slnx`, `.runsettings`, `.editorconfig`, `Directory.Build.props`, `launchSettings.json`, the test `.csproj`). Regions
  `RequestDisplay`, `StepThrough`, `BuilderVersion`, `AggregateLimit` and the VB `Generator` / `BatchLoop` exist in the
  samples but are not printed; the table cells that cite them say "not printed".

## 5 · Presentation

Format 00 via `brief_pdf.py`. Local helpers in the module: `listed()` only cleans VB highlighting — it does **not** put
panels in the Contents (kit request: an optional level for panel headings); `figure_heading()` gives the threecol a kept
heading; `cmd()` keeps table-cell commands whole; `sample()` forces a language for `.runsettings` / `.vsconfig` /
`Directory.Build.props`; `short()` re-labels a link for a narrow Source column; `Ref()` capitalises `ref()` at a sentence
start. Empty `_keep_with_next` blocks stand before tables 1.3, 5.3, 5.8 and 5.9 so a heading is not stranded at a page foot
(a renderer quirk for tables). A style block caps flowchart height at 3.2 in and sets `a.lnk { word-break: normal }` so a
link label wraps between words, not inside them (the kit's default breaks anywhere). Mermaid 5.2 uses `Note over`; step 5
(attach the debugger) is a solid arrow because it is a request. The heatmap uses `Com / Pro / Ent` because `cell` = 22 cannot
hold "Comm." and "Prof." side by side. Panels 5.1, 5.4, 5.5, 6.2, 7.1 and 7.3 are kept whole; 6.1 and 8.1 may split.

## 6 · Inputs

`roster.py` (row 13: `visual-studio-workflows`, 5 h, phase E · Tooling); `_curriculum.md` (lesson-13 plan, canonical
tariff); samples `L13.DebugLab` (C# console), `L13.DebugLab.Tests` (xUnit v3, `xunit.v3.mtp-off`, `RunSettingsFilePath`),
`L13.DebugLabVb` (VB twin, `Aggregate` member), `L13.PerfLab` (C# console) and, at the samples root, `.vsconfig`,
`.runsettings`, `.editorconfig`, `Directory.Build.props`, `L13.slnx`, `tools/capture.py`, `tools/measurements.json`. Sources
(read 2026-09-20 by the author and re-read 2026-09-21 by the fix pass where the review challenged them): Visual Studio
editions comparison (cells read through their accessible labels) · release history · servicing and lifecycle · VS 2026
announcement · import/export installation configurations (`.vsconfig`) · workload and component IDs · new solution file
format · `dotnet new sln` breaking change · solution filters · Open Folder · NuGet in Visual Studio · Central Package
Management · `dotnet package add` · `dotnet build` · global.json overview · MSBuild response files · breakpoints · Just My
Code · exception settings · Tasks window · decompilation · Source Link · data tips · attach to processes · Hot Reload ·
supported code changes · the Roslyn EnC supported-edits list · DebuggerDisplay · `dotnet run` (launch profiles) ·
launchSettings.json (ASP.NET Core environments) · Test Explorer · `.runsettings` · code coverage · Live Unit Testing ·
Microsoft Fakes · xUnit.net v3 MTP page · code styles and Code Cleanup · .NET code analysis overview · Copilot get started
and Copilot Free · profiling overview · .NET diagnostics tools · WinForms designer for .NET · C# Dev Kit FAQ and C# in VS
Code · JetBrains Rider · Visual Studio documentation home.

## 6a · Tariff and cross-lesson consistency

Uses the canonical tariff exactly (class rates 2.1 / 1.2 / 0.9 / 0.4 %, young-driver +20 %, claims 0 / 10 / 25 % and 3+
declined, commercial +25 / 35 %, no-claim 0–50 %, stamp duty 0.4 %, VAT 7 %, `MidpointRounding.AwayFromZero`); the lesson
says it is illustrative. Reused wording: SDK shadowing is lesson 01's, revisited in one paragraph from the IDE side; "Visual
Studio reads both from 17.14", `Directory.Build.rsp` ("a switch the IDE never sees") and `Directory.Solution.props/.targets`
("never inside Visual Studio") are lesson 07 §4.5's, and `EnforceCodeStyleInBuild` → IDE0161 is lesson 07 §7.3's;
analyzers, `.editorconfig` and `dotnet format` are lesson 07's (`ref(7)`); the async-windows row is a concept link to
lesson 05 and says no sample here runs async code; the `xunit.v3.mtp-off` choice and line/branch coverage gates are lesson
10's; VB/WinForms legacy is lesson 06's; modernization tooling is lesson 12's. `ref(n)` never sits inside parentheses that
already hold another `ref`, and opens a sentence only through `Ref()`. Every `ref(n)` was checked against the built text of
lesson n. Sections 3 to 7 are each anchored on a file (`.vsconfig`, `.slnx`, `launchSettings.json`, `.runsettings`,
`.editorconfig`); section 8 is not.

## 7 · Invariants

- The four sample projects build, run and exit on their own (or pass, for the tests) on the pinned SDK without Visual
  Studio; `verify_samples.py --only 13` ends "4/4 sample projects passed".
- The C# and VB consoles print identical figures; the `.runsettings` file is applied by `dotnet test` (an Environment test
  fails otherwise) and is the same file Visual Studio autodetects at the solution root **when Auto Detect runsettings Files
  is on**.
- No price is printed; the only currency-like figure is the Community organisation definition (US$1 million in annual
  revenue), which is a licence threshold, not a price. No employer, client or colleague is named.
- Every VERIFIED claim carries a `link()`; anything not confirmed on an official page is left out or labelled ESTIMATE (the
  last column of table 10.1, the IDE steps of the guided session, and the profiler totals in 8.5).

## 8 · Known gaps

- ⚠ **Not re-verifiable by a script.** All IDE behaviour — menu paths, shortcuts, edition gating, licence terms, version
  numbers, Hot Reload and designer limits, Copilot plan wording, Dev Kit and Rider terms — is documentation-backed and dated
  2026-09-21. Only the sample code, the settings files and the measured figures are proved by `verify_samples.py`; the
  guided session's IDE steps were not run in Visual Studio.
- ⚠ **Two Microsoft pages disagree** on code coverage in VS 2026 (the coverage page and the comparison page say all three
  editions; the Test Explorer page still says Enterprise in one sentence). The lesson reports the disagreement.
- ⚠ **The "Enterprise-only" list is the comparison page's, not a promise.** Chart 2.3 reads every row of the page's
  per-edition matrix; Microsoft can change it, and the lesson tells the reader to read the page before buying.
- ⚠ The component-ID page is labelled Visual Studio 2022; the lesson says so and tells the reader to export from their own
  installer. The nine IDs in `.vsconfig` are not checked against an installer here.
- ⚠ Not covered, on purpose (stated in the PDF where it matters): the WPF designer, IIS Express versus a full IIS site and
  `web.config`, a preview channel beyond the Insiders name, how AWS/Azure toolkits are added — none was confirmed on an
  official page. The Dev Kit and Rider rows state only what their pages say; feature parity with Visual Studio is not claimed.
- ⚠ The VB launch-settings location (`My Project/launchSettings.json`) is stated from the `dotnet run` page; the VB twin
  ships none. The `DOTNET_ENVIRONMENT` variable in the third launch profile is inert (nothing reads it) and the lesson says so.
- ⚠ Platform limits: Windows-only IDE features (designers, attach to `w3wp.exe`) are described, not run; the Kotlin panel
  in 6.3 is inline comparison code and is not compiled.
- ⚠ **For the lead (other lessons).** Lesson 01: "The twelve lessons" (§6.4), its KPI, study-time chart and hours-per-phase
  table still count twelve (`roster.py` lists 13, phase E) and its SDK-trap bullet has no pointer to lesson 13 §3. Lesson 12:
  an "After the track" pointer to lesson 13 (Copilot in Visual Studio, §7). Lesson 10: its "other lessons still reference
  xUnit v2" list is right for 02–06, 08, 09, 11, 12; lesson 13's tests use `xunit.v3.mtp-off` 4.0.1.
