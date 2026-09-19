#!/usr/bin/env python3
"""
measure_build.py - produce the MEASURED build figures that lesson 07 prints, and save them to
measurements.json beside this script (the lesson module reads that file; it never runs dotnet itself).

    python lesson-07-solutions-monorepo-build/samples/tools/measure_build.py

Works on temporary COPIES of samples/MotorMono (plus the repository-root Directory.Build.props and
global.json), so it never touches the shared .build/artifacts folder. It records:

  incremental      which projects re-run the compiler (CoreCompile) after each kind of edit
  preprocess       what `dotnet msbuild -pp` expands one 5-line project file into: lines by origin
                   (project file, Directory.* files, restore output, .NET SDK) and the import chain
  properties       the evaluated value of a few properties (`dotnet msbuild -getProperty`)
  list_projects    the console output of the custom ListProjects target
  solution_filter  the projects a solution filter lists vs the projects `dotnet build <filter>` builds
  solution_formats the same five projects in a classic .sln vs .slnx, and what `dotnet new sln` creates
  ci               the steps of samples/ci/build.yml run locally with CI=true: exit codes, test total,
                   the packages `dotnet pack` produced and their dependencies
  breaks           the first error a deliberately broken build reports
  analyzers        how many CA rules each AnalysisMode raises to a warning, counted in the SDK's own
                   analysislevel_10_<mode>.globalconfig files

SDK: $DOTNET_EXE, else $DOTNET_ROOT/dotnet(.exe), else `dotnet` on PATH.
"""
import datetime
import json
import os
import pathlib
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

HERE = pathlib.Path(__file__).resolve().parent
SAMPLES = HERE.parent
REPO = SAMPLES.parents[1]
OUT = HERE / "measurements.json"
sys.stdout.reconfigure(encoding="utf-8")

PARENT_IMPORT = ("  <Import Project=\"$([MSBuild]::GetPathOfFileAbove('Directory.Build.props',\n"
                 "                                                   '$(MSBuildThisFileDirectory)../'))\" />\n")
PROJECTS = ["src/L07.Core/L07.Core.csproj", "src/L07.Pricing/L07.Pricing.csproj",
            "src/L07.Pricing.Vb/L07.Pricing.Vb.vbproj", "src/L07.QuoteCli/L07.QuoteCli.csproj",
            "tests/L07.Pricing.Tests/L07.Pricing.Tests.csproj"]


def dotnet_exe():
    if os.environ.get("DOTNET_EXE"):
        return os.environ["DOTNET_EXE"]
    root = os.environ.get("DOTNET_ROOT")
    if root:
        for name in ("dotnet.exe", "dotnet"):
            if (pathlib.Path(root) / name).exists():
                return str(pathlib.Path(root) / name)
    return shutil.which("dotnet") or "dotnet"


DOTNET = dotnet_exe()
ENV = dict(os.environ, DOTNET_NOLOGO="1", DOTNET_CLI_TELEMETRY_OPTOUT="1", MSBUILDDISABLENODEREUSE="1")
ENV.pop("CI", None)


