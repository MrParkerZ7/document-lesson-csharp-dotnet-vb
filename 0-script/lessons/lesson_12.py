# -*- coding: utf-8 -*-
"""Lesson 12 — Cloud-Native .NET on AWS & Modernization. Built to 1-analysis/spec_lesson-pdfs/_standard.md;
unit spec 1-analysis/spec_lesson-pdfs/lesson-12-cloud-native-modernization.md."""
import re

from lesson_kit import (BUILD_DATE, DIFFERENT, ESTIMATE, MEASURED, REPO, RENAMED, SAME, TRAP, VERIFIED,
                        T_ARCH, T_CLOUD, T_LEGACY, T_PY, code, compare, days_until, esc,
                        from_sample, from_text, legend, link, loc, mapping, pill, snippet, style_block)
from lessons.roster import meta, ref

META = meta(
    12,
    subtitle="Ship MotorQuote to AWS Lambda and ECS Fargate from one VB rating library — Annotations, SnapStart, "
             "SDK container images, Terraform, OIDC, OpenTelemetry — then triage a .NET Framework estate",
    objectives=[
        "Choose between Lambda (managed dotnet10, SnapStart, Native AOT, Managed Instances), ECS Fargate and EC2 "
        "Windows + IIS from a workload's traffic shape, latency budget and legacy constraints",
        "Write, test and package a .NET Lambda function with Lambda Annotations, register SnapStart hooks, and "
        "read the handler string Lambda actually calls",
        "Publish a multi-architecture, non-root, chiseled container image with dotnet publish and no Dockerfile, "
        "and make it shut down inside the ECS stop timeout",
        "Describe both targets in Terraform, deploy them from GitHub Actions with OIDC, and emit OpenTelemetry "
        "traces, metrics and structured logs that reach X-Ray and CloudWatch",
        "Triage a .NET Framework / IIS estate with the AWS 7 Rs, map each API family to its .NET 10 replacement, "
        "and plan an incremental migration with YARP and System.Web adapters",
    ],
    maps_from="Python Lambda functions tuned for cold start and package size, Spring and NestJS services on ECS "
              "Fargate, Terraform estates of 1,000–2,000+ resources, GitHub Actions pipelines, and the Windows "
              "(IIS) workloads in an 80+ application migration inventory.",
)

L = "lesson-12-cloud-native-modernization/samples"
RATING = f"{L}/L12.RatingVb/Rating.vb"
FUNCS = f"{L}/L12.QuoteLambda/QuoteFunctions.cs"
STARTUP = f"{L}/L12.QuoteLambda/Startup.cs"
RAW_CS = f"{L}/L12.QuoteLambda/RawQuoteHandler.cs"
RAW_VB = f"{L}/L12.QuoteLambdaVb/QuoteHandler.vb"
LAMBDA_TESTS = f"{L}/L12.QuoteLambda.Tests/QuoteLambdaTests.cs"
API = f"{L}/L12.QuoteContainer/Program.cs"
API_PROJ = f"{L}/L12.QuoteContainer/L12.QuoteContainer.csproj"
API_TESTS = f"{L}/L12.QuoteContainer.Tests/ContainerApiTests.cs"
TRIAGE = f"{L}/L12.EstateTriage/Triage.cs"
ESTATE = f"{L}/L12.EstateTriage/estate.csv"
TF = f"{L}/infra/main.tf"
CI = f"{L}/ci/deploy.yml"

# ── official sources ─────────────────────────────────────────────────────────────────────────
RUNTIMES = link("Lambda runtimes", "https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html")
NET10 = link(".NET 10 runtime now available in AWS Lambda",
             "https://aws.amazon.com/blogs/compute/net-10-runtime-now-available-in-aws-lambda/")
NET8 = link("Introducing the .NET 8 runtime for AWS Lambda",
            "https://aws.amazon.com/blogs/compute/introducing-the-net-8-runtime-for-aws-lambda/")
HANDLER = link("Define Lambda function handler in C#",
               "https://docs.aws.amazon.com/lambda/latest/dg/csharp-handler.html")
SNAP = link("Lambda SnapStart", "https://docs.aws.amazon.com/lambda/latest/dg/snapstart.html")
SNAPHOOKS = link("SnapStart runtime hooks for .NET",
                 "https://docs.aws.amazon.com/lambda/latest/dg/snapstart-runtime-hooks-dotnet.html")
SNAPBEST = link("Maximize SnapStart performance",
                "https://docs.aws.amazon.com/lambda/latest/dg/snapstart-best-practices.html")
AOT = link("Compile .NET Lambda code to a native runtime format",
           "https://docs.aws.amazon.com/lambda/latest/dg/dotnet-native-aot.html")
LMI = link(".NET runtime for Lambda Managed Instances",
           "https://docs.aws.amazon.com/lambda/latest/dg/lambda-managed-instances-dotnet-runtime.html")
LOGS = link("Log and monitor C# Lambda functions", "https://docs.aws.amazon.com/lambda/latest/dg/csharp-logging.html")
ASPLAMBDA = link("Deploy ASP.NET applications to Lambda",
                 "https://docs.aws.amazon.com/lambda/latest/dg/csharp-package-asp.html")
POWERTOOLS = link("Powertools for AWS Lambda (.NET)", "https://docs.aws.amazon.com/powertools/dotnet/")
HTTPQUOTA = link("HTTP API quotas", "https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-quotas.html")
CONTAINERS = link("Containerize a .NET app reference",
                  "https://learn.microsoft.com/en-us/dotnet/core/containers/publish-configuration")
UBUNTU = link("Default .NET container tags now use Ubuntu",
              "https://learn.microsoft.com/en-us/dotnet/core/compatibility/containers/10.0/default-images-use-ubuntu")
PORT8080 = link("Default ASP.NET Core port changed from 80 to 8080",
                "https://learn.microsoft.com/en-us/dotnet/core/compatibility/containers/8.0/aspnet-port")
IMAGES = link(".NET container images", "https://learn.microsoft.com/en-us/dotnet/core/docker/container-images")
ECSPARAMS = link("ECS task definition parameters",
                 "https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definition_parameters.html")
HOST = link(".NET Generic Host in ASP.NET Core",
            "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/host/generic-host")
GHOIDC = link("Configuring OpenID Connect in AWS",
              "https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws")
TFISSUE = link("terraform-provider-aws #45888", "https://github.com/hashicorp/terraform-provider-aws/issues/45888")
CDK = link("Working with the AWS CDK in C#", "https://docs.aws.amazon.com/cdk/v2/guide/work-with-cdk-csharp.html")
ASPIRE = link("What's new in Aspire 13", "https://aspire.dev/whats-new/aspire-13/")
ASPIREAWS = link("Integrating AWS with Aspire",
                 "https://docs.aws.amazon.com/sdk-for-net/v4/developer-guide/aspire-integrations.html")
OTEL = link(".NET observability with OpenTelemetry",
            "https://learn.microsoft.com/en-us/dotnet/core/diagnostics/observability-with-otel")
XRAY = link("Migrating from X-Ray instrumentation to OpenTelemetry",
            "https://docs.aws.amazon.com/xray/latest/devguide/xray-sdk-migration.html")
SEVENRS = link("About the migration strategies",
               "https://docs.aws.amazon.com/prescriptive-guidance/latest/large-migration-guide/migration-strategies.html")
PORTING = link("Upgrade .NET apps overview", "https://learn.microsoft.com/en-us/dotnet/core/porting/")
UNAVAILABLE = link(".NET Framework technologies unavailable on .NET 6+",
                   "https://learn.microsoft.com/en-us/dotnet/core/porting/net-framework-tech-unavailable")
FXCORE = link("Migrate from ASP.NET Framework to ASP.NET Core",
              "https://learn.microsoft.com/en-us/aspnet/core/migration/fx-to-core/")
INCREMENTAL = link("Get started with incremental migration",
                   "https://learn.microsoft.com/en-us/aspnet/core/migration/fx-to-core/start")
COREWCF = link("CoreWCF 1.0 has been released", "https://devblogs.microsoft.com/dotnet/corewcf-v1-released/")
TRANSFORM = link("Modernizing .NET with AWS Transform",
                 "https://docs.aws.amazon.com/transform/latest/userguide/dotnet.html")
ECSWIN = link("Windows on Fargate",
              "https://docs.aws.amazon.com/AmazonECS/latest/developerguide/windows-considerations.html")
IIS = link("Host ASP.NET Core on Windows with IIS", "https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/iis/")
WEBFORMS = link("Migrate from ASP.NET Web Forms to Blazor",
                "https://learn.microsoft.com/en-us/dotnet/architecture/blazor-for-web-forms-developers/migration")
ACTIONS = {  # latest release tag of each action, read from GitHub on 2026-09-16
    "actions/checkout": ("v7", "https://github.com/actions/checkout/releases"),
    "actions/setup-dotnet": ("v6", "https://github.com/actions/setup-dotnet/releases"),
    "aws-actions/configure-aws-credentials": ("v6", "https://github.com/aws-actions/configure-aws-credentials/releases"),
    "aws-actions/amazon-ecr-login": ("v2", "https://github.com/aws-actions/amazon-ecr-login/releases"),
    "hashicorp/setup-terraform": ("v4", "https://github.com/hashicorp/setup-terraform/releases"),
}

# ── captured from real runs on the build machine (SDK 10.0.401, runtime 10.0.12, 2026-09-16) ──────────────
# `dotnet publish -c Release -o <dir>` per project, the folder zipped with deflate: (label, bytes, files)
PACKAGES = [("C# Annotations + DI", 807_838, 40), ("C# linux-arm64 publish", 722_956, 38),
            ("VB raw handler", 77_209, 9)]
# `dotnet publish -t:PublishContainer -p ContainerArchiveOutputPath=…`, compressed layer sizes read from the
# OCI manifests in the archive, in the order of the image history (see §4 table)
LAYERS = {"linux-x64": {"rootfs": 5_804_040, "home": 121, "runtime": 36_600_647, "symlink": 152,
                        "aspnet": 12_738_514, "app": 548_564},
          "linux-arm64": {"rootfs": 4_718_454, "home": 120, "runtime": 34_453_760, "symlink": 150,
                          "aspnet": 12_232_531, "app": 547_784}}
CAPTURED_TESTS = 16          # the two "Passed!" lines of panel 8.2
TF_PROVIDER = "6.64.0"       # hashicorp/aws resolved by `terraform init` for `~> 6.0`, then `terraform validate`

