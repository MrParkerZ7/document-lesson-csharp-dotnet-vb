# -*- coding: utf-8 -*-
"""Lesson 11 — Security & Identity with Entra ID. Built to 1-analysis/spec_lesson-pdfs/_standard.md; shape follows
lesson_01.py. Unit spec: 1-analysis/spec_lesson-pdfs/lesson-11-security-identity.md"""
import re

from lesson_kit import (DIFFERENT, ESTIMATE, MEASURED, REPO, RENAMED, SAME, TRAP, VERIFIED, T_ARCH, T_CLOUD, code,
                        compare, esc, from_sample, from_text, legend, link, loc, mapping, pill, snippet,
                        style_block)
from lessons.roster import meta, ref

META = meta(
    11,
    subtitle="Authentication schemes, authorization policies, JWT validation, Entra ID and the OAuth flows, a YARP "
             "gateway, secrets and hardening — proven by a 401/403/200 test matrix",
    objectives=[
        "Wire authentication and authorization in ASP.NET Core in the right order, and say which layer produces "
        "a 401, a 403 and a 429",
        "Configure JwtBearer against Entra ID, External ID, Auth0 or Cognito, and name the three defaults that "
        "differ from Spring Security: clock skew, audience and claim mapping",
        "Choose the OAuth flow for each caller — authorization code with PKCE, on-behalf-of, client credentials, "
        "workload identity federation — and implement the API side with Microsoft.Identity.Web",
        "Design authorization in layers: coarse route policies at a YARP gateway, scope and role policies per "
        "endpoint, and resource-based checks for one quote",
        "Keep secrets out of the repository, share a Data Protection key ring, and map a STRIDE review of one API "
        "to controls you can test",
        "Test all of it with locally signed tokens and WebApplicationFactory — no tenant, no network",
    ],
    maps_from="Spring Security resource servers and SecurityFilterChain, NestJS guards, gateway-level authorization "
              "in Zuul, and single sign-on with Entra ID, Azure AD B2C, Auth0 and Cognito — plus the Forms and "
              "Windows authentication still running in .NET Framework estates on IIS.",
)

L = "lesson-11-security-identity/samples"
API = f"{L}/L11.SecureQuoteApi"
API_PROGRAM = f"{API}/Program.cs"
AUTH_SETUP = f"{API}/Security/AuthenticationSetup.cs"
CLAIMS = f"{API}/Security/QuoteClaims.cs"
HANDLER = f"{API}/Security/QuoteAuthorizationHandler.cs"
PARTNERS = f"{API}/Partners/PartnerRatesClient.cs"
GATEWAY = f"{L}/L11.Gateway/Program.cs"
TESTS = f"{L}/L11.SecureQuoteApi.Tests"
MATRIX_TESTS = f"{TESTS}/StatusMatrixTests.cs"
TOKEN_LAB = f"{L}/L11.TokenLab/Program.cs"
PROTECT_LAB = f"{L}/L11.ProtectLab/Program.cs"
VB = f"{L}/L11.ClaimsVb/Program.vb"
PROJECTS = ["L11.SecureQuoteApi", "L11.Gateway", "L11.SecureQuoteApi.Tests", "L11.TokenLab", "L11.ProtectLab",
            "L11.ClaimsVb"]

# ── official sources ─────────────────────────────────────────────────────────────────────────
MIDDLEWARE = link("Middleware order", "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/middleware/")
FALLBACK = link("Require authenticated users",
                "https://learn.microsoft.com/en-us/aspnet/core/security/authorization/secure-data#require-authenticated-users")
CURRENT = link("Migrate from static ClaimsPrincipal access",
               "https://learn.microsoft.com/en-us/aspnet/core/migration/fx-to-core/areas/claimsprincipal-current")
CLAIMMAP = link("Map, customize and transform claims",
                "https://learn.microsoft.com/en-us/aspnet/core/security/authentication/claims")
MAPINBOUND = link("JwtBearerOptions.MapInboundClaims",
                  "https://learn.microsoft.com/en-us/dotnet/api/microsoft.aspnetcore.authentication.jwtbearer.jwtbeareroptions.mapinboundclaims")
SKEW = link("TokenValidationParameters.DefaultClockSkew",
            "https://learn.microsoft.com/en-us/dotnet/api/microsoft.identitymodel.tokens.tokenvalidationparameters.defaultclockskew")
JWT8 = link("Security token events return a JsonWebToken",
            "https://learn.microsoft.com/en-us/aspnet/core/breaking-changes/8/securitytoken-events")
SPRINGJWT = link("Spring Security: OAuth 2.0 Resource Server JWT",
                 "https://docs.spring.io/spring-security/reference/servlet/oauth2/resource-server/jwt.html")
CLAIMSREF = link("Access token claims reference",
                 "https://learn.microsoft.com/en-us/entra/identity-platform/access-token-claims-reference")
SCOPEROLES = link("Verify scopes and app roles",
                  "https://learn.microsoft.com/en-us/entra/identity-platform/scenario-protected-web-api-verification-scope-app-roles")
APICONFIG = link("Configure protected web API apps",
                 "https://learn.microsoft.com/en-us/entra/identity-platform/scenario-protected-web-api-app-configuration")
MIW = link("microsoft-identity-web", "https://github.com/AzureAD/microsoft-identity-web")
EXTFAQ = link("External ID FAQ", "https://learn.microsoft.com/en-us/entra/external-id/customers/faq-customers")
COGNITO = link("Cognito access token", "https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-the-access-token.html")
AUTH0RBAC = link("Auth0 RBAC for APIs", "https://auth0.com/docs/get-started/apis/enable-role-based-access-control-for-apis")
IMPLICIT = link("Implicit grant flow", "https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-implicit-grant-flow")
ROPC = link("ROPC grant", "https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth-ropc")
CLIENTCREDS = link("Client credentials flow",
                   "https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-client-creds-grant-flow")
OBO = link("On-behalf-of flow", "https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-on-behalf-of-flow")
DOWNSTREAM = link("Call downstream APIs from web APIs",
                  "https://learn.microsoft.com/en-us/entra/msidweb/call-downstream-apis/from-web-apis")
WIF = link("Workload identity federation", "https://learn.microsoft.com/en-us/entra/workload-id/workload-identity-federation")
CREDS = link("Credentials overview for Microsoft.Identity.Web",
             "https://learn.microsoft.com/en-us/entra/msidweb/authentication/credentials-overview")
AWSOUT = link("IAM outbound identity federation",
              "https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_outbound_getting_started.html")
RESOURCE = link("Resource-based authorization",
                "https://learn.microsoft.com/en-us/aspnet/core/security/authorization/resourcebased")
YARPAUTH = link("YARP authentication and authorization",
                "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/servers/yarp/authn-authz")
SECRETS = link("Safe storage of app secrets in development",
               "https://learn.microsoft.com/en-us/aspnet/core/security/app-secrets")
SSMCONFIG = link("aws-dotnet-extensions-configuration", "https://github.com/aws/aws-dotnet-extensions-configuration")
SSMDP = link("aws-ssm-data-protection-provider-for-aspnet",
             "https://github.com/aws/aws-ssm-data-protection-provider-for-aspnet")
DPKEYS = link("Data Protection key management and lifetime",
              "https://learn.microsoft.com/en-us/aspnet/core/security/data-protection/configuration/default-settings")
DPCONFIG = link("Configure Data Protection",
                "https://learn.microsoft.com/en-us/aspnet/core/security/data-protection/configuration/overview")
HTTPS = link("Enforce HTTPS", "https://learn.microsoft.com/en-us/aspnet/core/security/enforcing-ssl")
CSRF = link("Prevent cross-site request forgery",
            "https://learn.microsoft.com/en-us/aspnet/core/security/anti-request-forgery")
AUDIT = link("Auditing package dependencies", "https://learn.microsoft.com/en-us/nuget/concepts/auditing-packages")
CODEQL = link("CodeQL supported languages",
              "https://codeql.github.com/docs/codeql-overview/supported-languages-and-frameworks/")
OWASP = link("OWASP Top 10:2025", "https://top10.owasp.org/2025")
PROXY = link("Configure ASP.NET Core to work with proxy servers and load balancers",
             "https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/proxy-load-balancer")
JWTEVENTS = link("JwtBearerEvents",
                 "https://learn.microsoft.com/en-us/dotnet/api/microsoft.aspnetcore.authentication.jwtbearer.jwtbearerevents")
AUTHRESULT = link("Authorization middleware result handler",
                  "https://learn.microsoft.com/en-us/aspnet/core/security/authorization/customizingauthorizationmiddlewareresponse")
GENERIC = link("GenericPrincipal", "https://learn.microsoft.com/en-us/dotnet/api/system.security.principal.genericprincipal")
WINAUTH = link("Configure Windows Authentication",
               "https://learn.microsoft.com/en-us/aspnet/core/security/authentication/windowsauth")
COOKIE10 = link("Cookie login redirects disabled for API endpoints",
                "https://learn.microsoft.com/en-us/aspnet/core/breaking-changes/10/cookie-authentication-api-endpoints")
OIDCWEB = link("Configure OpenID Connect web authentication",
               "https://learn.microsoft.com/en-us/aspnet/core/security/authentication/configure-oidc-web-authentication")
KEYVAULT = link("Azure Key Vault configuration provider",
                "https://learn.microsoft.com/en-us/aspnet/core/security/key-vault-configuration")
SONAR = link("SonarQube: VB.NET analysis",
             "https://docs.sonarsource.com/sonarqube-server/analyzing-source-code/languages/vb-dotnet")
COOKIESHARE = link("Share authentication cookies among ASP.NET apps",
                   "https://learn.microsoft.com/en-us/aspnet/core/security/cookie-sharing")

# ── captured from real runs on the build machine (Windows 11, SDK 10.0.401, runtime 10.0.12, 2026-09-16) ──────
TOKEN_LAB_OUT = """
    DefaultClockSkew = 00:05:00

    valid token               ACCEPTED
    expired 3 min ago         ACCEPTED
    same token, skew 30 s     rejected  SecurityTokenExpiredException
    audience of another API   rejected  SecurityTokenInvalidAudienceException
    API sets no audience      rejected  SecurityTokenInvalidAudienceException
    issuer of another tenant  rejected  SecurityTokenInvalidIssuerException
    signed by a stranger key  rejected  SecurityTokenInvalidSignatureException
    unsigned, alg none        rejected  SecurityTokenInvalidSignatureException
    """
VB_CLAIMS_OUT = """
    One underwriter access token, read twice

    MapInboundClaims = True
      http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier = uw-1
      http://schemas.microsoft.com/identity/claims/scope = Quotes.Read Quotes.Write
      http://schemas.microsoft.com/ws/2008/06/identity/claims/role = Underwriter
      IsInRole("Underwriter") = False
      HasScope("Quotes.Read") = False

    MapInboundClaims = False
      sub = uw-1
      scp = Quotes.Read Quotes.Write
      roles = Underwriter
      IsInRole("Underwriter") = True
      HasScope("Quotes.Read") = True
    """
