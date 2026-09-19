# -*- coding: utf-8 -*-
"""Lesson 10 — Testing, TDD & 100% Coverage. Follows the reference shape of lesson_01.py and the
contract in 1-analysis/spec_lesson-pdfs/_standard.md.

The reader already runs TDD at 100% coverage, so the lesson spends its words on what is .NET-specific:
two test platforms under one framework choice, a coverage gate written in MSBuild, an assertion library
that changed its licence, and mutation testing as the answer to "100% covered but is it tested?".
Every score in §6 and §7 is measured from a real run of the samples in this repository.
"""
import re

import chart_svg
from lesson_kit import (BUILD_DATE, DIFFERENT, ESTIMATE, MEASURED, REPO, RENAMED, SAME, TRAP, VERIFIED,
                        T_ARCH, T_CS, T_TOOLING, code, compare, esc, from_sample, from_text,
                        legend, link, loc, mapping, pill, style_block)
from lessons.roster import meta, ref

META = meta(
    10,
    subtitle="xUnit v3, the two test platforms, a 100% coverage gate that fails the build, and the "
             "mutation score that tells you whether 100% meant anything",
    objectives=[
        "Pick a test framework and — the decision that actually matters in .NET — the test platform under it, "
        "and know what `dotnet test` does on the .NET 10 SDK in each mode",
        "Write xUnit v3 facts, theories and fixtures in C# and in Visual Basic, and read the NUnit and MSTest "
        "forms of the same test",
        "Build doubles the .NET way: NSubstitute for interaction tests, real in-memory fakes for state, and "
        "FakeTimeProvider instead of a clock you own",
        "Enforce 100% line and branch coverage as an MSBuild gate that fails `dotnet test`, and know which "
        "coverage driver survives a move to Microsoft.Testing.Platform",
        "Prove with Stryker.NET that a 100%-covered suite can assert almost nothing, and set a mutation "
        "threshold beside the coverage one",
        "Test an ASP.NET Core API in memory with WebApplicationFactory, swap its clock, and write executable "
        "Gherkin specifications with Reqnroll",
    ],
    maps_from="JUnit 5 with Mockito and AssertJ, MockMvc integration tests, JaCoCo coverage gates, PIT "
              "mutation testing, Cucumber feature files, Postman collections automated per environment and a "
              "delivery standard of 100% unit-test coverage.",
)

L = "lesson-10-testing-tdd-coverage/samples"
LIB = f"{L}/L10.Pricing"
NCB = f"{LIB}/NoClaimBonus.cs"
CALC = f"{LIB}/PremiumCalculator.cs"
TESTS = f"{L}/L10.Pricing.Tests"
NCB_TESTS = f"{TESTS}/NoClaimBonusTests.cs"
QS_TESTS = f"{TESTS}/QuoteServiceTests.cs"
VB_TESTS = f"{L}/L10.Pricing.VbTests"
VB_NCB = f"{VB_TESTS}/NoClaimBonusVbTests.vb"
VB_QS = f"{VB_TESTS}/QuoteServiceVbTests.vb"
WEAK = f"{L}/L10.Pricing.WeakTests/WeakSuite.cs"
API_TESTS = f"{L}/L10.QuoteApi.Tests/QuoteApiTests.cs"
FEATURE = f"{L}/L10.Pricing.Specs/Features/NoClaimBonus.feature"
STEPS = f"{L}/L10.Pricing.Specs/Steps/PremiumSteps.cs"
GATE = f"{L}/CoverageGate.props"
STRYKER_CFG = f"{L}/L10.Pricing.Tests.Mtp/stryker-config.json"
TEST_CSPROJ = f"{TESTS}/L10.Pricing.Tests.csproj"

# ── official sources ─────────────────────────────────────────────────────────────────────────────
PLATFORMS = link("Microsoft.Testing.Platform vs VSTest",
                 "https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-platform-vs-vstest")
DOTNETTEST = link("dotnet test docs",
                  "https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-with-dotnet-test")
XUNITMTP = link("xUnit.net v3 on Microsoft Testing Platform",
                "https://xunit.net/docs/getting-started/v3/microsoft-testing-platform")
XUNITMIG = link("xUnit.net v3 migration", "https://xunit.net/docs/getting-started/v3/migration")
XUNITNUGET = link("xunit.v3 on NuGet", "https://www.nuget.org/packages/xunit.v3")
XUNIT1051 = link("xUnit1051", "https://xunit.net/xunit.analyzers/rules/xUnit1051")
PARALLEL = link("xUnit parallelism", "https://xunit.net/docs/running-tests-in-parallel")
SHAREDCTX = link("xUnit shared context", "https://xunit.net/docs/shared-context")
NUNITNUGET = link("NUnit on NuGet", "https://www.nuget.org/packages/NUnit")
NUNITLIFE = link("NUnit FixtureLifeCycle",
                 "https://docs.nunit.org/articles/nunit/writing-tests/attributes/fixturelifecycle.html")
MSTESTNUGET = link("MSTest on NuGet", "https://www.nuget.org/packages/MSTest")
MSTESTLIFE = link("MSTest test lifecycle",
                  "https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-mstest-writing-tests-lifecycle")
FALICENCE = link("Fluent Assertions FAQ", "https://xceed.com/fluent-assertions-faq/")
AWESOME = link("AwesomeAssertions", "https://github.com/AwesomeAssertions/AwesomeAssertions")
MOQLOG = link("Moq changelog", "https://github.com/devlooped/moq/blob/main/changelog.md")
NSUBNUGET = link("NSubstitute on NuGet", "https://www.nuget.org/packages/NSubstitute")
COVERLET = link("coverlet", "https://github.com/coverlet-coverage/coverlet")
COVMTP = link("coverlet.MTP",
              "https://github.com/coverlet-coverage/coverlet/blob/master/Documentation/Coverlet.MTP.Integration.md")
MSCOV = link("Microsoft.Testing.Platform code coverage",
             "https://learn.microsoft.com/en-us/dotnet/core/testing/microsoft-testing-platform-extensions-code-coverage")
REPORTGEN = link("ReportGenerator", "https://github.com/danielpalme/ReportGenerator")
EXCLUDE = link("ExcludeFromCodeCoverageAttribute",
               "https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.codeanalysis.excludefromcodecoverageattribute")
STRYKER = link("Stryker.NET", "https://stryker-mutator.io/docs/stryker-net/introduction/")
STRYKERCFG = link("Stryker.NET configuration",
                  "https://stryker-mutator.io/docs/stryker-net/configuration/")
MUTSTATES = link("mutant states and metrics",
                 "https://stryker-mutator.io/docs/mutation-testing-elements/mutant-states-and-metrics/")
REQNROLL = link("SpecFlow EOL",
                "https://reqnroll.net/news/2025/01/specflow-end-of-life-has-been-announced/")
INTEGRATION = link("integration tests in ASP.NET Core",
                   "https://learn.microsoft.com/en-us/aspnet/core/test/integration-tests?view=aspnetcore-10.0")
PROGGEN = link("public Program source generator", "https://github.com/dotnet/aspnetcore/pull/58199")
HTTPFILES = link(".http files",
                 "https://learn.microsoft.com/en-us/aspnet/core/test/http-files?view=aspnetcore-10.0")
TESTCONTAINERS = link("Testcontainers for .NET", "https://www.nuget.org/packages/Testcontainers")
PLAYWRIGHT = link("Playwright .NET", "https://playwright.dev/dotnet/docs/intro")
WIREMOCK = link("WireMock.Net", "https://github.com/wiremock/WireMock.Net")
PACT = link("Pact.Net", "https://github.com/pact-foundation/pact-net")
FAKETIME = link("FakeTimeProvider",
                "https://learn.microsoft.com/en-us/dotnet/api/microsoft.extensions.time.testing.faketimeprovider")

# Pygments boxes tokens it cannot lex in red (VB interpolated strings, `$` inside a Gherkin/JSON string).
# The code is valid — every panel is cut from a project verify_samples.py builds — so drop the box.
_ERROR_SPAN = re.compile(r'<span style="border: 1px solid #F00">(.*?)</span>', re.S)

# Lesson-local print rules (kit request — as lessons 01/02/12): a callout or story heading never prints
# alone at a page foot, and the tall diagram families are capped so one diagram cannot fill a page.
LOCAL_CSS = ("<style>a.lnk, a { word-break:normal; overflow-wrap:anywhere; } "
             "h2 { break-after:avoid; page-break-after:avoid; } "
             '.callout[style*="#4F46E5"] { break-inside:avoid; page-break-inside:avoid; } '
             ".callout .ct { break-after:avoid; page-break-after:avoid; } "
             ".callout li:first-child { break-before:avoid; page-break-before:avoid; } "
             ".story .ct { break-after:avoid; page-break-after:avoid; } "
             '.mmd svg[aria-roledescription="sequence"] { max-height:3.3in; } '
             '.mmd svg[aria-roledescription="stateDiagram"] { max-height:2.2in; } '
             '.mmd svg[aria-roledescription="flowchart-v2"] { max-height:3.2in; } '
             ".codeblk > .ct { break-after:avoid; page-break-after:avoid; }</style>")


def listed(block, heading):
    """Put a code()/compare() panel in the Contents at level 2 and remove Pygments' error boxes
    (kit request — as lesson 01)."""
    block.update(heading=heading, toc=2)
    block["html"] = _ERROR_SPAN.sub(r"\1", block["html"])
    return block


def pcode(s, heading, note, keep=None):
    return listed(code(s, heading=heading, note=note, keep=keep), heading)


def pcompare(left, right, heading, note, keep=None):
    return listed(compare(left, right, heading=heading, note=note, keep=keep), heading)


def figure_heading(text):
    """A numbered heading for a block type that prints none of its own (threecol), kept with that block."""
    return {"type": "html", "html": f'<div class="figh"><h2>{esc(text)}</h2></div>', "heading": text,
            "toc": 2, "_keep_with_next": True}


def captured(text, label, note="captured on the build machine"):
    return from_text(text, "text", label=label, file=note)


def tnote(html):
    """A table's reading — `table` blocks render only heading + rows, so the note is its own block
    in the code-panel note style (kit request)."""
    return {"type": "html", "html": f'<div class="lnote" style="margin-top:-4px">{html}</div>'}


def nw(*items):
    """Table-cell code that never wraps inside itself (a wrapped attribute name reads wrong)."""
    return " · ".join(f'<code style="white-space:nowrap">{c}</code>' for c in items)


# ── measured figures ─────────────────────────────────────────────────────────────────────────────
def loc_dir(*relative_dirs):
    """Non-blank, non-comment lines of every C#/VB file under these sample folders (MEASURED)."""
    files = []
    for d in relative_dirs:
        for p in sorted((REPO / d).rglob("*")):
            if (p.is_file() and p.suffix in (".cs", ".vb") and not {"obj", "bin"} & set(p.parts)
                    and not p.name.endswith(".feature.cs")):   # Reqnroll regenerates that on every build
                files.append(str(p.relative_to(REPO)).replace("\\", "/"))
    return loc(*files)


def n_projects():
    return len(list((REPO / L).glob("*/*.*proj")))


def test_methods(*relative_dirs):
    """[Fact]/[Theory] and <Fact>/<Theory> methods declared under these folders (MEASURED)."""
    n = 0
    for d in relative_dirs:
        for p in (REPO / d).rglob("*"):
            if p.is_file() and p.suffix in (".cs", ".vb") and not {"obj", "bin"} & set(p.parts):
                text = p.read_text(encoding="utf-8-sig")
                n += len(re.findall(r"\[(?:Fact|Theory)[\](]", text))
                n += len(re.findall(r"<(?:Fact|Theory)>", text))
    return n


