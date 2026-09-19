# Unit spec — lesson-05-async-concurrency.pdf

Built to `_standard.md`. Content module `0-script/lessons/lesson_05.py` (shape follows `lesson_01.py`). Samples
`lesson-05-async-concurrency/samples/`.

## 1 · Purpose

Teach a Kotlin-coroutines / WebFlux / Node architect the .NET async model and where it differs: hot `Task`s, what
`await` compiles to and where the continuation runs (SynchronizationContext), explicit cancellation tokens and no
structured concurrency, fan-out to ~30 rating partners, `IAsyncEnumerable` and bounded `Channel` pipelines, shared
state and testable time (`TimeProvider`), the classic traps, and the async constructs Visual Basic rejects.

## 2 · Ownership & cadence

Owner **claude**, regenerable. Re-verify when .NET 11 ships (November 2026): §2's runtime-async paragraph cites the
.NET 11 Preview 4 release notes and should then cite the GA "What's new"; re-capture the console output (§4 below)
whenever a sample's output format or the partner catalog changes — the module raises if the captured counts disagree
with `FanOutTests` or with the notification event count.

## 3 · Structure

20 pages at the 2026-09-20 build; no page is more than about a quarter empty except the last (measured with PyMuPDF:
the emptiest are pp. 7, 10, 16 at 17-18% and p. 19 at 26%).

