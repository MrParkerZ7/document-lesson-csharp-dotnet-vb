# C# · .NET · Visual Basic — a lesson track for a JVM / TypeScript / Python architect

Twelve lessons, **one PDF per lesson**, that map what an experienced Kotlin/Java, TypeScript and Python
architect already knows onto C#, .NET 10 and Visual Basic .NET — from the runtime model to ASP.NET Core,
EF Core, testing, Entra ID security, AWS deployment and modernising Windows / IIS estates.

- 📄 **PDF format 00 · Full Spectrum** — numbered sections, contents page with real page numbers, concept maps,
  diagrams, charts, code panels, callouts and *Check yourself* questions in every lesson.
- ✅ **Every C# and VB code panel is real** — it is cut by `#region` name from a sample project in the lesson
  folder, and `0-script/verify_samples.py` builds, tests and runs every sample on the .NET 10 SDK.
- 🧭 **Tailored, not generic** — each lesson starts from the stack you have shipped (Kotlin mono-repos, Spring
  WebFlux, Python Lambdas, 100%-coverage TDD, Entra ID SSO, Terraform) and shows the .NET shape of it.

## Lessons

<!-- LESSONS:START -->
| # | Lesson | PDF | Maps from | Samples |
|---|---|---|---|---|
| 01 | [The .NET Platform Map](./lesson-01-dotnet-platform-map/README.md) | [pdf](./lesson-01-dotnet-platform-map/lesson-01-dotnet-platform-map.pdf) | JVM · Maven Central · GraalVM native-image | 3 project(s) |
<!-- LESSONS:END -->

## Repository layout

```
document-lesson-csharp-dotnet-vb/
├── README.md                 ← this file (the lesson table is generated)
├── global.json               ← pins the .NET SDK for every sample
├── Directory.Build.props     ← build settings every sample inherits (net10.0, warnings-as-errors, …)
├── lesson-NN-<slug>/
│   ├── README.md             ← generated: objectives, samples, rebuild commands
│   ├── lesson-NN-<slug>.pdf  ← the lesson
│   └── samples/              ← C# / VB projects the PDF's code panels are cut from
├── 0-script/
│   ├── build_lessons.py      ← renders the PDFs + READMEs
│   ├── verify_samples.py     ← builds, tests and runs every sample
│   ├── lessons/              ← one content module per lesson + roster.py (the curriculum)
│   └── _lib/                 ← lesson_kit.py + the vendored PDF renderer (brief_pdf, chart_svg)
└── 1-analysis/spec_lesson-pdfs/  ← the written contract every lesson PDF is built to
```

## Rebuild

```bash
# samples — needs the .NET 10 SDK (global.json pins 10.0.401, rolls forward to later feature bands)
python 0-script/verify_samples.py              # or --only 5

# PDFs — Windows + Microsoft Edge (headless print), Python deps, and mermaid-cli in the npx cache
pip install -r requirements.txt
npx -y @mermaid-js/mermaid-cli --version       # once, so diagrams render
python 0-script/build_lessons.py               # or --only 5 --qa
```

The contract for a lesson PDF — required sections, block usage, honesty labels, code-panel rules — is
[`1-analysis/spec_lesson-pdfs/_standard.md`](1-analysis/spec_lesson-pdfs/_standard.md).
