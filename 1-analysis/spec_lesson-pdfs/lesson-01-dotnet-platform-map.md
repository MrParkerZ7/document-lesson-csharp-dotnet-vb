# Unit spec — lesson-01-dotnet-platform-map.pdf

Built to `_standard.md`. Content module `0-script/lessons/lesson_01.py` (the reference implementation for every
other lesson). Samples `lesson-01-dotnet-platform-map/samples/`.

## 1 · Purpose

Orient a JVM / TypeScript / Python architect in the .NET platform before any language detail: what the runtime
is, how versions, support and runtime roll-forward work, how C#, VB and F# relate, what the CLI and the publish
options are, and how the twelve-lesson track is laid out.

## 2 · Ownership & cadence

Owner **claude**, regenerable. Re-verify the support dates every November (new .NET major) and rebuild after
**10 Nov 2026**: the ".NET 8 & 9 support" tile then reads "ended", chart 3.3's first two bars drop to zero, and the
§3 story, table 3.4 pill and the warn callout switch to past tense (all driven by `days_until(2026, 11, 10)`).

## 3 · Structure

16 pages at the 2026-09-20 build (cross-lesson review fixes applied; the text of §6's story is kept short on purpose: two more lines push chart 6.1 to the next page and the lesson to 17 pages).

| § | Heading | Blocks |
|---|---|---|
| — | Contents | `toc` depth 2 (code panels and the threecol are listed through a local `listed()` / `figure_heading()` helper) |
| 1 | Why this track exists — and who it is written for | story (4 ¶) · `kpi` 1.1 (5 tiles) · `legend` (runtime, tooling) · info callout "Before you start" (5 items: no prerequisite lesson + what you build · install the .NET 10 SDK 10.0.401+ · the "No .NET SDKs were found" PATH shadowing fix · how sections lead · honesty chips) |
| 2 | The platform in one picture | story · mermaid 2.1 flowchart (source → Roslyn/fsc → IL → JIT / ReadyToRun / Native AOT → process) · compare 2.2 (Kotlin runtime introspection ↔ C# `PlatformProbe.Capture`) · mapping 2.3 (17 rows) · cards 2.4 (runtime pieces, 3 + 2 in a "(continued)" band) |
| 3 | Versions — how to read a .NET codebase's age | story · mermaid 3.1 gantt (support windows .NET 5–10) · chartrow 3.2 bar (support months) + 3.3 bar (days of support left, counted from the build date) · table 3.4 (8 TFM rows, incl. old-style `TargetFrameworkVersion`) · mermaid 3.5 flowchart (dating a legacy repository) · code 3.6 (captured: net10.0 app on an 8.0-only host, exit 150) · warn callout "The 10 November 2026 double cut-off" (5 items) |
| 4 | Three languages, one runtime | story · code 4.1 (C# positional record) · compare 4.2 (C# ↔ VB program) · compare 4.3 (C# ↔ VB: compare and copy vs compare only) · chart 4.4 heatmap (C# 14 / VB / Java 21 / Kotlin 2 feature rubric, cell 34; the null-safety row scores C# "some" because nullable reference types are compile-time annotations, see lesson 02 §4) |
| 5 | The toolchain — one CLI, five publish options | story · table 5.1 (Task · Gradle/npm · .NET CLI · Note, 10 rows) · mermaid 5.2 sequence (`dotnet run`: muxer → SDK → hostfxr → CoreCLR) · compare 5.3 (csproj ↔ vbproj) · cards 5.4 (publish options, 3 + 2 in a "(continued)" band) |
| 6 | Your transfer map and learning path | story (names async and VB.NET as the two low scorers; VB is low because its syntax maps word for word but its semantics change numbers, the framing lesson 06 opens with) · chart 6.1 progress (transfer per lesson) · mermaid 6.2 flowchart TB with `direction LR` subgraphs (phases) · chart 6.3 donut (hours by phase) · table 6.4 (#, Lesson, Phase, Hours + total) · 6.5 threecol (carry over / learn / unlearn) |
| 7 | Hands-on — build and run the lesson-01 samples | story · code 7.1 `global.json` + `Directory.Build.props` (`keep=False`) · code 7.2 commands · compare 7.3 captured output (C# app ↔ VB app) · chart 7.4 bar (lines of code) · warn callout "Traps on day one" (4) · ok checkpoint (4) · summary "Check yourself" (7) · footer |

Standard minimums as built: 7 numbered stories · 1 mapping · 4 card bands (≤ 3 cards each) · 5 mermaid (flowchart ×3,
gantt, sequence) · 6 charts · 15 code panels (5 `code` + 5 `compare`) · C# ↔ VB compare (4.2, 4.3) · Kotlin ↔ C#
compare (2.2) · 1 threecol · 3 tables besides the mapping · 14 distinct official links.

## 4 · Derivation

- KPI ".NET 8 & 9 support" and chart 3.3 = `days_until()` to the VERIFIED end dates (10 Nov 2026, 14 Nov 2028),
  recounted at every build. ".NET 10 · LTS", gantt 3.1, chart 3.2 and table 3.4 dates are VERIFIED against the .NET
  support policy, the .NET releases-and-support page, the .NET 8/9 end-of-support post and the .NET Framework
  lifecycle page (4.6.2 ends 12 Jan 2027; 4.5.2–4.6.1 ended 26 Apr 2022).
- KPI "Languages, one runtime" = 3, VERIFIED (.NET managed languages strategy).
- KPI "This track" and chart 6.3 = sums of `roster.py` `hours` (ESTIMATE); chart 6.1 = `roster.py` `transfer`
  (ESTIMATE); table 6.4 is generated from `ROSTER`.
- KPI "Lesson 01 samples" and chart 7.4 = `loc()` over the three sample source files (MEASURED: 29 / 15 / 19 at
  this build). The 7.4 note computes the VB–C# gap and counts the `Module`/`Sub Main`/`End` wrapper lines, so it
  stays true if the samples change.
- Chart 4.4 heatmap is a rubric (yes / some / —), stated as such in its caption ("some = library, subset,
  compile-time-only or consume-only"); its note cites What's new in Visual Basic and The history of C# for the version
  dates and explains the C# "some" in the null-safety row with a pointer to lesson 02. Kotlin keeps "yes" (null-safety is
  part of its type system).
- Panel 7.3 output and panel 3.6 are captured from real runs on the build machine (Windows x64, .NET 10.0.12
  runtime; 3.6 run with the runtime-only `C:\Program Files\dotnet` that has only 8.0.19 / 8.0.28).
- CLI facts in table 5.1 (`dotnet package add`, `dnx`, `dotnet run app.cs`) cite What's new in the .NET 10 SDK;
  global.json semantics (7.1 note, check-yourself Q7) cite the global.json overview; runtime roll-forward (card 1,
  mapping row, 3.6, warn callout, trap 1, Q4) cites "Select which .NET version to use".

## 5 · Presentation

Format 00 via `brief_pdf.py`; code panels from `lesson_kit`. Local helpers in the module (kit requests):
`listed()` puts a code panel's heading on its block so the Contents lists it, and strips Pygments' red error box
around VB `$"` interpolated strings; `figure_heading()` gives the threecol a numbered, kept-with-next heading;
`cmd()` keeps table-cell commands from wrapping inside themselves; a small style block keeps a callout heading with
its first item. Mermaid 2.1 and 3.5 are `flowchart LR`; 6.2 is `flowchart TB` with `direction LR` subgraphs; 3.1
takes colour from an init directive; 5.2 uses `Note over` instead of self-messages. §5 orders the sequence diagram
before the project-file compare so no page is left more than about a third empty.

## 6 · Inputs

`roster.py`; samples `L01.PlatformKit` (C# library: `PlatformReport` record, `PlatformProbe.Capture`),
`L01.CSharpApp` (C# console), `L01.VbApp` (VB console); regions `report-record`, `capture`, `program`, `equality`;
repo `global.json`, `Directory.Build.props`. Sources: Microsoft Learn — .NET releases and support, Select which .NET
version to use, global.json overview, What's new in the .NET 10 SDK, .NET Framework lifecycle,
Assembly.ImageRuntimeVersion, Visual Basic language strategy, What's new in Visual Basic, .NET managed languages
strategy, What's new in C# 14, The history of C#; dotnet.microsoft.com — .NET support policy, .NET 10 download;
.NET Blog — .NET 8 and 9 end of support.

## 6a · Tariff and cross-lesson consistency

Lesson 01 prices no quote: it contains no premium, rate, loading, discount, stamp-duty or VAT figure, so there is nothing to
align to the canonical tariff (`_curriculum.md`, "Canonical tariff"). The only MotorQuote reference is the §6 sentence
promising that, from lesson 02 onward, the samples model a motor-insurance quoting service; that promise is now true
because every lesson that prices a quote uses the one canonical tariff. The transfer scores in chart 6.1 come from
`roster.py`; lesson 06's 35% is explained the way lesson 06 itself explains it (semantics, not syntax).

## 7 · Invariants

- The VB sample must keep demonstrating consumption-only: it reads and compares the C# record, never copies it.
- Both apps print the same report lines (including `target` and `server GC`) so 4.2, 7.3 and card 2.4 #4 agree.
- Diagram 3.5 must stay connected (every branch reachable from "Any .csproj or .vbproj?").
- No employer or client names (the IIS reference stays "a large multi-application migration estate").

## 8 · Known gaps

- ⚠ Captured output in 3.6 and 7.3 is pasted text; if the sample's output format changes, re-capture it.
- ⚠ The runtime patch number in 7.3 (10.0.12) reflects the build machine on 2026-09-16.
- ⚠ The publish-option cards describe trade-offs qualitatively; no measured start-up or size numbers yet.
- ⚠ `_curriculum.md` has no "Lesson plans" entry for 01 (its plans start at 02); this spec is the only plan to
  check lesson 01 against until the curriculum owner adds one.
