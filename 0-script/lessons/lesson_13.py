# -*- coding: utf-8 -*-
"""Lesson 13 — Working in Visual Studio. Built to 1-analysis/spec_lesson-pdfs/_standard.md;
unit spec 1-analysis/spec_lesson-pdfs/lesson-13-visual-studio-workflows.md.

A companion lesson: IDE behaviour cannot be run by a script, so every claim about what Visual Studio does is
VERIFIED against an official page fetched on VERIFIED_ON and linked; the samples prove only the parts that
are files and code (the settings Visual Studio reads, code that exercises the debugger)."""
import json
import re

from lesson_kit import (DIFFERENT, ESTIMATE, MEASURED, RENAMED, REPO, SAME, TRAP, VERIFIED, T_ARCH, T_CS, T_JVM,
                        T_LEGACY, T_TOOLING, T_VB, code, compare, esc, from_sample, from_text, legend, link,
                        mapping, pill, style_block)
from lessons.roster import meta, ref

META = meta(
    13,
    subtitle="A companion for teams that live in the IDE — Community, Professional and Enterprise compared "
             "without prices, the files Visual Studio reads (.vsconfig, .slnx, launchSettings, .runsettings, "
             ".editorconfig), the debugger and Test Explorer, and where VS Code and Rider fit",
    objectives=[
        "Explain why dotnet build and Build-in-Visual-Studio give the same result, and name the few things "
        "that legitimately differ (workloads, installed SDKs, two command-line-only files)",
        "Choose between Community, Professional and Enterprise from the licence rules and the features that "
        "are gated, using only claims you can check on an official page",
        "Share a Visual Studio setup through .vsconfig, .slnx, .editorconfig and .runsettings so the IDE and "
        "the CLI read the same files",
        "Drive the debugger with intent: conditional and dependent breakpoints, tracepoints, DebuggerDisplay, "
        "exception settings, Just My Code, Hot Reload and its limits",
        "Run and organise tests in Test Explorer, and reach the same tests, filters and settings from the CLI",
        "Decide when VS Code with the C# Dev Kit or JetBrains Rider is the better tool for a developer",
    ],
    maps_from="IntelliJ IDEA and Android Studio (Gradle run configurations, the debugger, inspections), "
              "VS Code for TypeScript and Python, and the CI pipelines you already run from the command line.",
)

VERIFIED_ON = "2026-09-21"          # the day every VERIFIED claim below was read on its official page
L = "lesson-13-visual-studio-workflows/samples"
CS = f"{L}/L13.DebugLab"
VB = f"{L}/L13.DebugLabVb"
TESTS = f"{L}/L13.DebugLab.Tests"
PERF = f"{L}/L13.PerfLab"
SLNX = f"{L}/L13.slnx"
VSCONFIG = f"{L}/.vsconfig"
EDITORCFG = f"{L}/.editorconfig"
RUNSETTINGS = f"{L}/.runsettings"
LAUNCH = f"{CS}/Properties/launchSettings.json"

# ── official sources (each read on VERIFIED_ON) ──────────────────────────────────────────────
COMPARE = link("Visual Studio editions comparison", "https://visualstudio.microsoft.com/vs/compare/")
RELHIST = link("Visual Studio 2026 release history",
               "https://learn.microsoft.com/en-us/visualstudio/releases/2026/release-history")
SERVICING = link("Visual Studio product lifecycle and servicing",
                 "https://learn.microsoft.com/en-us/visualstudio/releases/2026/servicing-vs")
VS26 = link("Visual Studio 2026 announcement",
            "https://devblogs.microsoft.com/visualstudio/visual-studio-2026-is-here-faster-smarter-and-a-hit-"
            "with-early-adopters/")
VSCONFIGDOC = link("import or export installation configurations",
                   "https://learn.microsoft.com/en-us/visualstudio/install/import-export-installation-configurations")
COMPIDS = link("workload and component IDs",
               "https://learn.microsoft.com/en-us/visualstudio/install/workload-component-id-vs-professional")
SLNXVS = link("the simpler solution file format",
              "https://devblogs.microsoft.com/visualstudio/new-simpler-solution-file-format/")
SLNXBREAK = link("dotnet new sln defaults to SLNX",
                 "https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/10.0/dotnet-new-sln-slnx-default")
FILTERS = link("solution filters in Visual Studio",
               "https://learn.microsoft.com/en-us/visualstudio/ide/filtered-solutions")
RSPDOC = link("MSBuild response files",
              "https://learn.microsoft.com/en-us/visualstudio/msbuild/msbuild-response-files")
GLOBALJSON = link("global.json and rollForward",
                  "https://learn.microsoft.com/en-us/dotnet/core/tools/global-json")
BREAKPOINTS = link("use the right type of breakpoint",
                   "https://learn.microsoft.com/en-us/visualstudio/debugger/using-breakpoints")
JMC = link("Just My Code", "https://learn.microsoft.com/en-us/visualstudio/debugger/just-my-code")
EXCEPTIONS = link("manage exceptions with the debugger",
                  "https://learn.microsoft.com/en-us/visualstudio/debugger/managing-exceptions-with-the-debugger")
TASKSWIN = link("the Tasks window",
                "https://learn.microsoft.com/en-us/visualstudio/debugger/using-the-tasks-window")
DECOMPILE = link("decompile .NET code while debugging",
                 "https://learn.microsoft.com/en-us/visualstudio/debugger/decompilation")
ATTACH = link("attach to running processes",
              "https://learn.microsoft.com/en-us/visualstudio/debugger/attach-to-running-processes-with-the-"
              "visual-studio-debugger")
HOTRELOAD = link("Hot Reload", "https://learn.microsoft.com/en-us/visualstudio/debugger/hot-reload")
ENCWIKI = link("Supported Edits in Edit and Continue and Hot Reload",
               "https://github.com/dotnet/roslyn/blob/main/docs/wiki/EnC-Supported-Edits.md")
DOTNETRUN = link("dotnet run", "https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-run")
SUPPORTED = link("supported code changes",
                 "https://learn.microsoft.com/en-us/visualstudio/debugger/supported-code-changes-csharp")
ENVIRONMENTS = link("launchSettings.json in ASP.NET Core",
                    "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/environments")
TESTEXPLORER = link("run unit tests with Test Explorer",
                    "https://learn.microsoft.com/en-us/visualstudio/test/run-unit-tests-with-test-explorer")
RUNSETTINGSDOC = link(".runsettings files",
                      "https://learn.microsoft.com/en-us/visualstudio/test/configure-unit-tests-by-using-a-dot-"
                      "runsettings-file")
COVERAGE = link("code coverage in Visual Studio",
                "https://learn.microsoft.com/en-us/visualstudio/test/using-code-coverage-to-determine-how-much-"
                "code-is-being-tested")
LUT = link("Live Unit Testing", "https://learn.microsoft.com/en-us/visualstudio/test/live-unit-testing")
FAKES = link("Microsoft Fakes",
             "https://learn.microsoft.com/en-us/visualstudio/test/isolating-code-under-test-with-microsoft-fakes")
XUNITMTP = link("xUnit.net v3 and Microsoft.Testing.Platform",
                "https://xunit.net/docs/getting-started/v3/microsoft-testing-platform")
CODESTYLE = link("code style options and Code Cleanup",
                 "https://learn.microsoft.com/en-us/visualstudio/ide/code-styles-and-code-cleanup")
COPILOT = link("Get started with GitHub Copilot in Visual Studio",
               "https://learn.microsoft.com/en-us/visualstudio/ide/visual-studio-github-copilot-get-started")
COPILOTFREE = link("GitHub Copilot Free in Visual Studio",
                   "https://learn.microsoft.com/en-us/visualstudio/ide/copilot-free-plan")
PROFILING = link("the profiling tools overview",
                 "https://learn.microsoft.com/en-us/visualstudio/profiling/profiling-feature-tour")
DIAGTOOLS = link(".NET diagnostics tools", "https://learn.microsoft.com/en-us/dotnet/core/diagnostics/")
WINFORMS = link("the WinForms designer for .NET",
                "https://learn.microsoft.com/en-us/dotnet/desktop/winforms/controls-design/designer-overview")
DEVKITFAQ = link("C# Dev Kit licensing FAQ", "https://code.visualstudio.com/docs/csharp/cs-dev-kit-faq")
DEVKIT = link("C# in VS Code", "https://code.visualstudio.com/docs/csharp/get-started")
RIDER = link("JetBrains Rider", "https://www.jetbrains.com/rider/")
NUGETVS = link("install and manage packages in Visual Studio",
               "https://learn.microsoft.com/en-us/nuget/consume-packages/install-use-packages-visual-studio")
CPM = link("Central Package Management",
           "https://learn.microsoft.com/en-us/nuget/consume-packages/central-package-management")
OPENFOLDER = link("develop code without projects or solutions",
                  "https://learn.microsoft.com/en-us/visualstudio/ide/develop-code-in-visual-studio-without-"
                  "projects-or-solutions")
DOTNETADD = link("dotnet package add", "https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-add-package")
DOTNETBUILD = link("dotnet build", "https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-build")
SOURCELINK = link("Source Link", "https://learn.microsoft.com/en-us/visualstudio/debugger/how-to-improve-"
                                 "diagnostics-debugging-with-sourcelink")
DATATIPS = link("data tips", "https://learn.microsoft.com/en-us/visualstudio/debugger/view-data-values-in-data-"
                             "tips-in-the-code-editor")
CODEANALYSIS = link("code analysis overview — enforce code style on build",
                    "https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/overview")
DBGDISPLAY = link("DebuggerDisplay",
                  "https://learn.microsoft.com/en-us/visualstudio/debugger/using-the-debuggerdisplay-attribute")

M = json.loads((REPO / f"{L}/tools/measurements.json").read_text(encoding="utf-8"))
PERFM = M["perflab"]
PERFD = M["perflab_debug"]
TRAITS = M["tests"]["by_trait"]

_ERROR_SPAN = re.compile(r'<span style="border: 1px solid #F00">(.*?)</span>', re.S)
_CODEH_CSS = ("font-weight:700;font-size:10pt;color:#1A237E;margin:12px 0 4px;border-bottom:2px solid #C5CAE9;"
              "padding-bottom:2px;break-after:avoid;page-break-after:avoid;")


def Ref(n):
    """ref() for the start of a sentence."""
    r = ref(n)
    return r[0].upper() + r[1:]


def short(a, label):
    """The same link with a short label - for the narrow Source column of a table, where a long official
    title breaks inside words."""
    return re.sub(r'>[^<]*</a>', '>' + esc(label) + '</a>', a, count=1)


def listed(block, heading):
    """Clean VB highlighting (as lesson 07). Unlike lesson 07 the panels are NOT listed in the Contents: with
    every panel listed the Contents ran to sixty entries, no longer fitted under the title, and cost page 1
    (kit request: an optional level for panel headings)."""
    if "vb" in block.get("_langs", []):
        block["html"] = _ERROR_SPAN.sub(r"\1", block["html"])
    return block