VB_LEGACY_OUT = """
    A Forms-era principal, read as claims
      http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name = uw-1
      http://schemas.microsoft.com/ws/2008/06/identity/claims/role = Underwriter
      IsInRole("Underwriter") = True
    """
PROTECT_OUT = """
    share link for Q-1001: 104 chars, starts CfDJ8

    same purpose, same key ring  Q-1001
    other purpose                rejected: Error occurred during a cryptographic operation
    one character changed        rejected: Error occurred during a cryptographic operation
    expired a second ago         rejected: The payload expired
    another instance's key ring  rejected: Error occurred during a cryptographic operation
    """
TESTS_PASSED = 49   # `dotnet test` on the build machine: Passed 49, Failed 0 — checked against the parse below
TEST_SUMMARY = ("Passed!  - Failed:     0, Passed:    49, Skipped:     0, Total:    49, Duration: 1 s\n"
                "  - L11.SecureQuoteApi.Tests.dll (net10.0)")
SPRING_SKEW_S = 60  # Spring Security resource server default clock skew — verified (SPRINGJWT)

# Pygments' vbnet lexer has no token for VB 14 interpolated strings, so every `$"` prints inside a red
# error box. The code is valid (the samples compile); drop the box, keep the text (as lesson 01).
_ERROR_SPAN = re.compile(r'<span style="border: 1px solid #F00">(.*?)</span>', re.S)


def listed(block, heading):
    """Copy a code panel's printed heading onto the block so the Contents lists it (as lesson 01)."""
    block.update(heading=heading, toc=2)
    # the printed heading becomes the panel's `.ct` first child: the renderer then pins the Contents marker to it
    # instead of making the whole panel unbreakable, so a panel over 18 lines may split rather than jump a page
    block["html"] = block["html"].replace('<div class="codeh">', '<div class="ct">', 1)
    if "vb" in block.get("_langs", []):
        block["html"] = _ERROR_SPAN.sub(r"\1", block["html"])
    return block


def figure_heading(text):
    """A numbered heading for a block type that prints none of its own (twocol), kept with that block."""
    return {"type": "html", "html": f'<div class="figh"><h2>{esc(text)}</h2></div>', "heading": text,
            "toc": 2, "_keep_with_next": True}


# ── MEASURED figures, read from the samples at build time ───────────────────────────────────
def _sources(project):
    root = REPO / L / project
    return [p.relative_to(REPO).as_posix() for p in sorted(root.rglob("*"))
            if p.suffix in (".cs", ".vb") and not {"bin", "obj"} & set(p.parts)]


def _status_matrix():
    """(endpoints, [(caller, [status per endpoint])]) parsed from StatusMatrixTests — the test's own data."""
    text = (REPO / MATRIX_TESTS).read_text(encoding="utf-8-sig")
    endpoints = re.findall(r'"((?:GET|POST) [^"]+)"', text.split("#region callers")[0])
    rows = [(m.group(1), [int(x) for x in re.findall(r"\d{3}", m.group(2))])
            for m in re.finditer(r'\("([\w-]+)",\s*\[([\d,\s]+)\]\)', snippet(MATRIX_TESTS, "matrix"))]
    if not endpoints or any(len(r) != len(endpoints) for _, r in rows):
        raise ValueError(f"status matrix no longer parses: {endpoints} / {rows}")
    return endpoints, rows


def _test_cases():
    """Cases per test class: [Fact] = 1, each [InlineData] = 1, [MemberData] = matrix rows × endpoints."""
    endpoints, rows = _status_matrix()
    counts = {}
    for p in sorted((REPO / TESTS).glob("*Tests.cs")):
        text = p.read_text(encoding="utf-8-sig")
        n = len(re.findall(r"\[(?:Fact|InlineData)\b", text))
        n += len(re.findall(r"\[MemberData\(", text)) * len(rows) * len(endpoints)
        counts[p.stem] = n
    if sum(counts.values()) != TESTS_PASSED:
        raise ValueError(f"test cases parsed {counts} = {sum(counts.values())}, but the captured `dotnet test` run "
                         f"passed {TESTS_PASSED}: re-run the tests and update TESTS_PASSED / TEST_SUMMARY")
    return counts


def _skew_seconds(relpath, at_least=1):
    """The ClockSkew a sample sets — every registration in the file must agree (the Entra path once kept 5 min)."""
    text = (REPO / relpath).read_text(encoding="utf-8-sig")
    found = {int(x) for x in re.findall(r"ClockSkew = TimeSpan\.FromSeconds\((\d+)\)", text)}
    n = len(re.findall(r"ClockSkew = TimeSpan\.FromSeconds", text))
    if len(found) != 1 or n < at_least:
        raise ValueError(f"{relpath}: ClockSkew set {n} time(s) to {sorted(found)}; expected {at_least}+ and one value")
    return found.pop()


def json_block(relpath, key):
    """One key of a JSON sample file, cut out with its original formatting and dedented — a config file is read
    from the sample folder, never retyped. Returns a from_text source."""
    lines = (REPO / relpath).read_text(encoding="utf-8-sig").splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.strip().startswith(f'"{key}":'))
    depth, end = 0, None
    for j in range(start, len(lines)):
        depth += sum(lines[j].count(c) for c in "{[") - sum(lines[j].count(c) for c in "}]")
        if depth == 0:
            end = j
            break
    if end is None:
        raise ValueError(f"{relpath}: key {key!r} is never closed")
    text = "\n".join(lines[start:end + 1]).rstrip(",")
    shown = "/".join(relpath.split("/")[2:])   # drop lesson folder and samples/
    return from_text(text, "json", file=f'{shown}  ·  "{key}"')


def _default_skew_seconds():
    m = re.search(r"DefaultClockSkew = (\d\d):(\d\d):(\d\d)", TOKEN_LAB_OUT)
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))


def _sequence_init():
    return ('%%{init: {"theme":"base","themeVariables": {"actorBkg":"#e0e7ff","actorBorder":"#4338ca",'
            '"actorTextColor":"#1f2937","actorLineColor":"#94a3b8","noteBkgColor":"#fef3c7",'
            '"noteBorderColor":"#d97706","noteTextColor":"#1f2937","signalColor":"#334155",'
            '"signalTextColor":"#1f2937","sequenceNumberColor":"#ffffff","fontSize":"16px"},'
            '"sequence": {"messageFontSize": 16, "noteFontSize": 15, "actorFontSize": 16, "width": 130, '
            '"actorMargin": 30, "messageMargin": 24}}}%%\n')


