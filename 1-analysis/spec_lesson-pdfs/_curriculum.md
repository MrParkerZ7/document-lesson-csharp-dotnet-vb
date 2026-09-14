# Curriculum — C# · .NET 10 · Visual Basic for a JVM / TypeScript / Python architect

Scope, running example and boundaries for all twelve lessons. Numbers, slugs, titles, hours and transfer
estimates live in `0-script/lessons/roster.py`; this file owns **what each lesson teaches and builds**.

## Reader

An architect / technology lead with ~8 years of delivery. Write every "maps from" against this experience,
**generically** (no employer, client or personal names — `_standard.md` §7 privacy):

| Area | Experience to map from |
|---|---|
| Languages | Kotlin, Java (Spring Boot, WebFlux, legacy Java EE/JSP/Servlet), TypeScript/JavaScript (NestJS, Node, React/Angular/Next/Vue), Python (serverless Lambda), Dart/Flutter |
| Architecture | microservices, serverless, event-driven (pub/sub, saga, CQRS, event sourcing), API-first, super-app / hyper-scale design, legacy modernisation, company-transition migrations |
| Mono-repos | Kotlin Gradle-DSL mono-repo of 50–120+ modules; Python mono-repo of 100–300+ modules with a custom packager (55 KB zipped functions, ~175 ms cold starts); Maven multi-module; Lerna TypeScript |
| Cloud | AWS Lambda, ECS Fargate/EC2, EC2 Windows (IIS), Step Functions, API Gateway, DynamoDB, Aurora/RDS, S3, SQS/SNS, EventBridge, Secrets Manager, multi-account networking; Terraform provisioning 1,000–2,000+ resources with a sub-3-minute full deploy |
| Identity | Spring Security, OAuth2/OIDC, SSO, Entra ID / AD B2C, Auth0, Cognito, gateway-level authorization (Zuul) |
| Quality | TDD/BDD, 100% unit-test coverage as a standard, Postman automation per environment, Flutter Drive E2E, k6 load tests, SAST/DAST/secret/licence scanning in pipelines, SonarQube |
| Data | SQL + NoSQL, JPA/Hibernate, TypeORM, Elasticsearch, RabbitMQ, Kafka, Metabase dashboards (~230 queries), a DynamoDB query auto-generator library |
| Delivery | GitHub Actions, Jenkins, Docker, Jira automation, architecture documentation for an 80+ application migration estate, multi-format report framework (PDF / Excel / JSON) |
| Domain | motor insurance (partner integrations with ~30 external partners), core banking, real-estate platforms |

The reader has **not** owned a .NET codebase. They know OOP, SOLID, DI and testing deeply — never explain
those from zero; explain the .NET shape and the traps.

## Running example — MotorQuote

From lesson 02 onward, samples model a **motor-insurance quoting service**. Each lesson's samples are
self-contained (their own projects) but use this vocabulary so the reader recognises the domain everywhere.
All rates are **illustrative, not a real tariff** — say so wherever a premium is calculated.

