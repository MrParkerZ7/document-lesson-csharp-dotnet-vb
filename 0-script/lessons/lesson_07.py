# -*- coding: utf-8 -*-
"""Lesson 07 — Solutions, MSBuild & Mono-repos. Built to 1-analysis/spec_lesson-pdfs/_standard.md;
unit spec 1-analysis/spec_lesson-pdfs/lesson-07-solutions-monorepo-build.md."""
import json
import re
import textwrap

from lesson_kit import (DIFFERENT, ESTIMATE, MEASURED, RENAMED, REPO, SAME, TRAP, VERIFIED, T_TOOLING, code,
                        compare, esc, from_sample, from_text, legend, link, loc, mapping, pill, style_block)
from lessons.roster import meta, ref

META = meta(
    7,
    subtitle="One solution, many projects — MSBuild evaluation, Directory.Build.* inheritance, central "
             "package management, a build graph whose cost you can predict, and one CI workflow for the repo",
    objectives=[
        "Read a .NET mono-repo's build: name what each Directory.* file contributes, when it is imported and "
        "which one wins",
        "Map Gradle, Maven and Lerna vocabulary onto MSBuild properties, items and targets, and inspect any "
        "build with -pp, -getProperty, -t: and -bl",
        "Own package versions centrally, pin transitive versions, and make CI fail when a lock file drifts",
        "Predict which projects recompile after an edit, and explain why an internal change sometimes "
        "recompiles the whole repository",
        "Gate the repo with analyzers, .editorconfig and dotnet format, then pack and push every module from "
        "one GitHub Actions workflow",
        "Keep C# and Visual Basic projects in one solution, one build graph and one set of packages",
    ],
    maps_from="Kotlin Gradle-DSL mono-repos of 50–120+ modules with convention plugins and version catalogs, "
              "Maven multi-module reactors, a Lerna TypeScript workspace, a Python mono-repo of 100–300+ "
              "modules with a custom packager, and the GitHub Actions pipelines you already run.",
)

L = "lesson-07-solutions-monorepo-build/samples"
MONO = f"{L}/MotorMono"
SLNX = f"{MONO}/MotorMono.slnx"
SLNF_FILE = f"{MONO}/MotorMono.Pricing.slnf"
DBP = f"{MONO}/Directory.Build.props"
ROOT_DBP = "Directory.Build.props"
DBT = f"{MONO}/Directory.Build.targets"
DPP = f"{MONO}/Directory.Packages.props"
EDITORCFG = f"{MONO}/.editorconfig"
PRICING_PROJ = f"{MONO}/src/L07.Pricing/L07.Pricing.csproj"
INTERNALS = f"{MONO}/src/L07.Pricing/Internals.cs"
NCB_CS = f"{MONO}/src/L07.Pricing/NoClaimBonus.cs"
NCB_VB = f"{MONO}/src/L07.Pricing.Vb/NoClaimBonusVb.vb"
TESTS_PROJ = f"{MONO}/tests/L07.Pricing.Tests/L07.Pricing.Tests.csproj"
CLI_CS = f"{MONO}/src/L07.QuoteCli/Program.cs"
CI_YML = f"{L}/ci/build.yml"

# ── official sources ─────────────────────────────────────────────────────────────────────────
BYDIR = link("Customize the build by folder",
             "https://learn.microsoft.com/en-us/visualstudio/msbuild/customize-by-directory")
BUILDPROC = link("How MSBuild builds projects",
                 "https://learn.microsoft.com/en-us/visualstudio/msbuild/build-process-overview")
SLNXBREAK = link("dotnet new sln defaults to SLNX",
                 "https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/10.0/dotnet-new-sln-slnx-default")
SLNXCLI = link("SLNX support in the .NET CLI",
               "https://devblogs.microsoft.com/dotnet/introducing-slnx-support-dotnet-cli/")
SLNXVS = link("the simpler solution file format",
              "https://devblogs.microsoft.com/visualstudio/new-simpler-solution-file-format/")
FILTERS = link("Solution filters in MSBuild",
               "https://learn.microsoft.com/en-us/visualstudio/msbuild/solution-filters")
CPM = link("Central Package Management",
           "https://learn.microsoft.com/en-us/nuget/consume-packages/central-package-management")
LOCKFILE = link("locking dependencies",
                "https://learn.microsoft.com/en-us/nuget/consume-packages/package-references-in-project-files"
                "#locking-dependencies")
AUDIT10 = link("restore audits transitive packages",
               "https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/10.0/nugetaudit-transitive-packages")
PRUNING = link("NuGet package pruning in .NET 10",
               "https://devblogs.microsoft.com/dotnet/nuget-package-pruning-in-dotnet-10/")
SRCMAP = link("package source mapping",
              "https://learn.microsoft.com/en-us/nuget/consume-packages/package-source-mapping")
ARTIFACTS = link("artifacts output layout", "https://learn.microsoft.com/en-us/dotnet/core/sdk/artifacts-output")
REFASM = link("reference assemblies",
              "https://learn.microsoft.com/en-us/dotnet/standard/assembly/reference-assemblies")
REFOUT = link("the Roslyn refout notes",
              "https://github.com/dotnet/roslyn/blob/main/docs/features/refout.md")
CODEANALYSIS = link("code analysis in .NET",
                    "https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/overview")
FORMAT = link("dotnet format", "https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-format")
IDE0161 = link("IDE0161",
               "https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/style-rules/ide0161")
PACK = link("dotnet pack", "https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-pack")
BINLOG = link("the MSBuild binary log",
              "https://github.com/dotnet/msbuild/blob/main/documentation/wiki/Binary-Log.md")
RSPDOC = link("MSBuild response files",
              "https://learn.microsoft.com/en-us/visualstudio/msbuild/msbuild-response-files")
SETUPDOTNET = link("actions/setup-dotnet", "https://github.com/actions/setup-dotnet/blob/main/README.md")
GHPKG = link("the GitHub Packages NuGet registry",
             "https://docs.github.com/en/packages/working-with-a-github-packages-registry/"
             "working-with-the-nuget-registry")
CODEARTIFACT = link("CodeArtifact with the dotnet CLI",
                    "https://docs.aws.amazon.com/codeartifact/latest/ug/nuget-cli.html")
SOURCELINK = link("Source Link is in the SDK",
                  "https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/8.0/source-link")
CATALOGS = link("Gradle version catalogs", "https://docs.gradle.org/current/userguide/version_catalogs.html")
KTINTERNAL = link("Kotlin visibility modifiers", "https://kotlinlang.org/docs/visibility-modifiers.html")

# ── MEASURED: lesson-07-.../samples/tools/measure_build.py writes this from real builds ────────
M = json.loads((REPO / f"{L}/tools/measurements.json").read_text(encoding="utf-8"))
PP = M["preprocess"]
INC = {r["scenario"]: r["compiled"] for r in M["incremental"]}
BREAKS = {r["break"]: r for r in M["breaks"]}
FMT = {f["file"]: f for f in M["solution_formats"]["files"]}
CA = M["analyzers"]["counts"]

# Pygments' vbnet lexer has no token for VB interpolated strings, so every `$"` prints inside a red
# error box. The code is valid (the samples compile); drop the box, keep the text. (as lesson 01)
_ERROR_SPAN = re.compile(r'<span style="border: 1px solid #F00">(.*?)</span>', re.S)


_CODEH_CSS = ("font-weight:700;font-size:10pt;color:#1A237E;margin:12px 0 4px;border-bottom:2px solid #C5CAE9;"
              "padding-bottom:2px;break-after:avoid;page-break-after:avoid;")


def listed(block, heading):
    """Put a code()/compare() panel in the Contents at level 2 and clean VB highlighting (as lesson 01).

    A listed block gets a Contents page marker, and brief_pdf makes the marker's host break-inside:avoid
    unless the host's first child is a `.ct` heading line — which turned every listed panel unbreakable, so
    a 28-line panel jumped whole and left a third of a page empty. A panel that is not kept (over the kit's
    18-line limit, or keep=False) therefore prints its heading as a `.ct` line styled like `.codeh`: the
    marker is pinned to the heading and the panel may split, as _standard.md section 5 describes. Kept
    panels are left alone (kit request, as lesson 04)."""
    block.update(heading=heading, toc=2)
    if "vb" in block.get("_langs", []):
        block["html"] = _ERROR_SPAN.sub(r"\1", block["html"])
    html = block["html"]
    if 'class="code keep"' not in html and 'class="cmp keep"' not in html:
        block["html"] = html.replace('<div class="codeh">', f'<div class="ct" style="{_CODEH_CSS}">', 1)
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
    """Table-cell commands that never wrap inside themselves (as lesson 01)."""
    return " · ".join(f'<code style="white-space:nowrap">{c}</code>' for c in commands)


def _sources(folder):
    """The C# / VB sources of one sample project, repo-relative — MEASURED input for loc()."""
    root = REPO / MONO / folder
    return [p.relative_to(REPO).as_posix() for p in sorted(root.rglob("*"))
            if p.suffix in (".cs", ".vb") and "/bin/" not in p.as_posix() and "/obj/" not in p.as_posix()]


def _loc(folder):
    return loc(*_sources(folder))


def _clip(text, width=96):
    """A verbatim prefix of a measured compiler message, for a table cell."""
    return esc(text) if len(text) <= width else esc(text[:width].rstrip()) + "…"


def _break_panel(key, what_changed, command):
    """A terminal panel built from one MEASURED deliberate failure in measurements.json."""
    b = BREAKS[key]
    body = textwrap.fill(f"error {b['code']}: {b['message']}", 74)
    return from_text(f"# {what_changed}\n$ {command}\n{body}\n# exit code {b['exit']}",
                     "shell", label="Terminal — a deliberately broken build",
                     file="captured on the build machine by measure_build.py")


