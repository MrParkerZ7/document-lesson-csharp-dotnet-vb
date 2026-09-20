# -*- coding: utf-8 -*-
"""Lesson 08 — ASP.NET Core Web APIs. Built to 1-analysis/spec_lesson-pdfs/_standard.md; unit spec
1-analysis/spec_lesson-pdfs/lesson-08-aspnet-core-web-apis.md."""
import re

from lesson_kit import (DIFFERENT, ESTIMATE, MEASURED, RENAMED, REPO, SAME, TRAP, VERIFIED, T_ARCH, code,
                        compare, esc, from_sample, from_text, legend, link, loc, mapping, pill, style_block)
from lessons.roster import meta, ref

META = meta(
    8,
    subtitle="Hosting, dependency injection, minimal APIs, OpenAPI, resilient partner calls and background "
             "work in ASP.NET Core 10 — mapped from Spring Boot, NestJS and Express",
    objectives=[
        "Read a Program.cs the way you read a Spring Boot application class: services, configuration and "
        "options, then the middleware pipeline in the order it runs",
        "Choose Singleton, Scoped or Transient for every registration and recognise a captive dependency before "
        "it reaches production",
        "Build minimal API endpoints with route groups, typed results, endpoint filters, .NET 10 validation and "
        "ProblemDetails — and know when a controller is still the better fit",
        "Publish a truthful OpenAPI 3.1 document and decide the defaults of rate limiting, output caching, "
        "health checks and CORS deliberately",
        "Call external rating partners through IHttpClientFactory and the standard resilience handler, and run "
        "background work in a hosted service without taking the host down",
        "Host the whole pipeline in memory with WebApplicationFactory to prove your own endpoints, and plug a "
        "Visual Basic library into a C# web host",
    ],
    maps_from="Spring Boot services (auto-configuration, @RestController, @ConfigurationProperties, Actuator, "
              "Resilience4j, @Scheduled, @SpringBootTest), NestJS and Express APIs, and the partner integrations "
              "of a motor-insurance platform that called ~30 external rating partners.",
)

L = "lesson-08-aspnet-core-web-apis/samples"
API = f"{L}/L08.QuoteApi"
PROGRAM = f"{API}/Program.cs"
CROSS = f"{API}/CrossCutting/CrossCutting.cs"
NOTIFY = f"{API}/Notifications/Notifications.cs"
PARTNERS = f"{API}/Partners/Partners.cs"
CONTRACTS = f"{API}/Quotes/QuoteContracts.cs"
ENDPOINTS = f"{API}/Quotes/QuoteEndpoints.cs"
REGISTRATION = f"{API}/Quotes/QuoteRegistration.cs"
VB_DIR = f"{L}/L08.Rating.Vb"
VB_MODULE = f"{VB_DIR}/RatingModule.vb"
LAB = f"{L}/L08.HostingLab/Program.cs"
PLAB = f"{L}/L08.PartnerLab/Program.cs"
TOUR = f"{L}/L08.ApiTour/Program.cs"
TESTS = f"{L}/L08.QuoteApi.Tests"
FACTORY = f"{TESTS}/QuoteApiFactory.cs"

# ── official sources (checked 2026-09-16) ───────────────────────────────────────────────────────────
WHATSNEW = link("What's new in ASP.NET Core in .NET 10",
                "https://learn.microsoft.com/en-us/aspnet/core/release-notes/aspnetcore-10.0")
APIS = link("APIs overview", "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/apis")
WEBAPP = link("WebApplication and WebApplicationBuilder",
              "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis/webapplication")
CONFIG = link("Configuration in ASP.NET Core",
              "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/configuration/")
DI = link("Dependency injection: scope validation",
          "https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection/overview")
OPENAPI = link("OpenAPI support in ASP.NET Core",
               "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/overview")
SWASH = link("Swashbuckle removal announcement", "https://github.com/dotnet/aspnetcore/issues/54599")
ERRORS = link("Handle errors in ASP.NET Core APIs",
              "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/error-handling-api")
EXHANDLER = link("IExceptionHandler", "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/error-handling")
RATELIMIT = link("Rate limiting middleware", "https://learn.microsoft.com/en-us/aspnet/core/performance/rate-limit")
REJECT = link("RejectionStatusCode", "https://learn.microsoft.com/en-us/dotnet/api/"
              "microsoft.aspnetcore.ratelimiting.ratelimiteroptions.rejectionstatuscode")
OUTPUT = link("Output caching middleware",
              "https://learn.microsoft.com/en-us/aspnet/core/performance/caching/output")
HEALTH = link("Health checks in ASP.NET Core",
              "https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/health-checks")
HCF = link("Use the IHttpClientFactory", "https://learn.microsoft.com/en-us/dotnet/core/extensions/httpclient-factory")
RESIL = link("Build resilient HTTP apps", "https://learn.microsoft.com/en-us/dotnet/core/resilience/http-resilience")
POLLY = link("Polly circuit breaker", "https://www.pollydocs.org/strategies/circuit-breaker.html")
BG6 = link(".NET 6 hosting exception handling",
           "https://learn.microsoft.com/en-us/dotnet/core/compatibility/core-libraries/6.0/hosting-exception-handling")
BG10 = link(".NET 10 BackgroundService change", "https://learn.microsoft.com/en-us/dotnet/core/compatibility/"
            "extensions/10.0/backgroundservice-executeasync-task")
ITEST = link("Integration tests in ASP.NET Core", "https://learn.microsoft.com/en-us/aspnet/core/test/integration-tests")
IIS_INPROC = link("In-process hosting with IIS",
                  "https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/iis/in-process-hosting")
VALIDATION = link("Validation in ASP.NET Core", "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/validation")
LOGGING = link("Logging in .NET", "https://learn.microsoft.com/en-us/dotnet/core/extensions/logging/overview")
WEBAPI = link("Create web APIs with ASP.NET Core", "https://learn.microsoft.com/en-us/aspnet/core/web-api/")

# ── captured from real runs on the build machine (Windows 11, SDK 10.0.401, ASP.NET Core 10.0.12, 2026-09-20) ──
TOUR_OUT = """
POST /quotes                               201  net 8,400.00  total 9,023.95 THB
POST /quotes  (driver 22, 1 claim)         201  net 21,840.00  total 23,462.28 THB
POST /quotes  (3 claims in 5 years)        201  Declined, 3+ claims in 5 years
POST /quotes  (invalid body)               400  errors: Vehicle.SumInsured, NotifyVia
POST /quotes  (5th write this minute)      429  application/problem+json
GET  /quotes/{id}                          200  Quoted
GET  /quotes/{unknown id}                  404  application/problem+json
POST /quotes/{id}/accept                   200  policy MQ-000001, 2026-09-15 to 2027-09-14
POST /quotes/{id}/accept  (again)          409  The quote is AlreadyAccepted.
GET  /tariff/Class3Plus  (VB endpoint)     200  {"coverage":"Class3Plus","baseRate":0.009}
GET  /partners/p07/rates  (fails twice)    200  partner attempts 3
GET  /partners/p09/rates  (always fails)   503  partner attempts 4, Retry-After 30
GET  /health                               200  Degraded
GET  /openapi/v1.json                      200  openapi 3.1.1, 5 paths
     POST /quotes                          documents 201 400 429
     GET  /quotes/{id}                     documents 200 404
     POST /quotes/{id}/accept              documents 200 404 409
     GET  /tariff/{coverage}               documents 200
     GET  /partners/{partnerId}/rates      documents 200
background notification sent: line  MQ-000001
"""

CONFIG_OUT = """
1 configuration: the last source that sets a key wins
   appsettings.json             30
   appsettings.Production.json  21
   environment                  14
   command line                 7
   => Quotes:ValidityDays = 7
2 options validation: fail at start-up, not on first use
   OptionsValidationException
                DataAnnotation validation failed for
                'QuoteOptions' members: 'ValidityDays' with
                the error: 'The field ValidityDays must be
                between 1 and 90.'.
"""

LIFETIME_OUT = """
3 lifetimes: two requests, each resolving every service twice
   request A: transient 1,2  scoped 1,1  singleton 1,1
   request B: transient 3,4  scoped 2,2  singleton 1,1
4 captive dependency: a singleton holding a scoped service
   unvalidated: scope 1 sees ScopedOp #3, scope 2 sees
                ScopedOp #3
   validated:   Cannot consume scoped service 'ScopedOp' from
                singleton 'PriceCache'.
5 keyed services: one interface, a key per implementation
   key "line" resolves LineNotifier
   unkeyed INotifier    null
"""

PARTNER_OUT = """
scenario                                  attempts  outcome
no resilience handler, partner fails once        1  503
standard handler, partner fails twice            3  200
standard handler, partner always fails           4  503
standard handler, POST, unsafe excluded          1  503
breaker opens early, call 1                      2  BrokenCircuitException
breaker opens early, call 2                      0  BrokenCircuitException
breaker opens early, call 3                      0  BrokenCircuitException
invalid options, rejected when the client is created:
  The sampling duration of circuit breaker strategy needs to be at least double of
  an attempt timeout strategy’s timeout interval, in order to be effective.
  Sampling Duration: 30s,Attempt Timeout: 20s
"""

# `dotnet new list --tag Web` on SDK 10.0.401 (template name and language columns)
WEB_TEMPLATES = """
API Controller                                apicontroller      [C#]
ASP.NET Core Empty                            web                [C#],F#
ASP.NET Core gRPC Service                     grpc               [C#]
ASP.NET Core Web API                          webapi             [C#],F#
ASP.NET Core Web API (native AOT)             webapiaot          [C#]
ASP.NET Core Web App (Model-View-Controller)  mvc                [C#],F#
ASP.NET Core Web App (Razor Pages)            webapp,razor       [C#]
Blazor Web App                                blazor             [C#]
Blazor WebAssembly Standalone App             blazorwasm         [C#]
MSTest Playwright Test Project                mstest-playwright  [C#]
MSTest Test Project                           mstest             [C#],F#,VB
MVC Controller                                mvccontroller      [C#]
MVC ViewImports                               viewimports        [C#]
MVC ViewStart                                 viewstart          [C#]
NUnit Playwright Test Project                 nunit-playwright   [C#]
NUnit Test Project                            nunit              [C#],F#,VB
Protocol Buffer File                          proto
Razor Class Library                           razorclasslib      [C#]
Razor Component                               razorcomponent     [C#]
Razor Page                                    page               [C#]
Razor View                                    view               [C#]
Worker Service                                worker             [C#],F#
xUnit Test Project                            xunit              [C#],F#,VB
"""

