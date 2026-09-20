# Unit spec — lesson-10-testing-tdd-coverage.pdf

Built to `_standard.md`, in the shape of `lesson-01-dotnet-platform-map.md`. Content module
`0-script/lessons/lesson_10.py`. Samples `lesson-10-testing-tdd-coverage/samples/` (9 projects).

## 1 · Purpose

Move a reader who already runs TDD at a 100%-coverage standard onto the .NET testing stack, and upgrade the
standard itself. Four things are .NET-specific and get the pages: the **two test platforms** (VSTest and
Microsoft.Testing.Platform) under one framework choice and what `dotnet test` does in each on the .NET 10 SDK;
the **xUnit lifecycle** (a new test-class instance per case) against NUnit's shared fixture instance; the
**coverage gate written as MSBuild properties**, including which coverlet driver survives a platform move; and
**mutation testing** as the measurement that separates two suites this lesson ships with identical 100% line
and branch coverage. Everything else — JUnit → xUnit, Mockito → NSubstitute, MockMvc → `WebApplicationFactory`,
JaCoCo → coverlet, PIT → Stryker.NET, Cucumber → Reqnroll, Postman → `.http` — is one row in the concept map.

## 2 · Ownership & cadence

Owner **claude**, regenerable. Rebuild when the samples, `lesson_kit.py` or the renderer change. Re-verify
every November (new .NET major) and whenever one of these moves: the current versions in the §2 story
(xUnit v3 4.0.1 · MSTest 4.4.1 · NUnit 4.6.1), the MTP-mode `global.json` key, coverlet's MTP incompatibility,
and the Fluent Assertions licence. **Also rebuild whenever the curriculum's canonical tariff moves** — every
premium in the lesson is a run of `L10.Pricing`, and the coverage, mutation and test-count figures all shift
with it (they did on 2026-09-20). The captured figures in §4 are re-captured by re-running the four commands
in 9.1; they are **not** recomputed at build time except the six `loc()` bars in 9.4 and the method / scenario
counts behind the KPI tile and 9.3 (`test_methods()`, `feature_scenarios()`).

## 3 · Structure

22 pages at the 2026-09-20 build (after the cross-lesson tariff alignment). 58 blocks.