def figure_heading(text):
    """A numbered heading for a block type that prints none of its own (threecol), kept with that block."""
    return {"type": "html", "html": f'<div class="figh"><h2>{esc(text)}</h2></div>', "heading": text,
            "toc": 2, "_keep_with_next": True}


def pcode(s, heading, note, keep=None):
    return listed(code(s, heading=heading, note=note, keep=keep), heading)


def pcompare(left, right, heading, note, keep=None):
    return listed(compare(left, right, heading=heading, note=note, keep=keep), heading)


def cmd(*commands):
    """Table-cell commands that never wrap inside themselves (as lesson 07)."""
    return " · ".join(f'<code style="white-space:nowrap">{c}</code>' for c in commands)


def sample(path, region=None, lang=None, label=None, file=None):
    """from_sample() with the language forced for file types the kit does not know (.runsettings, .vsconfig);
    `file` shortens the panel header where a half-width compare panel would cut the path."""
    s = from_sample(path, region, label=label)
    if lang:
        s["lang"] = lang
    if file:
        s["file"] = file
    return s


def _configs():
    """MEASURED at build time: every file that configures Visual Studio or the build in this lesson's
    samples plus the repository's own root files, with its line count."""
    rows = []
    for f in M["config_files"]:
        if f["file"].endswith((".csproj", ".vbproj")):
            continue
        name = f["file"].split("/")[-1]
        lines = len((REPO / L / f["file"]).read_text(encoding="utf-8").splitlines())   # read from disk now
        rows.append(("Directory.Build.props (samples)" if name == "Directory.Build.props" else name, lines))
    rows += [(label, len((REPO / name).read_text(encoding="utf-8").splitlines()))
             for label, name in (("global.json", "global.json"),
                                 ("Directory.Build.props (root)", "Directory.Build.props"))]
    return rows


def _projects():
    """MEASURED: the project files in this lesson's samples, read from disk."""
    root = REPO / L
    return sorted(p.name for p in root.rglob("*") if p.suffix in (".csproj", ".vbproj"))


def _s1():
    cfg, projs = _configs(), _projects()
    return [
        {"type": "story", "heading": "1 · Why an IDE, when the CLI builds everything",
         "html": (
             "<p><b>The first twelve lessons drive .NET from a terminal because a terminal is what CI runs — "
             "but your team probably opens Visual Studio every morning.</b> A JVM developer arrives with "
             "IntelliJ IDEA or Android Studio in the muscle memory: a run configuration, inspections that "
             "travel with the repository, a debugger that evaluates expressions. Visual Studio has an answer "
             "for each, and most of them live in <i>files you can commit</i>. This lesson is a companion, not a "
             "prerequisite: read it after " + ref(7) + " (solutions and MSBuild), or the day you join a team "
             "that lives in the IDE. It assumes " + ref(1) + " for the SDK and CLI.</p>"
             "<p><b>One rule keeps the IDE and the command line from drifting apart: the solution and project "
             "files are the source of truth, and both front ends only read them.</b> Build &gt; Build Solution "
             "and <code>dotnet build</code> run the same MSBuild targets over the same <code>.csproj</code>, "
             "<code>Directory.Build.props</code> and <code>global.json</code>. If a build passes in one and "
             "fails in the other, something outside the files both front ends read differs — an installed "
             "workload, an SDK, or a file only the command line reads: <code>Directory.Build.rsp</code> "
             "(a switch the IDE never sees) and <code>Directory.Solution.props</code> / "
             "<code>.targets</code> (they run only when MSBuild builds the solution, never inside Visual "
             "Studio). See " + ref(7) + " §4.5 and " + RSPDOC + ". §3 shows how to make that list "
             "shorter.</p>"
             "<p><b>So the IDE is not where your build lives; it is the best instrument for looking at a "
             "running program.</b> Its strengths are the ones a terminal cannot match — a debugger you can "
             "aim, a test runner that shows state, a profiler, designers, and refactorings that see the whole "
             "solution. Its weakness is the one you already know: a setting that lives only in a per-user "
             "Options dialog is invisible to a colleague and to CI. Every section from §3 to §7 is therefore "
             "anchored on a file that carries the setting into the repository. Facts about the product are "
             f"<b>VERIFIED</b> against an official page read on {VERIFIED_ON}; the samples prove only the parts "
             "that are code and files.</p>")},

        {"type": "kpi", "heading": "1.1 · The numbers to leave this lesson with",
         "items": [
             {"label": "Visual Studio 2026", "value": "18.10.1", "tone": "indigo",
              "sub": f"current Stable release, 2026-09-15 · VERIFIED {VERIFIED_ON}"},
             {"label": "First 2026 release", "value": "18.0.0", "tone": "violet",
              "sub": "released 2025-11-11 · release history"},
             {"label": "Sample projects", "value": f"{len(projs)} projects", "tone": "teal",
              "sub": "C# and VB · build without Visual Studio · measured"},
             {"label": "Tests in Test Explorer", "value": f"{M['tests']['total']} tests", "tone": "amber",
              "sub": f"{TRAITS['Tariff']} Tariff · {TRAITS['Batch']} Batch · {TRAITS['Environment']} "
                     "Environment · measured"},
             {"label": "Files the IDE reads", "value": f"{len(cfg) + len(projs)} files", "tone": "navy",
              "sub": f"{len(cfg)} settings files + {len(projs)} project files · measured"}]},

        legend(T_TOOLING),

        {"type": "callout", "variant": "info", "heading": "ℹ Before you start",
         "items": [
             "<b>You need " + ref(1) + " and " + ref(7) + ".</b> Lesson 01 gave you the CLI and the "
             "<code>global.json</code> trap; lesson 07 gave you solutions, <code>Directory.Build.props</code> "
             "and analyzers. Nothing here replaces them — it shows the IDE side of the same files.",
             "<b>You do not need Visual Studio to run anything in this lesson.</b> "
             f"{len(projs)} sample projects (C#, Visual Basic, xUnit v3) build and pass on the pinned SDK with "
             + cmd("python 0-script/verify_samples.py --only 13") + ". Open <code>samples/L13.slnx</code> in "
             "Visual Studio if you have it, and every step in §11 works there too.",
             "<b>Every claim about the IDE carries a source.</b> Editions, licence terms, version numbers and "
             "feature gating change several times a year, so this lesson prints no prices and labels anything "
             "it could not confirm on an official page. Read the page linked next to a claim before you "
             "act on it."]},

        {"type": "mermaid", "inline": True, "heading": "1.2 · Two front ends, one set of files",
         "caption": "indigo = files you commit · teal = shared build engine · amber = only the IDE · rose = only the "
                    "command line — a difference comes from an amber or rose box, never from the files both "
                    "front ends read",
         "code": ("flowchart TB\n"
                  '  D1["Only in the IDE:<br/>workloads, its own SDK,<br/>designers, debugger UI"]:::ide\n'
                  '  F["Files you commit<br/>.slnx · .csproj · .vbproj · Directory.Build.props<br/>global.json · '
                  '.editorconfig · .runsettings<br/>launchSettings.json · .vsconfig"]:::file\n'
                  '  D2["Only on the command line:<br/>Directory.Build.rsp,<br/>Directory.Solution.props/.targets,<br/>'
                  'the SDK found on PATH"]:::cli\n'
                  '  IDE["Visual Studio<br/>Build · F5 · Test Explorer"]:::ide\n'
                  '  CLI["dotnet CLI<br/>build · run · test"]:::cli\n'
                  '  MSB["MSBuild + the .NET SDK<br/>same targets, same output"]:::eng\n'
                  "  D1 -.differs.-> IDE\n"
                  "  F --> IDE\n"
                  "  F --> CLI\n"
                  "  D2 -.differs.-> CLI\n"
                  "  IDE --> MSB\n"
                  "  CLI --> MSB\n"
                  "  classDef file fill:#c7d2fe,color:#1f2937,stroke:#6366f1;\n"
                  "  classDef eng fill:#ccfbf1,color:#1f2937,stroke:#0d9488;\n"
                  "  classDef ide fill:#fde68a,color:#1f2937,stroke:#d97706;\n"
                  "  classDef cli fill:#fecdd3,color:#1f2937,stroke:#e11d48;\n")},

        {"type": "html", "html": "", "_keep_with_next": True},
        {"type": "table", "heading": "1.3 · Where the IDE wins, where the CLI wins",
         "cols": ["Job", "Reach for the IDE when", "Reach for the CLI when", "Source"],
         "rows": [
             ["<b>Debugging</b>", "you need to aim: conditional and dependent breakpoints, data tips, "
              "Just My Code, attach to a process", "you only need a stack trace in a log", short(BREAKPOINTS, "Breakpoint docs")],
             ["<b>Testing</b>", "you want state, grouping by trait and a one-click debug of one test",
              "the same tests must run identically in CI: <code>dotnet test</code>", short(TESTEXPLORER, "Test Explorer docs")],
             ["<b>Refactoring</b>", "the change spans a solution — Quick Actions and Refactorings",
              "you script a bulk style fix: <code>dotnet format</code>, as in " + ref(7),
              short(CODESTYLE, "Code style docs")],
             ["<b>Designers</b>", "you edit a WinForms form for .NET — the designer runs beside the IDE",
              "you only build or test the project: the form is code, and MSBuild compiles it",
              short(WINFORMS, "WinForms designer")],
             ["<b>Reproducible builds</b>", "never the source of truth — it reads the same files",
              "always: CI, release, anything another machine must repeat", short(GLOBALJSON, "global.json docs")],
             ["<b>Profiling</b>", "you want a guided tool for a Release build",
              "the machine has no Visual Studio: <code>dotnet-trace</code>, <code>dotnet-counters</code>",
              short(PROFILING, "Profiling docs")]]},
    ]


# the rows the comparison page marks Enterprise-only, read from the accessible labels of its icon cells
# ("feature available" / "feature not available") on VERIFIED_ON, in the order of the page's sections
ENT_SECTIONS = [("Debugging and diagnostics", 5), ("IDE and architecture", 4), ("Testing tools", 3),
                ("Performance hub", 1), ("Cross-platform", 1)]
ENT_ROWS = ["Live Dependency Validation", "Architectural Layer Diagrams", "Architecture Validation", "Code Clone",
            "IntelliTrace", "Code Map debugger link", ".NET Memory Dump Analysis", "Snapshot Debugger",
            "Time Travel Debugging", "Tier Interaction Profiling", "Live Unit Testing", "IntelliTest",
            "Microsoft Fakes", "Embedded Assemblies", "Code Coverage"]
assert sum(n for _, n in ENT_SECTIONS) == len(ENT_ROWS) - 1


