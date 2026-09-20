# Unit spec — lesson-07-solutions-monorepo-build.pdf

Built to `_standard.md`. Content module `0-script/lessons/lesson_07.py`. Samples
`lesson-07-solutions-monorepo-build/samples/` (the mini mono-repo `MotorMono`, the workflow file `ci/build.yml`
and the measurement script `tools/measure_build.py`).

## 1 · Purpose

Teach a Gradle / Maven / Lerna mono-repo architect to read, own and change the build of a .NET mono-repo: where
the configuration lives when the project file is five lines, how MSBuild evaluates a project before it builds
one, what each `Directory.*` file may decide and when it is imported, how central package management differs
from a version catalog, how to predict the incremental cost of an edit, and how one GitHub Actions workflow
gates, packs and publishes every module.

It is the third lesson of phase B (runtime & codebase) and the last before the service lessons: after it, the
reader can open an unfamiliar .NET repository and answer "how does this build?" without running it.

## 2 · Ownership & cadence

Owner **claude**, regenerable. Rebuild when the samples, `lesson_kit.py` or the renderer changes — and re-run
`samples/tools/measure_build.py` first, because **every build figure in the PDF is read from
`samples/tools/measurements.json` at render time**, not hard-coded. Re-verify the version-sensitive claims when
a new .NET major ships in November: the `.slnx` default, the `NuGetAuditMode`/`RestoreEnablePackagePruning`
defaults, the analyzer rule counts (they move with every SDK), and the GitHub Actions major versions in
`ci/build.yml`.

## 3 · Structure

19 pages at the 2026-09-20 build. No page except the last is more than a third empty; the two gaps worth naming
are page 15 with 30% (the §8 story grew when it started describing `rollForward`, and the 8.2 `sequenceDiagram`
below it is unbreakable, so it jumps whole to page 16) and page 8 with 18% (the 4.5 card band does not fit
after 4.4). Page 19 is the closing page, holding "Check yourself" and the footer. Measured with PyMuPDF over
the built PDF: every other page is between 0.2% and 2.7% empty.

