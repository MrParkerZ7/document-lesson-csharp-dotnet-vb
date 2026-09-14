#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_samples.py — prove the code in the lesson PDFs is real: build every sample project, run every
test project, and run every console sample to completion.

    python 0-script/verify_samples.py              # all lessons
    python 0-script/verify_samples.py --only 5 6   # lessons 05 and 06

Finds lesson-*/samples/**/*.csproj|*.vbproj. For each project:
  * test project (references Microsoft.NET.Test.Sdk or sets IsTestProject) -> `dotnet test`
  * web project (Sdk="Microsoft.NET.Sdk.Web")                              -> `dotnet build` only
  * console project (OutputType Exe)                                       -> `dotnet build` + `dotnet run`
  * library                                                                 -> `dotnet build`
Exit code 1 if anything fails. SDK: $DOTNET_EXE, else $DOTNET_ROOT/dotnet(.exe), else `dotnet` on PATH
(the SDK version is pinned by global.json at the repo root).
"""
import argparse
import os
import pathlib
import shutil
import subprocess
import sys
import time

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.stdout.reconfigure(encoding="utf-8")


def dotnet_exe():
    if os.environ.get("DOTNET_EXE"):
        return os.environ["DOTNET_EXE"]
    root = os.environ.get("DOTNET_ROOT")
    if root:
        for name in ("dotnet.exe", "dotnet"):
            if (pathlib.Path(root) / name).exists():
                return str(pathlib.Path(root) / name)
    return shutil.which("dotnet") or "dotnet"


def classify(proj):
    text = proj.read_text(encoding="utf-8-sig")
    if "Microsoft.NET.Test.Sdk" in text or "<IsTestProject>true" in text:
        return "test"
    if "Microsoft.NET.Sdk.Web" in text:
        return "web"
    if "<OutputType>Exe</OutputType>" in text:
        return "console"
    return "library"


ENV = dict(os.environ,
           DOTNET_NOLOGO="1", DOTNET_CLI_TELEMETRY_OPTOUT="1", DOTNET_SKIP_FIRST_TIME_EXPERIENCE="1",
           # several lessons may verify at once: no long-lived MSBuild nodes holding files between builds
           MSBUILDDISABLENODEREUSE="1")


def run(cmd, timeout=600):
    t = time.time()
    try:
        p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=timeout, env=ENV)
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or "") + (e.stderr or "")
        if isinstance(out, bytes):
            out = out.decode("utf-8", "replace")
        return 124, out + f"\nTIMEOUT after {timeout}s (a console sample must exit on its own)", time.time() - t
    return p.returncode, (p.stdout + p.stderr), time.time() - t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", type=int)
    args = ap.parse_args()
    dn = dotnet_exe()
    code, out, _ = run([dn, "--version"], 60)
    print(f"dotnet SDK {out.strip()}  ({dn})")
    projs = sorted(p for p in REPO.glob("lesson-*/samples/**/*") if p.suffix in (".csproj", ".vbproj"))
    if args.only:
        projs = [p for p in projs if int(p.relative_to(REPO).parts[0].split("-")[1]) in args.only]
    failures = []
    for proj in projs:
        rel = proj.relative_to(REPO).as_posix()
        kind = classify(proj)
        if kind == "test":
            steps = [[dn, "test", rel, "-c", "Release", "-nologo"]]
        elif kind == "console":
            steps = [[dn, "build", rel, "-c", "Release", "-nologo"],
                     [dn, "run", "--project", rel, "-c", "Release", "--no-build", "--no-launch-profile"]]
        else:
            steps = [[dn, "build", rel, "-c", "Release", "-nologo"]]
        ok, secs, tail = True, 0.0, ""
        for cmd in steps:
            c, o, s = run(cmd)
            secs += s
            if c != 0:
                ok, tail = False, o[-2500:]
                break
        print(f"{'PASS' if ok else 'FAIL'}  {kind:8s} {secs:6.1f}s  {rel}")
        if not ok:
            failures.append(rel)
            print(tail)
    print(f"\n{len(projs) - len(failures)}/{len(projs)} sample projects passed")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