# Pygments boxes tokens it cannot lex in red: VB 14 interpolated strings, Kotlin's `$` inside a JSONPath
# string. The code is valid, so the box is removed for every language (lesson 01 does it for VB only).
_ERROR_SPAN = re.compile(r'<span style="border: 1px solid #F00">(.*?)</span>', re.S)


# Lesson-local print rules: a story or callout heading never prints alone at a page foot, and an unkept code
# panel may split across pages (see listed()).
LOCAL_CSS = ("<style>.callout .ct { break-after:avoid; page-break-after:avoid; } "
             ".callout li:first-child { break-before:avoid; page-break-before:avoid; } "
             ".story .ct { break-after:avoid; page-break-after:avoid; } "
             ".codeblk > .ct { break-after:avoid; page-break-after:avoid; } "
             ".code .ch { break-after:avoid; page-break-after:avoid; } "
             ".code pre { orphans:4; widows:4; } "
             "a.lnk, a { word-break:normal; overflow-wrap:break-word; }</style>")

_UNKEPT_HEAD = re.compile(r'^<div class="codeblk">(<div class="codeh">.*?</div>)', re.S)


def listed(block, heading):
    """Put a code()/compare() panel in the Contents at level 2 and remove Pygments' error boxes.

    A listed block gets a Contents marker, and brief_pdf makes the marker's host break-inside:avoid unless the
    host opens with a `.ct` heading line, so a long panel built with keep=False still jumped whole to the next
    page and left a gap. For an unkept panel, wrap its heading in a `.ct` line: the marker is pinned to the
    heading and the panel may split as _standard.md section 5 describes. Kept panels are left alone."""
    block.update(heading=heading, toc=2)
    html = _ERROR_SPAN.sub(r"\1", block["html"])
    if 'class="code keep"' not in html and 'class="cmp keep"' not in html:
        html = _UNKEPT_HEAD.sub(r'<div class="codeblk"><div class="ct">\1</div>', html, count=1)
    block["html"] = html
    return block


def pcode(s, heading, note, keep=None):
    return listed(code(s, heading=heading, note=note, keep=keep), heading)


def _half_width(src):
    """A compare() panel is half a page wide, so its header truncates a long file label: drop the folder prefix
    the heading and the other panel already give (the code itself is untouched)."""
    label = src.get("file") or ""
    if label.startswith("captured"):
        return dict(src, file="captured run")
    path, sep, region = label.partition("  ·  ")
    if path.startswith("samples/"):
        path = path[len("samples/"):]
    if len(path + sep + region) > 56:
        path = path.rsplit("/", 1)[-1]
    return dict(src, file=path + sep + region)


def pcompare(left, right, heading, note, keep=None):
    return listed(compare(_half_width(left), _half_width(right), heading=heading, note=note, keep=keep), heading)


def figure_heading(text):
    """A numbered heading for a block type that prints none of its own (twocol), kept with that block."""
    return {"type": "html", "html": f'<div class="figh"><h2>{esc(text)}</h2></div>', "heading": text,
            "toc": 2, "_keep_with_next": True}


def captured(text, label):
    return from_text(text, "text", label=label, file="captured on the build machine")


# ── measured figures ─────────────────────────────────────────────────────────────────────────────
def sample_sources():
    root = REPO / L
    return sorted(p for p in root.rglob("*") if p.is_file() and p.suffix in (".cs", ".vb")
                  and "obj" not in p.parts and "bin" not in p.parts)


def tests_by_area():
    """[Fact] methods plus [InlineData] rows per test file — the xUnit test cases dotnet test reports."""
    names = {"QuoteEndpointTests.cs": "Endpoints", "HostingTests.cs": "Hosting & DI",
             "CrossCuttingTests.cs": "Cross-cutting", "PartnerResilienceTests.cs": "Resilience"}
    out = []
    for p in sorted((REPO / TESTS).glob("*.cs")):
        text = p.read_text(encoding="utf-8-sig")
        n = len(re.findall(r"\[Fact\]", text)) + len(re.findall(r"\[InlineData\(", text))
        if n:
            out.append((names.get(p.name, p.stem), n))
    return sorted(out, key=lambda r: -r[1])


def registrations_by_lifetime():
    """Service registrations written in the API and the VB module, grouped by lifetime (framework Add* calls
    such as AddOpenApi are not counted)."""
    files = [p for p in (REPO / API).rglob("*.cs") if "obj" not in p.parts] + [REPO / VB_MODULE]
    text = "\n".join(p.read_text(encoding="utf-8-sig") for p in files)
    return [("Singleton", len(re.findall(r"\.Add(?:Keyed)?Singleton[<(]", text))),
            ("Scoped", len(re.findall(r"\.Add(?:Keyed)?Scoped[<(]", text))),
            ("Transient", len(re.findall(r"\.Add(?:Keyed)?Transient[<(]", text))
             + len(re.findall(r"\.AddHttpClient<", text))),
            ("Hosted service", len(re.findall(r"\.AddHostedService<", text)))]


_ROUTES = [(r"^/quotes$", "POST /quotes"), (r"^/quotes/\{[^}]*\}$", "GET /quotes/{id}"),
           (r"^/quotes/\{id\}/accept$", "POST accept"), (r"^/tariff/", "GET tariff (VB)"),
           (r"^/partners/", "GET partner rate")]


def _op(route):
    return next((name for pat, name in _ROUTES if re.search(pat, route)), None)


def status_codes():
    """Per operation: the status codes the OpenAPI document declares and the codes the tour received."""
    documented, observed = {}, {}
    for ln in TOUR_OUT.strip("\n").splitlines():
        if m := re.match(r"^\s+(GET|POST)\s+(\S+)\s+documents ([\d ]+)$", ln):
            documented[_op(m.group(2))] = m.group(3).split()
        elif (m := re.match(r"^(GET|POST)\s+(.+?)\s{2,}.*?(\d{3})\s{2}", ln)) and _op(m.group(2)):
            observed.setdefault(_op(m.group(2)), []).append(m.group(3))
    ops = [name for _, name in _ROUTES]
    return ops, documented, {k: sorted(set(v)) for k, v in observed.items()}


# heatmap cell codes: colour intensity grows with the value, so the mismatch that matters is darkest
BOTH, DOC_ONLY, UNDOCUMENTED = 1, 2, 3
_CELL = {BOTH: "ok", DOC_ONLY: "doc", UNDOCUMENTED: "GAP"}


def status_matrix(ops, documented, observed):
    """Operations x status codes: documented and received (1), documented only (2), received only (3)."""
    codes = sorted({c for d in (documented, observed) for cs in d.values() for c in cs})
    matrix = []
    for op in ops:
        row = []
        for c in codes:
            doc, got = c in documented.get(op, []), c in observed.get(op, [])
            row.append(BOTH if doc and got else DOC_ONLY if doc else UNDOCUMENTED if got else None)
        matrix.append(row)
    return codes, matrix


def partner_attempts():
    rows = []
    for ln in PARTNER_OUT.strip("\n").splitlines()[1:]:
        if m := re.match(r"^(.+?)\s+(\d+)\s+(\S+)$", ln):
            rows.append((m.group(1), int(m.group(2)), m.group(3)))
    return rows


def templates_by_language():
    counts = {"C#": 0, "F#": 0, "VB": 0}
    rows = WEB_TEMPLATES.strip("\n").splitlines()
    for ln in rows:
        cols = re.split(r"\s{2,}", ln.strip())
        for lang in (cols[2] if len(cols) > 2 else "").replace("[", "").replace("]", "").split(","):
            if lang in counts:
                counts[lang] += 1
    return len(rows), list(counts.items())