| § | Heading | Blocks |
|---|---|---|
| — | Contents | `toc` depth 2 (code panels are listed through the local `listed()` helper) |
| 1 | Why a .NET mono-repo looks empty | story (4 ¶) · `kpi` 1.1 (5 tiles) · `legend` (the `tooling` tag — the only tag the lesson uses) · info callout "Before you start" (5 items: prerequisite lessons · what you build · how to run it · how the numbers are measured · the honesty chips) |
| 2 | Solutions — a list of projects, not a build script | story (3 ¶) · chart 2.1 bar (solution-file size, 3 bars) · code 2.2 (`MotorMono.slnx`, whole file) · mapping 2.3 (17 rows) · compare 2.4 (`MotorMono.Pricing.slnf` ↔ captured filtered build) |
| 3 | The MSBuild model — two phases, four nouns | story (3 ¶) · mermaid 3.1 `flowchart TB` with `direction LR` subgraphs (startup → six evaluation passes → execution; the three containers are filled to match their nodes) · table 3.2 (6 rows: property, item with its metadata, target, task, SDK, binary log) · chart 3.3 hbar (expanded project lines by origin) · code 3.4 (`Directory.Build.targets`) · code 3.5 (captured `-t:ListProjects` run) |
| 4 | Shared build logic — and the one rule that bites | story (3 ¶) · mermaid 4.1 `flowchart LR` (the measured import chain) · code 4.2 (`MotorMono/Directory.Build.props`) · code 4.3 (captured `NETSDK1013` from the deliberately broken build) · code 4.4 (the repository-root `Directory.Build.props` that 4.2 chains to, with its two `MSBuildProjectExtension` groups) · cards 4.5 (3 + 2 in a "(continued)" band) |
| 5 | Dependencies — one version list for the repository | story (3 ¶) · code 5.1 (`Directory.Packages.props` — the three packages are the xUnit v3 test stack lesson 10 teaches; the note names that lesson as the owner of the choice) · code 5.2 (`L07.Pricing.Tests.csproj` — references with no versions, plus the `OutputType Exe` xUnit v3 requires) · table 5.3 (4 failure modes with measured codes and abridged messages) · chart 5.4 heatmap (4 ecosystems × 6 capabilities, a rubric) |
| 6 | The build graph — what recompiles when you change one line | story (3 ¶) · mermaid 6.1 `flowchart LR` (build graph; every thin edge carries the public API only, the one thick labelled edge also carries internals) · chart 6.2 hbar (projects recompiled per edit kind) · compare 6.3 (Kotlin `internal` ↔ `Internals.cs` `#region internals`) · compare 6.4 (`NoClaimBonus.cs` ↔ `NoClaimBonusVb.vb`, both `#region ncb-rule` — the canonical no-claim ladder in two languages; the note names the shared tariff and the decline) |
| 7 | Quality gates that live inside the build | story (3 ¶) · code 7.1 (`.editorconfig`, whole file; its note pairs `end_of_line = lf` with the sample's `.gitattributes`) · chart 7.2 bar (CA rules at warning per analysis mode) · table 7.3 (6 gates × where it is switched on / what fails it / its name in your stack) |
| 8 | Packaging and CI — one workflow for the whole repository | story (3 ¶) · code 8.1 (`ci/build.yml` `#region build`) · mermaid 8.2 `sequenceDiagram` (one push through the pipeline, 8 messages, no numbering) · code 8.3 (`ci/build.yml` `#region publish`) · table 8.4 (6 packaging decisions) |
| 9 | Hands-on — drive MotorMono, then take it apart | story (2 ¶) · code 9.1 commands · code 9.2 captured `L07.QuoteCli` output · chart 9.3 hbar (lines of code per module) · 9.4 threecol (carries over / learn fresh / unlearn) · warn "Traps" (5) · ok checkpoint (4) · summary "Check yourself" (7, kept on one page with the footer) · footer |

Standard minimums as built: 9 numbered stories · 1 mapping (17 rows) · 2 card bands (3 + 2 cards) · 4 mermaid
(flowchart ×3, sequence ×1 — 2 families) · 6 charts (bar ×2, hbar ×3, heatmap ×1) · 16 code panels (13 `code` +
3 `compare`) · C# ↔ VB compare (6.4) · Kotlin ↔ C# compare (6.3) · 1 threecol · 4 tables besides the mapping ·
27 distinct official links (counted from the built PDF's link annotations).

## 3a · The canonical tariff in this lesson

`MotorMono` prices the track's running example, so it uses `_curriculum.md` § "Canonical tariff" exactly, with
no variant: Class 1 2.1% / Class 2+ 1.2% / Class 3+ 0.9% / Class 3 0.4% of the sum insured (`Internals.cs`
`BaseRates.For`), young driver +20% under 25, claims 0/1/2 → +0/+10/+25%, commercial +25% or +35% above
3,000 cc (`Rules.cs`), the no-claim ladder 0/20/25/30/40/50% by claim-free year and none after a claim
(`NoClaimBonus.cs` and its VB twin `NoClaimBonusVb.vb`), loadings summed onto the base and the discount applied
to the loaded premium, then stamp duty 0.4% and VAT 7%, every step rounded to 2 places away from zero
(`PremiumCalculator.cs`, `Money.Rounded()`).

Three or more claims in five years declines the quote. This lesson teaches neither exceptions nor data
modelling, so — per the curriculum's rule for such a lesson — it defines the smallest thing that fits:
`L07.Core/QuoteDeclined.cs`, a `QuoteDeclinedException` carrying the reason `"3+ claims in 5 years"`, thrown
from `ClaimsLoading.Factor`. The 6.4 note says so in one sentence and points at lesson 02 for exceptions
proper. The worked example — Class 1, 550,000 THB, driver 23, 4 claim-free years → base 11,550.00, net
8,316.00, stamp duty 33.26, VAT 584.45, **total 8,933.71 THB** — is asserted by the test
`The_worked_example_of_the_tariff_matches_the_cli` and is the run captured verbatim in panel 9.2.

## 4 · Derivation

**Everything measured comes from one file.** `samples/tools/measure_build.py` copies `samples/MotorMono` (plus
the repository `Directory.Build.props` and `global.json`) to a temporary folder, builds it, edits it, breaks it
and reads the SDK's own configuration files, then writes `samples/tools/measurements.json`. The lesson module
loads that JSON at render time and never runs `dotnet` itself. Re-measured 2026-09-20 with SDK 10.0.401 and
MSBuild 18.9.11.42413 on Windows, after the test stack moved to xUnit v3 and the rules moved to the canonical
tariff. Two figures moved with that re-measure and nothing else did: `ci.tests_total` 12 → 14 (the tariff
brought a decline test and a wider commercial theory) and the `NU1004` / `NU1008` messages in `breaks`, which
now quote `xunit.v3.mtp-off` instead of `xunit`. The lines-of-code chart moved too, but it is counted at render
time, not measured into the JSON.

`global.json` is the one input the module reads directly rather than through `measurements.json`: the §8 story
prints `sdk.version` and `sdk.rollForward` out of the file itself (`GJ` at the top of the module), so the
sentence about what the pin guarantees cannot drift from the file it describes.

- **KPI 1.1** — `5 projects` = `measurements.projects`; `17,412 lines` = `preprocess.preprocessed_lines` from
  `dotnet msbuild -pp` on the 5-line `L07.Pricing.csproj`; `16 lines` = `solution_formats` (the migrated
  `.slnx` against the classic `.sln`'s 101); `5 of 5 recompile` / `an internal one: 1` = the `incremental`
  rows; `145 CA rules` = `analyzers.counts.recommended`.
- **Chart 2.1** — `solution_formats.files`: the CLI created `Legacy.sln` with `--format sln`, the five projects
  were added, `dotnet sln migrate` produced `Legacy.slnx`; 101 lines / 10 GUIDs / 6,888 chars against 16 lines
  / 0 GUIDs / 530 chars. `dotnet new sln` with no `--format` created `Probe.slnx` — the measured proof of the
  .NET 10 default, which is also VERIFIED against the breaking-change page.
- **Compare 2.4** — the `.slnf` is read from the sample; the right panel is a real
  `dotnet build MotorMono.Pricing.slnf` run, with the absolute output paths shortened (stated in the panel's
  file line). Listed 3 / built 4 is also recorded in `solution_filter`.
- **Chart 3.3 and the §1 story** — `preprocess.lines_by_origin` and `preprocess.banner_lines`, produced by
  reading the `-pp` output's import banners. Each banner (wrapped in an XML comment) names the file the lines
  after it belong to — the imported file when entering, the importing file when returning — so the attribution
  follows the current file. (An earlier version kept a stack and popped one entry per `</Import>` banner; one
  banner can close several nested imports, so the stack went stale and named
  `Microsoft.Common.CurrentVersion.targets` as the importer of `Directory.Build.targets` — it is
  `Microsoft.Common.targets` — and counted 8 lines for the project file instead of its 5.) Result: 5 lines from
  the project file (the same 5 as on disk), 74 from `Directory.*`, 12 from restore output, 15,696 from the
  SDK — 15,787 lines of build logic — plus 1,625 banner lines = 17,412, across 117 files. The banner lines
  belong to no file, so the chart leaves them out and its caption and note say so.
- **Code 3.5, 9.2** — captured from real runs on the build machine (`dotnet msbuild -t:ListProjects` and
  `dotnet run --project src/L07.QuoteCli`). The commit SHA in 9.2 is whatever the repository's HEAD was at that
  build; the panel's note says so.
- **Mermaid 4.1** — every arrow is `preprocess.directory_chain`, read out of the expanded project, not drawn
  from the documentation: `Microsoft.Common.props` imports `MotorMono/Directory.Build.props`, which imports the
  repository root's by hand; `NuGet.props` imports `Directory.Packages.props`; `Microsoft.Common.targets`
  imports `Directory.Build.targets`. The same order is in Microsoft's "Customize the build by folder" table.
- **Code 4.4** — read with `from_sample("Directory.Build.props")`, the repository-root file (a shared input, not
  a lesson sample); its note describes the two `MSBuildProjectExtension` groups.
- **Code 4.3 and table 5.3** — `measurements.breaks`: six deliberately broken builds, each recorded with its
  exit code, the first error code and the verbatim message. 4.3 renders the `NETSDK1013` row through the local
  `_break_panel()` helper; 5.3 shows `NU1008`, `NU1004`, `NU1507` (verbatim prefixes via `_clip()`) plus the
  audit warnings, which are VERIFIED rather than measured because this repository excludes them from errors.
- **Chart 5.4** is a rubric (yes / some / —), labelled as such in the caption and tagged ESTIMATE in its note.
  The sharp claim it encodes — a Gradle version catalog declares but does not enforce — is quoted from the
  Gradle documentation.
- **Chart 6.2** — `measurements.incremental`: six scenarios, counted by parsing a detailed (`-v:d -m:1`) MSBuild
  log for projects whose `CoreCompile` actually invoked `Csc`/`Vbc`. 5 / 0 / 1 / 1 / 3 / 5. The asymmetry
  (internal in `L07.Core` = 1, internal in `L07.Pricing` = 3) is explained by `InternalsVisibleTo` keeping
  internals in the reference assembly, VERIFIED against the reference-assemblies article and the Roslyn refout
  notes.
- **Chart 7.2** — `analyzers.counts`: `dotnet_diagnostic.CA*.severity = warning` lines counted in the SDK's own
  `analysislevel_10_<mode>.globalconfig` files (92 / 145 / 280 for the minimum / recommended / all analysis
  modes). The text names the property correctly: `AnalysisMode`, or the mode half of a compound
  `AnalysisLevel` such as `latest-recommended` (which is what MotorMono sets); the table 7.3 vulnerability row
  names `NuGetAuditMode`, the property that defaults to `all` on `net10.0`.
- **The `end_of_line` claims (§7 story, 7.1, 7.3, trap 5)** — one half is measured: `measurements.breaks`
  records `dotnet format whitespace --verify-no-changes` exiting 2 on Windows over LF files once
  `end_of_line = lf` is removed. The other halves — the same files passing on Linux, and a CRLF checkout
  failing the pinned rule under Git for Windows' default `core.autocrlf=true` — are reasoning, and the PDF says
  so each time. The sample's `.gitattributes` (`* text=auto eol=lf`) is what makes the measured files LF.
- **Table 8.4 and the §8 story** — `measurements.ci`: the workflow's five steps run locally with `CI=true`
  (all exit 0), 14 tests, and the three `.nupkg` files with their ids, versions (`1.4.0-ci.42` from
  `-p:VersionSuffix=ci.42`) and generated dependencies. The SDK sentence in the same story is derived from
  `global.json` (above) and quotes two lines of the Microsoft Learn `global.json` page verbatim: the
  `latestFeature` row of the `rollForward` table, and its advice to set `rollForward` to `disable` when a
  repository uses package lock files — the second one is why the sentence teaches rather than only corrects,
  because §5 is the lesson that commits those lock files.
- **Chart 9.3 and the §9 story** — `loc()` over every `.cs`/`.vb` file of each project (306 lines total at this
  build), drawn as horizontal bars so the project names stay horizontal.
- **`properties`** (`UseArtifactsOutput`, `NuGetAuditMode`, `RestoreEnablePackagePruning`, `AnalysisLevel`,
  `MotorMonoBuiltFrom`) are evaluated with `dotnet msbuild -getProperty:` and quoted in §2, §5 and §7 — the
  measured confirmation of the .NET 10 defaults the text cites.

## 5 · Presentation

Format 00 via `brief_pdf.py`; code panels from `lesson_kit`. Local helpers in the module (kit requests):
`listed()` (puts a panel's heading in the Contents, strips Pygments' red error box around VB interpolated
strings, and — for a panel that is not kept — prints the heading as a `.ct` line so the Contents marker does
not make the panel unbreakable; as in lesson 04), `figure_heading()` (a numbered, kept-with-next heading for the
threecol), `pcode()` / `pcompare()` (the two together), `cmd()` (table-cell commands that do not wrap inside
themselves), `_break_panel()` (renders a measured failure as a terminal panel) and `_clip()` (a verbatim prefix
of a compiler message in a table cell).

Local CSS (one `html` block after the Contents): a story or callout heading is never left at a page foot
(`.story .ct`, `.callout .ct` break-after avoid, and the first paragraph or item stays with it).

Mermaid: 3.1 is `flowchart TB` with `direction LR` subgraphs (three stacked bands, each container filled with
the colour its nodes use, so the caption's colour language holds); 4.1 and 6.1 are `flowchart LR`; 8.2 is a
`sequenceDiagram` coloured by an `%%{init:…}%%` directive, since `classDef` is not supported there, with no
message numbering. Every `classDef` carries `color:#1f2937`. In 6.1 the two consumers each read both
producers, so two thin edges cross once; only the thick edge is labelled, and the caption says every unlabelled
edge carries the public API only.

Pagination: the solution-size chart (2.1) and the expanded-lines chart (3.3) sit before the code panel that
follows them, and the closing "Check yourself" callout is grouped with the footer (`_keep_with_next`) so the
last page holds a whole checklist rather than a split question. The Checkpoint callout and the Traps are left
breakable.

Heatmap 5.4 uses `cell: 44` with one-word column labels (`CPM`, `Gradle`, `npm`, `Maven`) and expands them in
the caption; the longer labels collided at `cell: 40`.

## 6 · Inputs

`roster.py`; the samples under `lesson-07-solutions-monorepo-build/samples/`:

- `MotorMono/` — `MotorMono.slnx`, `MotorMono.Pricing.slnf`, `Directory.Build.props` (imports the repository
  root's), `Directory.Build.targets`, `Directory.Packages.props`, `Directory.Build.rsp`, `nuget.config`,
  `.editorconfig`, `.gitattributes`, `src/L07.Core` (including `QuoteDeclined.cs`), `src/L07.Pricing`,
  `src/L07.Pricing.Vb` (VB), `src/L07.QuoteCli` (console), `tests/L07.Pricing.Tests` (xUnit v3 4.0.1, 14 tests,
  `OutputType Exe`), one `packages.lock.json` per project
- regions shown in the PDF: `internals` (`Internals.cs`), `ncb-rule` (`NoClaimBonus.cs` and
  `NoClaimBonusVb.vb`), `build` and `publish` (`ci/build.yml`)
- `ci/build.yml` — a GitHub Actions workflow that is **not** active in this repository (GitHub only runs files
  under `.github/workflows/`); it pins `actions/checkout@v7`, `actions/setup-dotnet@v6`,
  `actions/upload-artifact@v7`
- `tools/measure_build.py` → `tools/measurements.json`
- repository `global.json` and `Directory.Build.props` (the root file is also shown whole in 4.4)

Sources cited with `link()` — Microsoft Learn: Customize the build by folder, How MSBuild builds projects,
Solution filters in MSBuild, MSBuild response files, `global.json` and `rollForward`, `dotnet new sln` defaults
to SLNX, `dotnet restore` audits
transitive packages, Source Link included in the .NET SDK, artifacts output layout, Central Package Management,
locking dependencies, package source mapping, reference assemblies, code analysis in .NET, IDE0161,
`dotnet format`, `dotnet pack`; .NET Blog: SLNX support in the .NET CLI, NuGet package pruning in .NET 10;
Visual Studio Blog: the new simpler solution file format; GitHub: `dotnet/msbuild` Binary-Log.md,
`dotnet/roslyn` refout.md, `actions/setup-dotnet` README, GitHub Packages NuGet registry; AWS: CodeArtifact
with the `nuget`/`dotnet` CLI; Gradle: version catalogs; Kotlin: visibility modifiers.

## 7 · Invariants

- Every build figure is read from `measurements.json` at render time. A stale JSON must never be edited by
  hand — re-run `measure_build.py`, which works on a temporary copy and never touches `.build/artifacts`.
- `MotorMono/Directory.Build.props` must keep its hand-written `Import` of the parent: it is the subject of §4,
  the cause of the `NETSDK1013` break in 4.3, and without it the samples do not build at all.
- The repository-root `Directory.Build.props` (owned outside this lesson) must keep its two
  `MSBuildProjectExtension` groups — `.csproj` for `Nullable` and `.vbproj` for `Option Strict On` — because
  4.4 and the 6.4 note describe them and the mixed-language graph builds on them.
- `MotorMono/.gitattributes` must keep `eol=lf`: it is what makes the measured `end_of_line` break reproducible
  and what 7.1 and trap 5 tell the reader to pair with `.editorconfig`.
- `L07.Pricing` must keep a `tests/L07.Pricing.Tests` folder and `L07.Core` must not have one: the
  `InternalsVisibleTo` condition in `Directory.Build.targets` is what produces the 1-vs-3 asymmetry that
  chart 6.2 and the §6 story are built on.
- The VB project must keep implementing the same `IRatingRule` as the C# port, and the parity test
  (`Csharp_port_and_vb_original_agree`) must keep passing — 6.4 and 6.1 both claim one graph, two languages.
- Every rate, loading, ladder step and rounding in the samples must equal `_curriculum.md` § "Canonical
  tariff", with no deliberate variant. `The_worked_example_of_the_tariff_matches_the_cli` asserts the
  curriculum's worked total (8,933.71 THB) and `Three_claims_in_five_years_declines_the_quote` asserts the
  decline, so a drift away from the tariff fails the build rather than reaching the PDF. If the tariff ever
  changes, the 9.2 capture has to be re-run, not edited.
- The version list in `Directory.Packages.props` must stay the stack lesson 10 teaches (xUnit v3 4.0.1 via
  `xunit.v3.mtp-off`, runner 4.0.0, `Microsoft.NET.Test.Sdk` 18.10.0) and the test project must keep
  `OutputType Exe`. This lesson publishes "one version list for the repository", so a reader who copies it and
  then writes lesson 10's tests must get a project that compiles. Bumping it means re-running
  `measure_build.py`: the `NU1004` and `NU1008` rows of 5.3 quote the package name and versions verbatim.
- The §8 sentence about `global.json` must keep reading `sdk.version` and `sdk.rollForward` out of the file
  instead of naming them in prose — the pin is a *range*, and a hard-coded sentence is how that claim went
  wrong before.
- `L07.Pricing.Tests` must stay the only test project and `L07.QuoteCli` the only executable, or the "3 of 5
  projects pack" claim in 5.2 and 8.4 breaks.
- The sample workflow must never be copied to `.github/workflows/`; it is read into the PDF, not run.
- Internal figure references (`(4.3)`, `(6.2)`, …) must resolve to a heading that exists — checked by
  extracting every `(x.y)` from the rendered blocks and comparing it against the heading set.
- No employer, client or personal names; the mono-repo scale is referenced generically ("a Kotlin mono-repo of
  50–120+ modules").

## 8 · Known gaps

- ⚠ Captured output in 2.4, 3.5, 4.3 and 9.2 is pasted text. The commit SHA in 9.2 and the shortened paths in
  2.4 are build-machine specific; re-capture if the samples' output format changes.
- ⚠ The analyzer counts in 7.2 and the KPI row are SDK-specific (10.0.401). They will move with any SDK update
  and are re-measured, not quoted — but the surrounding prose names the numbers, so a rebuild is required
  rather than optional.
- ⚠ Chart 5.4 is the author's rubric of built-in behaviour across four ecosystems, not a measurement; only the
  .NET column is verified against this repository.
- ⚠ `ci/build.yml` is never executed in CI here, so its steps are verified only by `measure_build.py` running
  the same commands locally with `CI=true`. The `dotnet nuget push` step is the one thing in this lesson that
  has never run.
- ⚠ The Kotlin, Gradle and TOML comparison snippets are not compiled.
- ⚠ Two `end_of_line` claims are reasoning, not measurements (a Linux run and a CRLF checkout were never
  executed here); the PDF labels them as such.
- ⚠ Page 15 is about 30% empty and page 8 about 18% (the 8.2 `sequenceDiagram` and the 4.5 card band are
  unbreakable and jump whole); every other page except the last is under 3% empty. Page 15 is the worst gap in
  the lesson and is inside — but close to — the standard's one-third limit: shortening the §8 story would only
  move the gap, so closing it properly means making 8.2 short enough to fit beneath 8.1.
- ⚠ `.build/qa/lesson-07/_pdftext.txt` is **not** refreshed by `--qa` (only the page and sheet rasters are).
  Grep a freshly extracted text when checking the rendered wording, or the answer will be a build old.
- ⚠ The Contents-page mechanism makes a listed panel unbreakable unless `listed()` re-heads it; a future kit
  change to `code()` that renames the `.codeh` heading class would silently bring the page gaps back.