def run(args, cwd, env=None):
    p = subprocess.run([DOTNET, *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=env or ENV)
    return p.returncode, p.stdout + p.stderr


def fresh_copy(parent):
    if parent.exists():
        shutil.rmtree(parent)
    parent.mkdir(parents=True)
    shutil.copy(REPO / "Directory.Build.props", parent)
    shutil.copy(REPO / "global.json", parent)
    shutil.copytree(SAMPLES / "MotorMono", parent / "MotorMono",
                    ignore=shutil.ignore_patterns("bin", "obj"))
    return parent / "MotorMono"


def edit(mono, rel, old, new):
    p = mono / rel
    with open(p, encoding="utf-8", newline="") as f:
        text = f.read()
    if old not in text:
        raise SystemExit(f"edit target not found in {rel}: {old!r}")
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(text.replace(old, new, 1))


def compiled_projects(log):
    """Projects whose CoreCompile target ran its compiler task (serial -m:1 detailed log)."""
    compiled, current = set(), None
    for ln in log.splitlines():
        m = re.search(r'Target "CoreCompile" in file ".*?" from project "([^"]+)"', ln)
        if m:
            current = pathlib.PurePath(m.group(1).replace("\\", "/")).stem
        elif current and "Skipping target \"CoreCompile\"" in ln:
            current = None
        elif current and re.search(r'Task "(Csc|Vbc)"', ln):
            compiled.add(current)
            current = None
    return sorted(compiled)


def incremental(mono):
    steps = [
        ("clean build", None),
        ("no change", None),
        ("method body in L07.Core", ("src/L07.Core/Money.cs", "Cannot add {other.Currency} to",
                                     "Cannot add {other.Currency} money to")),
        ("internal member in L07.Core", ("src/L07.Core/Money.cs", "    public Money Times(",
                                         "    internal Money Half() => Times(0.5m);\n\n    public Money Times(")),
        ("internal member in L07.Pricing", ("src/L07.Pricing/Internals.cs",
                                            "internal static class Taxes\n{\n",
                                            "internal static class Taxes\n{\n"
                                            "    internal static decimal None() => 0m;\n\n")),
        ("public member in L07.Core", ("src/L07.Core/Money.cs", "    public Money Times(",
                                       "    public Money Negated() => Times(-1m);\n\n    public Money Times(")),
    ]
    rows = []
    for label, change in steps:
        if change:
            edit(mono, *change)
        code, log = run(["build", "MotorMono.slnx", "-tl:off", "-v:d", "-m:1", "-nologo"], mono)
        if code != 0:
            raise SystemExit(f"incremental step {label!r} failed:\n{log[-3000:]}")
        rows.append({"scenario": label, "compiled": compiled_projects(log)})
        print(f"  {label:32s} {len(rows[-1]['compiled'])} compiled  {rows[-1]['compiled']}")
    return rows


_BANNER = re.compile(r"^={100,}$")
_PATH = re.compile(r"^(?:[A-Za-z]:\\|/).+\.(?:\w*proj|props|targets)$")


def preprocess(mono, work):
    """Expand src/L07.Pricing with -pp and attribute every line to the file it came from.

    -pp marks each import with a banner wrapped in an XML comment: a line of 100+ '=' characters,
    `<Import ...>` (entering) or `</Import>` (returning), the resolved path, and another line of '='.
    Every banner names the file the lines that follow it belong to: the imported file when entering, the importing file when
    returning. One `</Import>` banner can close several nested imports at once, so a stack of paths
    would go stale; tracking only the current file cannot. The banner lines themselves belong to no
    file, so they are counted apart (`banner_lines`) and the origins plus the banners add up to the
    total."""
    out = work / "pp.xml"
    code, log = run(["msbuild", "src/L07.Pricing", f"-pp:{out}", "-nologo"], mono)
    if code != 0:
        raise SystemExit(f"preprocess failed:\n{log[-2000:]}")
    lines = out.read_text(encoding="utf-8", errors="replace").splitlines()
    root = str(mono.parent).lower()

    def category(path):
        low, name = path.lower(), path.replace("\\", "/").split("/")[-1]
        if name == "L07.Pricing.csproj":
            return "your project file"
        if name.startswith("Directory."):
            return "Directory.* files"
        if low.startswith(root) and ".nuget.g." in low:
            return "restore output (nuget.g)"
        if ".nuget" + os.sep + "packages" in low or "/.nuget/packages/" in low:
            return "NuGet package build files"
        return ".NET SDK and MSBuild"

    def label(path):
        name = path.replace("\\", "/").split("/")[-1]
        if name.startswith("Directory."):
            return ("MotorMono/" if "motormono" in path.lower() else "repo root/") + name
        return name

    cur, per_cat, files, chain, banner_lines, i = None, {}, set(), [], 0, 0
    while i < len(lines):
        top = i + 1 if lines[i].strip() == "<!--" and i + 1 < len(lines) else i   # the comment wrapper
        if _BANNER.match(lines[top].strip()):
            j = top + 1
            while j < len(lines) and not _BANNER.match(lines[j].strip()):
                j += 1
            end = j + 1 if j + 1 < len(lines) and lines[j + 1].strip() == "-->" else j
            banner_lines += end - i + 1
            block = [b.strip() for b in lines[top + 1:j] if b.strip()]
            path = block[-1] if block and _PATH.match(block[-1]) else None
            if path:
                if cur is not None and not block[0].startswith("</Import>"):   # entering an imported file
                    if category(path) == "Directory.* files":
                        chain.append({"file": label(path), "imported_by": label(cur)})
                cur = path                                     # entering, returning or the project itself
                files.add(path.lower())
            i = end + 1
            continue
        if cur:
            c = category(cur)
            per_cat[c] = per_cat.get(c, 0) + 1
        i += 1
    project_lines = len((mono / "src/L07.Pricing/L07.Pricing.csproj").read_text(encoding="utf-8").splitlines())
    print(f"  preprocessed L07.Pricing: {len(lines)} lines in {len(files)} files; {per_cat}")
    print(f"  Directory.* chain: {chain}")
    return {"project": "src/L07.Pricing/L07.Pricing.csproj", "project_file_lines": project_lines,
            "preprocessed_lines": len(lines), "files": len(files), "lines_by_origin": per_cat,
            "banner_lines": banner_lines, "directory_chain": chain}


def properties(mono):
    names = ["TargetFramework", "Nullable", "UseArtifactsOutput", "AnalysisLevel", "MotorMonoBuiltFrom",
             "NuGetAuditMode", "RestoreEnablePackagePruning", "ProduceReferenceAssembly"]
    code, out = run(["msbuild", "src/L07.Core", *[f"-getProperty:{n}" for n in names], "-nologo"], mono)
    start = out.find("{")
    data = json.loads(out[start:])["Properties"] if code == 0 and start >= 0 else {}
    print(f"  properties {data}")
    return data


def list_projects(mono):
    code, out = run(["msbuild", "src/L07.Core", "-t:ListProjects", "-nologo", "-tl:off"], mono)
    lines = [ln.rstrip() for ln in out.splitlines() if ln.strip()]
    print("  ListProjects:", lines)
    return lines


def solution_filter(mono):
    listed = json.loads((mono / "MotorMono.Pricing.slnf").read_text(encoding="utf-8"))["solution"]["projects"]
    listed = sorted(pathlib.PurePath(p.replace("\\", "/")).stem for p in listed)
    code, out = run(["build", "MotorMono.Pricing.slnf", "-tl:off", "-nologo", "-m:1"], mono)
    built = sorted({m.group(1) for m in re.finditer(r"^\s+(L07\.[\w.]+) -> ", out, re.M)})
    print(f"  solution filter lists {listed}, build produced {built}")
    return {"filter": "MotorMono.Pricing.slnf", "listed": listed, "built": built, "exit": code}


def solution_formats(work):
    """The five MotorMono projects in a classic .sln made by the CLI, that .sln migrated to .slnx, and
    the hand-written MotorMono.slnx; plus the file `dotnet new sln` creates with no --format."""
    mono = fresh_copy(work / "formats")
    steps = [["new", "sln", "--format", "sln", "-n", "Legacy"], ["sln", "Legacy.sln", "add", *PROJECTS],
             ["sln", "Legacy.sln", "migrate"]]
    for args in steps:
        code, out = run(args, mono)
        if code != 0:
            raise SystemExit(f"dotnet {' '.join(args)} failed:\n{out[-2000:]}")

    def stats(name):
        text = (mono / name).read_text(encoding="utf-8-sig")
        guids = set(re.findall(r"[0-9A-Fa-f]{8}-(?:[0-9A-Fa-f]{4}-){3}[0-9A-Fa-f]{12}", text))
        return {"file": name, "lines": len(text.splitlines()), "chars": len(text), "guids": len(guids)}

    probe = work / "probe"
    probe.mkdir()
    code, out = run(["new", "sln", "-n", "Probe"], probe)
    created = sorted(p.name for p in probe.iterdir())
    rows = [stats("Legacy.sln"), stats("Legacy.slnx"), stats("MotorMono.slnx")]
    print(f"  solution formats {rows}; dotnet new sln created {created}")
    return {"files": rows, "new_sln_creates": created}


def ci(work):
    """Run the steps of samples/ci/build.yml on a fresh copy, with CI=true as GitHub Actions sets it."""
    mono = fresh_copy(work / "ci")
    env = dict(ENV, CI="true")
    version = ["-p:VersionSuffix=ci.42"]
    steps = [("restore", ["restore", "MotorMono.slnx"]),
             ("format", ["format", "MotorMono.slnx", "--verify-no-changes", "--no-restore"]),
             ("build", ["build", "MotorMono.slnx", "-c", "Release", "--no-restore", *version, "-bl:build.binlog"]),
             ("test", ["test", "MotorMono.slnx", "-c", "Release", "--no-build"]),
             ("pack", ["pack", "MotorMono.slnx", "-c", "Release", "--no-build", *version, "-o", "packages"])]
    rows, tests = [], None
    for name, args in steps:
        code, out = run(args, mono, env)
        rows.append({"step": name, "command": "dotnet " + " ".join(args), "exit": code})
        if name == "test":
            m = re.search(r"Total:\s+(\d+)", out)
            tests = int(m.group(1)) if m else None
        if code != 0:
            print(out[-3000:])
            break
    packages = []
    for nupkg in sorted((mono / "packages").glob("*.nupkg")):
        with zipfile.ZipFile(nupkg) as z:
            nuspec = z.read(next(n for n in z.namelist() if n.endswith(".nuspec"))).decode("utf-8-sig")
            libs = sorted(n for n in z.namelist() if n.startswith("lib/"))
        packages.append({"id": re.search(r"<id>(.*?)</id>", nuspec).group(1),
                         "version": re.search(r"<version>(.*?)</version>", nuspec).group(1),
                         "dependencies": [f"{a} {b}" for a, b in
                                          re.findall(r'<dependency id="([^"]+)" version="([^"]+)"', nuspec)],
                         "lib": libs})
    binlog = mono / "build.binlog"
    result = {"steps": rows, "tests_total": tests, "packages": packages,
              "binlog_kb": round(binlog.stat().st_size / 1024) if binlog.exists() else None}
    print(f"  ci steps {[(r['step'], r['exit']) for r in rows]}, tests {tests}, "
          f"packages {[(p['id'], p['version'], p['dependencies']) for p in packages]}")
    return result


def first_error(log):
    """The first error line: code and message, without the trailing [project path]."""
    for ln in log.splitlines():
        m = re.search(r"\berror ([A-Z]+\d*): (.+)$", ln)
        if m:
            msg = re.sub(r"\s*\[[^\[\]]*[\\/][^\[\]]*\]\s*$", "", m.group(2)).strip()
            return {"code": m.group(1), "message": msg}
    return {"code": None, "message": None}


def breaks(work):
    rows = []

    mono = fresh_copy(work / "b1")
    edit(mono, "Directory.Build.props", PARENT_IMPORT, "")
    code, log = run(["build", "src/L07.Core", "-tl:off", "-nologo"], mono)
    rows.append({"break": "nested Directory.Build.props without the parent Import", "exit": code, **first_error(log)})

    mono = fresh_copy(work / "b2")
    run(["restore", "MotorMono.slnx", "-tl:off"], mono)
    edit(mono, "Directory.Packages.props", 'Include="xunit" Version="2.9.3"', 'Include="xunit" Version="2.9.2"')
    code, log = run(["restore", "MotorMono.slnx", "-tl:off"], mono, dict(ENV, CI="true"))
    rows.append({"break": "CI=true and a version changed without updating the lock file", "exit": code,
                 **first_error(log)})

    mono = fresh_copy(work / "b3")
    edit(mono, "tests/L07.Pricing.Tests/L07.Pricing.Tests.csproj",
         '<PackageReference Include="xunit" />', '<PackageReference Include="xunit" Version="2.9.3" />')
    code, log = run(["restore", "MotorMono.slnx", "-tl:off"], mono)
    rows.append({"break": "a Version attribute left on a PackageReference under CPM", "exit": code,
                 **first_error(log)})

    mono = fresh_copy(work / "b4")
    # NU1507 counts HTTP sources only: a local folder feed would not trigger it
    edit(mono, "nuget.config", '    <add key="nuget.org" value="https://api.nuget.org/v3/index.json" />\n',
         '    <add key="nuget.org" value="https://api.nuget.org/v3/index.json" />\n'
         '    <add key="second" value="https://data.nuget.org/v3/index.json" />\n')
    text = (mono / "nuget.config").read_text(encoding="utf-8")
    (mono / "nuget.config").write_text(re.sub(r"\s*<packageSourceMapping>.*</packageSourceMapping>", "", text,
                                              flags=re.S), encoding="utf-8", newline="")
    code, log = run(["restore", "MotorMono.slnx", "-tl:off"], mono)
    rows.append({"break": "a second package source and no packageSourceMapping", "exit": code, **first_error(log)})

    mono = fresh_copy(work / "b5")
    edit(mono, ".editorconfig", "end_of_line = lf\n", "")
    code, log = run(["format", "whitespace", "MotorMono.slnx", "--verify-no-changes"], mono)
    rows.append({"break": "end_of_line not pinned in .editorconfig (LF files)", "exit": code,
                 "platform": platform.system(), **first_error(log)})

    mono = fresh_copy(work / "b6")
    edit(mono, "src/L07.Core/Money.cs", "namespace L07.Core;\n", "namespace L07.Core\n{\n")
    with open(mono / "src/L07.Core/Money.cs", "a", encoding="utf-8", newline="") as f:
        f.write("}\n")
    code, log = run(["build", "src/L07.Core", "-tl:off", "-nologo"], mono)
    rows.append({"break": "a block-scoped namespace under the .editorconfig rule", "exit": code, **first_error(log)})

    for r in rows:
        print(f"  {r['break']:62s} exit {r['exit']}  {r['code']}  {r['message']}")
    return rows


def analyzers():
    code, out = run(["--version"], REPO)
    sdk = out.strip().splitlines()[-1]
    config = pathlib.Path(DOTNET).parent / "sdk" / sdk / "Sdks" / "Microsoft.NET.Sdk" / "analyzers" / "build" / "config"
    counts = {}
    for mode in ("minimum", "recommended", "all"):
        text = (config / f"analysislevel_10_{mode}.globalconfig").read_text(encoding="utf-8")
        counts[mode] = len(re.findall(r"^dotnet_diagnostic\.CA\d+\.severity = warning", text, re.M))
    print(f"  CA rules at warning: {counts}")
    return {"sdk": sdk, "counts": counts}


def main():
    code, out = run(["--version"], REPO)
    sdk = out.strip().splitlines()[-1]
    code, msb = run(["msbuild", "-version", "-nologo"], REPO)
    work = pathlib.Path(tempfile.mkdtemp(prefix="l07-measure-"))
    try:
        mono = fresh_copy(work / "main")
        print("incremental builds")
        inc = incremental(mono)
        print("evaluation")
        pp = preprocess(mono, work)
        props = properties(mono)
        lp = list_projects(mono)
        print("solutions")
        slnf = solution_filter(fresh_copy(work / "filter"))
        formats = solution_formats(work)
        print("ci workflow steps")
        pipeline = ci(work)
        print("broken builds")
        brk = breaks(work)
        print("analyzer modes")
        ana = analyzers()
    finally:
        shutil.rmtree(work, ignore_errors=True)
    projects = sorted(p.stem for p in (SAMPLES / "MotorMono").glob("*/*/*.*proj"))
    data = {"measured_on": datetime.date.today().isoformat(), "sdk": sdk,
            "msbuild": msb.strip().splitlines()[-1], "os": platform.system(), "projects": projects,
            "incremental": inc, "preprocess": pp, "properties": props, "list_projects": lp,
            "solution_filter": slnf, "solution_formats": formats, "ci": pipeline, "breaks": brk,
            "analyzers": ana}
    OUT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(REPO).as_posix()}")


if __name__ == "__main__":
    main()