def _s2():
    cards = [
        {"num": 1, "title": "Community", "tags": [T_TOOLING], "pills": [VERIFIED],
         "what": "The full IDE, free, for a stated list of users — the comparison page names them.",
         "lines": [("Who", "Individuals, classroom learning, academic research, open-source work, and "
                            "non-enterprise organisations with up to 5 users"),
                   ("Excluded", "An enterprise organisation: more than 250 PCs or more than US$1 million in annual "
                                "revenue (as the page defines it)"),
                   ("Channels", "Stable and Insiders only; must be updated within 180 days"),
                   ("Read", COMPARE + " · " + SERVICING)]},
        {"num": 2, "title": "Professional", "tags": [T_TOOLING], "pills": [VERIFIED],
         "what": "The paid team edition: what an organisation outside Community's rules assigns to developers.",
         "lines": [("Buys", "The same IDE, licensed for a team, plus the LTSC servicing channels Community "
                            "does not get"),
                   ("Testing", "Test Explorer and, in VS 2026, code coverage; not Live Unit Testing"),
                   ("Copilot", "Sold by GitHub plan, not by edition — see §7"),
                   ("Read", SERVICING + " · " + COVERAGE)]},
        {"num": 3, "title": "Enterprise", "tags": [T_TOOLING], "pills": [VERIFIED],
         "what": "Professional plus the 14 rows the comparison page marks Enterprise-only (chart 2.3).",
         "lines": [("Adds", "Live Unit Testing, Microsoft Fakes, IntelliTest, IntelliTrace, .NET memory dump "
                            "analysis, Snapshot Debugger, Time Travel Debugging (Preview), architecture and "
                            "layer-diagram tools, Tier Interaction Profiling, and more"),
                   ("Ask", "Does your team use any of them? Read the whole list on the comparison page "
                           "before you buy"),
                   ("Read", COMPARE + " · " + LUT + " · " + FAKES),
                   ("Note", "Gating moves between releases (see 2.3) — check the page for your version")]}]

    return [
        {"type": "story", "heading": "2 · The editions — Community, Professional, Enterprise",
         "html": (
             "<p><b>Three editions share one IDE; licence terms separate them first and the Enterprise-only "
             "tools second.</b> Community is the full IDE for a stated list of users: individual developers, "
             "classroom learning, academic research, contributing to open source, and non-enterprise "
             "organisations with up to five users. The page also defines the organisations that are "
             "<i>excluded</i> — more than 250 PCs or more than US$1 million in annual revenue — so a "
             f"commercial team of any size has to read that definition before it installs (" + COMPARE + ", read "
             f"{VERIFIED_ON}). When Community's rules exclude an organisation, the choice is Professional or "
             "Enterprise.</p>"
             "<p><b>Professional is what an organisation outside Community's rules assigns to developers who "
             "use none of the Enterprise-only tools — the comparison page marks 14 rows that way (2.3).</b> "
             "Servicing is the clearest difference you will feel: Microsoft ships Visual Studio 2026 on a "
             "modern lifecycle of two years of servicing per annual release, the second year security-only, "
             "delivered through the LTSC channel; the current Stable release is 18.10.1 (2026-09-15) and "
             "18.0.0 shipped on 2025-11-11 (" + RELHIST + " · " + VS26 + "). Community follows the Stable and "
             "Insiders channels and must "
             "keep up within 180 days; Professional and Enterprise can also hold an LTSC baseline (" + SERVICING
             + ").</p>"
             "<p><b>Feature gating moves, so read the feature's own page for your version.</b> Code coverage "
             "is the example that will bite you: the Microsoft page says it is available in Enterprise, "
             "Community and Professional in Visual Studio 2026, and that in Visual Studio 2022 and earlier it "
             "was limited to Enterprise (" + COVERAGE + "), while the Test Explorer page still says "
             "Enterprise in one sentence (" + TESTEXPLORER + "). "
             "When Microsoft's pages disagree, trust the menu in your own "
             "edition and record which page you followed. <b>No prices appear in this lesson</b>: they and the "
             "subscription terms change, and only Microsoft's page is authoritative.</p>")},

        {"type": "mermaid", "inline": True, "heading": "2.1 · Which edition — the decision as a flow",
         "caption": "indigo = a question · teal = an outcome · the licence terms Microsoft publishes bind you, "
                    "not this chart — confirm there before you install",
         "code": ("flowchart TB\n"
                  '  Q1["Individual, classroom, academic, open source,<br/>'
                  'or a non-enterprise organisation<br/>of up to 5 users?"]:::q\n'
                  '  Q2["Need a tool the comparison page<br/>marks Enterprise-only<br/>(the 14 rows of chart 2.3)?"]:::q\n'
                  '  C["Community"]:::out\n'
                  '  E["Enterprise"]:::out\n'
                  '  P["Professional<br/>(and LTSC servicing if you need it)"]:::out\n'
                  "  Q1 -->|yes| C\n"
                  "  Q1 -->|no| Q2\n"
                  "  Q2 -->|yes| E\n"
                  "  Q2 -->|no| P\n"
                  "  classDef q fill:#c7d2fe,color:#1f2937,stroke:#6366f1;\n"
                  "  classDef out fill:#ccfbf1,color:#1f2937,stroke:#0d9488;\n")},

        {"type": "cards",
         "band": {"title": "2.2 · One card per edition — and what Professional buys a team", "note": "verified",
                  "tone": "indigo"},
         "cards": cards},

        {"type": "chartrow", "charts": [
            {"heading": "2.3 · What each edition has — the Enterprise-only rows", "kind": "heatmap",
             "args": {"rows": ENT_ROWS, "cols": ["Com", "Pro", "Ent"],
                      "matrix": [[0, 0, 1]] * (len(ENT_ROWS) - 1) + [[1, 1, 1]],
                      "width": 260, "cell": 22, "tone": "indigo", "fmt": lambda v: "✓" if v else "—"},
             "caption": "Com = Community · Pro = Professional · Ent = Enterprise · ✓ = the comparison page marks "
                        "it “feature available” · — = “feature not available” · rubric, not a benchmark · read "
                        + VERIFIED_ON,
             "note": "<b>14 rows are Enterprise-only; code coverage, last row, is in all three.</b> The cells "
                     "on " + COMPARE + " are icons whose accessible labels this chart reads; Tier Interaction "
                     "Profiling is the one row stated as text. " + VERIFIED + "."},
            {"heading": "2.4 · The 14, by section of the page", "kind": "hbar",
             "args": {"data": ENT_SECTIONS, "tone": "amber", "width": 300, "labelw": 130},
             "caption": "count of rows per section of the comparison page · same read as 2.3",
             "note": "<b>Debugging and testing tools carry most of them.</b> Coverage moved from Enterprise-only "
                     "(Visual Studio 2022 and earlier) to all three in 2026 (" + COVERAGE + "). Gating moves; "
                     "read the page for your version."}]},
    ]


def _s3():
    return [
        {"type": "story", "heading": "3 · Install, workloads and .vsconfig",
         "html": (
             "<p><b>Visual Studio installs by workload, and a <code>.vsconfig</code> file makes a team's list of "
             "workloads a thing you commit instead of a wiki page.</b> The Installer groups components into "
             "workloads — <i>.NET desktop development</i> and <i>ASP.NET and web development</i> are the two this "
             "track needs — and lets you tick individual components on top. You export the selection to a "
             "<code>.vsconfig</code> JSON file from the Installer (More &gt; Export configuration), commit it, "
             "and from then on opening a solution whose root holds that file makes Visual Studio detect the "
             "missing components and offer to install them. The same file drives an unattended install: the "
             "edition bootstrapper with <code>--config</code> on a fresh machine, <code>setup.exe modify "
             "--config</code> on an existing one — <code>modify</code>, not <code>update</code>, which only "
             "refreshes components already installed (" + VSCONFIGDOC + ").</p>"
             "<p><b>The file has two arrays: <code>components</code> is required and may be empty, "
             "<code>extensions</code> is optional.</b> An extension must be a <code>.vsix</code>; only "
             "extensions hosted on the Visual Studio Marketplace trigger the automatic missing-component "
             "prompt, and a silent install needs <code>--allowUnsignedExtensions</code> for unsigned ones. "
             "The component IDs come from Microsoft's list (" + COMPIDS + "), which is labelled "
             "Visual Studio 2022 — export from your own installer to see the exact IDs it writes.</p>"
             "<p><b>Revisit lesson 01's SDK trap from this side: the IDE installs its own .NET SDK, and "
             "<code>global.json</code> is read from two different places.</b> Visual Studio installs a single "
             "copy of the SDK and, when you upgrade Visual Studio, removes the SDK version it installed "
             "before — even a different major — unless you install the stand-alone SDK, in which case Visual "
             "Studio no longer updates it. The <code>dotnet</code> muxer looks for <code>global.json</code> "
             "upward from the <i>current directory</i>; MSBuild's SDK resolver looks upward from the folder "
             "with the <i>solution file</i> (" + GLOBALJSON + "). So when a build passes in the IDE and <code>dotnet build</code> says “No .NET "
             "SDKs were found”, start where " + ref(1) + " does — the PATH — before you suspect the solution."
             "</p>")},

        pcode(sample(VSCONFIG, lang="json"), "3.1 · .vsconfig — the workloads this track needs",
              "<b>Nine IDs, one file, beside the solution.</b> Two workloads, the .NET SDK and its development "
              "tools, the C# and Visual Basic language services, NuGet, the diagnostic tools, IIS Express and "
              "Git. It contains no <code>extensions</code> array because nothing here needs one. "
              "Commit it at the folder that holds <code>L13.slnx</code>: that is the “solution root” Visual "
              "Studio checks (" + VSCONFIGDOC + ")."),

    ]


