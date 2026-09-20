# CLAUDE.md

Guidance for Claude Code when working in this repository.

## What this repository is

A lesson track — **C# · .NET 10 · Visual Basic .NET for a Kotlin/Java, TypeScript and Python architect** — delivered
as **one PDF per lesson** (PDF format 00 · Full Spectrum). It is a knowledge base with compiled samples, not an
application. The reader profile (8 years across Kotlin/Java, TypeScript, Python, Dart; architect / technology
lead; AWS, Terraform, Entra ID, TDD at 100% coverage, mono-repos at scale) drives every "maps from" section.

## The rules that matter

1. **PDFs are generated — never edit a PDF or a lesson README by hand.** Change the lesson module
   `0-script/lessons/lesson_NN.py` (content) or `0-script/_lib/lesson_kit.py` (shared rendering), then
   `python 0-script/build_lessons.py --only NN --qa`.
2. **Every C# and VB code panel comes from a sample file** via `from_sample(path, region)`. Never type C# or VB
   into a lesson module with `from_text` — only comparison code (Java, Kotlin, TypeScript, Python), terminal
   commands and captured output may be inline. Region markers: C# `#region name` / `#endregion`, VB
   `#Region "name"` / `#End Region`.
3. **Samples must pass** `python 0-script/verify_samples.py --only NN` (build · test · run) on the SDK pinned in
   `global.json`. Console samples must terminate on their own. Warnings are errors (`Directory.Build.props`).
4. **Look at the pixels.** After a render, view `.build/qa/lesson-NN/sheet-*.png` (and single `page-*.png` where
   something looks off) before calling a lesson done — structural success is not visual success.
5. **Honesty labels.** Version / support / feature facts link to an official source and carry `VERIFIED`;
   judgements carry `ESTIMATE`; numbers computed from the repo carry `MEASURED`. Never invent benchmark figures.
6. **Spec moves with the builder.** A change to what a lesson PDF contains or how it is structured updates
   `1-analysis/spec_lesson-pdfs/` in the same change (the standard for shared rules, `lesson-NN-<slug>.md` for
   one lesson).
7. **No employer, client or personal identifiers** in lessons — refer to experience generically ("a Kotlin
   mono-repo of 50–120+ modules", "a large multi-application migration estate").

## Commands

```bash
python 0-script/build_lessons.py --list            # roster
python 0-script/build_lessons.py --only 4 --qa     # render lesson 04 + rasterize for review
python 0-script/verify_samples.py --only 4         # build / test / run lesson 04 samples
python 0-script/check_tariff.py                    # every base-rate line matches the canonical MotorQuote tariff
```

SDK on the author's machine: `D:\_env_storeage\dotnet` (portable, not on PATH) — set
`DOTNET_ROOT=D:\_env_storeage\dotnet` before `verify_samples.py`.

## Layout

- `0-script/lessons/roster.py` — the curriculum (numbers, slugs, titles, hours, transfer estimates)
- `0-script/lessons/lesson_NN.py` — `META` + `blocks()` for one lesson; `lesson_01.py` is the reference shape
- `0-script/check_tariff.py` — guards the canonical MotorQuote tariff defined in `_curriculum.md` (run it after touching any rating code)
- `0-script/_lib/lesson_kit.py` — code panels, region snippets, concept-map tables, chip vocabulary
- `0-script/_lib/brief_pdf.py`, `chart_svg.py` — vendored renderer (do not edit; see `VENDORED.md`)
- `1-analysis/spec_lesson-pdfs/` — the written contract for the lesson PDFs
- `lesson-NN-<slug>/samples/` — sample projects, named `LNN.<Purpose>` (e.g. `L05.QuoteService`)
