#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_tariff.py — guard the canonical MotorQuote tariff.

    python 0-script/check_tariff.py

The running example prices the same quote in nine lessons. The numbers are defined once, in
1-analysis/spec_lesson-pdfs/_curriculum.md (section "Canonical tariff"), and this script reads the
base rates from there and checks every sample line that names a coverage class next to a rate.

What it checks
  * every line in lesson-*/samples/**/*.cs|*.vb that names Class1 / Class2Plus / Class3Plus / Class3
    (case-insensitive, so the legacy "CLASS1" strings count) AND carries a rate literal 0.0xx must carry
    the canonical rate for THAT class;
  * the canonical rates are found in the curriculum (so the script and the document cannot diverge).
What it does NOT check (a known limit — see the unit specs): loadings, the no-claim ladder, rounding and the
worked example. Those live in each lesson's own tests, which assert the values the lesson prints.

Exit code 1 lists every offending file:line.
"""
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
REPO = pathlib.Path(__file__).resolve().parent.parent
CURRICULUM = REPO / "1-analysis" / "spec_lesson-pdfs" / "_curriculum.md"

CLASSES = ["Class1", "Class2Plus", "Class3Plus", "Class3"]


def canonical_rates():
    text = CURRICULUM.read_text(encoding="utf-8")
    m = re.search(r"Class1\s+([\d.]+)%\s+Class2Plus\s+([\d.]+)%\s+Class3Plus\s+([\d.]+)%\s+Class3\s+([\d.]+)%", text)
    if not m:
        raise SystemExit("could not find the canonical base rates in _curriculum.md (section Canonical tariff)")
    return {c: round(float(v) / 100, 6) for c, v in zip(CLASSES, m.groups())}


TOKEN = {c: re.compile(r"\b" + c + r"\b", re.I) for c in CLASSES}
RATE = re.compile(r"(?<![\w.])(0?\.0\d{2,4})(?![\d])")


def main():
    canon = canonical_rates()
    print("canonical rates:", {k: f"{v:.3f}" for k, v in canon.items()})
    bad, checked = [], 0
    for p in sorted(REPO.glob("lesson-*/samples/**/*")):
        if not p.is_file() or p.suffix.lower() not in (".cs", ".vb") or any(x in p.parts for x in ("bin", "obj")):
            continue
        for i, line in enumerate(p.read_text(encoding="utf-8-sig").splitlines(), 1):
            named = [c for c in CLASSES if TOKEN[c].search(line)]
            if len(named) != 1:            # zero classes, or a line comparing several: not a rate arm
                continue
            m = RATE.search(line)
            if not m:
                continue
            checked += 1
            value = round(float(m.group(1)), 6)
            if abs(value - canon[named[0]]) > 1e-9:
                bad.append(f"{p.relative_to(REPO).as_posix()}:{i}  {named[0]} carries {m.group(1)} "
                           f"(canonical {canon[named[0]]:.3f})   {line.strip()[:90]}")
    print(f"{checked} base-rate line(s) checked")
    if bad:
        print("\nOFF-TARIFF:")
        print("\n".join("  " + b for b in bad))
        sys.exit(1)
    print("OK — every base-rate line matches the canonical tariff")


if __name__ == "__main__":
    main()
