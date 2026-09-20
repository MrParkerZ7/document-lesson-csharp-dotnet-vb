# -*- coding: utf-8 -*-
"""Lesson 05 — Async, Tasks & Concurrency. Built to 1-analysis/spec_lesson-pdfs/_standard.md; shape follows
lesson_01.py. Unit spec: 1-analysis/spec_lesson-pdfs/lesson-05-async-concurrency.md"""
import re

from lesson_kit import (DIFFERENT, ESTIMATE, MEASURED, RENAMED, REPO, SAME, TRAP, VERIFIED,
                        T_ARCH, T_CS, T_JVM, T_RUNTIME, esc, from_sample, from_text,
                        legend, link, loc, mapping, snippet, style_block)
from lesson_kit import code as _kit_code, compare as _kit_compare
from lessons.roster import ROSTER, meta, ref, row

META = meta(
    5,
    subtitle="Task and await, cancellation, fan-out, async streams, channels and shared state — for an "
             "engineer who ships Kotlin coroutines, Spring WebFlux and Node",
    objectives=[
        "Explain what await compiles to and which thread runs the code after it — in ASP.NET Core, a console "
        "app and a UI app — in terms of Kotlin dispatchers and the Node event loop",
        "Pass CancellationToken through a call chain, combine a caller token with a per-call deadline, and tell "
        "a timeout from a caller cancellation",
        "Fan out to ~30 rating partners with Task.WhenAll and Task.WhenEach, tolerating slow and failing partners",
        "Stream with IAsyncEnumerable and build a bounded Channel pipeline with back-pressure",
        "Choose Interlocked, Lock, SemaphoreSlim or a concurrent collection, and test timing code "
        "deterministically with FakeTimeProvider",
        "Spot async void, sync-over-async and fire-and-forget, and name the async constructs Visual Basic rejects",
    ],
    maps_from="Kotlin coroutines (suspend, async/awaitAll, coroutineScope, withTimeout, Flow, Channel), Spring "
              "WebFlux and Reactor Mono/Flux, CompletableFuture, the Node.js event loop with Promise.all and "
              "AbortController, and asyncio in Python Lambdas — plus the partner fan-out and notification "
              "fan-in you designed for a motor-insurance platform with ~30 external partners.",
)

L = "lesson-05-async-concurrency/samples"
RATES = f"{L}/L05.PartnerRates"
FANOUT = f"{RATES}/RateFanOut.cs"
STATS = f"{RATES}/RateStats.cs"
PARTNER = f"{RATES}/SimulatedPartner.cs"
TESTS = f"{L}/L05.PartnerRates.Tests"
FANOUT_TESTS = f"{TESTS}/FanOutTests.cs"
DESK_CS = f"{L}/L05.RateDesk/Program.cs"
DESK_VB = f"{L}/L05.VbAsync/Program.vb"
NOTIFY = f"{L}/L05.Notifications"
TRAPS = f"{L}/L05.AsyncTraps/Traps.cs"
VBRULES = f"{L}/L05.VbRules.Tests"
PROJECTS = [("L05.PartnerRates", "PartnerRates"), ("L05.PartnerRates.Tests", "PartnerRates.Tests"),
            ("L05.RateDesk", "RateDesk"), ("L05.VbAsync", "VbAsync (VB)"), ("L05.Notifications", "Notifications"),
            ("L05.AsyncTraps", "AsyncTraps"), ("L05.VbRules.Tests", "VbRules.Tests")]

# ── official sources ─────────────────────────────────────────────────────────────────────────────────
ASYNC = link("Asynchronous programming with async and await",
             "https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/")
VALUETASK = link("ValueTask<TResult>", "https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.valuetask-1")
RETURNS = link("async return types",
               "https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/async-return-types")
CONFIGAWAIT = link("ConfigureAwait FAQ", "https://devblogs.microsoft.com/dotnet/configureawait-faq/")
RUNTIMEASYNC = link(".NET 11 Preview 4 runtime notes",
                    "https://github.com/dotnet/core/blob/main/release-notes/11.0/preview/preview4/runtime.md")
CANCEL = link("cancellation in managed threads",
              "https://learn.microsoft.com/en-us/dotnet/standard/threading/cancellation-in-managed-threads")
WAITASYNC = link("Task.WaitAsync", "https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.task.waitasync")
WHENALL = link("Task.WhenAll", "https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.task.whenall")
WHENEACH = link("Task.WhenEach", "https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.task.wheneach")
PFOREACH = link("Parallel.ForEachAsync",
                "https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.parallel.foreachasync")
CHANNELS = link("Channels", "https://learn.microsoft.com/en-us/dotnet/core/extensions/channels")
ASYNCLINQ = link("System.Linq.AsyncEnumerable in .NET 10",
                 "https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/10.0/asyncenumerable")
LOCKSTMT = link("the lock statement",
                "https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/statements/lock")
LOCKTYPE = link("System.Threading.Lock", "https://learn.microsoft.com/en-us/dotnet/api/system.threading.lock")
TIMEPROVIDER = link("What is TimeProvider", "https://learn.microsoft.com/en-us/dotnet/standard/datetime/timeprovider-overview")
BESTPRACTICE = link("ASP.NET Core best practices",
                    "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/best-practices")
STARVATION = link("debug ThreadPool starvation",
                  "https://learn.microsoft.com/en-us/dotnet/core/diagnostics/debug-threadpool-starvation")
UNOBSERVED = link("TaskScheduler.UnobservedTaskException",
                  "https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.taskscheduler.unobservedtaskexception")
VBAWAIT = link("Await operator (Visual Basic)",
               "https://learn.microsoft.com/en-us/dotnet/visual-basic/language-reference/operators/await-operator")
CSHIST = link("The history of C#", "https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-version-history")
KOTLIN = link("Kotlin coroutine basics", "https://kotlinlang.org/docs/coroutines-basics.html")
KOTLINFLOW = link("kotlinx flow builder",
                  "https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/flow.html")
PYTASKGROUP = link("asyncio.TaskGroup", "https://docs.python.org/3/library/asyncio-task.html")
GREENTHREADS = link("the .NET green-threads experiment: results",
                    "https://github.com/dotnet/runtimelab/issues/2398")
GETORADD = link("ConcurrentDictionary.GetOrAdd",
                "https://learn.microsoft.com/en-us/dotnet/api/system.collections.concurrent.concurrentdictionary-2.getoradd")

# ── captured from real runs on the build machine (Windows x64, .NET 10.0.12 runtime) — see unit spec §4 ──
DESK_CS_OUT = """
    C#  30 partners, timeout 250 ms
      quoted 19, timed out 8, failed 3
      best   P12 12,090.00 THB
      wall   263 ms concurrently, 4,982 ms one after another
      pool   9 thread-pool threads
      first answers, in completion order:
        P18 quoted 15,210.00 THB
        P04 failed (P04: 503)
        P08 quoted 15,860.00 THB
        P29 quoted 12,155.00 THB
        P22 quoted 17,290.00 THB
      cancelled the partners still working
    """
DESK_VB_OUT = """
    VB  30 partners, timeout 250 ms
      quoted 19, timed out 8, failed 3
      best   P12 12,090.00 THB
      wall   276 ms concurrently, 4,982 ms one after another
      pool   5 thread-pool threads
      first answers, in completion order:
        P18 quoted 15,210.00 THB
        P04 failed (P04: 503)
        P08 quoted 15,860.00 THB
        P01 quoted 15,145.00 THB
        P22 quoted 17,290.00 THB
      cancelled the partners still working
    """
NOTIFY_OUT = """
    36 notifications, intake capacity 8, lane capacity 4
      Sms     9 sent
      Email   9 sent
      Line   18 sent, 4 retried
      producer waited for space 10 time(s)
    """
TRAPS_OUT = """
    await, lowered by hand
      premium 8,933.71 THB
    sync-over-async (.Result) on a one-thread context
      await captures the context -> DEADLOCK (gave up after 1 s)
      ConfigureAwait(false)      -> completed
    async void throws after its first await
      the caller's catch saw     -> nothing
      the context received       -> InvalidOperationException
    fire-and-forget Task.Run that throws
      reported only after a GC   -> True
    """

# Table 7.7 — every error id here must be asserted by VbAsyncRulesTests.cs (checked in _vb_rules()); the
# message text is what the VB compiler printed when the snippet was compiled on the build machine.
_VB_RULES = [
    ("<code>Await</code> inside <code>Catch</code>", "BC36943",
     "'Await' cannot be used inside a 'Catch' statement, a 'Finally' statement, or a 'SyncLock' statement.",
     "Allowed since C# 6"),
    ("<code>Await</code> inside <code>Finally</code>", "BC36943", "(same message)", "Allowed since C# 6"),
    ("<code>Await</code> inside <code>SyncLock</code>", "BC36943", "(same message)",
     "Also rejected: no <code>await</code> in a <code>lock</code> body"),
    ("<code>Async Sub Main()</code>", "BC36934", "The 'Main' method cannot be marked 'Async'.",
     "<code>async Task Main</code> since C# 7.1"),
    ("<code>Async Iterator Function</code>", "BC36936", "'Async' and 'Iterator' modifiers cannot be used together.",
     "Async streams since C# 8"),
    ("<code>Await For Each q In quotes</code>", "BC30201", "Expression expected.",
     "<code>await foreach</code> since C# 8"),
    ("<code>Await Using c As New …</code>", "BC30201", "Expression expected.",
     "<code>await using</code> since C# 8"),
    ("<code>Using c As New …</code> on a type with only <code>IAsyncDisposable</code>", "BC36010",
     "'Using' operand of type 'PartnerConnection' must implement 'System.IDisposable'.",
     "<code>await using</code> disposes it"),
    ("<code>Async Function … As ValueTask(Of T)</code>", "BC36945",
     "The 'Async' modifier can only be used on Subs, or on Functions that return Task or Task(Of T).",
     "<code>async ValueTask&lt;T&gt;</code> compiles"),
    ("<code>SyncLock</code> on a <code>System.Threading.Lock</code>", "BC37329",
     "A value of type 'System.Threading.Lock' is not supported in SyncLock. Consider manually calling 'Enter' "
     "and 'Exit' methods in a Try/Finally block instead.",
     "<code>lock</code> calls <code>EnterScope()</code> (C# 13)"),
]

# Pygments' vbnet lexer has no token for VB 14 interpolated strings, so every `$"` prints inside a red
# error box. The code is valid (the samples compile); drop the box, keep the text. (same fix as lessons 01, 03)
_ERROR_SPAN = re.compile(r'<span style="border: 1px solid #F00">(.*?)</span>', re.S)