TRIAGE_OUTPUT = """
Triage of 16 applications (illustrative inventory)
  policy-portal     net48   Refactor   ECS Fargate      Blazor pages strangled behind YARP
  quote-engine      net472  Replatform ECS Fargate      ASP.NET Core + System.Web adapters
  partner-gateway   net48   Replatform ECS Fargate      CoreWCF; gRPC for new callers
  claims-intake     net48   Replatform ECS Fargate      ASP.NET Core + System.Web adapters
  broker-desktop    net48   Retain     desktop          retarget net10.0-windows in place
  premium-batch     net48   Refactor   Lambda           event-driven function per job
  renewal-notices   net472  Replatform ECS Fargate      BackgroundService; MSMQ becomes SQS
  doc-generator     net40   Rehost     EC2 Windows/IIS  lift as-is; port once COM/GAC is gone
  agent-commission  vb6     Refactor   desktop          rewrite in C# for .NET: VB6 is COM, not .NET
  rates-admin       net8.0  Replatform ECS Fargate      retarget net10.0 + container publish
  payment-callbacks net8.0  Replatform ECS Fargate      retarget net10.0 + container publish
  legacy-reports    net35   Retire     -                archive the data, switch it off
  hr-leave          -       Repurchase SaaS             replace with the vendor's SaaS
  fx-rates-feed     net472  Replatform ECS Fargate      port to net10.0
  sms-dispatch      net48   Replatform ECS Fargate      port to net10.0
  vehicle-lookup    net48   Rehost     EC2 Windows/IIS  lift as-is; port once COM/GAC is gone
By strategy (7 Rs):
  Retire      1
  Retain      1
  Rehost      2
  Relocate    0
  Repurchase  1
  Replatform  8
  Refactor    3
By target:
  ECS Fargate      9
  desktop          2
  EC2 Windows/IIS  2
  Lambda           1
  -                1
  SaaS             1
"""

# Pygments marks tokens it does not know (VB `$"` interpolation) with a red error box. The code is valid
# (the samples compile); drop the box, keep the text. (kit request — as lesson 01)
_ERROR_SPAN = re.compile(r'<span style="border: 1px solid #F00">(.*?)</span>', re.S)

# Lesson-local print rules (kit request — as lessons 01/02): callout and story headings never print alone at a
# page foot, and tall diagram families are capped so one diagram does not fill a page.
LOCAL_CSS = ("<style>.callout .ct { break-after:avoid; page-break-after:avoid; } "
             ".callout li:first-child { break-before:avoid; page-break-before:avoid; } "
             ".story .ct { break-after:avoid; page-break-after:avoid; } "
             '.mmd svg[aria-roledescription="sequence"] { max-height:3.9in; } '
             '.mmd svg[aria-roledescription="stateDiagram"] { max-height:2.3in; } '
             '.mmd svg[aria-roledescription="flowchart-v2"] { max-height:3.6in; } '
             "h2 { break-after:avoid; page-break-after:avoid; } "
             "a.lnk, a { word-break:normal; overflow-wrap:break-word; }</style>")


def listed(block, heading):
    """Put a code()/compare() panel in the Contents at level 2 and clean VB highlighting (as lesson 01)."""
    block.update(heading=heading, toc=2)
    block["html"] = _ERROR_SPAN.sub(r"\1", block["html"])
    return block


def panel(src, heading, note, keep=None):
    return listed(code(src, heading=heading, note=note, keep=keep), heading)


def pair(left, right, heading, note, keep=None):
    return listed(compare(left, right, heading=heading, note=note, keep=keep), heading)


def figure_heading(text):
    """A numbered heading for a block type that prints none of its own (threecol), kept with that block."""
    return {"type": "html", "html": f'<div class="figh"><h2>{esc(text)}</h2></div>', "heading": text,
            "toc": 2, "_keep_with_next": True}


# ── helpers local to this lesson (MEASURED figures read from the samples at build time) ────────────
def region_loc(relpath, region):
    """Non-blank, non-comment lines inside one #region — the region-level twin of lesson_kit.loc()."""
    return sum(1 for ln in snippet(relpath, region).splitlines()
               if ln.strip() and not ln.strip().startswith(("//", "'")))


def test_cases(relpath):
    """xUnit test cases in one file: each [Fact] is one, each [InlineData] row of a [Theory] is one."""
    n = 0
    for ln in (REPO / relpath).read_text(encoding="utf-8-sig").splitlines():
        s = ln.strip()
        if s.startswith("[Fact") or s.startswith("[InlineData("):
            n += 1
    return n


def project_loc():
    """Code lines per sample project (C# and VB sources, generated output excluded)."""
    out = []
    for proj in sorted((REPO / L).glob("*/*.*proj")):
        files = [p for p in proj.parent.rglob("*") if p.suffix in (".cs", ".vb")
                 and not {"bin", "obj"} & set(p.relative_to(proj.parent).parts)]
        out.append((proj.stem.replace("L12.", ""), loc(*(p.relative_to(REPO).as_posix() for p in files))))
    return out


def triage_counts():
    """Strategy and target counts parsed from the captured triage output (panel 7.3)."""
    section, strategies, targets = None, [], []
    for ln in TRIAGE_OUTPUT.strip().splitlines():
        if ln.startswith("By strategy"):
            section = strategies
        elif ln.startswith("By target"):
            section = targets
        elif section is not None:
            name, count = ln.strip().rsplit(None, 1)
            section.append(("retired" if name == "-" else name, int(count)))
    return strategies, targets


def mb(n):
    return n / 1_000_000