def _s4():
    return [
        {"type": "story", "heading": "4 · Solutions and projects in the IDE",
         "html": (
             "<p><b>Solution Explorer is a view of the solution file, and the modern solution file is a "
             "dozen lines of XML you can read.</b> Visual Studio reads both <code>.sln</code> and "
             "<code>.slnx</code> from 17.14 (" + SLNXVS + "), and since .NET 10 <code>dotnet new sln</code> "
             "writes <code>.slnx</code> by default (" + SLNXBREAK + "); " + ref(7) + " measures the difference. "
             "The Solution Items folder in <code>L13.slnx</code> below is a display grouping only.</p>"
             "<p><b>A big solution opens faster with a solution filter, which is a committed list of projects "
             "to load.</b> Choose Do not load projects, load the ones you need, and File &gt; Save Solution "
             "As Filter writes a <code>.slnf</code>; from a shell, <code>devenv /donotloadprojects "
             "MySln.sln</code> does the same. Right-click a project for Load Direct Dependencies or Load Entire "
             "Dependency Tree; a project added to the solution later appears as unloaded (" + FILTERS + "). "
             "It is an IDE convenience, not a build boundary: MSBuild still follows references, as "
             + ref(7) + " shows.</p>"
             "<p><b>C# and Visual Basic projects sit in one solution, share one build and one debugger.</b> "
             "The attribute that shapes how the debugger shows a value is the same in both languages; the "
             "type around it is not. Visual Basic has no <code>record struct</code>, so the same idea is a "
             "structure with two read-only properties and a constructor — the compare below is the whole "
             "difference.</p>")},

        pcompare(sample(f"{CS}/Domain.cs", "MoneyDisplay", file="Domain.cs · #region MoneyDisplay"),
                 sample(f"{VB}/Domain.vb", "MoneyDisplay", file="Domain.vb · #region MoneyDisplay"),
                 "4.1 · The same debugger attribute on a C# record struct and a VB structure",
                 "<b>One attribute, two type declarations.</b> <code>{Amount} {Currency,nq}</code> is evaluated "
                 "by the debugger; <code>,nq</code> removes the quotes around a string. Left: a "
                 "<code>readonly record struct</code> in six lines. Right: Visual Basic writes the properties "
                 "and the constructor out."),

        pcode(sample(SLNX), "4.2 · L13.slnx — the whole solution file",
              "<b>Solution folders and projects, nothing else.</b> <code>/Solution Items/</code> lists the three "
              "files Visual Studio and the test runner read; <code>/src/</code> and <code>/tests/</code> group "
              "the four projects, C# and Visual Basic side by side. There is no configuration matrix and no "
              "GUID — the build order comes from each project's own references."),

        {"type": "table", "heading": "4.3 · One job, three places — Solution Explorer, the NuGet manager, the CLI",
         "cols": ["Job", "In Visual Studio", "In a file or on the command line", "Source"],
         "rows": [
             ["<b>Open code</b>", "File &gt; Open &gt; Folder needs no solution or project file; a folder with "
              "a <code>.sln</code> must be opened as a solution; custom build tasks and launch parameters come "
              "from JSON files", "<code>dotnet build</code> takes a project, a solution or a file-based app",
              short(OPENFOLDER, "Open Folder docs") + " · " + short(DOTNETBUILD, "dotnet build docs")],
             ["<b>Add a package</b>", "Project &gt; Manage NuGet Packages: Browse, Installed and Updates tabs; "
              ".NET SDK-style projects require <code>PackageReference</code>",
              cmd("dotnet package add &lt;name&gt;") + " adds or updates a <code>PackageReference</code> in the "
              "project file (.NET 10 form; earlier SDKs: <code>dotnet add package</code>)",
              short(NUGETVS, "NuGet in VS docs") + " · " + short(DOTNETADD, "dotnet package add docs")],
             ["<b>One version list</b>", "nothing IDE-specific: it applies to all <code>PackageReference</code>-based MSBuild projects",
              "<code>Directory.Packages.props</code> with <code>ManagePackageVersionsCentrally</code> and "
              "<code>PackageVersion</code> items; projects then omit <code>Version</code>, as in " + ref(7),
              short(CPM, "Central Package Mgmt docs")]]},
    ]


def _s5():
    return [
        {"type": "story", "heading": "5 · The inner loop: debugging",
         "html": (
             "<p><b>F5 is three steps — build, start with a launch profile, attach the debugger — and only the "
             "second one is yours to configure.</b> The profiles live in <code>Properties/launchSettings.json</code>: "
             "the toolbar's run dropdown lists them, each with a <code>commandName</code> (<code>Project</code> "
             "for a normal process), arguments and environment variables. The file is used only on the local "
             "development machine and is not deployed when the app is published (" + ENVIRONMENTS + "). "
             "IntelliJ's run configurations are the closest thing you know, with one difference that matters "
             "here: this one is a plain file in the repository, and the CLI reads it too — "
             "<code>dotnet run -lp \"Show quote 137\"</code> starts the profile below.</p>"
             "<p><b>A breakpoint is a condition, and the conditions are the whole skill.</b> Right-click the "
             "red dot and choose Conditions: a conditional expression (break when it is true, or when its value "
             "changes), a hit count, or a filter on machine, process or thread. Add an action and it becomes a "
             "tracepoint — it writes to the Output window and does not stop. A dependent breakpoint stays "
             "disabled until another one has been hit (" + BREAKPOINTS + "). The sample's batch loop is built "
             "for this: 240 quotes, four of which are declined, and one loop body worth stopping in once.</p>"
             "<p><b>Then shape what the debugger shows.</b> <code>[DebuggerDisplay]</code> puts a one-line "
             "summary in the Locals window and in data tips; a <code>DebuggerTypeProxy</code> replaces the raw "
             "fields with a view you design; <code>[DebuggerStepThrough]</code> tells F11 to skip plumbing. "
             "None of them changes what the program does.</p>")},

        pcode(sample(LAUNCH), "5.1 · launchSettings.json — three profiles for one project", keep=True, note=
              "<b>Names are the interface.</b> The dropdown shows <code>Batch</code>, <code>Show quote 137</code> "
              "and <code>Show quote 47 (declined)</code>; <code>dotnet run -lp</code> takes the same names. The "
              "third profile shows where an environment variable goes; this program does not read it, so it "
              "changes nothing here. <code>dotnet run</code> without <code>-lp</code> uses the first profile, in "
              "file order, whose <code>commandName</code> it supports; a Visual Basic project keeps the file at "
              "<code>My Project/launchSettings.json</code> instead (" + DOTNETRUN + "). The two Show profiles start "
              "<code>Program.Show</code>, which prices one quote and returns before the batch loop — a breakpoint "
              "in <code>QuoteBatch.Run</code> hits only under <code>Batch</code>."),

        {"type": "mermaid", "inline": True, "heading": "5.2 · What one press of F5 does",
         "caption": "solid arrows = requests · dashed = results · steps 1–3 are the MSBuild step the CLI shares, "
                    "dotnet run -lp reads the same profile · steps 5–6 exist only because a debugger is attached",
         "code": ('%%{init: {"theme":"base","themeVariables": {"actorBkg":"#E0E7FF","actorBorder":"#4338CA",'
                  '"actorTextColor":"#1f2937","noteBkgColor":"#FEF3C7","noteBorderColor":"#D97706",'
                  '"noteTextColor":"#1f2937","signalColor":"#334155","signalTextColor":"#1f2937",'
                  '"sequenceNumberColor":"#ffffff"}}}%%\n'
                  "sequenceDiagram\n"
                  "  autonumber\n"
                  "  participant D as Developer\n"
                  "  participant V as Visual Studio\n"
                  "  participant B as MSBuild\n"
                  "  participant P as Your process\n"
                  "  D->>V: F5, Start Debugging\n"
                  "  V->>B: build the startup project\n"
                  "  B-->>V: assemblies and .pdb files\n"
                  "  Note over V: read the selected launch profile\n"
                  "  V->>P: start it with the profile's arguments and variables\n"
                  "  V->>P: attach the debugger, bind breakpoints through the .pdb\n"
                  "  Note over V,P: the source and symbols must match the running binary\n"
                  "  P-->>D: stops at a breakpoint, or runs to the end\n")},

        {"type": "html", "html": "", "_keep_with_next": True},
        {"type": "table", "heading": "5.3 · The breakpoint kinds, what each is for, and where this lesson's code uses it",
         "cols": ["Kind", "How you set it", "Use it when", "In the samples"],
         "rows": [
             ["<b>Conditional</b>", "right-click the breakpoint &gt; Conditions &gt; Conditional Expression "
              "(<i>Is true</i> or <i>When changed</i>); a <code>+</code> marks it",
              "one iteration of a loop is wrong", "<code>i == 137</code> in <code>QuoteBatch.Run</code>"],
             ["<b>Hit count</b>", "Conditions &gt; Hit Count", "the loop misbehaves after N passes",
              "138, the same quote (<code>i</code> starts at 0)"],
             ["<b>Filter</b>", "Conditions &gt; Filter: machine, process id or name, thread id or name",
              "only one process or thread matters", "not needed — the samples are single-threaded"],
             ["<b>Tracepoint</b>", "Actions: log a message to the Output window, do not stop",
              "you want a trace without editing code",
              "log <code>{i}</code> and <code>{request.Coverage}</code> on the marked line of 5.4"],
             ["<b>Dependent</b>", "Only enable when the following breakpoint is hit",
              "a common path matters only from one caller",
              "a stop in <code>Request</code> that waits for the loop stop"],
             ["<b>Temporary</b>", "Disable breakpoint once hit (VS 2026 wording)",
              "you want to stop once, then never again", "the throw in <code>ClaimsLoading</code>"],
             ["<b>Data</b>", "Autos, Watch or Locals &gt; right-click &gt; Break when value changes",
              "you need to know who changed a property",
              "<b>not</b> on <code>BatchResult</code> — a type with a <code>DebuggerTypeProxy</code> cannot "
              "host one"]]},
        {"type": "html", "html": (
            '<div class="lnote" style="margin:-4px 0 10px"><b>Source:</b> ' + BREAKPOINTS + ". The page also "
            "lists what a data breakpoint cannot watch — static variables, classes with the "
            "<code>DebuggerTypeProxy</code> attribute and fields inside structs — and the hardware limit of 4 "
            "on x64 and x86. In Visual Studio 2022 the temporary breakpoint reads “Remove breakpoint once hit”. "
            + VERIFIED + " " + VERIFIED_ON + ".</div>")},
    ]