| Concept | Shape (C#) | Notes |
|---|---|---|
| `Money` | `readonly record struct Money(decimal Amount, string Currency)` | THB by default; `decimal`, never `double` |
| `CoverageClass` | `enum { Class1, Class2Plus, Class3Plus, Class3 }` | Thai motor classes: 1 = comprehensive … 3 = third-party only |
| `VehicleUse` | `enum { Private, Commercial }` | |
| `Vehicle` | `record Vehicle(string Make, string Model, int Year, int EngineCc, VehicleUse Use, Money SumInsured)` | |
| `Driver` | `record Driver(DateOnly DateOfBirth, int LicenceYears, int ClaimsLast5Years)` | no names |
| `QuoteRequest` | vehicle + driver + coverage + requested start date | |
| `Premium` | net premium, loadings, discounts, stamp duty, VAT, total | stamp duty 0.4% of net premium and VAT 7% on (net + duty) — illustrative |
| `Quote` | `QuoteId`, request, `Premium`, `ValidUntil`, `QuoteStatus { Draft, Quoted, Accepted, Expired, Declined }` | |
| `Policy` | `PolicyNumber`, `QuoteId`, inception, expiry | issued when a quote is accepted |
| Rating rules | base rate by class × sum insured; young-driver loading (< 25); claims loading; no-claim bonus by claim-free years; commercial-use loading | the same rules recur so later lessons can test, persist and deploy them |
| Partners | `IPartnerRateProvider` — external rating partners, some slow or failing | lesson 05 fan-out, lesson 08 resilient HttpClient |
| Notifications | SMS · Email · LINE channels | lesson 05 Channels, lesson 08 background service |

## Lesson boundaries — who owns what

A topic belongs to exactly one lesson. Others mention it in one sentence with `ref(n)`.

| Topic | Owner |
|---|---|
| runtime, IL, JIT/AOT, TFMs, support policy, dotnet CLI basics, publish modes | 01 |
| syntax, built-in types, `decimal`, strings, nullability, pattern matching, methods/parameters, exceptions, `using` | 02 |
| class/struct/record, properties, constructors, inheritance, interfaces, generics & variance, extension members, equality, operators | 03 |
| collections, LINQ, iterators, delegates/lambdas, expression trees, immutability helpers | 04 |
| Task/async/await, cancellation, channels, parallelism, synchronization, `TimeProvider` | 05 |
| VB.NET syntax & semantics, Option Strict, VB↔C# interop, VB migration strategy | 06 |
| solutions/.slnx, MSBuild, Directory.Build.*, central package management, analyzers/.editorconfig, packaging, CI for builds | 07 |
| ASP.NET Core hosting, DI lifetimes, configuration/options, minimal APIs & controllers, OpenAPI, middleware, HttpClientFactory & resilience, background services | 08 |
| EF Core, migrations, query translation, tracking, concurrency, Dapper, providers | 09 |
| test frameworks, mocking, coverage & thresholds, integration/API tests, BDD, mutation testing | 10 |
| authentication/authorization, JWT, Entra ID / Microsoft.Identity.Web, OIDC flows, YARP gateway, secrets, OWASP, supply-chain scanning | 11 |
| AWS Lambda / containers / IIS hosting, SDK container publish, Terraform & GitHub Actions deploy, OpenTelemetry, Aspire, .NET Framework → .NET 10 modernisation | 12 |

## Lesson plans

Each plan lists: numbered sections (titles are guidance — keep the substance), what the reader must be able to
do, and the sample projects. Every sample project name starts `LNN.`; at least one VB project per lesson.
Verify every version-sensitive claim online before writing it (marked **verify**).

### 02 · C# Language Essentials — maps from Java 21 · Kotlin · TypeScript syntax
1. Why C# reads differently — file-scoped namespaces, top-level statements, implicit/global usings, file-based
   apps (`dotnet run app.cs`, .NET 10 — verify); the shape of a C# source file vs a Kotlin file.
2. Types and values — built-in aliases (`int`=`System.Int32`), `decimal` for money vs `BigDecimal`/floating
   point, `checked` overflow, `var`, `const` vs `readonly`, strings: interpolation, raw string literals,
   verbatim strings, `StringComparison` traps.
3. Nullability — nullable reference types (compile-time only) vs Kotlin's type system; `?.` `??` `??=` `!`;
   `int?` = `Nullable<int>` at run time; null-conditional assignment (C# 14 — verify).
4. Control flow and pattern matching — switch expressions, type/property/relational/list patterns, `is not null`,
   vs Kotlin `when` and Java 21 pattern `switch`.
5. Methods — named/optional arguments, `params` collections (C# 13 — verify), `out`/`ref`/`in`, tuples and
   deconstruction vs Kotlin `Pair`/destructuring, local functions, expression-bodied members, lambdas preview.
6. Exceptions and resources — unchecked only, exception filters `when`, `throw` expressions, `using` declarations
   / `IDisposable` / `IAsyncDisposable` vs try-with-resources and Kotlin `use`.
7. VB alongside — `Dim`/`As`, `Nothing`, `If()` operator, `Select Case`, `Using`, `Try…Catch When`.
8. Hands-on.
- Samples: `L02.Syntax` (C# console tour), `L02.SyntaxVb` (VB console, same tour), `L02.Rating` (C# library:
  first premium calculation with `decimal`, switch-expression loadings), `L02.Rating.Tests` (xUnit).

### 03 · Types, OOP & Generics — maps from Java/Kotlin OOP · SOLID · type erasure
1. Five kinds of type — `class`, `struct`, `record`, `record struct`, `enum`; stack/heap/inline, boxing,
   `readonly struct`; `Money` as a value object.
2. Members — properties (auto, `init`, `required`, `field` keyword C# 14 — verify), constructors, primary
   constructors (C# 12) vs Kotlin primary constructors, object/collection initializers, static members, `const`.
3. Inheritance and interfaces — **methods are non-virtual by default** (trap vs Java), `virtual`/`override`/
   `sealed`/`abstract`, `new` hiding, default interface methods, static abstract interface members.
4. Generics — reified generics, constraints (`where T : …`), variance `in`/`out` vs Kotlin `in`/`out` and Java
   wildcards, generic math (`INumber<T>`).
5. Extension members — C# 14 extension blocks (properties, static members — verify) vs Kotlin extensions;
   classic extension methods.
6. Equality and operators — reference vs value equality, `IEquatable<T>`, records, `==` overloading,
   `GetHashCode` contract.
7. Design in C# — SOLID with interfaces and DI-friendly constructors; a **multi-format report framework**
   (`IReportRenderer<TReport>` strategy for PDF/Excel/JSON-like outputs, rendered to text in the sample).
8. VB alongside — `Class`/`Structure`/`Interface`, `Inherits`/`Implements`, `Overridable`/`MustInherit`/
   `Shadows`, `Of T` generics; what VB cannot declare (records, init-only, required).
9. Hands-on.
- Samples: `L03.Domain` (C# library: Money, Vehicle, Driver, Quote, CoverageClass), `L03.Reports` (generic
  renderer strategy), `L03.Domain.Tests` (xUnit), `L03.VbInterop` (VB console: uses the records, inherits a
  C# abstract renderer).

### 04 · Collections, LINQ & Functional C# — maps from Java Streams · Kotlin collections · TS array methods
1. The collection family — `IEnumerable<T>` → `IReadOnlyList<T>`/`IList<T>`, `List`, `Dictionary`, `HashSet`,
   arrays, `Span<T>` (one card), immutable and frozen collections, collection expressions `[..]` (C# 12).
2. LINQ basics — method vs query syntax; **deferred execution and multiple enumeration** (trap vs Java streams'
   single use); `ToList`/`ToArray` materialisation; `yield return` vs Kotlin `sequence {}`.
3. Operator map — Select/Where/SelectMany/GroupBy/ToLookup/Aggregate/Zip/Chunk/DistinctBy/MinBy and the .NET 9
   additions `CountBy`/`AggregateBy`/`Index` (verify) vs Stream/Kotlin/TS equivalents.
4. Functional C# — `Func`/`Action`/delegates, closures, higher-order functions, immutability with records and
   `with`, pure functions and pattern matching.
5. Quote analytics — dashboard-style queries over a deterministic quote dataset (conversion by coverage class,
   premium bands, top makes) — the Metabase-query habit expressed in LINQ.
6. Expression trees — `Expression<Func<T,bool>>` vs `Func<T,bool>`, how `IQueryable` providers translate; build a
   small **query generator** that turns a predicate into a DynamoDB-style filter expression.
7. VB LINQ — VB's richer query syntax (`Aggregate`, `Group By … Into`, `Distinct`, `Skip While`).
8. Hands-on.
- Samples: `L04.QuoteAnalytics` (C# console), `L04.QueryGen` (C# library: expression → filter string),
  `L04.QueryGen.Tests` (xUnit), `L04.VbLinq` (VB console: the same analytics in VB query syntax).

### 05 · Async, Tasks & Concurrency — maps from Kotlin coroutines · Spring WebFlux · Node event loop
1. The Task model — `Task`/`Task<T>`/`ValueTask`, what `await` compiles to, the thread pool, synchronization
   contexts (none in ASP.NET Core) vs dispatchers and the Node event loop.
2. Concept map — `suspend`, `launch`, `async/await`, structured concurrency, `Job.cancel`, `withTimeout`, `Flow`,
   `Channel`, Reactor `Mono`/`Flux` → their .NET forms, and where there is no equivalent.
3. Cancellation and timeouts — `CancellationToken` propagation, `CancelAfter`, `WaitAsync`, linked tokens.
4. Fan-out — `Task.WhenAll`/`WhenAny`/`Task.WhenEach` (.NET 9 — verify): query ~30 external rating partners with
   per-partner timeouts, tolerate failures, pick the best rate.
5. Streams and pipelines — `IAsyncEnumerable<T>` + `await foreach` vs `Flow`; `System.Threading.Channels` bounded
   producer/consumer with back-pressure: a multi-channel notification dispatcher (SMS · Email · LINE).
6. Shared state — `lock` and the .NET 9 `Lock` type (verify), `SemaphoreSlim`, `Interlocked`, concurrent
   collections, `Parallel.ForEachAsync`; testable time with `TimeProvider` + `FakeTimeProvider`.
7. Traps — `async void`, `.Result`/`.Wait()` sync-over-async, `ConfigureAwait(false)` in libraries,
   fire-and-forget, `Task.Run` inside ASP.NET Core; VB `Async`/`Await` and what VB restricts (verify by compiling).
8. Hands-on.
- Samples: `L05.PartnerRates` (C# library), `L05.PartnerRates.Tests` (xUnit, deterministic with
  `FakeTimeProvider` — no real sleeps), `L05.Notifications` (C# console with channels; exits by itself),
  `L05.VbAsync` (VB console).

### 06 · VB.NET for Legacy Estates — maps from Java EE / JSP legacy maintenance · polyglot repositories
1. Where VB.NET lives — .NET Framework WinForms / Web Forms / services; Microsoft's VB strategy; what .NET 10
   supports for VB (console, libraries, WinForms, WPF, tests) and what it does not (e.g. ASP.NET Core / Razor
   templates — verify).
2. Reading VB fluently — a large C# ↔ VB syntax table: `Dim`, `Nothing`, `Is`/`IsNot`, `AndAlso`/`OrElse`,
   `Mod`, `\`, `&`, `Shared`, `Friend`, `Module`, `MustInherit`, `NotInheritable`, `Handles`/`WithEvents`,
   `With`, `ReDim`, `My` namespace, `On Error` legacy.
3. Semantics that bite — `Option Strict Off` late binding and implicit conversions; `And`/`Or` do not
   short-circuit; `Dim a(5)` has six elements; `CInt`/`CDec`/`Math.Round` banker's rounding vs truncation (a
   premium-rounding trap); `Option Compare Text`; case-insensitivity.
4. VB ↔ C# interop — calling each way, `Microsoft.VisualBasic` runtime helpers, case-only member collisions,
   `CLSCompliant`, optional parameters and `ByRef` across the boundary.
5. Migration strategy — characterization tests first, strangler-fig by project, retarget VB libraries to
   `net10.0`, port UI to C#; code converters (verify current tools); the decision tree VB6 → rewrite,
   Web Forms → re-platform UI, WinForms → retarget `net10.0-windows`.
6. Parity testing — prove a C# port matches the VB original over a grid of inputs before switching.
7. Hands-on.
- Samples: `L06.LegacyRating` (VB library written in legacy style, including the rounding behaviour),
  `L06.LegacyRating.Tests` (VB xUnit characterization tests), `L06.ModernRating` (C# port),
  `L06.Parity.Tests` (C# xUnit: grid parity VB vs C#), `L06.WinFormsVb` (VB WinForms, `net10.0-windows`,
  build-only — `OutputType WinExe`).

### 07 · Solutions, MSBuild & Mono-repos — maps from Gradle Kotlin DSL · Maven multi-module · Lerna
1. Solutions — `.sln` vs the XML `.slnx` format (default in .NET 10 — verify), solution filters `.slnf`,
   vs `settings.gradle.kts`.
2. MSBuild model — properties, items, targets, evaluation vs execution, SDK-style defaults, `-bl` binary logs.
3. Shared build logic — `Directory.Build.props`/`.targets` (nearest wins; importing the parent is manual — trap),
   `Directory.Build.rsp`, conditions on project extension.
4. Dependencies — Central Package Management (`Directory.Packages.props`) vs Gradle version catalogs, transitive
   pinning, lock files, NuGet audit.
5. A mono-repo at scale — project references and the build graph, incremental builds, artifacts output layout,
   analyzers + `.editorconfig` + `dotnet format` as quality gates (vs SonarQube/ktlint), `InternalsVisibleTo`,
   mixed C#/VB projects in one tree.
6. Packaging and CI — `dotnet pack`, versioning strategies, private feeds (GitHub Packages, AWS CodeArtifact),
   a GitHub Actions workflow for build/test/pack with caching.
7. Hands-on.
- Samples: a self-contained mini mono-repo under `samples/MotorMono/`: `MotorMono.slnx`, a nested
  `Directory.Build.props` that **imports the repo root one**, `Directory.Packages.props`, a custom target that
  prints the module count, `src/L07.Core`, `src/L07.Pricing`, `src/L07.Pricing.Vb`, `tests/L07.Pricing.Tests`;
  plus `samples/ci/build.yml` (a workflow file read into the PDF, not active).

### 08 · ASP.NET Core Web APIs — maps from Spring Boot · NestJS · Express
1. Hosting — `WebApplication` builder, Kestrel, the middleware pipeline vs Spring filters / Express middleware;
   configuration sources and the options pattern vs `@ConfigurationProperties`; `ILogger`.
2. Dependency injection — built-in container, Singleton/Scoped/Transient vs Spring scopes, captive dependency
   trap, keyed services.
3. Endpoints — minimal APIs vs controllers (vs `@RestController`/NestJS controllers), route groups, typed
   results, endpoint filters, validation (built-in minimal-API validation in .NET 10 — verify), ProblemDetails.
4. OpenAPI — built-in `Microsoft.AspNetCore.OpenApi` document generation (verify .NET 10 OpenAPI version),
   Swashbuckle's removal from templates.
5. Cross-cutting — exception handling (`IExceptionHandler`), rate limiting, output caching, health checks, CORS.
6. Calling partners — `IHttpClientFactory`, typed clients, `Microsoft.Extensions.Http.Resilience` (retry,
   timeout, circuit breaker) for ~30 external partners.
7. Background work — `BackgroundService` vs `@Scheduled`; hosting a notification dispatcher.
8. Testing the API in-process — `WebApplicationFactory` vs `@SpringBootTest`/MockMvc (depth in `ref(10)`).
9. Hands-on. VB note: no VB web templates — a VB library consumed by the C# API.
- Samples: `L08.QuoteApi` (web: `POST /quotes`, `GET /quotes/{id}`, `POST /quotes/{id}/accept`, ProblemDetails,
  OpenAPI, health, in-memory repository), `L08.Rating.Vb` (VB library the API calls), `L08.QuoteApi.Tests`
  (xUnit + `WebApplicationFactory`).

### 09 · Data Access with EF Core — maps from JPA/Hibernate · TypeORM · Flyway/Liquibase
1. The model — `DbContext` vs `EntityManager`, `DbSet`, conventions / attributes / Fluent API, owned or complex
   types for `Money` vs `@Embeddable` (verify the recommended option in EF Core 10).
2. Querying — LINQ-to-SQL translation, `IQueryable` vs `IEnumerable` trap, `ToQueryString`, projections,
   `AsNoTracking`, N+1 and `Include` vs JPA fetch joins, split queries, `FromSql` parameterisation.
3. Change tracking and transactions — unit of work in `SaveChanges`, optimistic concurrency tokens vs `@Version`.
4. Migrations — `dotnet ef` as a local tool, migrations/bundles/idempotent scripts vs Flyway/Liquibase.
5. Beyond EF — Dapper (vs JdbcTemplate/MyBatis), bulk `ExecuteUpdate`/`ExecuteDelete`, providers (SQL Server,
   PostgreSQL/Npgsql, SQLite, MySQL, Aurora), DynamoDB via the AWS SDK instead of EF.
6. Testing data access — SQLite in-memory vs the InMemory provider trap, Testcontainers (mention), counting SQL
   commands with an interceptor.
7. VB alongside — querying a C# `DbContext` from VB; what EF tooling does not generate for VB (verify).
8. Hands-on.
- Samples: `L09.Data` (C# library: `MotorQuoteDbContext`, entities, configuration, a committed migration),
  `L09.Data.Tests` (xUnit on SQLite in-memory: N+1 vs `Include` command counts, concurrency conflict),
  `L09.QueryConsole` (C# console printing generated SQL), `L09.VbReport` (VB console querying the context).

### 10 · Testing, TDD & 100% Coverage — maps from JUnit · Mockito · MockMvc · Postman · BDD
1. The frameworks — xUnit (v3 status — verify), NUnit, MSTest vs JUnit 5; attribute map; Microsoft.Testing.Platform
   vs VSTest and `dotnet test` in .NET 10 (verify).
2. TDD in C# — red/green/refactor on the no-claim-bonus rule; `[Theory]` data vs `@ParameterizedTest`; fixtures.
3. Assertions and test doubles — built-in asserts, assertion-library licensing changes (verify FluentAssertions
   status and alternatives), NSubstitute / Moq vs Mockito, fakes vs mocks, `FakeTimeProvider`.
4. Coverage as a gate — coverlet (or Microsoft code coverage) → Cobertura, **line + branch thresholds at 100%**
   failing the build, ReportGenerator, `[ExcludeFromCodeCoverage]` discipline.
5. Integration and API tests — `WebApplicationFactory`, Testcontainers, `.http` files vs Postman collections,
   Playwright for .NET (mention).
6. BDD — Gherkin with Reqnroll (SpecFlow's successor — verify) vs Cucumber; when BDD pays.
7. Beyond coverage — mutation testing with Stryker.NET; test pyramid for a microservice estate.
8. VB alongside — xUnit tests written in VB.
9. Hands-on.
- Samples: `L10.Pricing` (C# library), `L10.Pricing.Tests` (xUnit: theories, NSubstitute, `FakeTimeProvider`,
  **coverage threshold 100% enforced so `dotnet test` fails below it**), `L10.Pricing.VbTests` (VB xUnit),
  optional `L10.Pricing.Specs` (Reqnroll) only if it builds cleanly on net10.0 — otherwise show Gherkin inline.

### 11 · Security & Identity with Entra ID — maps from Spring Security · OAuth2/OIDC · Entra ID / AD B2C
1. The model — authentication schemes vs authorization policies, `ClaimsPrincipal` vs `SecurityContext`,
   middleware order trap, `[Authorize]` / `RequireAuthorization`.
2. Tokens — JWT bearer validation (issuer, audience, keys, clock skew), scopes vs app roles, claim mapping traps.
3. Entra ID — `Microsoft.Identity.Web` for web APIs, Entra External ID vs Azure AD B2C for new customers
   (verify), Auth0 / Cognito as generic OIDC authorities.
4. Flows — authorization code + PKCE, client credentials, on-behalf-of, MSAL; workload identity federation (e.g.
   GitHub Actions OIDC) instead of secrets.
5. Authorization design — policy-based and resource-based authorization (only the quote owner or an underwriter),
   YARP as the gateway (vs Zuul / Spring Cloud Gateway).
6. Secrets and hardening — user-secrets, AWS Secrets Manager / Key Vault configuration providers, Data Protection,
   HTTPS/HSTS, CORS, antiforgery, rate limiting, NuGet vulnerability audit, CodeQL/SonarQube security analyzers,
   STRIDE per endpoint.
7. Testing security — locally signed test tokens in `WebApplicationFactory`; a 401/403/200 matrix.
8. VB and legacy — Forms/Windows authentication in .NET Framework estates and their modern replacements.
9. Hands-on.
- Samples: `L11.SecureQuoteApi` (web: JWT bearer, scope policies `quotes:read`/`quotes:write`, underwriter role,
  resource-based owner check, Entra configuration section), `L11.SecureQuoteApi.Tests` (xUnit, test-signed tokens,
  status matrix), `L11.ClaimsVb` (VB console/library inspecting a `ClaimsPrincipal`).

### 12 · Cloud-Native .NET on AWS & Modernization — maps from AWS Lambda · ECS Fargate · Terraform · GitHub Actions · IIS estates
1. Choosing a target — Lambda (managed `dotnet10` runtime — verify), Lambda + Native AOT, ECS Fargate containers,
   EC2 Windows + IIS; a decision flow by latency, traffic shape, statefulness and legacy constraints.
2. .NET on Lambda — handler model, `Amazon.Lambda.Annotations`, API Gateway events, ASP.NET Core on Lambda,
   SnapStart for .NET (verify), Powertools for AWS Lambda (.NET).
3. Containers — official images, chiseled/non-root, `dotnet publish` container support without a Dockerfile
   (verify), health checks, graceful shutdown on SIGTERM, arm64.
4. Infrastructure and delivery — Terraform for Lambda + API Gateway + ECS, a GitHub Actions pipeline with OIDC
   to AWS, AWS CDK in C# as an alternative, Aspire for local orchestration (verify current naming/version).
5. Observability — OpenTelemetry .NET (traces, metrics, logs) to CloudWatch / X-Ray, structured logging.
6. Modernising Windows / IIS estates — assess an 80+ application estate, the 6 Rs, .NET Framework → .NET 10
   porting map (`System.Web` → ASP.NET Core, WCF → CoreWCF/gRPC, Web Forms → Razor/Blazor, `web.config` →
   `appsettings.json`), incremental migration with YARP / System.Web adapters, tooling (verify the current state
   of .NET Upgrade Assistant, GitHub Copilot app modernization and AWS Transform for .NET).
7. Hands-on, and what to learn after this track.
- Samples: `L12.QuoteLambda` (C# Lambda function for an API Gateway HTTP API), `L12.QuoteLambda.Tests`
  (xUnit with the Lambda test utilities), `L12.QuoteContainer` (web API configured for SDK container publish,
  build-only), `L12.RatingVb` (VB library deployed inside the Lambda), `samples/infra/main.tf` and
  `samples/ci/deploy.yml` (read into the PDF; not executed).
