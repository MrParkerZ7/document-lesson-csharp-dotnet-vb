# Lesson PDF standard

The contract every `lesson-NN-<slug>.pdf` is built to. `lesson_01.py` is the reference implementation —
when this file and lesson 01 disagree, fix whichever is wrong in the same change.

## 1 · Purpose

Each PDF teaches one topic of C# / .NET 10 / Visual Basic .NET to **one reader**: an architect with ~8 years
across Kotlin/Java, TypeScript, Python and Dart (details in `_curriculum.md` § Reader). A lesson succeeds when
that reader can (a) read and review production .NET code on the topic, (b) write idiomatic C# for it,
(c) recognise the VB.NET form in a legacy estate, and (d) make the architecture decisions the topic implies.

It is a **map, not a restart**: every concept is introduced from something the reader has already shipped,
and labelled by how well that knowledge transfers.

## 2 · Ownership & cadence

- Owner: **claude** (regenerable). Nothing in a PDF or a lesson `README.md` is hand-edited.
- Rebuilt whenever its content module, its samples, `lesson_kit.py` or the vendored renderer changes.
- Content is dated by the build: `lesson_kit.BUILD_DATE`. Version and support facts are re-verified when a new
  .NET major ships (November) or a cited support date passes.

## 3 · Structure

A lesson module `0-script/lessons/lesson_NN.py` exports `META = roster.meta(NN, subtitle, objectives, maps_from)`
and `blocks()`. The block list follows this order:

| # | Block(s) | Rule |
|---|---|---|
| 0 | `style_block()` | **first block, always** — injects the code-panel CSS |
| 1 | `toc` | `{"type":"toc","heading":"▤ Contents","depth":2,"note":…}` |
| 2 | **§1 opener** — `story` "1 · …" | why the topic matters **to this reader**, tied to their experience (generically — see §7 privacy) |
| 3 | `kpi` "1.1 · …" | 4–5 tiles; every value is VERIFIED, MEASURED from the samples, or an explicit estimate |
| 4 | `legend(...)` | the fixed status chips + only the tags this lesson uses |
| 5 | `callout` info | "Before you start" — prerequisites (earlier lessons by `ref(n)`), what you will build |
| 6 | **§2 … §N** — 5 to 7 numbered topic sections | each opens with a `story` that **leads with its point** (bold first sentence); then evidence |
| 7 | **§N+1 · Hands-on** | `story` → commands (`from_text(…, "shell")`) → captured output → one MEASURED chart about the samples |
| 8 | `callout` warn | "⚠ Traps" — 3–5 things that look right to a JVM/TS/Python engineer and are wrong in .NET |
| 9 | `callout` ok | "✔ Checkpoint — you are ready for lesson NN+1 when" (lesson 12: "…when you can") |
| 10 | `callout` summary | "🔍 Check yourself" — 5–7 questions, each answerable with a fact from this lesson |
| 11 | `footer` | one-line lesson summary + `<b>Next:</b> ref(NN+1)` (lesson 12: what to do after the track) |

**Minimum content per lesson** (checked by `lesson_kit.lint_blocks`, a failed check stops the build):

| Element | Minimum | Notes |
|---|---|---|
| numbered `story` sections | 6 | `N · Title`; sub-blocks `N.M · Title` so the TOC nests |
| `mapping(...)` concept tables | 1 | "You already know → In .NET → Kind → Watch for" |
| `cards` sections | 1 | ≤ 3 cards per band — a band never splits across pages, so a big deck jumps whole and leaves a gap; continue a longer deck in a second band titled "… (continued)" with `"toc": False`. Each card line label ≤ 9 characters |
| `mermaid` diagrams | 3 | at least two different diagram families (flowchart · sequence · state · class · ER · gantt · timeline) |
| charts (`chart` / each chart in a `chartrow`) | 3 | every chart has a `note` that says what the data **means** |
| code panels | 6 | from `code(...)` / `compare(...)` |
| C# ↔ VB `compare` | 1 | the same behaviour in both languages, both from samples |
| known-language ↔ C# `compare` | 1 | Java / Kotlin / TypeScript / Python on the left (inline), C# from a sample on the right |
| `twocol` / `threecol` | 1 | |
| `table` (besides mapping) | 1 | |
| `link(...)` to official sources | 4 | Microsoft Learn, devblogs, GitHub repos of the library, AWS docs |

Typical length: **12–20 A4 pages**. Past 22 pages, split content into cards/tables rather than more prose.

## 4 · Derivation — where content comes from