def _s5b():
    return [
        pcode(sample(f"{CS}/Batch.cs", "BatchLoop"), "5.4 · A loop worth stopping in — 240 quotes, one of them is the question", keep=True, note=
              "<b>Aim, do not step.</b> A plain breakpoint on the marked line — the first inside the "
              "<code>try</code>, after <code>request</code> is assigned — stops 240 times. A conditional one with "
              "<code>i == 137</code>, or a hit count of 138 (the loop starts at 0), stops once with "
              "<code>request</code> already holding quote 137; the same line as a tracepoint logging "
              "<code>{i}</code> and <code>{request.Coverage}</code> traces the whole run without stopping. A "
              "breakpoint on <code>var request = Request(i);</code> itself would stop before the assignment. The "
              "<code>try/catch</code> matters for 5.6: the four declined quotes are caught here, so a plain run "
              "never shows them."),

        pcode(sample(f"{CS}/Batch.cs", "BatchResult"), "5.5 · DebuggerDisplay, a type proxy and a browsable view on one result", keep=True, note=
              "<b>Summary first, detail on demand.</b> <code>[DebuggerDisplay]</code> gives the one-line value; "
              "<code>DebuggerTypeProxy</code> swaps the expansion for <code>BatchResultView</code>, whose "
              "<code>RootHidden</code> array lists the declined indexes directly. Keep the braces to fields and "
              "properties: Microsoft warns that a general expression is evaluated every time the value is shown, "
              "by the evaluator of the frame's language, and can change program state — its recommended pattern "
              "is a private <code>DebuggerDisplay</code> property (" + DBGDISPLAY + ")."),

        pcode(sample(f"{CS}/Tariff.cs", "ClaimsLoading"), "5.6 · One exception setting finds the throw that a catch hides",
              "<b>Tick the type and the debugger stops at the <code>throw</code>, handled or not.</b> Open Debug "
              "&gt; Windows &gt; Exception Settings, add <code>L13.DebugLab.QuoteDeclinedException</code> and "
              "run: execution stops on the <code>_ =&gt; throw</code> arm, on quote 47, before the loop's "
              "<code>catch</code> sees it "
              "— a first-chance exception. The window does not check spelling, and the setting is kept per "
              "solution (" + EXCEPTIONS + ")."),

        {"type": "table", "heading": "5.7 · A window or a setting for each question",
         "cols": ["You ask", "Open or set", "What it does", "Source"],
         "rows": [
             ["Which quote is the first to decline?", "Exception Settings, tick the exception type",
              "Breaks where it is thrown, even when a <code>catch</code> handles it",
              short(EXCEPTIONS, "Exception docs")],
             ["Why does F11 skip a method?", "<code>[DebuggerStepThrough]</code> (on <code>Tariff.Satang</code>, "
              "in <code>Tariff.cs</code>, not printed); Just My Code",
              "Steps over non-user code; the Call Stack collapses it to <code>[External Code]</code>",
              short(JMC, "Just My Code docs")],
             ["What does this library do?", "Call Stack &gt; Show External Code, then double-click a frame",
              "Decompiles it (ILSpy-based, since 17.7) — C# only, and async code can come out incomplete",
              short(DECOMPILE, "Decompile docs")],
             ["Where is that library's source?", "a library built with Source Link and its symbols",
              "The debugger downloads the underlying source files as you step in; symbols can come from a "
              "symbol server such as NuGet.org's", short(SOURCELINK, "Source Link docs")],
             ["Which task is awaiting what?", "Debug &gt; Windows &gt; Tasks, or the Tasks view of Parallel Stacks",
              "Lists async/await tasks with status and parent — the tasks are those of " + ref(5)
              + "; no sample here runs async code", short(TASKSWIN, "Tasks window docs")],
             ["How do I keep a value in view?", "pin the data tip (the pushpin, Pin to source)",
              "Stays on the source line as you step; can carry comments and, for .NET Core 3.0 and later, pinned "
              "members; Debug &gt; Export DataTips saves them as XML", short(DATATIPS, "Data tips docs")]]},

        {"type": "html", "html": "", "_keep_with_next": True},
        {"type": "table", "heading": "5.8 · Hot Reload and Edit and Continue — the limits Microsoft documents",
         "cols": ["Kind", "What the page lists", "Source"],
         "rows": [
             ["<b>Not available</b>", "Release or custom build configurations, trimming, ReadyToRun, F#, "
              "mixed-mode debugging and optimized code", short(HOTRELOAD, "Hot Reload docs")],
             ["<b>Not available (Edit and Continue page)</b>", "dump debugging, and attaching to a process "
              "unless <code>COMPLUS_ForceENC=1</code> is set", short(SUPPORTED, "Supported code changes")],
             ["<b>Edits that need a restart, .NET 6+</b>", "modifying an interface; adding an abstract, virtual "
              "or override member; adding a destructor; changing a type parameter, base type or delegate type; "
              "deleting a type; an edit inside a catch or finally block that holds the active statement",
              short(ENCWIKI, "Roslyn supported edits")],
             ["<b>Edits that no longer need one</b>", "adding a <code>using</code> (VS 16.10); adding or changing "
              "an attribute and renaming a parameter (17.0); deleting members other than fields and namespace "
              "declarations (17.3); renaming members other than fields and changing parameter or return types "
              "(17.4)", short(ENCWIKI, "Roslyn supported edits")],
             ["<b>Visual Basic only</b>", "a member that contains <code>On Error</code> / <code>Resume</code>, "
              "or an <code>Aggregate</code>, <code>Group By</code>, simple <code>Join</code> or "
              "<code>Group Join</code> query clause, cannot be edited while the app runs — "
              "<code>QuoteCalculator.GrossTotal</code> in <code>L13.DebugLabVb</code> is one (not printed)",
              short(ENCWIKI, "Roslyn supported edits")]]},
        {"type": "html", "html": (
            '<div class="lnote" style="margin:-4px 0 10px"><b>Which list to follow:</b> the older table on '
            + SUPPORTED + " still lists renames, attributes and <code>using</code> as edits that cannot be "
            "applied; for .NET 6+ and Visual Studio 2022 and later that page points to the Roslyn list above, "
            "which this table follows. " + VERIFIED + " " + VERIFIED_ON + ".</div>")},

        {"type": "html", "html": "", "_keep_with_next": True},
        {"type": "table", "heading": "5.9 · Attaching to a process you did not start",
         "cols": ["Scenario", "Process", "Notes", "Source"],
         "rows": [
             ["Local app started without the debugger", "<code>appname.exe</code> · <code>iisexpress.exe</code>",
              "Debug &gt; Attach to Process, <code>Ctrl+Alt+P</code>; <code>Shift+Alt+P</code> reattaches",
              short(ATTACH, "Attach docs")],
             ["ASP.NET Core on IIS", "<code>w3wp.exe</code> or <code>dotnet.exe</code>",
              "in-process hosting uses <code>w3wp.exe</code> since .NET Core 3; the remote debugger must run on "
              "the server", short(ATTACH, "Attach docs")],
             ["A limited-user Visual Studio", "processes in Session 0, such as <code>w3wp.exe</code>",
              "not listed: run Visual Studio as an administrator, or use <code>vsjitdebugger.exe -p</code>",
              short(ATTACH, "Attach docs")]]},
    ]


def _s6():
    m = M["debuglab_cs"][1]
    return [
        {"type": "story", "heading": "6 · Testing in the IDE",
         "html": (
             "<p><b>Test Explorer is a live view of the tests the CLI would run — group it, filter it, and "
             "debug one test with a click.</b> Open it from Test &gt; Test Explorer (<code>Ctrl+E, T</code>); "
             "the default hierarchy is Project, Namespace, Class, and Group By adds Duration, State and Target "
             "Framework. A <code>[Trait(\"Category\", \"Tariff\")]</code> on an xUnit test appears under Group By &gt; "
             "Traits and in the Traits filter, and the same string reaches the CLI: <code>dotnet test --filter "
             "\"Category=Tariff\"</code> ran " + str(TRAITS["Tariff"]) + " of this lesson's " + str(M["tests"]["total"])
             + " tests (measured). Playlists save a hand-picked or rule-based list as a <code>.playlist</code> "
             "file you can commit (" + TESTEXPLORER + ").</p>"
             "<p><b>A <code>.runsettings</code> file is the test host's equivalent of a Gradle "
             "<code>tasks.test</code> block, and there are three ways to hand it over.</b> Visual Studio "
             "picks up a file named exactly <code>.runsettings</code> at the solution root when Test &gt; "
             "Configure Run Settings &gt; Auto Detect runsettings Files is on (look at your own Test menu — a "
             "correctly placed file is ignored when it is off); the same menu selects another file; and the "
             "<code>RunSettingsFilePath</code> MSBuild property in a project or <code>Directory.Build.props</code> "
             "makes <code>dotnet test</code> read the same file without depending on that switch and overrides "
             "the solution-level choice (" + RUNSETTINGSDOC + "). The file below "
             "sets test-host parallelism, a timeout, fails an empty run and sets two environment variables on "
             "the test host — and a test proves the variables arrived. One trap: "
             "<code>TestRunParameters</code> are documented for MSTest's and NUnit's <code>TestContext</code> "
             "only — the page describes no xUnit route — so this xUnit project uses environment variables.</p>"
             "<p><b>Coverage and Live Unit Testing are where the IDE and lesson 10's CLI gates differ.</b> "
             "Visual Studio counts coverage in <i>blocks</i> — a sequence of code with one entry and one exit "
             "— with lines as an optional column, so its percentage is not the line or branch percentage "
             + ref(10) + " gates on, and a threshold must name which one it means. Test &gt; Analyze Code "
             "Coverage for All Tests "
             "exports <code>.coverage</code>, XML or Cobertura (" + COVERAGE + "). Live Unit Testing reruns the "
             "tests your edit can affect as you type; its page says Enterprise only (" + LUT + "). And "
             "<code>xunit.v3.mtp-off</code> — the package " + ref(10) + " and this lesson's tests use — keeps the "
             "classic VSTest path instead of the Microsoft.Testing.Platform experience xUnit v3 projects get "
             "automatically (" + XUNITMTP + ").</p>")},

        pcode(sample(RUNSETTINGS, lang="xml"), "6.1 · .runsettings — one file, two readers",
              "<b>Named exactly <code>.runsettings</code>, beside the solution.</b> Visual Studio finds it by "
              "itself when Auto Detect runsettings Files is on; the test project's <code>RunSettingsFilePath</code> "
              "(next panel) makes <code>dotnet test</code> read the same file either way. "
              "<code>EnvironmentVariables</code> are set on the test host. Do not rely on a file in another "
              "folder being detected — only that exact name at the solution root is (" + RUNSETTINGSDOC + ")."),

        pcode(sample(f"{TESTS}/L13.DebugLab.Tests.csproj"), "6.2 · The test project — RunSettingsFilePath and the v3 packages",
              keep=False, note="<b>One property connects the two worlds.</b> <code>RunSettingsFilePath</code> points at "
              "<code>../.runsettings</code>; <code>Microsoft.NET.Test.Sdk</code> plus <code>xunit.v3.mtp-off</code> "
              "and <code>xunit.runner.visualstudio</code> keep the classic Test Explorer and "
              "<code>dotnet test</code> path, the same set " + ref(10) + " uses."),

        pcompare(from_text(
            '// build.gradle.kts\n'
            'tasks.test {\n'
            '    environment("L13_RUNSETTINGS", "applied")\n'
            '    environment("L13_BATCH_SIZE", "240")\n'
            '    maxParallelForks =\n'
            '        Runtime.getRuntime().availableProcessors()\n'
            '}\n'
            '\n'
            '// RunConfigTest.kt\n'
            '@Test\n'
            'fun `run configuration was applied`() {\n'
            '    assertEquals("applied",\n'
            '        System.getenv("L13_RUNSETTINGS"))\n'
            '    assertEquals("240",\n'
            '        System.getenv("L13_BATCH_SIZE"))\n'
            '}', "kotlin", file="build.gradle.kts + a JUnit test"),
                 sample(f"{TESTS}/RunSettingsTests.cs", "TestsRunSettings", file="RunSettingsTests.cs · TestsRunSettings"),
                 "6.3 · The same idea: test-run environment, in Gradle and in .runsettings",
                 "<b>Both hand the test process its environment before the first test runs — and both need a "
                 "test that proves it.</b> Gradle keeps that in the build script; .NET keeps it in a file both "
                 "Visual Studio and the CLI read. Without the assertion, a silently ignored settings file looks "
                 "like a passing run."),

        pcode(sample(f"{TESTS}/TariffTests.cs", "TestsWorkedExample"), "6.4 · A trait, and the worked example as a test",
              "<b>The trait is the Test Explorer group and the CLI filter at once.</b> The expected figures are the "
              "track's worked example (illustrative tariff, not a real one): Class 1, 550,000 THB, private use, "
              "a 23-year-old with 4 claim-free years. The program prints <code>" + esc(m) + "</code> and the "
              "test asserts the same four numbers."),

        {"type": "table", "heading": "6.5 · Test Explorer, the CLI and lesson 10's gates — the same tests, three doors",
         "cols": ["In Visual Studio", "On the command line", "Watch for"],
         "rows": [
             ["Group By &gt; Traits, or the Traits filter",
              cmd('dotnet test --filter "Category=Tariff"'),
              "Filter syntax is the framework's — the string is the same, the quoting differs by shell"],
             ["Run All (<code>Ctrl+R, V</code>)", cmd("dotnet test"),
              "Both must give " + str(M["tests"]["total"]) + " — a difference means settings or SDK differ (1.2)"],
             ["Test &gt; Configure Run Settings", "the <code>RunSettingsFilePath</code> property",
              "Autodetect needs the exact file name at the solution root and its option on"],
             ["Analyze Code Coverage for All Tests", "coverlet or Microsoft code coverage, as in " + ref(10),
              "Blocks in the IDE, line and branch in lesson 10 — never compare the percentages"],
             ["Live Unit Testing", "no equivalent used in this track",
              "Enterprise only on its own Learn page; the page for your version decides"]]},
        {"type": "html", "html": (
            '<div class="lnote" style="margin:-4px 0 10px"><b>Traits partition the suite: '
            f"{TRAITS['Tariff']} + {TRAITS['Batch']} + {TRAITS['Environment']} = {M['tests']['total']}.</b> "
            "The single Environment test fails if the settings file is not applied — the cheapest guard against "
            "a <code>.runsettings</code> that quietly stopped being read. " + MEASURED + " by "
            "<code>dotnet test --filter Category=…</code>.</div>")},
    ]