def blocks():
    endpoints, matrix = _status_matrix()
    cases = len(endpoints) * len(matrix)
    tests = _test_cases()
    n_tests = sum(tests.values())
    loc_by = {p: loc(*_sources(p)) for p in PROJECTS}
    vb_lines = loc_by["L11.ClaimsVb"]
    largest = max(loc_by.items(), key=lambda kv: kv[1])
    cs_lines = sum(loc_by.values()) - vb_lines
    default_skew = _default_skew_seconds()
    api_skew, gw_skew = _skew_seconds(AUTH_SETUP, 2), _skew_seconds(GATEWAY)   # both API registrations agree
    codes = [c for _, row in matrix for c in row]
    n_ok = sum(1 for c in codes if c < 300)
    n_401, n_403 = codes.count(401), codes.count(403)
    status_value = {200: 1.0, 201: 1.01, 403: 2.0, 401: 3.0}
    status_label = {v: str(k) for k, v in status_value.items()}
    short_ep = {"GET /quotes/Q-1001": "read", "POST /quotes": "create", "POST /quotes/Q-1001/accept": "accept",
                "GET /underwriting/referrals": "refer."}

    flow_cards = [
        {"num": 1, "title": "Authorization code + PKCE", "tags": [T_ARCH], "pills": [SAME],
         "what": "A user signs in through a browser, mobile or desktop client; the client gets a delegated token.",
         "lines": [("Token", "<code>scp</code> scopes, a user <code>sub</code> and <code>oid</code>"),
                   (".NET", "MSAL in the client; <code>AddOpenIdConnect</code> in a server-rendered app, which uses "
                            "pushed authorization requests from .NET 9 when the provider advertises them (" + OIDCWEB + ")"),
                   ("Retire", "Implicit grant — Microsoft recommends against it and silent renewal breaks without "
                              "third-party cookies (" + IMPLICIT + ")"),
                   ("Retire", "Password grant (ROPC) — incompatible with MFA (" + ROPC + ")")]},
        {"num": 2, "title": "On-behalf-of", "tags": [T_ARCH], "pills": [DIFFERENT],
         "what": "An API calls another API as the same user by exchanging the token it received.",
         "lines": [("Needs", "A confidential client; the incoming token's <code>aud</code> must be this API"),
                   ("Carries", "Delegated scopes only — app roles stay with the user, never the middle tier"),
                   ("Limit", "User tokens only: an app-only token cannot be exchanged (" + OBO + ")"),
                   (".NET", "<code>EnableTokenAcquisitionToCallDownstreamApi</code> + "
                            "<code>IDownstreamApi.GetForUserAsync</code> (5.3)")]},
        {"num": 3, "title": "Client credentials", "tags": [T_ARCH], "pills": [SAME],
         "what": "A daemon or batch job calls an API as itself; there is no user in the token.",
         "lines": [("Token", "Application permissions in <code>roles</code>; no <code>scp</code>"),
                   ("Scope", "Always <code>api://…/.default</code> — the permissions granted to the app"),
                   (".NET", "<code>GetForAppAsync</code>, or MSAL <code>AcquireTokenForClient</code>"),
                   ("Watch", "Users and apps share the <code>roles</code> claim: give them different role "
                             "names (" + SCOPEROLES + ")"),
                   ("Assign", "Unless the API requires assignment, any app in the tenant can get a token with no "
                              "<code>roles</code> — never accept “authenticated” alone (" + CLIENTCREDS + ")")]},
        {"num": 4, "title": "Workload identity federation", "tags": [T_CLOUD], "pills": [DIFFERENT],
         "what": "A workload outside Azure proves who it is with a token from its own platform instead of a secret.",
         "lines": [("From", "GitHub Actions, any Kubernetes cluster including EKS, Google Cloud, SPIFFE, and AWS "
                            "workloads through IAM outbound identity federation (" + WIF + ")"),
                   ("Exchange", "The platform's JWT becomes the client assertion of a client-credentials request"),
                   (".NET", "<code>ClientCredentials</code> with <code>SourceType: SignedAssertionFilePath</code> "
                            "in <code>appsettings.json</code> (" + CREDS + ")"),
                   ("Match", "<code>issuer</code>, <code>subject</code> and <code>audience</code> are compared "
                             "case-sensitively")]},
        {"num": 5, "title": "Gateway token relay", "tags": [T_ARCH], "pills": [RENAMED],
         "what": "A YARP gateway validates the bearer token, applies a route policy and forwards the request.",
         "lines": [("Forwards", "The same <code>Authorization</code> header — the API validates it again"),
                   ("Checks", "Coarse route policies only: it cannot see the quote a request touches"),
                   ("Not", "Windows / Negotiate identity: it is bound to a connection and does not flow through "
                           "the proxy (" + YARPAUTH + ")"),
                   ("Like", "Spring Cloud Gateway or Zuul with a token relay filter")]},
        {"num": 6, "title": "Secrets you should not have", "tags": [T_CLOUD], "pills": [TRAP],
         "what": "Client secrets are the weakest credential; the guidance ranks them last.",
         "lines": [("Secret", "Development and testing only (" + CREDS + ")"),
                   ("Cert", "Production outside Azure when federation is not available"),
                   ("Fed.", "No stored credential to leak, rotate or let expire"),
                   ("AWS", "IAM outbound identity federation issues the JWT: default 300 s, 60–3,600 s allowed "
                           "(" + AWSOUT + ")")]}]

    return [
        style_block(),
        {"type": "toc", "heading": "▤ Contents", "depth": 2,
         "note": "Page numbers are resolved from the rendered PDF. C# and VB panels are cut from the compiled samples; "
                 "outputs and counts marked measured come from real runs of those samples."},
        # a callout heading must not print alone at a page foot with its items on the next page (as lesson 01)
        {"type": "html", "html": "<style>.callout .ct { break-after:avoid; page-break-after:avoid; } "
                                 ".callout li:first-child { break-before:avoid; page-break-before:avoid; } "
                                 ".story .ct { break-after:avoid; page-break-after:avoid; } "
                                 ".story p { orphans:3; widows:3; } "
                                 ".story a.lnk, .cards a.lnk, td a.lnk, .callout a.lnk, .lnote a.lnk "
                                 "{ word-break:normal; overflow-wrap:break-word; } "
                                 ".toc { padding:7px 12px; margin:6px 0 10px; } "
                                 ".toc .trow { line-height:1.1; } .toc .tl1 { margin-top:2px; } "
                                 ".toc .tl2 { font-size:8.4pt; } "
                                 ".codeblk > .ct { font-weight:700; font-size:10pt; color:#1A237E; margin:12px 0 4px; "
                                 "border-bottom:2px solid #C5CAE9; padding-bottom:2px; break-after:avoid; "
                                 "page-break-after:avoid; } "
                                 ".callout { break-inside:avoid; page-break-inside:avoid; } "
                                 ".code .ch { break-after:avoid; page-break-after:avoid; } "
                                 ".code pre { orphans:4; widows:4; }</style>"},

        # ═══════════════════════════ 1 · WHY ═══════════════════════════
        {"type": "story", "heading": "1 · Why this lesson — the security you have shipped, in .NET terms",
         "html": (
             "<p><b>You have secured this kind of API before, and most of the ideas carry over; what changes is where "
             ".NET puts each decision and which defaults it chooses for you.</b> You have built Spring Security "
             "resource servers, NestJS guards and gateway-level authorization in Zuul, and integrated single sign-on "
             "with Entra ID, Azure AD B2C, Auth0 and Cognito. ASP.NET Core has the same parts: an authentication "
             "<i>scheme</i> turns a request into a <code>ClaimsPrincipal</code>, an authorization <i>policy</i> "
             "decides, and both are wired in <code>Program.cs</code> in the order you write them.</p>"
             "<p><b>The defaults are where an experienced engineer from another stack gets hurt.</b> A .NET API "
             f"accepts a token up to {default_skew // 60} minutes after it expired, where Spring allows "
             f"{SPRING_SKEW_S} seconds; it renames <code>scp</code> and <code>roles</code> to long URIs unless you "
             "switch mapping off; and an endpoint with no authorization requirement is public unless you set a "
             "fallback policy. Each is a one-line fix, and each is measured by a sample in this lesson.</p>"
             "<p><b>The identity landscape moved while you were shipping.</b> Azure AD B2C has not been sold to new "
             "customers since 1 May 2025 and is supported until at least May 2030; Microsoft Entra External ID is "
             "the customer-identity product now (" + EXTFAQ + ") " + VERIFIED + ". Workload identity federation lets a GitHub Actions "
             "job, a Kubernetes pod — EKS included — or an AWS workload obtain an Entra token without a client "
             "secret (" + WIF + ").</p>"
             f"<p><b>Every claim here is backed by code that runs.</b> A MotorQuote API, a YARP gateway, {n_tests} "
             f"tests including a {cases}-case status matrix, a token lab, a Data Protection lab and a Visual Basic "
             "console that reads the same claims. The tests sign their own tokens, so none of it needs a tenant or "
             "a network.</p>")},

        {"type": "kpi", "heading": "1.1 · The numbers to leave this lesson with",
         "items": [
             {"label": "Default clock skew", "value": f"{default_skew // 60} min", "tone": "red",
              "sub": f"Spring Security: {SPRING_SKEW_S} s · measured + verified"},
             {"label": "Azure AD B2C", "value": "closed", "tone": "amber",
              "sub": "to new customers since 1 May 2025 · verified"},
             {"label": "Status matrix", "value": f"{cases} cases", "tone": "teal",
              "sub": f"{len(matrix)} callers × {len(endpoints)} endpoints · measured"},
             {"label": "Lesson 11 tests", "value": str(n_tests), "tone": "indigo",
              "sub": "all passing, no tenant needed · measured"},
             {"label": "Lesson 11 samples", "value": f"{cs_lines + vb_lines} lines", "tone": "navy",
              "sub": f"C# {cs_lines} · VB {vb_lines} · {len(PROJECTS)} projects · measured"}]},

        legend(T_ARCH, T_CLOUD),

        {"type": "callout", "variant": "info", "heading": "ℹ Before you start",
         "items": [
             "<b>You need " + ref(8) + "</b> — hosting, dependency injection, options, minimal APIs and middleware — "
             "and the <code>WebApplicationFactory</code> basics of " + ref(10) + ". Async code follows " + ref(5) + ".",
             "<b>You will build six projects:</b> <code>L11.SecureQuoteApi</code> (web API: JwtBearer or "
             "Microsoft.Identity.Web, policies, a resource handler, hardening), <code>L11.Gateway</code> (YARP), "
             "<code>L11.SecureQuoteApi.Tests</code> (xUnit), <code>L11.TokenLab</code> and <code>L11.ProtectLab</code> "
             "(C# consoles) and <code>L11.ClaimsVb</code> (a Visual Basic console).",
             "<b>No Entra tenant is needed.</b> Tests sign tokens with an RSA key created for each test run. The "
             "Entra-specific registration and the downstream partner calls compile, and one test checks the "
             "registration's options, but nothing contacts Microsoft.",
             "Tenant and client IDs are zero-filled placeholders and every host except Entra's public sign-in address "
             "ends in <code>example.test</code>. "
             "Premiums are <b>illustrative, not a real tariff</b>: the quote API prices with the MotorQuote tariff "
             "every lesson shares — Class 1 at 2.1% of the sum insured, 0.4% stamp duty, 7% VAT — reduced to what a "
             "bare sum insured allows (no loadings, no no-claim discount, because the request carries no driver or "
             "claims data)."]},

        # ═══════════════════════════ 2 · THE MODEL ═══════════════════════════
        {"type": "story", "heading": "2 · The model — schemes, policies and the pipeline",
         "html": (
             "<p><b>ASP.NET Core splits security into two services: an authentication scheme says who the caller is, "
             "an authorization policy says what they may do.</b> <code>AddAuthentication().AddJwtBearer()</code> "
             "registers a scheme; <code>UseAuthentication()</code> runs it for each request and stores the result in "
             "<code>HttpContext.User</code>. That is Spring's <code>SecurityContext</code>, but carried by the request "
             "rather than a thread: <code>ClaimsPrincipal.Current</code> and <code>Thread.CurrentPrincipal</code> are "
             "not set by default (" + CURRENT + "). Policies are named requirements registered once and attached to "
             "endpoints with <code>RequireAuthorization(\"name\")</code> or <code>[Authorize(Policy = …)]</code>.</p>"
             "<p><b>A 401 and a 403 come from different places.</b> Authorization evaluates the endpoint's policy first. "
             "When the policy is not satisfied it looks at the caller: no authenticated user means the scheme's "
             "<i>challenge</i>, a 401 with <code>WWW-Authenticate: Bearer</code>; an authenticated user gets "
             "<i>forbid</i>, a 403. A check about one particular quote can only run inside the endpoint, so its "
             "403 comes from there (diagram 2.3).</p>"
             "<p><b>The pipeline is code, so its order is your responsibility.</b> CORS runs before authentication "
             "because a preflight request carries no token, and authentication runs before authorization "
             "(" + MIDDLEWARE + "). Swap the last two and the app compiles, starts and answers a valid token with 401 "
             "— test 2.4 proves it. If you call neither method and the services are registered, "
             "<code>WebApplication</code> adds both right after routing.</p>"
             "<p><b>Nothing is protected until you say so.</b> An endpoint without authorization metadata is public. "
             "A fallback policy applies to every endpoint that names no policy of its own, which turns “forgot the "
             "attribute” from a data leak into a 401 (" + FALLBACK + "). Test 2.5 shows both answers for one "
             "forgotten endpoint.</p>")},

        mapping("2.1 · Concept map — Spring Security and NestJS → ASP.NET Core", [
            ("<code>SecurityFilterChain</code> bean", "<code>UseAuthentication()</code> + <code>UseAuthorization()</code> "
             "in <code>Program.cs</code>", "trap", "Order is statement order; the wrong order still compiles (2.4)"),
            ("<code>SecurityContextHolder</code>", "<code>HttpContext.User</code> — a <code>ClaimsPrincipal</code>, "
             "or a <code>ClaimsPrincipal</code> handler parameter", "renamed", "No static access by default — pass "
             "the principal into services"),
            ("<code>oauth2ResourceServer { jwt { } }</code>", "<code>AddJwtBearer(o =&gt; o.Authority = …)</code>",
             "same", "Discovery document and JWKS keys are fetched and cached for you"),
            ("<code>jwt.audiences</code> (off unless set)", "<code>Audience</code> / <code>ValidAudience</code>",
             "trap", ".NET fails closed: with no audience configured every token is rejected (3.2)"),
            ("<code>JwtTimestampValidator</code>, 60 s skew", "<code>TokenValidationParameters.ClockSkew</code>, 5 min",
             "trap", "Set it: an expired token passed the gateway until it was lowered (3.3)"),
            ("<code>SCOPE_</code> authorities from <code>scp</code>", "The raw <code>scp</code> claim — after "
             "<code>MapInboundClaims = false</code>", "trap", "Default mapping renames claims; one string holds all "
             "scopes (3.4)"),
            ("<code>hasAuthority(\"SCOPE_x\")</code>", "Policy: <code>RequireAssertion(c =&gt; c.User.HasScope(x))</code>",
             "renamed", "<code>RequireClaim(\"scp\", x)</code> compares the whole space-separated string"),
            ("<code>@PreAuthorize(\"hasRole('X')\")</code>", "<code>.RequireAuthorization(\"policy\")</code> or "
             "<code>[Authorize(Policy = …)]</code>", "renamed", "Policies are named once, attached per endpoint"),
            ("<code>PermissionEvaluator</code> / <code>@PostAuthorize</code>", "<code>IAuthorizationService.AuthorizeAsync"
             "(user, quote, op)</code> + a handler", "different", "Imperative: called inside the endpoint, after the quote is loaded (6.3)"),
            ("<code>anyRequest().authenticated()</code>", "<code>SetFallbackPolicy(RequireAuthenticatedUser)</code>",
             "trap", "Not the default: without it, a new endpoint with no metadata is public (2.5)"),
            ("<code>AuthenticationEntryPoint</code> / <code>AccessDeniedHandler</code>", "Scheme challenge → 401 · "
             "forbid → 403", "renamed", "<code>Results.Forbid()</code> inside an endpoint produces the 403"),
            ("NestJS <code>AuthGuard('jwt')</code> + passport-jwt", "JwtBearer scheme + endpoint policy", "same",
             "Guards map to policies; interceptors to middleware or endpoint filters"),
            ("<code>@WithMockUser</code>, MockMvc <code>jwt()</code>", "Test-signed JWT + <code>WebApplicationFactory"
             "</code>", "different", "Real signature, issuer, audience and lifetime checks run in the tests (9)"),
            ("CSRF filter on by default", "Antiforgery for form posts and cookie auth only", "different",
             "Bearer tokens in a header are not sent automatically, so they are not a CSRF target (" + CSRF + ")"),
        ]),

        listed(code(from_sample(API_PROGRAM, "pipeline"), heading="2.2 · The pipeline of L11.SecureQuoteApi",
                    note="<b>Read it top to bottom as the order every request takes.</b> The rate limiter sits between "
                         "authentication and authorization because it partitions by the token's <code>sub</code>, "
                         "which only exists after <code>UseAuthentication</code>. The first comment is a design "
                         "decision explained in section 7: an API does not redirect HTTP to HTTPS. "
                         "<code>UseForwardedHeaders</code> is first so that every later step sees the caller's address, "
                         "not the load balancer's (7.3)."),
               "2.2 · The pipeline of L11.SecureQuoteApi"),

        {"type": "mermaid", "inline": True,
         "heading": "2.3 · Where a 401, a 403 and a 429 come from",
         "caption": "indigo = request · slate = the security middleware in Program.cs order, inside the grey box "
                    "(UseForwardedHeaders runs before it, 7.3) · amber = decision · green = the endpoint runs · "
                    "red = rejected · the 429 leaves the rate limiter",
         "code": ('%%{init: {"flowchart": {"nodeSpacing": 30, "rankSpacing": 34}}}%%\n'
                  "flowchart TB\n"
                  '  REQ["GET /quotes/Q-1001<br/>Authorization: Bearer ..."]:::start\n'
                  '  subgraph MW["Middleware, in the order Program.cs adds it"]\n'
                  "    direction LR\n"
                  '    CORS["UseCors<br/>answers preflights"]:::mw --> AUTHN["UseAuthentication<br/>JwtBearer sets User"]:::mw\n'
                  '    AUTHN --> RL["UseRateLimiter<br/>one bucket per sub"]:::mw --> AUTHZ["UseAuthorization<br/>endpoint policy or fallback"]:::mw\n'
                  "  end\n"
                  "  REQ --> CORS\n"
                  '  RL -- "UseRateLimiter:<br/>over the limit" --> R429["429"]:::bad\n'
                  '  AUTHZ --> Q1{"Policy<br/>satisfied?"}:::q\n'
                  '  Q1 -- "yes" --> EP["Endpoint loads Q-1001<br/>asks IAuthorizationService"]:::ok\n'
                  '  Q1 -- "no" --> Q2{"Caller<br/>authenticated?"}:::q\n'
                  '  Q2 -- "no" --> R401["401 challenge<br/>WWW-Authenticate: Bearer"]:::bad\n'
                  '  Q2 -- "yes" --> R403["403 forbid"]:::bad\n'
                  '  EP -- "not the owner" --> R403B["403 from the endpoint"]:::bad\n'
                  '  EP -- "owner or underwriter" --> R200["200 with the quote"]:::ok\n'
                  "  classDef start fill:#c7d2fe,color:#1f2937,stroke:#6366f1;\n"
                  "  classDef mw fill:#e2e8f0,color:#1f2937,stroke:#475569;\n"
                  "  classDef q fill:#fde68a,color:#1f2937,stroke:#d97706;\n"
                  "  classDef ok fill:#bbf7d0,color:#1f2937,stroke:#16a34a;\n"
                  "  classDef bad fill:#fecaca,color:#1f2937,stroke:#dc2626;\n"
                  "  style MW fill:#f8fafc,stroke:#94a3b8,color:#1f2937;\n")},

        listed(code(from_sample(f"{TESTS}/MiddlewareOrderTests.cs", "order-trap"),
                    heading="2.4 · The same valid token, two middleware orders",
                    note="<b>Both cases pass: the order that runs authorization first returns 401 for a token that "
                         "the other order accepts.</b> <code>UseAuthorization</code> asks whether "
                         "<code>HttpContext.User</code> is authenticated; nothing has authenticated it yet, so it "
                         "challenges. There is no warning at build or start-up — a test like this one is the guard."),
               "2.4 · The same valid token, two middleware orders"),

        listed(code(from_sample(f"{TESTS}/MiddlewareOrderTests.cs", "fallback-trap"),
                    heading="2.5 · An endpoint nobody protected, with and without a fallback policy",
                    note="<b>Without a fallback policy the forgotten endpoint answers an anonymous caller with 200.</b> "
                         "The second case adds one <code>SetFallbackPolicy</code> call and the same request gets 401. "
                         "An endpoint that names its own policy or <code>[AllowAnonymous]</code> is not affected, so "
                         "<code>/health</code> in the API stays open on purpose."),
               "2.5 · An endpoint nobody protected, with and without a fallback policy"),

        # ═══════════════════════════ 3 · TOKENS ═══════════════════════════
        {"type": "story", "heading": "3 · Tokens — what JwtBearer checks, and what it renames",
         "html": (
             "<p><b><code>AddJwtBearer</code> makes the checks a Spring resource server can make — signature, issuer, "
             "lifetime and audience — but two defaults differ.</b> With <code>Authority</code> set, the handler reads "
             "the provider's discovery document, caches its signing keys and, since .NET 8, validates with "
             "<code>JsonWebTokenHandler</code> (" + JWT8 + "). The audience check fails closed: an API that sets no "
             "audience rejects every token, where Spring checks <code>aud</code> only when you configure it "
             "(" + SPRINGJWT + "). Lifetime is lenient: "
             f"<code>TokenValidationParameters.DefaultClockSkew</code> is {default_skew} seconds (" + SKEW + ") " + VERIFIED + ", five "
             "times Spring's 60.</p>"
             "<p><b>Then the handler renames your claims.</b> <code>JwtBearerOptions.MapInboundClaims</code> "
             "defaults to <code>true</code> (" + MAPINBOUND + "): <code>sub</code>, <code>scp</code> and "
             "<code>roles</code> arrive under long WS-Federation-era URIs. Code written against the token as issued — "
             "<code>FindFirst(\"scp\")</code>, <code>RoleClaimType = \"roles\"</code> — then finds nothing, and a "
             "customer with a valid token gets 403 (output 3.6). Set <code>MapInboundClaims = false</code> on every "
             "scheme (" + CLAIMMAP + ").</p>"
             "<p><b>Scopes and roles answer different questions.</b> <code>scp</code> lists what a user allowed this "
             "client to do, as one space-separated string, and appears only in tokens that carry a user. "
             "<code>roles</code> is an array holding the app roles assigned to a user <i>and</i> the application "
             "permissions granted to a daemon (" + CLAIMSREF + "). A policy must accept each one on purpose, and "
             "Microsoft recommends separate role names for users and applications (" + SCOPEROLES + ").</p>")},

        listed(code(from_sample(TOKEN_LAB, "cases"), heading="3.1 · Eight tokens against one set of parameters",
                    note="<b>Each case changes one thing.</b> <code>Mint</code> signs a token that is valid by default; "
                         "an <code>Adjust</code> delegate changes the API's parameters for one case, such as a 30-second "
                         "skew or no audience at all. The loop reports the exception type the handler returns, which "
                         "is what an <code>OnAuthenticationFailed</code> event would see."),
               "3.1 · Eight tokens against one set of parameters"),

        listed(code(from_text(TOKEN_LAB_OUT, "text", label="Output — L11.TokenLab", file="captured on the build machine"),
                    heading="3.2 · What the handler accepted",
                    note="<b>Row two is the surprise: a token that expired three minutes ago is accepted.</b> The "
                         "30-second skew rejects the same token. Rows five and eight are the reassurance: no configured "
                         "audience means rejection, and an unsigned <code>alg: none</code> token fails signature "
                         "validation. " + MEASURED),
               "3.2 · What the handler accepted"),

        {"type": "chart", "heading": "3.3 · How long after exp a token is still accepted", "kind": "bar",
         "args": {"data": [("Spring default", SPRING_SKEW_S), (".NET default", default_skew),
                           ("L11 API", api_skew), ("L11 gateway", gw_skew)],
                  "ylabel": "seconds", "tone": "amber", "width": 560, "height": 165},
         "caption": "Spring default verified · .NET default measured by L11.TokenLab · API (both registrations) "
                    "and gateway parsed from their ClockSkew lines at build",
         "note": (f"<b>Five minutes is long enough to matter at a gateway.</b> With the default skew, "
                  "<code>L11.Gateway</code> accepted a token that had expired two minutes earlier and proxied it: "
                  "the gateway test expected 401 and received 502 (no destination exists in the test). Lowering the "
                  f"skew to {gw_skew} seconds made it reject the token itself. That comparison was made by hand on "
                  "2026-09-16, by commenting the line out — an observation, not a committed test. The bars come from "
                  "the samples at build " + MEASURED + "; Spring's 60 s is " + VERIFIED + ".")},

        listed(compare(from_sample(CLAIMS, "has-scope"), from_sample(VB, "has-scope"),
                       heading="3.4 · Reading scp — the same helper in C# and in Visual Basic",
                       note="<b>Split the one string, then compare ordinally.</b> An exact-value check such as "
                            "<code>RequireClaim(\"scp\", \"Quotes.Read\")</code> fails for a token whose "
                            "<code>scp</code> is <code>\"Quotes.Read Quotes.Write\"</code>. The VB version is a "
                            "<code>&lt;Extension&gt;</code> function in a module; both read the claim by its raw name, "
                            "so both depend on mapping being off."),
               "3.4 · Reading scp — the same helper in C# and in Visual Basic"),

        listed(code(from_sample(VB, "read-user"), heading="3.5 · Validating in Visual Basic, mapping on and off", keep=False,
                    note="<b>A VB library can validate and inspect tokens with the same handler.</b> "
                         "<code>MapInboundClaims</code> is a property of <code>JsonWebTokenHandler</code>; "
                         "<code>JwtBearerOptions.MapInboundClaims</code> sets it for you. Blocking on "
                         "<code>GetResult()</code> is acceptable only in a console <code>Sub Main</code> — "
                         + ref(5) + "."),
               "3.5 · Validating in Visual Basic, mapping on and off"),

        listed(code(from_text(VB_CLAIMS_OUT, "text", label="Output — L11.ClaimsVb (part 1)",
                              file="captured on the build machine"),
                    heading="3.6 · One underwriter token, read twice",
                    note="<b>With mapping on, the role check and the scope check both return False for a token that "
                         "carries both.</b> <code>RoleClaimType = \"roles\"</code> no longer matches the renamed "
                         "claim, and <code>FindFirst(\"scp\")</code> finds nothing. Note that <code>scp</code> is one "
                         "claim with two scopes in its value. " + MEASURED),
               "3.6 · One underwriter token, read twice"),

        figure_heading("3.7 · Delegated tokens and app-only tokens"),
        {"type": "twocol", "boxes": [
            {"heading": "A user is present — delegated", "tone": "indigo",
             "items": ["Issued by authorization code + PKCE, or by on-behalf-of",
                       "<code>scp</code>: one string, the scopes the user consented to for this client",
                       "<code>sub</code> is pairwise per application; <code>oid</code> is the same across the tenant",
                       "<code>roles</code> may also appear: app roles assigned to that user",
                       "In the samples: <code>owner</code>, <code>underwriter</code>, <code>owner-read-only</code>"]},
            {"heading": "No user — app-only", "tone": "teal",
             "items": ["Issued by client credentials, often with a federated assertion",
                       "No <code>scp</code>; application permissions arrive in <code>roles</code>",
                       "Scope requested is always <code>…/.default</code>",
                       "Cannot be exchanged on-behalf-of: there is no user to act for",
                       "In the samples: <code>back-office-app</code> — may read any quote, may accept none"]}]},

        # ═══════════════════════════ 4 · AUTHORITIES ═══════════════════════════
        {"type": "story", "heading": "4 · Entra ID, External ID and the other authorities",
         "html": (
             "<p><b>For Entra ID, <code>Microsoft.Identity.Web</code> is JwtBearer with Entra's rules applied for "
             "you.</b> <code>AddMicrosoftIdentityWebApi(config.GetSection(\"AzureAd\"))</code> builds the authority "
             "from <code>Instance</code> and <code>TenantId</code> — a test in <code>SecurityBehaviourTests</code> asserts "
             "<code>https://login.microsoftonline.com/{tenant}/v2.0</code> — and validates the issuer for "
             "multi-tenant apps. With the default App ID URI you configure no audience; a custom URI goes in "
             "<code>AzureAd:Audience</code> (" + APICONFIG + "). It also refuses a token that carries neither "
             "<code>scp</code> nor <code>roles</code> unless you opt into ACL-based authorization (" + SCOPEROLES + "). "
             "Version 4.14.2 was the latest on NuGet on 2026-09-16 (" + MIW + ") " + VERIFIED + ".</p>"
             "<p><b>Entra v2 tokens name the API by its client ID.</b> The <code>aud</code> claim of a v2 access "
             "token is always the API's client ID, even when the client requested "
             "<code>api://…/Quotes.Read</code> (" + CLAIMSREF + "). A hand-written <code>ValidAudience</code> "
             "copied from the scope string rejects every production token.</p>"
             "<p><b>Any other OpenID Connect provider goes through plain <code>AddJwtBearer</code>, but its claims "
             "differ.</b> With RBAC enabled, Auth0 narrows <code>scope</code> to the intersection of requested and "
             "assigned permissions; it adds a <code>permissions</code> array only when its separate “Add "
             "Permissions in the Access Token” setting is on too (" + AUTH0RBAC + "). A Cognito user-pool access "
             "token carries <code>scope</code>, <code>cognito:groups</code> and <code>client_id</code>, and has an "
             "<code>aud</code> claim only when the app requested a resource binding (" + COGNITO + "). Leaving "
             "<code>Audience</code> unset does not skip that check — JwtBearer then rejects every token, as output "
             "3.2 row 5 shows — so set <code>ValidateAudience = false</code> and check <code>client_id</code> and "
             "<code>token_use</code> yourself, in <code>OnTokenValidated</code> or a policy requirement. Table 4.1 "
             "lines them up.</p>"
             "<p><b>For customer sign-in on a new system, choose External ID.</b> Azure AD B2C P1 and P2 are no longer "
             "sold to new customers, existing tenants keep working, and Microsoft commits to support until at least "
             "May 2030. External ID uses the same MSAL code for workforce and customer scenarios (" + EXTFAQ + ") " + VERIFIED + ".</p>")},

        {"type": "table", "heading": "4.1 · The same API behind five authorities",
         "cols": ["Authority", "Scopes arrive in", "Roles or groups arrive in", ".NET registration", "Watch for"],
         "rows": [
             ["<b>Entra ID</b> (workforce, v2 tokens)", "<code>scp</code> — one string", "<code>roles</code> — "
              "array; <code>groups</code> (object IDs) when configured", "<code>AddMicrosoftIdentityWebApi</code>",
              "<code>aud</code> = client ID; more than 200 groups become an overage claim"],
             ["<b>Entra External ID</b>", "<code>scp</code>", "<code>roles</code>",
              "<code>AddMicrosoftIdentityWebApi</code>, external tenant",
              "Register the API in an <i>external</i> tenant; new customer systems start here, not on B2C"],
             ["<b>Azure AD B2C</b>", "<code>scp</code>", "Claims your user flow or custom policy adds",
              "<code>AddMicrosoftIdentityWebApi</code>",
              pill("Closed to new customers", "amber") + " supported to at least May 2030"],
             ["<b>Auth0</b>", "<code>scope</code>", "<code>permissions</code> array when RBAC and “Add Permissions in "
              "the Access Token” are on",
              "<code>AddJwtBearer</code>", "<code>scope</code> is the intersection of requested and assigned"],
             ["<b>Amazon Cognito</b>", "<code>scope</code>", "<code>cognito:groups</code>", "<code>AddJwtBearer</code>",
              "No <code>aud</code> without a resource binding — set <code>ValidateAudience = false</code>, then "
              "check <code>client_id</code> and <code>token_use</code>"]]},

        listed(code(from_sample(AUTH_SETUP, "jwt-bearer"), heading="4.2 · Any OpenID Connect authority", keep=False,
                    note="<b>Four settings carry the lesson so far.</b> <code>Authority</code> for discovery and keys, "
                         "<code>Audience</code> for this API, <code>MapInboundClaims = false</code> for raw claim "
                         f"names and a {api_skew}-second <code>ClockSkew</code>. For Cognito you would set "
                         "<code>ValidateAudience = false</code> and check <code>client_id</code> and "
                         "<code>token_use</code> in <code>OnTokenValidated</code>: leaving <code>Audience</code> "
                         "unset alone rejects every token (3.2). The rest is unchanged."),
               "4.2 · Any OpenID Connect authority"),

        listed(code(from_sample(AUTH_SETUP, "entra"), heading="4.3 · Entra ID through Microsoft.Identity.Web",
                    note="<b>One chain registers validation and token acquisition, and the library keeps its own "
                         "defaults for claims and skew.</b> The <code>Configure&lt;JwtBearerOptions&gt;</code> call "
                         "runs after the library's own configuration and repeats the claim and clock-skew settings "
                         "of 4.2: without it the skew would still be five minutes. With it the policies work "
                         "unchanged under either provider, and a test asserts the authority, the claim mapping and "
                         "the skew. The in-memory token cache holds downstream tokens per instance; an API that runs "
                         "as several ECS tasks needs <code>AddDistributedTokenCaches</code> (" + DOWNSTREAM + ")."),
               "4.3 · Entra ID through Microsoft.Identity.Web"),

        # ═══════════════════════════ 5 · FLOWS ═══════════════════════════
        {"type": "story", "heading": "5 · Flows — who gets a token for whom",
         "html": (
             "<p><b>Choose the flow by asking who is present: a user at a client, a user behind another API, or no "
             "user at all.</b> A user at a browser, phone or desktop gets a delegated token through authorization "
             "code with PKCE. The implicit grant and the password grant are both flows Microsoft recommends against "
             "(" + IMPLICIT + " · " + ROPC + ").</p>"
             "<p><b>An API that calls another API as the same user exchanges the token it received.</b> That is the "
             "on-behalf-of flow: the quote API sends the customer's token to Entra ID and gets a token for the "
             "partner-rates API that still names the customer. Only delegated scopes travel; the flow works for user "
             "tokens only, and a single-page app hands its token to a confidential middle tier rather than doing the "
             "exchange itself (" + OBO + ").</p>"
             "<p><b>A job with no user uses client credentials, and should not need a secret.</b> The token carries "
             "application permissions in <code>roles</code>. Microsoft.Identity.Web reads its credential from "
             "configuration and ranks client secrets as suitable for development and testing only (" + CREDS + "). "
             "Workload identity federation removes the stored credential: Entra trusts a token from the platform "
             "the job runs on — GitHub Actions, Kubernetes including EKS, or AWS through IAM outbound identity "
             "federation (" + WIF + " · " + AWSOUT + "). This lesson's <code>appsettings.json</code> holds only a "
             "file path to such a token.</p>")},

        {"type": "cards",
         "band": {"title": "5.1 · Six flows and credentials for the MotorQuote platform", "note": "identity view",
                  "tone": "indigo"},
         "cards": flow_cards[:2]},
        {"type": "cards", "toc": False,
         "band": {"title": "5.1 · Six flows and credentials (continued)", "note": "identity view", "tone": "indigo"},
         "cards": flow_cards[2:4]},
        {"type": "cards", "toc": False,
         "band": {"title": "5.1 · Six flows and credentials (continued)", "note": "identity view", "tone": "indigo"},
         "cards": flow_cards[4:]},

        {"type": "mermaid", "inline": True,
         "heading": "5.2 · A customer quote request that calls a rating partner",
         "caption": "indigo = participants · amber notes = where a token is validated · steps 1–2 happen once per "
                    "sign-in; steps 5–6 only when no cached partner token is still valid",
         "code": (_sequence_init() +
                  "sequenceDiagram\n"
                  "  autonumber\n"
                  "  participant C as Customer app\n"
                  "  participant E as Entra ID\n"
                  "  participant G as YARP gateway\n"
                  "  participant A as Quote API\n"
                  "  participant P as Partner rates API\n"
                  "  C->>E: sign in, code + PKCE\n"
                  "  E-->>C: token for Quote API\n"
                  "  C->>G: GET /api/quotes/Q-1001\n"
                  "  Note over G: validate<br/>customer-api\n"
                  "  G->>A: same request and header\n"
                  "  Note over A: validate again<br/>policy, owner\n"
                  "  A->>E: OBO exchange\n"
                  "  E-->>A: token for Partner API\n"
                  "  A->>P: GET rates/Q-1001\n"
                  "  P-->>A: rate\n"
                  "  A-->>C: 200, quote with rate\n")},

        listed(code(from_sample(PARTNERS, "downstream"), heading="5.3 · Calling the partner as the user, and as the API",
                    note="<b>The two calls differ in one word, and in who the partner sees.</b> "
                         "<code>GetForUserAsync</code> runs on-behalf-of with the scopes from "
                         "<code>DownstreamApis:PartnerRates</code>; <code>GetForAppAsync</code> runs client credentials "
                         "with <code>.default</code>. Both compile and are registered when <code>Identity:Provider</code> "
                         "is <code>Entra</code>; neither runs in the tests, because acquiring a token needs a real "
                         "tenant."),
               "5.3 · Calling the partner as the user, and as the API"),

        listed(code(json_block(f"{API}/appsettings.json", "AzureAd"),
                    heading="5.4 · A federated credential is a file path",
                    note="<b>No secret is stored: <code>SignedAssertionFilePath</code> names a file that holds a token "
                         "the platform issued.</b> The pod or job finds that token at the path — for example a "
                         "projected service-account token in Kubernetes — and Microsoft.Identity.Web sends it as the "
                         "client assertion, so there is nothing to rotate. Tenant and client IDs are zero-filled "
                         "placeholders and the path is illustrative (" + CREDS + ")."),
               "5.4 · A federated credential is a file path"),

        # ═══════════════════════════ 6 · AUTHORIZATION DESIGN ═══════════════════════════
        {"type": "story", "heading": "6 · Authorization design — policies, resources and the gateway",
         "html": (
             "<p><b>Put each decision where the data it needs is available.</b> A gateway sees only the token and the "
             "path, so it can check “a valid token” and “an underwriter”. An endpoint policy sees the token and the "
             "operation, so it checks scopes and roles. Only the endpoint that has loaded the quote can check "
             "“is this caller its owner”.</p>"
             "<p><b>Resource-based authorization is how .NET asks about one object.</b> The endpoint loads the quote "
             "and calls <code>IAuthorizationService.AuthorizeAsync(user, quote, QuoteOperations.Read)</code>; an "
             "<code>AuthorizationHandler&lt;OperationAuthorizationRequirement, Quote&gt;</code> decides "
             "(" + RESOURCE + "). The owner comes from the token's <code>sub</code>, never from the request body — "
             "the Spring equivalent is a <code>PermissionEvaluator</code> behind <code>hasPermission</code>.</p>"
             "<p><b>A YARP gateway reuses the same policies, per route, from configuration.</b> Each route names an "
             "<code>AuthorizationPolicy</code>; <code>default</code> and <code>anonymous</code> are special values, "
             "and a route with no policy is not authorized at all unless a fallback policy exists. Bearer headers "
             "flow to the destination unchanged, so the API validates the token again (" + YARPAUTH + "). Treat the "
             "gateway as the first filter, not the only one: in the status matrix the API alone decides every "
             "403 that depends on who owns a quote.</p>")},

        listed(compare(from_text("""
            // Spring Security 6 Kotlin DSL. A JWT converter
            // maps scp to SCOPE_ and roles to ROLE_ authorities.
            @Bean
            fun api(http: HttpSecurity): SecurityFilterChain {
                http {
                    authorizeHttpRequests {
                        authorize("/health", permitAll)
                        authorize(HttpMethod.GET, "/quotes/**",
                            hasAnyAuthority("SCOPE_Quotes.Read",
                                "ROLE_Quotes.Read.All"))
                        authorize(HttpMethod.POST, "/quotes/**",
                            hasAuthority("SCOPE_Quotes.Write"))
                        authorize("/underwriting/**",
                            hasRole("Underwriter"))
                        authorize(anyRequest, authenticated)
                    }
                    oauth2ResourceServer { jwt { } }
                }
                return http.build()
            }
            """, "kotlin", file="the paths-first shape you know"),
                       from_sample(API_PROGRAM, "policies"),
                       heading="6.1 · Access rules — Spring Security paths vs ASP.NET Core named policies",
                       note="<b>Spring maps paths to rules in one place; ASP.NET Core names the rules in one place and "
                            "attaches them to endpoints.</b> <code>SetFallbackPolicy</code> is "
                            "<code>anyRequest().authenticated()</code>. The underwriting policy demands the role "
                            "<i>and</i> a delegated scope, so an app-only token holding an <code>Underwriter</code> "
                            "role would still be refused. The handler registered last answers the per-quote question "
                            "in 6.2 and 6.3."),
               "6.1 · Access rules — Spring Security paths vs ASP.NET Core named policies"),

        listed(code(from_sample(API_PROGRAM, "read-endpoint"), heading="6.2 · Policy first, then the resource check", keep=False,
                    note="<b>Two checks, two kinds of 403.</b> <code>RequireAuthorization(\"quotes.read\")</code> "
                         "rejects a token without the scope before the handler body runs; "
                         "<code>AuthorizeAsync</code>, answered by the handler in 6.3, rejects the right scope on someone "
                         "else's quote. Here "
                         "existence is checked first, so a caller with the read scope can tell a missing quote (404) "
                         "from another customer's (403) — harmless for opaque IDs, an enumeration leak for "
                         "sequential ones like <code>Q-1001</code>."),
               "6.2 · Policy first, then the resource check"),

        listed(code(from_sample(HANDLER, "owner-handler"), heading="6.3 · Who may read or accept this quote",
                    note="<b>A handler succeeds or stays silent.</b> Leaving the requirement unmet is enough to deny; "
                         "calling <code>context.Fail()</code> would also stop any other handler from granting it. "
                         "Accepting a quote is an owner-only operation, so this handler refuses "
                         "<code>other-customer</code> and <code>underwriter-rw</code> in matrix 9.3: both hold the "
                         "write scope. The plain <code>underwriter</code> and the <code>back-office-app</code> never "
                         "reach it — with no <code>Quotes.Write</code> scope, policy <code>quotes.write</code> stops "
                         "them first."),
               "6.3 · Who may read or accept this quote"),

        listed(code(from_sample(GATEWAY, "gateway-policies"),
                    heading="6.4 · The YARP gateway: coarse checks per route",
                    note="<b>The gateway defines two policies and lets every route pick one by name.</b> Above this "
                         "panel in <code>Program.cs</code> sits a second JwtBearer registration that repeats the API's "
                         "claim settings — mapping off, <code>roles</code> as the role claim, the same clock skew — or "
                         "its role check would read a different claim than the API does. The gateway can ask only "
                         "“valid token?” and “underwriter?”: the quote a request touches is invisible to it."),
               "6.4 · The YARP gateway: coarse checks per route"),

        listed(compare(from_text("""
            # Spring Cloud Gateway application.yml, routes only
            routes:
              - id: quotes
                uri: http://quote-api:8080
                predicates: [ "Path=/api/quotes/**" ]
                filters: [ "StripPrefix=1" ]
              - id: underwriting
                uri: http://quote-api:8080
                predicates: [ "Path=/api/underwriting/**" ]
                filters: [ "StripPrefix=1" ]
              - id: health
                uri: http://quote-api:8080
                predicates: [ "Path=/health" ]
            # who may call each route is not here: a security
            # filter chain matches the paths a second time (6.1)
            """, "yaml", label="Spring Cloud Gateway — for comparison", file="the routes you know"),
                       json_block("lesson-11-security-identity/samples/L11.Gateway/appsettings.json", "Routes"),
                       heading="6.5 · Routes — Spring Cloud Gateway vs YARP",
                       note="<b>YARP puts the authorization rule on the route.</b> Each route names an "
                            "<code>AuthorizationPolicy</code> — <code>customer-api</code>, <code>underwriting</code> or "
                            "the built-in <code>anonymous</code> for <code>/health</code> — and YARP reloads the "
                            "configuration without a restart (" + YARPAUTH + "). Spring Cloud Gateway routes only match "
                            "and rewrite; the rule lives in a separate filter chain. The <code>ClusterId</code> points "
                            "at a cluster of destinations defined below these routes in the same file. YARP returns in "
                            + ref(12) + " for incremental migration."),
               "6.5 · Routes — Spring Cloud Gateway vs YARP"),

        # ═══════════════════════════ 7 · SECRETS & HARDENING ═══════════════════════════
        {"type": "story", "heading": "7 · Secrets and hardening — STRIDE for one API",
         "html": (
             "<p><b>Secrets leave the repository, and where possible they stop existing.</b> "
             "<code>dotnet user-secrets</code> keeps development values in an unencrypted JSON file in your profile "
             "and is added to configuration only in the Development environment (" + SECRETS + "). In production, "
             "AWS Systems Manager Parameter Store — including Secrets Manager secrets under "
             "<code>/aws/reference/secretsmanager/</code> — plugs in as a configuration provider "
             "(" + SSMCONFIG + "); on Azure the Key Vault configuration provider does the same and authenticates "
             "with a managed identity (" + KEYVAULT + "). Better still is no secret at all: a federated credential "
             "(section 5).</p>"
             "<p><b>Data Protection is the <code>&lt;machineKey&gt;</code> you now own.</b> It encrypts authentication "
             "cookies, antiforgery tokens and any payload you protect yourself, with AES-256-CBC and HMACSHA256 keys "
             "that rotate every 90 days (" + DPKEYS + ") " + VERIFIED + ". Keys are isolated by purpose string and application name, "
             "and a process with no shared key store has a ring of its own — so a cookie issued by one ECS task is "
             "unreadable on the next. Persist the ring to one store; on AWS, "
             "<code>PersistKeysToAWSSystemsManager</code> does it (" + SSMDP + "). <code>L11.ProtectLab</code> "
             "measures all four failure modes (7.4).</p>"
             "<p><b>Transport and browser controls are narrower for an API than for a site.</b> An API should not "
             "listen on HTTP or should reject it; a redirect arrives after the client has sent its token in clear, "
             "and HSTS is an instruction only browsers obey (" + HTTPS + "). CORS is an allowlist for browsers, "
             "antiforgery matters only for cookie-authenticated form posts, and rate limiting partitions by caller.</p>"
             "<p><b>Supply chain and static analysis are build gates, not reports.</b> For <code>net10.0</code> "
             "projects NuGet audits transitive packages by default (" + AUDIT + "); this repository keeps advisories "
             "as warnings so an old lesson does not break overnight — " + ref(7) + ". CodeQL analyses C# up to "
             "version 14 and ASP.NET Core but lists no Visual Basic support (" + CODEQL + "), so a VB estate needs "
             "another analyser: SonarQube Server and Community Build both analyse VB.NET (" + SONAR + "). Chart 7.1 "
             "scores these samples against the OWASP Top 10, and table 7.2 applies STRIDE to the quote API.</p>")},

        {"type": "chart", "heading": "7.1 · OWASP Top 10:2025 — what the lesson 11 samples cover", "kind": "heatmap",
         "args": {"rows": ["A01 Access control", "A02 Misconfiguration", "A03 Supply chain", "A04 Cryptography",
                           "A07 Authentication", "A09 Logging, alerting"],
                  "cols": ["API", "Gateway", "Tests", "Tokens", "Protect"],
                  "matrix": [[2, 2, 2, 0, 0], [2, 2, 2, 2, 0], [1, 1, 1, 1, 1], [0, 0, 0, 2, 2], [2, 2, 2, 2, 0],
                             [0, 0, 0, 0, 0]],
                  "cell": 36, "tone": "teal", "fmt": lambda v: {2: "tested", 1: "shown", 0: "—"}[int(v)]},
         "caption": "tested = asserted by a test or printed by a lab · shown = configured, not asserted · — = not "
                    "covered · a rubric, not a benchmark · A05, A06, A08 and A10 not scored",
         "note": "<b>The empty row is the honest one.</b> The samples log nothing when a request is denied, and no "
                 "test would notice. The hooks are small and official: <code>JwtBearerEvents.OnAuthenticationFailed</code> "
                 "fires when a token fails validation and <code>OnForbidden</code> when authorization ends in a 403 "
                 "(" + JWTEVENTS + "); an <code>IAuthorizationMiddlewareResultHandler</code> also sees the failed "
                 "requirements of a policy (" + AUTHRESULT + "). Log the subject, path and reason with a structured "
                 "message template — never the token. Where structured logs go is the CloudWatch example of " + ref(12) +
                 "; an alarm on the rate of 401 and 403 answers is left to your monitoring, and this track builds none. "
                 "Supply chain is “shown” only: NuGet audit runs on every restore, no test asserts it. Categories from "
                 + OWASP + "; the scores are the author's judgement " + ESTIMATE},

        {"type": "table", "heading": "7.2 · STRIDE for the quote API — threat, control, evidence",
         "cols": ["Threat", "Against MotorQuote", "Control", "Evidence in the samples"],
         "rows": [
             ["<b>S</b>poofing", "A token from another tenant, another API or a forged key",
              "Issuer, audience and signature validation; no <code>alg: none</code>",
              "Output 3.2 rows 4 and 6–8 · matrix row <code>wrong-audience</code> = 401"],
             ["<b>T</b>ampering", "An edited token or share link",
              "JWT signature; Data Protection MAC", "Output 3.2 stranger key · output 7.5 one character changed"],
             ["<b>R</b>epudiation", "“I never accepted that quote”",
              "The owner comes from the validated <code>sub</code>, never the body; log <code>sub</code> with the "
              "decision", "Owner check in 6.3 · decision logging " + pill("not in the samples", "slate")],
             ["<b>I</b>nformation disclosure", "Customer B reads customer A's quote",
              "Resource-based handler after the scope policy", "Matrix row <code>other-customer</code> = 403 on read"],
             ["<b>D</b>enial of service", "One caller floods <code>GET /quotes/{id}</code>",
              "Fixed-window limiter partitioned by <code>sub</code>", "Throttling test: 200, 200, 429"],
             ["<b>E</b>levation of privilege", "A customer lists referrals; an app accepts a quote",
              "Role + scope policy; accept is owner-only",
              "Matrix rows <code>owner</code> = 403 on referrals, <code>back-office-app</code> = 403 on accept"]]},

        listed(code(from_sample(API_PROGRAM, "hardening"), heading="7.3 · CORS and a per-caller rate limit", keep=False,
                    note="<b>Both are allowlists.</b> CORS names origins, methods and headers and never calls "
                         "<code>AllowCredentials</code>, because this API reads bearer tokens, not cookies. The limiter "
                         "partitions by the token's subject and falls back to the client IP. <b>Behind a load balancer "
                         "that IP is the balancer's,</b> so every anonymous caller shares one bucket. "
                         "<code>UseForwardedHeaders</code> swaps in the <code>X-Forwarded-For</code> value, but only for a "
                         "request that arrives from a known proxy or network, and by default only loopback is known "
                         "(" + PROXY + "). Add the balancer's subnet — <code>Proxy:Network</code> here — and run the "
                         "middleware before the others. <code>ForwardedHeadersTests</code> asserts both outcomes: with the "
                         "network trusted the second caller gets 200, without it 429."),
               "7.3 · CORS and a per-caller rate limit"),

        listed(code(from_sample(PROTECT_LAB, "protect"), heading="7.4 · Five ways to read one protected share link", keep=False,
                    note="<b>One success, four failures, and three of the failures are deliberately "
                         "indistinguishable.</b> <code>ToTimeLimitedDataProtector</code> adds an expiry; a purpose "
                         "string scopes a payload to one use. A wrong purpose, a changed character and a foreign key "
                         "ring all raise the same <code>CryptographicException</code>; only expiry says why. "
                         "<code>NewKeyRing()</code> is in-memory so the lab writes nothing to disk — production "
                         "persists and shares keys (" + DPCONFIG + ")."),
               "7.4 · Five ways to read one protected share link"),

        listed(code(from_text(PROTECT_OUT, "text", label="Output — L11.ProtectLab", file="captured on the build machine"),
                    heading="7.5 · What Data Protection returned",
                    note="<b>The last row is the production incident.</b> Two instances with separate key rings cannot "
                         "read each other's payloads — behind a load balancer, users are signed out at random. "
                         "<code>CfDJ8</code> is the payload's magic header, the same on every run. " + MEASURED),
               "7.5 · What Data Protection returned"),

        # ═══════════════════════════ 8 · VB & LEGACY ═══════════════════════════
        {"type": "story", "heading": "8 · VB and legacy — Forms and Windows authentication",
         "html": (
             "<p><b>Legacy .NET security is claims-based underneath, which makes the code migration smaller than the "
             "configuration migration.</b> Since .NET Framework 4.5, <code>GenericPrincipal</code> — what Forms "
             "authentication code typically put on the thread — inherits from <code>ClaimsPrincipal</code> "
             "(" + GENERIC + "). Its roles surface as the same <code>…/claims/role</code> claim type the default "
             "JwtBearer mapping produces (output 8.4), so a VB rule written against <code>IsInRole</code> keeps "
             "working when handed a modern principal.</p>"
             "<p><b>The plumbing mostly does not move.</b> <code>&lt;authentication mode=\"Forms\"&gt;</code>, "
             "Membership tables, <code>&lt;machineKey&gt;</code> and static <code>ClaimsPrincipal.Current</code> "
             "have no .NET 10 equivalent; table 8.1 maps each to its replacement. Windows authentication is the "
             "exception: an app hosted on IIS still switches it on in <code>web.config</code>, Kestrel and HTTP.sys "
             "use the Negotiate handler, and Microsoft positions it for intranets where users and servers share a "
             "domain (" + WINAUTH + ").</p>"
             "<p><b>.NET 10 changed one cookie default that mixed MVC-and-API estates will notice.</b> Cookie "
             "authentication now answers unauthenticated calls to known API endpoints with 401 and 403 instead of "
             "redirecting to a login page (" + COOKIE10 + ") — right for a JavaScript client, surprising for a page "
             "that relied on the redirect.</p>"
             "<p><b>Old and new applications can share one sign-in during a strangler migration.</b> The System.Web "
             "adapters' remote authentication, or OWIN cookie middleware reading a Data Protection ring shared with "
             "the new app, keeps users signed in across both (" + COOKIESHARE + "). That migration belongs to "
             + ref(12) + ", and moving the VB code itself to " + ref(6) + ". Visual Basic has no ASP.NET Core templates, so "
             "VB stays in libraries that receive a <code>ClaimsPrincipal</code> from a C# host.</p>")},

        {"type": "table", "heading": "8.1 · .NET Framework security pieces and their .NET 10 replacements",
         "cols": [".NET Framework on IIS", "ASP.NET Core on .NET 10", "Kind", "Migration note"],
         "rows": [
             ["Forms authentication, <code>FormsAuthentication.SetAuthCookie</code>",
              "Cookie scheme + OpenID Connect to Entra ID or External ID", DIFFERENT,
              "Stop owning passwords; the IdP signs users in"],
             ["IIS Windows authentication, <code>WindowsPrincipal</code>",
              "<code>web.config</code> on IIS as before; <code>AddNegotiate()</code> on Kestrel or HTTP.sys; or "
              "Entra SSO", SAME, "A Windows identity does not flow through YARP to the API"],
             ["ASP.NET Membership / SimpleMembership tables", "ASP.NET Core Identity, or the external IdP", DIFFERENT,
              "Different schema: migrate users, or move them to the IdP"],
             ["<code>&lt;machineKey&gt;</code>", "Data Protection key ring", RENAMED,
              "Persist and share the ring; keys rotate every 90 days"],
             ["<code>ClaimsPrincipal.Current</code>, <code>Thread.CurrentPrincipal</code>",
              "<code>HttpContext.User</code>, or a <code>ClaimsPrincipal</code> parameter", TRAP,
              "Not set by default: static access finds no user"],
             ["<code>User.IsInRole</code> in code-behind", "Policies; <code>IsInRole</code> still works", SAME,
              "Check which claim type the role arrives under"],
             ["Shared login across old and new apps", "System.Web adapters remote auth, or shared cookies",
              DIFFERENT, "Temporary by design — " + ref(12)]]},

        {"type": "mermaid", "inline": True,
         "heading": "8.2 · Choosing the replacement for a legacy login",
         "caption": "amber = question · slate = legacy starting point · green = target · while old IIS pages still "
                    "serve users, bridge the sign-in with System.Web adapters or a shared cookie (table 8.1)",
         "code": ("flowchart LR\n"
                  '  START["Legacy login<br/>Forms or Windows"]:::old --> Q1{"Who<br/>signs in?"}:::q\n'
                  '  Q1 -- "employees" --> Q2{"Behind a proxy<br/>or cloud host?"}:::q\n'
                  '  Q1 -- "customers<br/>or partners" --> EXT["OIDC to External ID<br/>+ cookie scheme"]:::good\n'
                  '  Q2 -- "no" --> NEG["Windows auth: web.config on IIS<br/>or Negotiate on Kestrel"]:::good\n'
                  '  Q2 -- "yes" --> ENTRA["OIDC to Entra ID<br/>workforce SSO"]:::good\n'
                  "  classDef old fill:#e2e8f0,color:#1f2937,stroke:#475569;\n"
                  "  classDef q fill:#fde68a,color:#1f2937,stroke:#d97706;\n"
                  "  classDef good fill:#bbf7d0,color:#1f2937,stroke:#16a34a;\n")},

        listed(code(from_sample(VB, "legacy-principal"),
                    heading="8.3 · A Forms-era principal read as claims, in Visual Basic",
                    note="<b>No conversion, no adapter.</b> The widening assignment to <code>ClaimsPrincipal</code> "
                         "compiles under <code>Option Strict On</code> because a <code>GenericPrincipal</code> already "
                         "is one. The loop is the same code a .NET 10 library would run over "
                         "<code>HttpContext.User</code>."),
               "8.3 · A Forms-era principal read as claims, in Visual Basic"),

        listed(code(from_text(VB_LEGACY_OUT, "text", label="Output — L11.ClaimsVb (part 2)",
                              file="captured on the build machine"),
                    heading="8.4 · The legacy role, under the long claim type",
                    note="<b>The role claim type printed here is exactly what <code>MapInboundClaims = true</code> "
                         "produced in 3.6.</b> That mapping exists so tokens look like the principals .NET Framework "
                         "code already understood — and new code turns it off. " + MEASURED),
               "8.4 · The legacy role, under the long claim type"),

        # ═══════════════════════════ 9 · HANDS-ON ═══════════════════════════
        {"type": "story", "heading": "9 · Hands-on — test-signed tokens and a 401/403/200 matrix",
         "html": (
             "<p><b>Test security with real tokens, not with a bypass.</b> Replacing authentication with a fake "
             "handler that always succeeds — the .NET cousin of <code>@WithMockUser</code> — exercises policies but "
             "never token validation, which is where sections 2 and 3 found the bugs. These tests sign JWTs with an "
             "RSA key made for the test run and point JwtBearer at that key, so issuer, audience, lifetime and "
             "signature are validated exactly as in production (" + link("Integration tests in ASP.NET Core",
                                                                     "https://learn.microsoft.com/en-us/aspnet/core/test/integration-tests") + ").</p>"
             f"<p><b>The matrix is a threat model you can run.</b> {len(matrix)} callers — anonymous, expired, wrong "
             "audience, the owner, another customer, a read-only owner, an underwriter, an underwriter who also holds "
             "the write scope and a back-office application "
             f"— against {len(endpoints)} endpoints gives {cases} cases with an expected status each. A change that "
             "opens a hole flips a cell and fails the build; the same file is the reviewable specification of who "
             "may do what.</p>"
             f"<p><b>Run everything, then compare with what you saw here.</b> {n_tests} tests across "
             f"{len(tests)} classes, three console labs and two web projects build on SDK 10.0.401 with warnings as "
             "errors.</p>")},

        listed(code(from_sample(f"{TESTS}/TestTokens.cs", "test-tokens"), heading="9.1 · Minting test tokens",
                    note="<b>The claim shapes copy Entra's.</b> <code>scp</code> is one string and <code>roles</code> a JSON "
                         "array, so a test fails for the same reasons production would. Issuer and audience are those "
                         "of the generic OpenID Connect setup in 4.2, where an <code>api://</code> audience is "
                         "legitimate; an Entra v2 token would carry the client ID (4). The "
                         "RSA key exists only in the test process; issuing tokens ten minutes in the past lets a test "
                         "set an expiry that is already over."),
               "9.1 · Minting test tokens"),

        listed(code(from_sample(f"{TESTS}/TestKeyFactory.cs", "factory"), heading="9.2 · Pointing both apps at the test key", keep=False,
                    note="<b><code>ConfigureTestServices</code> runs after the app's own registration.</b> Setting "
                         "<code>Configuration</code> directly skips the discovery request, and "
                         "<code>Authority = null</code> keeps JwtBearer from fetching one. The same generic factory "
                         "serves the API and the gateway; <code>MapInboundClaims</code> is exposed so one test can "
                         "turn the default mapping back on and watch the owner receive 403."),
               "9.2 · Pointing both apps at the test key"),

        listed(code(from_sample(MATRIX_TESTS, "matrix"), heading="9.3 · The expected status of every caller",
                    note="<b>Read it row by row as sentences.</b> The owner may read, create and accept but not list "
                         "referrals; another customer may create a quote but not read or accept Q-1001; an "
                         "underwriter who holds the write scope may read, create and list referrals but not accept "
                         "another customer's quote; the back-office application may read any quote and do nothing else. Heat map 9.8 is parsed "
                         "from this region at build time, so the picture cannot drift from the test."),
               "9.3 · The expected status of every caller"),

        listed(code(from_text("""
            # from the repository root — the SDK pinned by global.json must be installed
            dotnet test lesson-11-security-identity/samples/L11.SecureQuoteApi.Tests
            dotnet run --project lesson-11-security-identity/samples/L11.TokenLab
            dotnet run --project lesson-11-security-identity/samples/L11.ProtectLab
            dotnet run --project lesson-11-security-identity/samples/L11.ClaimsVb

            # or build, test and run every lesson 11 sample
            python 0-script/verify_samples.py --only 11
            """, "shell"), heading="9.4 · Commands",
                    note="<b>No tenant, no secrets, no network.</b> Restore needs nuget.org once; after that everything "
                         "runs offline. The two web projects are build-only in <code>verify_samples.py</code> — the "
                         "tests host them in memory."),
               "9.4 · Commands"),

        listed(code(from_text(TEST_SUMMARY, "text", label="Output — dotnet test", file="captured on the build machine"),
                    heading="9.5 · What you should see",
                    note=f"<b>{n_tests} passed, 0 failed.</b> The summary is one line, wrapped here before the file name; "
                         "the duration varies by machine. The console outputs are panels 3.2, 3.6, 7.5 and 8.4. " + MEASURED),
               "9.5 · What you should see"),

        {"type": "chartrow", "charts": [
            {"heading": "9.6 · Test cases per test class", "kind": "hbar",
             "args": {"data": sorted(tests.items(), key=lambda kv: -kv[1]), "tone": "indigo", "width": 390,
                      "labelw": 170},
             "caption": "[Fact] = 1 · [InlineData] = 1 · [MemberData] = matrix rows × endpoints · parsed at build",
             "note": (f"<b>The matrix is {100 * tests.get('StatusMatrixTests', 0) // n_tests}% of the suite.</b> The "
                      "other classes cover middleware order, claim mapping, the gateway's own rejections, throttling, "
                      "the forwarded-headers trap, "
                      "an anonymous health check and the Entra registration. " + MEASURED)},
            {"heading": "9.7 · Lines of code per project", "kind": "bar",
             "args": {"data": [(p.replace("L11.", "").replace("SecureQuoteApi", "API"), n) for p, n in loc_by.items()],
                      "ylabel": "lines", "tone": "navy", "width": 390, "height": 200, "rotate_labels": True},
             "caption": "non-blank, non-comment lines of .cs and .vb per project · measured at build",
             "note": (f"<b>{largest[0].replace('L11.', '')} is the largest project, at {largest[1]} lines.</b> "
                      f"The API ({loc_by['L11.SecureQuoteApi']} lines) and its tests ({loc_by['L11.SecureQuoteApi.Tests']}) "
                      f"are the same order of size: proving the rules takes about "
                      f"{loc_by['L11.SecureQuoteApi.Tests'] / loc_by['L11.SecureQuoteApi']:.1f}× the code that writes them. " + MEASURED + " — a size signal, not a quality score.")}]},

        {"type": "chartrow", "charts": [
            {"heading": "9.8 · The status matrix as a heat map", "kind": "heatmap",
             "args": {"rows": [c for c, _ in matrix], "cols": [short_ep.get(e, e) for e in endpoints],
                      "matrix": [[status_value[s] for s in row] for _, row in matrix],
                      "cell": 36, "tone": "slate", "fmt": lambda v: status_label[v]},
             "caption": "read = GET quote · create = POST /quotes · accept = POST accept · refer. = GET referrals · "
                        "parsed from StatusMatrixTests at build",
             "note": "<b>The darker the cell, the earlier the request stopped.</b> The top three rows are uniformly "
                     "401: those callers carry no valid identity, so the failed policy ends in a challenge. The 403 "
                     "cells below them are the authorization design of section 6 — three of them, "
                     "<code>other-customer</code> reading and accepting Q-1001 and <code>underwriter-rw</code> "
                     "accepting it, are decided by the owner handler rather than a policy. " + MEASURED},
            {"heading": "9.9 · Outcomes across the matrix", "kind": "donut",
             "args": {"data": [("2xx allowed", n_ok), ("401", n_401), ("403", n_403)],
                      "center": str(cases), "sub": "cases", "width": 390, "height": 200, "thickness": 34},
             "caption": "count of expected statuses in the matrix region · blue = allowed · teal = 401 · amber = 403",
             "note": (f"<b>Only {n_ok} of {cases} cases are allowed.</b> A security matrix that is mostly green is "
                      "testing the happy path; this one spends most of its cases on the ways a request must fail. "
                      + MEASURED)}]},

        {"type": "callout", "variant": "warn", "heading": "⚠ Traps",
         "items": [
             "<b>“My claim is called <code>scp</code>.”</b> Not with the default <code>MapInboundClaims = true</code>: "
             "it is <code>http://schemas.microsoft.com/identity/claims/scope</code>, and <code>roles</code> is renamed "
             "too. Set <code>MapInboundClaims = false</code> on every scheme, including the gateway's (3.6).",
             f"<b>“An expired token is rejected.”</b> For {default_skew // 60} more minutes it is not. Lower "
             "<code>ClockSkew</code>, especially at a gateway that forwards what it accepts (3.3).",
             "<b>“Authentication middleware is registered, so the endpoint is protected.”</b> Only endpoints with "
             "authorization metadata are; set a fallback policy (2.5). And put <code>UseAuthentication</code> before "
             "<code>UseAuthorization</code> — the reverse compiles and returns 401 (2.4).",
             "<b>“The audience is my <code>api://</code> URI.”</b> Entra v2 tokens carry the API's client ID; "
             "Cognito access tokens may carry no <code>aud</code> at all (4).",
             "<b>“Each instance can make its own keys.”</b> A Data Protection ring per ECS task means cookies and "
             "protected links fail on the next task. Persist and share the ring (7.5)."]},

        {"type": "callout", "variant": "ok", "heading": "✔ Checkpoint — you are ready for lesson 12 when",
         "items": [
             f"<code>python 0-script/verify_samples.py --only 11</code> reports {len(PROJECTS)}/{len(PROJECTS)} "
             "passed on your machine.",
             "You can explain every cell of matrix 9.3 by pointing at the policy, handler or validation step that "
             "produces it.",
             "Given a Spring Security configuration, you can write the equivalent policies and name the three "
             "defaults you must change.",
             "You can choose between authorization code + PKCE, on-behalf-of, client credentials and workload identity "
             "federation for a new caller, and say which claim the API checks for each."]},

        {"type": "callout", "variant": "summary", "heading": "🔍 Check yourself",
         "items": [
             "A request with a valid token gets 401. Name two causes this lesson demonstrated.",
             "What is the default <code>ClockSkew</code> in .NET, what is Spring Security's, and why does the "
             "difference matter more at a gateway?",
             "Why does <code>RequireClaim(\"scp\", \"Quotes.Read\")</code> reject a token whose scopes include "
             "Quotes.Read?",
             "Which claim carries application permissions in an app-only Entra token, and why can that token not be "
             "used on-behalf-of?",
             "What does a Cognito access token lack that JwtBearer checks by default, and what do you validate "
             "instead?",
             "Why can the YARP gateway not return the 403 for another customer reading Q-1001, and what does checking "
             "that the quote exists before checking its owner reveal to a caller?",
             "Why do an API's instances need one Data Protection key ring, and what happens without it?"]},

        {"type": "footer",
         "html": ("<b>Lesson 11 in one line:</b> ASP.NET Core authenticates with schemes and authorizes with named "
                  "policies in a pipeline whose order you write; set <code>MapInboundClaims = false</code>, a short "
                  "<code>ClockSkew</code> and a fallback policy, check one resource inside the endpoint, prefer "
                  "federated credentials to secrets, and prove it all with test-signed tokens."
                  "<br/><b>Next:</b> " + ref(12) + " — deploying this API to AWS Lambda and containers, and "
                  "modernising the Windows / IIS estates it replaces.")},
    ]