def feature_scenarios(*relative_dirs):
    """Gherkin `Scenario:` / `Scenario Outline:` lines under these folders — Reqnroll generates one test
    method for each (MEASURED)."""
    n = 0
    for d in relative_dirs:
        for p in (REPO / d).rglob("*.feature"):
            if not {"obj", "bin"} & set(p.parts):
                n += len(re.findall(r"^\s*Scenario(?: Outline)?:", p.read_text(encoding="utf-8-sig"), re.M))
    return n


# Test-case counts and scores captured from the real runs shown in 9.2 on the build machine.
CASES = [("C# unit tests", 28), ("VB unit tests", 8), ("Gherkin scenarios", 5),
         ("In-memory API tests", 3), ("Weak-suite demo", 2)]
STRONG_MUT, WEAK_MUT = 90.91, 11.36           # Stryker.NET mutation scores, %
MUT_TESTED, MUT_IGNORED, MUT_COMPILE = 44, 4, 4
STRONG_KILLED, STRONG_SURVIVED = 40, 4
WEAK_KILLED, WEAK_SURVIVED = 5, 39
CUT_LINE, CUT_BRANCH = 98.73, 96.55           # coverage with one test deleted

RED_OUTPUT = r"""
# NoClaimBonus.DiscountFor exists but still throws NotImplementedException
dotnet test --filter "FullyQualifiedName~NoClaimBonusTests"

  Failed L10.Pricing.Tests.NoClaimBonusTests.No_claim_free_years_means_no_discount [1 ms]
  Error Message:
   System.NotImplementedException : The method or operation is not implemented.

  Failed L10.Pricing.Tests.NoClaimBonusTests.Negative_years_are_rejected [2 ms]
  Error Message:
   Assert.Throws() Failure: Exception type was not an exact match
Expected: typeof(System.ArgumentOutOfRangeException)
Actual:   typeof(System.NotImplementedException)

Failed!  - Failed:     8, Passed:     0, Skipped:     0, Total:     8, Duration: 43 ms
"""

GREEN_OUTPUT = r"""
# the same command after the switch expression is written
Passed!  - Failed:     0, Passed:     8, Skipped:     0, Total:     8, Duration: 41 ms
"""

GATE_OUTPUT = r"""
# one test deleted: the (CoverageClass)99 arm of BaseRate is no longer reached
dotnet test L10.Pricing.Tests

Passed!  - Failed: 0, Passed: 27, Skipped: 0, Total: 27, Duration: 89 ms
  [coverlet]
  Calculating coverage result...
   Generating report '.build/artifacts/coverage/L10.Pricing.Tests/coverage.cobertura.xml'

+-------------+--------+--------+--------+
| Module      | Line   | Branch | Method |
+-------------+--------+--------+--------+
| L10.Pricing | 98.73% | 96.55% | 100%   |
+-------------+--------+--------+--------+

coverlet.msbuild.targets(73,5): error : The total line coverage is below the specified 100
coverlet.msbuild.targets(73,5): error : The total branch coverage is below the specified 100
# every test passed and dotnet test still failed — that is the gate
"""

HANDS_ON = r"""
# 1 · build, test and run all nine projects
python 0-script/verify_samples.py --only 10

# 2 · the strong suite with its 100% line + branch gate (VSTest mode)
dotnet test lesson-10-testing-tdd-coverage/samples/L10.Pricing.Tests

# 3 · the same tests as a Microsoft.Testing.Platform executable
dotnet run --project lesson-10-testing-tdd-coverage/samples/L10.Pricing.Tests.Mtp

# 4 · mutation-test the strong suite, then the deliberately weak one
cd lesson-10-testing-tdd-coverage/samples
dotnet tool restore
cd L10.Pricing.Tests.Mtp     && dotnet stryker
cd ../L10.Pricing.WeakTests.Mtp && dotnet stryker
"""

HANDS_ON_OUTPUT = r"""
# 1 · verify_samples.py --only 10   (paths shortened, five PASS lines left out)
dotnet SDK 10.0.401  (D:\_env_storeage\dotnet\dotnet.exe)
PASS  library     6.9s  L10.Pricing/L10.Pricing.csproj
PASS  test        6.0s  L10.Pricing.Tests/L10.Pricing.Tests.csproj
PASS  console     5.3s  L10.Pricing.Tests.Mtp/L10.Pricing.Tests.Mtp.csproj
PASS  web         5.0s  L10.QuoteApi/L10.QuoteApi.csproj

9/9 sample projects passed

# 2 · dotnet test L10.Pricing.Tests
Passed!  - Failed: 0, Passed: 28, Skipped: 0, Total: 28, Duration: 91 ms
| Module      | Line | Branch | Method |
| L10.Pricing | 100% | 100%   | 100%   |

# 3 · dotnet run --project L10.Pricing.Tests.Mtp
Test run summary: Passed! - L10.Pricing.Tests.Mtp.dll (net10.0|x64)
  total: 28   failed: 0   succeeded: 28   skipped: 0   duration: 320ms

# 4 · dotnet stryker, in each .Mtp project
[INF] 44 total mutants will be tested
Killed:   40      Survived:  4      Timeout:   0
[INF] The final mutation score is 90.91 %
Killed:    5      Survived: 39      Timeout:   0
[INF] The final mutation score is 11.36 %
[WRN] Final mutation score is below threshold break. Crashing...
"""

JUNIT_THEORY = """
// JUnit 5 — the same rule, the same shape
static Stream<Arguments> table() {
    return Stream.of(
        arguments(1, new BigDecimal("0.20")),
        arguments(2, new BigDecimal("0.25")),
        arguments(3, new BigDecimal("0.30")),
        arguments(4, new BigDecimal("0.40")),
        arguments(5, new BigDecimal("0.50")),
        arguments(9, new BigDecimal("0.50")));
}

@ParameterizedTest
@MethodSource("table")
void discountGrowsWithClaimFreeYears(
        int years, BigDecimal expected) {
    var discount = NoClaimBonus.discountFor(years);

    assertThat(discount).isEqualByComparingTo(expected);
}
"""


def suites_svg():
    """7.2 with the weak suite in amber, so green never means 'weak' next to 7.3 and 7.4 where it means
    'detected' (chart_svg takes no colours — kit request)."""
    svg = chart_svg.grouped_bar(
        ["Line %", "Branch %", "Mutation %"],
        [("Strong suite", [100.0, 100.0, STRONG_MUT]), ("Weak suite", [100.0, 100.0, WEAK_MUT])],
        width=390, height=165, ylabel="%")
    assert chart_svg.SERIES[1] in svg
    return svg.replace(chart_svg.SERIES[1], chart_svg.SERIES[2])


def mutant_states_svg():
    """7.3 recoloured to the language of 7.4: chart_svg's stacked_bar takes no colours, so swap its four
    series colours for detected = green, undetected = red, excluded = slate (kit request)."""
    svg = chart_svg.stacked_bar(
        ["Strong suite", "Weak suite"],
        [("Killed", [STRONG_KILLED, WEAK_KILLED]), ("Survived", [STRONG_SURVIVED, WEAK_SURVIVED]),
         ("Compile error", [MUT_COMPILE, MUT_COMPILE]), ("Ignored", [MUT_IGNORED, MUT_IGNORED])],
        width=390, height=165)
    for old, new in zip(chart_svg.SERIES[:4], ("#059669", "#DC2626", "#64748B", "#94A3B8")):
        assert old in svg, old
        svg = svg.replace(old, new)
    return svg