| § | Heading | Blocks |
|---|---|---|
| — | Contents | `toc` depth 2 (code panels and the twocol are listed through local `_listed()` / `figure_heading()` helpers); an empty `html` block forces a page break so page 1 is the Contents alone and §1 starts page 2 |
| 1 | Why this is the lesson to slow down on | story (4 ¶: transfer estimate from `roster.py` with an ESTIMATE chip, the partner fan-out and notification fan-in the reader has built, the three model differences, reproducibility) · `kpi` 1.1 (5 tiles: partners, fan-out wall clock, deterministic tests = every test in `L05.PartnerRates.Tests`, `Task.WhenEach` .NET 9, VB async gaps) · `legend` (C#, Java/Kotlin, runtime, architecture — only the tags the cards use) · info callout "Before you start" (4 items: `ref(2)`, `ref(3)`, `ref(4)` prerequisites · what you build · where the lesson stops → 08/10/06 · honesty chips) |
| 2 | The Task model — what await really does | story (5 ¶: Task + continuation · SynchronizationContext vs dispatchers / event loop · `ValueTask` rules · .NET 11 runtime async · why .NET has no virtual threads, citing the dotnet/runtimelab green-threads results) · mapping 2.1 (19 rows: 16 coroutine / Reactor / event-loop rows plus `CompletableFuture`, `Mono.block()` / `join()` and `asyncio.TaskGroup`) · mermaid 2.2 sequence (one await inside ASP.NET Core, init-directive colours) · code 2.3 (`lowered`: an await written out by hand) · cards 2.4 (6-type toolbox, 3 + 3 in a "(continued)" band) |
| 3 | Cancellation and timeouts — tokens, not scopes | story (3 ¶) · mermaid 3.1 flowchart LR (caller token + deadline → linked token → four outcomes) · code 3.2 (`per-partner-timeout`) · table 3.3 (four ways to give up: which stop the work) · code 3.4 (`wait-async` test on a fake clock) |
| 4 | Fan-out — 30 partners, one deadline | story (3 ¶; names the collection expression as what runs the lazy `Select`) · compare 4.1 (Kotlin `coroutineScope`/`async`/`awaitAll` ↔ C# `fan-out`) · chartrow 4.2 donut (outcomes) + 4.3 bar (one-by-one vs C# vs VB wall clock) · code 4.4 (`when-each`) · code 4.5 (`first-good-enough`) · code 4.6 (`throttle`: `Parallel.ForEachAsync`) · 4.7 twocol (what `Task.WhenAll` does / does not do) |
| 5 | Streams and pipelines — IAsyncEnumerable and Channels | story (3 ¶: async streams + .NET 10 in-box async LINQ · explicit cancellation · bounded channels and back-pressure) · compare 5.1 (Kotlin `Flow` ↔ C# `async-stream`) · mermaid 5.2 flowchart LR (dispatcher: intake → router → three lanes, capacities read from `Program.cs`; the router's three edges reach the lane nodes) · code 5.3 (`bounded-channel`) · code 5.4 (`pipeline`) · chart 5.5 stacked bar (delivered per channel, first attempt vs retry) |
| 6 | Shared state and testable time | story (3 ¶: no lock across await · smallest atomic tool · TimeProvider) · mermaid 6.1 flowchart TB (one row per question, each row a `direction LR` subgraph holding the question and its "yes" answer) · code 6.2 (`stats`: Interlocked + Lock) · code 6.3 (`single-flight`) · table 6.4 (primitives vs JVM counterparts, safe across await?, panel number of the sample) · code 6.5 (`token-gate`: `SemaphoreSlim.WaitAsync` / `Release` in `finally`) · code 6.6 (`fake-time` test) |
| 7 | Traps — and what Visual Basic cannot say | story (4 ¶: sync-over-async, ConfigureAwait and how the pool starves (2–3× cores, then 1–2 threads a second) · async void · fire-and-forget + Task.Run in ASP.NET Core · VB's async limits) · code 7.1 (`deadlock`) · mermaid 7.2 flowchart LR (the deadlock cycle; init directive widens the ranks so labels print at body scale; the caption names the three colours) · code 7.3 (`async-void`) · code 7.4 (`fire-and-forget`) · code 7.5 (captured `L05.AsyncTraps` output) · compare 7.6 (C# `stream` ↔ VB `stream`) · table 7.7 (8 VB compiler errors with captured messages and the C# form) · chart 7.8 heatmap (async features: C# 14 / VB / Kotlin / TypeScript / Python, cell 38, rubric) |
| 8 | Hands-on — run the rating desk in both languages | story (2 ¶) · compare 8.1 (C# `program` ↔ VB `program`) · code 8.2 commands · compare 8.3 (captured desk output C# ↔ VB) · code 8.4 (captured `L05.Notifications` output) · chart 8.5 hbar (lines of code per project) · warn "Traps" (5) · ok checkpoint (5) · summary "Check yourself" (7) · footer (Next: lesson 06) |

Standard minimums as built: 8 numbered stories · 1 mapping · 2 card bands (3 cards each) · 5 mermaid (sequence,
flowchart ×4) · 5 charts · 23 code panels (18 `code` + 5 `compare`) · C# ↔ VB compare (7.6, 8.1) · Kotlin ↔ C#
compare (4.1, 5.1) · 1 twocol · 3 tables besides the mapping · 25 distinct links (Microsoft Learn, .NET Blog, dotnet/core
release notes, dotnet/runtimelab, kotlinlang.org, docs.python.org).

## 4 · Derivation

- **KPI "Partners per quote"** = `PartnerCount` parsed from `SimulatedPartner.cs` (MEASURED, 30).
- **KPI "Fan-out wall clock"**, **chart 4.3** = parsed from the captured `L05.RateDesk` / `L05.VbAsync` output in the
  module (`DESK_CS_OUT`, `DESK_VB_OUT`): 263 ms (C#), 276 ms (VB), 4,982 ms one by one (the sample sums each partner's
  latency capped at the 250 ms deadline). MEASURED on the build machine (Windows x64, .NET 10.0.12 runtime); wall-clock
  values vary between runs, which the notes say. The "about 19×" in 4.3's note is computed from those numbers.
- **Chart 4.2** = quoted / timed out / failed parsed from the captured output (19 / 8 / 3). The module raises unless
  both captured runs equal the three counts `FanOutTests.Fan_out_ends_at_the_timeout_not_the_sum_of_latencies`
  asserts. The "six slow partners plus the two that never answer" wording follows `PartnerCatalog.Create`.
- **KPI "Deterministic tests"** = `[Fact]` + `[InlineData(` count over `L05.PartnerRates.Tests` (11: 8 in
  `FanOutTests`, 3 in `SharedStateTests`, the same figure 6.6's note prints); "0 real sleeps" = occurrences of
  `Thread.Sleep(` / `Task.Delay(` in that project (MEASURED). §8 adds the 9 VB compiler-rule tests (20 in all).
- **KPI "Task.WhenEach"** = ".NET 9 · yields tasks as they complete · verified" (API reference). The reference says the
  exact order in which tasks become available is not defined, so the lesson claims "as they complete", never a total
  order; 4.4's note says the fake-clock test can assert an order only because it completes one partner at a time.
- **KPI "VB async gaps"** and table 7.7 = the `Rejected/` `[InlineData]` rows of `VbAsyncRulesTests.cs` (8). The module
  raises if the table cites an error id the tests do not assert. Message text was captured by compiling each snippet
  with Microsoft.CodeAnalysis.VisualBasic 5.9.0 (the package the test project references) on 2026-09-16.
- **Chart 5.5**, panel 8.4 = parsed from the captured `L05.Notifications` output (9 / 9 / 18 sent, 4 retries, 10
  producer waits); event count and capacities in 5.2, 5.5 and 8.4 are read from `L05.Notifications/Program.cs`, and the
  module raises if the captured sent counts do not add up to the event count. The wait count is a timing result: it was
  10 or 11 in every one of 15 runs on the build machine (nine by the accuracy reviewer, six in the fix pass: 10
  eight times, 11 seven times), and the 5.5 and 8.4 notes say "10 or 11" rather than a stable value.
- **Chart 8.5** = `loc()` over every `.cs`/`.vb` file per project (233 / 231 / 40 / 53 / 106 / 131 / 131 at this
  build); its note computes tests + snippets + trap demos (493 of 925) against the library (233). Region line counts in
  the 7.6 and 8.1 notes (7 vs 11, 12 vs 14) and the `OneThreadContext` size in 7.1 (39) are computed at build time.
- **Chart 7.8** heatmap is a rubric (yes / some / —) with one rule for every column: *yes* = the language or its
  runtime does it for you; *some* = you pass a token, inject a clock or add a library. Its VB column's gaps are backed
  by table 7.7 (MEASURED); every other cell is labelled ESTIMATE in the note. C# dates cite The history of C#; Python's
  structured concurrency cites the asyncio docs (TaskGroup, 3.11). Row labels are kept under ~26 characters because
  `chart_svg.heatmap` reserves 152 px for them.
- **§1 "55% familiar"** = `roster.py` transfer estimate for lesson 05 (ESTIMATE chip); the module raises unless lesson
  06 is the only lesson with a lower estimate (the sentence says so).
- **Captured panels** 7.5, 8.3, 8.4 are pasted from real runs on 2026-09-16. The order of answers after P18/P04 in 8.3
  varies between runs (timer resolution), and 8.3's note explains the `pool` line (`ThreadPool.ThreadCount` after the
  run: 9 threads in C#, 5 in VB) using the two captured numbers.
- **VERIFIED facts and their sources:** `Task.WhenEach` .NET 9 (API reference) · `System.Threading.Lock` .NET 9 / C# 13
  `EnterScope` (API reference, lock statement, history of C#) · `await` not allowed in a `lock` body (lock statement) ·
  `TimeProvider` in the framework since .NET 8, `FakeTimeProvider` in Microsoft.Extensions.TimeProvider.Testing, the
  TimeProvider-accepting `Task.Delay` / `WaitAsync` / `CancellationTokenSource` (TimeProvider overview) · `WaitAsync`
  .NET 6, TimeProvider overloads .NET 8, `TimeoutException` (API reference) · `CancelAsync` .NET 8 runs callbacks
  asynchronously (API reference; cited in the 4.5 note without a link) · Channels in the shared framework since .NET
  Core 3.0, `FullMode` values, `Wait` default (Channels) · `System.Linq.AsyncEnumerable` in .NET 10 replacing
  System.Linq.Async (breaking-change page) · `ValueTask<T>` await-once rule and "default to Task" guidance (API
  reference) · ASP.NET Core has no SynchronizationContext; ConfigureAwait(false) for libraries, not app code (ConfigureAwait
  FAQ) · no `.Result`/`.Wait()`, no `Task.Run` then await, `async void` always bad in ASP.NET Core (ASP.NET Core best
  practices) · sync-over-async causes ThreadPool starvation, and in the walkthrough the pool grows quickly to 2–3× the
  core count and then adds 1–2 threads a second (debug ThreadPool starvation, fetched 2026-09-20) · `WhenAll` result
  order and aggregated exceptions (API reference) · `GetOrAdd` factory may run more than once (API reference) ·
  unobserved task exceptions do not terminate the process by default (UnobservedTaskException) · VB `Await` not in
  Catch/Finally/SyncLock, Async/Await since Visual Studio 2012 (VB Await operator) · runtime async in .NET 11 Preview 4
  runtime libraries (dotnet/core release notes) · the green-threads experiment was put on hold in 2023 to keep
  improving async/await, mainly to avoid a second programming model (dotnet/runtimelab issue #2398, fetched
  2026-09-20) · Kotlin structured concurrency (Kotlin coroutine basics) · `flow {}` checks cancellation on each `emit`
  (kotlinx flow builder API) · CS8425 warning for an async iterator without `[EnumeratorCancellation]` (verified by
  compiling a scratch file-based app on the build machine; cited in 4.4's note).
- **Not linked, stated as general knowledge in the mapping rows:** `Promise.all` / `awaitAll` / `Mono.zip` fail fast;
  `CompletableFuture.orTimeout` completes the future without stopping the work; Reactor refuses `block()` on its
  non-blocking threads; `asyncio.TaskGroup` cancels the siblings of a failed task. Blocking a Netty event-loop thread in
  WebFlux is offered as an analogy, not a measured claim.

## 5 · Presentation

Format 00 via `brief_pdf.py`; code panels from `lesson_kit`. Local helpers (as lessons 01 and 03): `_listed()` puts a
code panel's heading on its block so the Contents lists it and strips Pygments' red error box around VB `$"`;
`figure_heading()` gives the twocol a numbered, kept-with-next heading. Two local `html` blocks follow the Contents: an
empty one with `break-before:page`, and a `<style>` block that keeps `h2` / callout / story headings with their first
line and overrides the renderer's `word-break:break-all` on links (`body a.lnk, body a { word-break:normal }`) so link
labels are no longer split mid-word.

Mermaid: 2.2 is a sequence diagram coloured by an init directive; 3.1, 5.2, 6.1, 7.2 are flowcharts. 5.2 has no
subgraph, so the router's three labelled edges (`sms`, `email`, `line`) end on the lane nodes. 6.1 stacks four
`direction LR` row subgraphs (a question and its "yes" answer) joined by "no" edges between the rows; its init
directive sets `wrappingWidth: 520` because mermaid's default 200 px label wrap made every node three lines tall and the
figure taller than the page. 7.2's init directive sets `rankSpacing: 170` so the three-node cycle prints at body scale,
and its caption names the red / amber / slate colours. The flowchart class for the partner call is named `partner` —
`call` is a reserved word in mermaid flowcharts and fails the parse.

Pagination: every code panel is a monolithic block (`.code` has `overflow:hidden`), so `keep=False` does not let a long
panel split; gaps are closed by block order instead. §2 orders mapping → sequence diagram → code panel; §6 puts the
primitives table (6.4) before the `SemaphoreSlim` panel (6.5); §8 puts the desk comparison (8.1) before the commands
(8.2). The heatmap cell stays at 38 (at 32 the column headers "TypeScript" and "Python" run together).

## 6 · Inputs

`roster.py`; samples:
- `L05.PartnerRates` (C# library: `IPartnerRateProvider`, `SimulatedPartner` + `PartnerCatalog` on `TimeProvider`,
  `RateFanOut` with per-partner deadlines, `WhenAll`, `WhenEach`, first-good-enough, `Parallel.ForEachAsync` throttle;
  `RateStats` with `Interlocked` + `Lock`; `SingleFlight`; `PartnerToken` behind a `SemaphoreSlim`) — regions
  `contract`, `partner-call`, `per-partner-timeout`, `fan-out`, `when-each`, `first-good-enough`, `throttle`, `stats`,
  `single-flight`, `token-gate`
- `L05.PartnerRates.Tests` (xUnit, `FakeTimeProvider`, no real sleeps; 11 tests) — regions `fake-time`, `wait-async`
- `L05.RateDesk` (C# console on the real clock; in-box async LINQ `Take`) — regions `program`, `stream`
- `L05.VbAsync` (VB console, same desk over the C# library; blocks once in `Sub Main`) — regions `entry`, `program`, `stream`
- `L05.Notifications` (C# console: async stream → bounded intake → router → three bounded lanes) — regions
  `async-stream`, `bounded-channel`, `pipeline`, `main`
- `L05.AsyncTraps` (C# console: lowered await, `.Result` deadlock on a one-thread context, async void, fire-and-forget;
  exits by itself) — regions `lowered`, `deadlock`, `async-void`, `fire-and-forget` (all four shown as panels)
- `L05.VbRules.Tests` (xUnit compiling VB snippets with Roslyn: 8 rejected, 1 accepted) — regions in each snippet, `compile`

Sources: Microsoft Learn — Asynchronous programming with async and await, Async return types, `ValueTask<TResult>`,
Cancellation in managed threads, `Task.WaitAsync`, `Task.WhenAll`, `Task.WhenEach`, `Parallel.ForEachAsync`, Channels,
System.Linq.AsyncEnumerable in .NET 10, The lock statement, `System.Threading.Lock`, What is TimeProvider,
`ConcurrentDictionary.GetOrAdd`, `TaskScheduler.UnobservedTaskException`, Debug ThreadPool starvation, ASP.NET Core best
practices, Await operator (Visual Basic), The history of C#; .NET Blog — ConfigureAwait FAQ; GitHub dotnet/core — .NET 11
Preview 4 runtime release notes; GitHub dotnet/runtimelab — green-threads experiment results; kotlinlang.org —
coroutine basics, kotlinx `flow` builder; docs.python.org — asyncio tasks.

## 7 · Invariants

- Captured desk output must agree with the counts `FanOutTests` asserts (enforced at build).
- Every VB error id in table 7.7 must be asserted by `VbAsyncRulesTests.cs` (enforced at build).
- Captured notification counts must add up to the event count in `Program.cs` (enforced at build).
- Library code in `L05.PartnerRates` keeps `ConfigureAwait(false)` on every await and routes every timer through the
  injected `TimeProvider`; tests never sleep on the wall clock.
- `QueryOneAsync` never throws for a partner problem (only for caller cancellation) — §4's argument depends on it.
- The 30 calls start when the collection expression materialises the `Select` (`RateFanOut.QueryAllAsync`,
  `StreamAsync`); §4's prose and 4.7 depend on the result being an array, not a lazy `IEnumerable`.
- Console samples exit on their own; the deadlock demo gives up after one second.
- No employer or client names; the partner count stays "~30 external partners" (generic).

## 8 · Known gaps

- ⚠ Captured output in 7.5, 8.3 and 8.4 is pasted text; wall clock, pool size, the order of close answers and the
  producer-wait count (10 or 11) vary per run and per machine. Re-capture after changing a sample's output.
- ⚠ The fan-out speed-up is a single-run wall-clock measurement on one machine, not a benchmark.
- ⚠ The runtime-async paragraph describes a preview (.NET 11 Preview 4); update it when .NET 11 reaches GA.
- ⚠ Heatmap 7.8 is a rubric; only its VB column is backed by compilation. The other cells are the author's judgement
  and are labelled ESTIMATE, with links only for structured concurrency.
- ⚠ The VB accepted-patterns snippet (`AwaitPatterns`) is exercised by `L05.VbRules.Tests` but not shown as a panel.
- ⚠ Mapping rows for `CompletableFuture`, `Mono.block()`, `Promise.all` and `asyncio.TaskGroup` state behaviour of
  the reader's other stacks without a link (see § 4).
- ⚠ Mermaid 6.1 uses cluster-to-cluster edges: the "no" arrow leaves the row's border, not the hexagon.