def _s7():
    return [
        {"type": "story", "heading": "7 · Code quality and AI assistance in the IDE",
         "html": (
             "<p><b>A rule lives in an <code>.editorconfig</code> line, and the editor and the compiler read "
             "the same line.</b> The severity decides what you see: <i>suggestion</i> is a quiet marker, "
             "<i>warning</i> and <i>error</i> are squiggles. Whether a squiggle also fails <code>dotnet build</code> "
             "depends on the rule: compiler warnings and analyzer packages always run at build, but an "
             "<code>IDE</code>-prefixed style rule is evaluated by the build only when "
             "<code>EnforceCodeStyleInBuild</code> is true (" + CODEANALYSIS + "); with the repository's "
             "<code>TreatWarningsAsErrors</code> the warning then fails it for everyone. The Options dialog "
             "is the trap: code-style settings there belong to your Visual Studio "
             "account, are not associated with a codebase and are not enforced at build or in CI — and a setting "
             "in an <code>.editorconfig</code> takes precedence over them (" + CODESTYLE + "). Analyzers, "
             "severities and <code>dotnet format</code> belong to " + ref(7) + "; this is what they look "
             "like from the editor.</p>"
             "<p><b>Code Cleanup applies the rules you already chose, on demand or on save.</b> "
             "<code>Ctrl+K, Ctrl+E</code> runs a configured cleanup profile — remove unused usings, apply "
             "<code>var</code> and brace preferences and more. A severity of <i>Refactoring Only</i> keeps a rule out of cleanup and "
             "leaves it as a Quick Action, and Options &gt; Text Editor &gt; Code Cleanup has a switch to run a "
             "profile on save. For the whole solution the CLI's <code>dotnet format</code> does the same job, as "
             + ref(7) + " shows — pin <code>end_of_line</code> first, or Windows and Linux disagree about what "
             "is clean.</p>"
             "<p><b>GitHub Copilot is part of the IDE workflow now, and Microsoft's pages describe it by "
             "GitHub plan, not by Visual Studio edition.</b> On the Visual Studio 2026 page, the Copilot badge "
             "opens the chat, and someone without a "
             "subscription can start on Copilot Free. Chat has Ask, Agent and Plan modes; built-in agents cover "
             "debugging, profiling, testing and modernization; and repository files such as "
             "<code>.github/copilot-instructions.md</code> carry your team's instructions — a file you review "
             "like code (" + COPILOT + " · " + COPILOTFREE + "). <b>Review what it writes as you would a colleague's pull request</b> — the gates "
             "in " + ref(10) + " and " + ref(7) + " apply to generated code exactly as to typed code.</p>")},

        pcode(sample(EDITORCFG, lang="text"), "7.1 · .editorconfig — the same severity in the editor and in the build",
              keep=True, note="<b>Two rules, two severities.</b> <code>file_scoped:warning</code> is a squiggle in the "
              "editor, and a build error only because of 7.3; the primary-constructor line is a "
              "<code>suggestion</code> — a marker with a Quick Action that never fails anything. "
              "<code>root = true</code> stops the search, so an <code>.editorconfig</code> higher up cannot "
              "change these rules."),

        {"type": "table", "heading": "7.2 · Where a style setting can live, and who sees it",
         "cols": ["Place", "Seen by", "Enforced at build", "Travels with the repository"],
         "rows": [
             ["Tools &gt; Options &gt; Text Editor &gt; Code Style", "you", "no", "no"],
             ["<code>.editorconfig</code>, an <code>IDE</code> style rule at warning or error",
              "everyone who opens the code", "only with <code>EnforceCodeStyleInBuild</code> (on in 7.3)", "yes"],
             ["<code>.editorconfig</code> with <i>suggestion</i> or <i>Refactoring Only</i>",
              "everyone in the editor", "no — it is a hint or a Quick Action", "yes"],
             ["A compiler warning, or a Roslyn analyzer package as in " + ref(7), "everyone",
              "yes, at the severity you set", "yes"]]},
        {"type": "html", "html": ('<div class="lnote" style="margin:-4px 0 10px"><b>Source:</b> ' + CODESTYLE
                                  + " · " + CODEANALYSIS + ". Since Visual Studio 2019 16.8 the .NET code-style "
                                  "rules can be enforced at build, and a handful of them still apply only in the IDE. " + VERIFIED + " "
                                  + VERIFIED_ON + ".</div>")},

        pcode(sample(f"{L}/Directory.Build.props", lang="xml"),
              "7.3 · Directory.Build.props — the switch that turns a style squiggle into a build error",
              keep=True, note="<b>Chain to the parent, then flip one property.</b> MSBuild imports only the nearest "
              "<code>Directory.Build.props</code>, so this file imports the repository's by hand, as in " + ref(7)
              + " §4.2, and adds <code>EnforceCodeStyleInBuild</code>. " + MEASURED + " by "
              "<code>capture.py</code>: a block-scoped namespace fails <code>dotnet build</code> with "
              f"<b>{M['style_probe']['with_enforce'].split()[-1]}</b>; with the property off "
              "(<code>-p:EnforceCodeStyleInBuild=false</code>) the same file builds."),
    ]


def _s8():
    floor = PERFM["pricing only (floor)"]["bytes"]
    names = ["LINQ + string.Format", "StringBuilder", "StringBuilder, pre-sized"]
    above = [(n, PERFM[n]["bytes"] - floor) for n in names]
    calls = [(n, PERFM[n]["calls"]) for n in ["pricing only (floor)"] + names]
    heavy, presized = above[0][1], above[2][1]
    return [
        {"type": "story", "heading": "8 · Performance and diagnostics",
         "html": (
             "<p><b>Visual Studio has two performance tools, and the difference is whether you are already "
             "debugging.</b> The Diagnostic Tools window (<code>Ctrl+Alt+F2</code>) opens during a debug session "
             "with CPU, memory and .NET counter graphs and PerfTips on the source lines. The Performance "
             "Profiler (Debug &gt; Performance Profiler, <code>Alt+F2</code>) is aimed at Release builds and "
             "offers tools for .NET — CPU Usage, .NET Object Allocation, Memory Usage, Instrumentation (exact "
             "call counts), .NET Async, File I/O, .NET Counters, Database and GPU; in Visual Studio 2026 they "
             "are grouped into Flexible and Standalone tabs, with a Copilot “Recommended” tab in front. IntelliTrace "
             "events in the Diagnostic Tools are an Enterprise feature (" + PROFILING + ").</p>"
             "<p><b>Every tool has a command-line sibling, and you will need it on a server without an IDE.</b> "
             "<code>dotnet-counters</code>, <code>dotnet-trace</code>, <code>dotnet-dump</code>, "
             "<code>dotnet-stack</code> and <code>dotnet-monitor</code> are Microsoft's cross-platform "
             "diagnostics tools (" + DIAGTOOLS + "); Visual Studio's profiler can open a trace that "
             "<code>dotnet-trace</code> collected, which is the workflow for a problem that only shows in "
             "production. You know the shape from the JVM: a JFR recording collected on the server, opened in "
             "JDK Mission Control on your desk.</p>"
             "<p><b>This lesson prints only figures a script can reproduce: allocated bytes and call counts, "
             "never wall-clock time.</b> <code>L13.PerfLab</code> builds one report three ways and reads "
             "<code>GC.GetAllocatedBytesForCurrentThread</code> around each; the same code on the same runtime "
             "and configuration allocates the same number of bytes, so the Release table below is identical on "
             "every run (the capture script asserts it). The configuration matters: a Debug build of the same "
             f"program prints other absolute figures (floor {PERFD['pricing only (floor)']['bytes']:,}, LINQ + "
             f"string.Format {PERFD['LINQ + string.Format']['bytes']:,} bytes), so every figure here names "
             "<code>-c Release</code>. A timing from this box would differ on yours, so none is printed — use "
             "the profiler for that, on your own hardware.</p>")},

        pcode(sample(f"{PERF}/Program.cs", "Measure"), "8.1 · Measuring bytes, not time",
              "<b>Warm up, count, run once, subtract.</b> The first call pays static-setup costs, so it is thrown "
              "away and the counter is reset after it; <code>Report.PriceCalls</code> therefore counts one "
              "measured pass, which is not what a profiler over the whole run would total; the delta of "
              "<code>GetAllocatedBytesForCurrentThread</code> is the report's allocation. Figures: "
              "<code>dotnet run -c Release</code>."),
        pcode(sample(f"{PERF}/Report.cs", "HeavyVersion"), "8.2 · The allocation-heavy version",
              "<b>One LINQ expression, four kinds of garbage — and two <code>Price</code> calls per row.</b> "
              "The <code>Select</code> lambda is a closure, <code>string.Format</code> boxes its four arguments "
              "and builds a string per line, <code>ToList</code> keeps them all, and <code>Join</code> copies "
              "them again. Both versions return the same text, byte for byte; the program checks it and exits "
              "non-zero if not."),

        pcode(sample(f"{PERF}/Report.cs", "PresizedVersion"), "8.3 · The allocation-light version",
              "<b>Price once, reuse the enum names, reserve the buffer.</b> Compare with 8.2: no closure, no "
              "boxing, no per-line string, one <code>StringBuilder</code> sized up front, one <code>Price</code> "
              "call per quote."),

        {"type": "chartrow", "charts": [
            {"heading": "8.4 · Bytes the report allocates above pricing alone (Release)", "kind": "hbar",
             "args": {"data": above, "tone": "indigo", "width": 390, "labelw": 150},
             "caption": f"Release build · allocated bytes minus the {floor:,}-byte pricing floor · the same "
                        f"{int(re.search(r'[(](\d+) characters', M['perflab_raw'][-1]).group(1)):,}-character "
                        "report each time · measured",
             "note": f"<b>In a Release build the heavy report allocates {heavy:,} bytes above the floor; "
                     f"the pre-sized one {presized:,} — {heavy / presized:.1f} times less.</b> " + MEASURED
                     + " by <code>samples/tools/capture.py</code>; a Debug build gives other figures, so the "
                     "ratio is tied to Release."},
            {"heading": "8.5 · Calls to Price in one measured pass", "kind": "hbar",
             "args": {"data": calls, "tone": "amber", "width": 390, "labelw": 150},
             "caption": "the sample's own counter, one measured pass (reset after the warm-up) · 236 quotes are priced",
             "note": "<b>The heavy version calls <code>Price</code> twice per quote — 472 calls for 236 "
                     "quotes.</b> Some of its extra allocation is duplicated work, not formatting, which a bytes "
                     "table alone would hide. " + MEASURED + " The profiler was not run: over the whole program its "
                     "totals would include the warm-up pass — 472 for a single-pass version, 944 for "
                     "<code>Report.Heavy</code> " + ESTIMATE + "."}]},
    ]


