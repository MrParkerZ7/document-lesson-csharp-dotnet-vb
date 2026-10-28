# -*- coding: utf-8 -*-
"""Captures the MEASURED figures lesson 13 prints: the real output of the four sample projects, the
allocation table of L13.PerfLab, the test count, and the size of every file Visual Studio reads.

Run from the repository root with the .NET 10 SDK on PATH:
    python lesson-13-visual-studio-workflows/samples/tools/capture.py
It writes measurements.json next to itself. Nothing here needs Visual Studio."""
import json
import pathlib
import re
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
SAMPLES = HERE.parent
REPO = SAMPLES.parents[1]


def run(*args):
    p = subprocess.run(["dotnet", *args], cwd=REPO, capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    return p.returncode, p.stdout + p.stderr


def rel(p):
    return (SAMPLES / p).relative_to(REPO).as_posix()


def console(project, *extra, config="Release"):
    code, out = run("run", "--project", rel(project), "-c", config, "--no-launch-profile", *extra)
    assert code == 0, out
    return [ln for ln in out.splitlines() if ln.strip()]


def perf_table(lines):
    """Parse the four data rows of L13.PerfLab's table into {name: {calls, bytes, per_quote}}."""
    table = {}
    for ln in lines[2:6]:
        m = re.match(r"(.+?)\s{2,}(\d+)\s+([\d,]+)\s+([\d,]+)$", ln)
        table[m.group(1).strip()] = {"calls": int(m.group(2)), "bytes": int(m.group(3).replace(",", "")),
                                     "per_quote": int(m.group(4).replace(",", ""))}
    return table


def style_probe():
    """MEASURED: a block-scoped namespace against samples/.editorconfig (file_scoped:warning). The probe file
    is written, built twice and always deleted. Without EnforceCodeStyleInBuild the IDE-style rule is not
    evaluated by dotnet build; with it (samples/Directory.Build.props) the build fails on IDE0161."""
    probe = SAMPLES / "L13.DebugLab" / "_ProbeBlock.cs"
    project = rel("L13.DebugLab/L13.DebugLab.csproj")
    probe.write_text("namespace L13.DebugLab { public static class ProbeBlock { public static int One() => 1; } }"
                     + chr(10), encoding="utf-8")
    try:
        c_on, o_on = run("build", project, "--no-incremental", "-nologo")
        c_off, o_off = run("build", project, "--no-incremental", "-nologo", "-p:EnforceCodeStyleInBuild=false")
    finally:
        probe.unlink()
    assert c_on != 0 and "IDE0161" in o_on, o_on[-600:]
    assert c_off == 0, o_off[-600:]
    return {"with_enforce": "error IDE0161", "without_enforce": "Build succeeded"}


def lines_of(path):
    return len((SAMPLES / path).read_text(encoding="utf-8").splitlines())


def main():
    for proj in ("L13.DebugLab/L13.DebugLab.csproj", "L13.DebugLabVb/L13.DebugLabVb.vbproj",
                 "L13.PerfLab/L13.PerfLab.csproj", "L13.DebugLab.Tests/L13.DebugLab.Tests.csproj"):
        assert run("build", rel(proj), "-c", "Release", "-nologo")[0] == 0, proj

    cs = console("L13.DebugLab/L13.DebugLab.csproj")
    vb = console("L13.DebugLabVb/L13.DebugLabVb.vbproj")
    show137 = console("L13.DebugLab/L13.DebugLab.csproj", "--show", "137")
    show47 = console("L13.DebugLab/L13.DebugLab.csproj", "--show", "47")
    _c, lp_out = run("run", "--project", rel("L13.DebugLab/L13.DebugLab.csproj"), "-c", "Release", "--no-build",
                     "-lp", "Show quote 137")
    assert _c == 0, lp_out
    lp137 = [ln for ln in lp_out.splitlines() if ln.strip()]
    perf_raw = console("L13.PerfLab/L13.PerfLab.csproj")
    perf = perf_table(perf_raw)
    # the figures are bytes, not time: the same on every run of the same configuration on the same runtime
    again = console("L13.PerfLab/L13.PerfLab.csproj")
    assert again == perf_raw, "PerfLab output is not deterministic"
    # ...but not the same in Debug: allocation depends on the configuration, so the lesson names Release
    perf_debug = perf_table(console("L13.PerfLab/L13.PerfLab.csproj", config="Debug"))

    code, out = run("test", rel("L13.DebugLab.Tests/L13.DebugLab.Tests.csproj"), "-c", "Release", "-nologo")
    m = re.search(r"Passed!.*Passed:\s*(\d+).*Total:\s*(\d+)", out)
    assert code == 0 and m, out[-800:]

    traits = {}
    for cat in ("Tariff", "Batch", "Environment"):
        c2, o2 = run("test", rel("L13.DebugLab.Tests/L13.DebugLab.Tests.csproj"), "-c", "Release", "--no-build",
                     "--filter", f"Category={cat}")
        m2 = re.search(r"Passed!.*Total:\s*(\d+)", o2)
        assert c2 == 0 and m2, o2[-600:]
        traits[cat] = int(m2.group(1))

    probe = style_probe()

    files = ["L13.slnx", "Directory.Build.props", ".vsconfig", ".editorconfig", ".runsettings",
             "L13.DebugLab/Properties/launchSettings.json", "L13.DebugLab/L13.DebugLab.csproj",
             "L13.DebugLabVb/L13.DebugLabVb.vbproj", "L13.DebugLab.Tests/L13.DebugLab.Tests.csproj",
             "L13.PerfLab/L13.PerfLab.csproj"]
    data = {"debuglab_cs": cs, "debuglab_vb": vb, "show_137": show137, "show_47": show47, "launch_profile_137": lp137,
            "perflab": perf, "perflab_raw": perf_raw, "perflab_debug": perf_debug, "style_probe": probe,
            "tests": {"passed": int(m.group(1)), "total": int(m.group(2)), "by_trait": traits},
            "config_files": [{"file": f, "lines": lines_of(f)} for f in files]}
    (HERE / "measurements.json").write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: data[k] for k in ("perflab", "perflab_debug", "style_probe", "tests")}, indent=1))


if __name__ == "__main__":
    main()