def blocks():
    n_tests = sum(n for _, n in tests_by_area())
    sources = sample_sources()
    loc_total = loc(*[p.relative_to(REPO).as_posix() for p in sources])
    loc_vb = loc(*[p.relative_to(REPO).as_posix() for p in sources if p.suffix == ".vb"])
    n_proj = len(list((REPO / L).glob("*/*.*proj")))
    ops, documented, observed = status_codes()
    undocumented = {op: [c for c in observed.get(op, []) if c not in documented.get(op, [])] for op in ops}
    gaps = [(op, codes) for op, codes in undocumented.items() if codes]
    unseen = {op: [c for c in documented.get(op, []) if c not in observed.get(op, [])] for op in ops}
    attempts = partner_attempts()
    n_templates, by_lang = templates_by_language()
    vb_templates = dict(by_lang)["VB"]
    regs = registrations_by_lifetime()
    codes, matrix = status_matrix(ops, documented, observed)

    cross_cards = [
        {"num": 1, "title": "Rate limiting", "tags": [T_ARCH], "pills": [DIFFERENT],
         "what": "Named policies registered with <code>AddRateLimiter</code>, applied per endpoint with "
                 "<code>RequireRateLimiting</code>, enforced by <code>UseRateLimiter</code>.",
         "lines": [("Spring", "Resilience4j <code>@RateLimiter</code>, or a quota at the API gateway"),
                   ("Default", "A rejected request gets <b>503</b> — the sample sets 429 (" + REJECT + ")"),
                   ("Sample", "<code>quote-writes</code>: fixed window per client IP, limit from options"),
                   ("Watch", "Partitions keyed on client input such as IP are a DoS surface (" + RATELIMIT + ")")]},
        {"num": 2, "title": "Output caching", "tags": [T_ARCH], "pills": [DIFFERENT],
         "what": "Stores whole responses on the server and replays them; opt in per endpoint with "
                 "<code>CacheOutput()</code>.",
         "lines": [("Like", "Spring <code>@Cacheable</code>, but for the HTTP response, not a method result"),
                   ("Default", "GET/HEAD 200 only, no cookies, no authenticated requests, 60 s"),
                   ("Store", "In-process memory: every instance has its own cache — Redis to share it"),
                   ("Sample", "The second <code>GET /tariff/Class3Plus</code> carries an <code>Age</code> header (test)")]},
        {"num": 3, "title": "Health checks", "tags": [T_ARCH], "pills": [DIFFERENT],
         "what": "<code>AddHealthChecks().AddCheck&lt;T&gt;()</code> plus <code>MapHealthChecks(\"/health\")</code>.",
         "lines": [("Spring", "Actuator <code>/actuator/health</code>: <code>UP</code> or <code>DOWN</code>, "
                              "no built-in Degraded state"),
                   ("Status", "Healthy <b>200</b> · Degraded <b>200</b> · Unhealthy <b>503</b> (" + HEALTH + ")"),
                   ("Body", "Plain text: <code>Healthy</code>, <code>Degraded</code> or <code>Unhealthy</code>"),
                   ("Sample", "<code>PartnerHealthCheck</code> reports Degraded after a partner call fails")]},
    ]

    return [
        style_block(),
        {"type": "toc", "heading": "▤ Contents", "depth": 2,
         "note": "Page numbers are resolved from the rendered PDF. Code panels are cut from the compiled samples."},
        {"type": "html", "html": LOCAL_CSS},

        # ═══════════════════════════ 1 · WHY ═══════════════════════════
        {"type": "story", "heading": "1 · Why this lesson — the service you have built many times, rebuilt in .NET",
         "html": (
             "<p><b>You have shipped this service already: an HTTP API with validation, configuration per "
             "environment, a DI container, calls to unreliable partners and a background worker.</b> You built it "
             "in Spring Boot and WebFlux, in NestJS and Express, and you wired a motor-insurance platform to "
             "~30 external rating partners. ASP.NET Core does the same jobs; this lesson spends its words on "
             "where the .NET shape differs and where its defaults would surprise you.</p>"
             "<p><b>The biggest shift is from discovery to declaration.</b> Spring finds beans by scanning and "
             "configures itself from the classpath. An ASP.NET Core service states everything in "
             "<code>Program.cs</code>: each service and its lifetime, each middleware in the order it runs, each "
             "endpoint. That file is the architecture diagram, so reviewing it is where you catch design "
             "problems.</p>"
             "<p><b>The running example is the MotorQuote API.</b> <code>L08.QuoteApi</code> creates, reads and "
             "accepts quotes, prices them with rating rules written in Visual Basic (<code>L08.Rating.Vb</code>), "
             "calls rating partners through a resilient typed client, and notifies the customer from a background "
             "service. It prices with the track's canonical tariff — illustrative rates, not a real one — and its "
             "quote store stays in memory for the whole lesson: persistence is not this lesson's subject. "
             + ref(9) + " models the same quotes in a real database, a <code>DbContext</code> and migrations in "
             "projects of its own rather than by editing this API; " + ref(11) + " secures an API like this "
             "one.</p>")},

        {"type": "kpi", "heading": "1.1 · The numbers to leave this lesson with",
         "items": [
             {"label": "OpenAPI version emitted", "value": "3.1", "tone": "teal",
              "sub": ".NET 10 default · verified · sample serves 3.1.1"},
             {"label": "Retries, standard handler", "value": "3", "tone": "amber",
              "sub": "exponential + jitter, all methods · verified"},
             {"label": "Rate-limit rejection", "value": "503", "tone": "red",
              "sub": "default status, not 429 · verified"},
             {"label": "Lesson 08 tests", "value": str(n_tests), "tone": "indigo",
              "sub": "in-memory API tests · measured"},
             {"label": "Sample code", "value": f"{loc_total} lines", "tone": "navy",
              "sub": f"C# + VB, {n_proj} projects · measured"}]},

        legend(T_ARCH),

        {"type": "callout", "variant": "info", "heading": "ℹ Before you start",
         "items": [
             "<b>You need records and interfaces from " + ref(3) + "; <code>async</code>/<code>await</code>, "
             "cancellation and channels from " + ref(5) + "; and project references from " + ref(7) + ".</b> "
             "DI, SOLID and HTTP design are assumed; the lesson explains their .NET form, not the ideas.",
             f"<b>You will build and run {n_proj} projects:</b> the <code>L08.QuoteApi</code> web API, the "
             "<code>L08.Rating.Vb</code> Visual Basic library it calls, <code>L08.QuoteApi.Tests</code> "
             f"({n_tests} in-memory tests), and three console apps — <code>L08.HostingLab</code> (configuration "
             "and DI), <code>L08.PartnerLab</code> (resilience) and <code>L08.ApiTour</code> (the API as a "
             "client sees it). None opens a port or touches the network.",
             "<b>Chips:</b> " + SAME + " transfers as-is, " + RENAMED + " is the same idea under another name, "
             + DIFFERENT + " behaves differently, " + TRAP + " looks the same and bites. Facts that change between "
             "releases are " + VERIFIED + " with a link; numbers from this repository are " + MEASURED + "; "
             "judgements are " + ESTIMATE + ". Kotlin and TypeScript panels are for comparison and are not "
             "compiled."]},

        # ═══════════════════════════ 2 · HOSTING ═══════════════════════════
        {"type": "story", "heading": "2 · Hosting, configuration and options",
         "html": (
             "<p><b>An ASP.NET Core service is a console program that builds a host, and what Spring Boot does by "
             "scanning happens in explicit lines of <code>Program.cs</code>.</b> "
             "<code>WebApplication.CreateBuilder(args)</code> sets up configuration, logging, the DI container and "
             "Kestrel, the in-process web server that plays embedded Tomcat's or Netty's part. You register "
             "services on <code>builder.Services</code>, call <code>Build()</code>, add middleware and endpoints "
             "to <code>app</code>, and call <code>Run()</code>.</p>"
             "<p><b>Middleware runs in the order of the lines — after one step you did not write.</b> As in "
             "Express, each <code>Use…</code> wraps everything after it. When you map endpoints, "
             "<code>WebApplication</code> adds <code>UseRouting</code> itself, ahead of your middleware (" + WEBAPP +
             "), so the endpoint is already chosen when <code>UseCors</code> and <code>UseRateLimiter</code> run. "
             "Unlike Express, the exception handler goes first: it can only catch what runs inside it.</p>"
             "<p><b>Configuration is a stack of sources where the last one wins, and the options pattern is your "
             "<code>@ConfigurationProperties</code>.</b> For a web app, from highest priority: command line, "
             "environment variables, user secrets (Development only), <code>appsettings.{Environment}.json</code>, "
             "<code>appsettings.json</code> (" + CONFIG + "). An environment variable spells "
             "<code>Quotes:ValidityDays</code> as <code>Quotes__ValidityDays</code>. Bind a section to a class, "
             "validate it with DataAnnotations and call <code>ValidateOnStart()</code> — without that call a bad "
             "value fails the first request that reads it instead of failing the deployment.</p>"
             "<p><b>Logging is injected like any service: ask for <code>ILogger&lt;T&gt;</code> and you get the "
             "SLF4J logger for class <code>T</code>.</b> The category is <code>T</code>'s full name, and "
             "<code>Logging:LogLevel</code> in <code>appsettings.json</code> sets the minimum level per category "
             "prefix — the sample raises <code>Microsoft.AspNetCore</code> to Warning. A message is a template: "
             "in <code>\"Partner {PartnerId} unavailable\"</code> the placeholder is filled by position, like "
             "SLF4J's <code>{}</code>, and its name becomes a property that a structured log store can query "
             "(" + LOGGING + "). Build the message with <code>$\"…\"</code> and that property is gone. Log sinks, "
             "OpenTelemetry and CloudWatch belong to " + ref(12) + ".</p>")},

        {"type": "mermaid", "inline": True,
         "heading": "2.1 · The request pipeline of L08.QuoteApi",
         "caption": "numbers = run order · amber = the incoming request · slate = added by WebApplication · "
                    "indigo = middleware in Program.cs order · teal = the endpoint that runs · a response travels "
                    "back through the same steps in reverse",
         "code": ("flowchart TB\n"
                  '  IN["HTTP request<br/>Kestrel"]:::io\n'
                  '  subgraph AUTO["Added by WebApplication"]\n'
                  "    direction LR\n"
                  '    DEV["1 · Developer exception page<br/>Development only"]:::auto --> ROUTE["2 · UseRouting<br/>'
                  'matches the endpoint"]:::auto\n'
                  "  end\n"
                  '  subgraph MW["Your middleware, in Program.cs order"]\n'
                  "    direction LR\n"
                  '    EX["3 · UseExceptionHandler"]:::mw --> SC["4 · UseStatusCodePages"]:::mw --> '
                  'CO["5 · UseCors"]:::mw --> RL["6 · UseRateLimiter"]:::mw --> OC["7 · UseOutputCache"]:::mw\n'
                  "  end\n"
                  '  subgraph EP["8 · The matched endpoint runs"]\n'
                  "    direction LR\n"
                  '    MIN["Minimal API<br/>endpoint filters, handler"]:::ep\n'
                  '    CTL["Controller<br/>MVC filters, action"]:::ep\n'
                  '    HC["Health check<br/>OpenAPI document"]:::ep\n'
                  "    MIN ~~~ CTL ~~~ HC\n"
                  "  end\n"
                  "  IN --> AUTO\n"
                  "  AUTO --> MW\n"
                  "  MW --> EP\n"
                  "  style AUTO fill:#f8fafc,stroke:#cbd5e1\n"
                  "  style MW fill:#f8fafc,stroke:#cbd5e1\n"
                  "  style EP fill:#f8fafc,stroke:#cbd5e1\n"
                  "  classDef io fill:#fde68a,color:#1f2937,stroke:#d97706;\n"
                  "  classDef auto fill:#e2e8f0,color:#1f2937,stroke:#475569;\n"
                  "  classDef mw fill:#c7d2fe,color:#1f2937,stroke:#6366f1;\n"
                  "  classDef ep fill:#ccfbf1,color:#1f2937,stroke:#0d9488;\n")},

        pcode(from_sample(PROGRAM, "services"), "2.2 · Program.cs, part 1 — the services",
              "<b>Read it as the Spring application class with the scanning written out.</b> Framework features "
              "first — ProblemDetails, the exception handler, .NET 10 validation, OpenAPI, health checks — then "
              "one <code>Add…</code> call per feature registration, C# and VB side by side, then the cross-cutting "
              "policies of §6. Look twice at the JSON lines: minimal APIs read "
              "<code>ConfigureHttpJsonOptions</code> and controllers read <code>AddJsonOptions</code>, two "
              "separate option sets. Configure one and the other endpoint style keeps its defaults — the test "
              "<code>Minimal_APIs_and_controllers_read_separate_json_options</code> clears the MVC set and only the "
              "controller's enum turns into a number."),

        pcompare(from_text("""
            const app = express();

            // Express runs middleware in registration order too
            app.use(express.json());
            app.use(cors({ origin: "https://brokers.example" }));
            app.use("/quotes", rateLimit({ windowMs: 60000, limit: 20 }));

            app.get("/openapi.json", (_req, res) => res.json(spec));
            app.get("/health", healthHandler);
            app.use("/partners", partnersRouter);
            app.use("/quotes", quotesRouter);

            // the error handler is registered LAST in Express
            app.use((err, _req, res, _next) =>
              res.status(500)
                 .type("application/problem+json")
                 .json({ title: "Unexpected error", status: 500 }));

            app.listen(5174);
            """, "typescript", file="an Express service you know"),
                 from_sample(PROGRAM, "pipeline"),
                 "2.3 · Program.cs, part 2 — the pipeline, next to Express",
                 "<b>Same idea, two differences.</b> Express registers its error middleware last because errors are "
                 "passed forward to it; <code>UseExceptionHandler</code> goes first because it catches what runs "
                 "inside it. And there is no <code>UseRouting</code> line: <code>WebApplication</code> inserts it "
                 "before the first middleware. The OpenAPI document is mapped everywhere except Production — the "
                 "web API template maps it in Development only (" + OPENAPI + ")."),

        mapping("2.4 · Concept map — Spring Boot, NestJS and Express → ASP.NET Core", [
            ("<code>SpringApplication.run</code> · <code>NestFactory.create</code>",
             "<code>WebApplication.CreateBuilder(args)</code>", "renamed",
             "Register every service before <code>Build()</code>; the container is fixed after it"),
            ("Embedded Tomcat / Netty · Node <code>http</code>", "Kestrel, in process", "same",
             "Behind a load balancer or reverse proxy it is still Kestrel; under IIS the default in-process "
             "model uses IIS HTTP Server instead (" + IIS_INPROC + ") — " + ref(12)),
            ("Servlet filters · Express <code>app.use</code>", "Middleware: <code>app.UseX()</code>", "same",
             "Line order is run order; routing is inserted before your first middleware"),
            ("Component scanning + <code>@Autowired</code>", "Explicit <code>builder.Services.Add…</code> calls",
             "different", "Nothing is discovered; an unregistered type fails when it is resolved"),
            ("<code>@ConfigurationProperties</code> + <code>@Validated</code>",
             "Options pattern: <code>AddOptions&lt;T&gt;().Bind(…)</code>", "renamed",
             "Add <code>ValidateOnStart()</code>, or bad config fails on first use"),
            ("<code>application-{profile}.yml</code> · <code>NODE_ENV</code>",
             "<code>appsettings.{Environment}.json</code>", "renamed",
             "Picked by <code>ASPNETCORE_ENVIRONMENT</code>; variables use <code>__</code> for <code>:</code>"),
            ("SLF4J <code>Logger</code> · <code>@Slf4j</code> · NestJS <code>Logger</code>",
             "<code>ILogger&lt;T&gt;</code> + message templates", "trap",
             "Placeholders are named properties; a <code>$\"…\"</code> message loses them"),
            ("Jackson <code>ObjectMapper</code> configuration",
             "<code>ConfigureHttpJsonOptions</code> · <code>AddJsonOptions</code>", "trap",
             "Minimal APIs and controllers read separate JSON options — set both"),
            ("Spring request scope · NestJS <code>Scope.REQUEST</code>", "<code>AddScoped</code>", "trap",
             "A singleton holding it is caught only in Development — §3"),
            ("<code>@Qualifier(\"line\")</code>", "Keyed services: <code>[FromKeyedServices(\"line\")]</code>",
             "renamed", "An unkeyed <code>GetService&lt;T&gt;()</code> does not see keyed registrations"),
            ("<code>@RestController</code> · NestJS <code>@Controller</code>",
             "Minimal API <code>MapPost</code>, or <code>ControllerBase</code>", "different",
             "Minimal APIs are the recommended default for new projects — §4"),
            ("<code>HandlerInterceptor</code> · NestJS interceptors and pipes", "Endpoint filters (<code>IEndpointFilter</code>)",
             "renamed", "Filters see the bound arguments; middleware sees only the raw request"),
            ("Bean Validation <code>@Valid</code> · <code>class-validator</code>",
             "DataAnnotations + <code>AddValidation()</code> (.NET 10)", "renamed",
             "Parameters are checked on every endpoint; request types only if declared in the calling assembly"),
            ("springdoc-openapi · <code>@nestjs/swagger</code>", "<code>AddOpenApi</code> + <code>MapOpenApi</code>",
             "renamed", "OpenAPI 3.1, no UI in the box; documents only declared status codes"),
            ("<code>@ControllerAdvice</code> · NestJS exception filters",
             "<code>IExceptionHandler</code> + ProblemDetails", "renamed",
             ".NET 10 no longer logs exceptions a handler marks as handled"),
            ("<code>WebClient</code> + Resilience4j", "Typed client + standard resilience handler",
             "trap", "Retries every HTTP method by default — POST included"),
            ("<code>@Scheduled</code> worker · a BullMQ consumer", "<code>BackgroundService</code>", "different",
             "Singleton: open a scope per unit of work; an escaping exception stops the host"),
            ("<code>@SpringBootTest</code> + MockMvc · supertest", "<code>WebApplicationFactory&lt;Program&gt;</code>",
             "same", "Runs the real pipeline in memory; environment defaults to Development"),
        ]),

        pcompare(from_sample(LAB, "config-precedence"), captured(CONFIG_OUT, "Output — L08.HostingLab, parts 1 and 2"),
                 "2.5 · Configuration layers and options validation, run for real",
                 "<b>Every provider keeps its own value; the last one added answers.</b> The lab stacks four "
                 "sources the way <code>CreateBuilder</code> does and asks each for "
                 "<code>Quotes:ValidityDays</code>; the command line wins with 7. Part 2 binds "
                 "<code>ValidityDays = 0</code> to options with <code>[Range(1, 90)]</code> and "
                 "<code>ValidateOnStart()</code>: <code>StartAsync</code> throws "
                 "<code>OptionsValidationException</code> before any request is served."),

        pcompare(from_sample(REGISTRATION, "register"), from_sample(VB_MODULE, "register"),
                 "2.6 · A feature registration in C# and in Visual Basic",
                 "<b>The same registration in both languages.</b> Each registration binds its own configuration "
                 "section, validates it at start-up and registers its services; <code>Program.cs</code> calls "
                 "<code>AddQuoteFeature</code> and <code>AddMotorRating</code> side by side. Both are feature seams "
                 "inside an assembly, not the assembly-sized module " + ref(7) + " maps onto a Gradle module. The VB "
                 "version needs <code>&lt;Extension&gt;</code> inside a <code>Module</code> — there the VB keyword "
                 "for a type that holds only shared members — where C# writes <code>this</code> in a static class, "
                 "and <code>_</code> to continue a line that ends before the dot. The <code>RatingOptions</code> it "
                 "binds hold the track's canonical rates (§9.2)."),

        # ═══════════════════════════ 3 · DI ═══════════════════════════
        {"type": "story", "heading": "3 · Dependency injection — lifetimes are a design decision",
         "html": (
             "<p><b>The container does what Spring's does, with one change that shows up in code review: every "
             "registration names its lifetime.</b> Spring and NestJS default to singletons; here "
             "<code>AddSingleton</code>, <code>AddScoped</code> and <code>AddTransient</code> are separate calls. "
             "Scoped means one instance per HTTP request, because ASP.NET Core opens a scope for each request and "
             "disposes it at the end.</p>"
             "<p><b>The bug to design against is the captive dependency: a singleton that receives a scoped "
             "service keeps the first instance for the life of the process.</b> The container checks for it — "
             "scoped services resolved from the root provider or injected into singletons — only when the app runs "
             "in Development (" + DI + "). In Staging or Production the same code starts and silently shares "
             "one instance: in 3.3 two scopes both see <code>ScopedOp #3</code>. The sample's test factory "
             "turns the checks on for its Testing environment.</p>"
             "<p><b>Keyed services (.NET 8) replace <code>@Qualifier</code>.</b> "
             "<code>AddKeyedScoped&lt;INotificationChannel, LineChannel&gt;(\"line\")</code> registers one "
             "implementation per key; <code>[FromKeyedServices(\"line\")]</code> or "
             "<code>GetRequiredKeyedService</code> resolves it. A plain <code>GetService&lt;INotifier&gt;()</code> "
             "returns null, because keyed registrations are invisible to unkeyed resolution.</p>")},

        pcompare(from_sample(LAB, "lifetimes"), captured(LIFETIME_OUT, "Output — L08.HostingLab, parts 3 to 5"),
                 "3.1 · Two requests, three lifetimes",
                 "<b>Read the numbers as instance ids.</b> Each request resolves every service twice: transient "
                 "gives four instances (1–4), scoped one per request (1, 2), singleton one in total. Part 4 of the "
                 "output is the captive dependency in 3.3; part 5 is the keyed lookup from the story — the keyed "
                 "registrations of the API itself are in 8.3."),

        {"type": "table", "heading": "3.2 · Choosing a lifetime",
         "cols": ["Lifetime", "One instance per", "Spring · NestJS", "In L08.QuoteApi", "Watch for"],
         "rows": [
             ["<b>Singleton</b>", "container (process)", "singleton (the default) · default scope",
              "<code>IQuoteStore</code>, <code>PolicyNumbers</code>, <code>NotificationQueue</code>, VB "
              "<code>PremiumCalculator</code>",
              "Shared by concurrent requests: use <code>ConcurrentDictionary</code>, <code>Interlocked</code>, "
              "<code>Lock</code>"],
             ["<b>Scoped</b>", "HTTP request (or manual scope)", "request scope · <code>Scope.REQUEST</code>",
              "<code>QuoteService</code>, keyed notification channels",
              "Never inject into a singleton or a hosted service — create a scope"],
             ["<b>Transient</b>", "resolution", "prototype · <code>Scope.TRANSIENT</code>",
              "<code>PartnerRateClient</code> (typed <code>HttpClient</code>)",
              "A typed client captured by a singleton stops seeing DNS changes (" + HCF + ")"]]},

        pcode(from_sample(LAB, "captive"), "3.3 · A captive dependency, unvalidated and validated",
              "<b>The bug compiles, starts and passes a happy-path test.</b> <code>PriceCache</code> is a singleton "
              "whose constructor takes the scoped <code>ScopedOp</code>. Built without validation — the default "
              "outside Development — the provider hands both scopes the one instance it created first, "
              "<code>#3</code> because part 3 already made <code>#1</code> and <code>#2</code>. Built with "
              "<code>ValidateScopes</code> and <code>ValidateOnBuild</code>, it throws before any request: "
              "<i>Cannot consume scoped service 'ScopedOp' from singleton 'PriceCache'</i>. <code>Say</code> "
              "prints a label and wraps the text at 62 columns.", keep=True),

        {"type": "chart", "heading": "3.4 · Registrations by lifetime in the API", "kind": "hbar",
         "args": {"data": regs, "labelw": 120, "tone": "teal", "width": 760},
         "caption": "AddSingleton / AddScoped / AddTransient calls (keyed or not), typed AddHttpClient and "
                    "AddHostedService calls in L08.QuoteApi and the VB module · measured at build time",
         "note": "<b>Most services are singletons because the state lives in thread-safe stores.</b> The one "
                 "request-bound unit is <code>QuoteService</code> plus the keyed channels; the typed partner "
                 "client is transient; the hosted dispatcher is a singleton too, which is why it opens a scope per "
                 "message (§8). Counted from the sample source at build time; framework calls such as "
                 "<code>AddOpenApi</code> are not counted. " + MEASURED},

        # ═══════════════════════════ 4 · ENDPOINTS ═══════════════════════════
        {"type": "story", "heading": "4 · Endpoints — minimal APIs, typed results, filters and validation",
         "html": (
             "<p><b>Microsoft recommends minimal APIs for new projects; controllers remain for teams that need "
             "MVC's extension points (" + APIS + ").</b> A minimal API maps a route to a lambda or a static method "
             "with <code>MapGet</code>/<code>MapPost</code>, grouped under a prefix with <code>MapGroup</code>. A "
             "controller is the <code>@RestController</code> you know: an <code>[ApiController]</code> class "
             "mapped by <code>MapControllers()</code>. Both run in one app — this sample has both.</p>"
             "<p><b>Return typed results, because the return type is the contract.</b> "
             "<code>Results&lt;Ok&lt;PolicyResponse&gt;, NotFound, Conflict&lt;ProblemDetails&gt;&gt;</code> is "
             "checked by the compiler, read by the OpenAPI generator (§5) and asserted by unit tests without HTTP. "
             "Endpoint filters are the <code>HandlerInterceptor</code> of minimal APIs: they wrap the handler and "
             "see its bound arguments.</p>"
             "<p><b>.NET 10 validates minimal API arguments from DataAnnotations after one call, "
             "<code>AddValidation()</code>.</b> A source generator finds the types your endpoints bind — records "
             "and nested types included — and an endpoint filter answers 400 with a ValidationProblem. The "
             "generator only discovers types in the assembly where <code>AddValidation</code> is called "
             "(" + WHATSNEW + "); 4.7 shows what that means for a Visual Basic library. A rule that needs a "
             "service — today's date from <code>TimeProvider</code> — stays in your own filter.</p>")},

        pcompare(from_text("""
            @RestController
            @RequestMapping("/quotes")
            class QuoteController(private val service: QuoteService) {

                @PostMapping
                @RateLimiter(name = "quote-writes")
                fun create(@Valid @RequestBody request: QuoteRequest)
                    : ResponseEntity<QuoteResponse> {
                    val quote = service.create(request)
                    return ResponseEntity
                        .created(URI("/quotes/${quote.quoteId}"))
                        .body(quote)
                }

                @GetMapping("/{id}")
                fun get(@PathVariable id: UUID) =
                    service.find(id)?.let { ResponseEntity.ok(it) }
                        ?: ResponseEntity.notFound().build()

                @PostMapping("/{id}/accept")
                fun accept(@PathVariable id: UUID) = service.accept(id)
            }
            """, "kotlin", file="Spring Boot"),
                 from_sample(ENDPOINTS, "map-quotes"),
                 "4.1 · Routes — a Spring controller vs a minimal API route group",
                 "<b>Annotations become method calls on the route.</b> <code>@RequestMapping</code> is "
                 "<code>MapGroup</code>, <code>@PostMapping</code> is <code>MapPost</code>, "
                 "<code>@RateLimiter</code> is <code>RequireRateLimiting</code>. The <code>:guid</code> constraint "
                 "makes a malformed id a 404 before the handler runs. The two <code>Produces…</code> calls document "
                 "responses that filters and middleware produce — §5 shows why they are needed. The handlers "
                 "follow in 4.2."),

        pcode(from_sample(ENDPOINTS, "handlers"), "4.2 · Handlers that return typed results",
              "<b>Parameters are bound by type and source:</b> <code>Guid id</code> from the route, "
              "<code>QuoteRequest</code> from the JSON body, <code>QuoteService</code> from the request scope. "
              "<code>Accept</code> maps a domain outcome to three HTTP results with a switch expression; its union "
              "return type is what makes the OpenAPI document list 200, 404 and 409."),

        pcode(from_sample(CONTRACTS, "contracts"), "4.3 · Request contracts validated by AddValidation",
              "<b>Bean Validation annotations, in attribute form, on positional records.</b> "
              "<code>[AllowedValues]</code> and <code>[Range(typeof(decimal), …)]</code> come from "
              "<code>System.ComponentModel.DataAnnotations</code>; nested records are validated too, so the tour's "
              "invalid body gets 400 with errors for <code>Vehicle.SumInsured</code> and <code>NotifyVia</code>. "
              "These are wire contracts, not the MotorQuote domain types: <code>SumInsured</code> is a plain "
              "amount because the currency comes from <code>QuoteOptions</code>, and responses convert back to "
              "<code>Money</code>."),

        pcode(from_sample(ENDPOINTS, "endpoint-filter"), "4.4 · An endpoint filter for a rule that needs a service",
              "<b>A filter is middleware that knows the endpoint's arguments.</b> "
              "<code>GetArgument&lt;QuoteRequest&gt;(0)</code> reads the bound body; returning a result "
              "short-circuits the handler, calling <code>next</code> continues. The clock is injected "
              "<code>TimeProvider</code>, so tests fix the date with <code>FakeTimeProvider</code> — " + ref(5) + "."),

        pcode(from_sample(PARTNERS, "controller"), "4.5 · The controller you know — an [ApiController]",
              "<b>Attribute for attribute, this is <code>@RestController</code>.</b> <code>[ApiController]</code> "
              "requires attribute routing, infers binding sources (<code>partnerId</code> from the route, a "
              "complex type from the body) and answers invalid model state with an automatic 400 "
              "ValidationProblem (" + WEBAPI + "). <code>ActionResult&lt;PartnerRate&gt;</code> returns the value or "
              "any result. <code>[ProducesResponseType]</code> declares only 200, so the OpenAPI document lists "
              "only 200; the 503 that §5's exception handler writes for this route is missing (5.1)."),

        figure_heading("4.6 · Minimal API or controller?"),
        {"type": "twocol", "boxes": [
            {"heading": "Start with a minimal API when", "tone": "teal",
             "items": ["The service is new — it is Microsoft's recommended default (" + APIS + ")",
                       "Endpoints are thin and the logic lives in services, as it should in a microservice",
                       "You want typed results and endpoint filters without the MVC filter stack",
                       "You may publish with Native AOT later — " + ref(12)]},
            {"heading": "Keep or choose a controller when", "tone": "indigo",
             "items": ["You need custom model binders (<code>IModelBinder</code>) or <code>IModelValidator</code>",
                       "You rely on application parts, the application model or OData",
                       "A large existing MVC codebase already has conventions and filters that work",
                       "Its responses are documented by attributes such as <code>[ProducesResponseType]</code>, "
                       "as <code>PartnersController</code> in 4.5 is"]}]},

        pcode(from_sample(VB_MODULE, "tariff-endpoint"), "4.7 · A minimal API endpoint written in Visual Basic",
              "<b>Endpoints are just extension methods on <code>IEndpointRouteBuilder</code>, so a VB library can "
              "contribute them.</b> The C# host calls <code>app.MapTariff().CacheOutput()</code>. The VB lambda "
              "binds <code>coverage</code> from the route and <code>PremiumCalculator</code> from DI exactly as a "
              "C# handler would. Validation follows only half-way. <code>AddValidation</code>'s filter runs on "
              "every endpoint, so DataAnnotations on a VB handler's <i>parameters</i> are enforced; but its source "
              "generator sees only types declared in the assembly that calls it — the C# host — so attributes on a "
              "request <i>class</i> written in VB are silently ignored and the request gets 200 (" + VALIDATION +
              "). Declare request DTOs in C#, or validate VB types explicitly. "
              "<code>ValidationScopeTests</code> pins both behaviours against VB endpoints in "
              "<code>ValidationScope.vb</code>."),

        {"type": "mermaid", "inline": True,
         "heading": "4.8 · POST /quotes through middleware, filters and the VB calculator",
         "caption": "solid arrows = calls · dashed arrows = returns · each 400 or 429 short-circuits the rest",
         "code": ('%%{init: {"theme":"base","themeVariables": {"actorBkg":"#E0E7FF","actorBorder":"#4338CA",'
                  '"actorTextColor":"#1f2937","signalColor":"#334155","signalTextColor":"#1f2937",'
                  '"noteBkgColor":"#FEF3C7","noteBorderColor":"#D97706","noteTextColor":"#1f2937",'
                  '"labelBoxBkgColor":"#F8FAFC","labelTextColor":"#1f2937","sequenceNumberColor":"#ffffff"}}}%%\n'
                  "sequenceDiagram\n"
                  "  autonumber\n"
                  "  participant C as Client\n"
                  "  participant M as Middleware\n"
                  "  participant F as Endpoint filters\n"
                  "  participant H as Handler, QuoteService\n"
                  "  participant R as VB calculator\n"
                  "  C->>M: POST /quotes\n"
                  "  M-->>C: 429 when quote-writes is full\n"
                  "  M->>F: endpoint matched, body bound\n"
                  "  F-->>C: 400 if an attribute fails\n"
                  "  F-->>C: 400 if StartDate is out of range\n"
                  "  F->>H: next(context)\n"
                  "  H->>R: Calculate(RatingInput)\n"
                  "  R-->>H: PremiumBreakdown\n"
                  "  H-->>C: 201 Created with Location\n")},

        # ═══════════════════════════ 5 · OPENAPI & ERRORS ═══════════════════════════
        {"type": "story", "heading": "5 · OpenAPI and ProblemDetails — a contract that tells the truth",
         "html": (
             "<p><b>OpenAPI generation is built in: <code>AddOpenApi()</code> and <code>MapOpenApi()</code>, and "
             ".NET 10 emits OpenAPI 3.1 using Microsoft.OpenApi 2.0 (" + WHATSNEW + ").</b> Swashbuckle was "
             "removed from the web API template in .NET 9 (" + SWASH + "). The template maps only the JSON "
             "document, only in Development (" + OPENAPI + "); a browsing UI is a package you choose, as "
             "swagger-ui was with springdoc. The sample's document reports <code>3.1.1</code>.</p>"
             "<p><b>The document lists only the status codes something declared.</b> Typed results declare their "
             "own; <code>Produces…</code> calls and <code>[ProducesResponseType]</code> declare the rest. What "
             "middleware, exception handlers and filters return appears nowhere unless you say so — chart 5.1 "
             "compares what the tour received with what the document promises.</p>"
             "<p><b>Errors become RFC 9457 ProblemDetails when three things are registered.</b> "
             "<code>AddProblemDetails()</code>, <code>UseExceptionHandler()</code> and "
             "<code>UseStatusCodePages()</code> turn unhandled exceptions and empty 4xx/5xx responses into "
             "<code>application/problem+json</code> (" + ERRORS + "). <code>IExceptionHandler</code> is your "
             "<code>@ControllerAdvice</code>: handlers are singletons, called in registration order until one "
             "returns true (" + EXHANDLER + "). Since .NET 10 the middleware no longer logs an exception a handler "
             "reports as handled, so log it in the handler.</p>")},

        {"type": "chart", "heading": "5.1 · Status codes per operation — documented vs received in the tour",
         "kind": "heatmap",
         "args": {"rows": ops, "cols": codes, "matrix": matrix, "cell": 44, "tone": "amber",
                  "fmt": lambda v: _CELL[int(v)]},
         "caption": "ok = in /openapi/v1.json and received · doc = documented, not triggered by the tour · GAP = "
                    "received but not documented · blank = neither · parsed from the tour output in 9.2, measured "
                    "on the build machine",
         "note": ("<b>A GAP cell is a response a generated client does not expect.</b> "
                  + " · ".join(f"<i>{esc(op)}</i> returned {', '.join(cs)}, which its entry does not list"
                               for op, cs in gaps)
                  + " — the 503 comes from <code>PartnerExceptionHandler</code>, which no attribute declares. "
                  + "A doc cell is only a gap in the tour: "
                  + " · ".join(f"<i>{esc(op)}</i> documents {', '.join(cs)}, which the tour never triggered"
                               for op, cs in unseen.items() if cs)
                  + ". The POST /quotes row is all ok only because 4.1 adds <code>ProducesValidationProblem()</code> "
                    "and <code>ProducesProblem(429)</code>. " + MEASURED)},

        {"type": "table", "heading": "5.2 · Who writes each error response in the sample",
         "cols": ["Status", "Produced by", "Body", "In the OpenAPI document"],
         "rows": [
             ["400", "<code>AddValidation</code> filter, or <code>StartDateFilter</code>",
              "ValidationProblem with <code>errors</code> per field", "yes — <code>ProducesValidationProblem()</code>"],
             ["404", "<code>TypedResults.NotFound()</code>, or a malformed <code>{id:guid}</code>",
              "empty result → <code>UseStatusCodePages</code> writes problem+json", "yes — from the union return type"],
             ["409", "<code>TypedResults.Conflict(new ProblemDetails …)</code>", "the ProblemDetails you built",
              "yes — from the union return type"],
             ["429", "rate limiter middleware, <code>RejectionStatusCode = 429</code>",
              "no body → <code>UseStatusCodePages</code> writes problem+json (test)", "only via <code>ProducesProblem(429)</code>"],
             ["503", "<code>PartnerExceptionHandler</code>", "ProblemDetails + <code>partnerId</code>, "
              "<code>Retry-After: 30</code>", pill("no — nothing declares it", "amber")],
             ["500", "unhandled exception no handler claims", "ProblemDetails from <code>UseExceptionHandler</code>",
              pill("no — nothing declares it", "amber")]]},

        pcode(from_sample(CROSS, "exception-handler"), "5.3 · An IExceptionHandler that maps a partner outage to 503",
              "<b>Return false for exceptions that are not yours.</b> The next handler, then the middleware's "
              "default 500 ProblemDetails, takes over. <code>IProblemDetailsService</code> writes the body, so the "
              "503 carries the same shape as every other error plus a <code>partnerId</code> extension and a "
              "<code>Retry-After</code> header (asserted in the partner test). The explicit "
              "<code>LogWarning</code> exists because .NET 10 stopped logging handled exceptions; its template "
              "keeps <code>PartnerId</code> and <code>Reason</code> as properties you can filter on (§2)."),

        # ═══════════════════════════ 6 · CROSS-CUTTING ═══════════════════════════
        {"type": "story", "heading": "6 · Cross-cutting middleware — decide the defaults",
         "html": (
             "<p><b>What a Spring service gets from Actuator, Resilience4j and the API gateway ships inside "
             "ASP.NET Core as a service registration, a middleware and endpoint metadata.</b> "
             "<code>AddRateLimiter</code> / <code>UseRateLimiter</code> / <code>RequireRateLimiting</code>; "
             "<code>AddOutputCache</code> / <code>UseOutputCache</code> / <code>CacheOutput</code>; "
             "<code>AddHealthChecks</code> / <code>MapHealthChecks</code>. The registration defines policies, the "
             "middleware enforces them, the endpoint opts in. CORS works the same way and holds no surprise for a "
             "Spring or NestJS engineer: <code>AddCors</code> defines the <code>broker-portal</code> policy and "
             "<code>UseCors(\"broker-portal\")</code> answers the preflight for that one origin only (a test "
             "proves it).</p>"
             "<p><b>Three defaults need an explicit decision before production.</b> The rate limiter rejects "
             "with 503, which clients and dashboards read as an outage (" + REJECT + "). A Degraded health check "
             "still returns 200, so a load balancer keeps sending traffic (" + HEALTH + "). The output cache "
             "lives in process memory, so two ECS tasks hold two different caches (" + OUTPUT + ").</p>"
             "<p><b>Order is part of the configuration.</b> <code>UseOutputCache</code> goes after "
             "<code>UseCors</code> and after authentication, or cached responses bypass them; a rate limiter "
             "that reads endpoint policies must run after routing (" + RATELIMIT + ") — "
             "<code>WebApplication</code>'s implicit <code>UseRouting</code> guarantees that unless you move it. "
             "Authentication and authorization middleware belong to " + ref(11) + ".</p>")},

        {"type": "cards",
         "band": {"title": "6.1 · Three features whose defaults need a decision", "note": "L08.QuoteApi",
                  "tone": "teal"},
         "cards": cross_cards},

        pcode(from_sample(CROSS, "rate-limits"), "6.2 · A rate-limit policy that reads validated options",
              "<b>The limit is configuration, validated at start-up like any other option.</b> The policy "
              "partitions by client IP with a fixed one-minute window and no queue, and resolves "
              "<code>IOptions&lt;RateLimitOptions&gt;</code> from the request's services. The test factory sets "
              "the limit to 2 to prove the third write gets 429 with a problem+json body."),

        # ═══════════════════════════ 7 · PARTNERS ═══════════════════════════
        {"type": "story", "heading": "7 · Calling ~30 rating partners — HttpClientFactory and resilience",
         "html": (
             "<p><b><code>IHttpClientFactory</code> owns connection pooling and handler lifetimes; a typed client "
             "wraps it for one partner API.</b> <code>AddHttpClient&lt;IPartnerRateClient, "
             "PartnerRateClient&gt;</code> registers the client as transient and gives it an "
             "<code>HttpClient</code> whose handler is pooled and recycled every two minutes by default, so DNS "
             "changes are picked up (" + HCF + "). Store the client in a singleton and that recycling stops "
             "working.</p>"
             "<p><b>Microsoft.Extensions.Http.Resilience, built on Polly, is Resilience4j as one call: "
             "<code>AddStandardResilienceHandler()</code>.</b> It stacks five strategies in a fixed order with the "
             "defaults in table 7.1 and handles 5xx, 408 and 429 responses, <code>HttpRequestException</code> and "
             "<code>TimeoutRejectedException</code> (" + RESIL + "). Its options bind from configuration, so each "
             "partner can get its own section instead of its own code.</p>"
             "<p><b>Two defaults bite an insurance integration.</b> The handler retries <i>every</i> HTTP method: "
             "a POST that binds cover at a partner can be sent four times, so call "
             "<code>DisableForUnsafeHttpMethods()</code> — the lab's POST makes one attempt. And the circuit "
             "breaker needs at least 100 calls in its 30-second window before it can open, so a low-volume "
             "partner never trips it; the lab lowers the minimum to 2 and the circuit opens after two failed "
             "attempts. The options are validated too: a sampling duration shorter than twice the attempt timeout "
             "is rejected when the client is created.</p>")},

        {"type": "table", "heading": "7.1 · The standard resilience handler, outermost strategy first",
         "cols": ["#", "Strategy", "Default", "Resilience4j analogue (estimate)", "L08.QuoteApi"],
         "rows": [
             ["1", "Rate limiter", "1,000 concurrent permits, queue 0", "Bulkhead", "default"],
             ["2", "Total request timeout", "30 s, retries included", "TimeLimiter around the retry", "default"],
             ["3", "Retry", "3 retries · exponential · jitter · 2 s base delay", "Retry",
              "<code>MaxRetryAttempts: 3</code>; tests shorten the delay to 10 ms"],
             ["4", "Circuit breaker", "10% failures · min 100 calls · 30 s sampling · 5 s break", "CircuitBreaker",
              "<code>SamplingDuration: 00:00:30</code>"],
             ["5", "Attempt timeout", "10 s per attempt", "TimeLimiter per call", "<code>Timeout: 00:00:05</code>"],
             ["", "Source", VERIFIED + " " + RESIL, "", "from <code>appsettings.json</code>"]]},

        pcode(from_sample(PARTNERS, "partner-registration"), "7.2 · Registering the typed client and its pipeline",
              "<b>Options feed the client; configuration feeds the resilience pipeline.</b> The base address "
              "comes from validated <code>PartnerOptions</code>; <code>AddStandardResilienceHandler</code> binds "
              "<code>Partners:Resilience</code>, so retry count and timeouts change per environment without a "
              "rebuild. Tests replace only the primary handler, keeping the real pipeline in front of it. "
              "<code>IPartnerRateClient</code> plays the part of " + ref(5) + "'s <code>IPartnerRateProvider</code>, "
              "with one difference: a single typed client serves every partner by id, where lesson 05 had one "
              "provider per partner."),

        pcode(from_sample(PARTNERS, "typed-client"), "7.3 · The typed client — retries happen below this code",
              "<b>By the time an exception reaches the <code>catch</code>, the pipeline has already retried.</b> "
              "<code>HttpRequestException</code> means the partner kept failing; "
              "<code>ExecutionRejectedException</code> covers an open circuit and Polly timeouts. The client "
              "records health and throws a domain exception, which 5.3 turns into 503."),

        {"type": "mermaid", "inline": True,
         "heading": "7.4 · Circuit breaker states with the standard defaults",
         "caption": "green = calls flow · red = calls throw BrokenCircuitException without reaching the partner · "
                    "amber = one probe call decides · thresholds are the standard handler's defaults",
         "code": ('%%{init: {"themeVariables": {"fontSize": "11px"}}}%%\n'
                  "stateDiagram-v2\n"
                  "  direction LR\n"
                  "  [*] --> Closed\n"
                  "  Closed --> Open: ≥10% failed, ≥100 calls in 30 s\n"
                  "  Open --> HalfOpen: 5 s break over\n"
                  "  HalfOpen --> Closed: probe OK\n"
                  "  HalfOpen --> Open: probe failed\n"
                  "  classDef closed fill:#bbf7d0,color:#1f2937,stroke:#16a34a\n"
                  "  classDef open fill:#fecaca,color:#1f2937,stroke:#dc2626\n"
                  "  classDef half fill:#fde68a,color:#1f2937,stroke:#d97706\n"
                  "  class Closed closed\n"
                  "  class Open open\n"
                  "  class HalfOpen half\n")},

        pcompare(from_sample(PLAB, "unsafe-methods"), from_sample(PLAB, "early-breaker"),
                 "7.5 · Configuring the handler — no retried POST, an early circuit breaker",
                 "<b>Every strategy in table 7.1 is an options object you can change in code or bind from "
                 "configuration.</b> Left: <code>DisableForUnsafeHttpMethods()</code> keeps retries for GET but gives "
                 "POST, PUT, PATCH and DELETE a single attempt. Right: <code>MinimumThroughput = 2</code> and "
                 "<code>FailureRatio = 0.5</code> let the breaker open after two failed calls instead of waiting for "
                 "100 calls in 30 s. Both lab clients shorten <code>Retry.Delay</code> and switch off jitter so "
                 "the lab runs in milliseconds and prints the same counts every time."),

        {"type": "chart", "heading": "7.6 · Partner attempts per scenario in L08.PartnerLab", "kind": "hbar",
         "args": {"data": [(name, n) for name, n, _ in attempts], "labelw": 290, "tone": "amber", "width": 760},
         "caption": "HTTP attempts that reached the fake partner · outcome in 7.7 · measured from the captured output",
         "note": "<b>Four attempts is the ceiling of a default retry, one is what an unsafe method gets, and zero is "
                 "an open circuit.</b> The failing GET is tried 1 + 3 times and still ends in 503; the POST with "
                 "<code>DisableForUnsafeHttpMethods</code> is tried once; after two failures the lab's circuit "
                 "(minimum throughput 2) rejects the next calls without touching the partner (" + POLLY + "). "
                 + MEASURED},

        pcode(captured(PARTNER_OUT, "Output — L08.PartnerLab"), "7.7 · What the partner lab prints",
              "<b>The last three lines are a validation failure, not a crash.</b> The lab configures a 20 s "
              "attempt timeout with a 30 s sampling duration; the options validator rejects it the first time "
              "<code>CreateClient</code> builds the pipeline. Validate these values in tests, not in production."),

        # ═══════════════════════════ 8 · BACKGROUND ═══════════════════════════
        {"type": "story", "heading": "8 · Background work — hosted services",
         "html": (
             "<p><b><code>BackgroundService</code> is the long-running worker you wrote with "
             "<code>@Scheduled</code> or a queue consumer, hosted in the API process.</b> Register it with "
             "<code>AddHostedService&lt;T&gt;()</code>; the host calls <code>ExecuteAsync</code> at start-up and "
             "cancels its token at shutdown. Since .NET 10 the whole of <code>ExecuteAsync</code> runs in the "
             "background; before, the code ahead of the first <code>await</code> blocked start-up (" + BG10 + ").</p>"
             "<p><b>A hosted service is a singleton, so it creates a scope for each unit of work.</b> The "
             "dispatcher reads <code>QuoteAccepted</code> messages from a bounded channel, the type you met in "
             + ref(5) + ", opens a scope, resolves the keyed channel the customer chose and sends. Injecting a "
             "scoped service into its constructor is the captive dependency of §3.</p>"
             "<p><b>An exception that escapes <code>ExecuteAsync</code> stops the whole host — the default since "
             ".NET 6 (" + BG6 + ").</b> One bad message would take the API down, so the loop catches per message "
             "and logs. An in-memory channel loses work in two ways: when it is full, <code>TryWrite</code> "
             "returns false and the message is refused, so <code>QuoteService</code> checks the result and logs a "
             "warning; and whatever is queued is gone when the process stops. For work that must survive a "
             "deployment, publish to a durable queue such as SQS — " + ref(12) + ".</p>")},

        {"type": "mermaid", "inline": True,
         "heading": "8.1 · Accepting a quote returns before the notification is sent",
         "caption": "Accept handler = request scope · Queue = NotificationQueue singleton · Dispatcher = hosted "
                    "NotificationDispatcher · LineChannel = keyed, scoped · the client never waits for the send",
         "code": ('%%{init: {"theme":"base","themeVariables": {"actorBkg":"#CCFBF1","actorBorder":"#0F766E",'
                  '"actorTextColor":"#1f2937","signalColor":"#334155","signalTextColor":"#1f2937",'
                  '"noteBkgColor":"#FEF3C7","noteBorderColor":"#D97706","noteTextColor":"#1f2937"}}}%%\n'
                  "sequenceDiagram\n"
                  "  participant C as Client\n"
                  "  participant A as Accept handler\n"
                  "  participant Q as Queue\n"
                  "  participant D as Dispatcher\n"
                  "  participant K as LineChannel\n"
                  "  C->>A: POST /quotes/id/accept\n"
                  "  A->>Q: TryEnqueue(QuoteAccepted)\n"
                  "  A-->>C: 200 with the policy number\n"
                  "  Q->>D: ReadAllAsync yields the message\n"
                  "  Note over D: CreateAsyncScope()\n"
                  "  D->>K: SendAsync via GetRequiredKeyedService\n"
                  "  K-->>D: sent, scope disposed\n"
                  "  Note over D: any failure is caught<br/>and logged here\n")},

        pcode(from_sample(NOTIFY, "background-service"), "8.2 · The notification dispatcher",
              "<b>The <code>try</code> wraps the whole unit of work, and the filter asks the stopping token, not "
              "the exception type.</b> <code>ReadAllAsync(stoppingToken)</code> ends the loop at shutdown; "
              "<code>CreateAsyncScope()</code> gives each message fresh scoped services and disposes them "
              "asynchronously. Resolving the channel sits inside the <code>try</code> because an unknown key "
              "throws there. And <code>when (ex is not OperationCanceledException)</code> would be wrong: a gateway "
              "call that hits <code>HttpClient.Timeout</code> throws <code>TaskCanceledException</code>, which is "
              "an <code>OperationCanceledException</code>, so it would escape and stop the host. "
              "<code>DispatcherTests</code> sends both failures, then a good message, and asserts that it is sent "
              "and <code>/health</code> still answers."),

        pcode(from_sample(NOTIFY, "keyed-services"), "8.3 · Keyed channels and the hosted service",
              "<b>The key is data from the request.</b> The customer's <code>notifyVia</code> value "
              "(<code>sms</code>, <code>email</code> or <code>line</code>) travels in the message and selects the "
              "keyed registration. The queue and the log are singletons because they are shared between request "
              "threads and the dispatcher."),

        # ═══════════════════════════ 9 · HANDS-ON ═══════════════════════════
        {"type": "story", "heading": "9 · Hands-on — run the API in memory and test it the same way",
         "html": (
             f"<p><b>{n_proj} projects, one command to prove them, and a tour that prints what a client sees.</b> "
             "<code>L08.ApiTour</code> boots <code>L08.QuoteApi</code> on the in-memory test server with a fake "
             "clock and a fake partner and prints the status codes, bodies and OpenAPI operations a client sees. "
             "<code>L08.HostingLab</code> and <code>L08.PartnerLab</code> are the labs behind 2.5, 3.1, 3.3 and "
             "7.5–7.7.</p>"
             "<p><b>This lesson's own tests reach the API through "
             "<code>WebApplicationFactory&lt;Program&gt;</code>, the type that hosts the real "
             "<code>Program</code> and the real pipeline in memory.</b> That is all §9 uses it for — proving these "
             "endpoints, the rate limiter and the resilience handler without a port — and 9.3 shows the two seams it "
             "opens. Integration and API testing as a craft (what to double, how much to cover, driving an endpoint "
             "test-first) is " + ref(10) + ".</p>"
             f"<p><b>Visual Basic has no ASP.NET Core project templates, but a VB library can carry web code.</b> "
             f"Of the {n_templates} web-tagged templates in SDK 10.0.401, {vb_templates} offer VB, and all of them "
             "are test projects. <code>L08.Rating.Vb</code> references the <code>Microsoft.AspNetCore.App</code> "
             "shared framework, registers its options and maps <code>/tariff</code>; the whole VB library, rating "
             f"rules included, is {loc_vb} lines, and the C# host owns <code>Program.cs</code>. How far VB goes in a legacy estate is " + ref(6) + ".</p>")},

        pcode(from_text("""
            # from the repository root, with the .NET 10 SDK first on PATH
            dotnet run --project lesson-08-aspnet-core-web-apis/samples/L08.ApiTour
            dotnet run --project lesson-08-aspnet-core-web-apis/samples/L08.HostingLab
            dotnet run --project lesson-08-aspnet-core-web-apis/samples/L08.PartnerLab
            dotnet test lesson-08-aspnet-core-web-apis/samples/L08.QuoteApi.Tests
            # build, test and run every lesson-08 sample
            python 0-script/verify_samples.py --only 8
            # the web templates and the languages they offer
            dotnet new list --tag Web
            """, "shell"), "9.1 · Commands",
              "<b>No server to start.</b> The tour and the tests host the API in memory, so the commands work in "
              "CI without ports or network. <code>verify_samples.py</code> builds the web project, runs the tests "
              "and runs each console app to completion."),

        pcode(captured(TOUR_OUT, "Output — L08.ApiTour"), "9.2 · What you should see",
              "<b>Every line is one real request through the full pipeline.</b> The totals come from the VB "
              "calculator on the track's canonical tariff — illustrative rates, not a real one. Both quotes are "
              "Class 1 on 800,000 THB (base 2.1% = 16,800): the claim-free 36-year-old with ten licence years takes "
              "the 50% no-claim discount to a net 8,400.00 and a total of 9,023.95, and the 22-year-old with one "
              "claim takes +20% young driver and +10% claims to 21,840.00 and 23,462.28, with no discount because a "
              "claim resets it. Three claims in five years is declined, not priced: this API teaches data, not "
              "exceptions, so it stores that outcome as <code>QuoteStatus.Declined</code> and still answers 201. "
              "The 5th write in the minute gets 429 as problem+json; the partner that fails twice succeeds on the "
              "third attempt; the one that always fails ends in 503 with <code>Retry-After</code> and turns "
              "<code>/health</code> Degraded — still 200. The indented lines are the OpenAPI operations counted in "
              "5.1; the last line is written by the background dispatcher.", keep=False),

        pcode(from_sample(FACTORY, "factory"), "9.3 · The test factory — the real Program with two seams",
              "<b>Configuration first, then services.</b> The factory boots <code>Program.cs</code> on a "
              "<code>TestServer</code> — no port, no network — and would default to Development if it named no "
              "environment (" + ITEST + "). <code>UseSetting</code> overrides a configuration key, which is how the "
              "rate-limit test lowers the limit to 2; <code>ConfigureTestServices</code> runs after "
              "<code>Program.cs</code>, so its fake clock and fake partner handler win. Scope validation is on "
              "explicitly because the environment is Testing, not Development. This is the seam, not a testing "
              "curriculum: " + ref(10) + " designs the suite that uses it.", keep=False),

        {"type": "chartrow", "charts": [
            {"heading": "9.4 · Lesson 08 tests by area", "kind": "hbar",
             "args": {"data": tests_by_area(), "labelw": 110, "tone": "indigo", "width": 390},
             "caption": "[Fact] methods plus [InlineData] rows per test file · measured at build time",
             "note": f"<b>{n_tests} tests, most of them real HTTP calls through the full pipeline.</b> Endpoint "
                     "tests share one factory; resilience tests build one each so partner attempt counters start "
                     "at zero. " + MEASURED},
            {"heading": "9.5 · Web-tagged SDK templates by language", "kind": "bar",
             "args": {"data": by_lang, "ylabel": "templates", "tone": "blue", "width": 390, "height": 150},
             "caption": "dotnet new list --tag Web on SDK 10.0.401 · measured from the captured list",
             "note": f"<b>C# owns web development; VB appears on {vb_templates} templates, all test projects.</b> "
                     "A VB web API means a C# host plus VB libraries, as here. " + MEASURED}]},

        {"type": "callout", "variant": "warn", "heading": "⚠ Traps for a Spring, NestJS or Express engineer",
         "items": [
             "<b>“Scoped beans are checked by the framework.”</b> Only in Development. A singleton that takes a "
             "scoped service starts fine in Staging and Production and shares one instance across every request "
             "(3.3). Turn <code>ValidateScopes</code> and <code>ValidateOnBuild</code> on in your test factory.",
             "<b>“Retries are safe to switch on.”</b> The standard resilience handler retries POST, PUT and DELETE "
             "too. Against a partner that binds cover or issues a policy, call "
             "<code>DisableForUnsafeHttpMethods()</code> or make the partner call idempotent (7.5).",
             "<b>“A rejected request is a 429 and a Degraded check is a failure.”</b> The defaults are 503 and "
             "200. Set <code>RejectionStatusCode</code>, and map health statuses to what your load balancer and "
             "ECS health checks should act on (§6).",
             "<b>“A background job that throws just logs.”</b> An exception escaping "
             "<code>ExecuteAsync</code> stops the host and every endpoint. Catch per unit of work and let only the "
             "stopping token end the loop: an HTTP timeout is a cancellation exception too (8.2).",
             "<b>“The OpenAPI document describes the API.”</b> It describes what was declared. The tour's 503 "
             "is missing from the document; add <code>Produces…</code> metadata for every code middleware and "
             "handlers can return (5.1)."]},

        {"type": "callout", "variant": "ok", "heading": "✔ Checkpoint — you are ready for lesson 09 when",
         "items": [
             f"<code>python 0-script/verify_samples.py --only 8</code> reports {n_proj}/{n_proj} passed, including "
             f"the {n_tests} API tests.",
             "You can read <code>Program.cs</code> aloud as diagram 2.1: which middleware runs first, where routing "
             "happens and which endpoints opt into rate limiting and caching.",
             "You can give every registration in 2.6 and 8.3 its lifetime and explain the two <code>#3</code> ids in "
             "3.3.",
             "You can explain each status code in 9.2 by naming the component in table 5.2 that produced it.",
             "You can configure the standard resilience handler for a partner whose POST must not be retried, and "
             "say when its circuit breaker can open."]},

        {"type": "callout", "variant": "summary", "heading": "🔍 Check yourself",
         "items": [
             "A service maps endpoints and calls <code>UseRateLimiter()</code> but never <code>UseRouting()</code>. "
             "Does an endpoint's <code>RequireRateLimiting</code> policy apply, and why?",
             "Which configuration source wins when <code>appsettings.Production.json</code>, an environment "
             "variable and a command-line argument all set <code>Quotes:ValidityDays</code>?",
             "In which environment does ASP.NET Core reject a scoped service injected into a singleton, and what "
             "happens elsewhere?",
             "What must an endpoint return or declare for its 400, 404, 409 and 429 responses to appear in the "
             "OpenAPI document?",
             "Name the five strategies of the standard resilience handler in order, and the default number of "
             "calls before its circuit breaker can open.",
             "What status does the rate limiter send by default, and what does <code>/health</code> return when a "
             "check is Degraded?",
             "What happens to the API when an exception escapes <code>BackgroundService.ExecuteAsync</code>, and "
             "how does the dispatcher prevent it?"]},

        {"type": "footer",
         "html": ("<b>Lesson 08 in one line:</b> an ASP.NET Core API is declared, not discovered — explicit lifetimes, "
                  "middleware in line order behind an implicit <code>UseRouting</code>, typed results with .NET 10 "
                  "validation, an OpenAPI 3.1 document that lists only what you declare, a resilience handler that "
                  "retries every method, and hosted services that never let an exception escape. "
                  "<br/><b>Next:</b> " + ref(9) + " — the same quotes and policies in a real database: a "
                  "<code>DbContext</code>, migrations and the SQL EF Core generates, built in projects of its own.")},
    ]


