# spec_lesson-pdfs — the lesson PDF set

**Artifact:** twelve lesson PDFs, one per `lesson-NN-<slug>/lesson-NN-<slug>.pdf`, plus the generated
per-lesson `README.md` files and the lesson table in the root `README.md`.

**Renderer:** PDF format 00 (full-spectrum) via the vendored `0-script/_lib/brief_pdf.py`, extended for
code by `0-script/_lib/lesson_kit.py`.

## Files in this folder

| File | What it is |
|---|---|
| `_standard.md` | **The contract every lesson PDF is built to.** Structure, block usage, code-panel rules, honesty labels, visual QA gate. Shared by all units. |
| `_curriculum.md` | The track design: reader profile, running example (motor-insurance quoting), lesson-by-lesson scope and sample plan, and the boundaries between lessons so they don't overlap. |
| `_manifest.json` | Binding unit → spec → builder → content module → samples → output. **Generated** by `build_lessons.py` on every full build (not with `--only`). |
| `lesson-NN-<slug>.md` | One unit spec per lesson: the sections it actually has, what each figure's data is, which facts are verified where, and its known gaps. |

## Unit ownership map

Every unit is **Claude-owned and regenerable** — nothing in the PDF set is hand-edited.

| Unit | Owner | Content module | Samples | Output |
|---|---|---|---|---|
| lesson 01–12 | claude | `0-script/lessons/lesson_NN.py` | `lesson-NN-<slug>/samples/` | `lesson-NN-<slug>/lesson-NN-<slug>.pdf` + `README.md` |
| root lesson table | claude | `0-script/lessons/roster.py` + every `META` | — | `README.md` between the `LESSONS` markers |

The root `README.md` **outside** the `LESSONS` markers, `CLAUDE.md`, `global.json` and `Directory.Build.props`
are hand-maintained repository files, not generated units.

## Rebuild map

```
roster.py ─┐
lesson_NN.py (META + blocks) ─┬─> build_lessons.py ─> brief_pdf.render_brief ─> lesson-NN-<slug>.pdf
lesson_kit.py (panels) ───────┘         │                                        lesson-NN-<slug>/README.md
samples/**/*.cs|*.vb (#region) ──> from_sample()                                 README.md (LESSONS table)
                                        └─> _manifest.json (full build only)
samples/**/*.csproj|*.vbproj ──> verify_samples.py (build · test · run)
```

## Scripts

| Script | Role |
|---|---|
| `0-script/build_lessons.py` | builder for every unit |
| `0-script/verify_samples.py` | gate: every sample builds, every test passes, every console sample runs to completion |
| `0-script/check_tariff.py` | gate: every base-rate line in the samples equals the canonical tariff read from `_curriculum.md` (loadings, no-claim ladder and rounding are checked by each lesson's own tests) |
| `0-script/_lib/lesson_kit.py` | shared helper (code panels, snippets, concept maps, lint) |
| `0-script/_lib/brief_pdf.py`, `chart_svg.py` | vendored renderer — do not edit (`_lib/VENDORED.md`) |
| `0-script/lessons/roster.py` | curriculum data, read by every lesson module |
