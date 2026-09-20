# -*- coding: utf-8 -*-
"""Lesson 01 — The .NET Platform Map. Reference implementation of the lesson standard
(1-analysis/spec_lesson-pdfs/_standard.md): every later lesson follows this shape."""
import re

from lesson_kit import (BUILD_DATE, DIFFERENT, ESTIMATE, MEASURED, REPO, RENAMED, SAME, TRAP, VERIFIED,
                        T_RUNTIME, T_TOOLING, code, compare, days_until, esc, from_sample, from_text,
                        legend, link, loc, mapping, pill, style_block)
from lessons.roster import ROSTER, meta, ref

META = meta(
    1,
    subtitle="C# · .NET · VB for a Kotlin/Java, TypeScript & Python architect — runtime, languages, "
             "versions and toolchain",
    objectives=[
        "Explain CoreCLR, IL, tiered JIT, ReadyToRun, Native AOT and NuGet in terms of the JVM parts you already know",
        "Date any .NET codebase from its project file and target framework moniker, state its support status "
        "and say which runtime it will start on",
        "Say what C#, VB and F# share on one runtime — and where Visual Basic stops (consumption-only)",
        "Drive the dotnet CLI the way you drive Gradle or npm, and combine the publish options",
        "Build and run the samples: one C# library consumed by a C# app and a VB app",
    ],
    maps_from="The JVM runtime model (HotSpot, bytecode, JARs, GraalVM native-image), Maven Central / npm "
              "packaging and SDKMAN / pyenv version pinning — plus the Windows (IIS) workloads you met while "
              "documenting a large multi-application migration estate.",
)

L = "lesson-01-dotnet-platform-map/samples"
CS_LIB = f"{L}/L01.PlatformKit/PlatformReport.cs"
CS_APP = f"{L}/L01.CSharpApp/Program.cs"
VB_APP = f"{L}/L01.VbApp/Program.vb"

NET10 = link("releases and support", "https://learn.microsoft.com/en-us/dotnet/core/releases-and-support")
POLICY = link(".NET support policy", "https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core")
EOS89 = link(".NET 8 and 9 end of support", "https://devblogs.microsoft.com/dotnet/dotnet-8-9-end-of-support/")
FWLIFE = link(".NET Framework lifecycle", "https://learn.microsoft.com/en-us/lifecycle/products/microsoft-net-framework")
ROLLFWD = link("Select which .NET version to use", "https://learn.microsoft.com/en-us/dotnet/core/versions/selection")
GLOBALJSON = link("global.json overview", "https://learn.microsoft.com/en-us/dotnet/core/tools/global-json")
SDK10 = link("What's new in the .NET 10 SDK", "https://learn.microsoft.com/en-us/dotnet/core/whats-new/dotnet-10/sdk")
DOWNLOAD = link("download .NET 10", "https://dotnet.microsoft.com/download/dotnet/10.0")
LANGS = link(".NET managed languages strategy", "https://learn.microsoft.com/en-us/dotnet/fundamentals/languages")
VBSTRAT = link("Visual Basic language strategy",
               "https://learn.microsoft.com/en-us/dotnet/visual-basic/getting-started/strategy")
VBNEW = link("What's new in Visual Basic", "https://learn.microsoft.com/en-us/dotnet/visual-basic/whats-new/")
CS14 = link("What's new in C# 14", "https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14")
CSHIST = link("The history of C#", "https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-version-history")
IRV = link("Assembly.ImageRuntimeVersion",
           "https://learn.microsoft.com/en-us/dotnet/api/system.reflection.assembly.imageruntimeversion")

# Pygments' vbnet lexer has no token for VB 14 interpolated strings, so every `$"` prints inside a red
# error box. The code is valid (the samples compile); drop the box, keep the text. (kit request)
_ERROR_SPAN = re.compile(r'<span style="border: 1px solid #F00">(.*?)</span>', re.S)


def listed(block, heading):
    """lesson_kit code()/compare() return html blocks with no `heading` key, so the Contents skipped every
    code panel. Copy the printed heading onto the block and opt it in at level 2 (kit request)."""
    block.update(heading=heading, toc=2)
    if "vb" in block.get("_langs", []):
        block["html"] = _ERROR_SPAN.sub(r"\1", block["html"])
    return block


def figure_heading(text):
    """A numbered heading for a block type that prints none of its own (threecol), kept with that block."""
    return {"type": "html", "html": f'<div class="figh"><h2>{esc(text)}</h2></div>', "heading": text,
            "toc": 2, "_keep_with_next": True}


def cmd(*commands):
    """Table-cell commands that never wrap inside themselves (a wrapped `dotnet new console -` reads wrong)."""
    return " · ".join(f'<code style="white-space:nowrap">{c}</code>' for c in commands)


