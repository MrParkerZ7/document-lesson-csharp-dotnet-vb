# Unit spec — lesson-11-security-identity.pdf

Built to `_standard.md`. Content module `0-script/lessons/lesson_11.py`. Samples
`lesson-11-security-identity/samples/`. Plan: `_curriculum.md` § "11 · Security & Identity with Entra ID".

## 1 · Purpose

Show a Spring Security / NestJS / Zuul architect who has integrated Entra ID, Azure AD B2C, Auth0 and Cognito where
ASP.NET Core puts each security decision, which of its defaults differ from what they know (clock skew, audience
validation, inbound claim mapping, no protection without metadata), how to pick an OAuth flow and a credential per
caller, how to layer authorization between a YARP gateway, endpoint policies and a resource handler, how to keep
secrets and Data Protection keys out of trouble, and how Forms / Windows authentication estates map onto .NET 10.
Every behaviour claimed is either tested, printed by a lab sample, or linked to an official source.

## 2 · Ownership & cadence

Owner **claude**, regenerable. Re-verify every November (new .NET major) and when a cited date passes:
Microsoft.Identity.Web version (4.14.2 on 2026-09-16), Azure AD B2C status (closed to new customers since
1 May 2025, supported to at least May 2030), the workload identity federation scenario list (AWS via IAM outbound
identity federation), CodeQL's language list (C# up to 14, no Visual Basic), SonarQube's VB.NET support, NuGet audit
defaults for `net10.0`, the .NET 10 cookie-redirect breaking change, the Auth0 `permissions` claim setting, and
OWASP Top 10:2025 category names. Re-capture the five output panels (3.2, 3.6, 7.5, 8.4, 9.5) whenever a sample's
`Console.WriteLine` or the test count changes, and update `TESTS_PASSED` / `TEST_SUMMARY` in the module.

## 3 · Structure

