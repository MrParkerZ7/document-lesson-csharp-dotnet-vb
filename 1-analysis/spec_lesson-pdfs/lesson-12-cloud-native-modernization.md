# Unit spec — lesson-12-cloud-native-modernization.pdf

Built to `_standard.md`. Content module `0-script/lessons/lesson_12.py`. Samples
`lesson-12-cloud-native-modernization/samples/`. Plan: `_curriculum.md` § "12 · Cloud-Native .NET on AWS & Modernization".

## 1 · Purpose

Take a JVM / TypeScript / Python architect who has shipped Python Lambdas, Fargate services, large Terraform estates and
GitHub Actions pipelines — and has documented a migration inventory with Windows (IIS) workloads — from "I know AWS" to
"I can host, ship, observe and modernise .NET on AWS": choose between Lambda (managed `dotnet10`, SnapStart, Native AOT,
Lambda Managed Instances), ECS Fargate and EC2 Windows + IIS; write and test a Lambda function with Lambda Annotations;
publish a chiseled multi-arch image without a Dockerfile; describe both in Terraform and deploy with OIDC; emit
OpenTelemetry signals; and triage a .NET Framework estate with the AWS 7 Rs and the .NET 10 porting map. It is the last
lesson, so the footer says what to study after the track instead of "Next".

## 2 · Ownership & cadence

Owner **claude**, regenerable. Re-verify every November (new .NET major) and when AWS changes a runtime row:

- Lambda runtime dates (KPI 1.1, card 2.1 #1, table 3.6) — `days_until(2026, 11, 10)` drives the `dotnet8` tile and the
  pill colours; after 10 Nov 2026 the tile reads "deprecated" and the pills turn red automatically. A `dotnet12` runtime
  (expected after .NET 12 ships in Nov 2027) needs a new table row.
- Tool and product status in §5 and §7 (GitHub Action majors, Aspire version/name, AWS Transform supported versions,
  Upgrade Assistant deprecation, X-Ray maintenance mode, Powertools / ADOT support for Lambda Managed Instances).
- Captured figures: re-capture panels 4.5, 7.3 and 8.2 and the `PACKAGES` / `LAYERS` constants when the samples, the
  SDK or the base image change (7.3 was re-captured on 2026-09-20 after the VB6 desktop rule changed; the zip sizes, layer sizes,
  4.5 and 8.2 were re-captured on 2026-09-20 after the tariff change). `blocks()` raises if the test-case count drifts from
  `CAPTURED_TESTS = 22` (16 Lambda + 6 container) or the estate size drifts from the captured triage run. The app layer's
  compressed size varies by tens of bytes from run to run, and so do the manifest digests in 4.5.
- **The tariff** — every premium in this lesson's samples is the canonical tariff of `_curriculum.md` § "Canonical tariff"
  (Class 1 2.1% · Class2Plus 1.2% · Class3Plus 0.9% · Class 3 0.4%; loadings added: young driver +20%, 1 claim +10%, 2 claims
  +25%, commercial +25% or +35% above 3,000 cc; no-claim ladder 20/25/30/40/50% on claim-free licence years; net, stamp duty
  0.4% and VAT 7% each rounded to the satang, half away from zero; three or more claims decline the quote). A change to
  that section means re-running the samples and re-capturing 8.2.

## 3 · Structure

22 pages at the 2026-09-20 build (Lambda runtime dates, action majors and the terraform observation date from 2026-09-16 or the 2026-09-20 re-check; the zip sizes, layers, 4.5 and 8.2 were re-captured on 2026-09-20 after the cross-lesson tariff alignment).

| § | Heading | Blocks |
|---|---|---|
| — | Contents | `toc` depth 2 (code panels and the threecol listed through local `listed()` / `figure_heading()`) · lesson-local CSS block (callout/story headings kept with their first line; mermaid height caps: sequence 3.9in, state 2.3in, flowchart 3.6in) |
| 1 | Why this lesson — MotorQuote meets the AWS estate you already run | story (4 ¶; ¶2 states that every premium is the track's one illustrative tariff, that three or more claims decline the quote as HTTP 422 on every host, and that the request and stored quote are flat wire types, not lesson 03's `Money` / `QuoteId` structs) · `kpi` 1.1 (5 tiles) · `legend` (Python, cloud, architecture, legacy — only the tags the lesson's cards wear) · info callout "Before you start" (4 items; item 1 lists lessons 01, 06, 08, 10 and 11 — the same five the §1 story names, in roster order, so the checklist matches the story) |
| 2 | Choosing a hosting target | story (3 ¶) · cards 2.1 (6 hosting targets: 3 + 3 in a "(continued)" band, `toc: False`; card 5 also names the ECS Windows container) · mermaid 2.2 flowchart TB (decision flow, question boxes rather than diamonds; the Framework/COM/GAC answer is "Windows host: EC2 + IIS or an ECS Windows container") · chart 2.3 heatmap (5 targets × 6 questions, rubric, cell 40; Fargate scores "some" on .NET Framework / System.Web because it runs Windows containers with limits) · mapping 2.4 (14 rows — the SLF4J row was dropped: the message-template rule is lesson 08's) |
| 3 | .NET on Lambda — handlers, Annotations and SnapStart | story (3 ¶) · compare 3.1 (Python Powertools `APIGatewayHttpResolver` ↔ C# Annotations `CreateQuote`; its note says Annotations and Powertools for AWS Lambda (.NET) are complementary) · code 3.2 (`Startup`) · mermaid 3.3 sequenceDiagram (cold INIT then a warm request; six participants including `Startup`, `mirrorActors` off so the bottom row of boxes is gone and the diagram and 3.4 share a page) · compare 3.4 (raw C# handler ↔ raw VB handler; both catch `QuoteDeclinedException` and answer 422; the note says the parity test sends four bodies) · code 3.5 (SnapStart hooks: the before-snapshot hook drives ten requests through `RawQuoteHandler`) · table 3.6 (.NET runtimes on Lambda, 5 rows, with a note that `dotnet9` is image-only) · chartrow 3.7 bar (handler code lines) + 3.8 bar (deployment zip size) · code 3.9 (test of the generated wrapper) |
| 4 | Containers without a Dockerfile | story (3 ¶) · code 4.1 (`L12.QuoteContainer.csproj`, `keep=False`) · code 4.2 (hosting + shutdown budget) · code 4.3 (liveness/readiness) · mermaid 4.4 stateDiagram-v2 (ECS task life, `direction LR`) · code 4.5 (captured `dotnet publish -t:PublishContainer` to an archive) · chart 4.6 stacked_bar (compressed layers per architecture; 470 × 265 so the 4.7 MB layer clears the chart's label threshold; the caption names the 0.55 MB app layer, a sliver at this scale) · table 4.7 (image configuration from the manifest, 7 rows) |
| 5 | Infrastructure and delivery — Terraform, OIDC, CDK and Aspire | story (3 ¶) · mermaid 5.1 sequenceDiagram (OIDC push-to-deploy) · code 5.2 (`deploy.yml` #region build) · code 5.3 (`deploy.yml` #region ship) · code 5.4 (`main.tf` #region lambda, `keep=False`) · code 5.5 (`main.tf` #region ecs, `keep=False`; its note says the collector sidecar and `OTEL_EXPORTER_OTLP_ENDPOINT` are left out, so the sketched task exports nothing) · figure heading 5.6 + threecol (Terraform · AWS CDK in C# · Aspire). The pipeline comes before the Terraform it applies so that the two long panels 5.4 and 5.5 sit on separate pages with a diagram or workflow beside them. |
| 6 | Observability — OpenTelemetry on .NET's own APIs | story (3 ¶; ¶3 is Lambda-specific — the JSON log format turns template placeholders into CloudWatch Logs fields — and cites lesson 08 for why the message must be a template) · code 6.1 (telemetry wiring) · code 6.2 (span + counter + message-template log; a declined quote returns 422 before the counter and the log; the template rule is pointed at lesson 08) · mermaid 6.3 flowchart LR (where each signal goes) · code 6.4 (in-memory exporter span test) |
| 7 | Modernising Windows and IIS estates | story (3 ¶) · table 7.1 (porting map, 9 rows with Kind chips) · code 7.2 (triage rules) · code 7.3 (captured triage output, `keep=False`) · chartrow 7.4 bar (apps per 7 R strategy) + 7.5 hbar (apps per target) · mermaid 7.6 flowchart LR (strangler fig behind YARP) · table 7.7 (modernisation tools, 5 rows) |
| 8 | Hands-on — and what to learn after the track | story (3 ¶, the third is the after-the-track guidance) · code 8.1 commands · code 8.2 (captured verify_samples + dotnet test summary) · chart 8.3 hbar (code lines per project) · warn "⚠ Traps" (5: module-scope state · SnapStart is free · Native AOT built on a laptop · Dockerfile habits · Terraform runtime list + Git Bash `/t:`) · ok "✔ Checkpoint — you have finished the track when you can" (5) · summary "🔍 Check yourself" (7) · footer ("After the track:") |

Standard minimums as built: 8 numbered stories · 1 mapping (14 rows) · 2 card bands (3 cards each) · 6 mermaid
(flowchart ×3, sequenceDiagram ×2, stateDiagram-v2 ×1) · 7 charts · 22 code panels (18 `code` + 2 `compare`) · C# ↔ VB
compare (3.4) · Python ↔ C# compare (3.1) · 1 threecol · 4 tables besides the mapping · 41 distinct links (Microsoft
Learn, .NET Blog, AWS docs and blogs, GitHub docs and repositories, aspire.dev).

## 4 · Derivation

- **VERIFIED (dated 2026-09-16, linked):**
  - Lambda runtimes (KPI 1.1, cards, table 3.6): `dotnet10` AL2023, deprecation 14 Nov 2028, block create 14 Dec 2028,
    block update 15 Jan 2029; `dotnet9` container-only, deprecation 10 Nov 2026; `dotnet8` deprecation 10 Nov 2026,
    blocks 1 Feb / 3 Mar 2027; `dotnet6` AL2 deprecated 20 Dec 2024; `provided.al2023` 30 Jun 2029 — Lambda runtimes page.
    `dotnet10` launch 8 Jan 2026 and file-based functions — AWS Compute Blog post.
  - SnapStart: .NET 8+, published versions/aliases only, Annotations 1.6.0+, not with provisioned concurrency, EFS,
    ephemeral storage > 512 MB or OS-only runtimes, caching + restore charges except Java — SnapStart page; hooks in
    Amazon.Lambda.Core 2.5.0+, register in the constructor path — runtime hooks page; repeated warm-up calls because of
    tiered compilation, no side effects — best-practices page.
  - Native AOT: compile on AL2023 (Lambda CLI uses a Docker build container), source-generated serialisation, trimming —
    AOT page; managed runtime keeps .NET system libraries available vs `provided.al2023` — .NET 8 runtime blog.
  - Lambda Managed Instances: one .NET process, concurrent requests as Tasks, 32 per vCPU default, Amazon.Lambda.Core
    2.7.1+, Powertools and ADOT .NET not supported yet — LMI .NET runtime page.
  - Handler string format, class-library vs executable-assembly models, file-based functions default to Native AOT,
    Annotations documented for C# — C# handler page. JSON log format and message-template fields — C# logging page.
    `AddAWSLambdaHosting` swaps Kestrel only inside Lambda — ASP.NET on Lambda page. HTTP API 30 s integration
    timeout — API Gateway quotas. Lambda 900 s maximum timeout — SnapStart runtime hooks page.
  - Containers: multi-RID image index from SDK 8.0.405 / 9.0.102, archive output, registry push, no `RUN`, exposed port
    inferred from `ASPNETCORE_HTTP_PORTS`, rootless `app` user by default — publish configuration reference; port 8080
    since .NET 8 — breaking-change page; Ubuntu 24.04 default tags and no Debian images since .NET 10 — breaking-change
    page; size-optimised images carry no ICU/tzdata — container images page.
  - ECS Windows containers run on Fargate (Windows Server 2019 and 2022, Full and Core) and on EC2; on Fargate there is no
    gMSA, EFS, EBS, FSx, Firelens or Spot — "Windows containers on Fargate considerations" (fetched 2026-09-20). AWS
    App2Container is deliberately not named: it stopped accepting new customers on 7 Nov 2025 (search result; its product
    page now points to AWS Transform), although the 7 Rs page still lists it.
  - Powertools for AWS Lambda (.NET): utilities are Logging, Metrics, Tracing, Idempotency, Batch Processing, Parameters
    and an Event Handler that covers AppSync Events and Bedrock Agent functions only — no API Gateway router — Powertools
    docs (fetched 2026-09-20).
  - ECS `stopTimeout` default 30 s, max 120 s; health check `CMD` / `CMD-SHELL` — ECS task definition parameters.
    `HostOptions.ShutdownTimeout` default 30 s (5 s in .NET 5 and earlier), SIGTERM → `ApplicationStopping` — Generic
    Host page.
  - Delivery: OIDC permissions, `aud` `sts.amazonaws.com`, `sub` format — GitHub docs. Action majors (checkout v7,
    setup-dotnet v6, configure-aws-credentials v6, amazon-ecr-login v2, setup-terraform v4) = latest GitHub release tags
    read on 2026-09-16 (linked). Provider builds before the runtime launch rejected `dotnet10` — provider issue #45888.
    CDK: .NET stable, .NET 8+, Node.js for the CLI, VB/F# limited — CDK C# guide. Aspire rename at 13 (11 Nov 2025),
    .NET 10 SDK required — aspire.dev; `Aspire.Hosting.AWS` CloudFormation provisioning and local Lambda (preview) — AWS
    SDK for .NET guide.
  - Observability: `ActivitySource`/`Activity`, `Meter`, `ILogger` as the OTel APIs — Microsoft Learn; X-Ray SDKs and
    daemon in maintenance mode from 25 Feb 2026, collector/CloudWatch agent replacement, span → segment mapping — X-Ray
    migration page. Powertools utilities — Powertools docs.
  - Modernisation: the 7 Rs and "replatform first" advice — AWS Prescriptive Guidance; unavailable technologies and
    replacements (AppDomains, remoting, CAS, COM+, WF → CoreWF, CoreWCF) — Microsoft Learn; incremental migration with
    YARP + System.Web adapters, remote session/authentication — ASP.NET migration pages; CoreWCF 1.0 bindings, Microsoft
    support, gRPC for greenfield — .NET Blog; Upgrade Assistant deprecated in favour of GitHub Copilot app modernization
    — porting overview; AWS Transform for .NET sources/targets/project types, VB.NET preview — AWS Transform guide;
    Web Forms → Blazor — Microsoft architecture guide. Package versions in table 7.7 (System.Web adapters 2.3.0,
    CoreWCF 1.9.1) = latest stable on nuget.org on 2026-09-16.
- **MEASURED at build time** (recomputed on every render):
  - Chart 3.7: `region_loc()` over regions `annotations`, `raw-cs`, `raw-vb` (28 / 35 / 33 at this build); the note's
    percentage is computed from them.
  - Chart 8.3: `loc()` per sample project over `.cs`/`.vb` files, bin/obj excluded (EstateTriage 63, QuoteContainer 84,
    QuoteContainer.Tests 68, QuoteLambda 157, QuoteLambda.Tests 103, QuoteLambdaVb 50, RatingVb 61); the note's sums are
    computed.
  - Test-case count (KPI-adjacent text, 3.9, §8): `[Fact]` + `[InlineData(` lines in the two test files (16 + 6 = 22), checked
    against `CAPTURED_TESTS`. Estate size: rows of `estate.csv`, checked against the captured 7.3 header. Project count:
    `*.csproj`/`*.vbproj` under samples (7).
  - Charts 7.4 / 7.5 and KPI "Estate triage": parsed from the captured triage output string (`TRIAGE_OUTPUT`).
- **MEASURED — captured from real runs on the build machine (Windows x64, SDK 10.0.401, runtime 10.0.12; 7.3 on 2026-09-20, the rest re-run on 2026-09-20 after the tariff change):**
  - Chart 3.8 and KPI "Lambda zip": `dotnet publish -c Release -o <dir>` of `L12.QuoteLambda` (40 files, 809,341 bytes
    zipped with deflate), the same with `-r linux-arm64 --self-contained false` (38 files, 724,469 bytes) and
    `L12.QuoteLambdaVb` (9 files, 77,854 bytes), all re-run on 2026-09-20. The zipping was done with Python `zipfile` (ZIP_DEFLATED).
  - Chart 4.6, table 4.7 and KPI "App layer": `dotnet publish -t:PublishContainer -p ContainerArchiveOutputPath=…`
    produced an OCI archive; per-architecture compressed layer sizes and config (User 1654, `ASPNETCORE_HTTP_PORTS=8080`,
    `DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=true`, entrypoint, `DOTNET_VERSION=10.0.12`) were read from the manifests
    and image history in the archive. Layers mapped by history: rootfs, `/home/app`, .NET runtime, `dotnet` symlink,
    ASP.NET Core, app.
  - Panel 4.5: the publish command's output (absolute paths shortened, long lines wrapped by hand, digests truncated).
  - Panel 7.3: `dotnet run` of `L12.EstateTriage`. Panel 8.2: `verify_samples.py --only 12` and the two `dotnet test`
    summary lines (`Passed: 16` / `Passed: 6`; `$SAMPLES` substituted, durations trimmed from the `Passed!` lines; the PASS-line
    times are those of an incremental run).
  - Panel 4.5 label: "captured 2026-09-20 · edited: paths, wrapping, one publish line, MSBuild prefixes" — the panel drops
    the `release/` publish line and the MSBuild diagnostic prefix of the image-index line. Panel 8.2 label: the SDK path,
    test durations, the ` (net10.0)` suffix and the column padding of the `Passed!` lines are edited.
  - Panel 7.3 was re-captured on 2026-09-20 after the triage gained a `vb6` + `desktop` arm (`agent-commission` now targets
    `desktop`; ECS Fargate 9, desktop 2, EC2 Windows/IIS 2, Lambda 1, retired 1, SaaS 1; Refactor stays 3).
  - Panel 4.5 note and trap 5: in Git Bash, `/t:PublishContainer` failed with "MSB1008: Only one project can be
    specified" (MSYS path conversion); `-t:` works.
  - §3 story and 3.2 note (generated wrapper behaviour: singleton registration, eager resolve for INIT reports, per-request
    scope, 400 on unreadable body): read from the Annotations 2.4.0 generator output emitted with
    `EmitCompilerGeneratedFiles=true`.
- **One-off observation, not MEASURED:** the §5 story's `terraform validate` claim — on 2026-09-16 `terraform init` resolved
  `hashicorp/aws ~> 6.0` to 6.64.0 and `terraform validate` passed on a scratch copy of `main.tf`; an unknown runtime made
  validate fail with the provider's runtime list, which includes `dotnet10`. It was run once by hand, not by the build, and
  `~> 6.0` floats (6.65.0 was published on 2026-09-16), so the story words it as a dated observation.
- **Re-checked 2026-09-20:** table 3.6 (Lambda runtimes) against the AWS runtimes page; the `dotnet9` row is listed there as
  "container only" with the identifier `dotnet9`, so the identifier cell says "image only".
- **ESTIMATE:** chart 2.3 heatmap is a rubric (good / some / poor), labelled "a rubric, not a benchmark". No cold-start
  latency or cost figure appears anywhere.
- **Reader figures** (from `_curriculum.md`, not claims about AWS): ~175 ms cold starts, 55 KB zipped functions,
  1,000–2,000+ Terraform resources, 80+ application inventory.

## 5 · Presentation

Format 00 via `brief_pdf.py`; code panels from `lesson_kit`. Local helpers (kit requests): `listed()` / `panel()` /
`pair()` put code panels in the Contents and strip Pygments' error box; `figure_heading()` numbers the threecol;
`region_loc()`, `test_cases()`, `project_loc()`, `triage_counts()` compute measured figures. Mermaid lessons learned
while rendering:

- A subgraph whose nodes link outside it ignores its `direction` — the pipeline (5.3) and signal map (6.3) were redrawn
  without subgraphs (5.3 as a sequence diagram).
- A `classDef` named `box` renders its node's label at a much smaller size — renamed `ctr` in 2.2.
- Decision flows use rectangles, not diamonds, and `flowchart TB`, so the text stays legible under the 3.6in cap.
- Sequence notes are kept to short lines so the note box does not clip them.

Pagination: every code panel is listed in the Contents, and `brief_pdf._with_marker` makes a listed block
`break-inside:avoid`, so no panel splits across pages whatever `keep` says (`keep=False` only skips the compare / panel's
own `.keep` rule). Pages are packed by ordering and sizing the unbreakable blocks (panels, diagrams, charts, card bands)
around the breakable ones (stories, tables): the Python side of 3.1 is 21 lines so the compare fits under the §3 story;
the two card bands hold 3 cards each and were trimmed so both sit on one page; chart 4.6 is 470 × 265; the pipeline (5.1
to 5.3) precedes the two Terraform panels (5.4, 5.5). The lesson-local CSS also keeps every `h2` with what follows it (a
table heading printed alone at a page foot before) and lets links wrap at spaces. At this build no page except the last
is more than about a third empty: the largest gaps are page 20 (28%), page 8 (25%) and page 11 (22%), measured with
PyMuPDF as the last ink on the page against the content band.

## 6 · Inputs

`roster.py`; samples:

| Project | Kind | Regions read |
|---|---|---|
| `L12.RatingVb` | VB library (`Rating.Quote(coverage, sumInsured, driverAge, licenceYears, claims, commercial, engineCc)`, `PremiumBreakdown`, `CoverageClass`, `QuoteDeclinedException`) — the canonical illustrative tariff | `rating` (not printed) |
| `L12.QuoteLambda` | C# Lambda class library: Annotations functions, `Startup` (DI + SnapStart hooks that drive `RawQuoteHandler`), raw handler, in-memory store, generated `serverless.template` | `annotations`, `startup`, `snapstart`, `raw-cs` (`get` not printed) |
| `L12.QuoteLambdaVb` | VB Lambda class library, hand-written HTTP API v2 handler | `raw-vb` |
| `L12.QuoteLambda.Tests` | xUnit + Amazon.Lambda.TestUtilities: five tariff totals (row 1 is the worked example, 8,933.71 THB) + the three-claims decline, functions (201 / 400 / 422 / 404), generated wrapper, C# ↔ VB parity on four bodies (16 test cases) | `wrapper-test` |
| `L12.QuoteContainer` | ASP.NET Core API: SDK container publish settings, Lambda hosting adapter, OpenTelemetry, health checks | whole `.csproj`, `hosting`, `telemetry`, `health`, `endpoint` |
| `L12.QuoteContainer.Tests` | xUnit + `WebApplicationFactory` + in-memory OTel exporter: health, shutdown budget, the worked-example total, the 422 decline, spans (6 test cases) | `span-test` |
| `L12.EstateTriage` | C# console: 7 R triage of `estate.csv` (illustrative 16-app inventory) | `rules` (`program` not printed) |
| `infra/main.tf` | Terraform sketch (not applied): Lambda + SnapStart + alias, HTTP API, ECS task + target group | `lambda`, `ecs` (`api` not printed — 5.4's note says the HTTP API integration is in `main.tf` and not printed) |
| `ci/deploy.yml` | GitHub Actions workflow (inactive: not under `.github/workflows/`) | `build`, `ship` (`oidc` not printed) |

Sources (all linked in the PDF): AWS docs — Lambda runtimes; C# handler; C# logging; ASP.NET on Lambda; Native AOT;
SnapStart; SnapStart .NET hooks; SnapStart best practices; Lambda Managed Instances .NET runtime; API Gateway HTTP API
quotas; ECS task definition parameters; CDK in C#; Aspire integrations (SDK for .NET v4); X-Ray → OpenTelemetry
migration; AWS Transform for .NET; Prescriptive Guidance migration strategies; Powertools for AWS Lambda (.NET). AWS
Compute Blog — .NET 10 runtime; .NET 8 runtime. Microsoft Learn — container publish configuration; default Ubuntu tags;
port 8080 change; .NET container images; Generic Host; IIS hosting; .NET observability with OpenTelemetry; porting
overview; technologies unavailable on .NET 6+; ASP.NET Framework → Core migration; incremental migration; Web Forms →
Blazor. .NET Blog — CoreWCF 1.0. GitHub docs — OIDC in AWS. GitHub — terraform-provider-aws #45888; release pages of the
five actions. aspire.dev — What's new in Aspire 13. Version checks: nuget.org flat-container API (Amazon.Lambda.*,
OpenTelemetry, CoreWCF, System.Web adapters, YARP, Aspire.Hosting.AWS) and the GitHub releases API.

## 7 · Invariants

- The C# raw handler, the VB raw handler and the Annotations function must keep answering identically (status and body)
  — `HandlerParityTests` and 3.4's note depend on it.
- `HostOptions.ShutdownTimeout` stays below the ECS `stopTimeout` in `main.tf` (test
  `Shutdown_timeout_fits_inside_the_ecs_stop_timeout`; notes 4.2, 5.2; diagram 4.4).
- The handler string in `main.tf` names the generated class `QuoteFunctions_CreateQuote_Generated` (matches
  `serverless.template` and panel 5.1's note).
- The SnapStart before-snapshot hook (`Startup.cs` #region snapstart) calls `RawQuoteHandler` with a serialised
  `QuoteRequest` and must stay free of side effects (that handler saves nothing); the 3.5 note says the generated wrapper is
  not warmed by it.
- The triage rules keep a `vb6` + `desktop` arm above the generic `vb6` arm; `agent-commission` (desktop) therefore
  targets `desktop`, and panel 7.3, charts 7.4 / 7.5 and the 7.3 note depend on the captured counts.
- Every host calls `L12.RatingVb`, whose rules are the canonical tariff (`_curriculum.md` § "Canonical tariff"); rates stay
  illustrative and are labelled so. A request carries `licenceYears` and `engineCc` besides the old fields, and
  `QuoteDeclinedException` (three or more claims) is answered with HTTP 422 by all four hosts (Annotations function, raw C#
  handler, raw VB handler, container API).
- Estate rows stay fictional application names — no employer, client or product names (privacy, `_standard.md` §7).
- `main.tf` must keep passing `terraform validate` if its comment says so; `deploy.yml` stays outside `.github/workflows/`.
- The build raises if the test-case count or the estate size no longer matches the captured panels.

## 8 · Known gaps

- ⚠ Nothing is deployed: the Lambda, SnapStart hooks, OTLP export and ECS settings are verified by compilation, in-process
  tests and documentation, not by running on AWS. SnapStart hooks are registered in tests but never executed.
- ⚠ No cold-start, latency or cost numbers — none were measured; the hosting rubric (2.3) is a judgement.
- ⚠ Captured figures (zip sizes, image layers, publish output, triage output, test summary) are pasted constants; the
  size figures depend on package versions and the base image on 2026-09-20. Rerun the commands in 8.1 and update
  `PACKAGES`, `LAYERS` and the panels after any sample or SDK change.
- ⚠ The `terraform validate` check ran once by hand on a scratch copy with hashicorp/aws 6.64.0 and Terraform 1.13.0 (no
  terraform binary exists on the build machine); it is not part of `verify_samples.py`, `~> 6.0` floats, and the workflow
  file is not linted by any tool here. The ECS task in `main.tf` has no OpenTelemetry collector sidecar or
  `OTEL_EXPORTER_OTLP_ENDPOINT`, and 5.5's note says so.
- ⚠ The SnapStart hook warms the raw handler's JSON and rating path only; the generated Annotations wrapper (DI scope, body
  binding, response envelope) is not exercised before the snapshot.
- ⚠ Lambda Annotations' VB support is stated as "documented for C#"; VB was not tried with the generator.
- ⚠ Inline Python in 3.1 is not executed; `COVERAGE`, `quote` and `InMemoryQuoteStore` are assumed helpers.
- ⚠ The test projects use xUnit v2 packages (as most lessons do at this build); the xUnit v3 story belongs to lesson 10.
- ⚠ `_manifest.json` in this folder lists only lesson 01; adding lesson 12 is the curriculum owner's change.
- ⚠ `_curriculum.md` (plan for lesson 12, item 6) still says "the 6 Rs" and "an 80+ application estate"; the lesson teaches the
  AWS 7 Rs (AWS Prescriptive Guidance) and ships a 16-application inventory, citing 80+ only as the reader's prior experience.
  The curriculum is not this lesson's file: fix it there.
- ⚠ The decline is an exception in the VB library and a 422 in every host; the Python sketch in 3.1 leaves it to its assumed
  helpers (the 3.1 note says so). `QuoteRequest` and `StoredQuote` are flat wire types (decimal, string id) on purpose — the
  story names lesson 03's `Money` / `QuoteId` structs they are not.
- ⚠ The compressed size of the MotorQuote layer (about 0.55 MB) and the manifest digests change from run to run by tens of
  bytes; 4.5, 4.6 and the KPI are one captured run, not a reproducible byte count.