def blocks():
    n_proj = n_projects()
    loc_lib = loc_dir(LIB)
    loc_cs_tests = loc_dir(TESTS, f"{L}/Shared")
    loc_vb_tests = loc_dir(VB_TESTS)
    loc_specs = loc_dir(f"{L}/L10.Pricing.Specs")
    loc_api = loc_dir(f"{L}/L10.QuoteApi", f"{L}/L10.QuoteApi.Tests")
    loc_weak = loc_dir(f"{L}/L10.Pricing.WeakTests")
    loc_total = loc_lib + loc_cs_tests + loc_vb_tests + loc_specs + loc_api + loc_weak
    n_cases = sum(n for _, n in CASES)
    n_hand = test_methods(TESTS, VB_TESTS, f"{L}/L10.QuoteApi.Tests", f"{L}/L10.Pricing.WeakTests")
    n_scen = feature_scenarios(f"{L}/L10.Pricing.Specs")
    n_methods = n_hand + n_scen
    test_loc = loc_cs_tests + loc_vb_tests + loc_specs + loc_weak + loc_dir(f"{L}/L10.QuoteApi.Tests")
    ratio = test_loc / loc_lib

    double_cards = [
        {"num": 1, "title": "Built-in Assert — start here", "tags": [T_CS], "pills": [SAME],
         "what": "xUnit's <code>Assert</code> class: equality, collections, exceptions, async.",
         "lines": [("You know", "JUnit's <code>Assertions</code> before AssertJ arrived"),
                   ("Strength", "<code>Assert.Equal</code> on a <code>record</code> compares by value, so "
                                "one call checks a whole object"),
                   ("Throws", "<code>Assert.Throws&lt;T&gt;</code> is exact-type by default — a subclass fails "
                              "the assertion (3.2 shows the message)"),
                   ("Licence", "Apache-2.0 with the framework, nothing to decide")]},
        {"num": 2, "title": "Fluent Assertions 8+ — a licence decision", "tags": [T_TOOLING], "pills": [TRAP],
         "what": "The AssertJ of .NET, and since version 8 a paid product for commercial use.",
         "lines": [("Changed", "v8 moved to the Xceed Community License; commercial users must buy a "
                               "per-seat annual subscription (" + FALICENCE + ")"),
                   ("v7", "Stays Apache-2.0 and gets fixes — pinning it is a supported answer"),
                   ("Do now", "Treat it like any other licence finding in the pipeline scan you already run"),
                   ("Watch", "It reads like an assertion style; it is a procurement item")]},
        {"num": 3, "title": "AwesomeAssertions · Shouldly", "tags": [T_TOOLING], "pills": [RENAMED],
         "what": "The community answers to that change, both free for commercial use.",
         "lines": [("Fork", "AwesomeAssertions is the community fork of Fluent Assertions 7, same API "
                            "(" + AWESOME + ")"),
                   ("Other", "Shouldly is an older, smaller alternative with a different style"),
                   ("Cost", "Swapping assertion library touches every test file — decide once, per repo"),
                   ("Sample", "This lesson uses built-in <code>Assert</code> only, so nothing to swap")]},
        {"num": 4, "title": "NSubstitute — the default mock", "tags": [T_CS], "pills": [RENAMED],
         "what": "<code>Substitute.For&lt;T&gt;()</code>, then call the member to arrange or assert.",
         "lines": [("Mockito", "<code>when(x.y()).thenReturn(z)</code> becomes "
                               "<code>x.Y().Returns(z)</code>"),
                   ("Verify", "<code>await repo.Received(1).SaveAsync(...)</code> replaces "
                              "<code>verify(repo, times(1))</code>"),
                   ("Matchers", "<code>Arg.Any&lt;T&gt;()</code> and <code>Arg.Is&lt;T&gt;(p =&gt; ...)</code>"),
                   ("Licence", "BSD-3-Clause, 6.2.0 · Aug 2026 (" + NSUBNUGET + ")")]},
        {"num": 5, "title": "Moq — read it, inherit it", "tags": [T_TOOLING], "pills": [DIFFERENT],
         "what": "The oldest and most common mocking library; you will meet it in existing code.",
         "lines": [("Shape", "<code>new Mock&lt;T&gt;()</code>, <code>.Setup(...)</code>, "
                             "<code>.Object</code>, <code>.Verify(...)</code>"),
                   ("History", "4.20.0 (8 Aug 2023) shipped SponsorLink, which scanned local git data; "
                               "4.20.2 removed it the next day (" + MOQLOG + ")"),
                   ("Today", "Fine technically; many teams moved anyway and never moved back"),
                   ("Advice", "Do not mix two mocking libraries in one repo")]},
        {"num": 6, "title": "Fakes and FakeTimeProvider", "tags": [T_ARCH], "pills": [SAME],
         "what": "A real implementation with a cheap backing store, and a clock you control.",
         "lines": [("Fake", "<code>InMemoryQuoteRepository</code> is used by the tests <i>and</i> by the API"),
                   ("Clock", "<code>FakeTimeProvider</code> ships in "
                             "<code>Microsoft.Extensions.TimeProvider.Testing</code> (" + FAKETIME + ")"),
                   ("Moves", "<code>Advance(TimeSpan)</code>, <code>SetUtcNow(...)</code>, "
                             "<code>AutoAdvanceAmount</code>"),
                   ("Prefer", "A fake for state, a substitute for interaction — 5.1 substitutes the "
                              "repository, and the API tests in §8 run against the real in-memory one")]},
    ]

    return [
        style_block(),
        {"type": "toc", "heading": "▤ Contents", "depth": 2,
         "note": "Page numbers are resolved from the rendered PDF. Code panels are cut from the compiled "
                 "samples; every score in sections 6 and 7 comes from a real run on the build machine."},
        {"type": "html", "html": LOCAL_CSS},

        # ═══════════════════════════ 1 · WHY ═══════════════════════════
        {"type": "story", "heading": "1 · Why this lesson — you already test; .NET changes the plumbing",
         "html": (
             "<p><b>This is the lesson where your existing standards transfer almost intact — and where one "
             "of them turns out to be weaker than you thought.</b> You run TDD, you hold 100% unit-test "
             "coverage as a delivery standard, you automate Postman collections per environment, you run k6 "
             "and you gate merges on SonarQube. None of that has to change. What changes is the plumbing: "
             ".NET has <i>two</i> test platforms under one framework choice, its coverage gate is written in "
             "MSBuild rather than a plugin block, and its most popular assertion library became a paid "
             "product for commercial use in 2025.</p>"
             "<p><b>The standard that needs upgrading is the coverage number itself.</b> This lesson ships two "
             "suites against the same library. Both reach <b>100% line and 100% branch coverage</b>, so both "
             "pass the same gate. One of them asserts real behaviour and kills "
             f"{STRONG_KILLED} of {MUT_TESTED} injected bugs ({STRONG_MUT}%); the other runs every line, "
             f"swallows exceptions and kills {WEAK_KILLED} ({WEAK_MUT}%). Both numbers are measured, in §7, "
             "from a real Stryker.NET run in this repository. After that, \"100% covered\" stops being the "
             "last line of a quality report.</p>"
             "<p><b>The vocabulary maps cleanly, so most of the work is translation.</b> "
             "<code>@Test</code> is <code>[Fact]</code>, <code>@ParameterizedTest</code> is "
             "<code>[Theory]</code>, Mockito is NSubstitute, MockMvc is "
             "<code>WebApplicationFactory</code>, JaCoCo is coverlet, PIT is Stryker.NET and Cucumber is "
             "Reqnroll. Where a name is the only difference this lesson gives it one row in the map (2.1) and "
             "moves on; the pages go to the four places where .NET behaves differently.</p>"
             f"<p><b>You will build {n_proj} projects around the MotorQuote rating rules.</b> One library under "
             f"test, a strong C# suite, a Visual Basic suite, a deliberately weak suite, two "
             "Microsoft.Testing.Platform twins for the mutation runs, Gherkin specifications, a minimal quote "
             "API and its in-memory tests. Premiums are illustrative, not a real tariff. " + ref(8) + " owns "
             "ASP.NET Core itself; " + ref(9) + " owns EF Core; this lesson owns how you test them.</p>")},

        {"type": "kpi", "heading": "1.1 · The numbers to leave this lesson with",
         "items": [
             {"label": "Coverage gate", "value": "100 / 100", "tone": "teal",
              "sub": "line + branch, fails dotnet test · measured"},
             {"label": "Mutation, strong suite", "value": f"{STRONG_MUT}%", "tone": "indigo",
              "sub": f"{STRONG_KILLED} of {MUT_TESTED} mutants killed · measured"},
             {"label": "Mutation, weak suite", "value": f"{WEAK_MUT}%", "tone": "red",
              "sub": "same 100% coverage · measured"},
             {"label": "xUnit v3", "value": "4.0.1", "tone": "violet",
              "sub": "12 Sep 2026 · verified"},
             {"label": "Lesson 10 tests", "value": str(n_cases), "tone": "navy",
              "sub": f"from {n_hand} methods + {n_scen} scenarios · measured"}]},

        legend(T_CS, T_TOOLING, T_ARCH),

        {"type": "callout", "variant": "info", "heading": "ℹ Before you start",
         "items": [
             "<b>You need records and interfaces from " + ref(3) + ", <code>async</code>/<code>await</code> and "
             "<code>TimeProvider</code> from " + ref(5) + ", project files and MSBuild properties from "
             + ref(7) + ", and the minimal API shape from " + ref(8) + ".</b> TDD, test doubles, the test "
             "pyramid and coverage discipline are assumed — this lesson explains their .NET form, never the "
             "ideas.",
             f"<b>You will build and run {n_proj} projects, all offline.</b> <code>L10.Pricing</code> is the "
             "library under test; <code>L10.Pricing.Tests</code> is the strong xUnit suite with the coverage "
             "gate; <code>L10.Pricing.VbTests</code> is the same rules tested from Visual Basic; "
             "<code>L10.Pricing.WeakTests</code> is the 100%-covered suite that asserts almost nothing; the "
             "two <code>.Mtp</code> projects are the same test files built as Microsoft.Testing.Platform "
             "executables so Stryker.NET can run them; <code>L10.Pricing.Specs</code> holds the Gherkin; "
             "<code>L10.QuoteApi</code> and its tests exercise the API in memory. Nothing opens a port, and "
             "nothing needs Docker.",
             "<b>Mutation testing needs one extra tool:</b> <code>dotnet tool restore</code> inside the "
             "samples folder installs <code>dotnet-stryker</code> 5.0.0 from "
             "<code>dotnet-tools.json</code>. Without it every other command in 9.1 still works.",
             "<b>Chips:</b> " + SAME + " transfers as-is, " + RENAMED + " is the same idea under another name, "
             + DIFFERENT + " behaves differently, " + TRAP + " looks the same and bites. Version, support and "
             "licensing facts are " + VERIFIED + " with a link and were checked on "
             + BUILD_DATE.isoformat() + "; numbers computed from this repository or captured from a real run "
             "are " + MEASURED + "; judgements are " + ESTIMATE + ". The Java panel in 2.4 is for comparison "
             "and is not compiled."]},

        # ═══════════════════════════ 2 · FRAMEWORKS AND PLATFORMS ═══════════════════════════
        {"type": "story", "heading": "2 · The frameworks — and the platform underneath them",
         "html": (
             "<p><b>Choosing between xUnit, NUnit and MSTest is the small decision; choosing the test "
             "platform under them is the one that changes your build.</b> A test <i>framework</i> defines the "
             "model you write against. A test <i>platform</i> discovers and runs the tests, integrates with "
             "the IDE and the CLI, and owns the extension points — and .NET has two of them: the long-lived "
             "<b>VSTest</b>, and <b>Microsoft.Testing.Platform</b> (MTP), which makes a test project a plain "
             "executable. Microsoft's own guidance is to pick one per repository and configure everything "
             "consistently, because mixing VSTest-based and MTP-based projects in one solution is not a "
             "supported scenario (" + PLATFORMS + ").</p>"
             "<p><b>xUnit v3 is where that shift is most visible: a test project is an <code>Exe</code>, not a "
             "library.</b> v3 test projects are stand-alone executables, so <code>dotnet run</code> runs the "
             "tests directly (" + XUNITMIG + "). The NuGet package you reference chooses the platform: "
             "<code>xunit.v3</code> takes the release's default MTP version, while "
             "<code>xunit.v3.mtp-off</code> explicitly disables MTP support so the project runs under VSTest — "
             "package variants that arrived in v3 build 3.2.0 (" + XUNITMTP + "). Both suites in this lesson "
             "are built twice, once each way, from the same source files.</p>"
             "<p><b>On the .NET 10 SDK, <code>dotnet test</code> itself has two modes, and the old bridge "
             "between them is being retired.</b> VSTest mode is still the default. MTP mode is new in the "
             ".NET 10 SDK and is switched on in <code>global.json</code> with "
             "<code>{\"test\": {\"runner\": \"Microsoft.Testing.Platform\"}}</code>. The legacy path — running "
             "an MTP project under VSTest mode via the <code>TestingPlatformDotnetTestSupport</code> property "
             "— is documented as legacy and will be removed in MTP version 2 on the .NET 10 SDK "
             "(" + DOTNETTEST + ").</p>"
             "<p><b>All three frameworks are alive and shipping; the differences that matter are behavioural, "
             "not syntactic.</b> xUnit v3 4.0.1 (12 Sep 2026), MSTest 4.4.1 (16 Sep 2026) and NUnit 4.6.1 "
             "(19 May 2026) are the current releases (" + XUNITNUGET + " · " + MSTESTNUGET + " · "
             + NUNITNUGET + "). Pick xUnit for new work if you have no reason not to — it is the template "
             "default and the one the ecosystem samples use. The difference that silently breaks an "
             "inherited suite is the test-class lifecycle: xUnit and MSTest build a new instance per test, "
             "matching JUnit 5's default, while NUnit shares one instance across a whole fixture "
             "(" + MSTESTLIFE + " · " + NUNITLIFE + ") — table 4.3 has the rest.</p>")},

        mapping("2.1 · Concept map — your test stack in .NET names", [
            ("JUnit 5 + the Gradle <code>test</code> task", "xUnit v3 / NUnit / MSTest + <code>dotnet test</code>",
             "renamed", "The platform under the framework is a second, bigger choice (2.2)"),
            ("<code>@Test</code>", "<code>[Fact]</code>", "renamed",
             "A fact takes no arguments; anything data-driven is a <code>[Theory]</code>"),
            ("<code>@ParameterizedTest</code> + <code>@MethodSource</code>",
             "<code>[Theory]</code> + <code>[MemberData]</code> over <code>TheoryData&lt;T&gt;</code>", "renamed",
             "<code>TheoryData&lt;T&gt;</code> is type-checked; a raw <code>object[]</code> source is not"),
            ("<code>@BeforeEach</code>", "the test class constructor", "different",
             "xUnit builds a new instance per test case; NUnit shares one (4.3)"),
            ("Mockito <code>mock()</code> / <code>verify()</code>",
             "NSubstitute <code>Substitute.For&lt;T&gt;()</code> / <code>Received()</code>", "renamed",
             "No <code>when(...).thenReturn(...)</code> — you call the member and assign <code>.Returns()</code>"),
            ("A hand-written fake", "the same — a real in-memory implementation", "same",
             "<code>InMemoryQuoteRepository</code> serves the tests and the API"),
            ("A <code>Clock</code> / <code>InstantSource</code> you inject", "<code>TimeProvider</code> in the BCL",
             "renamed", "<code>FakeTimeProvider</code> is the test double — " + ref(5)),
            ("MockMvc · <code>WebTestClient</code>", "<code>WebApplicationFactory&lt;Program&gt;</code>", "same",
             "In-process over <code>TestServer</code>: no port, no socket (8.1)"),
            ("Postman collections per environment", "<code>.http</code> files in the project", "renamed",
             "Checked in beside the code; secrets come from user-secrets, not the file (8.5)"),
            ("Cucumber + Gherkin", "Reqnroll + the same Gherkin", "renamed",
             "SpecFlow reached end of life on 31 Dec 2024; Reqnroll is the community fork (8.4)"),
            ("JaCoCo <code>jacocoTestCoverageVerification</code>", "coverlet <code>Threshold</code> properties",
             "renamed", "The gate is MSBuild properties in a <code>.props</code> file (6.1)"),
            ("PIT mutation testing", "Stryker.NET", "same",
             "Same vocabulary: killed, survived, timeout, mutation score (§7)"),
            ("Testcontainers for Java", "Testcontainers for .NET", "same",
             "Still needs a Docker-compatible runtime, so this lesson does not use it"),
            ("AssertJ / Hamcrest", "built-in <code>Assert</code>, AwesomeAssertions or Shouldly", "trap",
             "Fluent Assertions 8+ needs a paid licence for commercial use (5.3)"),
            ("<code>@Disabled(\"reason\")</code>", "<code>[Fact(Skip = \"reason\")]</code>", "renamed",
             "The reason is the property value, so a skipped test names why"),
            ("A SonarQube quality gate on coverage", "the same, plus a mutation threshold", "same",
             "Coverage is the floor; §7 measures what it misses"),
        ]),

        {"type": "mermaid", "inline": True,
         "heading": "2.2 · Which platform, and what each command then does",
         "caption": "indigo = the decision · teal = Microsoft.Testing.Platform path · slate = VSTest path · "
                    "amber = the file or package that selects it · green = what you type",
         "code": ("flowchart LR\n"
                  '  Q{"New repo, or one<br/>suite at a time?"}:::q\n'
                  '  Q -- "greenfield" --> MTP["Microsoft.Testing.Platform<br/>test project is an .exe"]:::mtp\n'
                  '  Q -- "existing VSTest estate" --> VST["VSTest<br/>the long-standing default"]:::vst\n'
                  '  MTP --> PKG["xunit.v3<br/>UseMicrosoftTestingPlatformRunner"]:::cfg\n'
                  '  VST --> PKG2["xunit.v3.mtp-off +<br/>xunit.runner.visualstudio"]:::cfg\n'
                  '  PKG --> GJ["global.json<br/>test.runner = Microsoft.Testing.Platform"]:::cfg\n'
                  '  GJ --> RUN["dotnet test (MTP mode)<br/>or dotnet run"]:::cmd\n'
                  '  PKG --> CMTP["coverage: coverlet.MTP<br/>or Microsoft code coverage"]:::cfg\n'
                  '  PKG2 --> RUN2["dotnet test<br/>(VSTest mode, the default)"]:::cmd\n'
                  '  PKG2 --> CVST["coverage: coverlet.collector<br/>or coverlet.msbuild"]:::cfg\n'
                  "  classDef q fill:#c7d2fe,color:#1f2937,stroke:#6366f1;\n"
                  "  classDef mtp fill:#ccfbf1,color:#1f2937,stroke:#0d9488;\n"
                  "  classDef vst fill:#e2e8f0,color:#1f2937,stroke:#475569;\n"
                  "  classDef cfg fill:#fde68a,color:#1f2937,stroke:#d97706;\n"
                  "  classDef cmd fill:#bbf7d0,color:#1f2937,stroke:#16a34a;\n")},

        {"type": "table", "heading": "2.3 · Attribute map — one row per thing you write every day",
         "cols": ["JUnit 5", "xUnit v3", "NUnit 4", "MSTest 4"],
         "rows": [
             [nw("@Test"), nw("[Fact]"), nw("[Test]"), nw("[TestMethod]")],
             [nw("@ParameterizedTest") + " + " + nw("@ValueSource"), nw("[Theory]") + " + " + nw("[InlineData]"),
              nw("[TestCase]"), nw("[DataRow]")],
             [nw("@MethodSource"), nw("[MemberData]") + " over " + nw("TheoryData<T>"), nw("[TestCaseSource]"),
              nw("[DynamicData]")],
             [nw("@BeforeEach"), "the constructor", nw("[SetUp]"), nw("[TestInitialize]") + " or the constructor"],
             [nw("@AfterEach"), nw("IDisposable.Dispose") + " / " + nw("IAsyncDisposable"), nw("[TearDown]"),
              nw("[TestCleanup]") + " or " + nw("Dispose")],
             [nw("@BeforeAll"), nw("IClassFixture<T>") + " (constructor-injected)", nw("[OneTimeSetUp]"),
              nw("[ClassInitialize]")],
             [nw("@Disabled"), nw('[Fact(Skip = "…")]'), nw("[Ignore]"), nw("[Ignore]")],
             [nw("@Tag"), nw('[Trait("Category", "…")]'), nw("[Category]"), nw("[TestCategory]")]]},

        pcompare(from_text(JUNIT_THEORY, "java", file="not compiled — for comparison"),
                 from_sample(NCB_TESTS, "theory"),
                 "2.4 · The same parameterised test in JUnit 5 and xUnit v3",
                 "<b>Same idea, two smaller pieces of ceremony.</b> A <code>TheoryData&lt;int, decimal&gt;</code> "
                 "is typed, so a wrong column is a compile error rather than a cast failure at run time — the "
                 "<code>Stream&lt;Arguments&gt;</code> on the left is not. The parameter names in the test "
                 "method must match the data order, not any annotation. And note the money type: "
                 "<code>decimal</code> compares with <code>==</code> and with <code>Assert.Equal</code>, so "
                 "there is no <code>isEqualByComparingTo</code> to remember — " + ref(2) + " explains why "
                 "<code>decimal</code> and not <code>double</code>."),

        pcode(from_sample(TEST_CSPROJ),
              "2.5 · The strong suite's project file — VSTest, with the gate imported",
              "<b>Four lines decide the platform and the tooling.</b> <code>OutputType Exe</code> is required "
              "by xUnit v3; <code>xunit.v3.mtp-off</code> plus <code>xunit.runner.visualstudio</code> put the "
              "project on VSTest, which is what lets <code>coverlet.msbuild</code> in "
              "<code>../CoverageGate.props</code> measure and gate it (6.1). The "
              "<code>&lt;Compile Include&gt;</code> line links one shared test-data builder without a project "
              "reference, so the builder never counts as production code. The twin project "
              "<code>L10.Pricing.Tests.Mtp</code> compiles the same <code>.cs</code> files with "
              "<code>xunit.v3</code> and <code>UseMicrosoftTestingPlatformRunner</code> instead — and running "
              "<code>dotnet test</code> on that twin fails immediately with <i>\"Testing with VSTest target is "
              "no longer supported by Microsoft.Testing.Platform on .NET 10 SDK and later\"</i>, which is "
              "exactly the retirement the .NET 10 docs describe. Run it with <code>dotnet run</code> (9.1)."),

        pcompare(from_sample(NCB_TESTS, "theory"), from_sample(VB_NCB, "vb-theory"),
                 "2.6 · The same theory in Visual Basic — and the project file behind it",
                 "<b>The VB test is the same xUnit v3 test with different punctuation.</b> "
                 "<code>TheoryData(Of Integer, Decimal) From { ... }</code> is the collection initialiser, "
                 "<code>&lt;Theory&gt;</code> and <code>&lt;MemberData&gt;</code> use angle brackets, "
                 "<code>Sub</code> is a <code>void</code> method, <code>Dim</code> is <code>var</code>, and a "
                 "decimal literal ends in <code>D</code> where C# uses <code>m</code>. The assertion, the "
                 "data and the test name are identical, and the VB project runs its 8 cases "
                 "(this theory's six rows, the throws test and the expiry test in 5.2) under the same "
                 "<code>dotnet test</code>. The one place a VB estate has to get something right is the "
                 "project file: <code>L10.Pricing.VbTests.vbproj</code> sets <code>OutputType</code> to "
                 "<code>Exe</code>, which xUnit v3 requires, and references <code>xunit.v3.mtp-off</code> "
                 "plus <code>xunit.runner.visualstudio</code> — the same choices as 2.5, with each file "
                 "saying <code>Imports Xunit</code> where the C# project uses a global using. " + ref(6)
                 + " owns VB itself."),

        # ═══════════════════════════ 3 · TDD ═══════════════════════════
        {"type": "story", "heading": "3 · TDD on the no-claim-bonus rule — red, green, refactor",
         "html": (
             "<p><b>The loop is the one you already run; what is worth watching is how much of the design C# "
             "hands you for free.</b> The rule: a driver with no claims earns a discount that grows with "
             "claim-free years, capped at five years and beyond. Start with the failing test for the "
             "zero-years case, write the smallest switch expression that passes, then let the theory table "
             "drive the rest of the curve. Illustrative rates, not a real tariff.</p>"
             "<p><b>Red first, and read the failure message — it is part of the test.</b> The stub throws "
             "<code>NotImplementedException</code>, so every case fails for the same reason, and the "
             "exception-shape test fails with a message that names both types. That message is why "
             "<code>Assert.Throws&lt;T&gt;</code> matching the exact type is a feature rather than a nuisance: "
             "a test that accepts a subclass would have passed against the stub.</p>"
             "<p><b>Green is a switch expression over patterns, and it is the whole implementation.</b> "
             "Relational and constant patterns cover the guard clause, the five steps and the cap in twelve "
             "lines. The catch-all arm is what makes every input handled: without it the compiler flags the "
             "switch expression as not exhaustive (warning CS8509, an error in these samples because "
             "warnings are errors) — " + ref(2) + " owns pattern matching. The refactor step then has nothing to do, which is the honest outcome for a rule this "
             "small; the interesting refactor in this lesson happens in §7, when a mutation run shows that one "
             "boundary was never really tested.</p>"
             "<p><b>Name tests as sentences, not as identifiers.</b> <code>Negative_years_are_rejected</code> "
             "reads out of a CI log without the reader opening the file. That is the .NET convention you will "
             "see in the framework's own repositories, and it is the one the samples in this track follow. "
             "Reach for <code>[Fact(DisplayName = \"…\")]</code> only when the sentence will not fit in an "
             "identifier.</p>")},

        pcode(from_sample(NCB_TESTS, "first-test"),
              "3.1 · Red — the first test, before the rule exists",
              "<b>Three lines and one named argument.</b> <code>claimFreeYears: 0</code> is a named argument, "
              "not a comment, so the test states which input is zero — the discount, the years and the cap are "
              "all numbers and confusing them is the easiest bug in a rating rule. xUnit's "
              "<code>Assert.Equal(0.00m, discount)</code> compares <code>decimal</code> values exactly; "
              "nothing here needs a delta or a comparator."),

        pcode(captured(RED_OUTPUT, "Terminal — the red phase"),
              "3.2 · What red looks like, and why the exact-type assertion matters",
              "<b>Eight cases fail: one fact, six theory rows and the exception test.</b> The last failure is "
              "the one to read — <i>\"Exception type was not an exact match\"</i>. "
              "<code>Assert.Throws&lt;ArgumentOutOfRangeException&gt;</code> rejects the "
              "<code>NotImplementedException</code> that the stub throws, and it would equally reject a "
              "<code>ArgumentException</code> base-class throw once the rule is written. If you want the "
              "assertion to accept subclasses you have to say so with "
              "<code>Assert.ThrowsAny&lt;T&gt;</code>. " + MEASURED + " on the build machine from a stub copy "
              "of the library."),

        pcode(from_sample(NCB, "ncb-rule"),
              "3.3 · Green — the rule as a switch expression over patterns",
              "<b>The guard clause, the curve and the cap in one expression.</b> <code>&lt; 0</code> is a "
              "relational pattern and <code>_</code> is the catch-all that implements \"five years and "
              "beyond\", so the method has no <code>if</code> and no fall-through. Every arm is a value, which "
              "is why the whole method is an expression-bodied member. Two consequences for testing: the "
              "<code>_</code> arm means no input can reach an unhandled case, and every arm is a branch, so "
              "coverlet counts one branch per arm plus the implicit no-match path — 8 for these 7 arms. The "
              "theory table in 2.4 walks five of the seven arms; the zero-years fact in 3.1 and the "
              "negative-years test in 3.2 cover the other two, and all three are needed to reach 100% "
              "branch."),

        {"type": "table", "heading": "3.4 · The rating sheet the theory asserts — worked by hand first",
         "cols": ["Scenario", "Sum insured · class", "Loading", "No-claim bonus", "Total, THB"],
         "rows": [
             ["Standard — 36, 10 claim-free years", "600,000 · Class 1", "none", "50%", "<b>6,445.68</b>"],
             ["Young — 23, one claim, 3 licence years", "600,000 · Class 1", "+20% age, +10% claim", "none",
              "<b>16,759.41</b>"],
             ["Commercial — 45, four claims", "400,000 · Class 3", "+30% claims (capped), +25% use", "none",
              "<b>3,330.91</b>"],
             ["Boundary — turns 25 on the start date", "600,000 · Class 1", "none — 25 is not under 25", "50%",
              "<b>6,445.68</b>"]]},
        tnote("<b>Every total is net premium + 0.4% stamp duty, rounded up to the baht, + 7% VAT on the sum "
              "of the two.</b> The premiums are illustrative, not a real tariff — what matters is that each "
              "one was worked out from the sheet <i>before</i> the code existed. The fourth row was added "
              "later, <i>after</i> the mutation run in §7 showed that changing <code>&lt; 25</code> to "
              "<code>&lt;= 25</code> broke nothing any test could see."),

        # ═══════════════════════════ 4 · FIXTURES AND ISOLATION ═══════════════════════════
        {"type": "story", "heading": "4 · Fixtures and isolation — the constructor is your @BeforeEach",
         "html": (
             "<p><b>xUnit has no setup attribute because it does not need one: it builds a new instance of the "
             "test class for every test case, so the constructor <i>is</i> <code>@BeforeEach</code> and "
             "<code>readonly</code> fields <i>are</i> your fixture.</b> Teardown is "
             "<code>IDisposable.Dispose</code> or <code>IAsyncDisposable.DisposeAsync</code> on the same "
             "class. Nothing can leak from one test into the next through an instance field, which removes a "
             "whole class of order-dependent failures before you write any code.</p>"
             "<p><b>That default is not universal, and the exception is the trap.</b> NUnit creates one "
             "instance and shares it with every test in the fixture unless the class is marked "
             "<code>[FixtureLifeCycle(LifeCycle.InstancePerTestCase)]</code> (" + NUNITLIFE + "). A JUnit or "
             "xUnit engineer reading an NUnit suite will assume isolation that is not there; a mutable field "
             "set in one test is visible in the next, and the suite passes or fails depending on execution "
             "order. MSTest, like xUnit and JUnit 5, creates a fresh instance per test (" + MSTESTLIFE + ").</p>"
             "<p><b>Shared expensive setup is opt-in, and it is injected rather than inherited.</b> "
             "<code>IClassFixture&lt;T&gt;</code> builds one <code>T</code> for the whole test class and hands "
             "it to the constructor — that is how 8.2 gets one "
             "<code>WebApplicationFactory&lt;Program&gt;</code> for three API tests instead of booting the app "
             "three times. It is <code>@BeforeAll</code> without a static field, so each class gets its own "
             "copy even when classes run in parallel (next paragraph). One level up, the assembly-level "
             "attribute <code>[assembly: AssemblyFixture(typeof(T))]</code> does the same job for a whole "
             "assembly — still constructor-injected, but with no interface on the test class (" + SHAREDCTX
             + "); NUnit's <code>[SetUpFixture]</code> and MSTest's <code>[AssemblyInitialize]</code> are "
             "the equivalents.</p>"
             "<p><b>xUnit runs test <i>classes</i> in parallel by default, and the constructor does not "
             "protect you from that.</b> Tests inside one class run one after another, each on its own "
             "instance; two classes run at the same time, because each class is its own test collection by "
             "default (" + PARALLEL + "). Instance fields are safe. A <code>static</code> field, a file in "
             "the temp folder, an environment variable or a fixed port is shared by every class running at "
             "that moment, and JUnit 5 runs sequentially unless you configure it, so a suite that got away "
             "with those will flake here. Put the classes that share a resource in one "
             "<code>[Collection]</code> — they then run one after another — and share the expensive object "
             "with an <code>ICollectionFixture&lt;T&gt;</code>.</p>"
             "<p><b>One xUnit v3 habit to adopt on day one: pass the cancellation token.</b> The analyzer "
             "xUnit1051 warns whenever you call a method that accepts a "
             "<code>CancellationToken</code> without giving it one, and the token to give it is "
             "<code>TestContext.Current.CancellationToken</code> so that a timed-out test cancels its work "
             "instead of leaking it (" + XUNIT1051 + "). With warnings-as-errors on, as in every sample here, "
             "that warning is a build failure — which is why every asynchronous test in this lesson starts by "
             "capturing <code>ct</code>.</p>")},

        pcode(from_sample(QS_TESTS, "fixture"),
              "4.1 · The fixture is three readonly fields and a constructor",
              "<b>No attributes, no base class, no field mutation.</b> Each test case gets a fresh "
              "<code>FakeTimeProvider</code> pinned to 09:00, a fresh NSubstitute double and a fresh "
              "<code>QuoteService</code>, so a test that advances the clock cannot affect any other. "
              "<code>Nine</code> is <code>static readonly</code> because it is a constant, not state. The "
              "comment in the sample says what the shape means; the equivalent NUnit class would need "
              "<code>[SetUp]</code> and — to get the same isolation — "
              "<code>[FixtureLifeCycle(LifeCycle.InstancePerTestCase)]</code>."),

        {"type": "mermaid", "inline": True,
         "heading": "4.2 · What the runner does for every single test case",
         "caption": "one construction, one test, one optional disposal — then the whole cycle repeats for the "
                    "next case, with a brand-new instance",
         "code": ('%%{init: {"themeVariables": {"fontSize": "11px", "actorBkg": "#c7d2fe",'
                  '"actorTextColor": "#1f2937", "noteBkgColor": "#fde68a", "noteTextColor": "#1f2937"}}}%%\n'
                  "sequenceDiagram\n"
                  "  autonumber\n"
                  "  participant R as xUnit v3 runner\n"
                  "  participant T as QuoteServiceTests\n"
                  "  participant C as FakeTimeProvider\n"
                  "  R->>T: new QuoteServiceTests()\n"
                  "  Note over T: field initialisers, then the<br/>constructor = @BeforeEach\n"
                  "  T->>C: new FakeTimeProvider(09:00)\n"
                  "  R->>T: Create_saves_a_quote_valid_for_30_days(ct)\n"
                  "  T-->>R: passed\n"
                  "  R->>T: DisposeAsync, if implemented\n"
                  "  Note over R: nothing is reused:<br/>the next case starts over\n"
                  "  R->>T: new QuoteServiceTests()\n"
                  "  R->>T: Accepting_after_30_days_expires_the_quote(ct)\n"
                  "  T->>C: Advance(30 days + 1 tick)\n"
                  "  T-->>R: passed\n")},

        {"type": "table", "heading": "4.3 · Isolation by framework — the row that breaks inherited suites",
         "cols": ["Framework", "Instance per test case?", "Per-test setup", "Watch for"],
         "rows": [
             ["<b>xUnit v3</b>", pill("Yes — always", "green"), "the constructor",
              "There is no setup attribute to look for; read the constructor"],
             ["<b>MSTest 4</b>", pill("Yes", "green"), nw("[TestInitialize]") + " or the constructor",
              "Constructor first, then <code>[TestInitialize]</code> (" + MSTESTLIFE + ")"],
             ["<b>NUnit 4</b>", pill("No — one shared instance", "red"), nw("[SetUp]"),
              "Add <code>[FixtureLifeCycle(LifeCycle.InstancePerTestCase)]</code> or keep every field "
              "immutable (" + NUNITLIFE + ")"],
             ["<b>JUnit 5</b>", pill("Yes — PER_METHOD", "green"), nw("@BeforeEach"),
              "The habit you already have; xUnit and MSTest match it, NUnit does not"]]},

        # ═══════════════════════════ 5 · DOUBLES AND ASSERTIONS ═══════════════════════════
        {"type": "story", "heading": "5 · Assertions and test doubles — one licence decision, two habits",
         "html": (
             "<p><b>Start with the assertions the framework ships, because the fluent library you would reach "
             "for by reflex is now a procurement question.</b> Fluent Assertions — the AssertJ of .NET — moved "
             "to the Xceed Community License at version 8: commercial users must buy a per-seat annual "
             "subscription, while version 7 stays Apache-2.0 and keeps receiving fixes (" + FALICENCE + "). "
             "Pinning v7, adopting the community fork AwesomeAssertions or writing built-in "
             "<code>Assert</code> calls are all defensible; adding a paid dependency to every test file by "
             "accident is not. Put it in the licence scan your pipelines already run.</p>"
             "<p><b>For test doubles, .NET's default answer is NSubstitute, and the reason is partly "
             "historical.</b> Moq is older and more widespread, but version 4.20.0 shipped SponsorLink, which "
             "scanned local git data, and it was removed the next day in 4.20.2 (" + MOQLOG + "). The "
             "episode moved a lot of teams to NSubstitute, whose API is also closer to what you want: you call "
             "the member and assign a return value, instead of wrapping it in a <code>when(...)</code>.</p>"
             "<p><b>Prefer a fake for state and a substitute for interaction.</b> When a test asks \"was it "
             "saved?\", a substitute with <code>Received(1)</code> answers exactly that. When a test asks "
             "\"what happens after it is saved?\", a real in-memory implementation is simpler, faster to read "
             "and impossible to over-specify — and it doubles as the API's own repository until " + ref(9) + " "
             "replaces it with EF Core. Over-mocked tests fail on a rename; state-based ones fail on a "
             "behaviour change.</p>"
             "<p><b>Never read the clock in production code: take a <code>TimeProvider</code>.</b> It is in "
             "the base class library, so it needs no abstraction of your own, and "
             "<code>FakeTimeProvider</code> from <code>Microsoft.Extensions.TimeProvider.Testing</code> lets a "
             "test move time by an exact <code>TimeSpan</code> (" + FAKETIME + "). That is how 5.2 tests a "
             "30-day expiry in a millisecond, in both languages — " + ref(5) + " owns "
             "<code>TimeProvider</code> itself.</p>")},

        pcode(from_sample(QS_TESTS, "nsubstitute"),
              "5.1 · An interaction test — NSubstitute instead of Mockito",
              "<b>Two assertions of two different kinds.</b> <code>Assert.Equal</code> checks the value the "
              "service returned; <code>Received(1)</code> checks that it saved exactly once, with a "
              "<code>Quoted</code> quote and the same cancellation token. "
              "<code>Arg.Is&lt;Quote&gt;(q =&gt; ...)</code> is Mockito's <code>argThat</code>. Note the "
              "<code>await</code> before <code>_repo.Received(1)</code>: verifying an async member is itself "
              "awaited, and forgetting it is the commonest NSubstitute mistake."),

        pcompare(from_sample(QS_TESTS, "fake-time"), from_sample(VB_QS, "vb-fake-time"),
                 "5.2 · Testing a 30-day expiry in C# and in Visual Basic",
                 "<b>The same test, the same libraries, one runtime.</b> Both advance the fake clock by "
                 "exactly the validity window and then by a single tick, so the assertion proves the boundary "
                 "is exclusive rather than approximately right — a real clock could never test this. The VB "
                 "side shows what a VB test project costs you: <code>Async Function ... As Task</code> instead "
                 "of <code>async Task</code> and <code>Dim ... As New</code> instead of target-typed "
                 "<code>new</code>, but the same <code>&lt;Fact&gt;</code> attribute, the same "
                 "<code>Substitute.For(Of T)()</code> and the same <code>Assert.Equal</code>. A legacy VB "
                 "estate can be brought under test without a rewrite first — " + ref(6) + ".",
                 keep=False),

        {"type": "cards",
         "band": {"title": "5.3 · Assertions and doubles — what to adopt, what to inherit",
                  "note": "library view", "tone": "violet"},
         "cards": double_cards[:3]},
        {"type": "cards", "toc": False,
         "band": {"title": "5.3 · Assertions and doubles (continued)", "note": "library view",
                  "tone": "violet"},
         "cards": double_cards[3:]},

        # ═══════════════════════════ 6 · COVERAGE GATE ═══════════════════════════
        {"type": "story", "heading": "6 · Coverage as a gate — 100% line and branch, failing the build",
         "html": (
             "<p><b>In .NET the coverage gate is MSBuild properties, not a plugin block, and that is good "
             "news: it lives in one <code>.props</code> file that every test project imports.</b> coverlet is "
             "the de-facto tool. <code>Threshold</code>, <code>ThresholdType</code> and "
             "<code>ThresholdStat</code> make <code>dotnet test</code> itself fail below the bar, so the gate "
             "runs on a developer's machine and in CI with no extra step and nothing to configure twice "
             "(" + COVERLET + ").</p>"
             "<p><b>Gate both line and branch, because line coverage alone is satisfied by walking through a "
             "condition without ever taking the other side of it.</b> 6.2 deletes exactly one test — the one "
             f"that passes an undefined enum value — and coverage falls to {CUT_LINE}% line and {CUT_BRANCH}% "
             "branch. Every remaining test passes, and the command still fails. That is the behaviour you "
             "want: a suite cannot quietly shrink.</p>"
             "<p><b>Excluding code from the measurement is a discipline, not a convenience.</b> "
             "<code>[ExcludeFromCodeCoverage]</code> applies to an assembly, class, struct, constructor, "
             "method, property or event, and it carries a <code>Justification</code> property — use it, "
             "because an unexplained exclusion is how a 100% gate becomes decoration (" + EXCLUDE + "). The "
             "honest targets are generated code and thin composition roots; a hand-written branch you cannot "
             "reach is a design problem, not a coverage problem.</p>"
             "<p><b>One migration trap deserves its own sentence: your coverage driver depends on the "
             "platform you chose in §2.</b> coverlet's own documentation states that "
             "<code>coverlet.collector</code> and <code>coverlet.msbuild</code> cannot be used with "
             "Microsoft.Testing.Platform, because both rely on VSTest infrastructure; the MTP driver is "
             "<code>coverlet.MTP</code> (" + COVMTP + "), and Microsoft ships its own code-coverage extension "
             "for MTP as well (" + MSCOV + "). Move a suite to MTP without changing the driver and the gate "
             "does not fail — it simply stops existing.</p>")},

        pcode(from_sample(GATE),
              "6.1 · The gate — one .props file every test project imports",
              "<b>Seven properties are the whole policy.</b> <code>Include=[L10.Pricing]*</code> measures the "
              "library under test and nothing else, so test-support code cannot inflate the number; "
              "<code>Threshold 100</code> with <code>ThresholdType line,branch</code> fails the command below "
              "either bar; <code>ThresholdStat total</code> applies it to the whole module rather than "
              "per-file. Cobertura is the output format because every report tool reads it — "
              "ReportGenerator turns it into browsable HTML and a badge (" + REPORTGEN + "). Importing this "
              "file rather than repeating the properties is the " + ref(7) + " pattern: one place to raise "
              "the bar for every suite."),

        pcode(captured(GATE_OUTPUT, "Terminal — the gate doing its job"),
              "6.2 · One test deleted, all tests green, build red",
              f"<b>{CUT_LINE}% line and {CUT_BRANCH}% branch — and <code>dotnet test</code> fails.</b> The "
              "deleted test was the one that passes <code>(CoverageClass)99</code>, so the "
              "<code>_ =&gt; throw</code> arm of <code>BaseRate</code> is never reached: one line and one "
              "branch. Branch coverage falls further than line coverage because there are far fewer branch "
              "points than lines — 29 against 79 in that run — so one uncovered branch costs 3.45 points "
              "and one uncovered line 1.27, which is exactly why gating both is worth the extra property. "
              + MEASURED + " on the build machine from a scratch copy of the samples with that one test "
              "removed; the committed suite holds 100 / 100 / 100."),

        {"type": "chart", "heading": "6.3 · What one deleted test costs the gate", "kind": "bar",
         "args": {"data": [("Line · full suite", 100.0), ("Branch · full suite", 100.0),
                           ("Line · one test gone", CUT_LINE), ("Branch · one test gone", CUT_BRANCH)],
                  "ylabel": "% of L10.Pricing", "tone": "teal", "width": 560, "height": 210},
         "caption": "coverlet totals for the L10.Pricing module · the configured threshold is 100 for both "
                    "line and branch · measured from two real runs on the build machine",
         "note": "<b>The gap looks tiny and that is the point: a threshold of 100 turns a 1.27-point drop "
                 f"into a build failure.</b> A gate at 95% would have accepted {CUT_LINE}% line and "
                 f"{CUT_BRANCH}% branch without a word. Read the two right-hand bars as the cost of one "
                 "deleted test in a library of " + str(loc_lib) + " lines — then read §7, which shows that "
                 "the bars being back at 100 still does not mean the code is tested. " + MEASURED},

        {"type": "table", "heading": "6.4 · Coverage tooling — pick by platform first",
         "cols": ["Tool", "Platform", "Output", "Use it for"],
         "rows": [
             [nw("coverlet.msbuild"), pill("VSTest only", "amber"), "cobertura, opencover, json, lcov",
              "<b>The gate in this lesson</b> — thresholds that fail <code>dotnet test</code>"],
             [nw("coverlet.collector"), pill("VSTest only", "amber"), "same formats",
              "The template default; collects coverage but is driven by run settings"],
             [nw("coverlet.MTP"), pill("MTP", "teal"), "json + cobertura by default",
              "The MTP driver — what you move to when you leave VSTest (" + COVMTP + ")"],
             [nw("coverlet.console"), pill("Either", "slate"), "same formats",
              "A global tool for one-off runs and non-<code>dotnet test</code> harnesses"],
             ["Microsoft code coverage extension", pill("MTP", "teal"), "coverage (default), xml, cobertura",
              "Microsoft's own MTP coverage extension; pass <code>--coverage-output-format cobertura</code> "
              "if a report tool has to read it (" + MSCOV + ")"],
             ["ReportGenerator", pill("Either", "slate"), "HTML, badges, summaries",
              "Turning a cobertura file into something a human or a PR comment can read (" + REPORTGEN + ")"]]},

        # ═══════════════════════════ 7 · MUTATION TESTING ═══════════════════════════
        {"type": "story", "heading": "7 · Beyond coverage — what the mutation score tells you",
         "html": (
             "<p><b>100% coverage says every line ran. It does not say that anything was checked — and this "
             "lesson ships the proof as a compiling project.</b> <code>L10.Pricing.WeakTests</code> has two "
             "test methods. It loops over every input, swallows the exceptions with a "
             "<code>try/catch</code>, calls <code>Assert.NotNull</code> twice and asserts nothing else. It "
             "reaches <b>100% line and 100% branch coverage</b> and it passes the same gate as the strong "
             f"suite's {sum(n for lbl, n in CASES if lbl == 'C# unit tests')} cases.</p>"
             "<p><b>Mutation testing is the measurement that separates them.</b> Stryker.NET rewrites your "
             "production code one small change at a time — a comparison flipped, an operator swapped, a "
             "statement removed, a string emptied — and runs the tests against each mutant. A mutant that "
             "makes a test fail is <i>killed</i>; one that leaves every test passing <i>survived</i>, and it "
             "is a bug your suite would not catch. The score is <code>detected / valid × 100</code> "
             "(" + MUTSTATES + " · " + STRYKER + "). This is PIT, with the same vocabulary.</p>"
             f"<p><b>The measured result: {STRONG_MUT}% against {WEAK_MUT}%, from identical coverage.</b> Of "
             f"{MUT_TESTED} tested mutants the strong suite kills {STRONG_KILLED} and the weak suite kills "
             f"{WEAK_KILLED}. The weak suite's survivors are not exotic: <code>&lt; 25</code> becomes "
             "<code>&gt; 25</code>, <code>loading += 0.20m</code> becomes <code>-=</code>, "
             "<code>Math.Min</code> becomes <code>Math.Max</code>, a whole statement disappears. Every one of "
             "those would ship a wrong premium, and every one is invisible to a coverage report.</p>"
             f"<p><b>Read your survivors before you chase the number.</b> All {STRONG_SURVIVED} survivors in "
             "the strong suite are string mutations inside exception messages — the text of "
             "<code>\"cannot be negative\"</code>, of <code>\"unknown class\"</code> in "
             "<code>BaseRate</code> and of two interpolated <code>$\"quote {id} ...\"</code> "
             "messages. Nothing asserts on that text, and for internal exceptions nothing should. The useful "
             "response is to assert the message where a caller depends on it, exclude message mutations "
             "otherwise, and set the threshold below 100 on purpose — the configuration in 7.6 breaks the "
             "build under 80%, which the weak suite promptly does.</p>")},

        pcode(from_sample(WEAK, "weak"),
              "7.1 · The 100%-covered test that tests nothing",
              "<b>Every line of the rating rules runs, and only two assertions ever fire.</b> "
              "<code>Swallow</code> wraps each throwing call in a <code>try/catch</code>, so the guard clauses "
              "are <i>covered</i> without anyone checking which exception came out; the loop from "
              "<code>-1</code> to <code>5</code> walks every arm of the no-claim-bonus switch without checking "
              "a single discount. Do not copy this pattern — it exists so that 7.2 can put a number on it. If "
              "a suite you inherit is full of <code>Assert.NotNull</code> and empty catch blocks, you are "
              "looking at this."),

        {"type": "chartrow", "charts": [
            {"heading": "7.2 · Same coverage, different suites", "svg": suites_svg(),
             "caption": "coverlet totals and Stryker.NET scores for the same library · measured from real runs "
                        "on the build machine",
             "note": "<b>The first two pairs are identical; the third is a "
                     f"{STRONG_MUT - WEAK_MUT:.2f}-point gap.</b> A gate that reads only the first two bars "
                     "calls both suites finished. " + MEASURED},
            {"heading": "7.3 · Where the mutants went", "svg": mutant_states_svg(),
             "caption": "one Stryker.NET run per suite over the same generated mutants · green = detected, "
                        "red = counted against you, slate = excluded from the score, as in 7.4",
             "note": f"<b>{MUT_TESTED} mutants are scored; {MUT_COMPILE + MUT_IGNORED} are not.</b> A mutant "
                     "that does not compile and one filtered out as already-covered are both excluded from "
                     "<code>detected / valid</code>, which is why the denominator is "
                     f"{MUT_TESTED} and not {MUT_TESTED + MUT_COMPILE + MUT_IGNORED} (" + MUTSTATES + "). "
                     + MEASURED}]},

        {"type": "mermaid", "inline": True,
         "heading": "7.4 · The life of one mutant",
         "caption": "green = counted as detected · red = counted against you · slate = excluded from the "
                    "score entirely · lavender = still in flight · the score is detected / valid",
         "code": ('%%{init: {"themeVariables": {"fontSize": "11px"}}}%%\n'
                  "stateDiagram-v2\n"
                  "  direction LR\n"
                  "  [*] --> Generated\n"
                  "  Generated --> CompileError: does not compile\n"
                  "  Generated --> Ignored: filtered out by config\n"
                  "  Generated --> NoCoverage: no test runs that line\n"
                  "  Generated --> Tested: a test runs that line\n"
                  "  Tested --> Killed: at least one test failed\n"
                  "  Tested --> Survived: every test still passed\n"
                  "  Tested --> Timeout: the tests hung\n"
                  "  classDef good fill:#bbf7d0,color:#1f2937,stroke:#16a34a\n"
                  "  classDef bad fill:#fecaca,color:#1f2937,stroke:#dc2626\n"
                  "  classDef out fill:#e2e8f0,color:#1f2937,stroke:#475569\n"
                  "  class Killed good\n"
                  "  class Timeout good\n"
                  "  class Survived bad\n"
                  "  class NoCoverage bad\n"
                  "  class CompileError out\n"
                  "  class Ignored out\n")},

        {"type": "table", "heading": "7.5 · Mutant states, and what the strong suite actually produced",
         "cols": ["State", "What it means", "In the score?", "Strong suite"],
         "rows": [
             ["<b>Killed</b>", "At least one test failed while the mutant was active",
              pill("detected", "green"), f"<b>{STRONG_KILLED}</b>"],
             ["<b>Survived</b>", "Every test passed — a bug your suite cannot see",
              pill("undetected", "red"), f"<b>{STRONG_SURVIVED}</b> — all of them exception-message strings"],
             ["<b>No coverage</b>", "No test reaches that line at all", pill("undetected", "red"),
              "<b>0</b> — the 100% gate guarantees this"],
             ["<b>Timeout</b>", "The run hung, for example an inverted loop condition",
              pill("detected", "green"), "<b>0</b>"],
             ["<b>Compile error</b>", "The mutated code does not build", pill("excluded", "slate"),
              f"<b>{MUT_COMPILE}</b>"],
             ["<b>Ignored</b>", "Filtered out — here, mutants inside a block already covered",
              pill("excluded", "slate"), f"<b>{MUT_IGNORED}</b>"]]},
        tnote("<b>Only the first four states are scored.</b> Definitions from " + MUTSTATES + "; the counts "
              "are " + MEASURED + " from the Stryker.NET JSON report of the run in 9.2."),

        pcode(from_sample(STRYKER_CFG),
              "7.6 · Thresholds that fail the build, next to the coverage ones",
              "<b><code>break: 80</code> is the line that makes this a gate rather than a report.</b> Below "
              "it Stryker exits non-zero — the weak suite's "
              f"{WEAK_MUT}% ends with <i>\"Final mutation score is below threshold break. Crashing...\"</i>. "
              "<code>high</code> and <code>low</code> only colour the HTML report. "
              "<code>test-runner: mtp</code> is why the <code>.Mtp</code> twin projects exist: Stryker drives "
              "the tests through Microsoft.Testing.Platform. <code>concurrency: 1</code> keeps the run "
              "deterministic on a laptop; raise it in CI. Stryker.NET's default coverage analysis runs only the "
              "tests that cover each mutant (" + STRYKERCFG + "), so a run is far cheaper than one suite "
              "execution per mutant — about ten seconds for each of the two runs here (" + MEASURED
              + ", one run each, concurrency 1, projects already built). The cost still grows with the "
              "library and the suite, so run it nightly or per pull request on changed projects rather than "
              "on every commit (" + ESTIMATE + " for that cadence)."),

        # ═══════════════════════════ 8 · INTEGRATION, API AND BDD ═══════════════════════════
        {"type": "story", "heading": "8 · Integration, API and BDD tests — in memory, with a clock you own",
         "html": (
             "<p><b><code>WebApplicationFactory&lt;Program&gt;</code> is MockMvc with the real pipeline: your "
             "whole application, hosted in the test process, reached through an "
             "<code>HttpClient</code> that never opens a socket.</b> The "
             "<code>Microsoft.AspNetCore.Mvc.Testing</code> package copies the app's dependency file, sets "
             "the content root to the application project and boots it on <code>TestServer</code>; "
             "<code>CreateClient()</code> hands you a client that follows redirects and keeps cookies "
             "(" + INTEGRATION + "). Middleware, model binding, routing, filters and JSON options all run — "
             "which is the point, because those are the layers a unit test cannot reach.</p>"
             "<p><b>On .NET 10 you no longer have to make <code>Program</code> public yourself.</b> Top-level "
             "statements compile to an <code>internal</code> <code>Program</code> class, which used to force "
             "either a hand-written <code>public partial class Program { }</code> or an "
             "<code>InternalsVisibleTo</code> attribute. ASP.NET Core now ships a source generator that emits "
             "that declaration for apps using top-level statements; it landed for the 10.0 release "
             "(" + PROGGEN + "). <code>L10.QuoteApi/Program.cs</code> contains no such class, and "
             "<code>WebApplicationFactory&lt;Program&gt;</code> in the test project compiles — "
             + MEASURED + " by the fact that the project builds with warnings as errors.</p>"
             "<p><b>The technique that makes in-memory API tests worth writing is replacing one service.</b> "
             "<code>WithWebHostBuilder</code> plus <code>ConfigureTestServices</code> re-registers a single "
             "dependency for one test — here a <code>FakeTimeProvider</code> in place of "
             "<code>TimeProvider.System</code> — so the test can create a quote, move the world 31 days "
             "forward and assert a 409. No database, no container, no sleep. Replace a partner client the same "
             "way to test a timeout path.</p>"
             "<p><b>Out-of-process tools stay in the toolbox, and BDD earns its keep only at the boundary.</b> "
             "<code>.http</code> files are checked-in request collections with variables and response "
             "chaining — the sample's third request reads the quote id out of the first response, which is "
             "what a Postman collection does minus the export step (" + HTTPFILES + "). Testcontainers "
             "gives you a real database in a throwaway container when an in-memory double would lie, at the "
             "cost of a Docker runtime (" + TESTCONTAINERS + "), and Playwright for .NET drives real "
             "browsers (" + PLAYWRIGHT + "). Gherkin earns its ceremony when a non-engineer reads or "
             "writes the examples, and is pure overhead when the only readers are its authors.</p>"
             "<p><b>Across an estate of services the pyramid keeps its shape and gains one boundary: the "
             "partner.</b> Each service keeps many fast unit tests and a handful of in-process API tests "
             "like the ones above, and cannot prove a partner it does not own from inside its own process. "
             "So test each outbound client against a stub of the boundary — a hand-written "
             "<code>HttpMessageHandler</code> that returns a canned body, a 503 or a delay (" + ref(8)
             + " owns <code>HttpClientFactory</code> and its resilience policies), or WireMock.Net when you "
             "want a real stub HTTP server inside the test (" + WIREMOCK + ") — and the retry, timeout and "
             "failure paths are proved without calling anyone. Where you can get the other side to verify it, "
             "a consumer-driven contract test such as Pact.Net pins the shape both ways (" + PACT + "); for a "
             "third-party partner you cannot ask, the stubbed boundary is the test you have. Browser and "
             "container layers stay few. This is a design judgement (" + ESTIMATE + "), not a measurement.</p>")},

        {"type": "mermaid", "inline": True,
         "heading": "8.1 · Where an in-memory API test actually runs",
         "caption": "one process, one boundary crossed · indigo = test code · teal = the application under "
                    "test, unmodified · amber = the one service the test replaces · slate = what is absent",
         "code": ("flowchart TB\n"
                  '  subgraph PROC["a single test process"]\n'
                  "    direction TB\n"
                  '    subgraph TC["your test code"]\n'
                  "      direction LR\n"
                  '      T["QuoteApiTests<br/>[Fact]"]:::test --> F["WebApplicationFactory<br/>of Program"]:::test\n'
                  '      F --> C["HttpClient over<br/>TestServer"]:::test\n'
                  "    end\n"
                  '    subgraph APP["the application, unmodified"]\n'
                  "      direction LR\n"
                  '      MW["middleware, routing,<br/>JSON options"]:::app --> EP["MapPost /quotes"]:::app\n'
                  '      EP --> SVC["QuoteService"]:::app\n'
                  "    end\n"
                  "    C --> MW\n"
                  '    SVC --> REPO["InMemoryQuoteRepository"]:::app\n'
                  '    SVC --> CLK["FakeTimeProvider<br/>via ConfigureTestServices"]:::swap\n'
                  "  end\n"
                  '  C -.->|"never happens"| NET["TCP socket, port,<br/>DNS, TLS"]:::gone\n'
                  '  REPO -.->|"never happens"| DB["database or<br/>container"]:::gone\n'
                  "  classDef test fill:#c7d2fe,color:#1f2937,stroke:#6366f1;\n"
                  "  classDef app fill:#ccfbf1,color:#1f2937,stroke:#0d9488;\n"
                  "  classDef swap fill:#fde68a,color:#1f2937,stroke:#d97706;\n"
                  "  classDef gone fill:#e2e8f0,color:#1f2937,stroke:#94a3b8;\n")},

        pcode(from_sample(API_TESTS, "round-trip"),
              "8.2 · POST then GET — the whole pipeline, no port",
              "<b>One client, three HTTP calls, three assertions.</b> "
              "<code>PostAsJsonAsync</code> and <code>GetFromJsonAsync</code> serialise with a client-side copy "
              "of the options the API is configured with — the <code>HttpClient</code> never sees "
              "<code>ConfigureHttpJsonOptions</code>, so keeping the two in step is your job, and a drift in "
              "naming policy or enum handling fails here rather than in production. The <code>GET</code> reuses "
              "<code>created.Headers.Location</code> instead of rebuilding the URL, which makes the test also "
              "an assertion about the <code>Created</code> response. The factory itself arrives through "
              "<code>IClassFixture</code> (§4), so all three tests in the class share one booted "
              "application."),

        pcode(from_sample(API_TESTS, "swap-clock"),
              "8.3 · Replacing one service for one test",
              "<b><code>ConfigureTestServices</code> runs after the application's own registrations, so the "
              "last <code>AddSingleton&lt;TimeProvider&gt;</code> wins.</b> The test then owns time: create a "
              "quote at 09:00, advance 31 days, and the accept call must answer <b>409 Conflict</b> because "
              "the 30-day validity has passed. Note <code>await using</code> on the derived factory — it owns "
              "a second host that must be disposed. This is the hook to reach for whenever a test needs a "
              "different partner client, a stub authority or a deterministic random source; " + ref(11) + " "
              "uses it to sign test tokens."),

        pcompare(from_sample(FEATURE, label="Gherkin — NoClaimBonus.feature"),
                 from_sample(STEPS, "steps"),
                 "8.4 · Executable specification — Gherkin on the left, its bindings on the right",
                 "<b>Reqnroll generates one xUnit test per scenario and per example row, so this feature file "
                 "is five test cases.</b> <code>{int}</code> and <code>{decimal}</code> are Cucumber "
                 "expressions, not regular expressions — the parameters arrive typed, which is why "
                 "<code>ThenNet</code> takes a <code>decimal</code> and compares money exactly. "
                 "<code>Background</code> runs before every scenario, as in Cucumber. SpecFlow, the library "
                 "this API comes from, reached end of life on 31 December 2024 after Tricentis discontinued "
                 "it; Reqnroll is the community fork that carried the project forward, and it is what new "
                 ".NET work uses (" + REQNROLL + ")."),

        {"type": "table", "heading": "8.5 · Which test to write — cost against what it can prove",
         "cols": ["Layer", "In this lesson", "Costs", "Reach for it when"],
         "rows": [
             ["<b>Unit</b>", "<code>L10.Pricing.Tests</code> · <code>L10.Pricing.VbTests</code>",
              "milliseconds, no I/O", "A rule, a boundary or an error path — the bulk of the suite"],
             ["<b>Executable spec</b>", "<code>L10.Pricing.Specs</code> (Reqnroll)",
              "a feature file plus bindings to maintain",
              "A non-engineer reads or writes the examples — rating tables, eligibility rules"],
             ["<b>In-process API</b>", "<code>L10.QuoteApi.Tests</code> (<code>WebApplicationFactory</code>)",
              "a host boot per class, still no port",
              "Serialisation, routing, status codes, middleware, DI wiring"],
             ["<b>Container-backed</b>", "not used here — no Docker on the build machine",
              "a container per fixture, and a Docker runtime",
              "Provider-specific SQL or a broker where an in-memory double would lie (" + TESTCONTAINERS + ")"],
             ["<b>Partner boundary</b>", "described only — a stub handler is a few lines, WireMock.Net a "
              "package",
              "no network, one handler or stub to write",
              "Proving retry, timeout and failure paths against ~30 partners without calling them ("
              + WIREMOCK + ")"],
             ["<b>Out-of-process HTTP</b>", "<code>L10.QuoteApi.http</code>",
              "needs the app running; not part of <code>dotnet test</code>",
              "Exploring, demonstrating, or replacing a Postman collection (" + HTTPFILES + ")"],
             ["<b>Browser / E2E</b>", "mentioned only — " + ref(12) + " owns deployment",
              "slowest and most brittle", "A user journey no lower layer can prove (" + PLAYWRIGHT + ")"],
             ["<b>Mutation</b>", "<code>*.Mtp</code> + Stryker.NET",
              "only the covering tests run per mutant — about ten seconds here",
              "Judging the suite itself, nightly or per pull request"]]},

        # ═══════════════════════════ 9 · HANDS-ON ═══════════════════════════
        {"type": "story", "heading": "9 · Hands-on — run the suites, then judge them",
         "html": (
             f"<p><b>Four commands, in this order: prove the {n_proj} projects build and pass, watch the "
             "coverage gate, run the same tests on the other platform, then score both suites.</b> The first "
             "command is the one to keep in muscle memory — <code>verify_samples.py</code> builds every "
             "project, runs every test project and runs every console app to completion.</p>"
             "<p><b>The third command is the platform lesson from §2 in one line.</b> "
             "<code>L10.Pricing.Tests.Mtp</code> compiles the same test files as a Microsoft.Testing.Platform "
             "executable, so you run it with <code>dotnet run</code> and get a different output shape — a "
             "<code>Test run summary</code> block instead of VSTest's <code>Passed!</code> line. Running "
             "<code>dotnet test</code> against it fails by design on the .NET 10 SDK, because this repository "
             "does not opt its <code>global.json</code> into MTP mode.</p>"
             "<p><b>The fourth command is the one that changes how you report quality.</b> Two Stryker runs, "
             f"same library, same 100% coverage: {STRONG_MUT}% and {WEAK_MUT}%. The second run exits non-zero "
             "and says so. Put that number beside the coverage number in whatever dashboard your team already "
             "reads.</p>")},

        pcode(from_text(HANDS_ON, "shell"), "9.1 · Commands",
              "<b>Nothing here needs a network, a database or Docker.</b> <code>dotnet test</code> restores "
              "and builds first. <code>dotnet tool restore</code> reads "
              "<code>samples/dotnet-tools.json</code> and installs <code>dotnet-stryker</code> 5.0.0 locally; "
              "Stryker must be started from inside the test project's folder, which is why step 4 changes "
              "directory. Expect each mutation run to take about ten seconds on a warm build at "
              "<code>concurrency: 1</code> (" + MEASURED + " once on the build machine); a cold restore and "
              "build take longer."),

        pcode(captured(HANDS_ON_OUTPUT, "Output — the four commands",
                       "captured on the build machine · sample paths shortened"),
              "9.2 · What you should see",
              "<b>Your timings will differ; the counts and the two scores should not.</b> Read the four "
              "blocks as one argument: everything passes, the strong suite holds 100 / 100 / 100, the same "
              f"{sum(n for lbl, n in CASES if lbl == 'C# unit tests')} tests also pass on the other platform "
              "with no source change, and then the mutation scores split the two suites apart. The last line "
              "is Stryker failing the weak suite against its own <code>break: 80</code> threshold — a "
              "non-zero exit you can put in a pipeline. " + MEASURED),

        {"type": "chartrow", "charts": [
            {"heading": f"9.3 · The {n_cases} test cases by kind", "kind": "donut",
             "args": {"data": CASES, "center": str(n_cases), "sub": f"from {n_methods} methods",
                      "width": 390, "height": 230},
             "caption": "test cases reported by the runs in 9.2 · one Gherkin example row and one "
                        "[Theory] row each count as a case",
             "note": f"<b>{n_hand} hand-written test methods and {n_scen} Gherkin scenarios ({n_methods} test "
                     f"methods once Reqnroll has generated its two) produce {n_cases} cases, and most of the "
                     "multiplication is table data.</b> Counting cases rather than "
                     "methods is what makes a "
                     "<code>TheoryData</code> table worth writing: one method, six rows, six independent "
                     "failures with their own names in the log — and the same holds for the four example rows "
                     "of the one Scenario Outline in 8.4. " + MEASURED},
            {"heading": "9.4 · Sample code by role", "kind": "bar",
             "args": {"data": [("Library", loc_lib), ("C# tests", loc_cs_tests), ("VB tests", loc_vb_tests),
                               ("API + tests", loc_api), ("Specs", loc_specs), ("Weak demo", loc_weak)],
                      "ylabel": "code lines", "tone": "navy", "width": 390, "height": 230,
                      "rotate_labels": True},
             "caption": "non-blank, non-comment lines · measured from the sample files when this PDF was built",
             "note": f"<b>{test_loc} lines of test code to {loc_lib} lines of library — about "
                     f"{ratio:.1f}:1.</b> That ratio is normal for a rules engine held at 100% branch "
                     "coverage, and it is the number to quote when someone asks what a coverage standard "
                     "costs. Line counts are a size signal, not a quality score. " + MEASURED}]},

        figure_heading("9.5 · What carries over, what is new, what to unlearn"),
        {"type": "threecol", "boxes": [
            {"heading": "Carries over unchanged", "tone": "teal",
             "items": ["Red / green / refactor, and naming tests as sentences",
                       "The test pyramid and where to spend the budget",
                       "Gating merges on coverage, and reporting it",
                       "Fakes over mocks for state, doubles for interaction",
                       "Gherkin — the same syntax, a different runner"]},
            {"heading": "Learn fresh", "tone": "indigo",
             "items": ["Two test platforms, and which one your tooling supports",
                       "The coverage gate as MSBuild properties in a shared <code>.props</code>",
                       "<code>TimeProvider</code> / <code>FakeTimeProvider</code> instead of your own clock",
                       "<code>TestContext.Current.CancellationToken</code> in every async test",
                       "Mutation score as a second, harder gate"]},
            {"heading": "Unlearn", "tone": "rose",
             "items": ["“100% coverage means the code is tested” — §7 measures the gap",
                       "“Setup goes in an annotated method” — in xUnit it is the constructor",
                       "“The test class instance is reused” — true in NUnit, false in xUnit and MSTest",
                       "“A fluent assertion library is a style choice” — since v8 it is a licence",
                       "“Integration tests need a server and a port” — they need neither"]}]},

        {"type": "callout", "variant": "warn", "heading": "⚠ Traps",
         "items": [
             "<b>Isolation is not what JUnit 5 gave you, in two ways.</b> NUnit shares one fixture instance "
             "across its tests unless the class carries "
             "<code>[FixtureLifeCycle(LifeCycle.InstancePerTestCase)]</code>, so a mutable field becomes "
             "cross-test state and the result depends on execution order (" + NUNITLIFE + " · 4.3). And "
             "xUnit runs test classes in parallel by default: a static, a temp file or a shared port that "
             "JUnit 5's sequential default let you get away with will flake — put the classes that share a "
             "resource in one <code>[Collection]</code> (" + PARALLEL + " · §4).",
             "<b>Your test platform decides which tools still work, and the two platforms must not be "
             "mixed.</b> <code>coverlet.collector</code> and <code>coverlet.msbuild</code> cannot run under "
             "Microsoft.Testing.Platform: move a suite from VSTest to MTP without switching to "
             "<code>coverlet.MTP</code> or Microsoft's coverage extension and the threshold does not fail — "
             "it stops being evaluated — so check that your gate still <i>fails</i> after a migration. "
             "Microsoft documents mixing VSTest and MTP projects in one solution as unsupported, and on the "
             ".NET 10 SDK <code>dotnet test</code> in VSTest mode refuses an MTP project outright. Pick one "
             "platform per repository (" + COVMTP + " · " + PLATFORMS + " · " + DOTNETTEST + " · 6.4).",
             "<b>Fluent Assertions 8 and later is not free for commercial use.</b> It is the Xceed Community "
             "License with a per-seat annual subscription for business use; version 7 remains Apache-2.0. "
             "A routine dependency bump can therefore create a licence obligation across every test project "
             "(" + FALICENCE + " · 5.3).",
             "<b>A passing suite at 100% coverage can still be worthless.</b> The measured weak suite in this "
             f"lesson holds 100% line and branch coverage and kills {WEAK_MUT}% of mutants. Coverage answers "
             "\"did it run\"; only an assertion — or a mutation score — answers \"was it checked\" (§7).",
             "<b>Forgetting the cancellation token is a build error here, not a warning.</b> xUnit1051 fires "
             "on any call that accepts a <code>CancellationToken</code> without one, and every sample in this "
             "repository treats warnings as errors. Pass "
             "<code>TestContext.Current.CancellationToken</code> (" + XUNIT1051 + ")."]},

        {"type": "callout", "variant": "ok", "heading": "✔ Checkpoint — you are ready for lesson 11 when",
         "items": [
             f"<code>python 0-script/verify_samples.py --only 10</code> reports {n_proj}/{n_proj} passed on "
             "your machine, and <code>dotnet test</code> on <code>L10.Pricing.Tests</code> prints "
             "100% line and 100% branch.",
             "You can say which package reference and which project property put a test project on VSTest "
             "rather than on Microsoft.Testing.Platform, and what <code>dotnet test</code> does in each mode "
             "on the .NET 10 SDK.",
             "You can delete one test from the strong suite, predict which line and which branch stop being "
             "covered, and explain why the command fails even though every remaining test passes.",
             "You can run both Stryker configurations, read a survived mutant in the HTML report and decide "
             "whether it deserves a new test or an exclusion.",
             "You can write an in-memory API test that replaces one registered service, and say why "
             "<code>WebApplicationFactory&lt;Program&gt;</code> compiles without a "
             "<code>public partial class Program</code> on .NET 10."]},

        {"type": "callout", "variant": "summary", "heading": "🔍 Check yourself",
         "items": [
             "A test project references <code>xunit.v3.mtp-off</code> and "
             "<code>xunit.runner.visualstudio</code>. Which platform is it on, which coverlet package can "
             "measure it, and what has to change to move it to the other platform?",
             "Why does <code>dotnet test</code> fail on <code>L10.Pricing.Tests.Mtp</code> on the .NET 10 SDK, "
             "and what are your two ways to run those tests?",
             "xUnit has no <code>[SetUp]</code> attribute. Where does per-test setup live, what disposes it, "
             "and which of the four frameworks in 4.3 would leak state between tests?",
             "Two suites both report 100% line and 100% branch coverage of the same library. What single "
             "measurement separates them, what is its formula, and what did it measure here?",
             f"All {STRONG_SURVIVED} survivors in the strong suite are string mutations in exception "
             "messages. Name one case where that is worth a new test and one where it is not.",
             "Which two lines of <code>CoverageGate.props</code> would you change to gate at 95% line coverage "
             "only, and what would the run in 6.2 then report?",
             "You need a test that proves a quote expires after 30 days. Why is "
             "<code>FakeTimeProvider</code> the answer rather than a <code>Thread.Sleep</code>, a shortened "
             "validity constant, or a mocked <code>DateTime.UtcNow</code>?"]},

        {"type": "footer",
         "html": ("<b>Lesson 10 in one line:</b> the framework choice is small (xUnit v3, NUnit, MSTest all "
                  "work) and the <b>platform</b> choice is not — VSTest or Microsoft.Testing.Platform decides "
                  "what <code>dotnet test</code> does and which coverage driver works. Write the gate as "
                  "MSBuild properties so <code>dotnet test</code> fails below 100% line <i>and</i> branch, "
                  "then measure what the gate cannot see: two suites here share 100% coverage and score "
                  f"<b>{STRONG_MUT}%</b> and <b>{WEAK_MUT}%</b> on mutation. Fake the clock, fake the "
                  "repository, host the API in the test process, and keep Gherkin for the examples a "
                  "non-engineer reads. "
                  "<br/><b>Next:</b> " + ref(11) + " — locking the same API down with JWT bearer tokens, "
                  "Entra ID and policy-based authorization, and testing the 401 / 403 / 200 matrix.")},
    ]