def _map():
    return mapping("1.4 · Concept map — IntelliJ, Android Studio and VS Code habits to Visual Studio", [
        ("A Run/Debug Configuration", "a profile in <code>launchSettings.json</code>", "renamed",
         "A file in the repository, and <code>dotnet run -lp</code> reads it too (5.1)"),
        ("Gradle <code>tasks.test { environment(…) }</code>", "<code>.runsettings</code> "
         "<code>EnvironmentVariables</code>", "renamed", "Autodetected only under that exact name at the solution "
                                                         "root (6.1)"),
        ("An IDE code-style scheme and inspection profile", "<code>.editorconfig</code> severities and analyzers",
         "different", "Tools &gt; Options belongs to your account and is not enforced at build (7.2)"),
        ("A breakpoint condition, “Evaluate and log”", "a conditional breakpoint, a tracepoint", "same",
         "Conditions, hit count, filter, dependent, temporary — all in one dialog (5.3)"),
        ("<code>toString()</code> shown in the debugger", "<code>[DebuggerDisplay]</code>, "
         "<code>DebuggerTypeProxy</code>", "renamed", "Attributes in code; DebuggerDisplay wins over an "
                                                        "overridden <code>ToString()</code> (5.5)"),
        ("HotSwap in a debug session", "Hot Reload and Edit and Continue", "different",
         "A documented list of edits and build modes that do not apply (5.8)"),
        ("A shared plugin list", "<code>.vsconfig</code>: workloads, components, extensions", "different",
         "It installs components of the IDE itself, not only plugins (3.1)"),
        ("Attach to a remote JVM", "Attach to Process — <code>w3wp.exe</code>, <code>dotnet.exe</code>", "same",
         "Source and symbols must match the running binary (5.9)"),
        ("Run with Coverage", "Analyze Code Coverage for All Tests", "trap",
         "Counts blocks, not lines; its edition gating changed between releases (2.3, 6.5)"),
    ])


def _s9():
    return [
        {"type": "story", "heading": "9 · Legacy estates in the IDE",
         "html": (
             "<p><b>The IDE is where a legacy estate stops being abstract: you open the old solution, build it "
             "with the MSBuild you already know, and debug what runs.</b> Two facts from Microsoft's pages "
             "explain the parts that surprise people. The WinForms designer for .NET runs out of process, in "
             "a <code>DesignToolsServer.exe</code> beside <code>devenv.exe</code> on the same .NET version and "
             "platform as your app — Visual Studio itself is a .NET Framework application, so the designer for a "
             "modern .NET form has to live outside it (" + WINFORMS + "). And for a site "
             "already running on IIS you do not run it from the IDE: you attach to <code>w3wp.exe</code>, "
             "with Visual Studio elevated so the worker process is listed (" + ATTACH + ").</p>"
             "<p><b>What the IDE does not do here is decide how to migrate.</b> " + Ref(6) + " teaches the "
             "VB and WinForms code you will meet and " + ref(12) + " owns the modernization tooling; this "
             "lesson only notes that they all run inside the same solution, the same MSBuild and the same "
             "debugger. Two limits are worth knowing before you promise anything: decompilation generates C# "
             "only — never Visual Basic — and can be incomplete for async code (" + DECOMPILE + "). The WPF "
             "designer is <b>not</b> covered: this lesson verified the WinForms designer page only, so read "
             "the WPF one before you rely on it.</p>"
             "<p><b>Not covered here, and why:</b> IIS Express versus a full IIS site and the <code>web.config</code> "
             "settings a legacy site adds are not compared — this lesson read only the attach-to-process page, "
             "which does not compare them; a preview Visual Studio channel appears only as the Insiders channel "
             "named in 2.2.</p>")},
    ]


def _s10():
    return [
        {"type": "story", "heading": "10 · Other editors — VS Code with the C# Dev Kit, and Rider",
         "html": (
             "<p><b>Two other tools are worth knowing, and the licence condition is what most often decides "
             "between them.</b> The C# Dev Kit is Microsoft's extension for VS Code: free for personal, academic "
             "and open-source projects, and free for commercial use by teams of up to five; for six or more, its "
             "FAQ says a Visual Studio Professional or higher subscription is needed, and the get-started page says "
             "you sign in to a Visual Studio subscription to use it. The source of the base C# extension is "
             "MIT-licensed; read its terms for the shipped build (" + DEVKITFAQ + " · " + DEVKIT + "). JetBrains "
             "Rider is free for non-commercial use; JetBrains publishes the commercial terms (" + RIDER + "). Read "
             "the page on the day you buy — terms change.</p>"
             "<p><b>For a JVM developer the honest choice is about habits and estate, not features.</b> The "
             "right-hand column below is the author's judgement, labelled as such: it is not a benchmark and "
             "no vendor page says it.</p>")},

        {"type": "table", "heading": "10.1 · A decision table — vendor facts verified, the last column is an ESTIMATE",
         "cols": ["Tool", "What the vendor page states (verified " + VERIFIED_ON + ")", "Source",
                  "Choose it when (judgement)"],
         "rows": [
             ["<b>Visual Studio Community</b>", "the full IDE, free for individuals, classroom, academic, open "
              "source and non-enterprise organisations up to 5 users", short(COMPARE, "Editions page"),
              "you qualify and want the full debugger and designers"],
             ["<b>Visual Studio Professional</b>", "the paid team edition; LTSC servicing channels", 
              short(COMPARE, "Editions page"),
              "the team works on legacy WinForms/IIS/VB estates or needs LTSC servicing"],
             ["<b>VS Code + C# Dev Kit</b>", "free for personal, academic, open source, and commercial teams of "
              "up to 5; larger commercial teams need a Visual Studio Professional or higher subscription; "
              "creates and runs projects with <code>.NET: New Project</code>; sign-in to a Visual Studio "
              "subscription required", short(DEVKITFAQ, "Dev Kit FAQ") + " · " + short(DEVKIT, "C# in VS Code"),
              "you work in TypeScript and Python too and want one light editor for services"],
             ["<b>JetBrains Rider</b>", "free for non-commercial use; a cross-platform .NET IDE whose page lists "
              "inspections, debugging, unit testing, NuGet and version control, and ASP.NET, Blazor, MAUI, WPF "
              "and WinForms among its technologies", short(RIDER, "Rider page"),
              "you want the IntelliJ family's habits and your licence terms allow it"]]},
    ]