| § | Heading | Blocks |
|---|---|---|
| — | Contents | `toc` depth 2 (code panels are listed through the local `listed()` / `figure_heading()` helpers) |
| 1 | Why this lesson — you already test; .NET changes the plumbing | story (4 ¶) · `kpi` 1.1 (5 tiles) · `legend` (C#, tooling, architecture — only the tags the lesson uses) · info callout "Before you start" (4 items: prerequisite lessons · the 9 offline projects · `dotnet tool restore` for Stryker · the chip vocabulary) |
| 2 | The frameworks — and the platform underneath them | story (4 ¶) · mapping 2.1 (16 rows) · mermaid 2.2 flowchart LR (platform → package → `global.json` → command → coverage driver) · table 2.3 (attribute map, JUnit 5 / xUnit v3 / NUnit 4 / MSTest 4, 8 rows) · compare 2.4 (JUnit 5 `@ParameterizedTest` ↔ xUnit `TheoryData`) · code 2.5 (`L10.Pricing.Tests.csproj`) · compare 2.6 (C# `TheoryData` ↔ VB `TheoryData(Of …)`, plus the `.vbproj` decisions in its note — plan item 8) |
| 3 | TDD on the no-claim-bonus rule — red, green, refactor | story (4 ¶) · code 3.1 (first test) · code 3.2 (captured red run) · code 3.3 (the switch expression) · table 3.4 (the hand-worked rating sheet, **8 rows** — the canonical tariff's seven priced scenarios plus the declined one) + `tnote` · code 3.5 (`claims-guard` — the rule that refuses) + note |
| 4 | Fixtures and isolation — the constructor is your @BeforeEach | story (5 ¶ — the fifth is xUnit's parallel-by-class default and `[Collection]`; assembly fixtures are `[assembly: AssemblyFixture(typeof(T))]`) · code 4.1 (the fixture) · mermaid 4.2 sequence (per-test-case lifecycle) · table 4.3 (instance-per-test by framework, 4 rows) |
| 5 | Assertions and test doubles — one licence decision, two habits | story (4 ¶) · code 5.1 (NSubstitute) · compare 5.2 (C# ↔ VB `FakeTimeProvider` expiry, `keep=False`) · cards 5.3 (6 cards in 3 + 3 "(continued)" bands) |
| 6 | Coverage as a gate — 100% line and branch, failing the build | story (4 ¶) · code 6.1 (`CoverageGate.props`) · code 6.2 (captured failing run) · chart 6.3 bar (coverage with and without one test; no target line — it struck through the value labels, so the caption states the threshold instead) · table 6.4 (coverage tooling by platform, 6 rows) |
| 7 | Beyond coverage — what the mutation score tells you | story (4 ¶) · code 7.1 (the weak suite) · chartrow 7.2 grouped_bar (line / branch / mutation per suite; weak suite in amber) + 7.3 stacked_bar (mutants by outcome, recoloured green / red / slate to match 7.4) — both passed as ready `svg` because `chart_svg` takes no colours · mermaid 7.4 stateDiagram-v2 (life of a mutant) · table 7.5 (mutant states + the strong suite's counts, 6 rows) + `tnote` · code 7.6 (`stryker-config.json`) |
| 8 | Integration, API and BDD tests — in memory, with a clock you own | story (5 ¶ — the fifth is the test pyramid across an estate of services: the partner boundary, a stubbed `HttpMessageHandler` or WireMock.Net, contract tests with Pact.Net) · mermaid 8.1 flowchart TB with `direction LR` subgraphs (in-process request path) · code 8.2 (POST then GET) · code 8.3 (`ConfigureTestServices` clock swap) · compare 8.4 (Gherkin ↔ Reqnroll bindings) · table 8.5 (test layers, 8 rows incl. "Partner boundary") |
| 9 | Hands-on — run the suites, then judge them | story (3 ¶) · code 9.1 (4 commands) · code 9.2 (captured output of all four) · chartrow 9.3 donut (51 cases by kind) + 9.4 bar (`loc()` by role) · 9.5 threecol (carries over / learn fresh / unlearn) · warn "Traps" (5 — isolation incl. parallel classes, platform + coverage driver, Fluent Assertions licence, 100% ≠ tested, cancellation token) · ok checkpoint (5) · summary "Check yourself" (7) · footer |

Standard minimums as built: **9** numbered stories (need 6) · **1** mapping · **2** card bands of 3 (max 3) ·
**4** mermaid in **3** families — flowchart ×2, sequence, state (need 3 / 2) · **5** charts (need 3) · **23**
code panels from 15 `code()` + 4 `compare()` (need 6) · C# ↔ VB compares 2.6 and 5.2 · Java ↔ C# compare 2.4 ·
1 threecol · **6** tables besides the mapping (need 1) · **33** distinct official links (need 4).

## 4 · Derivation

Every number in the PDF is one of three kinds.

**MEASURED — captured from real runs on the build machine, re-captured by 9.1's four commands. Every row below
was re-run on 2026-09-20 after the canonical-tariff change; the dates in the rows say which run each figure
comes from:**

| Figure | Where | How |
|---|---|---|
| 33 / 8 / 5 / 3 / 2 test cases (51 total), from 25 hand-written test methods + 2 Gherkin scenarios | KPI, 9.2, 9.3 | `dotnet test` (and `dotnet run` for the MTP twin) on the five test projects; methods by `test_methods()` (`[Fact]`/`[Theory]`), scenarios by `feature_scenarios()` (`Scenario:` / `Scenario Outline:` — Reqnroll generates one method each, the outline's 4 example rows plus the plain scenario make its 5 cases). The C# count rose from 28 to 33 with the canonical tariff: the rating sheet grew to seven priced rows and the claims guard added its own decline theory |
| 100% line / 100% branch / 100% method | KPI, 6.2, 6.3, 7.2, §1, §7 | coverlet totals for the `L10.Pricing` module, for **both** the strong and the weak suite |
| 98.86% line / 97.14% branch, `dotnet test` fails (re-captured 2026-09-20 after the canonical-tariff change; it read 98.73% before, and 98.59% before that) | 6.2, 6.3 | a scratch copy of the samples with the `(CoverageClass)99` test deleted; the coverlet MSBuild task reports "The total line coverage is below the specified 100". The 6.3 note's drop is computed in the module as `100 − CUT_LINE` (1.14 points), never hard-typed |
| 35 branch points against 88 lines in that failing run — one uncovered branch costs 2.86 points, one uncovered line 1.14 | 6.2 note | `coverage.cobertura.xml` of the scratch run: `branches-valid=35`, `lines-valid=88` (both grew when the claims guard joined the library) |
| 8 branches for the 7 arms of `NoClaimBonus.DiscountFor` | 3.3 note | the committed suite's `coverage.cobertura.xml`: one branch line, `condition-coverage="100% (8/8)"` |
| Mutation 91.49% (43 killed / 4 survived) and 8.51% (4 / 43) | KPI, §1, §7, 7.2, 7.3, 9.2, footer | `dotnet stryker` in `L10.Pricing.Tests.Mtp` and `L10.Pricing.WeakTests.Mtp`, `test-runner: mtp`; re-run twice after the canonical-tariff change (13:53 and 15:04 on 2026-09-20) with identical results |
| 55 mutants: 47 tested, 4 compile error, 4 ignored | 7.3, 7.5 | Stryker.NET JSON report; the score denominator is `valid` = 47, per its own formula. Three more mutants than before the tariff change — the claims guard's arms |
| All 4 strong-suite survivors are exception-message string mutations | §7, 7.5 | the same JSON report — `NoClaimBonus.cs` L11 ("cannot be negative"), `PremiumCalculator.cs` L15 ("unknown class"), `QuoteService.cs` L31 and L33 (the two interpolated messages); the §7 story names all four. The claims guard's own message survives nothing: 3.5's theory asserts on `ex.Message`, which is why §7 can say the survivors are *everywhere except* there |
| A Stryker.NET run takes 14 s (strong) and 12 s (weak) | 7.6, 8.5, 9.1 notes | one run each on 2026-09-20 15:04 at `concurrency: 1` with the projects already built, timed from the run's own log timestamps |
| The red run: 8 failures, "Exception type was not an exact match" | 3.2 | the library stubbed with `throw new NotImplementedException()` in a scratch copy |
| `dotnet test` on the MTP twin fails with "Testing with VSTest target is no longer supported …" | 2.5 note | run against `L10.Pricing.Tests.Mtp` on SDK 10.0.401 |
| 120 / 211 / 57 / 75 / 32 / 47 code lines; 396 test lines to 120 library lines ≈ 3.3:1 | 9.4 | `loc_dir()` at build time (`lesson_kit.loc` over the sample `.cs`/`.vb` files, excluding Reqnroll's generated `*.feature.cs`) — these six bars and the ratio move on their own with every edit to the samples, so they needed no re-capture for the tariff change |

**VERIFIED — dated facts with a `link()` to an official source, checked 2026-09-19:**

- Two test platforms, "don't mix VSTest-based and MTP-based projects in the same solution", and `dotnet test`'s
  "Native MTP mode is available in .NET 10 SDK and later" — Microsoft Learn,
  [Microsoft.Testing.Platform vs VSTest](https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-platform-vs-vstest).
- MTP mode switched on by `{"test": {"runner": "Microsoft.Testing.Platform"}}` in `global.json`;
  `TestingPlatformDotnetTestSupport` is the legacy VSTest bridge and "will be removed in MTP version 2 if run
  with .NET 10 SDK" — Microsoft Learn,
  [Testing with dotnet test](https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-with-dotnet-test).
- `xunit.v3` package variants (`mtp-off` / `mtp-v1` / `mtp-v2`, since v3 build 3.2.0) and
  `UseMicrosoftTestingPlatformRunner` — [xUnit.net v3 on Microsoft Testing Platform](https://xunit.net/docs/getting-started/v3/microsoft-testing-platform);
  v3 test projects are stand-alone executables — [xUnit.net v3 migration](https://xunit.net/docs/getting-started/v3/migration).
- Current versions: xUnit v3 **4.0.1** (12 Sep 2026) · MSTest **4.4.1** (16 Sep 2026) · NUnit **4.6.1**
  (19 May 2026) · NSubstitute **6.2.0**, BSD-3-Clause (11 Aug 2026) · Testcontainers **4.15.0**, needs a
  Docker-compatible runtime — the four NuGet package pages.
- NUnit's default is **one fixture instance shared by every test**; `[FixtureLifeCycle(LifeCycle.InstancePerTestCase)]`
  since NUnit 3.13 — [NUnit FixtureLifeCycle](https://docs.nunit.org/articles/nunit/writing-tests/attributes/fixturelifecycle.html).
  MSTest creates the instance per test method — [MSTest test lifecycle](https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-mstest-writing-tests-lifecycle).
- Fluent Assertions 8+ is the Xceed Community License; commercial use needs a per-seat annual subscription;
  v7 stays Apache-2.0 — [Fluent Assertions licensing FAQ](https://xceed.com/fluent-assertions-faq/). The
  community fork is [AwesomeAssertions](https://github.com/AwesomeAssertions/AwesomeAssertions).
- Moq shipped SponsorLink in 4.20.0 (8 Aug 2023) and removed it in 4.20.2 the next day (the five-day span the
  first draft quoted runs from the 4.20.0-rc) — [Moq changelog](https://github.com/devlooped/moq/blob/main/changelog.md).
- xUnit runs test classes in parallel by default (each class is its own collection; tests inside one class do
  not run in parallel) and `[Collection]` groups classes — [xUnit parallelism](https://xunit.net/docs/running-tests-in-parallel).
  Assembly fixtures in v3 are `[assembly: AssemblyFixture(typeof(T))]`, constructor-injected, with **no**
  `IAssemblyFixture<T>` interface (that name belongs to a v2 third-party package; the first draft used it) —
  [xUnit shared context](https://xunit.net/docs/shared-context).
- Stryker.NET's default `coverage-analysis` is `perTest`: only the tests that cover a mutant run against it —
  [Stryker.NET configuration](https://stryker-mutator.io/docs/stryker-net/configuration/).
- WireMock.Net (stub HTTP server usable in unit and integration tests) and Pact.Net (consumer-driven contract
  testing) exist and are maintained — [WireMock.Net](https://github.com/wiremock/WireMock.Net) ·
  [Pact.Net](https://github.com/pact-foundation/pact-net).
- "coverlet.collector and coverlet.msbuild cannot be used with the Microsoft Testing Platform"; `coverlet.MTP`
  is the MTP driver — [coverlet](https://github.com/coverlet-coverage/coverlet) and its
  [MTP integration doc](https://github.com/coverlet-coverage/coverlet/blob/master/Documentation/Coverlet.MTP.Integration.md);
  Microsoft's own extension, whose `--coverage-output-format` accepts `coverage` (default), `xml` and `cobertura` —
  [MTP code coverage](https://learn.microsoft.com/en-us/dotnet/core/testing/microsoft-testing-platform-extensions-code-coverage);
  [ReportGenerator](https://github.com/danielpalme/ReportGenerator) for the HTML report.
- Mutant states and `mutation score = detected / valid × 100` —
  [mutant states and metrics](https://stryker-mutator.io/docs/mutation-testing-elements/mutant-states-and-metrics/) ·
  [Stryker.NET](https://stryker-mutator.io/docs/stryker-net/introduction/).
- SpecFlow reached end of life on **31 December 2024** after Tricentis discontinued it; Reqnroll is the
  community fork — [SpecFlow end-of-life](https://reqnroll.net/news/2025/01/specflow-end-of-life-has-been-announced/).
- `WebApplicationFactory` / `TestServer` / `ConfigureTestServices` —
  [integration tests in ASP.NET Core](https://learn.microsoft.com/en-us/aspnet/core/test/integration-tests?view=aspnetcore-10.0);
  the source generator that emits `public partial class Program` for top-level statements landed in the 10.0
  release — [dotnet/aspnetcore#58199](https://github.com/dotnet/aspnetcore/pull/58199).
- `.http` file syntax incl. request variables — [.http files](https://learn.microsoft.com/en-us/aspnet/core/test/http-files?view=aspnetcore-10.0).
  `FakeTimeProvider` ships in `Microsoft.Extensions.TimeProvider.Testing` — [FakeTimeProvider](https://learn.microsoft.com/en-us/dotnet/api/microsoft.extensions.time.testing.faketimeprovider).
  `[ExcludeFromCodeCoverage]` targets and its `Justification` property — [the API page](https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.codeanalysis.excludefromcodecoverageattribute).
  xUnit1051 wants `TestContext.Current.CancellationToken` — [xUnit1051](https://xunit.net/xunit.analyzers/rules/xUnit1051).
  Playwright for .NET framework integrations — [Playwright for .NET](https://playwright.dev/dotnet/docs/intro).

**TARIFF — the curriculum's canonical tariff, used exactly (no variant):**

`L10.Pricing` implements `_curriculum.md` § *Canonical tariff* verbatim: base rates Class 1 2.1% · Class 2+ 1.2% ·
Class 3+ 0.9% · Class 3 0.4% (a rate, never a flat amount); loadings young driver +20%, commercial +25% or +35%
over 3,000 cc, claims 0 → +0% · 1 → +10% · 2 → +25% · **3 or more → declined**; no-claim ladder 0/20/25/30/40/50%
on `claimFreeYears = ClaimsLast5Years == 0 ? LicenceYears : 0`; net, stamp duty (0.4%) and VAT (7%) each
`Math.Round(…, 2, MidpointRounding.AwayFromZero)` — **to the satang, not `Math.Ceiling`**. The decline is raised as
`QuoteDeclinedException` (lesson 02's vocabulary, named in 3.5's note) because this lesson teaches exceptions as
mutation targets, not persistence. Row 7 of the 3.4 sheet *is* the curriculum's worked example — Class 1,
550,000 THB, aged 23, 4 claim-free years → net 8,316.00 · duty 33.26 · VAT 584.45 · **total 8,933.71 THB** — so
the theory table fails the moment this lesson's arithmetic drifts from the other eleven. Only two panels in
the PDF print money — the 3.4 sheet and the Gherkin outline in 8.4 (`12600.00 / 10080.00 / 8820.00 / 6300.00`
net, and `13860.00` for the one-claim scenario) — and both are assertions a real run proves; `L10.QuoteApi`'s
round-trip test in 8.2 asserts status codes, not amounts. The 3.4 `tnote` tells the reader the rates are
illustrative and names the curriculum.

**ESTIMATE — labelled in place:** the mutation-run cadence in 7.6 ("nightly or per pull request on changed
projects") and the section 8 estate-pyramid paragraph (a design judgement). The mutation cost claim is no
longer an estimate: it is the measured 14 / 12 seconds plus the documented `perTest` analysis. Tables 2.1, 2.3,
4.3, 6.4 and 8.5 are mappings and judgements, not measurements.

## 5 · Presentation

Format 00 via `brief_pdf.py`; code panels from `lesson_kit`. Local helpers in the module (kit requests):
`listed()` / `pcode()` / `pcompare()` put a panel's heading in the Contents and strip Pygments' red error box;
`figure_heading()` gives the threecol a numbered, kept-with-next heading; `captured()` labels pasted terminal
output; `nw()` stops a table-cell attribute name wrapping inside itself; **`tnote()`** renders a table's
reading in the code-panel note style, because `brief_pdf`'s `table` block renders only heading + rows and
silently drops a `note` key. **`suites_svg()` / `mutant_states_svg()`** call `chart_svg` and swap its series
colours (it takes none) so 7.2's weak suite is amber and 7.3 uses 7.4's language — green detected, red counted
against you, slate excluded — instead of green meaning "weak" on one figure and "detected" on the next.
`LOCAL_CSS` keeps callout, story and table (`h2`) headings off a page foot, caps the three tall diagram families
(sequence 3.3in, state 2.2in, flowchart 3.2in), keeps the "Check yourself" callout in one piece, and lets link
labels wrap at spaces (`overflow-wrap:anywhere` instead of the renderer's `word-break:break-all`, which split
"Fluent A/ssertions" mid-word) — the link labels were also shortened.

Mermaid: 2.2 is `flowchart LR`; 8.1 is `flowchart TB` with `direction LR` subgraphs — it was a single-row
`LR` chain in the first render and printed as an unreadable strip; 4.2 and 7.4 take colour from an
`%%{init:…}%%` directive plus (7.4) `classDef` + `class` assignment, which `stateDiagram-v2` supports.

Pagination: the first render left pages 4, 5, 6, 9, 13 and 14 between a quarter and a half empty. Fixed by
removing a framework-capability heatmap that repeated tables 2.3 and 4.3, dropping two rows from 2.3,
shortening the chartrow to `height 165`, and giving compare 5.2 `keep=False`. After the review fixes added
2.6 and two paragraphs, page 9 fell to 38% empty until the 5.1 / 5.2 notes and two story sentences were
tightened so 5.2 fits behind 5.1. The canonical-tariff pass added four rows to 3.4 and the whole of 3.5, which
pushed the lesson from 21 to 22 pages and reshuffled the gaps. Measured with pymupdf on the final render
(trailing blank as a share of the content area): no page except the last is more than about a third empty; the
largest gaps are pages 10 (28.3%), 17 (25.4%), 12 (21.8%), 14 (16.9%) and 6 (16.8%), each where an unbreakable
panel or chartrow jumps. The last page (22) holds the "Check yourself" summary, the one-line recap and the
footer, and is 58% empty — the permitted exception.

## 6 · Inputs

`roster.py`; the nine sample projects — `L10.Pricing` (library under test), `L10.Pricing.Tests` (strong xUnit
suite + the 100% gate), `L10.Pricing.Tests.Mtp` and `L10.Pricing.WeakTests.Mtp` (the same sources built as
Microsoft.Testing.Platform executables, for Stryker), `L10.Pricing.VbTests` (VB xUnit),
`L10.Pricing.WeakTests` (100%-covered, asserts almost nothing), `L10.Pricing.Specs` (Reqnroll),
`L10.QuoteApi` + `L10.QuoteApi.Tests` (minimal API and its in-memory tests); shared files
`CoverageGate.props`, `Shared/Requests.cs`, `dotnet-tools.json`, `stryker-config.json`. Regions used:
`ncb-rule`, `claims-guard`, `first-test`, `theory`, `vb-theory`, `fixture`, `nsubstitute`, `fake-time`,
`vb-fake-time`, `weak`, `round-trip`, `swap-clock`, `steps`. `Shared/Requests.cs` carries an `engineCc`
parameter so the commercial +35% band above 3,000 cc can be quoted. Sources: the 33 links listed in §4 and
the module header; the premium rules come from `_curriculum.md` § *Canonical tariff*.

## 7 · Invariants

- `L10.Pricing.WeakTests` must keep reaching **100% line and branch** coverage while scoring far below the
  strong suite on mutation — that contrast is the lesson's argument. If a refactor of `L10.Pricing` breaks it,
  fix the weak suite's coverage, not the argument.
- The `.Mtp` twins must compile **the same source files** as their VSTest counterparts (`<Compile Include>`
  links, not copies), so "same tests, other platform" stays literally true.
- `L10.QuoteApi/Program.cs` must not declare `public partial class Program` — the §8 claim that .NET 10
  generates it is proved by the project compiling with warnings as errors.
- The panels in 2.4, 2.6, 5.2 and 8.4 are `compare()`s: every shown line stays ≤ 62 characters. The Gherkin feature
  file and `PremiumSteps.cs` were rewritten for that limit and must not grow back.
- Privacy: experience is referenced generically (a 100%-coverage TDD standard, Postman collections per
  environment, k6, SonarQube). No employer, client or insurer names.
- **`L10.Pricing` is the curriculum's canonical tariff and nothing else.** No rate, loading, ladder step or
  rounding may drift from `_curriculum.md` § *Canonical tariff*; row 7 of the 3.4 theory sheet is that
  section's own worked example (8,933.71 THB) and is the tripwire. A future change to the tariff changes the
  curriculum first, then this library, then the re-captured figures — never the other way round.
- Boundaries: ASP.NET Core belongs to lesson 08, EF Core to 09, `TimeProvider` to 05, MSBuild to 07, security
  testing to 11, deployment to 12 — each gets one sentence and a `ref(n)`. **Every `ref(n)` to an earlier
  lesson is in the past tense and names something that lesson really contains** — the cross-lesson review
  (2026-09-20) found two that were not: a forward promise that lesson 09 would replace this lesson's
  in-memory store, and a Browser/E2E row pointing at lesson 12 for content it has none of.

## 8 · Known gaps
- ⚠ **Two xUnit generations in one track (cross-lesson review 2026-09-20).** Lessons 07 and 10 use xUnit v3 (`xunit.v3.mtp-off`, `Exe` test projects); the test projects of lessons 02-06, 08, 09, 11 and 12 still reference xUnit v2 (`xunit` 2.9.3). Section 2 says so in one sentence; migrating those fourteen projects was judged not worth the risk because their `[Fact]`/`[Theory]`/`Assert` code is unchanged by v3. If they are ever migrated, delete that sentence.

- ⚠ Most of the measured figures are **captured text**, not recomputed at build time. If a test is added or
  the rating rules change, 9.2, the KPI tiles, 6.2/6.3 and 7.2/7.3/7.5 go stale together; re-run 9.1's four
  commands and update the constants at the top of `lesson_10.py` (`CASES`, `STRONG_MUT`, `WEAK_MUT`,
  `MUT_*`, `STRONG_KILLED` / `STRONG_SURVIVED`, `WEAK_KILLED` / `WEAK_SURVIVED`, `CUT_LINE`, `CUT_BRANCH`).
  **Re-capture the 6.2 scratch run whenever `L10.Pricing` changes** — its line figure has moved twice already
  (98.59 → 98.73 → 98.86), and the "35 branches against 88 lines" and "2.86 / 1.14 points" in the 6.2 note move
  with it; so does "8 branches for 7 arms" in the 3.3 note. The 6.3 caption's point-drop is now *derived*
  (`100 − CUT_LINE`) rather than typed, which is how the 1.27 from the previous run survived one cycle. Only
  the six `loc()` bars in 9.4 and the method / scenario counts are live.
- ⚠ 3.2 and 6.2 are captured from **scratch copies** of the samples (a stubbed library, and the suite with one
  test deleted). Those copies are not in the repository, so `verify_samples.py` cannot re-prove them.
- ⚠ Stryker.NET runs at `concurrency: 1` for determinism; the 14 s / 12 s in the 7.6, 8.5 and 9.1 notes is one
  measured run each on a warm build — a cold restore and build take longer, and CI at higher concurrency will
  differ. The figure grew from ten seconds when the claims guard added three mutants.
- ⚠ The partner-boundary paragraph and row in section 8 describe a stubbed `HttpMessageHandler`, WireMock.Net
  and Pact.Net; none is demonstrated by a sample (lesson 08 owns `HttpClientFactory`).
- ⚠ The repository's `global.json` does **not** opt into MTP mode (it is shared with eleven other lessons), so
  the MTP-mode `dotnet test` described in §2 is documented but not exercised by any sample. `dotnet run` is.
- ⚠ Testcontainers, Playwright and out-of-process `.http` execution are described, not demonstrated — no
  Docker, no browser and no listening port on the build machine.
- ⚠ The Java panel in 2.4 is not compiled; only its C# counterpart comes from a built sample.
- ⚠ `brief_pdf`'s `table` block ignores a `note` key. This lesson works around it with a local `tnote()`
  helper; a kit fix would let tables carry their reading natively (see `kit_requests`).
