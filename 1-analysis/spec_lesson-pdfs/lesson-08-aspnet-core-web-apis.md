# Unit spec — lesson-08-aspnet-core-web-apis.pdf

Built to `_standard.md`. Content module `0-script/lessons/lesson_08.py`. Samples
`lesson-08-aspnet-core-web-apis/samples/`. Plan: `_curriculum.md` § "08 · ASP.NET Core Web APIs".

## 1 · Purpose

Show a Spring Boot / NestJS / Express architect how an ASP.NET Core 10 web API is put together and where its
defaults differ from what they already ship: hosting, the middleware pipeline, configuration and options, `ILogger`,
DI lifetimes and the captive dependency, minimal APIs and controllers, typed results, filters and .NET 10
validation, OpenAPI 3.1 and ProblemDetails, rate limiting / output caching / health checks / CORS, calling ~30
rating partners through `IHttpClientFactory` and the standard resilience handler, hosted background work, and
in-memory API tests with `WebApplicationFactory`. The MotorQuote API prices quotes with Visual Basic rating rules
(illustrative rates). Request DTOs are wire contracts and deliberately differ from lesson 03's domain records
(`SumInsured` is a plain amount; `IPartnerRateClient` plays lesson 05's `IPartnerRateProvider`).

## 2 · Ownership & cadence

Owner **claude**, regenerable. Re-verify every November (new ASP.NET Core major): the OpenAPI version and
Microsoft.OpenApi version (§5), the `AddValidation` generator scope and its behaviour on VB endpoints (§4, pinned by
`ValidationScopeTests`), the exception-handler logging change (§5), the standard resilience handler defaults
(table 7.1), the `BackgroundService` behaviour and the host-stops-on-exception default (§8), the IIS in-process
hosting default (2.4) and the generated `public partial class Program` (§9). Re-capture the four pasted outputs (see
§4) whenever a lab or the tour changes what it prints, and the `dotnet new list --tag Web` list when the SDK band
changes.

## 3 · Structure

Rendered: **20 A4 pages**; every page is at least 74 % filled (the last page is 96 % full).

| Page(s) | § | Heading | Blocks |
|---|---|---|---|
| 1 | — | Contents | `toc` depth 2 |
| 1–2 | 1 | Why this lesson — the service you have built many times, rebuilt in .NET | story · `kpi` 1.1 (5 tiles) · `legend` (architecture tag only, the one tag the lesson uses) · info callout "Before you start" |
| 2–5 | 2 | Hosting, configuration and options | story (hosting, middleware order, configuration + options, `ILogger`) · mermaid 2.1 flowchart (request pipeline, numbered in run order) · code 2.2 (Program.cs services) · compare 2.3 (Express ↔ C# `pipeline`) · mapping 2.4 (18 rows) · compare 2.5 (C# `config-precedence` ↔ captured lab output parts 1–2) · compare 2.6 (C# `AddQuoteModule` ↔ VB `AddMotorRating`) |
| 6–7 | 3 | Dependency injection — lifetimes are a design decision | story · compare 3.1 (C# `lifetimes` ↔ captured lab output parts 3–5) · table 3.2 (lifetimes, 3 rows) · code 3.3 (`captive`, kept whole) · chart 3.4 hbar (registrations by lifetime) |
| 7–10 | 4 | Endpoints — minimal APIs, typed results, filters and validation | story · compare 4.1 (Kotlin Spring controller ↔ C# `map-quotes`) · code 4.2 (typed-result handlers) · code 4.3 (DataAnnotations contracts) · code 4.4 (endpoint filter) · code 4.5 (`[ApiController]` `PartnersController`) · twocol 4.6 (minimal API vs controller) · code 4.7 (VB minimal API endpoint) · mermaid 4.8 sequence (POST /quotes) |
| 11–12 | 5 | OpenAPI and ProblemDetails — a contract that tells the truth | story · chart 5.1 heatmap (operations × status codes: documented / received / gap) · table 5.2 (who writes each error, 6 rows) · code 5.3 (`IExceptionHandler`) |
| 12–13 | 6 | Cross-cutting middleware — decide the defaults | story (CORS in prose) · cards 6.1 (one band, 3 cards: rate limiting, output caching, health checks) · code 6.2 (rate-limit policy) |
| 13–16 | 7 | Calling ~30 rating partners — HttpClientFactory and resilience | story · table 7.1 (standard resilience handler, 5 strategies + source row) · code 7.2 (typed client registration) · code 7.3 (typed client) · mermaid 7.4 stateDiagram (circuit breaker) · compare 7.5 (C# `unsafe-methods` ↔ `early-breaker`) · chart 7.6 hbar (attempts per lab scenario) · code 7.7 (captured PartnerLab output) |
| 16–18 | 8 | Background work — hosted services | story · mermaid 8.1 sequence (accept → queue → dispatcher → keyed channel) · code 8.2 (`NotificationDispatcher`) · code 8.3 (keyed channels + `AddHostedService`) |
| 18–20 | 9 | Hands-on — run the API in memory and test it the same way | story (incl. the VB note) · code 9.1 commands (ApiTour, HostingLab, PartnerLab, tests, `verify_samples`, template list) · code 9.2 (captured ApiTour output) · compare 9.3 (Kotlin MockMvc ↔ C# `post-test`) · code 9.4 (`QuoteApiFactory`) · chartrow 9.5 hbar (tests by area) + 9.6 bar (web templates by language) · warn "Traps" (5) · ok checkpoint (5) · summary "Check yourself" (7) · footer (Next: lesson 09) |

Counts: 9 numbered stories · 1 mapping (18 rows) · 1 cards band (3 cards) · 4 mermaid (flowchart, 2 ×
sequenceDiagram, stateDiagram-v2) · 5 charts (3.4, 5.1, 7.6, 9.5, 9.6) · 24 code panels (17 single, 7 compares) ·
C# ↔ VB compare 2.6 · TypeScript ↔ C# compare 2.3 · Kotlin ↔ C# compares 4.1 and 9.3 · twocol 4.6 · 3 extra tables
(3.2, 5.2, 7.1) · 24 distinct links.

## 4 · Derivation

- **KPI "OpenAPI version emitted 3.1"** — VERIFIED (What's new in ASP.NET Core in .NET 10: default OpenAPI version
  3.1, Microsoft.OpenApi 2.0.0); the sub-line "sample serves 3.1.1" is MEASURED from the tour output.
- **KPI "Retries, standard handler 3"** and **table 7.1** — VERIFIED (Build resilient HTTP apps: order, defaults,
  handled status codes/exceptions, retries for all methods, `DisableForUnsafeHttpMethods`). The "Resilience4j
  analogue" column is the author's judgement, labelled "(estimate)" in its header; the "L08.QuoteApi" column is read
  from `appsettings.json` and `QuoteApiFactory`.
- **KPI "Rate-limit rejection 503"** — VERIFIED (`RateLimiterOptions.RejectionStatusCode` API reference).
- **KPI "Lesson 08 tests" (28)**, chart 9.5 and the counts in the callouts — MEASURED at build by `tests_by_area()`:
  `[Fact]` + `[InlineData(` per test file (Hosting & DI 10, Endpoints 10, Cross-cutting 6, Resilience 2), equal to
  the `dotnet test` total on the build machine.
- **KPI "Sample code" (1472 lines)** and the VB line count in the §9 story (157) — `loc()` over every `.cs` / `.vb`
  file under `samples/`, and over the `.vb` files, MEASURED at build.
- **Chart 3.4** — MEASURED: `registrations_by_lifetime()` counts `.Add[Keyed]Singleton/Scoped/Transient` calls,
  typed `.AddHttpClient<` (transient) and `.AddHostedService<` in `L08.QuoteApi` and `RatingModule.vb`.
- **Chart 5.1** and its note — MEASURED: `status_codes()` parses `TOUR_OUT`; "documented" = the `documents …` lines
  the tour prints from `/openapi/v1.json`, "received" = the status column of the request lines mapped to the five
  operations; `status_matrix()` turns both into cells (ok / doc / GAP). The note names the gaps it computes (GET
  partner rate received 503 undocumented; POST accept documents 404 the tour did not trigger).
- **Chart 7.6** — MEASURED: `partner_attempts()` parses `PARTNER_OUT`.
- **Chart 9.6** and "23 web-tagged templates, 3 offer VB" — MEASURED: `templates_by_language()` parses
  `WEB_TEMPLATES`, the output of `dotnet new list --tag Web` on SDK 10.0.401.
- **Captured outputs** `TOUR_OUT`, `CONFIG_OUT` + `LIFETIME_OUT` (together the full `L08.HostingLab` output) and
  `PARTNER_OUT` — pasted from real runs on the build machine (Windows 11, SDK 10.0.401, ASP.NET Core runtime
  10.0.12); byte-compared with fresh Release runs before the final render (2026-09-20, all three match). The labs wrap
  their own lines at 62 columns (`Say` helper) so the side-by-side panels show verbatim output.
- **Table 5.2** — MEASURED from the tour and tests (400, 404, 409, 429 as problem+json, 503) except the 500 row,
  which is VERIFIED from Handle errors in ASP.NET Core APIs and not exercised.
- **Behaviours demonstrated by tests, not just cited:** the dispatcher survives an unknown channel key and a
  `TaskCanceledException` (HttpClient timeout) and keeps sending (`DispatcherTests`); `AddValidation` enforces
  attributes on a VB handler's parameters (400) but ignores attributes on a VB-declared request class (200)
  (`ValidationScopeTests`, `ValidationScope.vb`); minimal APIs and controllers read separate JSON options
  (`JsonOptionsTests`); `QuoteService` logs a warning when the bounded notification queue refuses a message.
- **Prose facts, VERIFIED with links in the PDF:** implicit `UseRouting` placement (WebApplication docs); IIS
  in-process hosting uses IIS HTTP Server, not Kestrel (In-process hosting with IIS); configuration source priority
  and `__` (Configuration); `ILogger<T>` categories and named message-template properties (Logging in .NET); scope
  validation only in Development (DI overview); minimal APIs recommended for new projects and the controller
  feature list (APIs overview); `[ApiController]` behaviours (Create web APIs); `AddValidation` generator scope
  (What's new .NET 10, Validation in ASP.NET Core); template maps OpenAPI in Development only (OpenAPI overview);
  Swashbuckle removed from the web API template in .NET 9 (dotnet/aspnetcore #54599); ProblemDetails middleware,
  `IExceptionHandler` order/lifetime and the .NET 10 diagnostics change; output-cache defaults, in-memory store and
  `UseCors` ordering (Output caching middleware); rate limiter ordering and IP-partition DoS note (Rate limiting
  middleware); health status codes (Health checks); handler lifetime 2 min, typed clients transient, avoid in
  singletons (IHttpClientFactory); circuit breaker states and `BrokenCircuitException` (Polly docs); since .NET 6 an
  exception escaping `BackgroundService.ExecuteAsync` stops the host; .NET 10 runs all of `ExecuteAsync` in the
  background (page re-read 2026-09-20); WebApplicationFactory default environment Development (Integration tests);
  the `public partial class Program` emitted by a source generator in the ASP.NET Core shared framework
  (dotnet/aspnetcore PR 58199).

## 5 · Presentation

Format 00 via `brief_pdf.py`; code panels from `lesson_kit`, listed in the Contents at level 2 by the local
`listed()` helper. Because `brief_pdf` makes a listed block's marker host `break-inside:avoid`, `listed()` wraps an
unkept panel's heading in a `.ct` line (as lesson 02 does), so a panel longer than 18 lines can split across pages;
`LOCAL_CSS` adds `break-after:avoid` to story / callout / panel headers, `orphans:4; widows:4` to code so no split
leaves a stub, and `word-break:normal` on links. Panel 3.3 is `keep=True` (26 lines) and starts a page rather than
splitting two lines from its end. `pcompare()` shortens a half-width panel's file label (drops `samples/`, or the
folder when the label is over 56 characters; captured output is labelled "captured run") so headers never truncate.

Mermaid 2.1 is `flowchart TB` with `direction LR` subgraphs, numbered nodes in run order, group-to-group arrows and
the group fill set to slate so the caption's colour key is complete; 4.8 and 8.1 are `sequenceDiagram`s coloured by
`%%{init}%%` with five participants each (solid = call, dashed = return; 8.1 draws the queue-to-dispatcher read as a
call and marks scope creation and failure handling as notes); 7.4 is `stateDiagram-v2 direction LR` with a small
`fontSize` init so its labels match the other diagrams. Chart 5.1 is a heatmap (cell 44, amber tone) so the 503 gap is
visible without reading the note.

Pagination was tuned by reordering, not by shrinking type: the §3 table sits before the captive panel, the §4
controller panel precedes the decision box, table 5.2 precedes the handler panel, and notes were trimmed where a
knife-edge fit decided a page. Compare sides ≤ 62 characters, code panels ≤ 100 (no width warnings).

## 6 · Inputs

`roster.py`; samples `L08.QuoteApi` (web API: route group + controller, ProblemDetails, `AddValidation`, OpenAPI,
rate limiting, output cache, health checks, CORS, typed partner client with the standard resilience handler,
keyed notification channels, hosted dispatcher, in-memory store), `L08.Rating.Vb` (VB library: rating rules, options,
`AddMotorRating`, `MapTariff` endpoint, `ValidationScope.vb`; `FrameworkReference Microsoft.AspNetCore.App`),
`L08.QuoteApi.Tests` (xUnit + `Microsoft.AspNetCore.Mvc.Testing` + `FakeTimeProvider`, 28 tests), `L08.HostingLab`
(console: configuration, options validation, lifetimes, captive dependency, keyed services), `L08.PartnerLab`
(console: resilience scenarios against an in-process fake partner), `L08.ApiTour` (console: drives the API in memory
and prints responses and OpenAPI operations); repo `global.json`, `Directory.Build.props`.

Sources (all linked in the PDF): Microsoft Learn — What's new in ASP.NET Core in .NET 10 · APIs overview ·
WebApplication and WebApplicationBuilder · Configuration in ASP.NET Core · Logging in .NET · Dependency injection
(scope validation) · OpenAPI support in ASP.NET Core · Validation in ASP.NET Core · Create web APIs · Handle errors in
ASP.NET Core APIs · Error handling (IExceptionHandler) · Rate limiting middleware ·
RateLimiterOptions.RejectionStatusCode · Output caching middleware · Health checks · Use the IHttpClientFactory ·
Build resilient HTTP apps · .NET 6 hosting exception handling · .NET 10 BackgroundService change · In-process hosting
with IIS · Integration tests in ASP.NET Core; GitHub — dotnet/aspnetcore issue 54599, PR 58199; Polly — circuit
breaker strategy.

## 7 · Invariants

- Premiums are labelled illustrative wherever they appear (§1 story, 9.2 note); the rates live in `RatingOptions.vb`.
- The tour must keep exercising every status code chart 5.1 and table 5.2 rely on (201, 400, 429, 200, 404, 409,
  503) and keep printing the `documents …` lines; its rate limit is set to 3 so the 4th write is the 429.
- `PartnersController` deliberately declares only 200, so the 503 gap in chart 5.1 stays visible; the POST route
  declares 400 and 429 with `Produces…` calls.
- The dispatcher's `try` wraps scope creation, key resolution and the send, and its `catch` filters on
  `stoppingToken`, never on the exception type; `DispatcherTests` fails if either regresses.
- `L08.HostingLab` lines stay ≤ 62 characters (shown in compares) and tour / partner-lab lines ≤ 100 (single panels),
  so the captured panels print verbatim.
- Test files keep one topic each (endpoints, hosting & DI, cross-cutting, resilience): chart 9.5 groups by file.
- Boundaries: records/interfaces → 03, async/channels/`TimeProvider` → 05, VB language → 06, project references and
  `FrameworkReference` → 07, EF Core → 09, test design/coverage → 10, authentication/authorization → 11,
  observability, IIS hosting, Native AOT, SQS and deployment → 12. Each gets one sentence and `ref(n)` here.
- No employer, client or personal names; experience is referenced generically ("~30 external rating partners").

## 8 · Known gaps

- ⚠ The four captured outputs are pasted constants; they matched fresh runs on 2026-09-20 but the build does not
  re-run the samples. The tour's last line depends on the background dispatcher running within the tour's 2 s wait.
- ⚠ Chart 5.1's "received" series counts only what the tour exercised (e.g. no 404 on accept); it is not an
  exhaustive contract test.
- ⚠ The 4.7 panel shows the tariff endpoint; the validation behaviour its note describes is in `ValidationScope.vb`
  and `ValidationScopeTests`, cited by name rather than printed (page budget).
- ⚠ Pagination is tuned to the current text: a few blocks fit a page by a small margin (4.5 on page 9, the footer on
  page 20), so a wording change can move a block. Re-run `--qa` and check the page-fill list after any edit; page 15
  is the emptiest (74 %).
- ⚠ Inline TypeScript and Kotlin panels are not compiled (`express-rate-limit` v7 option names; Resilience4j and
  MockMvc Kotlin DSL shown for recognition).
- ⚠ The web-template list reflects SDK 10.0.401 on the build machine; installed template packs change it.