def _s11():
    cfg = _configs()
    cs, show137, show47 = M["debuglab_cs"], M["launch_profile_137"][1:], M["show_47"]
    declined = cs[3].split(": ", 1)[1]
    gross = cs[4].split(": ", 1)[1]
    q137 = show137[2].split(": ", 1)[1] + " → " + show137[3].split(": ", 1)[1]
    term = ('$ dotnet run --project samples/L13.DebugLab -lp "Show quote 137"\n' + "\n".join(show137)
            + "\n\n$ dotnet run --project samples/L13.DebugLab\n" + "\n".join(cs[2:])
            + "\n\n$ dotnet run --project samples/L13.DebugLab -- --show 47\n" + show47[2])
    return [
        {"type": "story", "heading": "11 · Hands-on — a guided debug session over a correct program",
         "html": (
             "<p><b>The best way to learn a debugger is to ask it questions whose answers you can check.</b> "
             "<code>L13.DebugLab</code> prices 240 generated quotes with the track's illustrative tariff; four are "
             "declined, and every test passes. Nothing is broken: each question below is answered by one IDE "
             "feature, and the CLI column reaches the same answer without an IDE, so you can tell whether the "
             "feature or your reading is at fault. The IDE steps below were not run — there is no Visual Studio on the build machine (" + ESTIMATE
             + ") — while the CLI column and its answers were run.</p>"
             "<ol><li>Open <code>samples/L13.slnx</code> in Visual Studio; the <code>.vsconfig</code> offers any "
             "missing workload.</li>"
             "<li>Make <code>L13.DebugLab</code> the startup project and pick the profile named in the row from "
             "the run dropdown — <code>Batch</code> for questions 1–4. The two Show profiles skip the batch "
             "loop, so a breakpoint in <code>QuoteBatch.Run</code> never hits there.</li>"
             "<li>Set the exception setting or breakpoint the row names, press F5, and read the value where "
             "the row says.</li>"
             "<li>Compare it with the answer. If they differ, run the CLI column: its output is the "
             "reference.</li></ol>")},

        {"type": "table", "heading": "11.1 · Five questions, the IDE feature that answers each, and the answer",
         "cols": ["Question", "In Visual Studio", "Without it", "The answer (measured)"],
         "rows": [
             ["1 · Which quote declines first?", "profile <code>Batch</code> · Exception Settings: tick "
              "<code>QuoteDeclinedException</code>, F5; double-click the <code>QuoteBatch.Run</code> frame in the "
              "Call Stack, read <code>i</code> in Locals", cmd("dotnet run … -- --show 47"),
              f"index 47 — the four are {declined}"],
             ["2 · What does quote 137 price to?", "profile <code>Batch</code> · a conditional breakpoint "
              "<code>i == 137</code> (or hit count 138) on the marked line of 5.4; read <code>request</code> in "
              "a data tip", cmd('dotnet run … -lp "Show quote 137"'), esc(q137)],
             ["3 · Where is that exception thrown?", "profile <code>Batch</code> · the same Exception Settings "
              "stop; read the top frame of the Call Stack",
              "the message names the throwing method", "<code>Tariff.ClaimsLoading</code>, the "
              "<code>_ =&gt; throw</code> arm"],
             ["4 · What is the total after the loop?", "profile <code>Batch</code> · a breakpoint on the line "
              "after <code>QuoteBatch.Run</code> in <code>Program.cs</code>; read <code>Summary</code> in the "
              "type proxy view of <code>result</code>", cmd("dotnet run …"), gross],
             ["5 · Which report prices twice?", ESTIMATE + " Performance Profiler &gt; Instrumentation on "
              "<code>L13.PerfLab</code>, a Release build", cmd("dotnet run -c Release --project …L13.PerfLab"),
              "<code>LINQ + string.Format</code> — " + str(PERFM["LINQ + string.Format"]["calls"]) + " calls for "
              + str(PERFM["pricing only (floor)"]["calls"]) + " quotes (Release run)"]]},

        pcode(from_text(term, "shell", label="Terminal — captured from a real run",
                        file="output of samples/tools/capture.py · path line omitted · header lines shown once"),
              "11.2 · The same answers from the command line", keep=False, note=
              "<b>Both routes must agree.</b> <code>dotnet run -lp</code> prints one extra first line naming the "
              "launch-settings file it used, and every run prints the same two header lines; both are omitted after "
              "the first run here. The figures are the tariff's own: the "
              "worked example prices to 8,933.71 THB — net 8,316.00, stamp duty 33.26, VAT 584.45 — and the "
              "four declined indexes are the ones the tests assert. " + MEASURED + "."),

        {"type": "table", "heading": "11.3 · The files Visual Studio reads in this lesson, and who else reads them",
         "cols": ["File", "Read by", "Controls", "Section"],
         "rows": [
             ["<code>L13.slnx</code>", "Visual Studio 17.14+, the .NET CLI", "the project list and solution folders",
              "4.2"],
             ["<code>.vsconfig</code>", "the Installer, and Visual Studio when the solution opens",
              "which components are installed", "3.1"],
             ["<code>global.json</code>", "the <code>dotnet</code> muxer and MSBuild's SDK resolver", "which SDK "
              "builds, per " + ref(1), "3"],
             ["<code>Directory.Build.props</code>", "MSBuild — IDE and CLI alike",
              "target framework, nullable, warnings as errors, and in the samples <code>EnforceCodeStyleInBuild</code>; "
              "see " + ref(7), "7.3"],
             ["<code>.editorconfig</code>", "the editor, the compiler, <code>dotnet format</code>",
              "style and analyzer severities", "7.1"],
             ["<code>.runsettings</code>", "Test Explorer (with Auto Detect on); <code>dotnet test</code> via a "
              "property", "test-host environment and limits", "6.1"],
             ["<code>launchSettings.json</code>", "the F5 dropdown, <code>dotnet run -lp</code>",
              "start-up profiles", "5.1"],
             ["<code>Directory.Build.rsp</code>, <code>Directory.Solution.props</code> / <code>.targets</code>",
              "the command line only: the response file, and MSBuild's solution build (" + RSPDOC + "; " + ref(7)
              + " §4.5)", "default switches and solution-level steps — the IDE ignores them", "1.2"]]},

        {"type": "chart", "heading": "11.4 · Every file that configures the IDE or the build, by size",
         "kind": "hbar",
         "args": {"data": sorted(cfg, key=lambda r: -r[1]), "tone": "indigo", "width": 560, "labelw": 170},
         "caption": "lines per file · the samples' own settings files and the repository root's global.json and "
                    "Directory.Build.props · measured from disk at build time",
         "note": f"<b>{len(cfg)} small files carry the whole setup; none is longer than "
                 f"{max(n for _, n in cfg)} lines</b> — short enough to live in the repository, where a "
                 "colleague and CI read it too. " + MEASURED + " from disk by <code>capture.py</code>."},

        figure_heading("11.5 · What to carry over, learn fresh and unlearn"),
        {"type": "threecol", "boxes": [
            {"heading": "Carries over unchanged", "tone": "teal",
             "items": ["Run configurations as named, shareable profiles",
                       "Conditions and actions on breakpoints",
                       "A rule file that travels with the repository",
                       "Attach to a process — and match its symbols",
                       "Selecting tests by tag from the IDE and the CLI"]},
            {"heading": "Learn fresh", "tone": "indigo",
             "items": ["Exception Settings and the first-chance stop",
                       "<code>[DebuggerDisplay]</code> and a type proxy",
                       "<code>.runsettings</code> and <code>RunSettingsFilePath</code>",
                       "Just My Code and <code>[External Code]</code>",
                       "<code>.vsconfig</code> in the solution root"]},
            {"heading": "Unlearn", "tone": "rose",
             "items": ["“The Options dialog holds team settings”",
                       "“Coverage needs Enterprise” — check the page for your version",
                       "“Hot Reload works in Release builds”",
                       "“The IDE builds differently from the CLI” — only a workload, an SDK or a command-line-only file does",
                       "“A profiler timing from my laptop is a benchmark”"]}]},
    ]


DOCS_HOME = link("Visual Studio documentation", "https://learn.microsoft.com/en-us/visualstudio/")


def blocks():
    n_tests = M["tests"]["total"]
    n_proj = len(_projects())
    return [
        style_block(),
        {"type": "toc", "heading": "▤ Contents", "depth": 2,
         "note": "Page numbers are resolved from the rendered PDF. Code panels (numbered N.M in the text) are "
                 "not listed here; they are cut from the compiled "
                 f"samples; every claim about Visual Studio was read on an official page on {VERIFIED_ON} and is "
                 "linked beside it."},
        {"type": "html", "html": "<style>.callout .ct, .story .ct { break-after:avoid; page-break-after:avoid; } "
                                 ".callout li:first-child, .story .ct + p "
                                 "{ break-before:avoid; page-break-before:avoid; } "
                                 "a.lnk { word-break:normal; overflow-wrap:break-word; } "
                                 '.mmd svg[aria-roledescription="flowchart-v2"] { max-height:3.2in; }</style>'},
        *_s1(), _map(), *_s2(), *_s3(), *_s4(), *_s5(), *_s5b(), *_s6(), *_s7(), *_s8(), *_s9(), *_s10(), *_s11(),

        {"type": "callout", "variant": "warn", "heading": "⚠ Traps",
         "items": [
             "<b>The Options dialog looks like team configuration and is not.</b> Code-style settings there "
             "belong to your Visual Studio account and are not enforced at build or in CI; an "
             "<code>.editorconfig</code> is the file that travels, and it wins over the dialog — but an "
             "<code>IDE</code> style rule in it fails <code>dotnet build</code> only when "
             "<code>EnforceCodeStyleInBuild</code> is on (" + CODESTYLE + ").",
             "<b>“Coverage needs Enterprise” is out of date — and two Microsoft pages still disagree.</b> "
             "The coverage page says Enterprise, Community and Professional in Visual Studio 2026; the Test "
             "Explorer page still says Enterprise in one sentence; Live Unit Testing, Fakes and IntelliTrace "
             "events are still Enterprise (" + COVERAGE + " · " + TESTEXPLORER + " · " + LUT + "). Read the page "
             "for your version, and confirm in your own Test menu.",
             "<b>A <code>.runsettings</code> is autodetected only under that exact name at the solution "
             "root, and only while Auto Detect runsettings Files is on</b> — and <code>TestRunParameters</code> are documented only for MSTest and NUnit, so an xUnit "
             "project reads environment variables instead (" + RUNSETTINGSDOC + ").",
             "<b>Hot Reload is a debug-session feature with a published list of limits — and the list "
             "is shorter than older pages say.</b> Release and optimized builds, attaching without "
             "<code>COMPLUS_ForceENC=1</code>, edits to interfaces, new abstract, virtual or override members, "
             "destructors, deleted types and, in Visual Basic, members with <code>Aggregate</code> or "
             "<code>On Error</code> end in a restart; renames, signature changes, attributes and a new "
             "<code>using</code> are supported in current Visual Studio, although the older table on the "
             "supported-code-changes page still lists them (" + HOTRELOAD + " · " + ENCWIKI + ").",
             "<b>Upgrading Visual Studio removes the .NET SDK it installed earlier</b> — even a different major "
             "— and a stand-alone SDK you install to avoid that is no longer updated by Visual Studio "
             "(" + GLOBALJSON + "). Decompiled code is never the original: C# only, and async can be "
             "incomplete (" + DECOMPILE + ")."]},

        {"type": "callout", "variant": "ok", "heading": "✔ Checkpoint — you can work in Visual Studio when",
         "items": [
             f"<code>python 0-script/verify_samples.py --only 13</code> reports {n_proj}/{n_proj} passed, and "
             f"<code>samples/tools/capture.py</code> reproduces the {n_tests} tests, the four declined indexes "
             "and the Release allocation table on your machine.",
             "You can explain why Build-in-Visual-Studio and <code>dotnet build</code> agree, and name what "
             "legitimately makes them differ: a workload, an SDK, and the two command-line-only files "
             "(<code>Directory.Build.rsp</code>, <code>Directory.Solution.props</code> / <code>.targets</code>).",
             "You can pick an edition from the published licence rules and say which gated features you "
             "checked on which page — and which page you would trust if two disagree.",
             "Given a loop that catches an exception, you can find the first throw and the 137th iteration "
             "without adding a line of code, and reach the same answers from the CLI."]},

        {"type": "callout", "variant": "summary", "heading": "🔍 Check yourself", "_keep_with_next": True,
         "items": [
             "A build passes in Visual Studio but <code>dotnet build</code> says “No .NET SDKs were found”. "
             "Which environment variable do you check first, and where does the IDE's own SDK come from?",
             "Which kind of organisation is excluded from Community, and which features does this lesson list "
             "as still Enterprise-only? Which page do you trust when two Microsoft pages disagree?",
             f"<code>dotnet test --filter \"Category=Tariff\"</code> ran {TRAITS['Tariff']} tests. Which Test "
             "Explorer control selects the same set, and which attribute makes both work?",
             "Give two breakpoint settings that stop on quote 137 of 240 with no code change, and the one "
             "setting that stops on each of the four declined quotes.",
             "Why does the pre-sized report allocate less than the heavy one, and why would a profiler over "
             "the whole program total more <code>Price</code> calls than the sample's own counter?",
             "Your <code>.runsettings</code> is in a folder called <code>settings</code> and Test Explorer "
             "ignores it. Why — and which property makes <code>dotnet test</code> read it anyway?",
             "A colleague edits a Visual Basic member that contains <code>Aggregate</code> while debugging and "
             "Hot Reload refuses. What do you do, and which page lists the limit?"]},

        {"type": "footer",
         "html": ("<b>Lesson 13 in one line:</b> Visual Studio is a front end to files you commit — "
                  "<code>.slnx</code>, <code>.vsconfig</code>, <code>.editorconfig</code>, "
                  "<code>.runsettings</code>, <code>launchSettings.json</code> — so the IDE and the CLI reach the "
                  "same build and the same tests; its own strengths are the debugger you can aim, Test Explorer "
                  "and the profiler, and every claim about editions and gating is one you check on Microsoft's "
                  f"page the day you decide (read {VERIFIED_ON})."
                  "<br/><b>Back to the track:</b> " + ref(7) + " for the files, " + ref(10) + " for the gates "
                  "these tools reach, and the official " + DOCS_HOME + " for everything newer than this PDF.")},
    ]