def _listed(block, heading):
    """Put a numbered code panel in the Contents at level 2 and clean VB highlighting (as lessons 01 and 03)."""
    if heading:
        block.update(heading=heading, toc=2)
    if "vb" in block.get("_langs", []):
        block["html"] = _ERROR_SPAN.sub(r"\1", block["html"])
    return block


def code(s, *, heading=None, note=None, keep=None):
    return _listed(_kit_code(s, heading=heading, note=note, keep=keep), heading)


def compare(left, right, *, heading=None, note=None, keep=None):
    return _listed(_kit_compare(left, right, heading=heading, note=note, keep=keep), heading)


def figure_heading(text):
    """A numbered heading for a block type that prints none of its own (twocol), kept with that block."""
    return {"type": "html", "html": f'<div class="figh"><h2>{esc(text)}</h2></div>', "heading": text,
            "toc": 2, "_keep_with_next": True}


def _read(relpath):
    return (REPO / relpath).read_text(encoding="utf-8-sig")


def _sources(project):
    """Every .cs / .vb file of one sample project (repo-relative)."""
    root = REPO / L / project
    files = list(root.rglob("*.cs")) + list(root.rglob("*.vb"))
    return sorted(p.relative_to(REPO).as_posix() for p in files if not {"bin", "obj"} & set(p.parts))


def _test_cases(project):
    """[Fact] methods + [InlineData] rows in one test project — a MEASURED figure."""
    text = "\n".join(_read(rp) for rp in _sources(project) if rp.endswith(".cs"))
    return len(re.findall(r"^\s*\[Fact\]", text, re.M)) + len(re.findall(r"^\s*\[InlineData\(", text, re.M))


def _region_loc(relpath, region, comment):
    """Non-blank, non-comment lines inside one #region — a MEASURED figure."""
    return sum(1 for ln in snippet(relpath, region).splitlines()
               if ln.strip() and not ln.strip().startswith(comment))


def _num(text):
    return int(text.replace(",", ""))


def _desk(out):
    """Figures printed by a rating-desk run (captured output above)."""
    q, t, f = map(int, re.search(r"quoted (\d+), timed out (\d+), failed (\d+)", out).groups())
    wall, seq = re.search(r"wall\s+([\d,]+) ms concurrently, ([\d,]+) ms", out).groups()
    return {"quoted": q, "timed_out": t, "failed": f, "wall": _num(wall), "sequential": _num(seq)}


def _asserted_outcomes():
    """The quoted / timed-out / failed counts FanOutTests asserts — the captured run must agree."""
    text = _read(FANOUT_TESTS)
    get = lambda kind: int(re.search(rf"Assert\.Equal\((\d+), outcomes\.OfType<{kind}>\(\)\.Count\(\)\)", text).group(1))
    return get("Quoted"), get("TimedOut"), get("Failed")


def _notify(out):
    sent = {m.group(1): (int(m.group(2)), int(m.group(3) or 0))
            for m in re.finditer(r"(Sms|Email|Line)\s+(\d+) sent(?:, (\d+) retried)?", out)}
    waits = int(re.search(r"waited for space (\d+)", out).group(1))
    return sent, waits


def _vb_rules():
    """Table 7.7 rows, after proving every error id is asserted by the VB compiler tests."""
    tests = _read(f"{VBRULES}/VbAsyncRulesTests.cs")
    missing = sorted({r[1] for r in _VB_RULES} - set(re.findall(r'"(BC\d{5})"', tests)))
    if missing:
        raise ValueError(f"table 7.7 cites {missing}, which VbAsyncRulesTests.cs does not assert")
    return [[construct, f"<code>{err}</code>", esc(msg), csharp] for construct, err, msg, csharp in _VB_RULES]