- **C# and VB code is never typed into a lesson module.** It comes from `from_sample(path, region)`, which
  reads a `#region` (C#) / `#Region "…"` (VB) out of a sample file. A missing file or region fails the build.
- Inline `from_text` is allowed only for: comparison code in Java, Kotlin, TypeScript or Python; terminal
  commands; captured program output (copy it from a real run of the sample); config formats that are not
  compiled (YAML, Terraform, JSON, HTTP files) **unless** the sample folder holds that file — then read it.
- **Samples** live in `lesson-NN-<slug>/samples/<Project>/`. Project names start `LNN.` (e.g. `L05.PartnerRates`)
  because build output is shared under `.build/artifacts/` by project name. Every sample inherits the repo
  `Directory.Build.props` (net10.0, nullable, Option Strict On, warnings as errors); a nested
  `Directory.Build.props` must import the parent:
  `<Import Project="$([MSBuild]::GetPathOfFileAbove('Directory.Build.props', '$(MSBuildThisFileDirectory)../'))" />`.
- `verify_samples.py --only NN` must pass: libraries build, test projects pass, console apps (`OutputType Exe`)
  run **and exit on their own** within a few seconds with no input, network or external service. Web apps are
  build-only — exercise them through `WebApplicationFactory` tests.
- **Numbers.** A figure is one of: **VERIFIED** (a dated fact with a `link()` to an official source),
  **MEASURED** (computed at build time from this repo — `loc()`, test counts, output of a sample), or
  **ESTIMATE** (the author's judgement, labelled as such in the caption). Never invent benchmark results,
  latencies, adoption percentages or costs. A rubric chart (e.g. a feature matrix) says "a rubric, not a
  benchmark" in its caption.
- **Transfer map values** (roster `transfer`, `hours`) are estimates owned by `roster.py`.

## 5 · Presentation

- **Chips.** Status: `SAME` · `RENAMED` · `DIFFERENT` · `TRAP` (how knowledge transfers) and `VERIFIED` ·
  `ESTIMATE` · `MEASURED` (how a figure is known). Tags: `T_CS` `T_VB` `T_JVM` `T_TS` `T_PY` `T_RUNTIME`
  `T_TOOLING` `T_CLOUD` `T_LEGACY` `T_ARCH`. Use `KIND[...]` in `mapping()` rows.
- **Headings and captions are plain text** (the renderer escapes them). `note`, `html`, card `what` and card
  line *values*, table *cells* and callout items are raw HTML — escape `<` as `&lt;` there, wrap identifiers
  in `<code>`.
- **Code panels.** Keep regions short and focused: a `code()` panel ≤ 35 lines and ≤ 100 characters per line;
  each side of a `compare()` ≤ 30 lines and ≤ 62 characters per line (wider lines wrap and look broken).
  Every panel is followed by a `note` saying what to notice. Use sample comments to annotate, sparingly.
  A panel of ≤ 18 lines (a `compare` of ≤ 24) is kept whole on one page; a longer one may split across pages.
  Pass `keep=False` when a kept panel would jump to the next page and strand a large gap.
- **Pagination.** No page may be left more than about a third empty except the last. When an unbreakable
  block (card band, figure, kept panel, diagram) jumps and leaves a gap, reorder the blocks, split the band,
  or shrink the figure — visual QA is where this is caught.
- **Mermaid** (constraints in the comment block above `render_mermaid_svg` in `brief_pdf.py`):
  quote every label; `<br/>` for line breaks; no node id `end`; `classDef` only in flowchart / state / class
  diagrams, every `classDef` carries `color:#1f2937`; other families take colour from an `%%{init:…}%%`
  directive; prefer `flowchart LR` or `TB` with `direction LR` subgraphs over long single-row chains (they
  render as an unreadable strip); set `"inline": True` unless the diagram deserves its own page. The caption
  explains the colour language.
- **Charts** (`chart_svg`): charts in a `chartrow` use `width` ≈ 390; `heatmap` `cell` ≤ 44; `progress`
  `labelw` sized to the longest label. Prefer measured/verified data; label estimates.
- **Language.** English, direct, second person ("you"), present tense. Bold first sentence in every story
  paragraph. Explain *why* before *how*. No filler, no marketing adjectives.
- **Cross-references** use `ref(n)` from `roster.py`, never a hard-coded title.

## 6 · Inputs

- `0-script/lessons/roster.py` (numbers, slugs, titles, hours, transfer estimates, phases)
- `1-analysis/spec_lesson-pdfs/_curriculum.md` (scope, running example, sample plan, lesson boundaries)
- the lesson's `samples/` tree; repo `global.json` + `Directory.Build.props`
- official documentation, cited with `link()` (Microsoft Learn, .NET Blog, AWS docs, library repos)

## 7 · Invariants

1. Every C# / VB panel resolves to a sample region; every sample passes `verify_samples.py`.
2. `build_lessons.py --only NN --qa` completes with no lint error, no "diagram not rendered" fallback, no
   chart failure and a verified Contents page (`TocMismatch` never suppressed).
3. **Visual QA is mandatory:** view every `.build/qa/lesson-NN/sheet-*.png`, and the full-size `page-*.png`
   of any page that looks wrong, before the lesson is called done. Fix: diagrams too small to read, tables
   with wrapped one-word columns, a figure stranded after a large white gap, code panels with wrapped lines.
4. **Privacy:** no employer, client, bank, insurer or colleague names; no personal data. Experience is
   referenced generically ("a Kotlin mono-repo of 50–120+ modules", "a motor-insurance platform with ~30
   external partner integrations", "a migration estate of 80+ applications").
5. No contradiction with another lesson: boundaries in `_curriculum.md` decide which lesson owns a topic;
   others give one sentence and a `ref(n)`.
6. The unit spec `lesson-NN-<slug>.md` describes what the built PDF actually contains.

## 8 · Known gaps

- ⚠ Visual QA is a human/Claude check on rasterized pages; there is no pixel-diff regression test.
- ⚠ Inline comparison code (Java/Kotlin/TypeScript/Python) is not compiled.
- ⚠ Rendering requires Windows + Microsoft Edge and mermaid-cli in the npx cache; the PDFs are committed so
  readers do not need the toolchain.
- ⚠ Facts marked VERIFIED are verified as of the build date shown on the lesson's KPI row or subtitle; support
  dates and preview features move.