def blocks():
    n_proj = len(M["projects"])
    pp_lines = PP["preprocessed_lines"]
    proj_lines = PP["project_file_lines"]
    origin = PP["lines_by_origin"]
    sdk_lines = origin[".NET SDK and MSBuild"]
    dir_lines = origin["Directory.* files"]
    restore_lines = origin["restore output (nuget.g)"]
    banner_lines = PP["banner_lines"]
    content_lines = sum(origin.values())
    sln_lines = FMT["Legacy.sln"]["lines"]
    slnx_lines = FMT["Legacy.slnx"]["lines"]
    sln_guids = FMT["Legacy.sln"]["guids"]
    public_edit = len(INC["public member in L07.Core"])
    core_internal = len(INC["internal member in L07.Core"])
    pricing_internal = len(INC["internal member in L07.Pricing"])
    tests_total = M["ci"]["tests_total"]
    pkgs = M["ci"]["packages"]
    filt = M["solution_filter"]
    modules = [("L07.Core", "src/L07.Core"), ("L07.Pricing", "src/L07.Pricing"),
               ("L07.Pricing.Vb", "src/L07.Pricing.Vb"), ("L07.QuoteCli", "src/L07.QuoteCli"),
               ("L07.Pricing.Tests", "tests/L07.Pricing.Tests")]
    mod_loc = [(name, _loc(folder)) for name, folder in modules]

    dir_cards = [
        {"num": 1, "title": "Directory.Build.props — the defaults", "tags": [T_TOOLING], "pills": [TRAP],
         "what": "Properties for every project below it. Imported EARLY, by Microsoft.Common.props, before the "
                 "project file — so a project can still override anything it sets.",
         "lines": [("Gradle", "The <code>subprojects { }</code> block of a root build script"),
                   ("Finds", "MSBuild walks up from the project folder and stops at the first one it finds"),
                   ("Trap", "Stopping means stopping: a nested file must import its parent by hand"),
                   ("In repo", "MotorMono's sets the version, analyzer level and lock-file policy")]},
        {"num": 2, "title": "Directory.Build.targets — the last word", "tags": [T_TOOLING], "pills": [DIFFERENT],
         "what": "Targets and late properties. Imported LATE, after the project file and after any .targets "
                 "from NuGet packages, so it sees what every project has already set.",
         "lines": [("Gradle", "A convention plugin, or <code>allprojects { }</code> applied last"),
                   ("Use for", "Items and targets built from what the project decided — not for defaults"),
                   ("In repo", "Adds <code>InternalsVisibleTo</code> when a matching .Tests folder exists, and "
                               "a <code>ListProjects</code> target"),
                   ("Note", "A property set here cannot be overridden by an individual project")]},
        {"num": 3, "title": "Directory.Packages.props — the versions", "tags": [T_TOOLING], "pills": [RENAMED],
         "what": "One list of package versions for the whole repository, imported by the SDK's NuGet.props.",
         "lines": [("Gradle", "<code>gradle/libs.versions.toml</code> plus a <code>platform</code>"),
                   ("Rule", "Projects name packages; only this file may carry a version"),
                   ("Pinning", "<code>CentralPackageTransitivePinningEnabled</code> makes the list win for "
                               "transitive packages too"),
                   ("Nearest", "Same first-hit-wins walk-up as Directory.Build.props")]},
        {"num": 4, "title": "Directory.Build.rsp — the switches", "tags": [T_TOOLING], "pills": [SAME],
         "what": "Default command-line arguments for builds started below this folder.",
         "lines": [("Gradle", "<code>gradle.properties</code> with <code>org.gradle.*</code> switches"),
                   ("Applies", "Command-line builds only — Visual Studio ignores it (" + RSPDOC + ")"),
                   ("In repo", "Turns off node reuse and stamps <code>MotorMonoBuiltFrom=command-line</code>"),
                   ("Watch", "A switch here is invisible in the IDE, so behaviour can differ per driver")]},
        {"num": 5, "title": "Directory.Solution.props / .targets", "tags": [T_TOOLING], "pills": [DIFFERENT],
         "what": "Hooks for the solution build itself, not for the projects inside it.",
         "lines": [("Runs when", "MSBuild builds a .slnx or .sln — never inside Visual Studio"),
                   ("Scope", "Nothing it sets reaches the individual project builds"),
                   ("Use for", "One-per-repository steps such as a report after every project is built"),
                   ("In repo", "Not used — MotorMono keeps repo-wide steps in CI instead")]}]

    return [
        style_block(),
        {"type": "toc", "heading": "▤ Contents", "depth": 2,
         "note": "Page numbers are resolved from the rendered PDF. Code panels are cut from the compiled "
                 "samples; every build figure is measured by "
                 "<code>samples/tools/measure_build.py</code> at build time."},
        {"type": "html", "html": "<style>.callout .ct, .story .ct { break-after:avoid; page-break-after:avoid; } "
                                 ".callout li:first-child, .story .ct + p "
                                 "{ break-before:avoid; page-break-before:avoid; }</style>"},

        # ═══════════════════════════ 1 · WHY IT LOOKS EMPTY ═══════════════════════════
        {"type": "story", "heading": "1 · Why a .NET mono-repo looks empty",
         "html": (
             "<p><b>Open a .NET mono-repo and the project files look like someone forgot to finish them.</b> "
             f"<code>L07.Pricing.csproj</code> in this lesson's samples is {proj_lines} lines long and names no "
             "target framework, no source files, no compiler settings and no package versions. That is not a "
             "minimal example: it is what a production project file looks like. The build did not disappear — it "
             "moved into two places you cannot see from the project file, the SDK and a small family of files "
             "named <code>Directory.*</code> that sit above it in the folder tree.</p>"
             f"<p><b>Those {proj_lines} lines evaluate to {pp_lines:,} lines of MSBuild.</b> "
             f"<code>dotnet msbuild -pp</code> expands every import into one document and marks each one with "
             f"a banner, {banner_lines:,} lines in all. Of the other {content_lines:,} lines, {sdk_lines:,} "
             f"come from the .NET SDK, {dir_lines} from the repository's own <code>Directory.*</code> files, "
             f"{restore_lines} from restore output and {origin['your project file']} from the project file "
             f"itself. Coming from a Kotlin mono-repo you "
             "are used to reading a module's <code>build.gradle.kts</code> to know how it builds. Here you read "
             "upwards, and the first question about any .NET repository is <i>which files above this one are "
             "changing the build</i>.</p>"
             "<p><b>The vocabulary maps cleanly; the inheritance rule does not.</b> Properties are Gradle's "
             "<code>ext</code> values, items are source sets, targets are tasks, the SDK is a convention plugin. "
             "But where Gradle merges a root script with every subproject script, MSBuild imports the "
             "<b>nearest</b> <code>Directory.Build.props</code> and then stops looking — a nested one must "
             "import its parent explicitly or the parent silently stops applying. That single rule is the most "
             "expensive thing in this lesson, and §4 shows what it costs when you miss it.</p>"
             "<p><b>What you get in exchange is a build graph you can reason about numerically.</b> Because the "
             "compiler writes a reference assembly next to each output, MSBuild can tell whether a change to a "
             "project can possibly affect the projects that depend on it. Change a method body in this repo and "
             f"one project recompiles; change a public signature and all {public_edit} do. §6 measures every "
             "case, including the one where an <i>internal</i> change behaves like a public one.</p>")},

        {"type": "kpi", "heading": "1.1 · The numbers to leave this lesson with",
         "items": [
             {"label": "MotorMono", "value": f"{n_proj} projects", "tone": "indigo",
              "sub": "C# + VB + tests, one solution · measured"},
             {"label": f"A {proj_lines}-line project file", "value": f"{pp_lines:,} lines", "tone": "violet",
              "sub": "after evaluation · dotnet msbuild -pp"},
             {"label": "Solution file", "value": f"{slnx_lines} lines", "tone": "teal",
              "sub": f"the same {n_proj} projects as .sln: {sln_lines} · measured"},
             {"label": "One public API change", "value": f"{public_edit} of {n_proj} recompile", "tone": "amber",
              "sub": f"an internal one in L07.Core: {core_internal} · measured"},
             {"label": "Analyzer rules on", "value": f"{CA['recommended']} CA rules", "tone": "navy",
              "sub": "latest-recommended, as warnings · measured"}]},

        legend(T_TOOLING),

        {"type": "callout", "variant": "info", "heading": "ℹ Before you start",
         "items": [
             "<b>You need " + ref(1) + " for target framework monikers, the CLI and the publish options, and "
             "enough C# to read a class from " + ref(2) + " and " + ref(3) + ".</b> The Visual Basic project in "
             "this lesson only has to be readable; " + ref(6) + " teaches the language and the migration plan.",
             "<b>You will build <code>samples/MotorMono</code>, a mini mono-repo inside this repository.</b> "
             f"{n_proj} projects in <code>src/</code> and <code>tests/</code>, one solution file, a nested "
             "<code>Directory.Build.props</code> that imports the repository's, central package management, a "
             "custom target, a solution filter and a GitHub Actions workflow that is read into this PDF but "
             "never runs here.",
             "<b>Run it with</b> " + cmd("python 0-script/verify_samples.py --only 7") + " from the repository "
             f"root. It must report {n_proj}/{n_proj} projects passed; the test project alone contributes "
             f"{tests_total} tests.",
             "<b>Every build number in this lesson is measured, not quoted.</b> "
             "<code>samples/tools/measure_build.py</code> copies MotorMono to a temporary folder, edits it, "
             "builds it, breaks it on purpose and records what happened in "
             f"<code>samples/tools/measurements.json</code> — re-measured on {M['measured_on']} with SDK "
             f"{M['sdk']} and MSBuild {M['msbuild']} on {M['os']}.",
             "Facts that change with releases are marked " + VERIFIED + " and link to the official source; "
             "numbers computed from this repository are " + MEASURED + "; a judgement is " + ESTIMATE + ". "
             "Gradle, Kotlin and TypeScript panels are for comparison and are not compiled."]},

        # ═══════════════════════════ 2 · SOLUTIONS ═══════════════════════════
        {"type": "story", "heading": "2 · Solutions — a list of projects, not a build script",
         "html": (
             "<p><b>A solution file is an index, and that is all it is.</b> It names the projects an IDE should "
             "load and a command-line build should walk. It defines no tasks, is not imported by any project "
             "and carries no shared build settings beyond a per-configuration mapping. Its only say in build "
             "order is the solution-level project dependencies an IDE can add, which MSBuild turns into "
             "<code>ProjectReference</code> items — the order the projects themselves declare is what a "
             "mono-repo runs on. If you are looking for the mono-repo's shared configuration, the solution "
             "file is the one place it is guaranteed not to be.</p>"
             "<p><b>In .NET 10 the format is XML, and it is the default.</b> "
             f"<code>dotnet new sln</code> now produces <code>.slnx</code>; the .NET SDK gained the format in "
             "9.0.200 and <code>--format sln</code> still writes the old one (" + SLNXBREAK + " · "
             + SLNXCLI + "). The old <code>.sln</code> is a line-oriented format from Visual Studio .NET whose "
             "content is mostly GUIDs and per-configuration mappings; the new one is a project list. Visual "
             "Studio reads both from 17.14 (" + SLNXVS + "), and MSBuild has accepted <code>.slnx</code> since "
             "17.12 (" + BUILDPROC + ").</p>"
             "<p><b>What you actually gain is merge behaviour.</b> The measured comparison below is the same "
             f"{n_proj} projects written both ways: {sln_lines} lines and {sln_guids} distinct GUIDs against "
             f"{slnx_lines} lines and none. Two people adding a project to a <code>.sln</code> on two branches "
             "conflict in a block of generated identifiers; on a <code>.slnx</code> they add one line each. "
             "This is the same reason your Gradle mono-repo keeps <code>settings.gradle.kts</code> boring.</p>")},

        {"type": "chart", "heading": "2.1 · The same five projects, two solution formats", "kind": "bar",
         "args": {"data": [(".sln (classic)", sln_lines), (".slnx (migrated)", slnx_lines),
                           (".slnx (hand-written)", FMT["MotorMono.slnx"]["lines"])],
                  "ylabel": "lines in the file", "tone": "teal", "width": 520, "height": 200},
         "caption": "measured by creating the classic file with the CLI, adding the five projects, then running "
                    "dotnet sln migrate on the build machine",
         "note": f"<b>{sln_lines} lines and {sln_guids} GUIDs become {slnx_lines} lines and none.</b> "
                 f"The classic file is {FMT['Legacy.sln']['chars']:,} characters against "
                 f"{FMT['Legacy.slnx']['chars']} — most of it per-project, per-configuration mappings that "
                 "merge badly. The hand-written file in this repository is "
                 f"{FMT['MotorMono.slnx']['lines']} lines because it adds solution folders for the build files. "
                 + MEASURED + ", and " + VERIFIED + " as the .NET 10 default (" + SLNXBREAK + ")."},

        pcode(from_sample(SLNX),
              "2.2 · The whole solution file",
              "<b>Folders, projects, nothing else.</b> The <code>/build/</code> folder is a <i>solution folder</i> "
              "— a display grouping that makes the shared build files visible in an IDE; it creates no directory "
              "and changes no build. Note what is absent: no configuration matrix, no project GUIDs, no build "
              "order. <code>dotnet build MotorMono.slnx</code> builds these projects in dependency order because "
              "each project declares its own <code>ProjectReference</code> items (6.1), not because this file "
              "says so."),

        mapping("2.3 · Concept map — Gradle, Maven and Lerna to MSBuild", [
            ("<code>settings.gradle.kts</code> · <code>lerna.json</code> · Maven <code>&lt;modules&gt;</code>",
             "<code>MotorMono.slnx</code>", "renamed",
             "A list of projects only: no build order, no shared settings, nothing imports it"),
            ("A module's <code>build.gradle.kts</code>", "<code>.csproj</code> / <code>.vbproj</code>", "renamed",
             f"{proj_lines} lines is normal — the SDK and the Directory.* files supply the rest"),
            ("Root <code>subprojects { }</code> / <code>allprojects { }</code>",
             "<code>Directory.Build.props</code>", "trap",
             "Only the NEAREST one is imported; a nested file must import its parent by hand (4.1)"),
            ("A convention plugin · <code>buildSrc</code>", "<code>Directory.Build.targets</code> or a custom SDK",
             "different", "Imported after the project file, so it can override what a project set"),
            ("<code>gradle.properties</code>", "Properties in <code>Directory.Build.props</code>", "same",
             "Plain name/value pairs, evaluated in order of appearance"),
            ("<code>-PsomeFlag=true</code>", "<code>-p:SomeFlag=true</code>", "same",
             "A global property: it beats any value a project file sets, though the project is read later"),
            ("A Gradle task · a task action", "An MSBuild target, which calls tasks (<code>Csc</code>, "
                                              "<code>Message</code>)", "renamed",
             "Ordered by <code>DependsOnTargets</code> / <code>BeforeTargets</code> / <code>AfterTargets</code>"),
            ("<code>sourceSets</code> / include patterns", "Items (<code>Compile</code>, "
                                                           "<code>ProjectReference</code>)", "renamed",
             "The SDK already globs every <code>.cs</code>: adding one by hand fails the build with "
             "<code>NETSDK1022</code> unless <code>EnableDefaultCompileItems</code> is off"),
            ("<code>gradle/libs.versions.toml</code>", "<code>Directory.Packages.props</code>", "different",
             "A catalog offers versions; central package management plus pinning enforces them (5.4)"),
            ("A Gradle <code>platform</code> · a Maven BOM",
             "<code>CentralPackageTransitivePinningEnabled</code>", "same",
             "The switch that makes your list win for packages you never referenced"),
            ("<code>gradle.lockfile</code> · <code>package-lock.json</code>",
             "<code>packages.lock.json</code>", "renamed",
             "Opt-in per project via <code>RestorePackagesWithLockFile</code>, and one file per project"),
            ("<code>npm ci</code> · <code>--offline</code>", "<code>RestoreLockedMode</code>", "renamed",
             "Turn it on only when <code>CI</code> is set, or every local version bump fails"),
            ("ktlint · Spotless · ESLint", ".editorconfig + Roslyn analyzers + " + cmd("dotnet format"),
             "different", "The rules ship inside the SDK; severity is per rule in <code>.editorconfig</code>"),
            ("A SonarQube quality gate", "<code>AnalysisLevel</code> + <code>TreatWarningsAsErrors</code>",
             "different", "In-build and per-project rather than a separate server pass (7.2)"),
            ("Kotlin <code>internal</code> (module = source set)",
             "<code>internal</code> + <code>InternalsVisibleTo</code>", "trap",
             "Gradle gives the test source set access for free; .NET needs the attribute (6.3)"),
            ("<code>mvn install</code> · <code>npm publish</code>", cmd("dotnet pack", "dotnet nuget push"),
             "renamed", "One <code>.nupkg</code> per packable project, versioned from one property (8.1)"),
            ("Maven Central · the npm registry", "nuget.org · GitHub Packages · AWS CodeArtifact", "same",
             "Map every package id to one feed or CPM warns NU1507 (5.3)"),
        ]),

        pcompare(from_sample(SLNF_FILE),
                 from_text("""
                 $ dotnet build MotorMono.Pricing.slnf
                   Determining projects to restore...
                   L07.Core -> ...bin/L07.Core/debug/L07.Core.dll
                   L07.Pricing -> ...L07.Pricing.dll
                   L07.Pricing.Vb -> ...L07.Pricing.Vb.dll
                   L07.Pricing.Tests -> ...L07.Pricing.Tests.dll
                 Build succeeded.  0 Warning(s)  0 Error(s)
                 """, "text", label="Terminal — three listed, four built",
                           file="captured on the build machine; output paths shortened"),
                 "2.4 · A solution filter lists three projects and builds four",
                 f"<b>A filter narrows what is loaded, not what is built.</b> The filter names "
                 f"{len(filt['listed'])} projects and the build produced {len(filt['built'])}: "
                 "<code>L07.Pricing.Tests</code> references the Visual Basic project, so MSBuild builds it too "
                 "— <i>“It builds a project if it's specified in the filter or referenced by a project that is "
                 "built”</i> (" + FILTERS + "). Treat <code>.slnf</code> as the IDE-startup-time tool it is, "
                 "not a module boundary; to cut a subgraph out of a build you have to cut the "
                 "<code>ProjectReference</code>. The shortened paths are the other setting worth copying: "
                 f"<code>UseArtifactsOutput</code> is <code>{M['properties']['UseArtifactsOutput']}</code> here, "
                 "so every project's <code>bin</code> and <code>obj</code> land under one "
                 "<code>artifacts/</code> tree — one folder to cache in CI and one to delete "
                 "(" + ARTIFACTS + ")."),

        # ═══════════════════════════ 3 · THE MSBUILD MODEL ═══════════════════════════
        {"type": "story", "heading": "3 · The MSBuild model — two phases, four nouns",
         "html": (
             "<p><b>MSBuild is not a script that runs top to bottom; it is a document that is evaluated, and "
             "then a graph of targets that is executed.</b> Everything outside a target — every property, every "
             "item, every import — is read first, in six ordered passes: environment variables, imports and "
             "properties, item definitions, items, <code>UsingTask</code> declarations, and finally target "
             "definitions. No compiler runs during any of it. Only then does execution start (" + BUILDPROC
             + ").</p>"
             "<p><b>Knowing which phase you are in explains the two things that surprise Gradle users most.</b> "
             "The first: properties are evaluated in order of appearance, so a property can read values declared "
             "above it but not below — which is why <code>Directory.Build.props</code> has to be imported early "
             "to be useful and why the SDK warns you not to read items from it. The second: because the whole "
             "document is read up front, a file your build writes during execution cannot change that same "
             "build. There is no <code>doLast { }</code> that edits the build.</p>"
             "<p><b>The nouns are few, and you already know them under other names.</b> A property is a string. "
             "An item is a named list of things with metadata attached. A target is an ordered unit of work that "
             "calls tasks, which are .NET classes. Command-line <code>-p:Name=Value</code> creates a "
             "<i>global</i> property that overrides whatever the project file says, even though the project is "
             "read later — the same escape hatch as Gradle's <code>-P</code>. Everything else in this lesson is "
             "a particular arrangement of those four ideas.</p>")},

        {"type": "mermaid", "inline": True,
         "heading": "3.1 · What happens before your code compiles",
         "caption": "indigo = your input · amber = evaluation, where nothing is built · teal = execution, where "
                    "tasks run · the six evaluation passes are ordered, and each can only see what came before it",
         "code": ("flowchart TB\n"
                  '  subgraph S["Startup — command line wins"]\n'
                  "    direction LR\n"
                  '    A1["dotnet build<br/>-p:Version=1.4.2"]:::io --> A2["Directory.Build.rsp<br/>default switches"]:::io --> A3["global properties<br/>override project files"]:::io\n'
                  "  end\n"
                  '  subgraph E["Evaluation — no compiler runs"]\n'
                  "    direction LR\n"
                  '    B1["1 environment<br/>variables"]:::ev --> B2["2 imports and<br/>properties"]:::ev --> B3["3 item<br/>definitions"]:::ev --> B4["4 items"]:::ev --> B5["5 UsingTask"]:::ev --> B6["6 target<br/>definitions"]:::ev\n'
                  "  end\n"
                  '  subgraph X["Execution — targets and tasks"]\n'
                  "    direction LR\n"
                  '    C1["ResolveProject<br/>References"]:::ex --> C2["CoreCompile<br/>Csc or Vbc"]:::ex --> C3["custom targets<br/>Pack, ListProjects"]:::ex\n'
                  "  end\n"
                  "  S --> E --> X\n"
                  "  classDef io fill:#c7d2fe,color:#1f2937,stroke:#6366f1;\n"
                  "  classDef ev fill:#fde68a,color:#1f2937,stroke:#d97706;\n"
                  "  classDef ex fill:#ccfbf1,color:#1f2937,stroke:#0d9488;\n"
                  "  style S fill:#eef2ff,color:#1f2937,stroke:#6366f1\n"
                  "  style E fill:#fffbeb,color:#1f2937,stroke:#d97706\n"
                  "  style X fill:#f0fdfa,color:#1f2937,stroke:#0d9488\n")},

        {"type": "table", "heading": "3.2 · The nouns of a build, and what you call them today",
         "cols": ["MSBuild", "What it is", "Gradle · npm", "In MotorMono"],
         "rows": [
             ["<b>Property</b>", "A single string, evaluated in order of appearance outside targets",
              "<code>ext</code> value · <code>gradle.properties</code> · a script variable",
              "<code>VersionPrefix</code>, <code>AnalysisLevel</code>, <code>MotorMonoBuiltFrom</code>"],
             ["<b>Item</b>", "A named list; each entry has an identity and metadata, read as "
                             "<code>%(Name)</code>",
              "A <code>sourceSet</code>, a dependency configuration",
              "<code>ProjectReference</code>, <code>PackageReference</code>, <code>MotorProject</code>, and "
              "<code>%(MotorProject.Filename)</code> in <code>ListProjects</code>"],
             ["<b>Target</b>", "An ordered unit of work with inputs, outputs and conditions",
              "A Gradle task · an npm script", "<code>ListProjects</code>, <code>StampBuildFacts</code>"],
             ["<b>Task</b>", "A .NET class the build loads and calls",
              "A task action · an Ant task", "<code>Message</code>, and <code>Csc</code> / <code>Vbc</code> "
                                             "from the SDK"],
             ["<b>SDK</b>", "A package of props and targets imported by the <code>Sdk</code> attribute",
              "A convention plugin applied by id", "<code>Microsoft.NET.Sdk</code> in all five projects"],

             ["<b>Binary log</b>", "A replayable recording of one build",
              "<code>--scan</code> / a build scan", cmd("-bl:build.binlog") + " in CI (" + BINLOG + ")"]]},

        {"type": "chart", "heading": "3.3 · Where the lines of an evaluated project come from", "kind": "hbar",
         "args": {"data": [(".NET SDK and MSBuild", sdk_lines), ("Directory.* files", dir_lines),
                           ("restore output (nuget.g)", origin["restore output (nuget.g)"]),
                           ("your project file", origin["your project file"])],
                  "labelw": 200, "tone": "violet", "width": 560},
         "caption": "lines of the expanded project produced by dotnet msbuild -pp on "
                    "src/L07.Pricing/L07.Pricing.csproj, attributed to the file each line came from · "
                    f"the {banner_lines:,} lines of import banners -pp writes between files belong to no file "
                    "and are left out",
         "note": f"<b>You wrote {origin['your project file']} of {content_lines:,} lines of build logic, and "
                 f"your repository contributed {dir_lines} more.</b> The rest is the SDK: "
                 f"{PP['files']} files imported into one document before anything is built; the other "
                 f"{banner_lines:,} lines of the {pp_lines:,} are the banners <code>-pp</code> writes between "
                 "files. Debugging a property means asking <i>where in this document is it set</i>, which is "
                 "what <code>-pp</code> is for (" + BYDIR + f"). And those {dir_lines} lines from "
                 "<code>Directory.*</code> are the highest-leverage lines in the repository: they apply to "
                 "every module, so an error there is an error everywhere. " + MEASURED + "."},

        pcode(from_sample(DBT),
              "3.4 · Items and targets — the repository's own build logic",
              "<b>Read this as three declarations and two behaviours.</b> The <code>InternalsVisibleTo</code> "
              "item is conditional on a folder existing, so a module gets test access by <i>convention</i> "
              "rather than per project — the Gradle rule reproduced by hand (6.3). <code>MotorProject</code> is "
              "an item built from two globs, so <code>@(MotorProject-&gt;Count())</code> is the module count of "
              "the repository. <code>ListProjects</code> runs only when you ask for it by name; "
              "<code>StampBuildFacts</code> hooks <code>BeforeTargets</code> on an SDK target and writes those "
              "facts into every executable's metadata, which is how the CLI can print them back (9.2). Because "
              "this file is imported <i>after</i> the project file, it can safely count what the projects "
              "declared (" + BYDIR + ")."),

        pcode(from_text("""
              $ dotnet msbuild src/L07.Core -t:ListProjects -nologo -tl:off

                MotorMono: 5 projects
                  L07.Core.csproj
                  L07.Pricing.Vb.vbproj
                  L07.Pricing.csproj
                  L07.QuoteCli.csproj
                  L07.Pricing.Tests.csproj
              """, "shell", label="Terminal — a custom target, run by name",
                        file="captured on the build machine"),
              "3.5 · Running one target and nothing else",
              "<b>A target you have to ask for is the safe way to add repository tooling.</b> "
              "<code>-t:ListProjects</code> evaluates the project and runs one target, skipping the compile "
              "graph. The count and names come from the <code>MotorProject</code> globs, so a new project "
              "appears the moment its file lands on disk. The order is the file system's, not the build "
              "order."),

        # ═══════════════════════════ 4 · SHARED BUILD LOGIC ═══════════════════════════
        {"type": "story", "heading": "4 · Shared build logic — and the one rule that bites",
         "html": (
             "<p><b>MSBuild walks up from each project folder, imports the first "
             "<code>Directory.Build.props</code> it finds, and stops.</b> Microsoft's own summary is blunt: "
             "<i>“the first Directory.Build.props that doesn't import anything is where MSBuild stops”</i> "
             "(" + BYDIR + "). Gradle merges a root script into every subproject automatically; MSBuild does "
             "not: the day someone adds a second file in a subfolder, every setting from the root silently "
             "stops applying beneath it.</p>"
             "<p><b>That is not a hypothetical — it is this lesson's samples.</b> MotorMono has its own "
             "<code>Directory.Build.props</code> for its own version and analyzer mode, and the repository "
             "root has one that sets <code>net10.0</code>, nullable reference types, "
             "<code>Option Strict On</code> and warnings-as-errors. The nested file's first line is a "
             "hand-written <code>Import</code> of the parent (4.2, 4.4); delete it and the build fails at once "
             f"with <code>{BREAKS['nested Directory.Build.props without the parent Import']['code']}</code> "
             "(4.3) — the target framework has vanished.</p>"
             "<p><b>Three other files complete the family, and the differences are about timing.</b> "
             "<code>Directory.Build.props</code> is imported <i>early</i>, before the project file, so a project "
             "can override it — it sets defaults. <code>Directory.Build.targets</code> is imported <i>late</i>, "
             "after the project file and after any <code>.targets</code> from NuGet packages, so it wins — it "
             "enforces. <code>Directory.Packages.props</code> is pulled in by the SDK's restore logic and owns "
             "versions (§5). <code>Directory.Build.rsp</code> is read by the command-line driver only, which "
             "makes it one of the two kinds of file that can make <code>dotnet build</code> and Visual Studio "
             "disagree — the other is <code>Directory.Solution.props</code> / <code>.targets</code> "
             "(4.5).</p>")},

        {"type": "mermaid", "inline": True,
         "heading": "4.1 · Who imports what, measured on L07.Pricing",
         "caption": "indigo = the project · grey = files the SDK supplies · green = files this repository owns · "
                    "every arrow was read out of the expanded project by measure_build.py; the doubled arrow is "
                    "the only import written by hand",
         "code": ("flowchart LR\n"
                  '  P["src/L07.Pricing<br/>L07.Pricing.csproj<br/>Sdk=Microsoft.NET.Sdk"]:::proj\n'
                  '  CP["Microsoft.Common.props<br/>SDK · early"]:::sdk\n'
                  '  D1["MotorMono/<br/>Directory.Build.props"]:::mine\n'
                  '  D2["repo root/<br/>Directory.Build.props"]:::mine\n'
                  '  NP["NuGet.props<br/>SDK · restore"]:::sdk\n'
                  '  D3["MotorMono/<br/>Directory.Packages.props"]:::mine\n'
                  '  CT["Microsoft.Common.targets<br/>SDK · late"]:::sdk\n'
                  '  D4["MotorMono/<br/>Directory.Build.targets"]:::mine\n'
                  '  P --> CP\n'
                  '  CP -->|"walks up · first hit wins"| D1\n'
                  '  D1 ==>|"GetPathOfFileAbove<br/>written by hand"| D2\n'
                  '  P --> NP\n'
                  '  NP -->|"walks up"| D3\n'
                  '  P --> CT\n'
                  '  CT -->|"walks up"| D4\n'
                  "  classDef proj fill:#c7d2fe,color:#1f2937,stroke:#6366f1;\n"
                  "  classDef sdk fill:#e2e8f0,color:#1f2937,stroke:#475569;\n"
                  "  classDef mine fill:#bbf7d0,color:#1f2937,stroke:#16a34a;\n")},

        pcode(from_sample(DBP),
              "4.2 · The nested Directory.Build.props, line by line",
              "<b>Line 3 is the whole lesson.</b> Without that <code>Import</code> the repository root's file "
              "never applies here. After it, read the rest as policy for every module: one "
              "<code>VersionPrefix</code> so the repo ships one version (8.4); "
              "<code>AnalysisLevel</code> + <code>EnforceCodeStyleInBuild</code> so analyzers and style rules "
              "run in the build rather than in an IDE (7.2); lock files everywhere, switched to locked mode "
              "only when the <code>CI</code> environment variable is set, which is how a version bump stays "
              "easy locally and impossible to forget in CI (5.3). The last group is a <i>convention</i>: any "
              "project whose name ends <code>.Tests</code> is not packable, so nobody has to remember "
              "<code>IsPackable</code> per project."),

        pcode(_break_panel("nested Directory.Build.props without the parent Import",
                           "MotorMono/Directory.Build.props with its parent Import deleted",
                           "dotnet build src/L07.Core"),
              "4.3 · What the trap actually looks like",
              "<b>The error names the symptom, not the cause.</b> <code>TargetFramework</code> is empty because "
              "the only file that sets it — the repository root's <code>Directory.Build.props</code> — is no "
              "longer imported, and nothing in the message mentions imports. This is the diagnosis loop to "
              "learn: when a property is missing or wrong, run "
              + cmd("dotnet msbuild &lt;project&gt; -getProperty:TargetFramework") + " to see its evaluated "
              "value, then " + cmd("dotnet msbuild &lt;project&gt; -pp:pp.xml") + " and search the expanded "
              "document for the file you expected to set it (" + BYDIR + "). " + MEASURED + " by deleting the "
              "import in a temporary copy of the samples."),

        pcode(from_sample(ROOT_DBP),
              "4.4 · The parent it chains to — and how one file serves C# and VB",
              "<b>The repository root's file is the one 4.2 imports, and it is where the two languages part "
              "ways.</b> The first group applies to every project; the two groups below it are gated on "
              "<code>MSBuildProjectExtension</code>, so a <code>.csproj</code> gets <code>Nullable</code> and "
              "<code>ImplicitUsings</code> while a <code>.vbproj</code> gets <code>Option Strict On</code> — "
              "settings that mean something to one compiler and are noise to the other. One file, two "
              "languages, no per-project copy. <code>WarningsNotAsErrors</code> keeps a newly published NuGet "
              "advisory from breaking an old lesson overnight (§5)."),

        {"type": "cards",
         "band": {"title": "4.5 · The Directory.* family — what each file may decide", "note": "build view",
                  "tone": "indigo"},
         "cards": dir_cards[:3]},
        {"type": "cards", "toc": False,
         "band": {"title": "4.5 · The Directory.* family (continued)", "note": "build view", "tone": "indigo"},
         "cards": dir_cards[3:]},

        # ═══════════════════════════ 5 · DEPENDENCIES ═══════════════════════════
        {"type": "story", "heading": "5 · Dependencies — one version list for the repository",
         "html": (
             "<p><b>Central package management moves every version out of every project file into one "
             "<code>Directory.Packages.props</code>, and then forbids the old way.</b> Set "
             "<code>ManagePackageVersionsCentrally</code>, list <code>PackageVersion</code> items, and a "
             "<code>PackageReference</code> that still carries a <code>Version</code> attribute is an error, not "
             "a warning (" + CPM + "). That last part is the difference from a Gradle version catalog, which is "
             "a convenience you can bypass one module at a time.</p>"
             "<p><b>The switch that matters is transitive pinning.</b> A Gradle version catalog declares the "
             "versions you <i>ask</i> for — the docs are explicit that Gradle <i>“may still select different "
             "versions due to dependency graph conflicts or constraints applied through platforms”</i> "
             "(" + CATALOGS + "). <code>CentralPackageTransitivePinningEnabled</code> is the "
             "<code>platform</code>/BOM half: a version in your list wins even for a package no project "
             "references directly. It has a library-author edge, and " + CPM + " states it: when you pack, a "
             "pinned transitive is promoted to an explicit dependency of your package. In an application "
             "repository that is what you want; in a published library it changes your public dependency "
             "set.</p>"
             "<p><b>Two .NET 10 defaults change what restore does, in your favour.</b> Auditing is now on for "
             "transitive packages, not just direct ones, whenever a project targets <code>net10.0</code> or "
             "later (" + AUDIT10 + "), and package pruning removes framework-provided packages from the graph "
             "for those projects — Microsoft measured <i>70% fewer transitive vulnerability reports</i> and "
             "restores <i>up to 50%</i> faster (" + PRUNING + "). Both are measured as on in this repository "
             f"(<code>NuGetAuditMode</code> = <code>{M['properties']['NuGetAuditMode']}</code>, "
             f"<code>RestoreEnablePackagePruning</code> = "
             f"<code>{M['properties']['RestoreEnablePackagePruning']}</code>). Audit warnings deliberately do "
             "<i>not</i> fail this repository's build: the root file excludes NU1901–NU1904 from "
             "warnings-as-errors so a newly published advisory cannot break an old lesson overnight.</p>")},

        pcode(from_sample(DPP),
              "5.1 · The repository's one version list",
              "<b>Three packages, three versions, one file, whole repository.</b> This is "
              "<code>gradle/libs.versions.toml</code> and a <code>platform</code> merged into one document — and "
              "unlike the catalog it is compulsory: with <code>ManagePackageVersionsCentrally</code> on, a "
              "project that names a version is rejected (5.3). The walk-up rule of §4 applies here too, so a "
              "nested <code>Directory.Packages.props</code> needs the same hand-written import. Lock files "
              "(<code>packages.lock.json</code>, one per project, committed) are what turn this list into a "
              "reproducible restore (" + LOCKFILE + ")."),

        pcode(from_sample(TESTS_PROJ),
              "5.2 · The consumer side — references without versions",
              "<b>Notice three conventions at once.</b> The <code>PackageReference</code> items carry no "
              "version, because §5.1 owns them. The <code>Using</code> item adds a global "
              "<code>using Xunit;</code> for every file in the project — an MSBuild item that changes the C# "
              "compilation, not a source edit. And nothing here marks this as a test project that must not "
              "ship: <code>Directory.Build.props</code> already did that for every name ending "
              f"<code>.Tests</code>, which is why <code>dotnet pack</code> produced {len(pkgs)} packages from "
              f"{n_proj} projects (8.4)."),

        {"type": "table", "heading": "5.3 · Four ways a shared version list fails, and what restore says",
         "cols": ["What someone did", "Code", "Abridged message from the real run", "The fix"],
         "rows": [
             ["Left <code>Version</code> on a <code>PackageReference</code> under CPM",
              pill(BREAKS["a Version attribute left on a PackageReference under CPM"]["code"], "red"),
              _clip(BREAKS["a Version attribute left on a PackageReference under CPM"]["message"]),
              "Move the version to a <code>PackageVersion</code> item"],
             ["Bumped a version and did not commit the lock file, with <code>CI=true</code>",
              pill(BREAKS["CI=true and a version changed without updating the lock file"]["code"], "red"),
              _clip(BREAKS["CI=true and a version changed without updating the lock file"]["message"]),
              "Restore locally, commit <code>packages.lock.json</code>"],
             ["Added a second feed and no source mapping",
              pill(BREAKS["a second package source and no packageSourceMapping"]["code"], "red"),
              _clip(BREAKS["a second package source and no packageSourceMapping"]["message"]),
              "Map every package id to one feed (" + SRCMAP + ")"],
             ["Referenced a package with a known vulnerability",
              pill("NU1901–NU1904", "amber"),
              "Audit warns at restore; on <code>net10.0</code> for transitive packages too (" + AUDIT10 + ")",
              "Upgrade, or scope <code>WarningsNotAsErrors</code> deliberately"]]},

        {"type": "chart", "heading": "5.4 · What each ecosystem's shared version list actually guarantees",
         "kind": "heatmap",
         "args": {"rows": ["One file owns the versions", "Transitive versions pinned",
                           "Lock file enforced in CI", "Vulnerability audit at restore",
                           "Per-project override", "One feed, package ids mapped"],
                  "cols": ["CPM", "Gradle", "npm", "Maven"],
                  "matrix": [[2, 2, 1, 2], [2, 1, 1, 2], [2, 1, 2, 0], [2, 0, 2, 0], [2, 2, 1, 2],
                             [2, 1, 1, 1]],
                  "cell": 44, "tone": "indigo", "fmt": lambda v: {2: "yes", 1: "some", 0: "—"}[int(v)]},
         "caption": "CPM = .NET 10 central package management · npm = npm workspaces · yes = built in and "
                    "enforced · some = possible with a second mechanism or a plugin · — = not in the box · "
                    "a rubric, not a benchmark",
         "note": "<b>Read the second row first.</b> Gradle scores <i>some</i> because the catalog declares and "
                 "a <code>platform</code> enforces — two mechanisms (" + CATALOGS + ") — where CPM plus "
                 "<code>CentralPackageTransitivePinningEnabled</code> is one. Row 4 is the .NET 10 change: "
                 "audit is in <code>dotnet restore</code> itself, at <code>all</code> by default for "
                 "<code>net10.0</code> (" + AUDIT10 + "), where the JVM reaches for a plugin. Row 6 is the "
                 "supply-chain one: <code>packageSourceMapping</code> binds each id to one feed, which is the "
                 "answer to dependency confusion when you add a private feed (§8). " + ESTIMATE + " — the "
                 "author's rubric of built-in behaviour, not a measurement."},

        # ═══════════════════════════ 6 · THE BUILD GRAPH ═══════════════════════════
        {"type": "story", "heading": "6 · The build graph — what recompiles when you change one line",
         "html": (
             "<p><b>The build order is not in the solution; it is the transitive closure of "
             "<code>ProjectReference</code> items.</b> During execution, <code>ResolveProjectReferences</code> "
             "calls MSBuild on each referenced project and pauses until it returns, so the graph is walked "
             "depth-first as a tree of builds (" + BUILDPROC + "). <code>L07.QuoteCli</code> in the samples "
             "never references <code>L07.Core</code>, yet compiles against it: a project reference is "
             "transitive, which is the opposite of Gradle's <code>implementation</code> and the same as its "
             "<code>api</code>.</p>"
             "<p><b>What makes the graph cheap is the reference assembly.</b> Every project also emits a "
             "metadata-only copy of itself, and Microsoft's description of why is exact: <i>“The reference "
             "assembly only changes when its public API is affected. So, using the reference assembly as an "
             "input file instead of the implementation assembly allows skipping the build of the dependent "
             f"project in some cases”</i> (" + REFASM + "). Measured on this repository: a method body edit in "
             f"<code>L07.Core</code> recompiles {len(INC['method body in L07.Core'])} project; changing a public "
             f"signature recompiles all {public_edit}.</p>"
             "<p><b>And then there is the case that breaks the rule.</b> An internal member added to "
             f"<code>L07.Core</code> recompiles {core_internal} project — but the same edit in "
             f"<code>L07.Pricing</code> recompiles {pricing_internal}. The reason is one line of "
             "<code>Directory.Build.targets</code>: <code>L07.Pricing</code> has a test project, so it gets "
             "<code>InternalsVisibleTo</code>, and <i>“If there are no <code>InternalsVisibleTo</code> "
             "attributes, internal function members are also removed”</i> from the reference assembly "
             "(" + REFASM + " · " + REFOUT + "). Granting test access to internals is not free: it puts your "
             "internals in the public contract the build compares.</p>")},

        {"type": "mermaid", "inline": True,
         "heading": "6.1 · The MotorMono build graph, and what each edge carries",
         "caption": "violet = C# library · blue = Visual Basic library · green = console app · amber = tests · "
                    "every thin edge is a project reference that carries the public API only, so an internal "
                    "change stops there; the one thick edge also carries internals, because InternalsVisibleTo "
                    "keeps them in the reference assembly",
         "code": ("flowchart LR\n"
                  '  CORE["L07.Core<br/>Money · QuoteRequest<br/>IRatingRule"]:::lib\n'
                  '  PR["L07.Pricing<br/>calculator · rules<br/>internals visible to tests"]:::lib\n'
                  '  VB["L07.Pricing.Vb<br/>the same interface,<br/>in Visual Basic"]:::vb\n'
                  '  TS["L07.Pricing.Tests<br/>xUnit"]:::test\n'
                  '  CLI["L07.QuoteCli<br/>console · not packable"]:::app\n'
                  '  CORE --> PR\n'
                  '  CORE --> VB\n'
                  '  PR ==>|"public + internal"| TS\n'
                  '  VB --> TS\n'
                  '  PR --> CLI\n'
                  '  VB --> CLI\n'
                  "  classDef lib fill:#ede9fe,color:#1f2937,stroke:#6d28d9;\n"
                  "  classDef vb fill:#dbeafe,color:#1f2937,stroke:#1d4ed8;\n"
                  "  classDef app fill:#bbf7d0,color:#1f2937,stroke:#16a34a;\n"
                  "  classDef test fill:#fef3c7,color:#1f2937,stroke:#b45309;\n")},

        {"type": "chart", "heading": "6.2 · Projects the compiler re-ran, by kind of edit", "kind": "hbar",
         "args": {"data": [(scenario, len(INC[scenario])) for scenario in
                           ["clean build", "no change", "method body in L07.Core",
                            "internal member in L07.Core", "internal member in L07.Pricing",
                            "public member in L07.Core"]],
                  "labelw": 210, "tone": "amber", "width": 560},
         "caption": "projects whose CoreCompile target actually invoked Csc or Vbc, counted from a detailed "
                    "MSBuild log after each edit, on a temporary copy of the samples",
         "note": f"<b>The two middle bars are the same edit in two projects, and they differ.</b> An internal "
                 f"member added to <code>L07.Core</code> costs {core_internal} compile; the same member in "
                 f"<code>L07.Pricing</code> costs {pricing_internal}, because that project's reference assembly "
                 "carries its internals for the test project. The ceiling is a public signature change: "
                 f"{public_edit} of {n_proj}. Scale it mentally to a 120-module repository and the design rule "
                 "writes itself — keep the widely referenced projects small and their public surface stable, and "
                 "do not hand out <code>InternalsVisibleTo</code> to a project everything depends on. "
                 + MEASURED + "."},

        pcompare(from_text("""
                 // a Gradle module is one compilation unit, and
                 // src/main + src/test are the SAME module
                 internal object BaseRates {
                     // share of the sum insured, illustrative
                     fun forClass(c: CoverageClass): BigDecimal =
                         when (c) {
                             CLASS_1 -> "0.018".toBigDecimal()
                             CLASS_3 -> "0.004".toBigDecimal()
                             else -> throw IllegalArgumentException()
                         }
                 }

                 // nothing to declare anywhere: the test source
                 // set already sees main's internal members
                 class BaseRatesTest {
                     @Test fun class1() = assertEquals(
                         "0.018".toBigDecimal(),
                         BaseRates.forClass(CLASS_1))
                 }
                 """, "kotlin", file="Kotlin — internal is per module, tests included"),
                 from_sample(INTERNALS, "internals"),
                 "6.3 · internal in Kotlin and in C# — the same word, a different boundary",
                 "<b>Kotlin's module is a Gradle source set, and its test source set is inside it; .NET's "
                 "module is the assembly, and the test project is a different one.</b> Kotlin grants the test "
                 "access by definition — the language reference lists <i>“A Gradle source set (with the "
                 "exception that the <code>test</code> source set can access the internal declarations of "
                 "<code>main</code>)”</i> (" + KTINTERNAL + "). In .NET nothing is visible across an assembly "
                 "until <code>InternalsVisibleTo</code> says so, which is why this repository re-creates the "
                 "Gradle convention with the glob condition in 3.4, and why the test in the samples can call "
                 "<code>BaseRates.For</code> at all. The cost is measured in 6.2 — and the "
                 "<code>ArgumentOutOfRangeException</code> arm exists because the C# compiler, unlike Kotlin's "
                 "<code>when</code> over an enum, does not treat the switch as exhaustive."),

        pcompare(from_sample(NCB_CS, "ncb-rule"), from_sample(NCB_VB, "ncb-rule"),
                 "6.4 · One build graph, two languages, one interface",
                 "<b>A mixed-language mono-repo needs no bridge: both projects implement the same "
                 "<code>IRatingRule</code> from <code>L07.Core</code> and both are referenced by the same "
                 "console app and the same test project.</b> The build differences are real but small: the VB "
                 "project needs <code>Implements IRatingRule.Name</code> on each member where C# infers it, and "
                 "the repository root's <code>Directory.Build.props</code> has to split its settings by project "
                 "extension so C# gets <code>Nullable</code> and VB gets <code>Option Strict On</code> (4.4). For a "
                 "migration this is the whole strategy in one screen — port a rule to C#, keep both in the "
                 "graph, and let the parity test in <code>L07.Pricing.Tests</code> prove they agree before the "
                 "VB one is deleted (" + ref(6) + ")."),

        # ═══════════════════════════ 7 · QUALITY GATES ═══════════════════════════
        {"type": "story", "heading": "7 · Quality gates that live inside the build",
         "html": (
             "<p><b>In .NET the linter is the compiler.</b> Roslyn analyzers ship inside the SDK and run as part "
             "of every build, so there is no ktlint to add, no ESLint config to maintain and no separate lint "
             "task in CI. <code>AnalysisMode</code> — or the mode half of a compound "
             "<code>AnalysisLevel</code> such as <code>latest-recommended</code> — chooses how many rules are "
             "raised to warnings, <code>.editorconfig</code> overrides any single rule's severity, and "
             "<code>TreatWarningsAsErrors</code> decides whether a warning stops the build "
             "(" + CODEANALYSIS + "). A SonarQube-style server pass becomes a property in a shared file.</p>"
             "<p><b>The counts are worth knowing before you pick a mode.</b> Counted in the SDK's own "
             f"configuration files, <code>minimum</code> raises {CA['minimum']} CA rules to warning, "
             f"<code>recommended</code> raises {CA['recommended']} and <code>all</code> raises {CA['all']}. "
             "MotorMono sets <code>AnalysisLevel</code> to <code>latest-recommended</code>, the "
             "<code>recommended</code> mode, and the repository root turns warnings into "
             "errors, which is why no sample in this track can teach a habit the compiler dislikes. On an "
             "existing estate, go the other way: start at <code>minimum</code>, fix, raise.</p>"
             "<p><b>Formatting is the one gate that is still a separate command, and it has a portability "
             "trap.</b> " + cmd("dotnet format --verify-no-changes") + " fails the build when a file is not "
             "formatted (" + FORMAT + "). Measured on this repository, on Windows: remove "
             "<code>end_of_line = lf</code> from <code>.editorconfig</code> and the same command exits "
             f"{BREAKS['end_of_line not pinned in .editorconfig (LF files)']['exit']}, asking to replace "
             "characters with CRLF. On Linux, where the formatter's default line ending is LF, the same files "
             "pass — that half is reasoning, not a measurement. The pin only helps if the files on disk really "
             "are LF, which is the job of the sample's two-line <code>.gitattributes</code>; together they "
             "keep a green pipeline from meeting a red desk, or the reverse.</p>")},

        pcode(from_sample(EDITORCFG),
              "7.1 · The whole style configuration",
              "<b>Four decisions, and each one is load-bearing.</b> <code>end_of_line</code> pins line endings "
              "so <code>dotnet format</code> gives the same answer on every OS (7.3) — but only if the files "
              "on disk are LF, and that is the other half: <code>.gitattributes</code> holds "
              "<code>* text=auto eol=lf</code>. Without it, Git for Windows' default "
              "<code>core.autocrlf=true</code> checks CRLF files out and the same rule fails there instead "
              "(reasoning, not a measurement). The "
              "<code>csharp_style_namespace_declarations</code> rule is set to <code>:warning</code>, not "
              "<code>:suggestion</code>, so with <code>EnforceCodeStyleInBuild</code> and warnings-as-errors a "
              "block-scoped namespace is a build error — measured as "
              f"<code>{BREAKS['a block-scoped namespace under the .editorconfig rule']['code']}</code> "
              "(" + IDE0161 + "). The last section is the pattern to copy: relax a rule for a folder rather "
              "than for the repository, here letting test method names read as sentences with underscores. "
              "This file is also the only place a Gradle user needs no translation — it is the same "
              "<code>.editorconfig</code> your IDE already reads."),

        {"type": "chart", "heading": "7.2 · How many code-analysis rules each analysis mode turns on",
         "kind": "bar",
         "args": {"data": [("minimum", CA["minimum"]), ("recommended", CA["recommended"]), ("all", CA["all"])],
                  "ylabel": "CA rules at warning", "tone": "navy", "width": 500, "height": 200},
         "caption": "counted in the SDK's own analysislevel_10_<mode>.globalconfig files on the build machine, "
                    "SDK " + M["analyzers"]["sdk"],
         "note": f"<b>The jump from <code>recommended</code> to <code>all</code> is {CA['all'] - CA['recommended']} "
                 "more rules, and on an existing codebase most of them fire at once.</b> This is why "
                 "<code>AnalysisLevel</code> belongs in a shared file: one edit changes the gate for every "
                 "module, and one project can still opt out locally. MotorMono runs "
                 f"<code>{M['properties']['AnalysisLevel']}</code>, so {CA['recommended']} rules are warnings "
                 "and — because the root file treats warnings as errors — any one of them can stop the build. "
                 + MEASURED + "; the rule sets move with every SDK, so re-count rather than quote this."},

        {"type": "table", "heading": "7.3 · Every gate in this repository, and what you knew it as",
         "cols": ["Gate", "Switched on in", "Fails the build when", "You knew it as"],
         "rows": [
             ["Compiler warnings", "repo root: <code>TreatWarningsAsErrors</code>",
              "any C# or VB warning is raised", "<code>-Werror</code> · <code>tsc</code> in strict mode"],
             ["Code analysis (CA)", f"MotorMono: <code>AnalysisLevel</code> = "
                                    f"<code>{M['properties']['AnalysisLevel']}</code>",
              f"one of {CA['recommended']} rules fires", "SonarQube rules, but in-build"],
             ["Code style (IDE)", "<code>.editorconfig</code> + <code>EnforceCodeStyleInBuild</code>",
              "a rule set to <code>:warning</code> is violated — "
              f"<code>{BREAKS['a block-scoped namespace under the .editorconfig rule']['code']}</code>",
              "ktlint · ESLint rules"],
             ["Formatting", cmd("dotnet format --verify-no-changes") + " in CI, plus <code>.gitattributes</code> "
                                                                       "<code>eol=lf</code>",
              "a file is unformatted or its line endings differ from <code>end_of_line</code>",
              cmd("prettier --check") + " · <code>spotlessCheck</code>"],
             ["Restore reproducibility", "<code>RestorePackagesWithLockFile</code>, plus "
                                         "<code>RestoreLockedMode</code> when <code>CI</code> is set",
              "a version moved and the lock file did not", cmd("npm ci")],
             ["Vulnerabilities", "<code>NuGetAuditMode</code> — <code>all</code> by default on "
                                 "<code>net10.0</code>",
              "never here: the root excludes NU1901–NU1904 from errors", cmd("npm audit") + " · Dependabot"]]},

        # ═══════════════════════════ 8 · PACKAGING AND CI ═══════════════════════════
        {"type": "story", "heading": "8 · Packaging and CI — one workflow for the whole repository",
         "html": (
             "<p><b>Packing a mono-repo is one command over the solution, and the interesting decisions are "
             "about versions.</b> " + cmd("dotnet pack MotorMono.slnx") + " produces one <code>.nupkg</code> per "
             f"packable project — measured: {len(pkgs)} packages from {n_proj} projects, because test and "
             "executable projects opt out. Each project reference becomes a package dependency at the same "
             f"version, so the measured <code>{pkgs[1]['id']}</code> package depends on "
             f"<code>{pkgs[1]['dependencies'][0]}</code>. Publish one module of a set and you have published a "
             "package whose dependency does not exist on the feed yet.</p>"
             "<p><b>One property sets the version for every module.</b> <code>VersionPrefix</code> lives in "
             "<code>Directory.Build.props</code>; CI appends a suffix on ordinary builds "
             f"(<code>{pkgs[0]['version']}</code> was produced with <code>-p:VersionSuffix=ci.42</code>) and "
             "passes <code>-p:Version=</code> from the tag on a release. Order matters: a suffix is only "
             "applied when <code>Version</code> is not already set — <i>“If Version has a value and you pass a "
             "version-suffix, the value specified for the version-suffix is ignored”</i> (" + PACK + ").</p>"
             "<p><b>The workflow is ordinary GitHub Actions with three .NET-specific details.</b> "
             "<code>setup-dotnet</code> installs the SDK from the repository's own "
             "<code>global.json</code>, so the runner and every developer use one SDK, and its cache keys on "
             "the hash of the <code>packages.lock.json</code> files — the action fails outright if no lock file "
             "exists (" + SETUPDOTNET + "). GitHub sets <code>CI=true</code>, which is what flips this "
             "repository into locked restore mode. And <code>-bl</code> writes a binary log that is uploaded "
             "even when the build fails, so a red pipeline is debuggable without reproducing it.</p>")},

        pcode(from_sample(CI_YML, "build"),
              "8.1 · The build half of the workflow",
              "<b>Five commands, in the only order that works.</b> Restore first so every later step can pass "
              "<code>--no-restore</code>; format before build, because a formatting failure should be reported "
              "in seconds; build once and test with <code>--no-build</code> so the tested binaries are the "
              "built ones; pack with the same version arguments as the build. The two "
              "<code>if: github.ref_type</code> steps are the versioning rule from the story, written as "
              "environment variables rather than duplicated command lines. Note what is <i>not</i> here: no "
              "per-project steps, no matrix over modules — the solution file is the unit of work."),

        {"type": "mermaid", "inline": True,
         "heading": "8.2 · One push through the pipeline",
         "caption": "the runner reads global.json for the SDK, the lock files for the cache key, and the CI "
                    "environment variable for locked restore; only a tag reaches the feed",
         "code": ('%%{init: {"theme":"base","themeVariables": {"actorBkg":"#c7d2fe",'
                  '"actorBorder":"#6366f1","actorTextColor":"#1f2937","signalTextColor":"#1f2937",'
                  '"noteBkgColor":"#fde68a","noteTextColor":"#1f2937","noteBorderColor":"#d97706",'
                  '"activationBkgColor":"#ccfbf1","labelBoxBkgColor":"#e2e8f0","labelTextColor":"#1f2937",'
                  '"sequenceNumberColor":"#1f2937"}}}%%\n'
                  "sequenceDiagram\n"
                  "  participant D as You\n"
                  "  participant R as GitHub runner\n"
                  "  participant C as NuGet cache\n"
                  "  participant F as GitHub Packages\n"
                  "  D->>R: push to main, or a tag v1.4.2\n"
                  "  R->>R: setup-dotnet reads global.json\n"
                  "  R->>C: locked restore (CI=true) · cache key = hash of packages.lock.json\n"
                  "  R->>R: format --verify-no-changes\n"
                  "  R->>R: build -bl · test --no-build · pack\n"
                  "  R->>F: dotnet nuget push, only on a tag\n"
                  "  R-->>D: packages and build.binlog, even if red\n")},

        pcode(from_sample(CI_YML, "publish"),
              "8.3 · The publish half, and the secret that is not a secret",
              "<b><code>GITHUB_TOKEN</code> is enough to push to the repository owner's feed</b> — the "
              "workflow's <code>permissions: packages: write</code> is what grants it, and the source URL is "
              "scoped to the owner, <code>nuget.pkg.github.com/&lt;owner&gt;/index.json</code> "
              "(" + GHPKG + "). On AWS the same step becomes "
              + cmd("aws codeartifact login --tool dotnet") + " before the push, which writes a token valid for "
              "at most 12 hours into the NuGet configuration (" + CODEARTIFACT + "). Either way, add the feed "
              "to <code>nuget.config</code> <i>and</i> to <code>packageSourceMapping</code>: an unmapped second "
              "feed is the NU1507 row of 5.3 and, in a repository with private package ids, a dependency-"
              "confusion risk (" + SRCMAP + "). The <code>if: always()</code> on the artifact upload is what "
              "makes the binary log useful; treat that file as sensitive — it records the environment variables "
              "that influenced the build (" + BINLOG + ")."),

        {"type": "table", "heading": "8.4 · The packaging decisions, and what MotorMono chose",
         "cols": ["Decision", "MotorMono", "The alternative", "Why"],
         "rows": [
             ["Where the version lives", "<code>VersionPrefix</code> in "
                                         "<code>Directory.Build.props</code> — one version per repo",
              "A version per project, or a git-height tool",
              "One number to reason about; independent versions need independent release notes"],
             ["CI versions", f"<code>-p:VersionSuffix=ci.N</code> → <code>{pkgs[0]['version']}</code>, "
                             "and <code>-p:Version=</code> from the tag",
              "Only tagged builds produce packages",
              "Every build is installable, and pre-release ordering is a NuGet rule, not a convention"],
             ["What ships", f"{len(pkgs)} of {n_proj} projects; anything ending <code>.Tests</code> and the "
                             "console app opt out",
              "<code>IsPackable</code> written per project",
              "A naming convention in a shared file cannot be forgotten on a new project"],
             ["Package dependencies", f"<code>{pkgs[1]['id']}</code> → "
                                      f"<code>{pkgs[1]['dependencies'][0]}</code>, generated from the "
                                      "project reference",
              "Merge several projects into one package",
              "Publish the set together, or a consumer restores a version that is not on the feed"],
             ["Feed", "GitHub Packages, owner-scoped, <code>GITHUB_TOKEN</code>",
              "AWS CodeArtifact, Azure Artifacts, nuget.org",
              "Whatever you pick, map the ids (" + SRCMAP + ")"],
             ["Reproducibility", "<code>Deterministic</code> at the root, "
                                 "<code>ContinuousIntegrationBuild</code> when <code>CI</code> is set",
              "Default (local) builds",
              "Normalises paths in the output so two builds of one commit match"]]},

        # ═══════════════════════════ 9 · HANDS-ON ═══════════════════════════
        {"type": "story", "heading": "9 · Hands-on — drive MotorMono, then take it apart",
         "html": (
             "<p><b>Build it first, then inspect it — the second half is the part you will use at work.</b> "
             f"The whole mini mono-repo is {n_proj} projects and "
             f"{sum(v for _n, v in mod_loc)} lines of C# and Visual Basic, so every command below finishes in "
             "seconds, and the four inspection commands are exactly what you run on a repository you have "
             "never seen: what is my evaluated property, which files set it, what targets exist, and what did "
             "the build actually do.</p>"
             "<p><b>Then break it on purpose.</b> "
             + cmd("python samples/tools/measure_build.py") + " re-runs every measurement in this lesson on a "
             "temporary copy — the incremental-build table, the expanded-project line counts, the packaging "
             "results and all six deliberate failures — and rewrites "
             "<code>samples/tools/measurements.json</code>, which is where the numbers in this PDF come from. "
             "Reading that script is the fastest way to learn the diagnostic flags.</p>")},

        pcode(from_text("""
              # from the repository root: build, test and run every lesson-07 project
              python 0-script/verify_samples.py --only 7

              # from lesson-07-solutions-monorepo-build/samples/MotorMono
              dotnet build MotorMono.slnx                    # the whole graph, in dependency order
              dotnet build MotorMono.Pricing.slnf            # a filtered subset (and its references)
              dotnet test  MotorMono.slnx                    # every test project in the solution
              dotnet run --project src/L07.QuoteCli          # the console app, output in 9.2

              # inspect instead of build
              dotnet msbuild src/L07.Core -getProperty:TargetFramework      # one evaluated property
              dotnet msbuild src/L07.Pricing -pp:pp.xml                     # every import, expanded
              dotnet msbuild src/L07.Core -t:ListProjects -tl:off           # one target, by name
              dotnet build MotorMono.slnx -bl:build.binlog                  # a replayable recording

              # re-measure everything this PDF prints (works on a temporary copy)
              python lesson-07-solutions-monorepo-build/samples/tools/measure_build.py
              """, "shell"),
              "9.1 · Commands",
              "<b>The four inspection commands are the ones to memorise.</b> "
              "<code>-getProperty:</code> answers <i>what is the value</i> without a build; "
              "<code>-pp:</code> answers <i>which file set it</i>; <code>-t:</code> runs one target, so "
              "repository tooling never slows an ordinary build; <code>-bl:</code> records the build for "
              "later (" + BINLOG + "). <code>-tl:off</code> turns off the terminal logger's live display when "
              "you are capturing output."),

        pcode(from_text("""
              MotorMono CLI 1.4.0  commit 4f35a48
                projects   5
                built via  command-line

              Class1 · sum insured 850,000.00 THB · driver age 23
                base premium                        15,300.00 THB
                young driver     L07.Pricing         3,825.00 THB
                no-claim bonus   L07.Pricing.Vb     -4,590.00 THB
                net premium                         14,535.00 THB
                stamp duty 0.4%                         58.14 THB
                VAT 7%                               1,021.52 THB
                total                               15,614.66 THB
              rates are illustrative, not a real tariff
              """, "text", label="Output — dotnet run --project src/L07.QuoteCli",
                        file="captured on the build machine"),
              "9.2 · What you should see",
              "<b>Every line of the header came from the build, not from the source.</b> The version is "
              "<code>VersionPrefix</code>; the commit is stamped into "
              "<code>AssemblyInformationalVersion</code> because the SDK has shipped Source Link since .NET 8 "
              "(" + SOURCELINK + "), so yours will differ from the one above; <code>projects 5</code> and "
              "<code>built via command-line</code> are the <code>AssemblyMetadata</code> items that "
              "<code>StampBuildFacts</code> wrote in 3.4 — run the app from an IDE and the last line reads "
              "<code>IDE</code>, because only the command line reads <code>Directory.Build.rsp</code>. The "
              "third column names the <i>module</i> each rating rule was compiled into: the mixed-language "
              "graph of 6.1 printing itself."),

        {"type": "chart", "heading": "9.3 · Lines of code per module", "kind": "hbar",
         "args": {"data": mod_loc, "labelw": 150, "tone": "violet", "width": 560},
         "caption": "non-blank, non-comment lines of C# and Visual Basic, measured from the sample files when "
                    "this PDF was built",
         "note": f"<b>{sum(v for _n, v in mod_loc)} lines of code, and everything in this lesson is about the "
                 f"{PP['project_file_lines']}-line project files and the {dir_lines} lines of "
                 "<code>Directory.*</code> around them.</b> That ratio is the honest reason build engineering "
                 "is a discipline in a mono-repo: the shared files are small, they apply everywhere, and they "
                 "are the only code in the repository with no tests. " + MEASURED + " — the counts change as "
                 "the samples change, and the point does not."},

        figure_heading("9.4 · What carries over from Gradle, what to learn, what to unlearn"),
        {"type": "threecol", "boxes": [
            {"heading": "Carries over unchanged", "tone": "teal",
             "items": ["Convention over per-module configuration",
                       "One version source for the whole repository",
                       "Lock files committed, enforced only in CI",
                       "Quality gates inside the build, not beside it",
                       "Keeping widely referenced modules small"]},
            {"heading": "Learn fresh", "tone": "indigo",
             "items": ["Evaluation before execution, and the six ordered passes",
                       "Nearest-file import, and chaining to the parent by hand",
                       "Reference assemblies, and what they let the build skip",
                       "<code>InternalsVisibleTo</code> as a build-cost decision",
                       "<code>-pp</code>, <code>-getProperty</code>, <code>-t:</code>, <code>-bl</code>"]},
            {"heading": "Unlearn", "tone": "rose",
             "items": ["“The solution file configures the build” — it is an index",
                       "“A solution filter isolates a subgraph” — it builds references too",
                       "“An internal change is always cheap”",
                       "“The project file tells me how this module builds”",
                       "“A version catalog and central package management are the same thing”"]}]},

        {"type": "callout", "variant": "warn", "heading": "⚠ Traps",
         "items": [
             "<b>Only the nearest <code>Directory.Build.props</code> is imported.</b> Add one in a subfolder "
             "and everything the root file set stops applying below it, with no warning — the samples fail with "
             f"<code>{BREAKS['nested Directory.Build.props without the parent Import']['code']}</code> when the "
             "hand-written <code>Import</code> is removed (4.3). The same first-hit-wins rule applies to "
             "<code>Directory.Packages.props</code> and <code>Directory.Build.targets</code> "
             "(" + BYDIR + " · " + CPM + ").",
             "<b>Granting test access to internals makes internal changes expensive.</b> "
             "<code>InternalsVisibleTo</code> keeps internal members in the reference assembly, so an internal "
             f"edit in <code>L07.Pricing</code> recompiles {pricing_internal} projects where the same edit in "
             f"<code>L07.Core</code> recompiles {core_internal} (6.2). Prefer testing through the public "
             "surface on the projects everything depends on (" + REFASM + ").",
             "<b>A solution filter is not a build boundary.</b> "
             f"<code>MotorMono.Pricing.slnf</code> lists {len(filt['listed'])} projects and "
             f"{len(filt['built'])} are built, because MSBuild follows references out of the filter "
             "(" + FILTERS + "). Use it to make an IDE open faster, not to prove a subsystem builds alone.",
             "<b>A version catalog is not central package management.</b> Gradle's catalog declares the "
             "versions you request and a <code>platform</code> enforces them (" + CATALOGS + "); CPM with "
             "<code>CentralPackageTransitivePinningEnabled</code> does both — and when you pack, a pinned "
             "transitive becomes an explicit dependency of your package, which quietly widens a published "
             "library's contract (" + CPM + ").",
             "<b>Pin <code>end_of_line</code>, make the disk agree, and treat <code>build.binlog</code> as "
             "sensitive.</b> Without <code>end_of_line = lf</code>, "
             + cmd("dotnet format --verify-no-changes") + " exits "
             f"{BREAKS['end_of_line not pinned in .editorconfig (LF files)']['exit']} on Windows over LF files "
             "(measured; the Linux pass is reasoning). With it but without <code>.gitattributes</code> "
             "<code>eol=lf</code>, a CRLF checkout fails the rule the other way. And "
             "a binary log records the environment variables that influenced the build, so an uploaded artifact "
             "can leak more than you meant — do not set "
             "<code>MSBUILDLOGALLENVIRONMENTVARIABLES</code> in CI (" + BINLOG + ")."]},

        {"type": "callout", "variant": "ok", "heading": "✔ Checkpoint — you are ready for lesson 08 when",
         "items": [
             f"<code>python 0-script/verify_samples.py --only 7</code> reports {n_proj}/{n_proj} passed, and "
             f"<code>python .../tools/measure_build.py</code> reproduces the {len(M['incremental'])} "
             "incremental-build rows on your machine.",
             "You can name every <code>Directory.*</code> file in the samples, say when it is imported and "
             "give one thing that belongs in it and one that does not.",
             "Given an edit to a project in a mono-repo, you can predict which projects recompile — including "
             "the case where an internal change behaves like a public one.",
             "You can take a repository with per-project package versions and no lock files and write the "
             "three-file change that centralises the versions, pins transitives and fails CI on drift."]},

        {"type": "callout", "variant": "summary", "heading": "🔍 Check yourself", "_keep_with_next": True,
         "items": [
             "A project sets a property in its <code>.csproj</code> and a "
             "<code>Directory.Build.targets</code> above it sets the same property. Which value does the build "
             "use, and why is the answer different for <code>Directory.Build.props</code>?",
             f"A {PP['project_file_lines']}-line project file evaluates to {PP['preprocessed_lines']:,} lines. "
             "Which command shows you that document, and what is the first thing you search it for?",
             "Why does adding an internal member to one project recompile one project, and adding an internal "
             "member to another recompile three?",
             "<code>dotnet build MyFilter.slnf</code> builds a project the filter does not list. Is that a bug, "
             "and what would actually keep that project out of the build?",
             "Under central package management, what happens if a <code>PackageReference</code> keeps its "
             "<code>Version</code> attribute — and what happens to your published package's dependencies if you "
             "pin a transitive version?",
             "Your CI passes <code>-p:Version=1.4.2</code> and <code>-p:VersionSuffix=rc.1</code>. What version "
             "ships, and why?",
             "Which two files make <code>dotnet build</code> on a developer machine and in Visual Studio behave "
             "differently, and how would you notice?"]},

        {"type": "footer",
         "html": ("<b>Lesson 07 in one line:</b> a .NET mono-repo keeps its build above the projects — the "
                  "solution file is only an index, <code>Directory.Build.props</code> applies to everything "
                  "below it <i>until the next one shadows it</i>, <code>Directory.Packages.props</code> owns "
                  "every version and pins transitives, and reference assemblies make the incremental cost of a "
                  f"change predictable: {core_internal} project for an internal edit, {public_edit} for a "
                  "public one. Analyzers, <code>dotnet format</code> and a lock file are properties in a shared "
                  "file, and one workflow packs the whole repository."
                  "<br/><b>Next:</b> " + ref(8) + " — the framework those projects exist to build.")},
    ]