def blocks():
    d89 = days_until(2026, 11, 10)
    d10 = days_until(2028, 11, 14)
    live89 = d89 > 0
    eos_value = f"{d89} days" if live89 else "ended"
    hours = sum(r[4] for r in ROSTER)
    phases = {}
    for r in ROSTER:
        phases[r[6]] = phases.get(r[6], 0) + r[4]
    loc_lib, loc_cs, loc_vb = loc(CS_LIB), loc(CS_APP), loc(VB_APP)
    vb_wrap = sum(1 for ln in (REPO / VB_APP).read_text(encoding="utf-8-sig").splitlines()
                  if ln.strip() in ("Module Program", "Sub Main()", "End Sub", "End Module"))
    vb_extra = loc_vb - loc_cs
    n_proj = len(list((REPO / L).glob("*/*.*proj")))

    runtime_cards = [
        {"num": 1, "title": "CoreCLR — the Common Language Runtime", "tags": [T_RUNTIME], "pills": [RENAMED],
         "what": "Loads assemblies, verifies and JIT-compiles IL, runs the garbage collector, owns threads and exceptions.",
         "lines": [("JVM", "HotSpot / OpenJ9"),
                   ("Differs", "One runtime serves every .NET language — C#, VB and F# share types directly"),
                   ("Roll-fwd", "An app starts on a newer patch or minor of the runtime it targets — never on a newer major by default"),
                   ("Old name", "The .NET Framework CLR is a separate, Windows-only runtime — see §3")]},
        {"num": 2, "title": "IL, metadata and assemblies", "tags": [T_RUNTIME], "pills": [RENAMED],
         "what": "The compiler emits intermediate language plus rich type metadata into an assembly.",
         "lines": [("JVM", "Bytecode in .class files, packaged into a JAR"),
                   (".NET", "IL + metadata in one assembly (.dll) that holds many types"),
                   ("Target", "The build stamps <code>TargetFrameworkAttribute</code> into it — <code>.NETCoreApp,Version=v10.0</code> in the samples"),
                   ("Inspect", "ILSpy or ildasm — the javap of .NET"),
                   ("Trap", "The .exe beside your .dll is a native <i>apphost</i> launcher; your program is still IL")]},
        {"num": 3, "title": "Tiered JIT, dynamic PGO and ReadyToRun", "tags": [T_RUNTIME], "pills": [SAME],
         "what": "Start fast with a quick JIT, then recompile hot methods with full optimisation.",
         "lines": [("JVM", "C1 → C2 tiered compilation"),
                   (".NET", "Tier-0 quick JIT → tier-1 optimised JIT; on by default since .NET Core 3.0"),
                   ("PGO", "Dynamic profile-guided optimisation is on by default since .NET 8"),
                   ("R2R", "ReadyToRun ships pre-compiled native code inside the assembly to cut start-up; JIT still available")]},
        {"num": 4, "title": "Garbage collector and value types", "tags": [T_RUNTIME], "pills": [DIFFERENT],
         "what": "A generational, compacting GC — plus a type system that avoids many allocations in the first place.",
         "lines": [("JVM", "G1 / ZGC / Parallel collectors"),
                   ("Modes", "Workstation or Server GC; ASP.NET Core apps default to Server GC"),
                   ("Structs", "Value types live inline (stack or inside an object) and copy on assignment"),
                   ("Sample", "Both lesson-01 apps print <code>server GC False</code> — the console default")]},
        {"num": 5, "title": "Base Class Library and NuGet", "tags": [T_TOOLING], "pills": [RENAMED],
         "what": "A large standard library, and one public package registry.",
         "lines": [("JDK", "java.base, java.net.http, java.time …"),
                   (".NET", "System.*, System.Net.Http, System.Text.Json, System.Collections.Generic"),
                   ("Registry", "nuget.org ≈ Maven Central; dependencies are PackageReference items in the project file"),
                   ("Lock file", "packages.lock.json is opt-in (RestorePackagesWithLockFile) — unlike npm")]}]

    publish_cards = [
        {"num": 6, "title": "Framework-dependent", "tags": [T_TOOLING], "pills": [SAME],
         "what": "Ship your IL and dependencies; the machine supplies the .NET runtime.",
         "lines": [("Like", "A thin JAR on an installed JRE · a Python zip on a Lambda runtime"),
                   ("Size", "Smallest package — only your IL and its dependencies"),
                   ("Pick when", "AWS Lambda managed runtime, containers on the aspnet image, servers you patch"),
                   ("Combines", "With single-file and ReadyToRun; the host still needs a matching major runtime")]},
        {"num": 7, "title": "Self-contained", "tags": [T_TOOLING], "pills": [RENAMED],
         "what": "Ship the runtime with the app, for one runtime identifier such as linux-x64.",
         "lines": [("Like", "A jlink runtime image"),
                   ("Cost", "Every app carries its own runtime copy; runtime patches arrive only when you redeploy"),
                   ("Pick when", "Hosts where you cannot install or control the runtime"),
                   ("Combines", "With single-file, ReadyToRun and trimming")]},
        {"num": 8, "title": "Single-file", "tags": [T_TOOLING], "pills": [RENAMED],
         "what": "Bundle the app (and optionally the runtime) into one executable file.",
         "lines": [("Like", "A fat JAR with a native launcher"),
                   ("Note", "Still JIT-compiled at start-up unless combined with ReadyToRun"),
                   ("Pick when", "CLI tools and agents you copy onto machines"),
                   ("Combines", "Framework-dependent or self-contained")]},
        {"num": 9, "title": "ReadyToRun", "tags": [T_RUNTIME], "pills": [DIFFERENT],
         "what": "Pre-compile IL to native code at publish time and keep the JIT as a fallback.",
         "lines": [("Like", "An ahead-of-time compilation cache — faster start, same compatibility"),
                   ("Cost", "Larger assemblies; hot methods are still re-compiled at tier 1"),
                   ("Pick when", "Start-up matters but you depend on reflection-heavy libraries"),
                   ("Combines", "Framework-dependent or self-contained, single-file or not")]},
        {"num": 10, "title": "Native AOT", "tags": [T_RUNTIME], "pills": [SAME],
         "what": "Compile the whole app to a native executable — no JIT and no IL at run time.",
         "lines": [("Like", "GraalVM native-image — the same closed-world trade-off"),
                   ("For you", "The .NET answer to the ~175 ms cold starts you tuned in Python Lambdas — " + ref(12)),
                   ("Limits", "No run-time code generation; reflection needs trimming annotations"),
                   ("Implies", "Self-contained and trimmed; the sample's <code>JIT on</code> line would print False")]}]

    return [
        style_block(),
        {"type": "toc", "heading": "▤ Contents", "depth": 2,
         "note": "Page numbers are resolved from the rendered PDF. Code panels are cut from the compiled samples."},
        # a callout heading must not print alone at a page foot with its items on the next page (kit request)
        {"type": "html", "html": "<style>.callout .ct { break-after:avoid; page-break-after:avoid; } "
                                 ".callout li:first-child { break-before:avoid; page-break-before:avoid; }</style>"},

        # ═══════════════════════════ 1 · WHY THIS TRACK ═══════════════════════════
        {"type": "story", "heading": "1 · Why this track exists — and who it is written for",
         "html": (
             "<p><b>This track is written for one reader: an architect with eight years across Kotlin/Java, "
             "TypeScript, Python and Dart who has never had to own a .NET codebase — and keeps meeting one.</b> "
             "Many insurance and banking estates run line-of-business systems on .NET, and the Windows (IIS) "
             "workloads that sit beside ECS Fargate and Lambda in a migration inventory are where .NET Framework "
             "most often hides. Reading that code, sizing its migration and designing its replacement is "
             "architecture work; this track gives you the vocabulary to do it first-hand.</p>"
             "<p><b>The approach is map, don't restart.</b> Every lesson starts from something you have already "
             "built — a Kotlin mono-repo of 50–120+ modules, a Spring WebFlux service, a Python Lambda tuned to "
             "~175 ms cold starts, a 100%-coverage TDD suite, an Entra ID single sign-on integration — and shows "
             "the .NET shape of the same idea. Chips say whether an idea transfers as-is (" + SAME + "), only "
             "changes its name (" + RENAMED + "), genuinely behaves differently (" + DIFFERENT + ") or looks the "
             "same and bites (" + TRAP + ").</p>"
             "<p><b>New .NET work is C#, but estates from the 2000s still run Visual Basic .NET, so you need to "
             "read both.</b> A modernisation architect has to read VB, keep it running and plan its exit. VB "
             "appears beside C# wherever the difference teaches something, and " + ref(6) + " is dedicated to "
             "it.</p>"
             "<p><b>Every code panel is real.</b> C# and VB snippets are cut from sample projects in this "
             "repository by <code>#region</code> name, and <code>0-script/verify_samples.py</code> builds, tests "
             "and runs those projects on the .NET 10 SDK. A snippet that did not compile could not appear here.</p>")},

        {"type": "kpi", "heading": "1.1 · The numbers to leave this lesson with",
         "items": [
             {"label": ".NET 10 · LTS", "value": "to Nov 2028", "tone": "teal",
              "sub": "supported until 14 Nov 2028 · verified"},
             {"label": ".NET 8 & 9 support", "value": eos_value, "tone": "red",
              "sub": "end 10 Nov 2026 · counted from " + BUILD_DATE.isoformat()},
             {"label": "Languages, one runtime", "value": "3", "tone": "violet",
              "sub": "C# · Visual Basic · F# · verified"},
             {"label": "This track", "value": f"{hours} h", "tone": "indigo",
              "sub": "12 lessons · study-time estimate"},
             {"label": "Lesson 01 samples", "value": f"{loc_lib + loc_cs + loc_vb} lines", "tone": "navy",
              "sub": "C# + VB · measured at build"}]},

        legend(T_RUNTIME, T_TOOLING),

        {"type": "callout", "variant": "info", "heading": "ℹ Before you start",
         "items": [
             "<b>No earlier lesson is needed — this is where the track starts.</b> You will build "
             "<code>L01.PlatformKit</code>, a C# class library that reports the runtime a program is running on, "
             "and use it unchanged from a C# console app (<code>L01.CSharpApp</code>) and a Visual Basic console "
             "app (<code>L01.VbApp</code>).",
             "<b>Install the .NET 10 SDK</b> — 10.0.401 or any later 10.0 SDK, which is what this repository's "
             "<code>global.json</code> accepts (" + DOWNLOAD + "). <code>dotnet --list-sdks</code> must list it. "
             "Python 3 runs <code>0-script/verify_samples.py</code>, which needs no extra packages.",
             "<b>If <code>dotnet</code> says “No .NET SDKs were found”, a runtime-only install earlier on PATH is "
             "shadowing the SDK.</b> Put the SDK's <code>dotnet</code> folder first on PATH, or call that "
             "<code>dotnet.exe</code> by its full path. <code>DOTNET_ROOT</code> does not help: it tells an "
             "apphost where the runtime is, not which SDKs the <code>dotnet</code> command sees.",
             "<b>Every numbered section leads with its point.</b> Evidence, code and diagrams follow, so the first "
             "paragraph of each section gives you the whole argument.",
             "Facts that change with releases are marked " + VERIFIED + " and link to the official source; "
             "judgements such as study hours are marked " + ESTIMATE + "; numbers computed from this repository "
             "at build time are marked " + MEASURED + ". Code panels name the file and <code>#region</code> they "
             "were cut from; Java, Kotlin, TypeScript and Python panels are for comparison and are not compiled."]},

        # ═══════════════════════════ 2 · THE PLATFORM ═══════════════════════════
        {"type": "story", "heading": "2 · The platform in one picture",
         "html": (
             "<p><b>.NET is a runtime plus a class library plus compilers — the same three-part shape as the JDK, "
             "with one decisive difference: the runtime was designed for many languages from day one.</b> C#, "
             "Visual Basic and F# compile to the same intermediate language (IL), load into the same runtime and "
             "share the same type system. A VB program can call a C# library with no bridge, adapter or "
             "marshalling layer — the lesson-01 samples do exactly that.</p>"
             "<p><b>The pieces map almost one-to-one onto the JVM.</b> CoreCLR is HotSpot. IL inside an assembly "
             "is bytecode inside a JAR. The Base Class Library is the JDK class library. NuGet is Maven Central. "
             "Roslyn — the C# and VB compilers, written in C# and VB themselves — is javac with a public API that "
             "analyzers and IDEs call directly.</p>"
             "<p><b>Four things stop mapping: generics, value types, exceptions and how IL becomes machine "
             "code.</b> Generics are <i>reified</i>: <code>List&lt;int&gt;</code> is a real type at run time and "
             "stores unboxed integers. User-defined value types (<code>struct</code>) are stored inline in whatever "
             "holds them — a local, an array, an object's field — instead of as separate heap objects, and they "
             "copy on assignment. Exceptions are all unchecked. And the compiled output does not have to stay IL: "
             "ReadyToRun pre-compiles it at publish time and Native AOT removes the JIT altogether — "
             "GraalVM native-image is the nearest thing you know.</p>")},

        {"type": "mermaid", "inline": True,
         "heading": "2.1 · From source file to running process",
         "caption": "indigo = source · amber = compiler or decision · slate = artefact · teal = runtime path · "
                    "green = the OS process · framework-dependent vs self-contained is a separate switch (5.4)",
         "code": ("flowchart LR\n"
                  '  CS["Program.cs"]:::src --> ROS["Roslyn<br/>csc and vbc"]:::tool\n'
                  '  VB["Program.vb"]:::src --> ROS\n'
                  '  FS["Program.fs"]:::src --> FSC["F# compiler<br/>fsc"]:::tool\n'
                  '  NUG["NuGet packages<br/>.nupkg"]:::art -.->|"referenced at compile"| ROS\n'
                  '  ROS --> IL["Assembly .dll<br/>IL + metadata"]:::art\n'
                  '  FSC --> IL\n'
                  '  IL --> DEP{"How does IL become<br/>machine code?"}:::tool\n'
                  '  DEP -- "JIT at run time (default)" --> JIT["CoreCLR<br/>tiered JIT"]:::run\n'
                  '  DEP -- "ReadyToRun at publish" --> R2R["Pre-compiled code<br/>JIT as fallback"]:::run\n'
                  '  DEP -- "Native AOT at publish" --> AOT["Native executable<br/>no JIT at run time"]:::run\n'
                  '  JIT --> OS["OS process"]:::os\n'
                  '  R2R --> OS\n'
                  '  AOT --> OS\n'
                  "  classDef src fill:#c7d2fe,color:#1f2937,stroke:#6366f1;\n"
                  "  classDef tool fill:#fde68a,color:#1f2937,stroke:#d97706;\n"
                  "  classDef art fill:#e2e8f0,color:#1f2937,stroke:#475569;\n"
                  "  classDef run fill:#ccfbf1,color:#1f2937,stroke:#0d9488;\n"
                  "  classDef os fill:#bbf7d0,color:#1f2937,stroke:#16a34a;\n")},

        listed(compare(from_text("""
            // no single JVM API holds all of this: the nearest calls
            fun capture(caller: Class<*>) = PlatformReport(
                framework = "Java ${Runtime.version()}",
                // no stored target framework: a .class file records
                // only its format version (major 65 = Java 21)
                operatingSystem = System.getProperty("os.name"),
                arch = System.getProperty("os.arch"),
                gc = ManagementFactory.getGarbageCollectorMXBeans()
                    .joinToString { it.name },
                // null when the JVM has no JIT compiler
                jitOn = ManagementFactory.getCompilationMXBean() != null,
                callerJar = caller.protectionDomain.codeSource
                    ?.location?.path ?: "(unknown)",
            )
            """, "kotlin", file="the JVM questions you already ask"),
                       from_sample(CS_LIB, "capture"),
                       heading="2.2 · Asking the runtime what it is — Kotlin on the JVM vs C#",
                       note="<b>.NET answers each question with one typed API; the JVM spreads them over system "
                            "properties and management beans.</b> <code>FrameworkDescription</code> is the runtime "
                            "executing the process, after roll-forward; <code>TargetFrameworkAttribute</code> is what "
                            "the assembly was built for — the JVM keeps no such record, only a class-file version. "
                            "<code>IsDynamicCodeCompiled</code> is false under Native AOT, much as the compilation "
                            "bean is null on a JVM without a JIT. The record this fills is shown in 4.1."),
               "2.2 · Asking the runtime what it is — Kotlin on the JVM vs C#"),

        mapping("2.3 · Concept map — JVM and friends → .NET", [
            ("JVM (HotSpot)", "CoreCLR", "renamed", "Multi-language by design — not a VM for one language"),
            ("Bytecode in .class", "IL in an assembly (.dll)", "renamed", "An assembly is closer to a JAR than to a .class"),
            ("JAR / fat JAR", "Assembly / self-contained publish", "renamed", "The .exe apphost is a native launcher over IL, not a native build"),
            ("A Java 8 JAR usually runs on a Java 21 JRE", "A <code>net8.0</code> app needs an 8.0 runtime", "trap",
             "The host rolls forward to a newer patch or minor, never a newer major — unless <code>RollForward</code> is <code>Major</code>"),
            ("JDK class library", "Base Class Library (BCL)", "same", "Namespaces start with <code>System.</code>"),
            ("Maven Central / npm", "NuGet (nuget.org)", "renamed", "No separate pom or package.json — it is all in the project file"),
            ("pom.xml / build.gradle.kts", ".csproj / .vbproj (MSBuild)", "different", "Declarative XML; shared logic goes in Directory.Build.props — " + ref(7)),
            ("Generics with type erasure", "Reified generics", "different", "<code>typeof(T)</code> works; <code>List&lt;int&gt;</code> stores unboxed integers"),
            ("Java primitives (int, double) · Kotlin value class", "User-defined value types (<code>struct</code>)", "trap",
             "Copies on assignment, so changing a copy changes nothing; casting to <code>object</code> or an interface boxes it"),
            ("Checked exceptions", "Unchecked exceptions only", "different", "No <code>throws</code>; document with <code>/// &lt;exception&gt;</code>"),
            ("Kotlin data class / Java record", "C# <code>record</code>", "same", "<code>with</code> = <code>copy()</code>; VB can use records but not declare them — " + ref(3)),
            ("Kotlin coroutines / WebFlux", "<code>async</code>/<code>await</code> + <code>Task</code>", "different", ref(5)),
            ("GraalVM native-image", "Native AOT", "same", "Same closed-world trade-off: reflection needs annotations"),
            ("SDKMAN / .sdkmanrc / pyenv", "global.json", "renamed", "Pins the SDK, not the runtime; it selects among installed SDKs and never installs one"),
            ("Spring Boot", "ASP.NET Core", "different", "Built-in container with explicit registration — no component scanning — " + ref(8)),
            ("Java EE app on WebSphere", "ASP.NET on IIS (.NET Framework)", "same", "<code>System.Web</code> does not exist on modern .NET — port, don't lift"),
            ("JUnit + Mockito", "xUnit / NUnit / MSTest + NSubstitute / Moq", "renamed", ref(10)),
        ]),

        {"type": "cards",
         "band": {"title": "2.4 · Runtime pieces — the JVM parts under their .NET names", "note": "runtime view",
                  "tone": "violet"},
         "cards": runtime_cards[:3]},
        {"type": "cards", "toc": False,
         "band": {"title": "2.4 · Runtime pieces (continued)", "note": "runtime view", "tone": "violet"},
         "cards": runtime_cards[3:]},

        # ═══════════════════════════ 3 · VERSIONS ═══════════════════════════
        {"type": "story", "heading": "3 · Versions — how to read a .NET codebase's age",
         "html": (
             "<p><b>There are two .NETs, and a codebase's project file tells you which one it needs in the first "
             "ten lines.</b> <i>.NET Framework</i> (1.0 in 2002 → 4.8.1 in 2022) is Windows-only, ships as a "
             "Windows component and receives no new major versions. <i>.NET</i> — born as .NET Core 1.0 in 2016 and "
             "renamed at .NET 5 in 2020, skipping “4” to avoid confusion — is cross-platform, open source and ships "
             "every November (" + NET10 + ").</p>"
             "<p><b>The release rhythm is predictable.</b> Even-numbered releases are Long Term Support "
             "(36 months); odd-numbered releases are Standard Term Support, extended from 18 to 24 months starting "
             "with .NET 9. That extension makes .NET 8 (LTS) and .NET 9 (STS) leave support on the <b>same day, "
             "10 November 2026</b>. .NET 10 shipped on 11 November 2025 and is supported until 14 November 2028 "
             "(" + POLICY + " · " + EOS89 + ").</p>"
             + (f"<p><b>New work targets <code>net10.0</code>, and anything on <code>net8.0</code> or "
                f"<code>net9.0</code> has {d89} days left to get there.</b> " if live89 else
                "<p><b>New work targets <code>net10.0</code>, and anything on <code>net8.0</code> or "
                "<code>net9.0</code> has been out of support since 10 November 2026.</b> ")
             + "Anything on .NET Core 3.1, .NET 5, 6 or 7 is already unsupported. A .NET Framework 4.8.1 "
             "application is still supported as a component of the Windows version it runs on (" + FWLIFE + "), "
             "but it will never get a new runtime feature — a migration argument rather than a security one. "
             "Retargeting is not optional: an app does not move to a newer major runtime on its own (3.6).</p>")},

        {"type": "mermaid", "inline": True,
         "heading": "3.1 · Support windows of modern .NET",
         "caption": "grey = out of support · red = ends 10 Nov 2026 · teal = current LTS · red vertical line = the day this PDF was built",
         "code": ('%%{init: {"theme":"base","themeVariables": {"taskTextColor":"#1f2937",'
                  '"taskTextDarkColor":"#1f2937","taskTextLightColor":"#1f2937","taskTextOutsideColor":"#1f2937",'
                  '"sectionBkgColor":"#EEF2FF","sectionBkgColor2":"#F8FAFC","altSectionBkgColor":"#F8FAFC",'
                  '"doneTaskBkgColor":"#CBD5E1","doneTaskBorderColor":"#64748B","critBkgColor":"#FCA5A5",'
                  '"critBorderColor":"#DC2626","activeTaskBkgColor":"#5EEAD4","activeTaskBorderColor":"#0F766E",'
                  '"todayLineColor":"#DC2626","gridColor":"#E2E8F0"},'
                  '"gantt": {"barHeight": 20, "fontSize": 12, "sectionFontSize": 12, "leftPadding": 70}}}%%\n'
                  "gantt\n"
                  "  dateFormat YYYY-MM-DD\n"
                  "  axisFormat %Y\n"
                  "  section LTS\n"
                  "  NET 6 LTS   :done, n6, 2021-11-08, 2024-11-12\n"
                  "  NET 8 LTS   :crit, n8, 2023-11-14, 2026-11-10\n"
                  "  NET 10 LTS  :active, n10, 2025-11-11, 2028-11-14\n"
                  "  section STS\n"
                  "  NET 5       :done, n5, 2020-11-10, 2022-05-10\n"
                  "  NET 7 STS   :done, n7, 2022-11-08, 2024-05-14\n"
                  "  NET 9 STS   :crit, n9, 2024-11-12, 2026-11-10\n")},

        {"type": "chartrow", "charts": [
            {"heading": "3.2 · Support length by release", "kind": "bar",
             "args": {"data": [(".NET 5", 18), (".NET 6", 36), (".NET 7", 18), (".NET 8", 36), (".NET 9", 24),
                               (".NET 10", 36)],
                      "ylabel": "months", "tone": "indigo", "width": 390, "height": 220},
             "caption": "months from GA to end of support · verified against the .NET support policy",
             "note": "<b>Even = 36 months, odd = 18 → 24.</b> The STS extension is why .NET 9 does not buy "
                     "you any time over .NET 8: both end on 10 Nov 2026. " + VERIFIED + " " + POLICY + "."},
            {"heading": "3.3 · Days of support left", "kind": "bar",
             "args": {"data": [(".NET 8", max(d89, 0)), (".NET 9", max(d89, 0)), (".NET 10", max(d10, 0))],
                      "ylabel": "days", "tone": "amber", "width": 390, "height": 220},
             "caption": "days from the build date " + BUILD_DATE.isoformat() + " to end of support · counted from the verified dates",
             "note": (f"<b>.NET 8 and .NET 9 share one countdown — {d89} days — while .NET 10 has {d10}.</b> "
                      "The bars are recounted on every build, so the first two drop to zero after 10 Nov 2026."
                      if live89 else
                      f"<b>.NET 8 and .NET 9 are out of support; .NET 10 has {max(d10, 0)} days left.</b> "
                      "The bars are recounted on every build from the verified end dates.")}]},

        {"type": "table", "heading": "3.4 · Target framework monikers you will find in project files",
         "cols": ["TFM", "What it targets", "Where you meet it", "Status"],
         "rows": [
             ["<code>&lt;TargetFrameworkVersion&gt;v4.x</code> (no <code>Sdk</code> attribute)",
              ".NET Framework 4.x in an old-style project — Windows only",
              "Unmigrated apps, often with <code>packages.config</code> and <code>Global.asax</code>",
              pill("4.6.1 and older ended Apr 2022", "red") + " " + pill("4.6.2 ends 12 Jan 2027", "amber")],
             ["<code>net48</code> · <code>net481</code>", ".NET Framework 4.8 / 4.8.1 in an SDK-style project",
              "Apps part-way through a migration; ASP.NET, WCF and WinForms on Windows servers",
              pill("Legacy · follows Windows", "slate")],
             ["<code>netstandard2.0</code>", "An API contract, not a runtime",
              "Shared libraries that must load in both .NET Framework and modern .NET", pill("Bridge", "sky")],
             ["<code>netcoreapp3.1</code>", ".NET Core 3.1", "First-wave migrations", pill("Ended Dec 2022", "red")],
             ["<code>net6.0</code> · <code>net7.0</code>", ".NET 6 LTS · .NET 7 STS", "Services built 2021–2023",
              pill("Ended 2024", "red")],
             ["<code>net8.0</code> · <code>net9.0</code>", ".NET 8 LTS · .NET 9 STS", "Most services running today",
              pill("Ends 10 Nov 2026" if live89 else "Ended 10 Nov 2026", "amber" if live89 else "red")],
             ["<code>net10.0</code>", ".NET 10 LTS", "New work — every sample in this track",
              pill("Supported to Nov 2028", "green")],
             ["<code>net10.0-windows</code>", ".NET 10 plus Windows-only APIs", "Modernised WinForms / WPF desktop apps",
              pill("Windows only", "violet")]]},

        {"type": "mermaid", "inline": True,
         "heading": "3.5 · What am I looking at? — dating a legacy repository",
         "caption": "indigo = start · amber = question · green = modern · sky = bridge · slate = .NET Framework · rose = not .NET at all",
         "code": ("flowchart LR\n"
                  '  Q0{"Any .csproj<br/>or .vbproj?"}:::start\n'
                  '  Q0 -- "no" --> Q4{"What is there<br/>instead?"}:::q\n'
                  '  Q4 -- ".vbp .frm .bas" --> VB6["Visual Basic 6<br/>COM, not .NET: rewrite"]:::bad\n'
                  '  Q4 -- ".asp pages" --> ASP["Classic ASP<br/>VBScript, not .NET: rewrite"]:::bad\n'
                  '  Q4 -- ".aspx + web.config" --> WEB["ASP.NET Web Site project<br/>.NET Framework on IIS"]:::legacy\n'
                  '  Q0 -- "yes" --> Q1{"Root element is<br/>Project Sdk=...?"}:::q\n'
                  '  Q1 -- "yes: SDK-style" --> Q2{"TargetFramework<br/>or TargetFrameworks?"}:::q\n'
                  '  Q1 -- "no: TargetFrameworkVersion,<br/>packages.config" --> Q3{"Global.asax<br/>or .svc files?"}:::q\n'
                  '  Q2 -- "netcoreapp or net5.0+" --> MOD["Modern .NET<br/>support date in 3.4"]:::good\n'
                  '  Q2 -- "netstandard2.0, or<br/>net48;net8.0" --> STD["Shared library<br/>loads in both worlds"]:::bridge\n'
                  '  Q2 -- "only net4x, e.g.<br/>net472 or net48" --> HALF["Framework app<br/>part-way migrated"]:::bridge\n'
                  '  Q3 -- "yes" --> IIS["ASP.NET or WCF on IIS<br/>System.Web: port, do not lift"]:::legacy\n'
                  '  Q3 -- "no" --> DESK["WinForms, console<br/>or Windows service"]:::legacy\n'
                  "  classDef start fill:#c7d2fe,color:#1f2937,stroke:#6366f1;\n"
                  "  classDef q fill:#fde68a,color:#1f2937,stroke:#d97706;\n"
                  "  classDef good fill:#bbf7d0,color:#1f2937,stroke:#16a34a;\n"
                  "  classDef bridge fill:#e0f2fe,color:#1f2937,stroke:#0369a1;\n"
                  "  classDef legacy fill:#e2e8f0,color:#1f2937,stroke:#475569;\n"
                  "  classDef bad fill:#fce7f3,color:#1f2937,stroke:#be185d;\n")},

        listed(code(from_text(r"""
            # a host whose only runtimes are 8.0.19 and 8.0.28
            dotnet L01.CSharpApp.dll
            You must install or update .NET to run this application.

            Architecture: x64
            Framework: 'Microsoft.NETCore.App', version '10.0.0' (x64)
            .NET location: C:\Program Files\dotnet\

            The following frameworks were found:
              8.0.19 at [C:\Program Files\dotnet\shared\Microsoft.NETCore.App]
              8.0.28 at [C:\Program Files\dotnet\shared\Microsoft.NETCore.App]

            # exit code 150 · the App: path line and the download links are left out
            """, "text", label="Terminal — the net10.0 sample on an 8.0-only host",
                              file="captured on the build machine"),
                    heading="3.6 · A net10.0 app on a host that only has .NET 8",
                    note="<b>The host rolls forward, never back — and never across a major version by default.</b> "
                         "<code>L01.CSharpApp.runtimeconfig.json</code> asks for Microsoft.NETCore.App 10.0.0, so "
                         "the host accepts any installed 10.0 patch but not 8.0. The reverse fails the same way: a "
                         "<code>net8.0</code> app does not start on a host that has only .NET 10 unless its "
                         "<code>RollForward</code> is <code>Major</code> (" + ROLLFWD + ")."),
               "3.6 · A net10.0 app on a host that only has .NET 8"),

        {"type": "callout", "variant": "warn", "heading": "⚠ The 10 November 2026 double cut-off",
         "items": [
             ("<b>.NET 8 (LTS) and .NET 9 (STS) stop receiving security fixes on the same day.</b>" if live89 else
              "<b>.NET 8 (LTS) and .NET 9 (STS) stopped receiving security fixes on the same day.</b>")
             + " Upgrading from 8 to 9 buys nothing; the only supported destination is .NET 10.",
             "<b>Start the inventory with the TFM, not the language.</b> A VB.NET service on <code>net8.0</code> is a "
             "one-line retarget plus a test run; a C# service on <code>net48</code> is a port.",
             "<b>Installing the .NET 10 runtime upgrades nothing.</b> A <code>net8.0</code> app still needs an 8.0 "
             "runtime, because the default <code>RollForward</code> policy (<code>Minor</code>) never crosses a major "
             "version. Retarget and retest; set <code>RollForward</code> to <code>Major</code> only as a documented "
             "stop-gap (" + ROLLFWD + ").",
             "<b>Change the TFM and the container base image together.</b> An app retargeted to <code>net10.0</code> "
             "whose Dockerfile still says FROM an 8.0 runtime image fails at start-up, as 3.6 shows; an app still on "
             "<code>net8.0</code> placed on a 10.0 image does not start either.",
             "Sources: " + EOS89 + " · " + POLICY + "."]},

        # ═══════════════════════════ 4 · LANGUAGES ═══════════════════════════
        {"type": "story", "heading": "4 · Three languages, one runtime",
         "html": (
             "<p><b>C# is where .NET evolves; Visual Basic is deliberately stable; F# is the functional "
             "option.</b> C# 14 ships with .NET 10 and keeps adding syntax — extension members, the "
             "<code>field</code> keyword, null-conditional assignment (" + CS14 + "). Microsoft's stated strategy "
             "for Visual Basic is <i>consumption-only</i>: VB code can use new .NET APIs and types, but the "
             "language will generally not add syntax to <i>define</i> things that need new language support "
             "(" + VBSTRAT + " · " + LANGS + ").</p>"
             "<p><b>A VB project uses a C# library as if it were written in VB — it just cannot declare everything "
             "C# can.</b> Same types, same exceptions, same debugger. VB can read a C# <code>record</code>, compare "
             "it and pass it on; it cannot declare a record or use <code>with</code> to copy one. The samples below "
             "are the proof: one C# class library, consumed unchanged by a C# console app and a VB console app.</p>"
             "<p><b>Mixed-language solutions need no FFI, so a VB-to-C# migration can move one project at a "
             "time.</b> New code goes into C# libraries, old VB calls it, and each VB project is converted when it "
             "is next touched. " + ref(6) + " turns this into a plan.</p>")},

        listed(code(from_sample(CS_LIB, "report-record"),
                    heading="4.1 · The shared C# library — a positional record",
                    note="<b>One declaration gives you</b> a constructor, init-only properties (settable only while "
                         "the object is created, including by a <code>with</code> copy), value equality, "
                         "<code>ToString()</code> and <code>Deconstruct</code> — Kotlin's <code>data class</code> in "
                         "C#. Read the two version fields apart: <code>TargetFramework</code> is what the assembly "
                         "was built for; <code>ImageRuntimeVersion</code> is the CLR version string written into the "
                         "metadata header, still <code>v4.0.30319</code> — not the .NET version (" + IRV + ")."),
               "4.1 · The shared C# library — a positional record"),

        listed(compare(from_sample(CS_APP, "program"), from_sample(VB_APP, "program"),
                       heading="4.2 · The same program in C# and in Visual Basic",
                       note="<b>Same library, same types, same output.</b> C# uses top-level statements; VB needs a "
                            "<code>Module</code> with <code>Sub Main</code> around this region. VB is "
                            "case-insensitive and line-oriented — the <code>Capture(</code> call continues on the "
                            "next line without a <code>_</code> because it ends with an open parenthesis."),
               "4.2 · The same program in C# and in Visual Basic"),

        listed(compare(from_sample(CS_APP, "equality"), from_sample(VB_APP, "equality"),
                       heading="4.3 · What each language can do with the same C# record",
                       note="<b>C# can compare and copy; VB can only compare.</b> Both get value equality from the "
                            "record, so a fresh capture equals the first one. C# makes a modified copy with "
                            "<code>with</code>; VB has no syntax for that — consumption-only in one screen. For a "
                            "migration this is good news: shared models can move to C# first without breaking their "
                            "VB callers. Records, <code>with</code> and equality in depth: " + ref(3) + "."),
               "4.3 · What each language can do with the same C# record"),

        {"type": "chart", "heading": "4.4 · Language feature matrix — C#, VB and the languages you know",
         "kind": "heatmap",
         "args": {"rows": ["Records / data classes", "Non-destructive copy", "Null-safety in types",
                           "Pattern-matching switch", "async / await style", "Language-integrated query",
                           "Runtime (reified) generics", "User-defined value types", "Properties",
                           "Extension members", "XML literals"],
                  "cols": ["C# 14", "VB", "Java 21", "Kotlin 2"],
                  "matrix": [[2, 1, 2, 2], [2, 0, 0, 2], [1, 0, 0, 2], [2, 1, 2, 1], [2, 2, 1, 2],
                             [2, 2, 1, 1], [2, 2, 0, 1], [2, 2, 0, 1], [2, 2, 0, 2], [2, 1, 0, 2],
                             [0, 2, 0, 0]],
                  "cell": 34, "tone": "violet", "fmt": lambda v: {2: "yes", 1: "some", 0: "—"}[int(v)]},
         "caption": "yes = first-class syntax · some = library, subset, compile-time-only or consume-only · — = none · a rubric, not a benchmark",
         "note": "<b>VB stopped gaining new syntax around 2017; its gaps are the features C# has added since.</b> "
                 "VB 15 took tuples alongside C# 7 but not C# 7's pattern matching, and later VB releases mostly "
                 "learned to consume new C# constructs, such as init-only properties in VB 16.9 (" + VBNEW + "). "
                 "The gaps: pattern matching (C# 7, 2017), nullable reference types (C# 8, 2019), records and "
                 "<code>with</code> (C# 9, 2020) (" + CSHIST + "); VB never had C#'s unsafe code either. Its one "
                 "unique row — XML literals — is also why some legacy VB code is hard to port mechanically. Java's "
                 "“some” async is virtual threads and <code>CompletableFuture</code>; Kotlin's “some” generics are "
                 "<code>inline reified</code> functions. C#'s “some” in the null-safety row is deliberate: nullable "
                 "reference types are compiler annotations, not runtime types (" + ref(2) + ")."},

        # ═══════════════════════════ 5 · TOOLCHAIN ═══════════════════════════
        {"type": "story", "heading": "5 · The toolchain — one CLI, five publish options",
         "html": (
             "<p><b>The <code>dotnet</code> CLI does the jobs of Gradle and npm in one executable, and "
             "<code>global.json</code> does <code>.sdkmanrc</code>'s job of pinning the SDK.</b> The CLI scaffolds "
             "from templates, restores packages, builds, tests, runs, packs and publishes. It selects among the SDKs "
             "installed on the machine but does not install one. This repository's <code>global.json</code> asks "
             "for 10.0.401 with <code>rollForward: latestFeature</code>, so the CLI uses the highest installed 10.0 "
             "SDK at or above that version (" + GLOBALJSON + "). Restore is implicit in build, test and run, so "
             "the everyday loop is two commands.</p>"
             "<p><b>A project file is declarative MSBuild, not a script.</b> An SDK-style <code>.csproj</code> or "
             "<code>.vbproj</code> is often five lines, because the SDK supplies defaults: every source file in the "
             "folder is compiled, packages restore from nuget.org, output goes to <code>bin/</code>. Shared "
             "settings live in <code>Directory.Build.props</code>, which MSBuild imports for every project beneath "
             "it — this repository uses one to put all build output in <code>.build/artifacts</code>. "
             + ref(7) + " goes deep.</p>"
             "<p><b>Publishing is a set of switches, not one choice.</b> Framework-dependent or self-contained is "
             "one switch; single-file and ReadyToRun are independent switches that work with either; Native AOT "
             "implies self-contained. Together they trade start-up time and package size against compatibility with "
             "reflection-heavy libraries — the same trade you made choosing between a JAR on a JRE and a GraalVM "
             "native image, and the one you tuned when you got Python Lambda packages down to 55 KB.</p>")},

        {"type": "table", "heading": "5.1 · The dotnet CLI next to the tools you use today",
         "cols": ["Task", "Gradle · npm", ".NET CLI", "Note"],
         "rows": [
             ["Scaffold", cmd("gradle init", "npm init"), cmd("dotnet new console -lang VB"),
              "<code>dotnet new list</code> shows templates"],
             ["Restore", "implicit · " + cmd("npm install"), cmd("dotnet restore"), "implicit in build, test and run"],
             ["Compile", cmd("gradle build", "npm run build"), cmd("dotnet build -c Release"),
              "Debug is the default configuration"],
             ["Test", cmd("gradle test", "npm test"), cmd("dotnet test"), "xUnit, NUnit and MSTest — " + ref(10)],
             ["Run", cmd("gradle bootRun", "npm start"), cmd("dotnet run"),
              ".NET 10 also runs one file: " + cmd("dotnet run app.cs")],
             ["Package an app", cmd("gradle bootJar"), cmd("dotnet publish"),
              cmd("-r linux-x64 --self-contained", "-p:PublishAot=true")],
             ["Package a library", cmd("gradle publish", "npm publish"), cmd("dotnet pack", "dotnet nuget push"),
              "produces a .nupkg"],
             ["Add a dependency", "edit the build file · " + cmd("npm install x"), cmd("dotnet package add X"),
              "the .NET 10 noun-first form; " + cmd("dotnet add package X") + " still works (" + SDK10 + ")"],
             ["Tools", "SDKMAN · " + cmd("npm i -g", "npx"), cmd("dotnet tool install -g", "dnx"),
              "<code>dnx</code> runs a tool once without installing it, like npx; repo-local tools live in "
              "<code>dotnet-tools.json</code>"],
             ["Format / lint", "Spotless, ktlint · Prettier, ESLint", cmd("dotnet format"),
              "rules come from <code>.editorconfig</code>"]]},

        {"type": "mermaid", "inline": True,
         "heading": "5.2 · What happens on dotnet run (simplified)",
         "caption": "the muxer finds the SDK through global.json; the host finds the runtime through runtimeconfig.json, within one major version",
         "code": ("sequenceDiagram\n"
                  "  autonumber\n"
                  "  participant U as You\n"
                  "  participant M as dotnet muxer\n"
                  "  participant S as SDK and MSBuild\n"
                  "  participant H as hostfxr and hostpolicy\n"
                  "  participant C as CoreCLR\n"
                  "  U->>M: dotnet run --project L01.VbApp\n"
                  "  M->>S: pick SDK via global.json, restore, build\n"
                  "  S-->>M: L01.VbApp.dll + runtimeconfig.json + deps.json\n"
                  "  M->>H: launch the app\n"
                  "  Note over H: runtimeconfig.json<br/>wants 10.0.0, gets 10.0.x\n"
                  "  H->>C: load the runtime, resolve deps.json\n"
                  "  Note over C: JIT-compiles<br/>Sub Main, runs it\n"
                  "  C-->>U: Hello from VB on .NET 10.0.x\n")},

        listed(compare(from_sample(f"{L}/L01.CSharpApp/L01.CSharpApp.csproj"),
                       from_sample(f"{L}/L01.VbApp/L01.VbApp.vbproj"),
                       heading="5.3 · Two project files — the language is the file extension",
                       note="<b>The same MSBuild, the same SDK.</b> Neither file lists a source file or a target "
                            "framework: the SDK compiles every <code>.cs</code> or <code>.vb</code> in the folder, "
                            "and <code>net10.0</code> comes from the repository's <code>Directory.Build.props</code>. "
                            "The VB app references the C# library exactly the way the C# app does."),
               "5.3 · Two project files — the language is the file extension"),

        {"type": "cards",
         "band": {"title": "5.4 · Five publish options — and how they combine", "note": "deployment view",
                  "tone": "teal"},
         "cards": publish_cards[:3]},
        {"type": "cards", "toc": False,
         "band": {"title": "5.4 · Five publish options (continued)", "note": "deployment view", "tone": "teal"},
         "cards": publish_cards[3:]},

        # ═══════════════════════════ 6 · TRANSFER MAP ═══════════════════════════
        {"type": "story", "heading": "6 · Your transfer map and learning path",
         "html": (
             "<p><b>Most of this track is translation, and the chart below says where it is not.</b> The estimate "
             "for each lesson is the share of its content that a Java/Kotlin, TypeScript and Python engineer "
             "already knows under another name. Two lessons fall well below the rest: asynchronous code, where "
             "C#'s <code>Task</code> model differs from both coroutines and reactive streams, and VB.NET, where "
             "the syntax maps word for word but the semantics quietly change numbers (" + ref(6) + ").</p>"
             "<p><b>The path has four phases.</b> <i>Foundations</i> makes you fluent in the language. "
             "<i>Runtime &amp; codebase</i> covers concurrency, legacy VB and how large solutions are built — the "
             "three things that decide whether you can read an existing estate. <i>Services</i> builds, persists "
             "and tests an ASP.NET Core API. <i>Production</i> secures it with Entra ID and ships it to AWS, and "
             "closes with modernising a Windows / IIS application.</p>"
             "<p><b>One running example ties the samples together.</b> From lesson 02 onward the samples model a "
             "motor-insurance quoting service — vehicles, drivers, quotes, premiums and policies — so each lesson "
             "adds a layer to something you already understand rather than starting a new toy.</p>")},

        {"type": "chart", "heading": "6.1 · Transfer map — how much of each lesson you already know",
         "kind": "progress",
         "args": {"rows": [(f"{r[0]:02d} · {r[2]}", r[5], r[3]) for r in ROSTER], "labelw": 250, "tone": "teal"},
         "caption": "estimate · red below 34% · amber below 67% · the grey line under each bar names what it maps from",
         "note": "<b>Spend the saved time on lessons 05 and 06.</b> Everything above 70% is mostly vocabulary; "
                 "async (55%) and VB.NET (35%) are where a senior engineer from another stack most often writes "
                 "code that compiles and is still wrong."},

        {"type": "mermaid", "inline": True,
         "heading": "6.2 · Learning path",
         "caption": "arrows = recommended order · colours = the four phases",
         "code": ("flowchart TB\n"
                  '  subgraph A["A · Foundations"]\n'
                  "    direction LR\n"
                  '    L1["01 Platform map"]:::a --> L2["02 C# essentials"]:::a --> L3["03 Types, OOP, generics"]:::a --> L4["04 LINQ and functional"]:::a\n'
                  "  end\n"
                  '  subgraph B["B · Runtime and codebase"]\n'
                  "    direction LR\n"
                  '    L5["05 Async and concurrency"]:::b --> L6["06 VB.NET legacy"]:::b --> L7["07 MSBuild and mono-repos"]:::b\n'
                  "  end\n"
                  '  subgraph C["C · Services"]\n'
                  "    direction LR\n"
                  '    L8["08 ASP.NET Core APIs"]:::c --> L9["09 EF Core data"]:::c --> L10["10 Testing and TDD"]:::c\n'
                  "  end\n"
                  '  subgraph D["D · Production"]\n'
                  "    direction LR\n"
                  '    L11["11 Security and Entra ID"]:::d --> L12["12 AWS and modernization"]:::d\n'
                  "  end\n"
                  "  A --> B --> C --> D\n"
                  "  classDef a fill:#c7d2fe,color:#1f2937,stroke:#6366f1;\n"
                  "  classDef b fill:#fde68a,color:#1f2937,stroke:#d97706;\n"
                  "  classDef c fill:#ccfbf1,color:#1f2937,stroke:#0d9488;\n"
                  "  classDef d fill:#fce7f3,color:#1f2937,stroke:#be185d;\n")},

        {"type": "chart", "heading": "6.3 · Where this track's study time goes", "kind": "donut",
         "args": {"data": list(phases.items()), "center": f"{hours} h", "sub": "12 lessons",
                  "width": 560, "height": 220},
         "caption": "suggested hours per learning-path phase · estimate",
         "note": "<b>Foundations take the largest share on purpose.</b> Language and type-system habits are what "
                 "make C# read like C# rather than Java written in C# syntax."},

        {"type": "table", "heading": "6.4 · The twelve lessons",
         "cols": ["#", "Lesson", "Phase", "Hours"],
         "rows": [[f"{r[0]:02d}", f"<b>{r[2]}</b>", r[6], str(r[4])] for r in ROSTER]
                 + [["", "<b>Total</b>", ESTIMATE, f"<b>{hours}</b>"]]},

        figure_heading("6.5 · What carries over, what to learn, what to unlearn"),
        {"type": "threecol", "boxes": [
            {"heading": "Carries over unchanged", "tone": "teal",
             "items": ["OOP, SOLID and dependency-injection thinking",
                       "Unit testing, TDD and coverage discipline",
                       "Microservice, event-driven and cloud architecture",
                       "Build-pipeline and mono-repo design instincts"]},
            {"heading": "Learn fresh", "tone": "indigo",
             "items": ["Value types and struct copy semantics",
                       "<code>async</code>/<code>await</code> and <code>Task</code> as the concurrency model",
                       "LINQ and expression trees",
                       "MSBuild evaluation and <code>Directory.Build.props</code>"]},
            {"heading": "Unlearn", "tone": "rose",
             "items": ["Type-erasure workarounds such as <code>Class&lt;T&gt;</code> tokens",
                       "Checked exceptions and <code>throws</code> clauses",
                       "Hand-written getters and setters — use properties",
                       "“A newer runtime runs any older app” — not across a major version",
                       "“The .exe is my app in native code” — it is a native launcher over IL"]}]},

        # ═══════════════════════════ 7 · HANDS-ON ═══════════════════════════
        {"type": "story", "heading": "7 · Hands-on — build and run the lesson-01 samples",
         "html": (
             "<p><b>Three projects, two languages, one command each.</b> <code>L01.PlatformKit</code> is a C# "
             "class library holding the <code>PlatformReport</code> record and the <code>PlatformProbe</code> that "
             "fills it. <code>L01.CSharpApp</code> and <code>L01.VbApp</code> are console apps that reference it and "
             "print what runtime they are on. Running both is the fastest way to see that the language is a front "
             "end and the runtime is shared.</p>"
             "<p><b>Two repository-level files make every sample build the same way.</b> <code>global.json</code> "
             "pins the SDK; <code>Directory.Build.props</code> sets the target framework, nullable reference "
             "types for C#, <code>Option Strict On</code> for VB, and treats warnings as errors so no sample "
             "teaches a habit the compiler is already complaining about.</p>")},

        listed(code(from_sample("global.json"), heading="7.1 · The two files every sample inherits",
                    note="<b>Pins the SDK, not the runtime.</b> <code>latestFeature</code> uses the highest installed "
                         "10.0 SDK at or above 10.0.401 — 10.0.500 beats 10.0.401 when both are installed — but "
                         "never an 11.0 SDK. Use <code>feature</code> instead if you want the 10.0.4xx band preferred "
                         "and later bands only as a fallback."),
               "7.1 · The two files every sample inherits"),

        code(from_sample("Directory.Build.props"), keep=False,
             note="<b>Read the conditions on the last two groups.</b> "
                  "<code>$(MSBuildProjectExtension)</code> lets one file give C# projects nullable reference "
                  "types and VB projects <code>Option Strict On</code>. The <code>NU1901–NU1904</code> exclusion "
                  "stops a newly published package advisory from failing an old lesson overnight."),

        listed(code(from_text("""
            # the SDK this repository pins (global.json) must be installed
            dotnet --list-sdks

            # from the repository root
            dotnet run --project lesson-01-dotnet-platform-map/samples/L01.CSharpApp
            dotnet run --project lesson-01-dotnet-platform-map/samples/L01.VbApp

            # or build, test and run every sample of this lesson
            python 0-script/verify_samples.py --only 1
            """, "shell"), heading="7.2 · Commands",
                    note="<b>There is no separate restore or build step:</b> <code>dotnet run</code> restores and "
                         "builds first. <code>--project</code> takes a project folder or file. "
                         "<code>dotnet --list-sdks</code> must show 10.0.401 or a later 10.0 SDK; if it shows none, "
                         "see <i>Before you start</i>."),
               "7.2 · Commands"),

        listed(compare(from_text("""
            Hello from C# on .NET 10.0.12
              target    .NETCoreApp,Version=v10.0
              os        Microsoft Windows 10.0.26200
              arch      X64
              server GC False
              JIT on    True
              image     v4.0.30319
              assembly  L01.CSharpApp
              same?     False
              copy?     True
            """, "text", label="Output — C# app", file="captured on the build machine"),
                       from_text("""
            Hello from VB on .NET 10.0.12
              target    .NETCoreApp,Version=v10.0
              os        Microsoft Windows 10.0.26200
              arch      X64
              server GC False
              JIT on    True
              image     v4.0.30319
              assembly  L01.VbApp
              equal?    True
            """, "text", label="Output — VB app", file="captured on the build machine"),
                       heading="7.3 · What you should see",
                       note="<b>Your OS line, architecture and runtime patch number may differ; the other lines "
                            "should not.</b> The first line is the runtime executing the app (10.0.12 here, newer "
                            "than the 10.0.0 the app asked for); <code>target</code> is what it was built for. "
                            "<code>JIT on True</code> means a normal JIT-compiled run — publish with Native AOT and "
                            "it prints False. <code>image v4.0.30319</code> appears on .NET 10 exactly as it did on "
                            ".NET Framework 4."),
               "7.3 · What you should see"),

        {"type": "chart", "heading": "7.4 · Lines of code in the lesson-01 samples",
         "kind": "bar",
         "args": {"data": [("C# library", loc_lib), ("C# app", loc_cs), ("VB app", loc_vb)],
                  "ylabel": "code lines", "tone": "navy", "width": 520, "height": 200},
         "caption": "non-blank, non-comment lines · measured from the sample files when this PDF was built",
         "note": (f"<b>The VB app is {vb_extra} lines longer, and "
                  + ("all of them are" if vb_extra == vb_wrap else f"{vb_wrap} of them are")
                  + " the <code>Module</code> / <code>Sub Main</code> wrapper and its <code>End</code> lines.</b> "
                  "The rest is line-for-line, because VB continues a statement after an open parenthesis without a "
                  "<code>_</code>. " + MEASURED + " from the sample files at build time; line count is a "
                  "readability signal, not a quality score.")},

        {"type": "callout", "variant": "warn", "heading": "⚠ Traps on day one",
         "items": [
             "<b>“A newer runtime runs my older app.”</b> A Java 8 JAR usually runs on a Java 21 JRE, but a "
             "<code>net8.0</code> app does not start on a host that has only .NET 10. The host rolls forward to a "
             "newer patch or minor, never a newer major, unless <code>RollForward</code> is <code>Major</code> — "
             "retarget instead (3.6).",
             "<b><code>ImageRuntimeVersion</code> says v4.0.30319.</b> That is the CLR version string written into "
             "the metadata header, frozen at CLR 4. For the target framework read <code>TargetFrameworkAttribute</code> "
             "(the <code>target</code> line in 7.3, or ILSpy), the <code>tfm</code> in <code>*.runtimeconfig.json</code>, "
             "or the project file. <code>RuntimeInformation.FrameworkDescription</code> tells you which runtime is "
             "executing the process, which can be newer.",
             "<b>The .exe is not your program compiled to native code.</b> <code>L01.VbApp.exe</code> is a small "
             "native apphost that starts the runtime and loads the IL in <code>L01.VbApp.dll</code>. Copying only "
             "the .exe to another machine does not work.",
             "<b>Reading a struct out of a list or a property gives you a copy.</b> Changing that copy leaves the "
             "original untouched, where changing a Java object through its reference would not — " + ref(3) + "."]},

        {"type": "callout", "variant": "ok", "heading": "✔ Checkpoint — you are ready for lesson 02 when",
         "items": [
             f"<code>python 0-script/verify_samples.py --only 1</code> reports {n_proj}/{n_proj} passed on your machine.",
             "You can point at each box in diagram 2.1 and name its JVM counterpart.",
             "Given a project file, you can say which row of table 3.4 it belongs to, what its support status is "
             "and which runtime it will start on.",
             "You can explain why the VB app can compare the C# record but cannot copy it with <code>with</code>."]},

        {"type": "callout", "variant": "summary", "heading": "🔍 Check yourself",
         "items": [
             "Why does an assembly built for .NET 10 report <code>ImageRuntimeVersion</code> v4.0.30319, and where "
             "do you read its target framework instead?",
             "A repository has <code>packages.config</code>, <code>Global.asax</code> and "
             "<code>&lt;TargetFrameworkVersion&gt;v4.7.2</code>. Which runtime does it need, and why can it not run "
             "on a Linux container unchanged?",
             "On what date do .NET 8 and .NET 9 leave support, and why is upgrading from 8 to 9 not a fix?",
             "A host has only the .NET 10 runtime. Does a <code>net8.0</code> app start there, and what are your "
             "two ways out?",
             "Which publish options would you combine for a latency-sensitive Lambda function, and what do you "
             "give up?",
             "What can Visual Basic do with a C# <code>record</code>, and what can it not do?",
             "With <code>rollForward: latestFeature</code> and version 10.0.401 in <code>global.json</code>, which "
             "SDK runs when both 10.0.401 and 10.0.500 are installed?"]},

        {"type": "footer",
         "html": ("<b>Lesson 01 in one line:</b> .NET is a multi-language runtime shaped like the JVM — CoreCLR, IL "
                  "assemblies, a tiered JIT and NuGet — shipped every November, with <b>.NET 10 LTS</b> as the "
                  "target for new work and <b>10 Nov 2026</b> as the end of .NET 8 and 9. Apps roll forward within "
                  "a major version, never across one. C# evolves; VB consumes. "
                  "<br/><b>Next:</b> " + ref(2) + " — the syntax and type-system habits that make C# read like C#.")},
    ]
