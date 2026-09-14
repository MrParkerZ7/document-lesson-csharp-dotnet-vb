# -*- coding: utf-8 -*-
"""Lesson 01 — The .NET Platform Map. Reference implementation of the lesson standard
(1-analysis/spec_lesson-pdfs/lesson-pdf-standard.md): every later lesson follows this shape."""
from lesson_kit import (BUILD_DATE, DIFFERENT, ESTIMATE, MEASURED, RENAMED, SAME, TRAP, VERIFIED,
                        T_CS, T_JVM, T_LEGACY, T_RUNTIME, T_TOOLING, T_VB, code, compare, days_until,
                        from_sample, from_text, legend, link, loc, mapping, pill, style_block)
from lessons.roster import ROSTER, meta, ref

META = meta(
    1,
    subtitle="C# · .NET · VB for a Kotlin/Java, TypeScript & Python architect — runtime, languages, "
             "versions and toolchain",
    objectives=[
        "Explain CoreCLR, IL, tiered JIT, ReadyToRun, Native AOT and NuGet in terms of the JVM parts you already know",
        "Date any .NET codebase from its project file and target framework moniker, and state its support status",
        "Say what C#, VB and F# share on one runtime — and where Visual Basic stops (consumption-only)",
        "Drive the dotnet CLI the way you drive Gradle, Maven or npm, and choose a deployment mode",
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

NET10 = link(".NET releases and support", "https://learn.microsoft.com/en-us/dotnet/core/releases-and-support")
EOS89 = link(".NET 8 and .NET 9 end of support", "https://devblogs.microsoft.com/dotnet/dotnet-8-9-end-of-support/")
LANGS = link(".NET managed languages strategy", "https://learn.microsoft.com/en-us/dotnet/fundamentals/languages")
VBSTRAT = link("Visual Basic language strategy",
               "https://learn.microsoft.com/en-us/dotnet/visual-basic/getting-started/strategy")
CS14 = link("What's new in C# 14", "https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14")


def blocks():
    d89 = days_until(2026, 11, 10)
    eos_value = f"{d89} days" if d89 > 0 else "ended"
    hours = sum(r[4] for r in ROSTER)
    phases = {}
    for r in ROSTER:
        phases[r[6]] = phases.get(r[6], 0) + r[4]
    loc_lib, loc_cs, loc_vb = loc(CS_LIB), loc(CS_APP), loc(VB_APP)

    return [
        style_block(),
        {"type": "toc", "heading": "▤ Contents", "depth": 2,
         "note": "Page numbers are resolved from the rendered PDF. Code panels are cut from the compiled samples."},

        # ═══════════════════════════ 1 · WHY THIS TRACK ═══════════════════════════
        {"type": "story", "heading": "1 · Why this track exists — and who it is written for",
         "html": (
             "<p><b>This track is written for one reader: an architect with eight years across Kotlin/Java, "
             "TypeScript, Python and Dart who has never had to own a .NET codebase — and keeps meeting one.</b> "
             "Insurance and banking estates run a large share of their line-of-business systems on .NET, and the "
             "Windows (IIS) workloads that sit beside ECS Fargate and Lambda in a migration inventory are where "
             ".NET Framework most often hides. Reading that code, sizing its migration and designing its "
             "replacement is architecture work; this track gives you the vocabulary to do it first-hand.</p>"
             "<p><b>The approach is map, don't restart.</b> Every lesson starts from something you have already "
             "built — a Kotlin mono-repo of 50–120+ modules, a Spring WebFlux service, a Python Lambda tuned to "
             "~175 ms cold starts, a 100%-coverage TDD suite, an Entra ID single sign-on integration — and shows "
             "the .NET shape of the same idea. Chips say whether an idea transfers as-is (" + SAME + "), only "
             "changes its name (" + RENAMED + "), genuinely behaves differently (" + DIFFERENT + ") or looks the "
             "same and bites (" + TRAP + ").</p>"
             "<p><b>Why C# and VB together.</b> New .NET work is written in C#. Estates that have been running "
             "since the 2000s also carry Visual Basic .NET, and a modernisation architect has to read it, keep it "
             "running and plan its exit. VB appears beside C# wherever the difference teaches something, and "
             + ref(6) + " is dedicated to it.</p>"
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
              "sub": "C# · Visual Basic · F#"},
             {"label": "This track", "value": f"{hours} h", "tone": "indigo",
              "sub": "12 lessons · study-time estimate"},
             {"label": "Lesson 01 samples", "value": f"{loc_lib + loc_cs + loc_vb} lines", "tone": "navy",
              "sub": "C# + VB · measured at build"}]},

        legend(T_CS, T_VB, T_JVM, T_RUNTIME, T_TOOLING, T_LEGACY),

        {"type": "callout", "variant": "info", "heading": "ℹ How to read every lesson in this track",
         "items": [
             "Each numbered section <b>leads with its point</b>; evidence, code and diagrams follow. Reading only "
             "the first paragraph of each section gives you the whole argument.",
             "Facts that change with releases — support dates, runtime versions, language features — are marked "
             + VERIFIED + " and link to the official source. Judgements such as study hours are marked "
             + ESTIMATE + "; numbers computed from this repository at build time are marked " + MEASURED + ".",
             "Code panels are labelled with the file and <code>#region</code> they were cut from, so you can open "
             "the sample and run it. Java, Kotlin, TypeScript and Python panels are for comparison only and are "
             "not compiled.",
             "Every lesson ends with <b>Check yourself</b> questions. If you can answer them from memory, move on."]},

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
             "Roslyn — the C# and VB compiler, itself written in C# — is javac with a public API that analyzers and "
             "IDEs call directly.</p>"
             "<p><b>Where it stops being the JVM.</b> Generics are <i>reified</i>: <code>List&lt;int&gt;</code> is "
             "a real type at run time and stores unboxed integers. User-defined value types (<code>struct</code>) "
             "live inline, not on the heap. Exceptions are all unchecked. And the compiled output does not have to "
             "stay IL: ReadyToRun pre-compiles it and Native AOT removes the JIT altogether — "
             "GraalVM native-image is the nearest thing you know.</p>")},

        {"type": "mermaid", "inline": True,
         "heading": "2.1 · From source file to running process",
         "caption": "indigo = source · amber = compiler or decision · slate = artefact · teal = runtime path · green = the OS process",
         "code": ("flowchart LR\n"
                  '  CS["Program.cs"]:::src --> ROS["Roslyn<br/>csc and vbc"]:::tool\n'
                  '  VB["Program.vb"]:::src --> ROS\n'
                  '  FS["Program.fs"]:::src --> FSC["F# compiler<br/>fsc"]:::tool\n'
                  '  NUG["NuGet packages<br/>.nupkg"]:::art -.->|"referenced at compile"| ROS\n'
                  '  ROS --> IL["Assembly .dll<br/>IL + metadata"]:::art\n'
                  '  FSC --> IL\n'
                  '  IL --> DEP{"How is it<br/>published?"}:::tool\n'
                  '  DEP -- "framework-dependent" --> JIT["CoreCLR<br/>tiered JIT"]:::run\n'
                  '  DEP -- "ReadyToRun" --> R2R["Pre-compiled code<br/>JIT as fallback"]:::run\n'
                  '  DEP -- "Native AOT" --> AOT["Native executable<br/>no JIT at run time"]:::run\n'
                  '  JIT --> OS["OS process"]:::os\n'
                  '  R2R --> OS\n'
                  '  AOT --> OS\n'
                  "  classDef src fill:#c7d2fe,color:#1f2937,stroke:#6366f1;\n"
                  "  classDef tool fill:#fde68a,color:#1f2937,stroke:#d97706;\n"
                  "  classDef art fill:#e2e8f0,color:#1f2937,stroke:#475569;\n"
                  "  classDef run fill:#ccfbf1,color:#1f2937,stroke:#0d9488;\n"
                  "  classDef os fill:#bbf7d0,color:#1f2937,stroke:#16a34a;\n")},

        {"type": "cards",
         "band": {"title": "2.2 · Runtime pieces — the JVM parts under their .NET names", "note": "runtime view",
                  "tone": "violet"},
         "cards": [
             {"num": 1, "title": "CoreCLR — the Common Language Runtime", "tags": [T_RUNTIME], "pills": [RENAMED],
              "what": "Loads assemblies, verifies and JIT-compiles IL, runs the garbage collector, owns threads and exceptions.",
              "lines": [("JVM", "HotSpot / OpenJ9"),
                        ("Differs", "One runtime serves every .NET language — C#, VB and F# share types directly"),
                        ("Variants", "CoreCLR on servers and desktop; a Mono-derived runtime on Android, iOS and WebAssembly"),
                        ("Old name", "The .NET Framework CLR is a separate, Windows-only runtime — see §3")]},
             {"num": 2, "title": "IL, metadata and assemblies", "tags": [T_RUNTIME], "pills": [RENAMED],
              "what": "The compiler emits intermediate language plus rich type metadata into an assembly.",
              "lines": [("JVM", "Bytecode in .class files, packaged into a JAR"),
                        (".NET", "IL + metadata in one assembly (.dll) that holds many types"),
                        ("Inspect", "ILSpy or ildasm — the javap of .NET"),
                        ("Trap", "The .exe beside your .dll is an <i>apphost</i> launcher; the program is still IL")]},
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
                        ("Sample", "The lesson-01 console app reports <code>ServerGc = False</code> — a console default")]},
             {"num": 5, "title": "Base Class Library and NuGet", "tags": [T_TOOLING], "pills": [RENAMED],
              "what": "A large standard library, and one public package registry.",
              "lines": [("JDK", "java.base, java.net.http, java.time …"),
                        (".NET", "System.*, System.Net.Http, System.Text.Json, System.Collections.Generic"),
                        ("Registry", "nuget.org ≈ Maven Central; dependencies are PackageReference items in the project file"),
                        ("Lock file", "packages.lock.json is opt-in (RestorePackagesWithLockFile) — unlike npm")]}]},

        mapping("2.3 · Concept map — JVM and friends → .NET", [
            ("JVM (HotSpot)", "CoreCLR", "renamed", "Multi-language by design — not a VM for one language"),
            ("Bytecode in .class", "IL in an assembly (.dll)", "renamed", "An assembly is closer to a JAR than to a .class"),
            ("JAR / fat JAR", "Assembly / self-contained publish", "renamed", "The .exe apphost is a launcher, not a native build"),
            ("JDK class library", "Base Class Library (BCL)", "same", "Namespaces start with <code>System.</code>"),
            ("Maven Central / npm", "NuGet (nuget.org)", "renamed", "No separate pom or package.json — it is all in the project file"),
            ("pom.xml / build.gradle.kts", ".csproj / .vbproj (MSBuild)", "different", "Declarative XML; shared logic goes in Directory.Build.props — " + ref(7)),
            ("Generics with type erasure", "Reified generics", "trap", "<code>typeof(T)</code> works; <code>List&lt;int&gt;</code> never boxes"),
            ("Primitive wrappers, autoboxing", "Value types (<code>struct</code>)", "different", "Mutating a copy of a struct changes nothing — a classic bug"),
            ("Checked exceptions", "Unchecked exceptions only", "different", "No <code>throws</code>; document with <code>/// &lt;exception&gt;</code>"),
            ("Kotlin data class / Java record", "C# <code>record</code>", "same", "<code>with</code> = <code>copy()</code>; VB can use records but not declare them"),
            ("Kotlin coroutines / WebFlux", "<code>async</code>/<code>await</code> + <code>Task</code>", "different", ref(5)),
            ("GraalVM native-image", "Native AOT", "same", "Same closed-world trade-off: reflection needs annotations"),
            ("SDKMAN / .nvmrc / pyenv", "global.json", "renamed", "Pins the SDK, not the runtime; <code>rollForward</code> decides"),
            ("Spring Boot", "ASP.NET Core", "different", "The DI container is built in — " + ref(8)),
            ("Java EE app on WebSphere", "ASP.NET on IIS (.NET Framework)", "same", "<code>System.Web</code> does not exist on modern .NET — port, don't lift"),
            ("JUnit + Mockito", "xUnit / NUnit / MSTest + NSubstitute / Moq", "renamed", ref(10)),
        ]),

        # ═══════════════════════════ 3 · VERSIONS ═══════════════════════════
        {"type": "story", "heading": "3 · Versions — how to read a .NET codebase's age",
         "html": (
             "<p><b>There are two .NETs, and a codebase's project file tells you which one it needs in the first "
             "ten lines.</b> <i>.NET Framework</i> (1.0 in 2002 → 4.8.1 in 2022) is Windows-only, ships as a "
             "Windows component and receives no new major versions. <i>.NET</i> — born as .NET Core 1.0 in 2016 and "
             "renamed at .NET 5 in 2020, skipping “4” to avoid confusion — is cross-platform, open source and ships "
             "every November.</p>"
             "<p><b>The release rhythm is predictable.</b> Even-numbered releases are Long Term Support "
             "(36 months); odd-numbered releases are Standard Term Support, extended from 18 to 24 months starting "
             "with .NET 9. That extension makes .NET 8 (LTS) and .NET 9 (STS) leave support on the <b>same day, "
             "10 November 2026</b>. .NET 10 shipped on 11 November 2025 and is supported until 14 November 2028 "
             "(" + NET10 + " · " + EOS89 + ").</p>"
             "<p><b>What that means for an architect in September 2026.</b> New work targets <code>net10.0</code>. "
             "Anything on <code>net8.0</code> or <code>net9.0</code> has a hard upgrade deadline this quarter. "
             "Anything on .NET Core 3.1, .NET 5, 6 or 7 is already unsupported. And a .NET Framework 4.8.1 "
             "application is still supported — for as long as the Windows version it runs on is — but it will "
             "never get a new runtime feature, which is a migration argument rather than a security one.</p>")},

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
             "caption": "months from GA to end of support · verified against Microsoft's lifecycle pages",
             "note": "<b>Even = 36 months, odd = 18 → 24.</b> The STS extension is why .NET 9 does not buy "
                     "you any time over .NET 8: both end on 10 Nov 2026."},
            {"heading": "3.3 · Where this track's study time goes", "kind": "donut",
             "args": {"data": list(phases.items()), "center": f"{hours} h", "sub": "12 lessons",
                      "width": 390, "height": 220},
             "caption": "suggested hours per learning-path phase · estimate",
             "note": "<b>Foundations take the largest share on purpose.</b> Language and type-system habits are "
                     "what make C# read like C# rather than Java written in C# syntax."}]},

        {"type": "table", "heading": "3.4 · Target framework monikers you will find in project files",
         "cols": ["TFM", "What it targets", "Where you meet it", "Status"],
         "rows": [
             ["<code>net48</code> · <code>net481</code>", ".NET Framework 4.8 / 4.8.1 — Windows only",
              "ASP.NET, WCF and WinForms apps; IIS on Windows servers", pill("Legacy · follows Windows", "slate")],
             ["<code>netstandard2.0</code>", "An API contract, not a runtime",
              "Shared libraries that must load in both .NET Framework and modern .NET", pill("Bridge", "sky")],
             ["<code>netcoreapp3.1</code>", ".NET Core 3.1", "First-wave migrations", pill("Ended Dec 2022", "red")],
             ["<code>net6.0</code> · <code>net7.0</code>", ".NET 6 LTS · .NET 7 STS", "Services built 2021–2023",
              pill("Ended 2024", "red")],
             ["<code>net8.0</code> · <code>net9.0</code>", ".NET 8 LTS · .NET 9 STS", "Most services running today",
              pill("Ends 10 Nov 2026", "amber")],
             ["<code>net10.0</code>", ".NET 10 LTS", "New work — every sample in this track",
              pill("Supported to Nov 2028", "green")],
             ["<code>net10.0-windows</code>", ".NET 10 plus Windows-only APIs", "Modernised WinForms / WPF desktop apps",
              pill("Windows only", "violet")]]},

        {"type": "mermaid", "inline": True,
         "heading": "3.5 · What am I looking at? — dating a legacy repository",
         "caption": "indigo = start · amber = question · green = modern · sky = bridge · slate = .NET Framework · rose = not .NET at all",
         "code": ("flowchart LR\n"
                  '  S["Open the<br/>repository"]:::start --> Q0{"Any .csproj<br/>or .vbproj?"}:::q\n'
                  '  Q0 -- "no: only .vbp<br/>.frm .bas files" --> VB6["Visual Basic 6<br/>COM, not .NET: rewrite"]:::bad\n'
                  '  Q0 -- "yes" --> Q1{"File starts with<br/>Project Sdk=...?"}:::q\n'
                  '  Q1 -- "yes, SDK-style" --> Q2{"TargetFramework?"}:::q\n'
                  '  Q1 -- "no: ToolsVersion,<br/>Compile Include lists" --> Q3{"web.config + Global.asax<br/>or .svc files?"}:::q\n'
                  '  Q2 -- "net5.0 to net10.0" --> MOD["Modern .NET<br/>cross-platform"]:::good\n'
                  '  Q2 -- "netstandard2.0" --> STD["Shared library<br/>loads in both worlds"]:::bridge\n'
                  '  Q2 -- "net48" --> HALF["Framework app<br/>part-way migrated"]:::bridge\n'
                  '  Q3 -- "yes" --> IIS["ASP.NET or WCF on IIS<br/>System.Web: port, do not lift"]:::legacy\n'
                  '  Q3 -- "no" --> DESK["WinForms, console<br/>or Windows service"]:::legacy\n'
                  "  classDef start fill:#c7d2fe,color:#1f2937,stroke:#6366f1;\n"
                  "  classDef q fill:#fde68a,color:#1f2937,stroke:#d97706;\n"
                  "  classDef good fill:#bbf7d0,color:#1f2937,stroke:#16a34a;\n"
                  "  classDef bridge fill:#e0f2fe,color:#1f2937,stroke:#0369a1;\n"
                  "  classDef legacy fill:#e2e8f0,color:#1f2937,stroke:#475569;\n"
                  "  classDef bad fill:#fce7f3,color:#1f2937,stroke:#be185d;\n")},

        {"type": "callout", "variant": "warn", "heading": "⚠ The 10 November 2026 double cut-off",
         "items": [
             "<b>.NET 8 (LTS) and .NET 9 (STS) stop receiving security fixes on the same day.</b> Upgrading from 8 to "
             "9 buys nothing; the only supported destination is .NET 10.",
             "<b>Start the inventory with the TFM, not the language.</b> A VB.NET service on <code>net8.0</code> is a "
             "one-line retarget plus a test run; a C# service on <code>net48</code> is a port.",
             "<b>Check the container base images too.</b> An app retargeted to <code>net10.0</code> but still built on "
             "an 8.0 runtime image is still running .NET 8.",
             "Source: " + EOS89 + "."]},

        # ═══════════════════════════ 4 · LANGUAGES ═══════════════════════════
        {"type": "story", "heading": "4 · Three languages, one runtime",
         "html": (
             "<p><b>C# is where .NET evolves; Visual Basic is deliberately stable; F# is the functional "
             "option.</b> C# 14 ships with .NET 10 and keeps adding syntax — extension members, the "
             "<code>field</code> keyword, null-conditional assignment (" + CS14 + "). Microsoft's stated strategy "
             "for Visual Basic is <i>consumption-only</i>: VB code can use new .NET APIs and types, but the "
             "language will generally not add syntax to <i>define</i> things that need new language support "
             "(" + VBSTRAT + " · " + LANGS + ").</p>"
             "<p><b>What that means in practice.</b> A VB project can reference a C# library and call it as if it "
             "were written in VB — same types, same exceptions, same debugger. It can read a C# "
             "<code>record</code>, compare it and pass it on; it cannot declare a record or use <code>with</code> "
             "to copy one. The samples below are the proof: one C# class library, consumed unchanged by a C# "
             "console app and a VB console app.</p>"
             "<p><b>What an architect does with this.</b> Mixed-language solutions are normal and cheap — there is "
             "no FFI to design. Migration from VB to C# can therefore be incremental: new code in C# libraries, "
             "old VB calling it, one project converted at a time. " + ref(6) + " turns this into a plan.</p>")},

        code(from_sample(CS_LIB, "report-record"),
             heading="4.1 · The shared C# library — a positional record",
             note="<b>One declaration gives you</b> a constructor, read-only properties, value equality, "
                  "<code>ToString()</code> and deconstruction — Kotlin's <code>data class</code> in C#. Note "
                  "<code>MetadataVersion</code>: every modern .NET assembly reports <code>v4.0.30319</code>, the "
                  "metadata format version, not the .NET version."),

        compare(from_sample(CS_APP, "program"), from_sample(VB_APP, "program"),
                heading="4.2 · The same program in C# and in Visual Basic",
                note="<b>Same library, same types, same output.</b> C# uses top-level statements; VB wraps the code "
                     "in a <code>Module</code> with <code>Sub Main</code>. VB is case-insensitive and "
                     "line-oriented — the <code>Capture(</code> call continues on the next line because it ends "
                     "with an open parenthesis."),

        compare(from_text("""
            data class PlatformReport(
                val framework: String,
                val serverGc: Boolean,
                // ...
            )

            val flipped = r.copy(serverGc = !r.serverGc)
            println("  same?     ${r == flipped}")   // false
            println("  copy?     ${r == r.copy()}")  // true
            """, "kotlin", file="the idea you already know"),
                from_sample(CS_APP, "record-equality"),
                heading="4.3 · Value equality and non-destructive copy — Kotlin vs C#",
                note="<b>" + SAME + " idea, different keyword.</b> <code>with { }</code> is <code>copy()</code>. "
                     "Because records compare by value, <code>r == r with { }</code> is true even though it is a "
                     "new object."),

        code(from_sample(VB_APP, "record-equality"),
             heading="4.4 · What Visual Basic can do with that C# record",
             note="<b>Consumption-only in one screen.</b> VB calls <code>Equals</code> and reads every property; "
                  "there is no VB syntax for a <code>with</code> copy. For a migration plan this is good news: "
                  "shared models can move to C# first without breaking their VB callers."),

        {"type": "chart", "heading": "4.5 · Language feature matrix — C#, VB and the languages you know",
         "kind": "heatmap",
         "args": {"rows": ["Records / data classes", "Non-destructive copy", "Null-safety in types",
                           "Pattern-matching switch", "async / await style", "Language-integrated query",
                           "Runtime (reified) generics", "User-defined value types", "Properties",
                           "Extension members", "XML literals"],
                  "cols": ["C# 14", "VB", "Java 21", "Kotlin 2"],
                  "matrix": [[2, 1, 2, 2], [2, 0, 0, 2], [2, 0, 0, 2], [2, 1, 2, 1], [2, 2, 1, 2],
                             [2, 2, 1, 1], [2, 2, 0, 1], [2, 2, 0, 1], [2, 2, 0, 2], [2, 1, 0, 2],
                             [0, 2, 0, 0]],
                  "cell": 44, "tone": "violet", "fmt": lambda v: {2: "yes", 1: "some", 0: "—"}[int(v)]},
         "caption": "yes = first-class syntax · some = library, subset or consume-only · — = none · a rubric, not a benchmark",
         "note": "<b>VB matches C# on everything that existed before 2015 and stops there.</b> Its gaps are the "
                 "post-2019 C# features (records, <code>with</code>, nullable reference types, pattern matching). "
                 "Its one unique row — XML literals — is also why some legacy VB code is hard to port mechanically. "
                 "Java's “some” async is virtual threads and <code>CompletableFuture</code>; Kotlin's “some” "
                 "generics are <code>inline reified</code> functions."},

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
                       "“The .exe is native code” — it is an apphost over IL"]}]},

        # ═══════════════════════════ 5 · TOOLCHAIN ═══════════════════════════
        {"type": "story", "heading": "5 · The toolchain — one CLI, five ways to ship",
         "html": (
             "<p><b>The <code>dotnet</code> CLI is Gradle, npm and SDKMAN in one executable.</b> It scaffolds from "
             "templates, restores packages, builds, tests, runs, packs and publishes. Its SDK version is pinned "
             "per repository by <code>global.json</code> — this repository pins 10.0.401 and lets later feature "
             "bands roll forward. Restore is implicit in build, test and run, so the everyday loop is two "
             "commands.</p>"
             "<p><b>A project file is declarative MSBuild, not a script.</b> An SDK-style <code>.csproj</code> or "
             "<code>.vbproj</code> is often five lines, because the SDK supplies defaults: every source file in the "
             "folder is compiled, packages restore from nuget.org, output goes to <code>bin/</code>. Shared "
             "settings live in <code>Directory.Build.props</code>, which MSBuild imports for every project beneath "
             "it — this repository uses one to put all build output in <code>.build/artifacts</code>. "
             + ref(7) + " goes deep.</p>"
             "<p><b>Publishing is a decision, not a default.</b> The same IL can ship framework-dependent, "
             "self-contained, as a single file, pre-compiled with ReadyToRun, or as a Native AOT executable. The "
             "choice trades start-up time and package size against compatibility with reflection-heavy "
             "libraries — the same trade you made choosing between a JAR on a JRE and a GraalVM native image, "
             "and the one you tuned when you got Python Lambda packages down to 55 KB.</p>")},

        {"type": "table", "heading": "5.1 · The dotnet CLI next to the tools you use today",
         "cols": ["Task", "Maven / Gradle", "npm", ".NET CLI", "Note"],
         "rows": [
             ["Scaffold", "<code>gradle init</code>", "<code>npm init</code>",
              "<code>dotnet new console -lang VB</code>", "<code>dotnet new list</code> shows templates"],
             ["Restore dependencies", "implicit", "<code>npm install</code>", "<code>dotnet restore</code>",
              "implicit in build, test and run"],
             ["Compile", "<code>gradle build</code>", "<code>npm run build</code>",
              "<code>dotnet build -c Release</code>", "Debug is the default configuration"],
             ["Test", "<code>gradle test</code>", "<code>npm test</code>", "<code>dotnet test</code>",
              "works with xUnit, NUnit and MSTest — " + ref(10)],
             ["Run", "<code>gradle bootRun</code>", "<code>npm start</code>", "<code>dotnet run</code>",
              ".NET 10 also runs a single file: <code>dotnet run app.cs</code>"],
             ["Package an app", "<code>gradle bootJar</code>", "—", "<code>dotnet publish</code>",
              "<code>-r linux-x64 --self-contained</code> · <code>-p:PublishAot=true</code>"],
             ["Package a library", "<code>gradle publish</code>", "<code>npm publish</code>",
              "<code>dotnet pack</code> · <code>dotnet nuget push</code>", "produces a .nupkg"],
             ["Add a dependency", "edit the build file", "<code>npm install x</code>",
              "<code>dotnet add package X</code>", "writes a PackageReference"],
             ["Global tools", "SDKMAN candidates", "<code>npm i -g</code>", "<code>dotnet tool install -g</code>",
              "repo-local tools: <code>dotnet-tools.json</code>"],
             ["Format / lint", "Spotless · ktlint", "Prettier · ESLint", "<code>dotnet format</code>",
              "rules come from <code>.editorconfig</code>"]]},

        compare(from_sample(f"{L}/L01.CSharpApp/L01.CSharpApp.csproj"),
                from_sample(f"{L}/L01.VbApp/L01.VbApp.vbproj"),
                heading="5.2 · Two project files — the language is the file extension",
                note="<b>The same MSBuild, the same SDK.</b> Neither file lists a source file or a target "
                     "framework: the SDK compiles every <code>.cs</code> or <code>.vb</code> in the folder, and "
                     "<code>net10.0</code> comes from the repository's <code>Directory.Build.props</code>. The VB "
                     "app references the C# library exactly the way the C# app does."),

        {"type": "cards",
         "band": {"title": "5.3 · Five ways to ship the same code", "note": "deployment view", "tone": "teal"},
         "cards": [
             {"num": 6, "title": "Framework-dependent", "tags": [T_TOOLING], "pills": [SAME],
              "what": "Ship your IL and dependencies; the machine supplies the .NET runtime.",
              "lines": [("Like", "A thin JAR on an installed JRE · a Python zip on a Lambda runtime"),
                        ("Size", "Smallest package — the lesson-01 VB app is a few kilobytes of IL"),
                        ("Pick when", "AWS Lambda managed runtime, containers on the aspnet image, servers you patch")]},
             {"num": 7, "title": "Self-contained", "tags": [T_TOOLING], "pills": [RENAMED],
              "what": "Ship the runtime with the app, for one runtime identifier such as linux-x64.",
              "lines": [("Like", "A jlink runtime image"),
                        ("Cost", "Tens of megabytes more; runtime patches arrive only when you redeploy"),
                        ("Pick when", "Hosts where you cannot install or control the runtime")]},
             {"num": 8, "title": "Single-file", "tags": [T_TOOLING], "pills": [RENAMED],
              "what": "Bundle the app (and optionally the runtime) into one executable file.",
              "lines": [("Like", "A fat JAR with a native launcher"),
                        ("Note", "Still JIT-compiled at start-up unless combined with ReadyToRun"),
                        ("Pick when", "CLI tools and agents you copy onto machines")]},
             {"num": 9, "title": "ReadyToRun", "tags": [T_RUNTIME], "pills": [DIFFERENT],
              "what": "Pre-compile IL to native code at publish time and keep the JIT as a fallback.",
              "lines": [("Like", "An ahead-of-time compilation cache — faster start, same compatibility"),
                        ("Cost", "Larger assemblies; tier-1 JIT still re-optimises hot code"),
                        ("Pick when", "Start-up matters but you depend on reflection-heavy libraries")]},
             {"num": 10, "title": "Native AOT", "tags": [T_RUNTIME], "pills": [SAME],
              "what": "Compile the whole app to a native executable — no JIT and no IL at run time.",
              "lines": [("Like", "GraalVM native-image — the same closed-world trade-off"),
                        ("For you", "The .NET answer to the ~175 ms cold starts you tuned in Python Lambdas — " + ref(12)),
                        ("Limits", "No run-time code generation; reflection needs trimming annotations"),
                        ("Tell-tale", "<code>RuntimeFeature.IsDynamicCodeCompiled</code> returns false")]}]},

        {"type": "mermaid", "inline": True,
         "heading": "5.4 · What happens on dotnet run (simplified)",
         "caption": "the muxer finds the SDK through global.json; the host finds the runtime through runtimeconfig.json",
         "code": ("sequenceDiagram\n"
                  "  autonumber\n"
                  "  participant U as You\n"
                  "  participant M as dotnet muxer\n"
                  "  participant S as SDK and MSBuild\n"
                  "  participant H as hostfxr and hostpolicy\n"
                  "  participant C as CoreCLR\n"
                  "  U->>M: dotnet run --project L01.VbApp\n"
                  "  M->>S: resolve SDK from global.json, restore, build\n"
                  "  S-->>M: L01.VbApp.dll + runtimeconfig.json + deps.json\n"
                  "  M->>H: launch the app\n"
                  "  H->>H: pick the shared framework from runtimeconfig.json\n"
                  "  H->>C: load runtime, resolve dependencies from deps.json\n"
                  "  C->>C: JIT-compile Sub Main and run it\n"
                  "  C-->>U: Hello from VB on .NET 10\n")},

        # ═══════════════════════════ 6 · TRANSFER MAP ═══════════════════════════
        {"type": "story", "heading": "6 · Your transfer map and learning path",
         "html": (
             "<p><b>Most of this track is translation, and the chart below says where it is not.</b> The estimate "
             "for each lesson is the share of its content that a Java/Kotlin, TypeScript and Python engineer "
             "already knows under another name. Two lessons fall well below the rest: asynchronous code, where "
             "C#'s <code>Task</code> model differs from both coroutines and reactive streams, and VB.NET, where the "
             "syntax itself is new.</p>"
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

        {"type": "table", "heading": "6.3 · The twelve lessons",
         "cols": ["#", "Lesson", "Maps from", "Phase", "Hours", "Transfer"],
         "rows": [[f"{r[0]:02d}", f"<b>{r[2]}</b>", r[3], r[6], str(r[4]), f"{r[5]}%"] for r in ROSTER]
                 + [["", "<b>Total</b>", "", "", f"<b>{hours}</b>", ESTIMATE]]},

        # ═══════════════════════════ 7 · HANDS-ON ═══════════════════════════
        {"type": "story", "heading": "7 · Hands-on — build and run the lesson-01 samples",
         "html": (
             "<p><b>Three projects, two languages, one command each.</b> <code>L01.PlatformKit</code> is a C# "
             "class library holding the <code>PlatformReport</code> record. <code>L01.CSharpApp</code> and "
             "<code>L01.VbApp</code> are console apps that reference it and print what runtime they are on. "
             "Running both is the fastest way to see that the language is a front end and the runtime is "
             "shared.</p>"
             "<p><b>Two repository-level files make every sample build the same way.</b> <code>global.json</code> "
             "pins the SDK; <code>Directory.Build.props</code> sets the target framework, nullable reference "
             "types for C#, <code>Option Strict On</code> for VB, and treats warnings as errors so no sample "
             "teaches a habit the compiler is already complaining about.</p>")},

        code(from_sample("global.json"), heading="7.1 · The two files every sample inherits",
             note="<b>Pins the SDK, not the runtime.</b> <code>latestFeature</code> accepts 10.0.402 or 10.0.500 "
                  "if 10.0.401 is missing, but never an 11.0 SDK."),

        code(from_sample("Directory.Build.props"),
             note="<b>Read the conditions on the last two groups.</b> "
                  "<code>$(MSBuildProjectExtension)</code> lets one file give C# projects nullable reference "
                  "types and VB projects <code>Option Strict On</code>. The <code>NU1901–NU1904</code> exclusion "
                  "stops a newly published package advisory from failing an old lesson overnight."),

        code(from_text("""
            # the SDK this repository pins (global.json) must be installed
            dotnet --list-sdks

            # from the repository root
            dotnet run --project lesson-01-dotnet-platform-map/samples/L01.CSharpApp
            dotnet run --project lesson-01-dotnet-platform-map/samples/L01.VbApp

            # or build, test and run every sample of this lesson
            python 0-script/verify_samples.py --only 1
            """, "shell"), heading="7.2 · Commands"),

        compare(from_text("""
            Hello from C# on .NET 10.0.12
              os        Microsoft Windows 10.0.26200
              arch      X64
              JIT on    True
              metadata  v4.0.30319
              assembly  L01.CSharpApp
              same?     False
              copy?     True
            """, "text", label="Output — C# app", file="captured on the build machine"),
                from_text("""
            Hello from VB on .NET 10.0.12
              os        Microsoft Windows 10.0.26200
              arch      X64
              JIT on    True
              metadata  v4.0.30319
              assembly  L01.VbApp
              equal?    True
            """, "text", label="Output — VB app", file="captured on the build machine"),
                heading="7.3 · What you should see",
                note="<b>Your OS line will differ; the rest should not.</b> <code>JIT on True</code> means a normal "
                     "JIT-compiled run — publish with Native AOT and it prints False. "
                     "<code>metadata v4.0.30319</code> appears on .NET 10 exactly as it did on .NET Framework 4."),

        {"type": "chart", "heading": "7.4 · Lines of code in the lesson-01 samples",
         "kind": "bar",
         "args": {"data": [("C# library", loc_lib), ("C# app", loc_cs), ("VB app", loc_vb)],
                  "ylabel": "code lines", "tone": "navy", "width": 520, "height": 200},
         "caption": "non-blank, non-comment lines · measured from the sample files when this PDF was built",
         "note": "<b>The VB app is longer for the same behaviour</b> — a <code>Module</code>/<code>Sub Main</code> "
                 "wrapper, explicit line continuations and <code>End</code> keywords. Line count is a readability "
                 "signal, not a quality score: VB's verbosity is part of why it stays approachable."},

        {"type": "callout", "variant": "warn", "heading": "⚠ Three traps on day one",
         "items": [
             "<b>“No .NET SDKs were found.”</b> A runtime-only install (for example a Desktop Runtime under "
             "Program Files) earlier on PATH shadows the SDK. <code>dotnet --list-sdks</code> must list 10.0.x; "
             "if not, put the SDK folder first on PATH or set <code>DOTNET_ROOT</code>.",
             "<b><code>ImageRuntimeVersion</code> says v4.0.30319.</b> That is the metadata format, unchanged since "
             ".NET Framework 4. Read the target framework from the project file or "
             "<code>RuntimeInformation.FrameworkDescription</code>, never from assembly metadata.",
             "<b>The .exe is not native code.</b> <code>L01.VbApp.exe</code> is an apphost that starts the runtime "
             "and loads <code>L01.VbApp.dll</code>. Copying only the .exe to another machine does not work."]},

        {"type": "callout", "variant": "ok", "heading": "✔ Checkpoint — you are ready for lesson 02 when",
         "items": [
             "<code>python 0-script/verify_samples.py --only 1</code> reports 3/3 passed on your machine.",
             "You can point at each box in diagram 2.1 and name its JVM counterpart.",
             "Given a project file, you can say which row of table 3.4 it belongs to and what its support status is.",
             "You can explain why the VB app can compare the C# record but cannot copy it with <code>with</code>."]},

        {"type": "callout", "variant": "summary", "heading": "🔍 Check yourself",
         "items": [
             "Why does an assembly built for .NET 10 report <code>ImageRuntimeVersion</code> v4.0.30319, and what "
             "should you read instead to find its target framework?",
             "A repository has <code>packages.config</code>, <code>Global.asax</code> and "
             "<code>&lt;TargetFrameworkVersion&gt;v4.7.2</code>. Which runtime does it need, and why can it not run "
             "on a Linux container unchanged?",
             "On what date do .NET 8 and .NET 9 leave support, and why is upgrading from 8 to 9 not a fix?",
             "Which publish mode would you choose for a latency-sensitive Lambda function, and what do you give up?",
             "What can Visual Basic do with a C# <code>record</code>, and what can it not do?",
             "Which file pins the SDK version for a repository, and which file shares build settings across its "
             "projects?"]},

        {"type": "footer",
         "html": ("<b>Lesson 01 in one line:</b> .NET is a multi-language runtime shaped like the JVM — CoreCLR, IL "
                  "assemblies, a tiered JIT and NuGet — shipped every November, with <b>.NET 10 LTS</b> as the "
                  "target for new work and <b>10 Nov 2026</b> as the end of .NET 8 and 9. C# evolves; VB consumes. "
                  "<br/><b>Next:</b> " + ref(2) + " — the syntax and type-system habits that make C# read like C#.")},
    ]