| § | Heading | Blocks |
|---|---|---|
| — | Contents | `toc` depth 2 · style block (callouts kept whole, story and panel headings kept with their first line, link labels wrap at spaces, compact Contents so it stays on page 1) |
| 1 | Why this lesson — the security you have shipped, in .NET terms | story (4 paragraphs) · `kpi` 1.1 (5 tiles) · `legend` (architecture, cloud — the only tags used) · info callout "Before you start" (4) |
| 2 | The model — schemes, policies and the pipeline | story · mapping 2.1 (14 rows, Spring Security / NestJS → ASP.NET Core) · code 2.2 (`pipeline`) · mermaid 2.3 flowchart (401 / 403 / 429 origins: policy first, then authenticated? → 401 or 403) · code 2.4 (`order-trap` test) · code 2.5 (`fallback-trap` test: 200 without a fallback policy, 401 with one) |
| 3 | Tokens — what JwtBearer checks, and what it renames | story · code 3.1 (TokenLab `cases`) · code 3.2 (captured TokenLab output) · chart 3.3 bar (clock skew seconds) · compare 3.4 (C# `has-scope` ↔ VB `has-scope`) · code 3.5 (VB `read-user`) · code 3.6 (captured ClaimsVb output part 1) · twocol 3.7 (delegated vs app-only tokens) |
| 4 | Entra ID, External ID and the other authorities | story · table 4.1 (Entra, External ID, B2C, Auth0, Cognito) · code 4.2 (`jwt-bearer`) · code 4.3 (`entra`: repeats the claim and clock-skew settings of 4.2) |
| 5 | Flows — who gets a token for whom | story · cards 5.1 in three bands of two: auth code + PKCE, on-behalf-of · client credentials, workload identity federation · gateway token relay, secrets · mermaid 5.2 sequenceDiagram (customer → gateway → API → OBO → partner) · code 5.3 (`downstream`) · code 5.4 (`appsettings.json` `"AzureAd"` — the `SignedAssertionFilePath` credential, cut from the file) |
| 6 | Authorization design — policies, resources and the gateway | story · compare 6.1 (Kotlin Spring Security DSL ↔ C# `policies`) · code 6.2 (`read-endpoint`) · code 6.3 (`owner-handler`) · code 6.4 (Gateway `gateway-policies`) · compare 6.5 (Spring Cloud Gateway YAML ↔ YARP `"Routes"` cut from `L11.Gateway/appsettings.json`) |
| 7 | Secrets and hardening — STRIDE for one API | story · chart 7.1 heatmap (OWASP Top 10:2025 rubric) · table 7.2 (STRIDE: threat, control, evidence) · code 7.3 (`hardening`) · code 7.4 (ProtectLab `protect`) · code 7.5 (captured ProtectLab output) |
| 8 | VB and legacy — Forms and Windows authentication | story · table 8.1 (Framework piece → .NET 10 replacement, with Kind chips) · mermaid 8.2 flowchart (choosing the replacement login) · code 8.3 (VB `legacy-principal`) · code 8.4 (captured ClaimsVb output part 2) |
| 9 | Hands-on — test-signed tokens and a 401/403/200 matrix | story · code 9.1 (`test-tokens`) · code 9.2 (`factory`) · code 9.3 (`matrix`) · code 9.4 (commands) · code 9.5 (captured `dotnet test` summary) · chartrow 9.6 hbar (test cases per class) + 9.7 bar (lines per project) · chartrow 9.8 heatmap (status matrix) + 9.9 donut (outcomes) · warn "Traps" (5) · ok checkpoint (4) · summary "Check yourself" (7, covering §2–§7 including the gateway / enumeration question) · footer (Next: lesson 12) |

Counts checked by `lint_blocks`: 9 numbered stories · 1 mapping · 3 cards bands (2 + 2 + 2) · 3 mermaid (flowchart,
sequenceDiagram, flowchart) · 6 charts · 27 code panels (24 `code` + 3 `compare`) · C# ↔ VB compare 3.4 ·
Kotlin ↔ C# compare 6.1 · YAML ↔ JSON compare 6.5 · twocol 3.7 · 3 extra tables · 43 distinct links (the 40 of the
first build returned HTTP 200 on 2026-09-16; the three added since — Configure OpenID Connect web authentication,
Azure Key Vault configuration provider, SonarQube VB.NET analysis — were fetched on 2026-09-20).
Rendered: 22 A4 pages.

## 4 · Derivation

- **KPI "Default clock skew 5 min"** and chart 3.3 ".NET default" — MEASURED: parsed at build from the captured
  TokenLab line `DefaultClockSkew = 00:05:00`; VERIFIED against the `TokenValidationParameters.DefaultClockSkew`
  API page (300 seconds).
- **KPI sub "Spring Security: 60 s"** and chart 3.3 "Spring default" — VERIFIED: Spring Security reference,
  OAuth 2.0 Resource Server JWT ("a clock skew of 60 seconds"; `aud` not validated unless configured).
- **Chart 3.3 "L11 API" / "L11 gateway"** — MEASURED: `_skew_seconds()` parses `ClockSkew = TimeSpan.FromSeconds(N)`
  from `AuthenticationSetup.cs` (both registrations, `jwt-bearer` and `entra`; the build fails unless there are at
  least two and they agree) and from `L11.Gateway/Program.cs`. `Entra_registration_derives_the_authority_from_the_AzureAd_section`
  asserts the Entra path's 30 s skew and `NameClaimType`, so the bar cannot drift from the registration it names.
- **Chart 3.3 note (gateway 502)** — an observation, not a test, and worded so: on 2026-09-16, with the gateway's
  `ClockSkew` line commented out, `GatewayTests` expected 401 for a token expired two minutes earlier and received
  502 (no destination is reachable in the test); the line was restored. No committed test reproduces it.
- **KPI "Azure AD B2C closed"** — VERIFIED: External ID FAQ (P1/P2 not available to new customers from 1 May 2025;
  support until at least May 2030).
- **KPI "Status matrix 36 cases"**, heatmap 9.8 and donut 9.9 — MEASURED: `_status_matrix()` parses the endpoint list
  and the `matrix` region of `StatusMatrixTests.cs`; heat-map values are an ordinal encoding (allowed < 403 < 401),
  labels are the real status codes. 9 callers × 4 endpoints. Donut counts: 11 allowed · 12 × 401 · 13 × 403. The 9.8
  note names the three 403 cells decided by the owner handler: `other-customer` read and accept, `underwriter-rw`
  accept; the `underwriter` and `back-office-app` accept 403s come from policy `quotes.write` (6.3 note).
- **KPI "Lesson 11 tests 47"**, chart 9.6 and panel 9.5 — MEASURED: `_test_cases()` counts `[Fact]` = 1,
  `[InlineData]` = 1, `[MemberData]` = matrix rows × endpoints per `*Tests.cs` class, and raises if the total differs
  from `TESTS_PASSED` (47), the count of the captured `dotnet test` run. Per class: StatusMatrixTests 36,
  SecurityBehaviourTests 4, MiddlewareOrderTests 4, GatewayTests 3.
- **KPI "Lesson 11 samples" and chart 9.7** — MEASURED: `loc()` over the `.cs` / `.vb` files of each of the six
  projects (at the final build: API 240, Tests 281, ClaimsVb 79, TokenLab 56, ProtectLab 42, Gateway 24). The 9.7
  note names the largest project from the data.
- **Chart 7.1 heatmap** — ESTIMATE: the author's rubric (tested / shown / —) for six OWASP Top 10:2025 categories
  and the five sample projects; labelled "a rubric, not a benchmark" in the caption, which also says that A05, A06,
  A08 and A10 are not scored, and "Estimate" in the note. Category names VERIFIED against top10.owasp.org/2025.
- **Output panels 3.2, 3.6, 7.5, 8.4 and 9.5** — captured from real runs of `L11.TokenLab`, `L11.ClaimsVb`,
  `L11.ProtectLab` and `dotnet test` on the build machine (Windows 11, SDK 10.0.401, runtimes 10.0.12); the three
  console outputs were re-run and compared on 2026-09-20, the test summary (47 passed, 275 ms) was captured on the
  same day. The test summary is wrapped before the file name (said in the note).
- **Order trap 2.4 and fallback trap 2.5** — MEASURED: `MiddlewareOrderTests` passes all four cases (authentication
  first → 200; authorization first → 401 for the same token; endpoint with no metadata → 200 without and 401 with a
  fallback policy).
- **Claim-mapping facts in §3** — MEASURED by `L11.ClaimsVb` output and `Default_claim_mapping_renames_scp_so_the_owner_gets_403`;
  default `MapInboundClaims = true` VERIFIED on the API page.
- **Audience fails closed** — MEASURED: TokenLab case "API sets no audience" → `SecurityTokenInvalidAudienceException`.
  The Cognito advice (4.2 note, §4, table 4.1) therefore names `ValidateAudience = false` plus a `client_id` /
  `token_use` check; leaving `Audience` unset alone rejects every token.
- **Gateway routes (6.5) and the credential file (5.4)** — read from `L11.Gateway/appsettings.json` and
  `L11.SecureQuoteApi/appsettings.json` by `json_block()` at build (original formatting, dedented); the Spring Cloud
  Gateway side is inline YAML, not compiled.
- **VERIFIED statements** (each linked where it appears): middleware order (CORS before authentication, auto-added
  auth middleware), fallback policy scope, `ClaimsPrincipal.Current` not set in ASP.NET Core, .NET 8 switch to
  `JsonWebTokenHandler`, PAR used by default from .NET 9 when the server supports it, Entra `scp` / `roles` / `sub` /
  `oid` / v2 `aud` = client ID / group overage at 200, separate role names for users and apps, IDW10201 without scope
  or roles, default App ID URI needs no audience, Auth0 `scope` intersection and the separate "Add Permissions in the
  Access Token" setting for the `permissions` claim, Cognito `aud` only with a resource binding, implicit and ROPC not
  recommended, OBO user-tokens-only and aud requirement, client credentials `.default` and role-less app tokens
  without assignment, workload identity federation scenarios and case-sensitive matching, AWS `GetWebIdentityToken`
  lifetime 60–3,600 s default 300 s, Microsoft.Identity.Web credential ranking and `SignedAssertionFilePath`,
  distributed token cache for several instances, YARP `default` / `anonymous` / no-policy behaviour and header
  flow, resource-based authorization, user-secrets unencrypted and Development-only, Key Vault configuration provider
  with a managed identity, SSM configuration provider `/aws/reference/secretsmanager/`,
  `PersistKeysToAWSSystemsManager`, Data Protection 90-day keys and AES-256-CBC + HMACSHA256, API HTTPS guidance (no
  redirect, no HSTS), bearer tokens and CSRF, NuGetAuditMode `all` for `net10.0`, CodeQL languages, SonarQube VB.NET
  analysis in Server and Community Build, `GenericPrincipal : ClaimsPrincipal`, Windows authentication on IIS
  (`web.config`) versus Negotiate on Kestrel / HTTP.sys and its intranet positioning, .NET 10 cookie 401/403 for API
  endpoints, cookie sharing with OWIN and System.Web adapters. Dated facts carry a Verified chip.

## 5 · Presentation

Format 00 via `brief_pdf.py`; code panels from `lesson_kit`, listed in the Contents with the lesson-01 `listed()`
helper (which also strips Pygments' red error box around VB interpolated strings). Three additions live in the
lesson's own style block and helper, not in the kit:

- `listed()` prints the panel heading as the block's first `.ct` child, so the renderer pins the Contents marker to
  the heading instead of making the whole panel unbreakable. A panel over 18 lines (and any panel passed
  `keep=False`) may therefore split across pages; `.code .ch` and `.codeblk > .ct` keep the file bar with the
  heading and the first lines (`orphans` / `widows` 4). Panels 3.5, 4.2, 6.2, 7.3, 7.4 and 9.2 (15–18 lines) are
  `keep=False` for this reason. Without it the first rebuild with the new content was 24 pages, with gaps of 25–30 % after each jumped panel.
- The Contents is compacted (`.toc` line height and padding) so it stays on page 1 under the banner; at its
  natural size it jumped whole to page 2 and left page 1 empty.
- Callouts are `break-inside: avoid` (the Check-yourself list must not split), and link labels wrap at spaces
  (`.story a.lnk` etc.) instead of mid-word.

Mermaid 2.3 is `flowchart TB` with a `direction LR` middleware subgraph, an init directive for tighter spacing and a
grey `style MW` box named in the caption; the 429 edge is labelled `UseRateLimiter: over the limit` because
mermaid attaches both outgoing edges to the subgraph border. 5.2 is a `sequenceDiagram` coloured by an init
directive with 16px fonts and short messages; 8.2 is a 4-column `flowchart LR` (a 6-column version was an unreadable
strip and a `TB` version a narrow column). The pipeline panel 2.2 precedes diagram 2.3 so the breakable table 2.1 and
the small panel fill the page before the unbreakable diagram. Endpoint 6.2 precedes handler 6.3. In §7 the OWASP
heatmap comes before the STRIDE table so the breakable table, not the chart, meets the page boundary. The two
chartrows of §9 are ordered smaller first (tests / lines, then heat map / donut) for the same reason. Heatmaps use
cell 40 (7.1) and 36 (9.8); 7.1 at cell 27 printed overlapping labels. Compare sides ≤ 62 characters and code panels ≤
100 (no width warnings at the final build). Cards are bands of two (a band never splits across pages).

Pagination at the final build (empty share of each page, PyMuPDF): pages 1–22 all ≤ 20 %, except the last (69 %,
the Check-yourself list and the footer). Largest interior gaps: page 10 (20 %, the fifth and sixth flow cards do not
fit under the first four), pages 12, 16 and 19 (14 % each).

## 6 · Inputs

`roster.py`; samples:
- `L11.SecureQuoteApi` (web, build-only): `Program.cs` (provider switch, policies + fallback, CORS, partitioned
  rate limiter, pipeline, endpoints), `Security/AuthenticationSetup.cs` (plain JwtBearer; Microsoft.Identity.Web
  with token acquisition and a downstream API, both with `MapInboundClaims = false`, `NameClaimType`,
  `RoleClaimType` and a 30 s `ClockSkew`), `Security/QuoteClaims.cs`, `Security/QuoteAuthorizationHandler.cs`,
  `Partners/PartnerRatesClient.cs` (OBO and client-credentials calls, compiled, not run), `Quotes/QuoteStore.cs`
  (illustrative premiums), `appsettings.json` (placeholder tenant, `SignedAssertionFilePath` credential,
  `DownstreamApis:PartnerRates`). Packages: JwtBearer 10.0.12, Microsoft.Identity.Web and .DownstreamApi 4.14.2.
- `L11.Gateway` (web, build-only): YARP 2.3.0 with JwtBearer and two route policies; three routes, each naming an
  `AuthorizationPolicy`, in `appsettings.json` (nested regions `gateway` ⊃ `gateway-policies` in `Program.cs`).
- `L11.SecureQuoteApi.Tests` (xUnit v2, `Microsoft.AspNetCore.Mvc.Testing` 10.0.12): `TestTokens`, `TestKeyFactory`,
  `StatusMatrixTests` (9 callers × 4 endpoints, including `underwriter-rw`), `GatewayTests`, `SecurityBehaviourTests`,
  `MiddlewareOrderTests` (order trap and fallback trap) — 47 cases.
- `L11.TokenLab` (C# console, `Microsoft.IdentityModel.JsonWebTokens` 8.22.0): eight tokens against one parameter set.
- `L11.ProtectLab` (C# console, `FrameworkReference Microsoft.AspNetCore.App`): time-limited protector, purposes,
  tampering, expiry and separate in-memory key rings.
- `L11.ClaimsVb` (VB console, `Option Strict On`): validation with mapping on and off, `HasScope` extension,
  a `GenericPrincipal` read as claims.

Sources (all linked in the PDF): Microsoft Learn — Middleware order · Require authenticated users · Migrate from
static ClaimsPrincipal access · Map, customize and transform claims · Configure OpenID Connect web authentication ·
JwtBearerOptions.MapInboundClaims · TokenValidationParameters.DefaultClockSkew · Security token events return a
JsonWebToken · Access token claims reference · Verify scopes and app roles · Configure protected web API apps ·
External ID FAQ · Implicit grant flow · ROPC grant · On-behalf-of flow · Client credentials flow · Call downstream
APIs from web APIs · Workload identity federation · Credentials overview for Microsoft.Identity.Web ·
Resource-based authorization · YARP authentication and authorization · Safe storage of app secrets in development ·
Azure Key Vault configuration provider · Data Protection key management and lifetime · Configure Data Protection ·
Enforce HTTPS · Prevent cross-site request forgery · Auditing package dependencies · GenericPrincipal · Configure
Windows Authentication · Cookie login redirects disabled for API endpoints · Share authentication cookies among
ASP.NET apps · Integration tests in ASP.NET Core. GitHub — AzureAD/microsoft-identity-web ·
aws/aws-dotnet-extensions-configuration · aws/aws-ssm-data-protection-provider-for-aspnet · CodeQL supported
languages. SonarSource docs — VB.NET analysis. AWS docs — Cognito access token · IAM outbound identity federation.
Spring Security reference — Resource Server JWT. Auth0 docs — RBAC for APIs. OWASP Top 10:2025.

## 7 · Invariants

- Tests never contact an identity provider: `TestKeyFactory` sets `Authority = null` and a local
  `OpenIdConnectConfiguration`; issuer, audience, lifetime and signature are still validated.
- `StatusMatrixTests` keeps one `("caller", [s1, s2, s3, s4])` row per line and the endpoint list before
  `#region callers`: `_status_matrix()` parses both, so 9.8 / 9.9 and the KPI cannot drift from the test.
- `TESTS_PASSED` equals the parsed case count; the build fails otherwise.
- Both apps — and both API registrations — configure `MapInboundClaims = false`, `RoleClaimType = "roles"` and the
  same 30 s `ClockSkew`; the Entra registration's options are asserted by a test.
- The API derives the quote owner from `sub`, never from the body; accept stays owner-only, and it is the handler
  (not a policy) that refuses `other-customer` and `underwriter-rw`.
- The API does not call `UseHttpsRedirection` or `UseHsts` (documented in the `pipeline` comment and §7).
- ProtectLab uses in-memory key rings only (it writes no keys to the user profile).
- Every premium is illustrative; tenant and client IDs are zero-filled placeholders; every host except Entra's public
  sign-in address (`login.microsoftonline.com`, the `AzureAd:Instance` value) ends in `example.test`.
- Boundaries: hosting, DI, options, middleware basics → lesson 08; test frameworks and `WebApplicationFactory`
  basics → lesson 10; NuGet audit configuration → lesson 07; VB migration → lesson 06; incremental migration with
  YARP / System.Web adapters, forwarded headers, OpenTelemetry → lesson 12. Each gets one sentence and `ref(n)`.
- No employer, client or personal names (grep of the module, samples, spec and PDF text on 2026-09-20: none).

## 8 · Known gaps

- ⚠ Nothing contacts Entra ID: the Microsoft.Identity.Web registration is checked only through its options, and the
  on-behalf-of / client-credentials calls in `PartnerRatesClient` compile but never run; the `SignedAssertionFilePath`
  path in 5.4 is illustrative.
- ⚠ The Kotlin Spring Security panel in 6.1 and the Spring Cloud Gateway YAML in 6.5 are not compiled; the ROLE_
  authorities in 6.1 assume a custom JWT converter.
- ⚠ Output panels are pasted text; the test duration (275 ms) varies per run.
- ⚠ Rubric 7.1 is a judgement and scores 6 of the 10 OWASP categories; OWASP A09 (logging and alerting) is
  deliberately shown as not covered.
- ⚠ Table 4.1 rows for External ID and Azure AD B2C describe claim sources in general terms; no External ID or B2C
  tenant was used to capture a token. The Auth0 and Cognito rows come from their documentation, not from captured
  tokens.
- ⚠ Decision logging for repudiation (table 7.2) is recommended but not implemented in the samples.
- ⚠ The gateway 502 observation (3.3 note) depends on the test having no reachable destination and was made by hand;
  it is labelled as an observation.
- ⚠ Two code panels split across a page break by design (2.4 and 6.3) and the STRIDE table 7.2 continues on the next
  page with its header repeated; 22 pages is the top of the standard's range, so further additions need matching cuts.
