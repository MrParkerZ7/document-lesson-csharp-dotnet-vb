# Vendored renderer

`brief_pdf.py` and `chart_svg.py` are copied verbatim from the author's prompt-master repo
(`claude-prompt-root-master/shared/workflows/`, commit `2ce3931`, 2026-09-14) so this repository
renders its PDFs with no outside checkout. They implement PDF **format 00 (full-spectrum)** —
the block vocabulary (story · cards · table · callout · chart · chartrow · kpi · mermaid · toc …)
documented in that repo's `shared/prompts/PROMPT_BRIEF_PDF_STANDARD.md`.

- Do not edit them here; lesson-specific rendering lives in `lesson_kit.py`.
- To render with a newer copy without re-vendoring: `BRIEF_PDF_HOME=<folder> python 0-script/build_lessons.py`.
- To upgrade: copy both files again and update the commit above.