def blocks():
    transfer = row(5)[5]
    if [r[0] for r in ROSTER if r[5] < transfer] != [6]:
        raise ValueError("§1 says only the VB lesson has a lower transfer estimate — roster.py changed")
    partners = int(re.search(r"PartnerCount = (\d+)", _read(PARTNER)).group(1))
    cs, vb = _desk(DESK_CS_OUT), _desk(DESK_VB_OUT)
    for run in (cs, vb):
        if (run["quoted"], run["timed_out"], run["failed"]) != _asserted_outcomes():
            raise ValueError("captured desk output disagrees with the counts FanOutTests asserts — re-capture it")
    speedup = cs["sequential"] / cs["wall"]
    pool_cs = int(re.search(r"pool\s+(\d+)", DESK_CS_OUT).group(1))
    pool_vb = int(re.search(r"pool\s+(\d+)", DESK_VB_OUT).group(1))
    sent, waits = _notify(NOTIFY_OUT)
    retries = sum(r for _s, r in sent.values())
    consts = _read(f"{NOTIFY}/Program.cs")
    n_events, intake_cap, lane_cap = map(int, re.search(
        r"count = (\d+), intakeCapacity = (\d+), laneCapacity = (\d+)", consts).groups())
    if sum(s for s, _r in sent.values()) != n_events:
        raise ValueError("captured Notifications output does not add up to the event count in Program.cs")
    test_text = "\n".join(_read(rp) for rp in _sources("L05.PartnerRates.Tests"))
    real_sleeps = len(re.findall(r"Thread\.Sleep\(|Task\.Delay\(", test_text))
    vb_rules = _vb_rules()
    n_rejected = len(re.findall(r'\[InlineData\("Rejected/', _read(f"{VBRULES}/VbAsyncRulesTests.cs")))
    loc_context = loc(f"{L}/L05.AsyncTraps/OneThreadContext.cs")
    tests_rates, tests_vb = _test_cases("L05.PartnerRates.Tests"), _test_cases("L05.VbRules.Tests")
    loc_by_project = [(label, loc(*_sources(p))) for p, label in PROJECTS]
    loc_of = {p: n for (p, _label), (_l, n) in zip(PROJECTS, loc_by_project)}
    total_loc = sum(loc_of.values())
    lib_loc = loc_of["L05.PartnerRates"]
    proof_loc = loc_of["L05.PartnerRates.Tests"] + loc_of["L05.VbRules.Tests"] + loc_of["L05.AsyncTraps"]
    desk_cs_loc, desk_vb_loc = loc_of["L05.RateDesk"], loc_of["L05.VbAsync"]
    n_proj = len(list((REPO / L).glob("*/*.*proj")))
    cs_prog, vb_prog = _region_loc(DESK_CS, "program", "//"), _region_loc(DESK_VB, "program", "'")
    cs_stream, vb_stream = _region_loc(DESK_CS, "stream", "//"), _region_loc(DESK_VB, "stream", "'")

    toolbox = [
        {"num": 1, "title": "Task and Task<T>", "tags": [T_CS, T_RUNTIME], "pills": [SAME],
         "what": "The unit of async work: a promise for an operation that is <b>already running</b>.",
         "lines": [("Kotlin", "<code>Deferred&lt;T&gt;</code> from <code>async {}</code>"),
                   ("TS", "<code>Promise&lt;T&gt;</code>"),
                   ("Ends as", "<code>RanToCompletion</code> · <code>Faulted</code> · <code>Canceled</code>"),
                   ("Rule", "Return it and await it; never block on it with <code>.Result</code>")]},
        {"num": 2, "title": "ValueTask<T>", "tags": [T_CS, T_RUNTIME], "pills": [DIFFERENT],
         "what": "A struct result that avoids a heap allocation when the answer is often ready at once.",
         "lines": [("Use when", "A profiled hot path completes synchronously most of the time"),
                   ("Rule", "Await it once, never twice and never concurrently"),
                   ("Seen in", "<code>IAsyncEnumerator.MoveNextAsync</code>, <code>ChannelReader.WaitToReadAsync</code>"),
                   ("Default", "Return <code>Task&lt;T&gt;</code> unless a profile says otherwise")]},
        {"num": 3, "title": "CancellationToken", "tags": [T_CS, T_ARCH], "pills": [DIFFERENT],
         "what": "The cooperative stop signal you pass as the last parameter of every async call.",
         "lines": [("Kotlin", "<code>Job.cancel()</code> — but no scope passes it for you"),
                   ("Owner", "<code>CancellationTokenSource</code>: <code>Cancel</code>, <code>CancelAfter</code>, linked sources"),
                   ("Signals", "<code>OperationCanceledException</code> from whoever observes it"),
                   ("Trap", "A method without the parameter cannot be stopped")]},
        {"num": 4, "title": "IAsyncEnumerable<T>", "tags": [T_CS, T_JVM], "pills": [SAME],
         "what": "A cold, pull-based async sequence, consumed with <code>await foreach</code>.",
         "lines": [("Kotlin", "<code>Flow&lt;T&gt;</code>"),
                   ("LINQ", "In the box since .NET 10 (<code>System.Linq.AsyncEnumerable</code>)"),
                   ("Cancel", "A parameter marked <code>[EnumeratorCancellation]</code>"),
                   ("VB", "No <code>Await For Each</code>: drive the enumerator by hand (7.6)")]},
        {"num": 5, "title": "Channel<T>", "tags": [T_CS, T_ARCH], "pills": [SAME],
         "what": "An async producer/consumer queue, bounded or unbounded.",
         "lines": [("Kotlin", "<code>Channel(capacity)</code>"),
                   ("When full", "<code>Wait</code> (default) · <code>DropOldest</code> · <code>DropNewest</code> · <code>DropWrite</code>"),
                   ("In-box", "Part of the shared framework since .NET Core 3.0"),
                   ("Ends", "<code>Writer.Complete()</code> lets readers drain, then stop")]},
        {"num": 6, "title": "TimeProvider", "tags": [T_CS, T_RUNTIME], "pills": [DIFFERENT],
         "what": "An injectable clock: timestamps, timers and delays that a test can move by hand.",
         "lines": [("Kotlin", "<code>runTest</code> virtual time with <code>advanceTimeBy</code>"),
                   ("Since", ".NET 8, in the framework"),
                   ("Accepted", "<code>Task.Delay</code>, <code>WaitAsync</code>, <code>CancellationTokenSource</code>"),
                   ("Tests", "<code>FakeTimeProvider.Advance()</code> fires due timers")]},
    ]

    return [
        style_block(),
        {"type": "toc", "heading": "▤ Contents", "depth": 2,
         "note": "Page numbers are resolved from the rendered PDF. Code panels are cut from the compiled samples."},
        # the Contents fills most of page 1: start section 1 on page 2 instead of stranding its heading at the foot
        {"type": "html", "html": '<div style="height:0;break-before:page;page-break-before:always"></div>'},
        # a callout, story or figure heading must not print alone at a page foot with its body on the next page,
        # and the renderer breaks link text anywhere (word-break:break-all): keep a link label whole
        {"type": "html", "html": "<style>h2 { break-after:avoid; page-break-after:avoid; } "
                                 ".callout .ct { break-after:avoid; page-break-after:avoid; } "
                                 ".callout li:first-child { break-before:avoid; page-break-before:avoid; } "
                                 ".story .ct { break-after:avoid; page-break-after:avoid; } "
                                 ".story .ct + p { break-before:avoid; page-break-before:avoid; } "
                                 "body a.lnk, body a { word-break:normal; overflow-wrap:break-word; }</style>"},

        # ═══════════════════════════ 1 · WHY ═══════════════════════════
        {"type": "story", "heading": "1 · Why this is the lesson to slow down on",
         "html": (
             f"<p><b>The transfer map in {ref(1)} rates this lesson {transfer}% familiar " + ESTIMATE + " — lower than every lesson "
             "except Visual Basic — because C# async reads like Kotlin and TypeScript and behaves like neither.</b> "
             "<code>async</code>/<code>await</code> looks exactly like a <code>suspend</code> function or a "
             "TypeScript <code>async function</code>, so an experienced engineer from either world writes code "
             "that compiles, passes its unit test, and then deadlocks a UI thread, starves the thread pool under "
             "load or loses an exception nobody observed.</p>"
             "<p><b>You have already built the hard version of this problem.</b> Quoting a motor policy against "
             "~30 external partners means calling them concurrently, giving each its own deadline, tolerating the "
             "ones that fail or never answer, and returning the best price before the customer leaves. Sending the "
             "result over SMS, email and LINE is a producer/consumer pipeline with back-pressure. This lesson builds "
             "both in .NET, so every concept lands on a design you already own.</p>"
             "<p><b>The model differs from yours in three places, and each has a trap attached.</b> A "
             "<code>Task</code> is already running when you receive it — hot like a JavaScript Promise or a Kotlin "
             "<code>async {}</code>, unlike a cold Reactor <code>Mono</code>. Cancellation is a token you pass by "
             "hand: .NET has no structured concurrency, so no scope cancels children for you. And the code after "
             "an <code>await</code> resumes wherever the current <i>SynchronizationContext</i> says, which is why "
             "one library behaves differently in a WinForms app, classic ASP.NET and ASP.NET Core.</p>"
             "<p><b>Every result here is reproducible.</b> Partner latencies are <code>TimeProvider</code> timers, "
             "so the tests move a fake clock instead of sleeping, and the console output was captured from real "
             "runs. Premiums are illustrative, not a real tariff.</p>")},

        {"type": "kpi", "heading": "1.1 · The numbers to leave this lesson with",
         "items": [
             {"label": "Partners per quote", "value": str(partners), "tone": "indigo",
              "sub": "one fan-out · measured from the catalog"},
             {"label": "Fan-out wall clock", "value": f"{cs['wall']} ms", "tone": "teal",
              "sub": f"vs {cs['sequential']:,} ms one by one · captured"},
             {"label": "Deterministic tests", "value": f"{tests_rates}", "tone": "violet",
              "sub": f"fake clock · {real_sleeps} real sleeps · measured"},
             {"label": "Task.WhenEach", "value": ".NET 9", "tone": "navy",
              "sub": "yields tasks as they complete · verified"},
             {"label": "VB async gaps", "value": str(n_rejected), "tone": "red",
              "sub": "compiler errors · measured by compiling"}]},

        legend(T_CS, T_JVM, T_RUNTIME, T_ARCH),

        {"type": "callout", "variant": "info", "heading": "ℹ Before you start",
         "items": [
             f"<b>Read {ref(2)}, {ref(3)} and {ref(4)} first.</b> This lesson uses <code>using</code> "
             "declarations, exception filters (<code>catch … when</code>), switch expressions, records, lambdas and "
             "LINQ without explaining them again.",
             "<b>You will build</b> <code>L05.PartnerRates</code> (C# library: partner fan-out with per-partner "
             "deadlines, streaming results, thread-safe statistics, a shared token behind a semaphore) and its "
             "xUnit tests on virtual time; "
             "<code>L05.RateDesk</code> and <code>L05.VbAsync</code> (the same console desk in C# and VB); "
             "<code>L05.Notifications</code> (a bounded Channels pipeline); <code>L05.AsyncTraps</code> (four "
             "traps, reproduced and contained); and <code>L05.VbRules.Tests</code> (VB compiler rules proved by "
             "compiling snippets).",
             f"<b>Where this lesson stops.</b> Resilient <code>HttpClient</code> calls (retry, circuit breaker) and "
             f"hosting the dispatcher as a <code>BackgroundService</code> are {ref(8)}; test frameworks in depth "
             f"are {ref(10)}; VB syntax at large is {ref(6)}.",
             "Facts that change between releases are marked " + VERIFIED + " and link to the official source; "
             "judgements are marked " + ESTIMATE + "; numbers computed from the samples or captured from their runs "
             "are marked " + MEASURED + ". Kotlin panels are for comparison and are not compiled."]},

        # ═══════════════════════════ 2 · THE TASK MODEL ═══════════════════════════
        {"type": "story", "heading": "2 · The Task model — what await really does",
         "html": (
             "<p><b>A <code>Task</code> is a promise object for work already under way, and <code>await</code> is "
             "the compiler rewriting the rest of your method into a callback on it.</b> An <code>async</code> method "
             "runs synchronously on its caller's thread until it awaits something that has not finished. There it "
             "registers the remainder of the method as a continuation, returns an incomplete <code>Task</code> to "
             "its caller and gives the thread back. No thread waits for the socket or the timer; when the operation "
             "completes, the continuation is scheduled and the method resumes where it stopped (" + ASYNC + ").</p>"
             "<p><b>Where that continuation runs is the decision your other stacks made differently.</b> Kotlin "
             "resumes on the dispatcher you name; Node always resumes on its single event-loop thread. .NET asks the "
             "<i>SynchronizationContext</i> that was current at the <code>await</code>. A WinForms or WPF UI thread "
             "and classic ASP.NET on .NET Framework install one, so continuations queue back to that thread. "
             "ASP.NET Core, console apps and worker services have none, so continuations run on any thread-pool "
             "thread (" + CONFIGAWAIT + ").</p>"
             "<p><b><code>Task&lt;T&gt;</code> is the default return type; <code>ValueTask&lt;T&gt;</code> is an "
             "optimisation with rules.</b> <code>ValueTask&lt;T&gt;</code> saves an allocation when a result is "
             "usually available at once, such as a cache hit, but it may be awaited only once, and the documented "
             "default is to return <code>Task&lt;T&gt;</code> unless performance analysis proves otherwise "
             "(" + VALUETASK + "). <code>void</code> is for event handlers only, and "
             "<code>IAsyncEnumerable&lt;T&gt;</code> marks an async stream (" + RETURNS + ").</p>"
             "<p><b>.NET 11 moves the machinery, not the meaning.</b> From .NET 11 Preview 4 the runtime libraries "
             "are compiled with <i>runtime async</i>: the runtime, instead of a compiler-generated state machine, "
             "suspends and resumes async methods (" + RUNTIMEASYNC + "). Hot tasks, context capture and cancellation "
             "tokens — everything this lesson teaches — keep their meaning. " + VERIFIED + "</p>"
             "<p><b>.NET has no virtual threads, by decision.</b> Java 21 made blocking code cheap with virtual "
             "threads; the .NET team prototyped the same idea, green threads, and in 2023 put the experiment on "
             "hold to keep improving <code>async</code>/<code>await</code>, mainly because a second programming "
             "model was a larger cost than the gain (" + GREENTHREADS + "). " + VERIFIED + " The Task model in "
             "this lesson is the model you will keep using.</p>")},

        mapping("2.1 · Concept map — coroutines, Reactor and the event loop → .NET", [
            ("Kotlin <code>suspend fun</code> · TS <code>async function</code>", "<code>async Task&lt;T&gt;</code> method",
             "renamed", "<code>async</code> is an implementation detail; callers see only the <code>Task&lt;T&gt;</code>"),
            ("<code>async {}</code> → <code>Deferred</code> · JS <code>Promise</code>", "a started <code>Task&lt;T&gt;</code>",
             "same", "Hot: the work starts when the method is called, not when it is awaited"),
            ("Reactor <code>Mono&lt;T&gt;</code>", "<code>Task&lt;T&gt;</code>", "trap",
             "A <code>Mono</code> re-runs per subscriber; a <code>Task</code> runs once, and awaiting it again returns the same result"),
            ("<code>coroutineScope {}</code> — structured concurrency", "no equivalent", "different",
             "Nothing cancels or awaits children for you: pass a token and <code>await Task.WhenAll</code> (§4)"),
            ("<code>Job.cancel()</code> · <code>AbortController</code>", "<code>CancellationTokenSource.Cancel()</code>",
             "different", "Kotlin scopes pass cancellation down for you; every .NET async method takes the token "
             "as a parameter, explicitly. <code>AbortController</code> is the near-rename (3)"),
            ("<code>withTimeout</code> / <code>withTimeoutOrNull</code>",
             "<code>new CancellationTokenSource(timeout)</code> · <code>WaitAsync</code>", "trap",
             "<code>WaitAsync</code> stops <i>waiting</i>; only a token stops the <i>work</i> (3.4)"),
            ("<code>awaitAll()</code> · <code>Promise.all</code> · <code>Mono.zip</code>", "<code>Task.WhenAll</code>",
             "trap", "Those fail fast; <code>WhenAll</code> waits for every task even after one fails, and "
             "<code>await</code> rethrows only the first exception (4.7)"),
            ("<code>select {}</code> · <code>Promise.race</code>", "<code>Task.WhenAny</code> · <code>Task.WhenEach</code>",
             "renamed", "<code>WhenEach</code> (.NET 9) streams tasks as they complete"),
            ("Kotlin <code>Flow&lt;T&gt;</code>", "<code>IAsyncEnumerable&lt;T&gt;</code> + <code>await foreach</code>",
             "same", "Cold and pull-based; cancellation arrives through an attributed parameter (§5)"),
            ("Reactor <code>Flux&lt;T&gt;</code> with back-pressure", "bounded <code>Channel&lt;T&gt;</code>", "different",
             "No reactive operator library in the box; async LINQ is, since .NET 10"),
            ("<code>Dispatchers.IO</code> / <code>Default</code>", "the thread pool", "different",
             "No named dispatchers: I/O needs no thread, and <code>Task.Run</code> queues CPU work"),
            ("<code>Dispatchers.Main</code> · Node's loop thread", "a <code>SynchronizationContext</code>", "trap",
             "Blocking that thread on <code>.Result</code> deadlocks it (7.1)"),
            ("<code>runBlocking {}</code>", "<code>.GetAwaiter().GetResult()</code>", "trap",
             "Tolerable once in a console <code>Main</code> with no context; a starvation risk anywhere else"),
            ("<code>synchronized</code> · kotlinx <code>Mutex</code>", "<code>lock</code> · <code>SemaphoreSlim</code>",
             "different", "<code>lock</code> cannot contain an <code>await</code>; <code>SemaphoreSlim.WaitAsync</code> can (§6)"),
            ("<code>GlobalScope.launch</code> · a floating Promise", "<code>_ = Task.Run(…)</code>", "trap",
             "Its exception surfaces only when the GC finalizes the task, if ever (7.4)"),
            ("<code>runTest</code> + <code>advanceTimeBy</code>", "<code>FakeTimeProvider.Advance</code>", "different",
             "Kotlin makes every <code>delay</code> virtual; only .NET code that takes a <code>TimeProvider</code> "
             "sees the fake clock (6.6)"),
            ("<code>CompletableFuture</code> · <code>allOf</code> · <code>orTimeout</code>",
             "<code>Task</code> · <code>Task.WhenAll</code> · <code>WaitAsync</code>", "trap",
             "Hot like a <code>Task</code>; and <code>orTimeout</code>, like <code>WaitAsync</code>, stops waiting "
             "without stopping the work (3.3)"),
            ("<code>Mono.block()</code> · <code>CompletableFuture.join()</code>",
             "<code>.Result</code> · <code>.GetAwaiter().GetResult()</code>", "trap",
             "Reactor refuses <code>block()</code> on its non-blocking threads; .NET compiles it and then hangs a "
             "one-thread context or starves the pool (7.1)"),
            ("<code>asyncio.TaskGroup</code> (Python 3.11)", "no equivalent", "different",
             "The group cancels the siblings of a failed task and waits for all; in .NET use a linked token and "
             "<code>WhenAll</code> (4.7)"),
        ]),

        {"type": "mermaid", "inline": True,
         "heading": "2.2 · One await, step by step — a partner call inside ASP.NET Core",
         "caption": "solid arrows = calls and resumptions · dashed arrows = a returned Task or a completion signal · "
                    "no thread is blocked between steps 3 and 5",
         "code": ('%%{init: {"theme":"base","themeVariables": {"actorBkg":"#E0E7FF","actorBorder":"#4338CA",'
                  '"actorTextColor":"#1f2937","noteBkgColor":"#FEF3C7","noteBorderColor":"#D97706",'
                  '"noteTextColor":"#1f2937","signalColor":"#334155","signalTextColor":"#1f2937",'
                  '"sequenceNumberColor":"#ffffff"}}}%%\n'
                  "sequenceDiagram\n"
                  "  autonumber\n"
                  "  participant H as Quote endpoint\n"
                  "  participant M as GetRateAsync\n"
                  "  participant O as Socket or timer\n"
                  "  participant P as Thread pool\n"
                  "  H->>M: GetRateAsync(request, ct)\n"
                  "  M->>O: start the I/O, get an incomplete Task\n"
                  "  M-->>H: return an incomplete Task at the first await\n"
                  "  Note over H,P: the request thread goes back to the pool\n"
                  "  O-->>P: I/O completes, queue the continuation\n"
                  "  Note over P: no SynchronizationContext<br/>any pool thread will do\n"
                  "  P->>M: resume after the await\n"
                  "  M-->>H: complete the Task, resume the endpoint\n")},

        code(from_sample(TRAPS, "lowered"),
             heading="2.3 · What the compiler builds, written out by hand",
             note="<b>An <code>await</code> is an awaiter, a completion check and a callback.</b> If the awaited "
                  "task is already done, execution continues synchronously with no suspension at all. Otherwise "
                  "<code>OnCompleted</code> registers everything after the <code>await</code> and the method returns "
                  "its <code>Task</code> at once. <code>GetResult()</code> rethrows a failure, which is why "
                  "<code>try</code>/<code>catch</code> works around an <code>await</code>. The real compiler output "
                  "is a state-machine struct driven by <code>AsyncTaskMethodBuilder</code>, and it also flows "
                  "<code>ExecutionContext</code> (for example <code>AsyncLocal</code> values); "
                  "<code>L05.AsyncTraps</code> runs this version and prints <code>premium 8,933.71 THB</code> — the "
                  "total the MotorQuote running example prices for a Class 1 policy, 550,000 THB insured, driver aged "
                  "23 with four claim-free years (an illustrative tariff, not a real one), standing in for a slow "
                  "rating call."),

        {"type": "cards",
         "band": {"title": "2.4 · The async toolbox — six types in every .NET service", "note": "API view",
                  "tone": "violet"},
         "cards": toolbox[:3]},
        {"type": "cards", "toc": False,
         "band": {"title": "2.4 · The async toolbox (continued)", "note": "API view", "tone": "violet"},
         "cards": toolbox[3:]},

        # ═══════════════════════════ 3 · CANCELLATION ═══════════════════════════
        {"type": "story", "heading": "3 · Cancellation and timeouts — tokens, not scopes",
         "html": (
             "<p><b>Cancellation in .NET is a token passed down by hand, and nothing stops unless the code holding "
             "the token checks it.</b> A <code>CancellationTokenSource</code> owns the signal; its "
             "<code>Token</code> travels as the last parameter of every async method down to <code>HttpClient</code>, "
             "EF Core or <code>Task.Delay</code>, which observe it and throw <code>OperationCanceledException</code> "
             "(" + CANCEL + "). Kotlin propagates cancellation through the coroutine scope; in .NET a method that "
             "forgets the parameter is a method nobody can stop.</p>"
             "<p><b>A timeout is a token that cancels itself, so each partner call needs two tokens.</b> The caller's "
             "token says the customer has gone; a per-partner deadline says this partner is too slow. "
             "<code>CreateLinkedTokenSource</code> combines them, and an exception filter tells them apart "
             "afterwards: if the caller's token is not cancelled, the deadline fired, and the partner is recorded as "
             "<code>TimedOut</code> instead of the whole quote being abandoned.</p>"
             "<p><b><code>WaitAsync</code> is the <code>withTimeout</code> look-alike that cancels nothing.</b> It "
             "returns a task that fails with <code>TimeoutException</code> when time is up, but the operation "
             "underneath keeps running and its result is discarded (" + WAITASYNC + ", .NET 6; the "
             "<code>TimeProvider</code> overloads arrived in .NET 8). Use it only for work that takes no token, and "
             "budget for that work finishing anyway.</p>")},

        {"type": "mermaid", "inline": True,
         "heading": "3.1 · Two tokens, four outcomes — one partner call",
         "caption": "violet = tokens · slate = the partner call · green / amber / red = recorded outcomes · "
                    "rose = the only case that escapes to the caller",
         "code": ("flowchart LR\n"
                  '  C["Caller token<br/>the customer left"]:::tok --> LK["Linked token source<br/>fires on either"]:::tok\n'
                  '  D["Per-partner deadline<br/>250 ms on TimeProvider"]:::tok --> LK\n'
                  '  LK --> G["partner.GetRateAsync<br/>request, linked.Token"]:::partner\n'
                  '  G -- "answers in time" --> Q["Quoted"]:::ok\n'
                  '  G -- "canceled, caller still waiting" --> T["TimedOut"]:::slow\n'
                  '  G -- "any other exception" --> F["Failed"]:::bad\n'
                  '  G -- "canceled by the caller" --> X["OperationCanceledException<br/>propagates"]:::stop\n'
                  "  classDef tok fill:#ede9fe,color:#1f2937,stroke:#6d28d9;\n"
                  "  classDef partner fill:#e2e8f0,color:#1f2937,stroke:#475569;\n"
                  "  classDef ok fill:#bbf7d0,color:#1f2937,stroke:#16a34a;\n"
                  "  classDef slow fill:#fde68a,color:#1f2937,stroke:#d97706;\n"
                  "  classDef bad fill:#fecaca,color:#1f2937,stroke:#dc2626;\n"
                  "  classDef stop fill:#fce7f3,color:#1f2937,stroke:#be185d;\n")},

        code(from_sample(FANOUT, "per-partner-timeout"),
             heading="3.2 · A per-partner deadline on an injected clock",
             note="<b>Three details carry the design.</b> The deadline is a <code>CancellationTokenSource</code> "
                  "built on the injected <code>TimeProvider</code>, so tests can fire it without waiting. Both token "
                  "sources are <code>using</code> declarations: a linked source registers callbacks on its parents "
                  "and must be disposed. And the two <code>when</code> filters decide who asked to stop — a "
                  "cancellation the caller did not request is this partner's timeout, and a caller cancellation "
                  "passes straight through both filters and out of the method."),

        {"type": "table", "heading": "3.3 · Four ways to give up — which ones stop the work",
         "cols": ["API", "Stops the partner call?", "What the caller sees", "Use it for"],
         "rows": [
             ["<code>new CancellationTokenSource(timeout, time)</code>", "Yes, if the call observes the token",
              "<code>OperationCanceledException</code>", "A deadline per call, testable with a fake clock"],
             ["<code>CreateLinkedTokenSource(ct, deadline.Token)</code>", "Yes — whichever token fires first",
              "<code>OperationCanceledException</code>", "Combining the caller's token with your own deadline"],
             ["<code>cts.CancelAfter(timeout)</code>", "Yes, if the call observes the token",
              "<code>OperationCanceledException</code>", "Adding a deadline to a source you already hold"],
             ["<code>task.WaitAsync(timeout, time)</code>", "<b>No</b> — only the waiting stops",
              "<code>TimeoutException</code>", "Work that accepts no token; the work runs on unobserved"]]},

        code(from_sample(FANOUT_TESTS, "wait-async"),
             heading="3.4 · Proof on a fake clock — WaitAsync gives up, the partner does not",
             note="<b>The test moves time instead of sleeping.</b> <code>Advance(Timeout)</code> fires the "
                  "<code>WaitAsync</code> timer, so awaiting <code>waiting</code> throws <code>TimeoutException</code> "
                  "— yet <code>call.IsCompleted</code> is still false. Two more virtual seconds later the stubborn "
                  "partner returns its 13,000.00 THB quote to nobody. That orphaned call is the cost of a timeout "
                  "without a token: under load it is a connection, a thread-pool work item and a partner's rate "
                  "limit spent on an answer you threw away."),

        # ═══════════════════════════ 4 · FAN-OUT ═══════════════════════════
        {"type": "story", "heading": "4 · Fan-out — 30 partners, one deadline",
         "html": (
             "<p><b>Start every call first, then await them together: the fan-out lasts as long as the slowest "
             "partner you are prepared to wait for, not the sum of all of them.</b> "
             "<code>partners.Select(p =&gt; QueryOneAsync(…))</code> only describes the calls; the collection "
             "expression <code>[.. …]</code> around it runs them, and each call returns a "
             f"task that is already running. <code>Task.WhenAll</code> then waits for all {partners}. The captured "
             f"run finished in {cs['wall']} ms, where awaiting the partners one after another would have waited "
             f"{cs['sequential']:,} ms. The classic mistake is an <code>await</code> inside a <code>foreach</code> — "
             "sequential code that only looks asynchronous.</p>"
             "<p><b>There is no <code>coroutineScope</code> to clean up after you.</b> In Kotlin a failing child "
             "cancels its siblings and the scope waits for all of them. <code>Task.WhenAll</code> waits for every "
             "task but cancels none, and <code>await</code> rethrows only the first exception while the rest stay "
             "on the task's <code>Exception</code> (" + WHENALL + "). That is why <code>QueryOneAsync</code> never "
             "throws for a partner problem: every call ends as a <code>Quoted</code>, <code>TimedOut</code> or "
             "<code>Failed</code> record, and one bad partner cannot sink the quote.</p>"
             "<p><b>Three shapes cover a real rating desk.</b> <i>Everything by a deadline</i> is "
             "<code>WhenAll</code> over per-call timeouts. <i>Results as they arrive</i> is "
             "<code>Task.WhenEach</code> (.NET 9), an <code>IAsyncEnumerable</code> that yields each task the "
             "moment it completes and replaces the <code>WhenAny</code>-in-a-loop pattern that re-scans the list "
             "after every completion (" + WHENEACH + "). <i>First good-enough answer</i> reads that stream and "
             "cancels the rest. When a partner contract caps concurrent calls, <code>Parallel.ForEachAsync</code> "
             "with <code>MaxDegreeOfParallelism</code> keeps that many in flight (" + PFOREACH + ").</p>")},

        compare(from_text("""
            suspend fun queryAll(request: QuoteRequest)
                    : List<PartnerOutcome> = coroutineScope {
                // async {} starts all 30 children at once
                partners.map { p -> async { queryOne(p, request) } }
                    .awaitAll()
            }   // the scope cannot end while a child is running

            fun best(all: List<PartnerOutcome>): Quoted? =
                all.filterIsInstance<Quoted>()
                    .minByOrNull { it.premium.amount }
            """, "kotlin", file="the coroutine fan-out you already write"),
                from_sample(FANOUT, "fan-out"),
                heading="4.1 · The same fan-out — Kotlin coroutines vs C#",
                note="<b>Line for line the same shape; the guarantees differ.</b> <code>coroutineScope</code> "
                     "guarantees no child outlives it and cancels the siblings of a failed child. The C# version has "
                     "no scope: the 30 tasks live on their own, and <code>WhenAll</code> only waits. <code>Select</code> "
                     "is lazy; materialising it into an array is what starts the tasks, which is why the code keeps "
                     "an array rather than a re-enumerable <code>IEnumerable</code> (enumerate that twice and every "
                     "partner is called twice). The C# code stays safe because <code>QueryOneAsync</code> (3.2) turns every "
                     "partner failure into a value and bounds every call with a deadline — the discipline "
                     "the Kotlin scope gave you for free. <code>ConfigureAwait(false)</code> marks library code "
                     "(7.1). " + KOTLIN + "."),

        {"type": "chartrow", "charts": [
            {"heading": "4.2 · What 30 partners returned", "kind": "donut",
             "args": {"data": [("quoted", cs["quoted"]), ("timed out", cs["timed_out"]), ("failed", cs["failed"])],
                      "center": str(partners), "sub": "partners", "width": 390, "height": 230, "thickness": 34},
             "caption": "one fan-out with a 250 ms deadline per partner · captured from L05.RateDesk and asserted by FanOutTests",
             "note": (f"<b>{cs['quoted']} quotes arrived in time; {cs['timed_out']} partners were cut off and "
                      f"{cs['failed']} failed — and the quote still succeeded.</b> The timed-out slice is the six "
                      "slow partners plus the two that never answer. " + MEASURED + " — the counts are identical in "
                      "the C# and VB runs and in the test that runs on a fake clock.")},
            {"heading": "4.3 · Waiting for 30 partners", "kind": "bar",
             "args": {"data": [("one by one", cs["sequential"]), ("C# fan-out", cs["wall"]), ("VB fan-out", vb["wall"])],
                      "ylabel": "ms", "tone": "teal", "width": 390, "height": 230},
             "caption": "one by one = the sum of each partner's wait, capped at the deadline · fan-out = measured wall clock",
             "note": (f"<b>About {speedup:.0f}× faster, and bounded by the deadline rather than by the partner "
                      "count.</b> The fan-out bars sit just above 250 ms: the deadline plus start-up and scheduling. "
                      "Add a 31st partner and they stay put; the one-by-one bar grows. " + MEASURED + " on the build "
                      "machine — wall-clock figures vary from run to run.")}]},

        code(from_sample(FANOUT, "when-each"),
             heading="4.4 · Results as they arrive — Task.WhenEach",
             note="<b><code>WhenEach</code> turns a batch of tasks into an async stream that yields each one as it "
                  "completes.</b> "
                  "Each <code>done</code> task has already finished, so <code>await done</code> returns at once "
                  "and unwraps its result. <code>[EnumeratorCancellation]</code> lets a consumer pass a token with "
                  "<code>WithCancellation</code>; without the attribute the compiler warns (CS8425), which this "
                  "repository treats as an error. The test "
                  "<code>WhenEach_hands_back_each_outcome_the_moment_it_completes</code> advances a fake clock "
                  "partner by partner and asserts the order — which the API does not promise for tasks that "
                  "complete at the same instant; the test can assert it only because the fake clock finishes "
                  "the partners one at a time."),

        code(from_sample(FANOUT, "first-good-enough"),
             heading="4.5 · First good-enough quote, then cancel the rest",
             note="<b>Stop paying for answers you no longer need.</b> The loop reads outcomes as they arrive and, at "
                  "the first premium at or below the target, cancels the linked source that every remaining partner "
                  "call is listening to. <code>CancelAsync</code> (.NET 8) runs the registered callbacks without "
                  "blocking this thread. The matching test counts the calls that observed cancellation and requires "
                  "it to equal the number of partners still working at that virtual instant."),

        code(from_sample(FANOUT, "throttle"),
             heading="4.6 · When a partner contract caps concurrent calls",
             note="<b><code>Parallel.ForEachAsync</code> keeps at most <code>maxConcurrent</code> calls in flight, "
                  "where <code>WhenAll</code> starts all 30.</b> It is the <code>flatMapMerge(concurrency)</code> of "
                  "this lesson. The body runs on several threads at once, so results go into a "
                  "<code>ConcurrentBag</code> and are sorted afterwards. Each partner's deadline starts when its own "
                  "call starts, not when it queues, so a throttled desk can take longer than one deadline. The test "
                  "<code>Throttled_fan_out_never_exceeds_the_concurrency_budget</code> wraps every partner in a probe "
                  "and requires the peak number of calls in flight to stay within the budget."),

        figure_heading("4.7 · What Task.WhenAll does — and what Kotlin engineers expect it to do"),
        {"type": "twocol", "boxes": [
            {"heading": "Task.WhenAll does", "tone": "teal",
             "items": ["Wait for every task, including the ones still running after another has failed",
                       "Return all results in the order the tasks were passed in",
                       "Fault with every task's exception collected on <code>Task.Exception</code>",
                       "Hold no thread while it waits"]},
            {"heading": "Task.WhenAll does not", "tone": "rose",
             "items": ["Cancel the other tasks when one fails — pass a token and cancel it yourself",
                       "Rethrow more than the first exception from <code>await</code>",
                       "Start anything — the array it receives was already running (hand it a lazy <code>IEnumerable</code> "
                       "and enumeration, not <code>WhenAll</code>, starts the calls)",
                       "Limit concurrency — 30 partners means 30 calls in flight"]}]},

        # ═══════════════════════════ 5 · STREAMS & PIPELINES ═══════════════════════════
        {"type": "story", "heading": "5 · Streams and pipelines — IAsyncEnumerable and Channels",
         "html": (
             "<p><b><code>IAsyncEnumerable&lt;T&gt;</code> is Kotlin's <code>Flow</code>: cold, pull-based and "
             "consumed with <code>await foreach</code>.</b> An <code>async</code> method that uses "
             "<code>yield return</code> produces one; nothing runs until something iterates it, and each "
             "<code>MoveNextAsync</code> pulls one item. .NET 10 put LINQ for async streams in the box as "
             "<code>System.Linq.AsyncEnumerable</code>, replacing the community <code>System.Linq.Async</code> "
             "package — remove that reference when you upgrade, or calls such as <code>Take</code> become ambiguous "
             "(" + ASYNCLINQ + "). " + VERIFIED + "</p>"
             "<p><b>Cancellation has to be threaded in explicitly.</b> Kotlin's <code>flow {}</code> checks for "
             "cancellation on every <code>emit</code> (" + KOTLINFLOW + "). A C# async iterator sees a token only through a parameter "
             "marked <code>[EnumeratorCancellation]</code>, which receives both the token passed to the method and "
             "one passed later with <code>WithCancellation</code>.</p>"
             "<p><b>When producers and consumers run at different speeds, put a bounded <code>Channel&lt;T&gt;</code> "
             "between them.</b> The notification dispatcher reads quote events, routes each to an SMS, email or "
             "LINE lane, and sends with one worker per lane. Every channel is bounded, and with the default "
             "<code>FullMode = Wait</code> a full channel makes its writer wait — back-pressure that travels upstream "
             "until the event reader slows down, instead of memory growing until the process fails. "
             "<code>DropOldest</code>, <code>DropNewest</code> and <code>DropWrite</code> trade that safety for lost "
             "messages (" + CHANNELS + "). It is the in-process version of the SQS/SNS fan-in you run between "
             f"services; {ref(8)} hosts it as a <code>BackgroundService</code>.</p>")},

        compare(from_text("""
            // cold, like IAsyncEnumerable: nothing runs
            // until someone collects it
            fun readQuoteEvents(count: Int): Flow<Notification> =
                flow {
                    for (id in 1..count) {
                        yield()          // stand-in for an event read
                        val channel = when (id % 4) {
                            0 -> NotifyChannel.EMAIL
                            2 -> NotifyChannel.SMS
                            else -> NotifyChannel.LINE
                        }
                        val quoteId = "Q-${1000 + id}"
                        // emit() also checks for cancellation
                        emit(Notification(id, quoteId, channel,
                            "Quote $quoteId is ready"))
                    }
                }
            """, "kotlin", file="the Flow you already write"),
                from_sample(f"{NOTIFY}/Notification.cs", "async-stream"),
                heading="5.1 · An event stream — Kotlin Flow vs IAsyncEnumerable",
                note="<b>Same shape, one extra parameter.</b> <code>flow {}</code> + <code>emit</code> becomes an "
                     "<code>async</code> method with <code>yield return</code>; <code>collect</code> becomes "
                     "<code>await foreach</code>. The difference is the token: Kotlin inherits cancellation from "
                     "the collector's scope, while C# receives it as a parameter and checks it with "
                     "<code>ThrowIfCancellationRequested</code>. <code>await Task.Yield()</code> plays the role of "
                     "Kotlin's <code>yield()</code>: it forces the rest of the loop to continue asynchronously."),

        {"type": "mermaid", "inline": True,
         "heading": "5.2 · The notification dispatcher — bounded at every stage",
         "caption": f"indigo = async stream · amber = bounded channels (capacities from Program.cs) · teal = workers "
                    f"· one lane and one sender per channel · dashed = back-pressure: a full intake makes "
                    f"SubmitAsync wait",
         "code": ("flowchart LR\n"
                  f'  E["QuoteEvents.ReadAsync<br/>{n_events} events"]:::src -->|"SubmitAsync"| I["intake channel<br/>capacity {intake_cap}"]:::chan\n'
                  '  I --> R["router<br/>await foreach"]:::work\n'
                  f'  R -->|"sms"| S["SMS lane · {lane_cap}"]:::chan --> S1["SMS sender"]:::work\n'
                  f'  R -->|"email"| M["Email lane · {lane_cap}"]:::chan --> M1["Email sender"]:::work\n'
                  f'  R -->|"line"| N["LINE lane · {lane_cap}"]:::chan --> N1["LINE sender<br/>retries a rate-limit reply"]:::work\n'
                  '  I -. "full: the producer waits" .-> E\n'
                  "  classDef src fill:#c7d2fe,color:#1f2937,stroke:#6366f1;\n"
                  "  classDef chan fill:#fde68a,color:#1f2937,stroke:#d97706;\n"
                  "  classDef work fill:#ccfbf1,color:#1f2937,stroke:#0d9488;\n")},

        code(from_sample(f"{NOTIFY}/Dispatcher.cs", "bounded-channel"),
             heading="5.3 · Bounded channels and a producer that waits",
             note="<b><code>TryWrite</code> first, <code>WriteAsync</code> only when full.</b> A successful "
                  "<code>TryWrite</code> costs no await at all; a full intake falls through to "
                  "<code>WriteAsync</code>, which completes when the router makes room — the dispatcher counts those "
                  "waits. <code>SingleReader = true</code> is a promise that lets the channel use a cheaper "
                  "implementation; <code>Complete()</code> is how the producer says it is done."),

        code(from_sample(f"{NOTIFY}/Dispatcher.cs", "pipeline"),
             heading="5.4 · Router and senders — completion flows downstream",
             note="<b>Shutdown is a relay, not a kill.</b> The router's <code>await foreach</code> ends only when the "
                  "intake is completed <i>and</i> empty; it then completes each lane, each sender drains its lane "
                  "and returns its count, and <code>Task.WhenAll</code> collects the three results. Nothing is "
                  "dropped, and the program exits by itself."),

        {"type": "chart", "heading": "5.5 · What the dispatcher delivered", "kind": "stacked_bar",
         "args": {"categories": ["SMS", "Email", "LINE"],
                  "series": [("sent on the first attempt", [sent["Sms"][0] - sent["Sms"][1],
                                                            sent["Email"][0] - sent["Email"][1],
                                                            sent["Line"][0] - sent["Line"][1]]),
                             ("sent after one retry", [sent["Sms"][1], sent["Email"][1], sent["Line"][1]])],
                  "width": 560, "height": 210},
         "caption": f"{n_events} quote events · intake capacity {intake_cap} · lane capacity {lane_cap} · captured from L05.Notifications",
         "note": (f"<b>All {n_events} notifications were delivered, {retries} of them after a retry, and the "
                  f"producer had to wait for space about {waits} times.</b> Those waits are back-pressure working: the "
                  "event reader was paused, and no queue grew past its bound. LINE carries half the traffic because "
                  "the routing rule sends every odd-numbered event there, and a LINE message whose event number is a "
                  "multiple of 5 is rejected once by the simulated rate limit. The wait count is a timing result: 10 or 11 "
                  "across repeated runs on the build machine. " + MEASURED)},

        # ═══════════════════════════ 6 · SHARED STATE ═══════════════════════════
        {"type": "story", "heading": "6 · Shared state and testable time",
         "html": (
             "<p><b>Async code still runs on many threads at once, so shared state needs the discipline you know "
             "from Java — plus one new rule: never hold a lock across an <code>await</code>.</b> The code after an "
             "<code>await</code> may resume on a different thread from the one that took the lock, so C# rejects "
             "<code>await</code> inside a <code>lock</code> body (" + LOCKSTMT + ") and VB rejects it inside "
             "<code>SyncLock</code> (7.7). Around an <code>await</code>, use <code>SemaphoreSlim.WaitAsync</code>, "
             "which waits without holding a thread (6.5).</p>"
             "<p><b>Pick the smallest tool that makes the operation atomic.</b> One counter is "
             "<code>Interlocked.Increment</code>. A read-compare-write — is this quote cheaper than the best so far? "
             "— needs a lock; on .NET 9 and later, lock a dedicated <code>System.Threading.Lock</code>, which the "
             "C# 13 compiler turns into <code>EnterScope()</code> (" + LOCKTYPE + "). A keyed cache or an in-flight "
             "map is a <code>ConcurrentDictionary</code>, whose <code>GetOrAdd</code> may run its factory more than once "
             "under a race (" + GETORADD + ") — so wrap a partner call in <code>Lazy&lt;T&gt;</code>.</p>"
             "<p><b>Time is shared state too, and <code>TimeProvider</code> makes it injectable.</b> Every timer in "
             "<code>L05.PartnerRates</code> — each partner's simulated latency and each per-partner deadline — goes "
             "through a <code>TimeProvider</code>. Production passes <code>TimeProvider.System</code>; tests pass "
             "<code>FakeTimeProvider</code> from <code>Microsoft.Extensions.TimeProvider.Testing</code> and call "
             "<code>Advance</code>, so a 250 ms timeout costs no wall-clock time and cannot flake on a slow build "
             "agent (" + TIMEPROVIDER + ").</p>")},

        {"type": "mermaid", "inline": True,
         "heading": "6.1 · Choosing a primitive for shared state",
         "caption": "one row per question, asked top to bottom · amber = question · teal = safe across await · "
                    "green = lock-free · slate = must not span an await",
         "code": ('%%{init: {"flowchart": {"nodeSpacing": 40, "rankSpacing": 26, "wrappingWidth": 520}}}%%\n'
                  "flowchart TB\n"
                  "  subgraph R1[\" \"]\n"
                  "    direction LR\n"
                  '    Q1{{"await inside the critical section?"}}:::q -- "yes" --> '
                  'SEM["SemaphoreSlim(1,1): await WaitAsync, Release in finally"]:::async\n'
                  "  end\n"
                  "  subgraph R2[\" \"]\n"
                  "    direction LR\n"
                  '    Q2{{"one counter or reference swap?"}}:::q -- "yes" --> '
                  'INT["Interlocked: Increment, CompareExchange"]:::free\n'
                  "  end\n"
                  "  subgraph R3[\" \"]\n"
                  "    direction LR\n"
                  '    Q3{{"keyed cache or in-flight map?"}}:::q -- "yes" --> '
                  'CD["ConcurrentDictionary with Lazy values"]:::free\n'
                  "  end\n"
                  "  subgraph R4[\" \"]\n"
                  "    direction LR\n"
                  '    Q4{{"work passed from producer to consumer?"}}:::q -- "yes" --> '
                  'CH["a bounded Channel of T"]:::async\n'
                  "  end\n"
                  '  LCK["otherwise: lock on a System.Threading.Lock, short, no await"]:::lock\n'
                  '  R1 -- "no" --> R2\n'
                  '  R2 -- "no" --> R3\n'
                  '  R3 -- "no" --> R4\n'
                  '  R4 -- "no" --> LCK\n'
                  "  classDef q fill:#fde68a,color:#1f2937,stroke:#d97706;\n"
                  "  classDef async fill:#ccfbf1,color:#1f2937,stroke:#0d9488;\n"
                  "  classDef free fill:#bbf7d0,color:#1f2937,stroke:#16a34a;\n"
                  "  classDef lock fill:#e2e8f0,color:#1f2937,stroke:#475569;\n"
                  "  classDef row fill:#f8fafc,color:#1f2937,stroke:#cbd5e1;\n"
                  "  class R1,R2,R3,R4 row\n")},

        code(from_sample(STATS, "stats"),
             heading="6.2 · Interlocked for counters, Lock for read-compare-write",
             note="<b>Two tools, chosen per field.</b> Each counter changes with one atomic increment, so "
                  "<code>Interlocked</code> needs no lock. Updating <code>_best</code> reads, compares and writes — "
                  "three steps another thread could interleave — so it happens inside <code>lock (_gate)</code>, "
                  "which compiles to <code>_gate.EnterScope()</code> for a <code>Lock</code>. The test "
                  "<code>RateStats_counts_exactly_under_parallel_writers</code> records 30,000 outcomes from "
                  "<code>Parallel.For</code> and requires exact counts."),

        code(from_sample(STATS, "single-flight"),
             heading="6.3 · One partner call per key, however many callers",
             note="<b>The <code>Lazy</code> wrapper is the whole trick.</b> Under a race "
                  "<code>ConcurrentDictionary.GetOrAdd</code> may invoke the factory on two threads, but only one "
                  "value is stored; building a cheap <code>Lazy</code> is harmless, and only the stored "
                  "<code>Lazy</code> is ever started. The test fires 50 concurrent callers for one vehicle key and "
                  "asserts exactly one partner call: stampede protection, as Caffeine gives you on the JVM."),

        {"type": "table", "heading": "6.4 · Concurrency primitives next to their JVM counterparts",
         "cols": ["Primitive", "JVM / Kotlin counterpart", "Across an await?", "In the samples"],
         "rows": [
             ["<code>Interlocked</code>", "<code>AtomicInteger</code>, <code>AtomicReference</code>",
              "Yes — no lock is held", "6.2 <code>RateStats</code> counters"],
             ["<code>lock</code> on <code>System.Threading.Lock</code>", "<code>synchronized</code>, <code>ReentrantLock</code>",
              "<b>No</b> — a compile error", "6.2 <code>RateStats</code> best quote"],
             ["<code>SemaphoreSlim</code>", "<code>Semaphore</code>, kotlinx <code>Mutex</code>",
              "Yes, with <code>WaitAsync</code>", "6.5 <code>PartnerToken</code>"],
             ["<code>ConcurrentDictionary</code>", "<code>ConcurrentHashMap</code>", "Yes",
              "6.3 <code>SingleFlight</code>"],
             ["<code>ConcurrentBag</code> · <code>ConcurrentQueue</code>", "<code>ConcurrentLinkedQueue</code>", "Yes",
              "4.6 throttled fan-out"],
             ["<code>Channel&lt;T&gt;</code>", "<code>BlockingQueue</code>, Kotlin <code>Channel</code>", "Yes",
              "5.3, 5.4 notification dispatcher"],
             ["<code>Parallel.ForEachAsync</code>", "<code>flatMapMerge(concurrency)</code>",
              "Yes", "4.6 <code>QueryAllThrottledAsync</code>"]]},

        code(from_sample(f"{RATES}/PartnerToken.cs", "token-gate"),
             heading="6.5 · A lock you can hold across an await — SemaphoreSlim",
             note="<b><code>SemaphoreSlim(1, 1)</code> is the mutex that may span an <code>await</code>: "
                  "<code>WaitAsync</code> queues callers without holding a thread.</b> It is the job kotlinx "
                  "<code>Mutex.withLock</code> does in a coroutine. <code>Release</code> belongs in "
                  "<code>finally</code>, or one failed refresh leaves every later caller waiting for ever. The "
                  "fast path skips the gate; after the gate the code reads the token again, because the caller ahead "
                  "may already have refreshed it. The test "
                  "<code>PartnerToken_is_fetched_once_for_fifty_callers_and_again_after_it_expires</code> lets fifty "
                  "callers share one fetch, then moves a fake clock past the expiry and requires exactly one more."),

        code(from_sample(FANOUT_TESTS, "fake-time"),
             heading="6.6 · A 250 ms deadline tested in microseconds",
             note="<b>249 ms proves nothing has fired; 1 ms more proves everything does.</b> Every partner timer and "
                  "deadline is registered on the <code>FakeTimeProvider</code> when <code>QueryAllAsync</code> "
                  "starts, and fires only inside <code>Advance</code>. The three counts are exact because no wall "
                  f"clock is involved — the same {cs['quoted']} / {cs['timed_out']} / {cs['failed']} the real-clock "
                  f"run printed in 4.2. The test project has {tests_rates} tests and {real_sleeps} calls to "
                  "<code>Thread.Sleep</code> or <code>Task.Delay</code>. " + MEASURED),

        # ═══════════════════════════ 7 · TRAPS ═══════════════════════════
        {"type": "story", "heading": "7 · Traps — and what Visual Basic cannot say",
         "html": (
             "<p><b>Blocking on a task with <code>.Result</code> or <code>.Wait()</code> deadlocks wherever a "
             "SynchronizationContext owns a single thread.</b> The blocked thread is the only one allowed to run the "
             "continuation that would unblock it. ASP.NET Core has no such context, so the same code appears to work "
             "there — and instead holds a pool thread per request. Starvation is quiet rather than loud: in "
             "Microsoft's walkthrough the pool grew quickly to 2–3 times the core count and then added only 1–2 "
             "threads a second, so under load requests queue and latency climbs instead of anything failing — the "
             "same stall as blocking a Netty event-loop thread in WebFlux (" + BESTPRACTICE + " · " + STARVATION
             + "). " + VERIFIED + " General-purpose libraries therefore put "
             "<code>ConfigureAwait(false)</code> on every <code>await</code> so they never need the caller's context; "
             "application code does not (" + CONFIGAWAIT + ").</p>"
             "<p><b><code>async void</code> exists for event handlers only.</b> The caller gets nothing to await, so it "
             "cannot catch the method's exception; the exception is re-raised on the SynchronizationContext, or on "
             "the thread pool when there is none, where it is likely to terminate the process (" + RETURNS + "). In "
             "ASP.NET Core the documentation calls it always a bad practice.</p>"
             "<p><b>A task nobody awaits hides its failure.</b> <code>_ = Task.Run(…)</code> compiles cleanly; if it "
             "throws, <code>TaskScheduler.UnobservedTaskException</code> is raised only when the garbage collector "
             "finalizes the task — the demo in 7.4 has to force a collection to see it — and by default the process "
             "carries on (" + UNOBSERVED + "). Background work belongs in a hosted "
             f"service, covered in {ref(8)}. And inside ASP.NET Core, <code>await Task.Run(…)</code> around code already running "
             "on a pool thread only adds a scheduling hop.</p>"
             "<p><b>Visual Basic has had <code>Async</code> and <code>Await</code> since Visual Studio 2012, and "
             "stopped there.</b> The VB compiler rejects <code>Await</code> in <code>Catch</code>, <code>Finally</code> "
             "and <code>SyncLock</code> (" + VBAWAIT + "), <code>Async Sub Main</code>, async iterators, "
             "<code>Await For Each</code> and <code>ValueTask</code>-returning async functions. It also has no "
             "<code>Await Using</code>, and a plain <code>Using</code> refuses a type that implements only "
             "<code>IAsyncDisposable</code> — the <code>await using</code> from " + ref(2) + " has no VB spelling. "
             "Table 7.7 lists the exact errors, captured by compiling each snippet in "
             "<code>L05.VbRules.Tests</code>. VB can still consume everything the C# library offers — it just does "
             "so by hand: <code>Await c.DisposeAsync()</code> after the block, never in <code>Finally</code> "
             "(7.6).</p>")},

        code(from_sample(TRAPS, "deadlock"),
             heading="7.1 · Sync-over-async on a one-thread context",
             note="<b>Same method, one argument apart.</b> With <code>ConfigureAwait(true)</code> the continuation of "
                  "<code>GetPremiumAsync</code> is posted to the thread's context — the thread blocked in "
                  "<code>.Result</code>, which will never pump it. With <code>false</code> it runs on the pool and "
                  f"completes. <code>OneThreadContext</code> is a {loc_context}-line stand-in for a UI thread or "
                  "classic ASP.NET; the demo gives up after one second instead of hanging (output in 7.5)."),

        {"type": "mermaid", "inline": True,
         "heading": "7.2 · Why the deadlock never resolves",
         "caption": "a cycle of two waits: the thread waits for the task, the task waits for the thread · red = the "
                    "blocked thread · amber = the task it waits for · slate = the continuation queued to that thread",
         "code": ('%%{init: {"flowchart": {"nodeSpacing": 60, "rankSpacing": 170}}}%%\n'
                  "flowchart LR\n"
                  '  UI["UI or request thread<br/>owns the context"]:::thr -- "calls .Result<br/>and blocks" --> W["Task of Money<br/>not complete"]:::wait\n'
                  '  W -- "completes only when<br/>the continuation runs" --> K["continuation<br/>posted to the context"]:::cont\n'
                  '  K -- "needs the context thread<br/>which is blocked" --> UI\n'
                  "  classDef thr fill:#fecaca,color:#1f2937,stroke:#dc2626;\n"
                  "  classDef wait fill:#fde68a,color:#1f2937,stroke:#d97706;\n"
                  "  classDef cont fill:#e2e8f0,color:#1f2937,stroke:#475569;\n")},

        code(from_sample(TRAPS, "async-void"),
             heading="7.3 · async void — the exception the caller never sees",
             note="<b>The <code>catch</code> around the call cannot fire.</b> <code>SendQuoteEmail</code> returns at "
                  "its first <code>await</code>; 20 ms later the exception is posted to the captured context, where "
                  "the demo pumps it out. With no context it would be thrown on the thread pool. Return "
                  "<code>Task</code> and <code>await</code> it."),

        code(from_sample(TRAPS, "fire-and-forget"),
             heading="7.4 · A forgotten Task.Run — the failure nobody observes",
             note="<b>The exception is reported only when the garbage collector finalizes the faulted "
                  "<code>Task</code>.</b> <code>StartAndForget</code> keeps just a <code>WeakReference</code>, and "
                  "<code>NoInlining</code> keeps a strong reference out of the caller's frame, so nothing holds the "
                  "task. The demo waits until the task has faulted, then forces <code>GC.Collect()</code> and "
                  "<code>WaitForPendingFinalizers()</code> so <code>UnobservedTaskException</code> fires now, and "
                  "<code>SetObserved()</code> marks it handled. Production code has no such push: the event comes "
                  "whenever a collection happens to run, or never."),

        code(from_text(TRAPS_OUT, "text", label="Output — L05.AsyncTraps", file="captured on the build machine"),
             heading="7.5 · The four traps, reproduced",
             note="<b>Read each pair as cause and effect.</b> The deadlock line takes one second because the demo "
                  "waits that long before giving up. <code>nothing</code> / <code>InvalidOperationException</code> is "
                  "the async-void exception escaping its caller (7.3). The last line is <code>True</code> only "
                  "because the sample forces a garbage collection (7.4) — in production the unobserved exception "
                  "appears whenever the GC happens to run, or never."),

        compare(from_sample(DESK_CS, "stream"), from_sample(DESK_VB, "stream"),
                heading="7.6 · Consuming an async stream — C# vs Visual Basic",
                note=f"<b>{cs_stream} lines in C#, {vb_stream} in VB, and most of the difference is enumerator plumbing "
                     "that <code>await foreach</code> writes for C#.</b> With no <code>Await For Each</code>, VB calls "
                     "<code>GetAsyncEnumerator</code>, loops on <code>Await e.MoveNextAsync()</code> and disposes the "
                     "enumerator itself — after the loop, because an <code>Await</code> in a <code>Finally</code> "
                     "block does not compile, so an exception inside the loop would skip the dispose. The C# side "
                     "uses <code>Take(5)</code> from the .NET 10 in-box async LINQ. On both sides, leaving the loop "
                     "does not stop the partner calls; cancelling the token does."),

        {"type": "table", "heading": "7.7 · What the Visual Basic compiler rejects",
         "cols": ["VB construct", "Error", "Message (captured)", "C#"],
         "rows": vb_rules},

        {"type": "chart", "heading": "7.8 · Async features across the languages you use", "kind": "heatmap",
         "args": {"rows": ["async / await syntax", "await in catch / finally", "Consume async streams",
                           "Produce async streams", "Async entry point", "Structured concurrency",
                           "Cancellation is implicit", "Virtual time, no injection"],
                  "cols": ["C# 14", "VB", "Kotlin", "TypeScript", "Python"],
                  "matrix": [[2, 2, 2, 2, 2], [2, 0, 2, 2, 2], [2, 1, 2, 2, 2], [2, 0, 2, 2, 2],
                             [2, 0, 2, 2, 1], [0, 0, 2, 0, 2], [1, 1, 2, 1, 2], [1, 1, 2, 1, 1]],
                  "cell": 38, "tone": "violet", "fmt": lambda v: {2: "yes", 1: "some", 0: "—"}[int(v)]},
         "caption": "yes = the language or its runtime does it for you · some = you pass a token, inject a clock or "
                    "add a library · — = none · a rubric, not a benchmark",
         "note": ("<b>C# hands you the tools, not the automation: structured concurrency, implicit cancellation "
                  "and ambient virtual time are the rows where Kotlin stays ahead, and VB loses every row that "
                  "needed syntax after 2012.</b> One rule scores every column: <i>some</i> means a token you pass, a "
                  "clock you inject or a library you add. The VB column's gaps are " + MEASURED + " by compiling "
                  "(table 7.7); every other cell is an " + ESTIMATE + ", the author's judgement. Structured "
                  "concurrency: Kotlin (<code>coroutineScope</code>) and Python (" + PYTASKGROUP + ", 3.11). C# "
                  "dates: " + CSHIST + ".")},

        # ═══════════════════════════ 8 · HANDS-ON ═══════════════════════════
        {"type": "story", "heading": "8 · Hands-on — run the rating desk in both languages",
         "html": (
             f"<p><b>{n_proj} projects, one command.</b> <code>verify_samples.py</code> builds every lesson-05 "
             f"project, runs the {tests_rates + tests_vb} tests (the fan-out on a fake clock, the VB compiler rules) "
             "and runs the four console apps, each of which exits by itself. Run the two rating desks yourself to "
             "watch the fan-out on the real clock.</p>"
             "<p><b>Two lines will differ on your machine, and that is part of the lesson:</b> the wall clock, and the "
             "order of answers that arrive a few milliseconds apart, change from run to run because real timers are "
             "coarse. That is why the tests use <code>FakeTimeProvider</code>: on a fake clock the order is "
             "exact.</p>")},

        compare(from_sample(DESK_CS, "program"), from_sample(DESK_VB, "program"),
                heading="8.1 · The same desk — C# vs Visual Basic, one C# library",
                note=f"<b>{cs_prog} lines each side — VB awaits a C# <code>Task</code> exactly as C# does.</b> "
                     "<code>Dim … As New</code>, <code>For Each … Next</code> and <code>&amp;</code> for string "
                     "concatenation are syntax, not semantics. The difference sits outside this region: VB cannot "
                     "declare <code>Async Sub Main</code>, so <code>L05.VbAsync</code> blocks once in "
                     "<code>Main</code> with <code>GetAwaiter().GetResult()</code> — safe only because a console app "
                     "has no SynchronizationContext." if cs_prog == vb_prog else
                     f"<b>{cs_prog} lines in C#, {vb_prog} in VB — VB awaits a C# <code>Task</code> exactly as C# "
                     "does.</b> <code>Dim … As New</code>, <code>For Each … Next</code> and <code>&amp;</code> for "
                     "string concatenation are syntax, not semantics. VB cannot declare <code>Async Sub Main</code>, "
                     "so <code>L05.VbAsync</code> blocks once in <code>Main</code> with "
                     "<code>GetAwaiter().GetResult()</code> — safe only because a console app has no "
                     "SynchronizationContext."),

        code(from_text("""
            # build, test and run every lesson-05 sample
            python 0-script/verify_samples.py --only 5

            # the rating desk on the real clock, in C# and in VB
            dotnet run --project lesson-05-async-concurrency/samples/L05.RateDesk
            dotnet run --project lesson-05-async-concurrency/samples/L05.VbAsync

            # the pipeline, the traps, and the tests on virtual time
            dotnet run --project lesson-05-async-concurrency/samples/L05.Notifications
            dotnet run --project lesson-05-async-concurrency/samples/L05.AsyncTraps
            dotnet test lesson-05-async-concurrency/samples/L05.PartnerRates.Tests
            """, "shell"), heading="8.2 · Commands",
             note="<b>No restore or build step:</b> <code>dotnet run</code> and <code>dotnet test</code> do both first; "
                  "<code>L05.VbRules.Tests</code> also downloads the Roslyn VB compiler on first restore."),

        compare(from_text(DESK_CS_OUT, "text", label="Output — C# desk", file="captured on the build machine"),
                from_text(DESK_VB_OUT, "text", label="Output — VB desk", file="captured on the build machine"),
                heading="8.3 · What you should see",
                note="<b>The counts and the best premium must match yours; the timings will not.</b> The wall clock, the "
                     "pool size and the order after <code>P18</code> and <code>P04</code> vary: partners answering "
                     "1–3 ms apart can arrive in any order, and <code>P04</code>, a failure, still counts as an "
                     "answer. <code>pool</code> is <code>ThreadPool.ThreadCount</code> after the run: "
                     f"{pool_cs} threads (C#) and {pool_vb} (VB) served 30 concurrent calls because no call held a "
                     "thread while it waited; one blocked thread per partner would need about 30 (7.1)."),

        code(from_text(NOTIFY_OUT, "text", label="Output — L05.Notifications", file="captured on the build machine"),
             heading="8.4 · What the dispatcher prints",
             note=f"<b>The delivery counts are deterministic; the wait count is not.</b> "
                  f"{n_events} events split {sent['Sms'][0]} / {sent['Email'][0]} / {sent['Line'][0]} by the routing "
                  f"rule and the {retries} retries follow from the simulated rate limit. The {waits} producer waits "
                  "depend on capacities and simulated latencies: 10 or 11 on the build machine, a timing result."),

        {"type": "chart", "heading": "8.5 · Lines of code in the lesson-05 samples", "kind": "hbar",
         "args": {"data": loc_by_project, "tone": "navy", "labelw": 150, "width": 620},
         "caption": "non-blank, non-comment lines per project, including test snippets · measured when this PDF was built",
         "note": (f"<b>Tests, compiler-rule snippets and trap demos make up {proof_loc} of the {total_loc} lines, "
                  f"against {lib_loc} lines of library.</b> "
                  f"{tests_rates} fan-out and shared-state tests and {tests_vb} compiler-rule tests back the claims; "
                  f"the two desks ({desk_cs_loc} and {desk_vb_loc} lines) are thin callers of the same library "
                  "(8.1). " + MEASURED + " — a size signal, not a quality score.")},

        {"type": "callout", "variant": "warn", "heading": "⚠ Traps",
         "items": [
             "<b>“An <code>await</code> inside <code>foreach</code> calls the partners concurrently.”</b> It calls "
             "them one after another. Start every task first, then <code>await Task.WhenAll</code> (4.1).",
             "<b>“<code>Task.WhenAll</code> cancels the rest when one fails,” like <code>coroutineScope</code>.</b> It "
             "cancels nothing and <code>await</code> rethrows only the first exception. Turn partner failures into "
             "values and cancel through a token (4.7).",
             "<b>“<code>WaitAsync(timeout)</code> is <code>withTimeout</code>.”</b> It stops the waiting, not the "
             "work (test 3.4).",
             "<b>“<code>.Result</code> is fine — it works in my API.”</b> ASP.NET Core has no SynchronizationContext, "
             "so it does not deadlock there; it starves the thread pool under load, and the same library "
             "deadlocks a WinForms caller (7.1).",
             "<b>“An <code>async void</code> method is like a TypeScript <code>async</code> handler.”</b> Its "
             "exception bypasses the caller and can end the process, and a discarded <code>Task.Run</code> loses "
             "its failure the same way. Return <code>Task</code> and await it (7.3, 7.4)."]},

        {"type": "callout", "variant": "ok", "heading": "✔ Checkpoint — you are ready for lesson 06 when",
         "items": [
             f"<code>python 0-script/verify_samples.py --only 5</code> reports {n_proj}/{n_proj} passed on your machine.",
             "Using diagram 2.2, you can say which thread resumes after an <code>await</code> in ASP.NET Core, a "
             "console app and WinForms.",
             "You can turn a <code>foreach</code> with an <code>await</code> inside into a fan-out with per-call "
             "deadlines, and say what happens to a partner that never answers.",
             "You can explain what <code>Advance(249 ms)</code> followed by <code>Advance(1 ms)</code> proves in "
             "test 6.6, and why it cannot flake.",
             "You can read the VB desk and name two things its C# twin does that VB cannot express."]},

        {"type": "callout", "variant": "summary", "heading": "🔍 Check yourself",
         "items": [
             "An async method is called but its task is never awaited. Is the work running? How does that differ "
             "from a Reactor <code>Mono</code> nobody subscribes to?",
             "Where does the code after an <code>await</code> run in ASP.NET Core, and why do libraries use "
             "<code>ConfigureAwait(false)</code> while application code does not?",
             "<code>QueryOneAsync</code> catches <code>OperationCanceledException</code> only "
             "<code>when (!ct.IsCancellationRequested)</code>. What breaks without that filter when the customer "
             "leaves?",
             "What does <code>Task.WhenEach</code> give you that <code>Task.WhenAll</code> does not, and which .NET "
             "version added it?",
             "A bounded channel with <code>FullMode = Wait</code> has a slow consumer. What happens to the producer, "
             "and what would <code>DropOldest</code> change?",
             "Why can a <code>lock</code> body not contain an <code>await</code>, and what do you use instead?",
             "Name three async constructs the VB compiler rejects, and the C# form that compiles."]},

        {"type": "footer",
         "html": ("<b>Lesson 05 in one line:</b> a <code>Task</code> is hot, <code>await</code> resumes wherever the "
                  "SynchronizationContext says, cancellation is a token you pass by hand — so fan out over per-call "
                  "deadlines, stream through bounded channels, never block or lock across an <code>await</code>, "
                  "and inject <code>TimeProvider</code>."
                  "<br/><b>Next:</b> " + ref(6) + " — reading, keeping and retiring the Visual Basic estates this "
                  "lesson kept running into.")},
    ]
