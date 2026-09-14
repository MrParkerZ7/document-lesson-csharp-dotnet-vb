# Unit spec — lesson-01-dotnet-platform-map.pdf

Built to `_standard.md`. Content module `0-script/lessons/lesson_01.py` (the reference implementation for every
other lesson). Samples `lesson-01-dotnet-platform-map/samples/`.

## 1 · Purpose

Orient a JVM / TypeScript / Python architect in the .NET platform before any language detail: what the runtime
is, how versions and support work, how C#, VB and F# relate, what the CLI and publish modes are, and how the
twelve-lesson track is laid out.

## 2 · Ownership & cadence

Owner **claude**, regenerable. Re-verify the support dates and the `kpi` countdown every November (new .NET
major) and after **10 Nov 2026** (the .NET 8/9 tile then reads "ended").

## 3 · Structure

| § | Heading | Blocks |
|---|---|---|
| — | Contents | `toc` depth 2 |
| 1 | Why this track exists — and who it is written for | story · `kpi` 1.1 (5 tiles) · `legend` · info callout "How to read every lesson" |
| 2 | The platform in one picture | story · mermaid 2.1 flowchart (source → IL → JIT / R2R / AOT) · cards 2.2 (5 runtime pieces) · mapping 2.3 (16 rows) |
| 3 | Versions — how to read a .NET codebase's age | story · mermaid 3.1 gantt (support windows) · chartrow 3.2 bar (support months) + 3.3 donut (study hours by phase) · table 3.4 (TFMs) · mermaid 3.5 flowchart (dating a repository) · warn callout (10 Nov 2026) |
| 4 | Three languages, one runtime | story · code 4.1 (C# record) · compare 4.2 (C# ↔ VB program) · compare 4.3 (Kotlin ↔ C# record copy) · code 4.4 (VB consuming the record) · chart 4.5 heatmap (feature rubric) · threecol (carry / learn / unlearn) |
| 5 | The toolchain — one CLI, five ways to ship | story · table 5.1 (CLI vs Maven/Gradle/npm) · compare 5.2 (csproj ↔ vbproj) · cards 5.3 (5 publish modes) · mermaid 5.4 sequence (`dotnet run`) |
| 6 | Your transfer map and learning path | story · chart 6.1 progress (transfer per lesson) · mermaid 6.2 flowchart (phases) · table 6.3 (twelve lessons) |
| 7 | Hands-on — build and run the lesson-01 samples | story · code 7.1 `global.json` + `Directory.Build.props` · code 7.2 commands · compare 7.3 captured output · chart 7.4 bar (lines of code) · warn callout (day-one traps) · ok checkpoint · summary "Check yourself" (6) · footer |

## 4 · Derivation

- KPI ".NET 8 & 9 support" = `days_until(2026, 11, 10)` from the build date (MEASURED at build); ".NET 10 · LTS"
  and the support windows in 3.1/3.2 are VERIFIED (links in §3 story and the warn callout).
- KPI "This track" and chart 3.3 = sums of `roster.py` `hours` (ESTIMATE); chart 6.1 = `roster.py` `transfer`
  (ESTIMATE); table 6.3 is generated from `ROSTER`.
- KPI "Lesson 01 samples" and chart 7.4 = `loc()` over the three sample source files (MEASURED).
- Chart 4.5 heatmap is a rubric (yes / some / —), stated as such in its caption.
- Panel 7.3 output is captured from a real run on the build machine (Windows, .NET 10.0.12 runtime).

## 5 · Presentation

Format 00 via `brief_pdf.py`; code panels from `lesson_kit`. Mermaid 3.5 is `flowchart LR`, 6.2 is `flowchart TB`
with `direction LR` subgraphs (a single-row chain rendered as an unreadable strip). Heatmap cell 44. ~13 pages.

## 6 · Inputs

`roster.py`; samples `L01.PlatformKit` (C# library), `L01.CSharpApp` (C# console), `L01.VbApp` (VB console);
repo `global.json`, `Directory.Build.props`. Sources: Microsoft Learn — .NET releases and support, Visual Basic
language strategy, .NET managed languages strategy, What's new in C# 14; .NET Blog — .NET 8 and 9 end of support.

## 7 · Invariants

- The VB sample must keep demonstrating consumption-only: it reads and compares the C# record, never copies it.
- Diagram 3.5 must stay connected (every branch reachable from "Open the repository").
- No employer or client names (the IIS reference stays "a large multi-application migration estate").

## 8 · Known gaps

- ⚠ Captured output in 7.3 is pasted text; if the sample's output format changes, re-capture it.
- ⚠ The runtime patch number in 7.3 (10.0.12) reflects the build machine on 2026-09-14.
- ⚠ The publish-mode cards describe trade-offs qualitatively; no measured start-up or size numbers yet.