def blocks():
    d8 = days_until(2026, 11, 10)
    live8 = d8 > 0
    n_tests = {LAMBDA_TESTS: test_cases(LAMBDA_TESTS), API_TESTS: test_cases(API_TESTS)}
    total_tests = sum(n_tests.values())
    if total_tests != CAPTURED_TESTS:
        raise ValueError(f"the samples now hold {total_tests} test cases but panel 8.2 shows a captured run of "
                         f"{CAPTURED_TESTS}: re-run dotnet test and re-capture 8.2")
    n_apps = sum(1 for ln in (REPO / ESTATE).read_text(encoding="utf-8").splitlines()[1:] if ln.strip())
    if f"Triage of {n_apps} applications" not in TRIAGE_OUTPUT:
        raise ValueError(f"estate.csv holds {n_apps} applications but panel 7.3 was captured for another count")
    strategies, targets = triage_counts()
    by_strategy, by_target = dict(strategies), dict(targets)
    n_proj = len(list((REPO / L).glob("*/*.*proj")))
    h_annot, h_raw_cs, h_raw_vb = (region_loc(FUNCS, "annotations"), region_loc(RAW_CS, "raw-cs"),
                                   region_loc(RAW_VB, "raw-vb"))
    kb = {label: round(size / 1000) for label, size, _files in PACKAGES}
    files = {label: n for label, _size, n in PACKAGES}
    x64, arm = LAYERS["linux-x64"], LAYERS["linux-arm64"]
    x64_total, arm_total = sum(x64.values()), sum(arm.values())
    app_share = x64["app"] / x64_total * 100
    locs = project_loc()
    loc_by = dict(locs)
    top_proj = max(locs, key=lambda r: r[1])

    target_cards = [
        {"num": 1, "title": "Lambda — managed dotnet10 runtime", "tags": [T_CLOUD, T_PY], "pills": [SAME],
         "what": "Upload a framework-dependent zip; Lambda supplies .NET 10 on Amazon Linux 2023, x86_64 or arm64.",
         "lines": [("You know", "Your Python Lambdas — same event model, same INIT phase, same 15-minute limit"),
                   ("Package", f"IL + dependencies: {kb['C# Annotations + DI']} KB zipped with a DI host, "
                               f"{kb['VB raw handler']} KB without (3.8)"),
                   ("Start-up", "Assemblies load and methods JIT-compile on first use — the cold start to manage"),
                   ("Pick when", "Spiky or event-driven work; HTTP API integrations time out at 30 s (" + HTTPQUOTA + ")"),
                   ("Support", "Deprecation 14 Nov 2028 (" + RUNTIMES + ")")]},
        {"num": 2, "title": "Lambda + SnapStart", "tags": [T_CLOUD], "pills": [DIFFERENT],
         "what": "Lambda initialises a published version once, snapshots memory and disk, and resumes copies.",
         "lines": [("Needs", "dotnet8 or later · published versions or aliases · Annotations 1.6.0+"),
                   ("Cost", "For .NET: snapshot caching and each restore are billed — free only for Java"),
                   ("Not with", "Provisioned concurrency, EFS, ephemeral storage over 512 MB, OS-only runtimes"),
                   ("Trap", "Anything unique made during INIT is cloned into every copy (" + SNAP + ")")]},
        {"num": 3, "title": "Lambda + Native AOT", "tags": [T_CLOUD], "pills": [SAME],
         "what": "Compile the function to a native executable: no JIT at start-up.",
         "lines": [("You know", "GraalVM native-image on a custom runtime"),
                   ("Build", "On Amazon Linux 2023 for the target architecture — the Lambda CLI uses a build container"),
                   ("Runtime", "Managed runtime, or OS-only provided.al2023 (" + NET8 + ")"),
                   ("Needs", "Source-generated JSON, trim-safe libraries, a test on Lambda (" + AOT + ")")]},
        {"num": 4, "title": "ECS Fargate — container", "tags": [T_CLOUD, T_ARCH], "pills": [RENAMED],
         "what": "An ASP.NET Core API in a Linux container behind a load balancer.",
         "lines": [("You know", "Spring Boot or NestJS on Fargate"),
                   ("Image", "<code>dotnet publish -t:PublishContainer</code>: chiseled, UID 1654, port 8080 (§4)"),
                   ("Stop", "SIGTERM, then SIGKILL after stopTimeout — 30 s by default, 120 s at most"),
                   ("Pick when", "Steady traffic, long requests or connections, background work, no cold starts")]},
        {"num": 5, "title": "EC2 Windows + IIS", "tags": [T_LEGACY], "pills": [DIFFERENT],
         "what": "Where .NET Framework, COM and GAC dependencies keep running while you port them.",
         "lines": [("Runs", "ASP.NET 4.x unchanged; ASP.NET Core through the Hosting Bundle's ASP.NET Core Module"),
                   ("Default", "In-process hosting in w3wp.exe, which cannot load a single-file app (" + IIS + ")"),
                   ("Or", "An ECS Windows container; Fargate has no gMSA, EFS or EBS (" + ECSWIN + ")"),
                   ("Pick when", "Rehost first, then port — the 7 R triage in §7; you own OS patching")]},
        {"num": 6, "title": "Lambda Managed Instances", "tags": [T_CLOUD], "pills": [TRAP],
         "what": "Lambda functions on Amazon EC2 instances, keeping Lambda's operating model; .NET 10 is supported.",
         "lines": [("Model", "One .NET process per environment; concurrent requests run as Tasks"),
                   ("Default", "32 concurrent requests per vCPU; Amazon.Lambda.Core 2.7.1 or later"),
                   ("Trap", "The handler is shared: every mutable field, static and collection must be thread-safe"),
                   ("Gap", "Powertools and ADOT .NET instrumentation are not supported yet (" + LMI + ")")]}]

    return [
        style_block(),
        {"type": "toc", "heading": "▤ Contents", "depth": 2,
         "note": "Page numbers are resolved from the rendered PDF. Code panels are cut from the compiled samples."},
        {"type": "html", "html": LOCAL_CSS},

        # ═══════════════════════════ 1 · WHY ═══════════════════════════
        {"type": "story", "heading": "1 · Why this lesson — MotorQuote meets the AWS estate you already run",
         "html": (
             "<p><b>You have already shipped the hard parts of this lesson, in other languages.</b> Python Lambda "
             "functions tuned to ~175 ms cold starts and 55 KB packages, services on ECS Fargate, Terraform that "
             "provisions 1,000–2,000+ resources in under three minutes, GitHub Actions pipelines, and the Windows "
             "(IIS) rows of an 80+ application migration inventory. On .NET the architecture carries over; what "
             "changes is how a function is found and started, how an image is built, which API emits telemetry, "
             "and what the legacy you have to move is made of.</p>"
             "<p><b>The samples take MotorQuote to AWS twice, from one Visual Basic rating library.</b> "
             "<code>L12.RatingVb</code> is called by a C# Lambda function written with Lambda Annotations, by a "
             "hand-written VB Lambda handler, and by an ASP.NET Core API that publishes itself as a container image "
             "without a Dockerfile. <code>infra/main.tf</code> and <code>ci/deploy.yml</code> describe how both "
             "would ship; tests prove the handlers agree. All premiums are illustrative, not a real tariff.</p>"
             "<p><b>Then it turns to the estate you would actually be asked to move.</b> A triage console sorts an "
             "illustrative 16-application .NET Framework inventory into the AWS 7 Rs and a target platform, and "
             "§7 maps every Framework API family to what replaces it on .NET 10.</p>"
             "<p><b>This is the last lesson, so it leans on the others.</b> Hosting, DI and health checks come from "
             + ref(8) + ", tests from " + ref(10) + ", identity and secrets from " + ref(11) + " and publish modes "
             "from " + ref(1) + ". The words here go to the hosting decision, the traps and the migration plan.</p>")},

        {"type": "kpi", "heading": "1.1 · The numbers to leave this lesson with",
         "items": [
             {"label": "dotnet10 on Lambda", "value": "to Nov 2028", "tone": "teal",
              "sub": "managed runtime · deprecation 14 Nov 2028 · verified"},
             {"label": "dotnet8 on Lambda", "value": f"{d8} days" if live8 else "deprecated", "tone": "red",
              "sub": "deprecation 10 Nov 2026 · counted from " + BUILD_DATE.isoformat()},
             {"label": "Lambda zip, C# + DI", "value": f"{kb['C# Annotations + DI']} KB", "tone": "amber",
              "sub": f"VB raw handler {kb['VB raw handler']} KB · measured"},
             {"label": "App layer in the image", "value": f"{mb(x64['app']):.2f} MB", "tone": "indigo",
              "sub": f"of {mb(x64_total):.1f} MB linux-x64 · measured"},
             {"label": "Estate triage", "value": f"{n_apps} apps", "tone": "navy",
              "sub": f"{by_strategy['Replatform']} replatform · {by_strategy['Refactor']} refactor · measured"}]},

        legend(T_PY, T_CLOUD, T_ARCH, T_LEGACY),

        {"type": "callout", "variant": "info", "heading": "ℹ Before you start",
         "items": [
             "<b>Earlier lessons this one builds on:</b> " + ref(1) + " (publish modes, Native AOT), " + ref(6)
             + " (VB migration strategy), " + ref(8) + " (hosting, health checks) and " + ref(10)
             + " (xUnit, <code>WebApplicationFactory</code>).",
             f"<b>You will build {n_proj} projects:</b> <code>L12.RatingVb</code> (VB library), "
             "<code>L12.QuoteLambda</code> + <code>.Tests</code> (C# Lambda), <code>L12.QuoteLambdaVb</code> (VB "
             "Lambda), <code>L12.QuoteContainer</code> + <code>.Tests</code> (container API) and "
             "<code>L12.EstateTriage</code> (console). <code>infra/main.tf</code> and <code>ci/deploy.yml</code> "
             "are read into the PDF and never applied.",
             "<b>No AWS account, Docker or Terraform is needed to run anything.</b> Handlers are tested in process "
             "with <code>Amazon.Lambda.TestUtilities</code>; the API through <code>WebApplicationFactory</code>. "
             "Publishing an image archive needs internet access to mcr.microsoft.com but no Docker daemon.",
             "Figures are marked " + VERIFIED + " (dated, linked), " + MEASURED + " (computed from the samples or "
             "captured from a real run on the build machine on 2026-09-16) or " + ESTIMATE + ". No cold-start "
             "latency is quoted: none was measured."]},

        # ═══════════════════════════ 2 · CHOOSING A TARGET ═══════════════════════════
        {"type": "story", "heading": "2 · Choosing a hosting target",
         "html": (
             "<p><b>Choose the target from the workload's shape, not from the language: .NET runs on every AWS "
             "compute option you already use.</b> Lambda has had a managed <code>dotnet10</code> runtime since "
             "8 January 2026, on Amazon Linux 2023 for x86_64 and arm64 (" + NET10 + "). ECS Fargate runs the same "
             "code as a Linux container. EC2 Windows with IIS — or a Windows container on ECS — keeps running what cannot leave .NET Framework yet. "
             "The decision inputs are the ones you used for Java and Python: traffic shape, latency budget, request "
             "length, statefulness and legacy dependencies.</p>"
             "<p><b>Cold start is where .NET on Lambda differs from Python, and there are three answers.</b> A "
             "framework-dependent zip loads assemblies and JIT-compiles methods on first use. SnapStart snapshots an "
             "initialised environment and restores copies — billed for .NET, unlike Java. Native AOT removes the JIT "
             "but must be compiled on Amazon Linux 2023 and needs source-generated serialisation. The rubric in 2.3 "
             "ranks these as a judgement; this lesson quotes no latency, because none was measured.</p>"
             "<p><b>Lambda Managed Instances change the concurrency contract.</b> Functions run on Amazon EC2 instances "
             "with Lambda's operating model, and one .NET process serves concurrent requests as Tasks — 32 per vCPU by default "
             "(" + LMI + "). Every piece of state a handler shares must be thread-safe, which is why the sample store "
             "is a <code>ConcurrentDictionary</code>.</p>")},

        {"type": "cards",
         "band": {"title": "2.1 · Six ways to host MotorQuote on AWS", "note": "hosting view", "tone": "rose"},
         "cards": target_cards[:3]},
        {"type": "cards", "toc": False,
         "band": {"title": "2.1 · Six ways to host MotorQuote on AWS (continued)", "note": "hosting view",
                  "tone": "rose"},
         "cards": target_cards[3:]},

        {"type": "mermaid", "inline": True,
         "heading": "2.2 · A decision flow for one workload",
         "caption": "amber = question · slate = legacy target · teal = Lambda options · indigo = container · "
                    "15 min is Lambda's maximum timeout, 30 s the HTTP API integration timeout",
         "code": ("flowchart TB\n"
                  '  Q1["Needs .NET Framework,<br/>COM or the GAC?"]:::q\n'
                  '  Q1 -- "yes" --> IIS["Windows host: EC2 + IIS<br/>or an ECS Windows container<br/>rehost, then port"]:::legacy\n'
                  '  Q1 -- "no" --> Q2["Jobs over 15 min, sync calls<br/>over 30 s, long-lived connections?"]:::q\n'
                  '  Q2 -- "yes" --> ECS["ECS Fargate<br/>container"]:::ctr\n'
                  '  Q2 -- "no" --> Q3["Traffic shape?"]:::q\n'
                  '  Q3 -- "steady, high" --> Q4["Keep the Lambda<br/>programming model?"]:::q\n'
                  '  Q4 -- "no" --> ECS\n'
                  '  Q4 -- "yes" --> LMI["Lambda Managed<br/>Instances"]:::fn\n'
                  '  Q3 -- "spiky, event-driven" --> Q5["Cold-start budget?"]:::q\n'
                  '  Q5 -- "relaxed" --> LAM["Lambda<br/>dotnet10 zip"]:::fn\n'
                  '  Q5 -- "tight, reflection-<br/>heavy libraries" --> SNAP["Lambda +<br/>SnapStart"]:::fn\n'
                  '  Q5 -- "tight, trim-<br/>safe code" --> AOT["Lambda +<br/>Native AOT"]:::fn\n'
                  "  classDef q fill:#fde68a,color:#1f2937,stroke:#d97706;\n"
                  "  classDef legacy fill:#e2e8f0,color:#1f2937,stroke:#475569;\n"
                  "  classDef ctr fill:#e0e7ff,color:#1f2937,stroke:#4338ca;\n"
                  "  classDef fn fill:#ccfbf1,color:#1f2937,stroke:#0d9488;\n")},

        {"type": "chart", "heading": "2.3 · Hosting targets against the questions that decide them", "kind": "heatmap",
         "args": {"rows": ["Pay nothing when idle", "Low cold-start latency", "Long requests, connections",
                           "Reflection-heavy libraries", ".NET Framework / System.Web", "No OS or image patching"],
                  "cols": ["Lambda", "SnapStart", "AOT", "Fargate", "EC2 IIS"],
                  "matrix": [[2, 1, 2, 0, 0], [0, 1, 1, 2, 2], [0, 0, 0, 2, 2], [2, 2, 0, 2, 2],
                             [0, 0, 0, 1, 2], [2, 2, 1, 1, 0]],
                  "cell": 40, "tone": "teal", "fmt": lambda v: {2: "good", 1: "some", 0: "poor"}[int(v)]},
         "caption": "good = strength · some = with a cost or caveat · poor = weakness · a rubric, not a benchmark",
         "note": "<b>No column wins every row, which is why an estate ends up on several targets.</b> SnapStart's "
                 "“some” on idle cost is its caching charge; AOT's “some” on patching is that the runtime is compiled "
                 "into your binary, so a .NET patch reaches it only when you rebuild; Fargate's is the base image you "
                 "rebuild. Only a Windows host runs System.Web: EC2 with IIS, or a Windows container on ECS — on Fargate "
                 "with limits, hence “some” (" + ECSWIN + "). §7 is about making that row irrelevant. " + ESTIMATE},

        mapping("2.4 · Concept map — Python, JVM and AWS habits → .NET on AWS", [
            ("Python handler <code>def handler(event, context)</code>", "Class-library handler "
             "<code>ASSEMBLY::TYPE::METHOD</code>", "different",
             "Lambda finds a method on a .NET type; with Annotations the type is the generated class (5.4)"),
            ("Powertools <code>APIGatewayHttpResolver</code> routes", "Lambda Annotations <code>[LambdaFunction]</code> "
             "+ <code>[HttpApi]</code>", "renamed", "A source generator writes the real handler; the VB sample writes its own"),
            ("Module-scope clients, created once", "Handler constructor · <code>[LambdaStartup]</code>", "same",
             "The Annotations function class is a singleton: no per-request state in its fields"),
            ("SnapStart for Java — no extra charge", "SnapStart for .NET 8 and later", "trap",
             "Billed for caching and restores; uniqueness is cloned; not on OS-only runtimes"),
            ("GraalVM native-image", "Native AOT on Lambda", "same",
             "Compile on Amazon Linux 2023; source-generated JSON; treat trim warnings as bugs"),
            ("A thin zipped Python package", "Framework-dependent <code>dotnet publish</code> zip", "different",
             f"The generic host adds {files['C# Annotations + DI'] - files['VB raw handler']} files: "
             f"{kb['C# Annotations + DI']} KB vs {kb['VB raw handler']} KB (3.8)"),
            ("Dockerfile + <code>docker build</code>", "<code>dotnet publish -t:PublishContainer</code>", "different",
             "No <code>RUN</code>; the base comes from <code>ContainerFamily</code>; no daemon for an archive"),
            ("<code>EXPOSE 80</code>, running as root", "Port 8080, user <code>app</code> (UID 1654)", "trap",
             "Default since .NET 8 images — a port mapping or target group on 80 gets no answer"),
            ("Actuator liveness and readiness", "<code>MapHealthChecks</code> with tags", "renamed",
             "Chiseled images have no shell: probe from the load balancer, not <code>CMD-SHELL</code>"),
            ("<code>server.shutdown=graceful</code>", "<code>HostOptions.ShutdownTimeout</code> (30 s)", "renamed",
             "Keep it below the ECS <code>stopTimeout</code> (30 s default, 120 s max)"),
            ("OpenTelemetry Java agent · Micrometer", "<code>ActivitySource</code> · <code>Meter</code> · "
             "<code>ILogger</code> + OpenTelemetry SDK", "renamed",
             "The API is in the base library; an <code>Activity</code> is the span"),
            ("SLF4J <code>log.info(\"{}\", x)</code>", "Message templates <code>\"{Total}\"</code>", "trap",
             "An interpolated <code>$\"…\"</code> string flattens the fields into one message"),
            ("X-Ray SDK + daemon", "OpenTelemetry + ADOT collector or CloudWatch agent", "different",
             "X-Ray SDKs and daemon in maintenance mode since 25 Feb 2026"),
            ("Terraform · GitHub Actions OIDC", "The same tools", "same",
             "Provider builds older than the dotnet10 launch reject the runtime value"),
            ("Java EE on WebSphere → Spring Boot", "ASP.NET on IIS → ASP.NET Core", "different",
             "<code>System.Web</code> is gone: migrate route by route behind YARP (7.6)"),
        ]),

        # ═══════════════════════════ 3 · LAMBDA ═══════════════════════════
        {"type": "story", "heading": "3 · .NET on Lambda — handlers, Annotations and SnapStart",
         "html": (
             "<p><b>A .NET Lambda function is a method that Lambda finds by name.</b> In the class-library model all "
             "samples use, the handler string is <code>ASSEMBLY::TYPE::METHOD</code>: Lambda loads the assembly into "
             "the managed runtime, constructs the type during INIT and calls the method per event. The alternative "
             "executable-assembly model starts the runtime client itself with <code>LambdaBootstrapBuilder</code>; "
             ".NET 10 file-based functions (one <code>.cs</code> file, no project) use it and default to Native AOT "
             "(" + HANDLER + ").</p>"
             "<p><b>Lambda Annotations is the .NET counterpart of Powertools' event handler — and it is a source "
             "generator.</b> You write a normal method with <code>[LambdaFunction]</code> and <code>[HttpApi]</code> "
             "and constructor-injected services. At compile time it writes "
             "<code>QuoteFunctions_CreateQuote_Generated</code>, whose constructor runs <code>Startup</code>, "
             "registers the function class as a singleton and builds the container during INIT; per request it "
             "creates a DI scope, binds the HTTP API body and returns 400 when the body cannot be read. It also "
             "keeps <code>serverless.template</code> in step. AWS documents Annotations for C# functions, so the VB "
             "project writes its handler by hand (3.4).</p>"
             "<p><b>SnapStart moves INIT from the first request to publish time.</b> Lambda initialises a published "
             "version, snapshots it, and resumes new environments from the snapshot. What you give up: anything "
             "unique created during INIT is identical in every copy, connections opened during INIT may be stale, "
             "and for .NET you pay for caching and each restore (" + SNAP + "). Hooks run code just before the "
             "snapshot and just after a restore; they need Amazon.Lambda.Core 2.5.0 or later (" + SNAPHOOKS + ").</p>")},

        pair(from_text('''
            from aws_lambda_powertools import Logger
            from aws_lambda_powertools.event_handler import (
                APIGatewayHttpResolver, Response)

            logger, app = Logger(), APIGatewayHttpResolver()
            store = InMemoryQuoteStore()  # module scope: once

            @app.post("/quotes")
            def create_quote():
                req = app.current_event.json_body
                coverage = COVERAGE.get(req["coverage"].lower())
                if coverage is None:
                    return Response(400, "application/json",
                                    '"unknown coverage"')
                saved = store.save(quote(coverage, req))
                logger.info("Quoted", extra={"quote_id": saved.id})
                location = f"/quotes/{saved.id}"
                return Response(201, "application/json", saved.to_json(),
                                headers={"Location": location})

            def handler(event, context):  # handler: app.handler
                return app.resolve(event, context)
            ''', "python", file="Powertools for AWS Lambda (Python)"),
             from_sample(FUNCS, "annotations"),
             "3.1 · POST /quotes — a Python Powertools handler and its Annotations twin",
             "<b>Same shape, different mechanism.</b> Python routes at run time inside <code>app.resolve</code>; "
             "Annotations routes at compile time, so a C# function is one route per Lambda function and the "
             "binding code is generated, not reflected. <code>[FromBody]</code> replaces "
             "<code>json_body</code>, <code>IHttpResult</code> replaces <code>Response</code>, and "
             "<code>context.Logger</code> takes a message template whose <code>{QuoteId}</code> becomes a JSON field "
             "when the function's log format is JSON (" + LOGS + "). Neither handler touches rates: both call a "
             "rating module — in .NET, the VB library. <b>Annotations does not replace Powertools; the two are "
             "complementary.</b> Annotations takes over the routing, binding and DI half of Python's event handler; "
             "Powertools for AWS Lambda (.NET) has no API Gateway router of its own — its Event Handler covers "
             "AppSync Events and Bedrock Agent functions — and stays what you add for logging, metrics, tracing, "
             "idempotency, batch processing and parameters (" + POWERTOOLS + ")."),

        panel(from_sample(STARTUP, "startup"), "3.2 · Startup — what runs once per execution environment",
              "<b>This is Lambda's INIT phase, written as DI.</b> The generated wrapper's constructor calls "
              "<code>ConfigureHostBuilder</code>, adds <code>QuoteFunctions</code> as a singleton and resolves it "
              "eagerly, so construction time shows up in the INIT report rather than the first request. A singleton "
              "store survives between invocations of one environment only; Lambda runs many environments in parallel "
              "and recycles them, which is why production state belongs in DynamoDB (" + ref(9) + " covers data "
              "access)."),

        {"type": "mermaid", "inline": True,
         "heading": "3.3 · One cold request, then a warm one",
         "caption": "INIT runs once per execution environment; a warm request skips steps 1–3 · with SnapStart, "
                    "steps 1–3 happen when the version is published and a restore replaces them",
         "code": ('%%{init: {"theme":"base","themeVariables": {"actorBkg":"#ccfbf1","actorBorder":"#0f766e",'
                  '"actorTextColor":"#1f2937","noteBkgColor":"#fef3c7","noteBorderColor":"#d97706",'
                  '"noteTextColor":"#1f2937","signalColor":"#334155","signalTextColor":"#1f2937"}}}%%\n'
                  "sequenceDiagram\n"
                  "  autonumber\n"
                  "  participant G as API Gateway HTTP API\n"
                  "  participant R as Lambda dotnet10 runtime\n"
                  "  participant W as Generated wrapper\n"
                  "  participant F as QuoteFunctions\n"
                  "  participant V as Rating (VB)\n"
                  "  R->>W: load L12.QuoteLambda.dll, run constructor\n"
                  "  W->>W: Startup.ConfigureHostBuilder, build DI\n"
                  "  W->>F: resolve singleton (INIT ends)\n"
                  "  G->>R: POST /quotes, payload format 2.0\n"
                  "  R->>W: CreateQuote(request, context)\n"
                  "  W->>F: new scope, bind body to QuoteRequest\n"
                  "  F->>V: Rating.Quote(coverage, sum, ...)\n"
                  "  V-->>F: PremiumBreakdown\n"
                  "  F-->>G: 201 Created + Location\n"
                  "  Note over G,V: next request, same environment: steps 4-9 only\n")},

        pair(from_sample(RAW_CS, "raw-cs"), from_sample(RAW_VB, "raw-vb"),
             "3.4 · The same handler without Annotations — C# and Visual Basic",
             "<b>Line for line the same program, and a test proves it.</b> Both take the raw "
             "<code>APIGatewayHttpApiV2ProxyRequest</code>, deserialise with <code>JsonSerializerOptions.Web</code> "
             "(camelCase, case-insensitive), parse the coverage case-insensitively and serialise the VB "
             "<code>PremiumBreakdown</code>. <code>HandlerParityTests</code> sends three bodies — including an unknown "
             "coverage — to both and asserts equal status codes and byte-identical bodies. VB spells "
             "<code>If(a, b)</code> for <code>??</code>, <code>[Enum]</code> for the keyword clash and "
             "<code>From { }</code> for the dictionary initialiser; its handler string is "
             "<code>L12.QuoteLambdaVb::L12.QuoteLambdaVb.QuoteHandler::FunctionHandler</code>."),

        panel(from_sample(STARTUP, "snapstart"), "3.5 · SnapStart hooks — warm before the snapshot, renew after restore",
              "<b>Two hooks, two different jobs.</b> The before-snapshot hook sends a request through the raw handler ten "
              "times — JSON in, rating, JSON out — so that code is already compiled in the snapshot. AWS's .NET "
              "guidance calls the handler repeatedly because of tiered compilation, and warns that warm-up calls "
              "must have no side effects (" + SNAPBEST + "); this handler saves nothing. It does not warm the "
              "generated wrapper's DI scope or body binding, because the wrapper's constructor is what runs "
              "<code>Startup</code>: a production hook should drive the real handler where it can. The after-restore "
              "hook renews <code>EnvironmentId</code>, which would otherwise be the same GUID in every restored "
              "environment. Register hooks in the handler's constructor path — here <code>Startup</code>. The unit "
              "tests run the registration; only Lambda runs the hooks."),

        {"type": "table", "heading": "3.6 · .NET runtimes on Lambda",
         "cols": ["Runtime", "Identifier", "OS", "Deprecation", "Block create", "Block update"],
         "rows": [
             [".NET 10", "<code>dotnet10</code>", "Amazon Linux 2023", pill("14 Nov 2028", "green"), "14 Dec 2028",
              "15 Jan 2029"],
             [".NET 9 — container image only", "<code>dotnet9</code> · image only",
              "Amazon Linux 2023",
              pill("10 Nov 2026", "amber" if live8 else "red"), "not scheduled", "not scheduled"],
             [".NET 8", "<code>dotnet8</code>", "Amazon Linux 2023", pill("10 Nov 2026", "amber" if live8 else "red"),
              "1 Feb 2027", "3 Mar 2027"],
             [".NET 6", "<code>dotnet6</code>", "Amazon Linux 2", pill("20 Dec 2024", "red"), "1 Feb 2027",
              "3 Mar 2027"],
             ["OS-only (Native AOT option)", "<code>provided.al2023</code>", "Amazon Linux 2023",
              pill("30 Jun 2029", "green"), "31 Jul 2029", "31 Aug 2029"]]},
        {"type": "html",
         "html": ('<div class="lnote"><b>Four of these five identifiers are values for <code>runtime =</code>.</b> '
                  'AWS ships .NET 9 only as a container base image, so a zip function cannot name it and a '
                  'container-image function sets no runtime at all. Dates re-checked against the AWS table on '
                  '2026-09-20 (' + RUNTIMES + ").</div>")},

        {"type": "chartrow", "charts": [
            {"heading": "3.7 · Handler code lines — Annotations vs by hand", "kind": "bar",
             "args": {"data": [("C# Annotations", h_annot), ("C# raw", h_raw_cs), ("VB raw", h_raw_vb)],
                      "ylabel": "code lines", "tone": "violet", "width": 390, "height": 220},
             "caption": "non-blank, non-comment lines in regions annotations, raw-cs and raw-vb · measured at build",
             "note": f"<b>Annotations writes about {round((1 - h_annot / h_raw_cs) * 100)}% fewer lines than the "
                     "hand-written C# handler.</b> The binding, the 400 for an unreadable body and the response "
                     "envelope move into generated code; the raw handlers in 3.4 show the work it takes over — "
                     "work VB must still write. " + MEASURED},
            {"heading": "3.8 · Deployment package size", "kind": "bar",
             "args": {"data": [(label.replace(" publish", ""), kb[label]) for label, _s, _f in PACKAGES],
                      "ylabel": "KB zipped", "tone": "amber", "width": 390, "height": 220},
             "caption": "dotnet publish -c Release, folder zipped with deflate · captured on the build machine 2026-09-16",
             "note": f"<b>The DI host, not .NET, makes the package "
                     f"{kb['C# Annotations + DI'] / kb['VB raw handler']:.0f} times larger.</b> The Annotations function "
                     f"pulls in <code>Microsoft.Extensions.Hosting</code>: {files['C# Annotations + DI']} files and "
                     f"{kb['C# Annotations + DI']} KB, against {files['VB raw handler']} files and "
                     f"{kb['VB raw handler']} KB for the raw VB handler. Publishing for <code>linux-arm64</code> drops "
                     "the Windows-only EventLog assets. Set that against the 55 KB zipped Python functions you shipped. " + MEASURED}]},

        panel(from_sample(LAMBDA_TESTS, "wrapper-test"), "3.9 · Testing the class Lambda actually calls",
              "<b>Test the generated wrapper, not only your method.</b> Constructing "
              "<code>QuoteFunctions_CreateQuote_Generated</code> runs <code>Startup</code> and the SnapStart "
              "registration exactly as INIT would; the test then feeds it an HTTP API v2 event and reads the "
              "serialised response stream. It catches what a direct call to <code>CreateQuote</code> cannot: a "
              "broken DI registration, a body-binding change, a missing <code>Location</code> header. "
              + f"The lesson's two test projects hold {total_tests} test cases ({ref(10)} covers the framework)."),

        # ═══════════════════════════ 4 · CONTAINERS ═══════════════════════════
        {"type": "story", "heading": "4 · Containers without a Dockerfile",
         "html": (
             "<p><b>The .NET SDK builds OCI images itself: <code>dotnet publish -t:PublishContainer</code>.</b> "
             "MSBuild properties replace the Dockerfile — <code>ContainerRepository</code>, "
             "<code>ContainerFamily</code>, <code>ContainerImageTags</code>. Listing several "
             "<code>ContainerRuntimeIdentifiers</code> produces a multi-architecture image index (SDK 8.0.405 and "
             "9.0.102 onwards); <code>ContainerRegistry</code> pushes straight to ECR and "
             "<code>ContainerArchiveOutputPath</code> writes a tarball with no Docker daemon. There is no "
             "<code>RUN</code>: anything a Dockerfile would install belongs in a custom base image (" + CONTAINERS
             + ").</p>"
             "<p><b>The image defaults changed twice, and both changes break copied Dockerfile habits.</b> Since "
             ".NET 8, official images listen on port 8080 and ship a non-root <code>app</code> user "
             "(" + PORT8080 + "). Since .NET 10, the default tags are Ubuntu 24.04 “Noble” and no Debian images "
             "ship (" + UBUNTU + "). Chiseled images remove the shell and package manager, and the size-optimised "
             "ones carry no ICU or tzdata — hence <code>InvariantGlobalization</code> in the project file "
             "(" + IMAGES + ").</p>"
             "<p><b>Graceful shutdown is an agreement between two timeouts.</b> ECS sends SIGTERM, waits the "
             "container's <code>stopTimeout</code> — 30 s unless set, 120 s at most — and then sends SIGKILL "
             "(" + ECSPARAMS + "). The generic host turns SIGTERM into <code>ApplicationStopping</code>, stops "
             "accepting connections and waits <code>HostOptions.ShutdownTimeout</code> — 30 s by default — for "
             "in-flight requests (" + HOST + "). Equal defaults leave no margin, so the sample sets 20 s and a test "
             "fails if anyone raises it to 30.</p>")},

        panel(from_sample(API_PROJ), "4.1 · The project file is the Dockerfile",
              "<b>Read the second property group as a Dockerfile.</b> <code>ContainerFamily</code> "
              "<code>noble-chiseled</code> picks <code>aspnet:10.0-noble-chiseled</code> as the base; the two RID "
              "lists make one image per architecture plus an index; the tags name the image. The Lambda hosting "
              "package lets the same API run on Lambda — <code>AddAWSLambdaHosting</code> replaces Kestrel only "
              "inside a Lambda environment (" + ASPLAMBDA + "). The API calls the same VB rating library as the "
              "functions.", keep=False),

        panel(from_sample(API, "hosting"), "4.2 · Two hosting targets, one shutdown budget",
              "<b>One codebase, two hosts, one rule.</b> On ECS the process is Kestrel on port 8080; on Lambda the "
              "adapter swaps the server and the HTTP API event becomes an <code>HttpContext</code>. The 20-second "
              "<code>ShutdownTimeout</code> is checked by <code>Shutdown_timeout_fits_inside_the_ecs_stop_timeout</code>, "
              "so the ECS <code>stopTimeout</code> of 30 s in <code>main.tf</code> always has headroom."),

        panel(from_sample(API, "health"), "4.3 · Liveness and readiness without a shell",
              "<b>Two endpoints, two questions.</b> <code>/health/live</code> runs no checks — the process answers, "
              "so do not restart it. <code>/health/ready</code> runs the checks tagged <code>ready</code>; here "
              "<code>RatingSelfCheck</code> prices a quote through the VB library. ECS container health checks run "
              "a command inside the container (<code>CMD</code> or <code>CMD-SHELL</code>), and a chiseled image "
              "has neither a shell nor curl — so the load balancer's target group probes <code>/health/ready</code> "
              "from outside (5.5)."),

        {"type": "mermaid", "inline": True,
         "heading": "4.4 · An ECS task's life, from pull to SIGKILL",
         "caption": "green = serving · amber = draining · rose = forced stop · the numbers are this lesson's settings: "
                    "HostOptions 20 s inside an ECS stopTimeout of 30 s",
         "code": ("stateDiagram-v2\n"
                  "  direction LR\n"
                  '  state "PROVISIONING<br/>pull image index,<br/>pick arm64 manifest" as prov\n'
                  '  state "RUNNING<br/>Kestrel :8080<br/>as UID 1654" as run\n'
                  '  state "HEALTHY<br/>target group:<br/>/health/ready 200" as healthy\n'
                  '  state "DRAINING<br/>SIGTERM →<br/>ApplicationStopping" as drain\n'
                  '  state "STOPPED<br/>requests done<br/>within 20 s" as stopped\n'
                  '  state "KILLED<br/>SIGKILL at<br/>stopTimeout 30 s" as killed\n'
                  "  [*] --> prov\n"
                  "  prov --> run\n"
                  "  run --> healthy : readiness passes\n"
                  "  healthy --> drain : deploy or scale-in\n"
                  "  drain --> stopped : host exits\n"
                  "  drain --> killed : still busy\n"
                  "  stopped --> [*]\n"
                  "  killed --> [*]\n"
                  "  classDef serving fill:#bbf7d0,color:#1f2937,stroke:#16a34a;\n"
                  "  classDef draining fill:#fde68a,color:#1f2937,stroke:#d97706;\n"
                  "  classDef forced fill:#fce7f3,color:#1f2937,stroke:#be185d;\n"
                  "  classDef plain fill:#e2e8f0,color:#1f2937,stroke:#475569;\n"
                  "  class healthy,run serving\n"
                  "  class drain draining\n"
                  "  class killed forced\n"
                  "  class prov,stopped plain\n")},

        panel(from_text("""
            $ dotnet publish $SAMPLES/L12.QuoteContainer -c Release -t:PublishContainer \\
                -p ContainerArchiveOutputPath=./images/
              L12.QuoteContainer -> .build/artifacts/publish/L12.QuoteContainer/release_linux-arm64/
              L12.QuoteContainer -> .build/artifacts/publish/L12.QuoteContainer/release_linux-x64/
              Building image 'motorquote/quote-api' for runtime identifier 'linux-x64'
                on top of base image 'mcr.microsoft.com/dotnet/aspnet:10.0-noble-chiseled'.
              Building image 'motorquote/quote-api' for runtime identifier 'linux-arm64'
                on top of base image 'mcr.microsoft.com/dotnet/aspnet:10.0-noble-chiseled'.
              Building image index 'motorquote/quote-api:1.0.0, latest' on top of manifests
                sha256:9363f67bcb83…, sha256:4d61971fda01….
              Pushed image 'motorquote/quote-api:1.0.0, latest' to local archive at
                './images/motorquote/quote-api.tar.gz'.
            """, "text", label="Terminal — image, no Dockerfile, no daemon",
                        file="captured 2026-09-16 · edited: paths, wrapping, one publish line, MSBuild prefixes"),
              "4.5 · What you should see — two images and an index",
              "<b>No Docker, no Dockerfile.</b> The SDK publishes the app once per RID, downloads the chiseled base "
              "image from mcr.microsoft.com, adds one layer with your files and writes both images plus an OCI "
              "image index into the archive. Swap <code>ContainerArchiveOutputPath</code> for "
              "<code>ContainerRegistry</code> and the same command pushes to ECR, as the pipeline in 5.3 does. In Git "
              "Bash on Windows write <code>-t:</code>: the shell rewrites <code>/t:PublishContainer</code> as a "
              "file path and MSBuild stops with “Only one project can be specified”."),

        {"type": "chart", "heading": "4.6 · What is inside the image, per architecture", "kind": "stacked_bar",
         "args": {"categories": ["linux-x64", "linux-arm64"],
                  "series": [("Ubuntu chiseled", [round(mb(x64["rootfs"] + x64["home"]), 1),
                                                  round(mb(arm["rootfs"] + arm["home"]), 1)]),
                             (".NET runtime", [round(mb(x64["runtime"] + x64["symlink"]), 1),
                                               round(mb(arm["runtime"] + arm["symlink"]), 1)]),
                             ("ASP.NET Core", [round(mb(x64["aspnet"]), 1), round(mb(arm["aspnet"]), 1)]),
                             ("MotorQuote app", [round(mb(x64["app"]), 2), round(mb(arm["app"]), 2)])],
                  "width": 470, "height": 265},
         "caption": "compressed layer sizes in MB, read from the image manifests in the archive · captured 2026-09-16 · "
                    "the MotorQuote app layer is 0.55 MB — 1% of the image, a sliver at this scale",
         "note": f"<b>Your code is {app_share:.1f}% of the image — a {mb(x64['app']):.2f} MB layer on "
                 f"{mb(x64_total - x64['app']):.1f} MB of base.</b> The base layers are shared by every .NET 10 API "
                 "in the registry and on the host, so a deploy moves only the top layer. The arm64 image is "
                 f"{mb(arm_total):.1f} MB against {mb(x64_total):.1f} MB for x64; the two tiny layers (the "
                 "<code>/home/app</code> folder and the <code>dotnet</code> symlink) are folded into their neighbours. "
                 + MEASURED},

        {"type": "table", "heading": "4.7 · The image configuration the SDK wrote",
         "cols": ["Setting", "Value in the linux-x64 manifest", "Where it came from"],
         "rows": [
             ["Base image", "<code>mcr.microsoft.com/dotnet/aspnet:10.0-noble-chiseled</code>",
              "<code>ContainerFamily</code> + the <code>net10.0</code> TFM"],
             ["User", "<code>1654</code> (<code>APP_UID</code>)", "the base image's non-root <code>app</code> user"],
             ["Port", "<code>ASPNETCORE_HTTP_PORTS=8080</code> · exposed <code>8080/tcp</code>",
              "base image variable; the SDK infers the exposed port from it"],
             ["Globalization", "<code>DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=true</code>",
              "chiseled base without ICU — matches <code>InvariantGlobalization</code>"],
             ["Entry point", "<code>dotnet /app/L12.QuoteContainer.dll</code> · working dir <code>/app/</code>",
              "the SDK, framework-dependent publish"],
             ["Runtime", "<code>DOTNET_VERSION=10.0.12</code> · <code>ASPNET_VERSION=10.0.12</code>",
              "the base image on the day of the build"],
             ["Tags", "<code>1.0.0</code> · <code>latest</code> → one OCI index over amd64 + arm64",
              "<code>ContainerImageTags</code> + <code>ContainerRuntimeIdentifiers</code>"]]},

        # ═══════════════════════════ 5 · INFRA & DELIVERY ═══════════════════════════
        {"type": "story", "heading": "5 · Infrastructure and delivery — Terraform, OIDC, CDK and Aspire",
         "html": (
             "<p><b>Your Terraform and GitHub Actions carry over; three .NET details do not.</b> The runtime is "
             "<code>dotnet10</code> and, with Annotations, the handler names the generated class. SnapStart needs "
             "<code>publish = true</code> and an alias, because it applies only to published versions. And an AWS "
             "provider build from before the runtime existed rejects <code>dotnet10</code> at validate time — "
             "exactly what users reported in January 2026 (" + TFISSUE + "). The sample's <code>~&gt; 6.0</code> "
             f"floats: on 2026-09-16 it resolved to hashicorp/aws {TF_PROVIDER}, whose runtime list includes "
             "<code>dotnet10</code>, and a one-off <code>terraform validate</code> on that copy passed — run by "
             "hand, not repeated by the build, so read it as a dated observation, not a guarantee.</p>"
             "<p><b>The pipeline authenticates with OIDC and stores no AWS keys.</b> <code>id-token: write</code> lets "
             "GitHub mint a token that <code>configure-aws-credentials</code> exchanges for a role session; the "
             "role's trust policy pins the audience <code>sts.amazonaws.com</code> and a <code>sub</code> such as "
             "<code>repo:org/repo:ref:refs/heads/main</code> (" + GHOIDC + "). Identity and secrets in depth: "
             + ref(11) + ". Action majors in the sample were the latest releases on 2026-09-16: "
             + " · ".join(link(f"{name}@{tag}", url) for name, (tag, url) in ACTIONS.items()) + ".</p>"
             "<p><b>C# teams have two more infrastructure tools.</b> The AWS CDK treats .NET as a stable, fully "
             "supported language (.NET 8 or later; the CDK CLI still needs Node.js) (" + CDK + "). Aspire — renamed "
             "from “.NET Aspire” at version 13 on 11 November 2025, and needing the .NET 10 SDK (" + ASPIRE + ") — "
             "orchestrates the local loop; its AWS integration provisions resources through CloudFormation and, in "
             "preview, runs Lambda functions locally (" + ASPIREAWS + ").</p>")},

        {"type": "mermaid", "inline": True,
         "heading": "5.1 · From push to running, with no stored keys",
         "caption": "the only credentials are the ones STS returns in step 4, and they expire · the token's sub claim "
                    "is what the role's trust policy matches",
         "code": ('%%{init: {"theme":"base","themeVariables": {"actorBkg":"#c7d2fe","actorBorder":"#4338ca",'
                  '"actorTextColor":"#1f2937","noteBkgColor":"#fef3c7","noteBorderColor":"#d97706",'
                  '"noteTextColor":"#1f2937","signalColor":"#334155","signalTextColor":"#1f2937"}}}%%\n'
                  "sequenceDiagram\n"
                  "  autonumber\n"
                  "  participant GH as GitHub Actions job\n"
                  "  participant ID as GitHub OIDC provider\n"
                  "  participant STS as AWS STS\n"
                  "  participant ECR as Amazon ECR\n"
                  "  participant RUN as Lambda and ECS\n"
                  "  Note over GH: push to main:<br/>checkout and<br/>dotnet test\n"
                  "  GH->>ID: request a token (id-token: write)\n"
                  "  ID-->>GH: signed JWT, sub repo:org/repo:ref:refs/heads/main\n"
                  "  GH->>STS: AssumeRoleWithWebIdentity(JWT)\n"
                  "  STS-->>GH: short-lived role credentials\n"
                  "  Note over GH: dotnet publish<br/>Lambda zip\n"
                  "  GH->>ECR: dotnet publish -t:PublishContainer (amd64 + arm64)\n"
                  "  GH->>RUN: terraform apply: Lambda version + live alias\n"
                  "  GH->>RUN: terraform apply: new ECS task definition\n"
                  "  RUN->>ECR: Fargate pulls the arm64 manifest\n")},

        panel(from_sample(CI, "build"), "5.2 · The workflow — test, authenticate, package",
              "<b>The SDK version comes from the repository, the credentials from a role.</b> "
              "<code>setup-dotnet</code> reads <code>global.json</code>, so CI builds with the SDK your laptop pins "
              "(" + ref(7) + "). <code>role-to-assume</code> is the only AWS setting — no access key exists to leak. "
              "The Lambda zip is framework-dependent IL, so it runs on the <code>arm64</code> function although the "
              "runner is x64."),

        panel(from_sample(CI, "ship"), "5.3 · The workflow — push the image, apply the plan",
              "<b>No Docker build step, no Dockerfile in the repository.</b> <code>amazon-ecr-login</code> gives the "
              "SDK registry credentials; <code>ContainerRegistry</code> redirects the publish from 4.5 to ECR, and "
              "the commit SHA replaces the tags. Terraform receives the zip path and the image reference as "
              "variables, so one apply moves both targets. The file sits under <code>samples/ci/</code>, where "
              "GitHub never runs it."),

        panel(from_sample(TF, "lambda"), "5.4 · Terraform — the function, SnapStart and a live alias",
              "<b>Three lines carry the .NET decisions.</b> <code>runtime = \"dotnet10\"</code> with "
              "<code>architectures = [\"arm64\"]</code> runs the same IL on Graviton. The handler string names the "
              "generated wrapper tested in 3.9 — name <code>QuoteFunctions</code> instead and the function fails when it "
              "initialises, not when Terraform applies. <code>publish = true</code> plus <code>snap_start</code> "
              "snapshots each published version; the HTTP API integrates with the <code>live</code> alias (in "
              "<code>main.tf</code>, not printed), never <code>$LATEST</code>. <code>log_format = \"JSON\"</code> "
              "turns message-template arguments into fields.", keep=False),

        panel(from_sample(TF, "ecs"), "5.5 · Terraform — the Fargate task and its target group",
              "<b>The container side repeats §4 in HCL.</b> <code>cpu_architecture = \"ARM64\"</code> picks the "
              "arm64 manifest from the image index, <code>containerPort = 8080</code> matches the image, "
              "<code>stopTimeout = 30</code> is the budget the host's 20 s fits in, and the target group probes "
              "<code>/health/ready</code> because the image has no shell. The VPC, cluster, service, listener and "
              "IAM roles arrive as variables; the collector sidecar and the "
              "<code>OTEL_EXPORTER_OTLP_ENDPOINT</code> that points the API at it are left out too, so as written "
              "this task exports no telemetry (6.1 shows the app side). A sketch that validates, not a stack that "
              "was applied.", keep=False),

        figure_heading("5.6 · Three ways to describe the same infrastructure"),
        {"type": "threecol", "boxes": [
            {"heading": "Terraform (HCL)", "tone": "violet",
             "items": ["What the sample uses — your existing estate, state and modules carry over",
                       "Runtime strings validated by the provider: pin a build that knows <code>dotnet10</code>",
                       "Language-neutral: the .NET build stays in <code>dotnet publish</code>"]},
            {"heading": "AWS CDK in C#", "tone": "teal",
             "items": ["Infrastructure as C# classes and props objects — <code>Amazon.CDK.Lib</code>",
                       "Stable and fully supported for .NET; VB and F# work with limited support",
                       "Synthesises CloudFormation; the CLI still needs Node.js"]},
            {"heading": "Aspire", "tone": "indigo",
             "items": ["Local orchestration and a telemetry dashboard for multi-service apps",
                       "Aspire 13 dropped the “.NET” prefix and requires the .NET 10 SDK",
                       "<code>Aspire.Hosting.AWS</code>: CloudFormation provisioning; local Lambda runs in preview"]}]},

        # ═══════════════════════════ 6 · OBSERVABILITY ═══════════════════════════
        {"type": "story", "heading": "6 · Observability — OpenTelemetry on .NET's own APIs",
         "html": (
             "<p><b>In .NET the OpenTelemetry API is already in the base library.</b> "
             "<code>ActivitySource</code> and <code>Activity</code> are the tracer and the span, "
             "<code>System.Diagnostics.Metrics.Meter</code> is the meter, and <code>ILogger</code> is the logger; the "
             "OpenTelemetry packages subscribe to them by name and export (" + OTEL + "). A library can emit spans "
             "without referencing OpenTelemetry at all — the reverse of adding the Java agent or Micrometer to a "
             "Spring service.</p>"
             "<p><b>On AWS, export OTLP to a collector and let it reach X-Ray and CloudWatch.</b> The X-Ray SDKs and "
             "daemon entered maintenance mode on 25 February 2026; AWS recommends OpenTelemetry instrumentation with "
             "an OpenTelemetry collector (such as ADOT's) or the CloudWatch agent in place of the daemon, and converts server spans to "
             "segments and attributes to metadata (" + XRAY + "). The sample exports only when "
             "<code>OTEL_EXPORTER_OTLP_ENDPOINT</code> is set, so tests and laptops need no collector.</p>"
             "<p><b>Structured logs depend on message templates on both targets.</b> With the function's log format "
             "set to JSON, Lambda turns <code>{QuoteId}</code> placeholders passed to <code>context.Logger</code> "
             "into top-level JSON fields (" + LOGS + "); <code>ILogger</code> does the same for any structured "
             "provider. An interpolated string gives both a single opaque message. On Lambda, Powertools for AWS "
             "Lambda (.NET) adds cold-start fields, EMF metrics and idempotency (" + POWERTOOLS + ").</p>")},

        panel(from_sample(API, "telemetry"), "6.1 · Wiring traces, metrics and logs",
              "<b>Subscribe by name, export by configuration.</b> <code>AddSource</code> and <code>AddMeter</code> "
              "name the <code>ActivitySource</code> and <code>Meter</code> declared in <code>QuoteTelemetry</code>; "
              "the ASP.NET Core instrumentation adds a server span and HTTP metrics per request. "
              "<code>UseOtlpExporter</code> sends all three signals to one OTLP endpoint — on ECS, a CloudWatch agent "
              "or ADOT collector sidecar on <code>localhost:4317</code>. The resource name "
              "<code>motorquote-api</code> is the <code>service.name</code> every backend groups by."),

        panel(from_sample(API, "endpoint"), "6.2 · One request: a span, a counter and a structured log",
              "<b>Three signals, three APIs, no vendor type.</b> <code>StartActivity</code> returns "
              "<code>null</code> when nothing listens — hence <code>span?.</code>. The counter's "
              "<code>coverage</code> tag becomes a metric dimension, so keep its values few. The log call passes "
              "<code>Coverage</code> and <code>Total</code> as template arguments; written as "
              "<code>$\"Quoted {req.Coverage}\"</code> it would search as one string. The premium comes from "
              "the VB rules, as in every other host in this lesson."),

        {"type": "mermaid", "inline": True,
         "heading": "6.3 · Where each signal goes",
         "caption": "violet = .NET APIs in your code · indigo = OpenTelemetry SDK · amber = collector · slate = AWS "
                    "backends · the Lambda path needs no collector for logs",
         "code": ('%%{init: {"flowchart": {"nodeSpacing": 22, "rankSpacing": 55}}}%%\n'
                  "flowchart LR\n"
                  '  AS["ActivitySource<br/>MotorQuote.Api"]:::net --> SDK["OpenTelemetry SDK<br/>OTLP exporter"]:::otel\n'
                  '  ME["Meter<br/>MotorQuote.Api"]:::net --> SDK\n'
                  '  LG["ILogger<br/>message templates"]:::net --> SDK\n'
                  '  SDK -- "OTLP :4317" --> COL["CloudWatch agent<br/>or ADOT collector"]:::col\n'
                  '  COL --> XR["X-Ray<br/>traces"]:::aws\n'
                  '  COL --> CWM["CloudWatch<br/>metrics"]:::aws\n'
                  '  COL --> CWL["CloudWatch<br/>Logs"]:::aws\n'
                  '  FN["Lambda context.Logger<br/>log format JSON"]:::net -- "stdout, JSON" --> CWL\n'
                  "  classDef net fill:#ede9fe,color:#1f2937,stroke:#6d28d9;\n"
                  "  classDef otel fill:#c7d2fe,color:#1f2937,stroke:#6366f1;\n"
                  "  classDef col fill:#fde68a,color:#1f2937,stroke:#d97706;\n"
                  "  classDef aws fill:#e2e8f0,color:#1f2937,stroke:#475569;\n")},

        panel(from_sample(API_TESTS, "span-test"), "6.4 · Asserting on spans in a test",
              "<b>Telemetry is behaviour, so it gets a test.</b> <code>ConfigureTestServices</code> adds an in-memory "
              "exporter to the tracer provider the app already configured, and the test asserts that both the "
              "domain span <code>rate-quote</code> and the ASP.NET Core server span were exported. The server span "
              "ends after the response is written, so the test waits for it — asserting straight away would race "
              "the server span."),

        # ═══════════════════════════ 7 · MODERNISATION ═══════════════════════════
        {"type": "story", "heading": "7 · Modernising Windows and IIS estates",
         "html": (
             "<p><b>Triage the estate with the AWS 7 Rs — not six.</b> AWS Prescriptive Guidance lists Retire, Retain, "
             "Rehost, Relocate, Repurchase, Replatform and Refactor, and for large migrations recommends rehosting, "
             "relocating or replatforming first and modernising afterwards, because refactoring during the move is "
             "the most complex path (" + SEVENRS + "). For a .NET estate the deciding signals sit in each repository: "
             "the target framework, <code>System.Web</code>, WCF, COM and the GAC, MSMQ, Web Forms. "
             "<code>L12.EstateTriage</code> turns one signal into one rule.</p>"
             "<p><b>Port by API family, not by project.</b> Application domains, remoting, code access security and "
             "COM+ do not exist on .NET 10; WCF services move to CoreWCF for existing SOAP clients or to gRPC for new "
             "ones (" + UNAVAILABLE + " · " + COREWCF + "). The route for a large ASP.NET application is incremental: "
             "an ASP.NET Core app in front proxies every route not yet migrated to the Framework app with YARP, and "
             "the System.Web adapters let shared libraries keep using <code>HttpContext</code> while routes move "
             "(" + FXCORE + " · " + INCREMENTAL + "). Web Forms has no port — its pages are rebuilt, typically in "
             "Blazor (" + WEBFORMS + "). VB6 is COM, not .NET: " + ref(6) + ".</p>"
             "<p><b>Tools now plan and rewrite code; they do not make the decisions.</b> .NET Upgrade Assistant is "
             "deprecated in favour of GitHub Copilot app modernization (" + PORTING + "). AWS Transform for .NET "
             "moves .NET Framework 3.5+ code to .NET 8 or .NET 10 on Linux; the project types it lists include MVC, "
             "Web API, Web Forms and WCF services, with VB.NET in preview (" + TRANSFORM + "). Both produce a plan "
             "and a branch; the 7 R call and the target stay with you.</p>")},

        {"type": "table", "heading": "7.1 · Porting map — .NET Framework on IIS → .NET 10",
         "cols": ["In the Framework app", "On .NET 10", "Kind", "Watch for"],
         "rows": [
             ["ASP.NET MVC 5 · Web API 2 (<code>System.Web</code>)", "ASP.NET Core controllers or minimal APIs — "
              + ref(8), DIFFERENT, "Migrate route by route; System.Web adapters for shared <code>HttpContext</code> code"],
             ["Web Forms (<code>.aspx</code>)", "Blazor or Razor Pages", TRAP,
              "No port: pages are rebuilt, events become components"],
             ["WCF service (<code>.svc</code>)", "CoreWCF · gRPC for new callers", RENAMED,
              "1.0 shipped HTTP and NetTCP bindings: check your bindings against the current release"],
             ["<code>web.config</code> app settings · <code>Global.asax</code>",
              "<code>appsettings.json</code> + environment · <code>Program.cs</code> middleware", RENAMED,
              "Secrets move to a secrets manager — " + ref(11)],
             ["HTTP modules and handlers", "Middleware", RENAMED, "Order matters and is explicit in code"],
             ["Windows service · MSMQ", "<code>BackgroundService</code> worker · Amazon SQS", DIFFERENT,
              "MSMQ does not exist on Linux: the queue is an architecture change"],
             ["Application domains · .NET Remoting", "Processes or containers · gRPC, HTTP, StreamJsonRpc", DIFFERENT,
              "<code>AppDomain.CreateDomain</code> throws <code>PlatformNotSupportedException</code>"],
             ["Code access security · COM+ (<code>EnterpriseServices</code>)", "OS, container and IAM boundaries",
              TRAP, "No replacement API — redesign the boundary"],
             ["Windows Workflow Foundation", "CoreWF (community port) or Step Functions", DIFFERENT,
              "Not supported on .NET 6+ — decide per workflow"]]},

        panel(from_sample(TRIAGE, "rules"), "7.2 · The triage rules — one signal, one arm",
              "<b>The order of the arms is the policy.</b> A C# switch expression takes the first matching arm, so "
              "“stop” decisions (retire, buy, rewrite VB6) come before “can we lift it” (COM or GAC → rehost on "
              "Windows) and before the ports. Property patterns read like the inventory columns; <code>when</code> "
              "guards test the signal set. The inventory is illustrative, and the rules are a starting point to "
              "argue with, not an assessment method."),

        panel(from_text(TRIAGE_OUTPUT, "text", label="Output — L12.EstateTriage",
                        file="captured on the build machine 2026-09-16"),
              "7.3 · What you should see — sixteen applications, seven Rs",
              f"<b>{by_strategy['Replatform']} of {n_apps} applications replatform, and only "
              f"{by_strategy['Rehost']} need Windows servers at all.</b> The two rehosts are held back by COM and the "
              "GAC, not by C# or VB, and they can land on EC2 with IIS or in an ECS Windows container; the one refactor "
              "to Lambda is a spiky batch job; the WinForms desktop is retained and retargeted in place, and the VB6 "
              "desktop app is rewritten as a .NET desktop app (" + ref(6) + "). Relocate stays at zero: it moves servers to a "
              "cloud version of the same platform, and no row here is that.", keep=False),

        {"type": "chartrow", "charts": [
            {"heading": "7.4 · Applications per migration strategy", "kind": "bar",
             "args": {"data": strategies, "ylabel": "applications", "tone": "navy", "width": 390, "height": 220,
                      "rotate_labels": True},
             "caption": "parsed from the captured triage output (7.3) · illustrative inventory",
             "note": f"<b>Replatform dominates ({by_strategy['Replatform']} of {n_apps}), which matches AWS's advice "
                     "for large migrations.</b> Refactor is kept for a VB6 rewrite, a Web Forms rebuild and an "
                     "event-driven batch job. " + MEASURED},
            {"heading": "7.5 · Applications per target platform", "kind": "hbar",
             "args": {"data": targets, "tone": "rose", "width": 390, "labelw": 118},
             "caption": "parsed from the captured triage output (7.3) · retired = no target",
             "note": f"<b>ECS Fargate takes {by_target['ECS Fargate']} of {n_apps}.</b> Once "
                     "<code>System.Web</code> is gone a Linux container is the default; Lambda gets the one workload "
                     "whose traffic shape fits it. " + MEASURED}]},

        {"type": "mermaid", "inline": True,
         "heading": "7.6 · Strangling one IIS application behind YARP",
         "caption": "slate = still .NET Framework on IIS · teal = ASP.NET Core on .NET 10 · amber = the shared piece "
                    "· each release moves routes from the dotted path to the solid one",
         "code": ("flowchart LR\n"
                  '  U["Brokers and<br/>partners"]:::user --> Y["ASP.NET Core front<br/>YARP proxy, .NET 10"]:::core\n'
                  '  Y -- "migrated routes<br/>/quotes, /policies" --> N["ASP.NET Core<br/>endpoints"]:::core\n'
                  '  Y -. "every other route" .-> F["ASP.NET MVC 5<br/>on IIS, net48"]:::fx\n'
                  '  N --> LIB["Shared libraries<br/>net48 + net10.0<br/>System.Web adapters"]:::shared\n'
                  "  F --> LIB\n"
                  '  N -. "remote session<br/>and authentication" .-> F\n'
                  '  N --> DB[("Policy database")]:::data\n'
                  "  F --> DB\n"
                  "  classDef user fill:#c7d2fe,color:#1f2937,stroke:#6366f1;\n"
                  "  classDef core fill:#ccfbf1,color:#1f2937,stroke:#0d9488;\n"
                  "  classDef fx fill:#e2e8f0,color:#1f2937,stroke:#475569;\n"
                  "  classDef shared fill:#fde68a,color:#1f2937,stroke:#d97706;\n"
                  "  classDef data fill:#f1f5f9,color:#1f2937,stroke:#64748b;\n")},

        {"type": "table", "heading": "7.7 · Modernisation tools as of September 2026",
         "cols": ["Tool", "What it does", "Status"],
         "rows": [
             ["GitHub Copilot app modernization", "Assesses a solution, writes an upgrade plan, applies and "
              "validates the changes; its cloud steps target Azure", pill("Recommended by Microsoft", "green")
              + " needs GitHub Copilot access"],
             [".NET Upgrade Assistant", "Visual Studio extension and CLI that applies common upgrade changes",
              pill("Deprecated", "red") + " use only without Copilot access"],
             ["AWS Transform for .NET", ".NET Framework 3.5+ → .NET 8 or .NET 10 on Linux; MVC, Web API, Web Forms "
              "projects, WCF services; commits to a branch", pill("Available", "green") + " VB.NET in preview"],
             ["System.Web adapters · YARP", "Run Framework and Core side by side; share session and authentication",
              pill("Current · 2.3.0", "green") + " the incremental-migration toolkit"],
             ["CoreWCF", "Service-side WCF on .NET: SOAP over HTTP and NetTCP, WSDL", pill("Current · 1.9.1", "green")
              + " Microsoft support; gRPC for greenfield"]]},

        # ═══════════════════════════ 8 · HANDS-ON ═══════════════════════════
        {"type": "story", "heading": "8 · Hands-on — and what to learn after the track",
         "html": (
             f"<p><b>{n_proj} projects, one command to prove them.</b> <code>verify_samples.py</code> builds the VB "
             f"rating library and both Lambda projects, runs {total_tests} test cases in two test projects, builds "
             "the container API and runs the triage console to completion. None of it touches AWS.</p>"
             "<p><b>Two commands go further than the verifier.</b> <code>dotnet publish -t:PublishContainer</code> "
             "writes the image archive of 4.5 (it downloads the chiseled base image), and a plain "
             "<code>dotnet publish</code> of each Lambda project gives the folders whose zips 3.8 measures. "
             "Deploying for real needs an AWS account, a deploy role trusted for your repository and the variables "
             "<code>main.tf</code> declares.</p>"
             "<p><b>After the track, go deeper where your next project is.</b> For serverless, the AWS Lambda .NET "
             "developer guide and Powertools for AWS Lambda (.NET); for containers, the .NET container publishing "
             "reference; for a Framework estate, Microsoft's ASP.NET Framework → ASP.NET Core migration guide and "
             "AWS Transform for .NET; for the local loop and telemetry, Aspire. Keep re-verifying: Lambda runtime and "
             "SDK dates move every November.</p>")},

        panel(from_text("""
            # build, test and run every lesson-12 sample (from the repository root)
            python 0-script/verify_samples.py --only 12

            # the tests on their own
            dotnet test lesson-12-cloud-native-modernization/samples/L12.QuoteLambda.Tests
            dotnet test lesson-12-cloud-native-modernization/samples/L12.QuoteContainer.Tests

            # triage the illustrative estate
            dotnet run --project lesson-12-cloud-native-modernization/samples/L12.EstateTriage

            # a multi-arch image archive, no Docker (Git Bash: -t:, not /t:)
            dotnet publish lesson-12-cloud-native-modernization/samples/L12.QuoteContainer \\
                -c Release -t:PublishContainer -p ContainerArchiveOutputPath=./images/

            # the Lambda package folders measured in 3.8
            dotnet publish lesson-12-cloud-native-modernization/samples/L12.QuoteLambda -c Release -o out/cs
            dotnet publish lesson-12-cloud-native-modernization/samples/L12.QuoteLambdaVb -c Release -o out/vb
            """, "shell"), "8.1 · Commands",
              "<b>Every command runs offline except the image publish.</b> The SDK comes from "
              "<code>global.json</code> (10.0.401 or a later 10.0 feature band). <code>out/</code> and "
              "<code>images/</code> are scratch output — do not commit them."),

        panel(from_text("""
            dotnet SDK 10.0.401
            PASS  console     2.3s  $SAMPLES/L12.EstateTriage/L12.EstateTriage.csproj
            PASS  web         1.9s  $SAMPLES/L12.QuoteContainer/L12.QuoteContainer.csproj
            PASS  test        6.1s  $SAMPLES/L12.QuoteContainer.Tests/L12.QuoteContainer.Tests.csproj
            PASS  library     1.7s  $SAMPLES/L12.QuoteLambda/L12.QuoteLambda.csproj
            PASS  test        7.0s  $SAMPLES/L12.QuoteLambda.Tests/L12.QuoteLambda.Tests.csproj
            PASS  library     1.0s  $SAMPLES/L12.QuoteLambdaVb/L12.QuoteLambdaVb.vbproj
            PASS  library     1.0s  $SAMPLES/L12.RatingVb/L12.RatingVb.vbproj

            7/7 sample projects passed

            Passed!  - Failed: 0, Passed: 11, Skipped: 0, Total: 11 - L12.QuoteLambda.Tests.dll
            Passed!  - Failed: 0, Passed:  5, Skipped: 0, Total:  5 - L12.QuoteContainer.Tests.dll
            """, "text", label="Output — verify_samples, dotnet test",
                        file="captured 2026-09-16 · $SAMPLES = lesson-12-…/samples · SDK path, times, TFM, padding cut"),
              "8.2 · What you should see",
              "<b>Timings will differ; the counts should not.</b> Eleven Lambda test cases cover the illustrative "
              "rating totals, the Annotations function, the generated wrapper and C# ↔ VB handler parity; five "
              "container tests cover both health endpoints, the shutdown budget, the VB-computed total and the "
              "exported spans. If a count differs, a sample changed — the PDF build checks the source against "
              "these numbers."),

        {"type": "chart", "heading": "8.3 · Code lines per lesson-12 project", "kind": "hbar",
         "args": {"data": locs, "tone": "navy", "width": 760, "labelw": 170},
         "caption": "non-blank, non-comment C# and VB lines per project · measured at build time",
         "note": f"<b>The VB rating rules are {loc_by['RatingVb']} lines, and three hosts and {total_tests} test "
                 f"cases depend on them.</b> The largest project is <code>{top_proj[0]}</code> at {top_proj[1]} lines; "
                 f"the three hosts and their two test projects add up to "
                 f"{sum(loc_by[k] for k in ('QuoteLambda', 'QuoteLambdaVb', 'QuoteContainer', 'QuoteLambda.Tests', 'QuoteContainer.Tests'))} "
                 "lines around that small core — the shape a modernised estate should have: move the rules once, "
                 "re-host them many times. " + MEASURED},

        {"type": "callout", "variant": "warn", "heading": "⚠ Traps",
         "items": [
             "<b>“Module-scope state is fine in Lambda.”</b> It lives per execution environment, many run in "
             "parallel and any can be recycled — and on Lambda Managed Instances one handler object serves "
             "concurrent requests. Use DynamoDB for state and thread-safe types for caches.",
             "<b>“SnapStart is free and transparent.”</b> For .NET it bills caching and every restore; a GUID, "
             "random seed or cached credential created during INIT is identical in every restored copy; and it does "
             "not combine with provisioned concurrency or OS-only runtimes.",
             "<b>“Interpolated strings are just nicer logging.”</b> <code>LogInformation($\"Quoted {id}\")</code> "
             "writes one opaque message. Pass a template and arguments so CloudWatch Logs gets <code>QuoteId</code> "
             "as a field.",
             "<b>“The Dockerfile habits still apply.”</b> .NET 8+ images listen on 8080 as UID 1654, chiseled images "
             "have no shell for <code>CMD-SHELL</code> health checks or ICU for culture data, and "
             "<code>HostOptions.ShutdownTimeout</code> equal to the ECS <code>stopTimeout</code> leaves no margin.",
             "<b>“Terraform will accept any runtime AWS has launched.”</b> The provider validates the runtime list it "
             "was built with; pin a version that knows <code>dotnet10</code>. And in Git Bash, "
             "<code>/t:PublishContainer</code> becomes a path — write <code>-t:</code>."]},

        {"type": "callout", "variant": "ok", "heading": "✔ Checkpoint — you have finished the track when you can",
         "items": [
             f"Run <code>python 0-script/verify_samples.py --only 12</code> and see {n_proj}/{n_proj} passed.",
             "Write the handler string for a class-library function, with and without Annotations, and say what "
             "runs during INIT.",
             "Pick a target for a workload from the flow in 2.2 and defend it against two other columns of 2.3.",
             "Publish the API as an image archive and explain every row of table 4.7.",
             "Take one row of the triage output in 7.3 and list its ports from table 7.1 and its route to "
             "production from 7.6."]},

        {"type": "callout", "variant": "summary", "heading": "🔍 Check yourself",
         "items": [
             "What is the handler string of the Annotations function in <code>main.tf</code>, and why does it not name "
             "<code>QuoteFunctions</code>?",
             "Name three things SnapStart requires or rules out, and one thing it charges .NET functions for that "
             "Java functions do not pay.",
             "Why does the Terraform sample set <code>publish = true</code> and route the API to an alias?",
             "Which port and user does the published image run as, and which two .NET releases changed the image "
             "defaults?",
             "ECS sends SIGTERM to the API. Which host event fires, which timeout applies, and why is it 20 s in the "
             "sample?",
             "Which .NET types are OpenTelemetry's tracer, span and meter, and what happened to the X-Ray SDKs on "
             "25 February 2026?",
             "List the AWS 7 Rs, and name the tool Microsoft now recommends instead of .NET Upgrade Assistant."]},

        {"type": "footer",
         "html": ("<b>Lesson 12 in one line:</b> .NET on AWS is the architecture you already run with different "
                  "mechanics — Lambda finds a method by name and SnapStart or Native AOT answer its cold start, "
                  "the SDK builds non-root, chiseled, multi-arch images without a Dockerfile, OpenTelemetry sits on "
                  "APIs already in the base library, and a .NET Framework estate moves route by route after a "
                  "7 R triage. <br/><b>After the track:</b> build one real service end to end on your next project, "
                  "then go deeper through the AWS Lambda .NET guide, Powertools for AWS Lambda (.NET), the .NET "
                  "container reference, the ASP.NET Framework → ASP.NET Core migration guide and Aspire — and "
                  "re-verify the dates in this PDF every November, starting with " + ref(1) + ".")},
    ]
