# -*- coding: utf-8 -*-
"""Lesson 09 — Data Access with EF Core. Built to 1-analysis/spec_lesson-pdfs/_standard.md, shaped like lesson 01.
Unit spec: 1-analysis/spec_lesson-pdfs/lesson-09-data-access-efcore.md"""
import json
import re

from lesson_kit import (DIFFERENT, ESTIMATE, MEASURED, REPO, RENAMED, SAME, TRAP, VERIFIED,
                        T_ARCH, T_CS, T_LEGACY, days_until, esc, from_sample,
                        from_text, legend, link, loc, mapping, pill, snippet, style_block)
from lesson_kit import code as _kit_code, compare as _kit_compare
from lessons.roster import meta, ref

META = meta(
    9,
    subtitle="DbContext, LINQ-to-SQL, change tracking, concurrency, migrations and Dapper — EF Core 10 read "
             "through JPA/Hibernate, TypeORM and Flyway",
    objectives=[
        "Map a MotorQuote model with a DbContext, IEntityTypeConfiguration classes and complex types for Money, "
        "and say where it differs from JPA entities and @Embeddable",
        "Predict the SQL a LINQ query sends — read it with ToQueryString, and spot the IEnumerable, missing-Include "
        "and N+1 traps by counting commands",
        "Explain SaveChanges as a unit of work, wrap several writes in one explicit transaction, and build optimistic "
        "concurrency on a database with no rowversion",
        "Ship schema changes with dotnet ef: committed migrations, a CI gate, SQL scripts or migration bundles",
        "Choose between tracked EF Core, ExecuteUpdate, Dapper and the AWS SDK, and between SQLite in-memory, "
        "a real database and the InMemory provider for tests",
        "Query a C# DbContext from Visual Basic — and know which EF Core tooling refuses VB projects",
    ],
    maps_from="JPA/Hibernate entity mapping and the persistence context, Spring Data repositories and JdbcTemplate, "
              "TypeORM entities and query builders, Flyway/Liquibase migrations, H2 test databases — and the "
              "Metabase-style reporting SQL and DynamoDB access code you have written for insurance platforms.",
)

L = "lesson-09-data-access-efcore/samples"
DATA = f"{L}/L09.Data"
TESTS = f"{L}/L09.Data.Tests"
CONSOLE = f"{L}/L09.QueryConsole/Program.cs"
VB_REPORT = f"{L}/L09.VbReport/Program.vb"
VB_MODEL = f"{L}/L09.VbModel/LegacyQuoteContext.vb"
MIGRATION = f"{DATA}/Migrations/20260914121532_InitialCreate.cs"
PROJECTS = ["L09.Data", "L09.Data.Tests", "L09.QueryConsole", "L09.VbReport", "L09.VbModel"]

# ── official sources ────────────────────────────────────────────────────────────────────────────────────────
EF_RELEASES = link("EF Core releases and planning", "https://learn.microsoft.com/en-us/ef/core/what-is-new/")
EF10 = link("What's new in EF Core 10", "https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-10.0/whatsnew")
COMPLEX = link("Complex types", "https://learn.microsoft.com/en-us/ef/core/modeling/complex-types")
MODELING = link("Creating and configuring a model", "https://learn.microsoft.com/en-us/ef/core/modeling/")
LIFETIME = link("DbContext lifetime", "https://learn.microsoft.com/en-us/ef/core/dbcontext-configuration/")
SPLIT = link("Single vs. split queries", "https://learn.microsoft.com/en-us/ef/core/querying/single-split-queries")
LAZY = link("Lazy loading", "https://learn.microsoft.com/en-us/ef/core/querying/related-data/lazy")
SQLQ = link("SQL queries", "https://learn.microsoft.com/en-us/ef/core/querying/sql-queries")
CONCURRENCY = link("Handling concurrency conflicts", "https://learn.microsoft.com/en-us/ef/core/saving/concurrency")
EXECUPD = link("ExecuteUpdate and ExecuteDelete",
               "https://learn.microsoft.com/en-us/ef/core/saving/execute-insert-update-delete")
BATCHING = link("Efficient updating", "https://learn.microsoft.com/en-us/ef/core/performance/efficient-updating")
APPLYING = link("Applying migrations",
                "https://learn.microsoft.com/en-us/ef/core/managing-schemas/migrations/applying")
EF9BREAK = link("EF Core 9 breaking changes",
                "https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-9.0/breaking-changes")
EFCLI = link("EF Core tools reference", "https://learn.microsoft.com/en-us/ef/core/cli/dotnet")
SQLITE_LIMITS = link("SQLite provider limitations",
                     "https://learn.microsoft.com/en-us/ef/core/providers/sqlite/limitations")
TESTING = link("Choosing a testing strategy",
               "https://learn.microsoft.com/en-us/ef/core/testing/choosing-a-testing-strategy")
PROVIDERS = link("Database providers", "https://learn.microsoft.com/en-us/ef/core/providers/")
EF6 = link("Compare EF6 and EF Core", "https://learn.microsoft.com/en-us/ef/efcore-and-ef6/")
NPGSQL = link("Npgsql EF Core provider on NuGet", "https://www.nuget.org/packages/Npgsql.EntityFrameworkCore.PostgreSQL")
MYSQL = link("MySql.EntityFrameworkCore on NuGet", "https://www.nuget.org/packages/MySql.EntityFrameworkCore")
POMELO = link("Pomelo MySQL provider on NuGet", "https://www.nuget.org/packages/Pomelo.EntityFrameworkCore.MySql")
VBPKG = link("EntityFrameworkCore.VisualBasic on NuGet", "https://www.nuget.org/packages/EntityFrameworkCore.VisualBasic")
DAPPER = link("Dapper", "https://github.com/DapperLib/Dapper")
DYNAMO = link("DynamoDB .NET object persistence model",
              "https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DotNetSDKHighLevel.html")
TESTCONTAINERS = link("Testcontainers for .NET", "https://dotnet.testcontainers.org/")
CONNRES = link("Connection resiliency",
               "https://learn.microsoft.com/en-us/ef/core/miscellaneous/connection-resiliency")
NPGSQL_TOKEN = link("Npgsql concurrency tokens", "https://www.npgsql.org/efcore/modeling/concurrency.html")

# ── captured from real runs on the build machine (Windows x64, .NET SDK 10.0.401, EF Core 10.0.12) ───────────
CONSOLE_OUT = """
EF Core 10.0.12 on SQLite in-memory; illustrative rates

== 1. ToQueryString: a projection
  .param set @coverage 'Class1'

  SELECT "q"."Reference", "v"."Make", "q"."Total_Amount", (
      SELECT COUNT(*)
      FROM "PremiumLines" AS "p"
      WHERE "q"."Id" = "p"."QuoteId")
  FROM "Quotes" AS "q"
  INNER JOIN "Vehicles" AS "v" ON "q"."VehicleId" = "v"."Id"
  WHERE "q"."Coverage" = @coverage
  ORDER BY "q"."Reference"
  Q-0001  Toyota  12,289.76  4 lines
  Q-0005  Isuzu   22,044.23  5 lines
  Q-0009  Mazda   22,559.88  3 lines
  Q-0013  Toyota  21,034.40  4 lines
  Q-0017  Honda   12,461.65  3 lines

== 2. Commands to load N quotes with their premium lines
  quotes   N+1   Include   AsSplitQuery
       1     2         1              2
       5     6         1              2
      10    11         1              2
      20    21         1              2

== 3. One Count as IEnumerable, as IQueryable; then AsNoTracking
  IEnumerable  count 5  commands 1  tracked 20
  SELECT "q"."Id", "q"."Coverage", "q"."Reference", "q"."Status", "q"."ValidUntil",
        "q"."VehicleId", "q"."Version", "q"."Driver_ClaimsLast5Years",
        "q"."Driver_DateOfBirth", "q"."Driver_LicenceYears", "q"."Total_Amount",
        "q"."Total_Currency"
  FROM "Quotes" AS "q"
  IQueryable   count 5  commands 1  tracked 0
  SELECT COUNT(*)
  FROM "Quotes" AS "q"
  WHERE "q"."Coverage" = 'Class1'
  AsNoTracking count 5  commands 1  tracked 0

== 4. FromSql with hostile input
  input  Toyota' OR '1'='1
  rows   0
  SELECT * FROM Vehicles WHERE Make = @p0

== 5. Expire stale quotes: tracked SaveChanges vs ExecuteUpdate
  tracked + SaveChanges  rows 10  commands 11
  ExecuteUpdate          rows 10  commands  1
  UPDATE "Quotes" AS "q"
  SET "Status" = @p,
      "Version" = @p2
  WHERE "q"."Status" = 'Quoted' AND "q"."ValidUntil" < @today

== 6. Quoted quotes by coverage: EF Core LINQ and Dapper SQL
  LINQ    Class1       5
  LINQ    Class2Plus   3
  LINQ    Class3       4
  LINQ    Class3Plus   5
  Dapper  Class1       5  lines 19
  Dapper  Class2Plus   3  lines 11
  Dapper  Class3       4  lines 16
  Dapper  Class3Plus   5  lines 19

== 7. decimal is stored as TEXT on SQLite
  EF Core  top 3 by total  Q-0009, Q-0005, Q-0013
  .param set @p 3

  SELECT "q"."Reference"
  FROM "Quotes" AS "q"
  ORDER BY "q"."Total_Amount" COLLATE EF_DECIMAL DESC
  LIMIT @p
  EF Core  totals over 20,000: 3
  SELECT "q"."Reference"
  FROM "Quotes" AS "q"
  WHERE ef_compare("q"."Total_Amount", '20000.0') > 0
  raw SQL  top 3 by total  Q-0015 9919.91, Q-0003 8604.98, Q-0002 7476.99
  raw SQL  3 smallest (CAST AS REAL)  Q-0016 2457.95, Q-0012 2492.33, Q-0008 3824.44
"""

VB_OUT = """
L09.VbReport: a C# DbContext queried from Visual Basic
  Class1       5
  Class2Plus   3
  Class3       4
  Class3Plus   5
SELECT "q"."Coverage", COUNT(*) AS "Quotes"
FROM "Quotes" AS "q"
WHERE "q"."Status" = 'Quoted'
GROUP BY "q"."Coverage"
ORDER BY "q"."Coverage"
SELECT "v"."Model"
FROM "Vehicles" AS "v"
WHERE "v"."Make" = 'Toyota'
  models: Yaris Ativ, Hilux Revo
"""

BUNDLE_BYTES = 34_632_598  # efbundle.exe from `dotnet ef migrations bundle` on the build machine (win-x64)

# Pygments' vbnet lexer has no token for VB 14 interpolated strings, so every `$"` prints inside a red error box.
# The code is valid (the samples compile); drop the box, keep the text. (same fix as lessons 01, 03 and 06)
_ERROR_SPAN = re.compile(r'<span style="border: 1px solid #F00">(.*?)</span>', re.S)


def _listed(block, heading):
    """Put a numbered code panel in the Contents at level 2 and clean VB highlighting (as lessons 01, 03, 06)."""
    if heading:
        block.update(heading=heading, toc=2)
    if "vb" in block.get("_langs", []):
        block["html"] = _ERROR_SPAN.sub(r"\1", block["html"])
    return block


def code(s, *, heading=None, note=None, keep=None):
    return _listed(_kit_code(s, heading=heading, note=note, keep=keep), heading)


def compare(left, right, *, heading=None, note=None, keep=None):
    return _listed(_kit_compare(left, right, heading=heading, note=note, keep=keep), heading)


def figure_heading(text):
    """A numbered heading for a block type that prints none of its own (twocol), kept with that block."""
    return {"type": "html", "html": f'<div class="figh"><h2>{esc(text)}</h2></div>', "heading": text,
            "toc": 2, "_keep_with_next": True}


def kept_table(heading, cols, rows, note=None):
    """A numbered table printed in one piece (heading, rows and reading never split across pages)."""
    head = "<thead><tr>" + "".join(f"<th>{esc(c)}</th>" for c in cols) + "</tr></thead>"
    body = "<tbody>" + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows) + "</tbody>"
    nt = f'<div class="fign" style="margin:6px 0 10px">{note}</div>' if note else ""
    return {"type": "html", "heading": heading, "toc": 2,
            "html": (f'<div style="break-inside:avoid;page-break-inside:avoid"><h2>{esc(heading)}</h2>'
                     f'<table class="sum">{head}{body}</table>{nt}</div>')}


def _section(num):
    """Lines of one `== N.` section of the captured L09.QueryConsole output."""
    text = CONSOLE_OUT.strip("\n")
    part = text.split(f"== {num}.", 1)[1].split("\n== ", 1)[0]
    return part.splitlines()[1:]


def _sources(project, generated=None):
    """.cs / .vb files of one sample project; generated=True only Migrations/, False everything else."""
    root = REPO / L / project
    files = sorted(list(root.rglob("*.cs")) + list(root.rglob("*.vb")))
    out = []
    for p in files:
        if {"bin", "obj"} & set(p.parts):
            continue
        in_mig = "Migrations" in p.parts
        if generated is None or generated == in_mig:
            out.append(p.relative_to(REPO).as_posix())
    return out


def _test_cases_by_class():
    """[Fact] methods + [InlineData] rows per test class — a MEASURED figure."""
    counts = {}
    for rp in _sources("L09.Data.Tests"):
        text = (REPO / rp).read_text(encoding="utf-8-sig")
        parts = re.split(r"^public class (\w+)", text, flags=re.M)
        for name, body in zip(parts[1::2], parts[2::2]):
            n = len(re.findall(r"^\s*\[Fact\]", body, re.M)) + len(re.findall(r"^\s*\[InlineData\(", body, re.M))
            counts[name] = counts.get(name, 0) + n
    return counts


def _package_version(project_file, package):
    text = (REPO / project_file).read_text(encoding="utf-8-sig")
    return re.search(rf'Include="{re.escape(package)}" Version="([^"]+)"', text).group(1)


def cmd(*commands):
    """Table-cell commands that never wrap inside themselves."""
    return " · ".join(f'<code style="white-space:nowrap">{c}</code>' for c in commands)


def blocks():
    # ── measured figures ────────────────────────────────────────────────────────────────────────────────────
    loads = [tuple(int(x) for x in ln.split()) for ln in _section(2) if re.match(r"^\s*\d", ln)]
    ns = [str(r[0]) for r in loads]
    nplus1 = {r[0]: r[1] for r in loads}
    include = {r[0]: r[2] for r in loads}
    split = {r[0]: r[3] for r in loads}
    n_max = max(nplus1)
    shape = {m.group(1): (int(m.group(2)), int(m.group(3)), int(m.group(4)))
             for m in (re.match(r"^\s*(\w+)\s+count (\d+)\s+commands (\d+)\s+tracked (\d+)", ln) for ln in _section(3))
             if m}
    expire = {m.group(1).strip(): (int(m.group(2)), int(m.group(3)))
              for m in (re.match(r"^\s*(tracked \+ SaveChanges|ExecuteUpdate)\s+rows\s+(\d+)\s+commands\s+(\d+)", ln)
                        for ln in _section(5)) if m}
    tracked_rows, tracked_cmds = expire["tracked + SaveChanges"]
    bulk_rows, bulk_cmds = expire["ExecuteUpdate"]
    cases = _test_cases_by_class()
    n_tests = sum(cases.values())
    ef_version = _package_version(f"{DATA}/L09.Data.csproj", "Microsoft.EntityFrameworkCore.Sqlite")
    dapper_version = _package_version(f"{DATA}/L09.Data.csproj", "Dapper")
    tool_version = json.loads((REPO / L / "dotnet-tools.json").read_text(encoding="utf-8-sig"))[
        "tools"]["dotnet-ef"]["version"]
    n_proj = len(list((REPO / L).glob("*/*.*proj")))
    loc_rows = [("L09.Data (hand-written)", loc(*_sources("L09.Data", generated=False))),
                ("L09.Data Migrations (generated)", loc(*_sources("L09.Data", generated=True))),
                ("L09.Data.Tests", loc(*_sources("L09.Data.Tests"))),
                ("L09.QueryConsole", loc(*_sources("L09.QueryConsole"))),
                ("L09.VbReport (VB)", loc(*_sources("L09.VbReport"))),
                ("L09.VbModel (VB)", loc(*_sources("L09.VbModel")))]
    hand = loc_rows[0][1]
    generated = loc_rows[1][1]
    d_ef10 = days_until(2028, 11, 10)
    migration_lines = len(snippet(MIGRATION, "create-quotes").splitlines())
    sec7 = "\n".join(_section(7))
    raw7 = {"ef": re.search(r"EF Core  top 3 by total  (.+)", sec7).group(1),
            "top": re.search(r"raw SQL  top 3 by total  (.+)", sec7).group(1),
            "cast": re.search(r"raw SQL  3 smallest \(CAST AS REAL\)  (.+)", sec7).group(1)}

    model_cards = [
        {"num": 1, "title": "Conventions", "tags": [T_CS], "pills": [SAME],
         "what": "EF Core builds most of the model without being told: <code>Id</code> is the key, a "
                 "<code>List&lt;PremiumLine&gt;</code> navigation is a one-to-many, public properties become columns.",
         "lines": [("JPA", "The defaults behind <code>@Entity</code> — but EF needs no marker on the class"),
                   ("Finds", "Every type reachable from a <code>DbSet</code> or from another entity's navigation"),
                   ("Watch", "Enums map to integers; <code>Money</code> is not discovered as a complex type — "
                             "configure it"),
                   ("Sample", "<code>Vehicle.Id</code>, <code>Quote.VehicleId</code> and the table names")]},
        {"num": 2, "title": "Data annotations", "tags": [T_CS], "pills": [RENAMED],
         "what": "Attributes on the class — <code>[Key]</code>, <code>[MaxLength]</code>, "
                 "<code>[ConcurrencyCheck]</code>, <code>[Timestamp]</code>, <code>[ComplexType]</code>.",
         "lines": [("JPA", "<code>@Id</code>, <code>@Column(length=…)</code>, <code>@Version</code>, "
                           "<code>@Embeddable</code>"),
                   ("Costs", "None for these five — they are BCL types. EF's own <code>[Index]</code>, <code>[Owned]</code>, "
                             "<code>[Precision]</code> live in <code>Microsoft.EntityFrameworkCore.Abstractions</code> "
                             "and do put EF in the domain assembly"),
                   ("Rule", "Fluent API configuration overrides an attribute when both are present (" + MODELING + ")")]},
        {"num": 3, "title": "Fluent API in IEntityTypeConfiguration", "tags": [T_CS, T_ARCH], "pills": [DIFFERENT],
         "what": "One configuration class per entity, applied by "
                 "<code>ApplyConfigurationsFromAssembly</code>.",
         "lines": [("JPA", "<code>orm.xml</code>, rarely used — annotations won; in EF Core the Fluent API is "
                           "the idiomatic default"),
                   ("Gives", "Persistence-ignorant entities, and what annotations cannot say (value conversions, "
                             "query filters, seed data)"),
                   ("Sample", "<code>QuoteConfiguration</code> in 2.2")]},
        {"num": 4, "title": "Complex types", "tags": [T_CS], "pills": [SAME],
         "what": "A value object with no key, stored as columns of its owner's table (or one JSON column).",
         "lines": [("JPA", "<code>@Embeddable</code> / <code>@Embedded</code>"),
                   ("Since", "EF Core 8; structs, optional values and JSON mapping in EF Core 10 (" + COMPLEX + ")"),
                   ("Limits", "No navigations inside; collections of complex types only as JSON"),
                   ("Sample", "<code>Money</code> → <code>Total_Amount</code>, <code>Total_Currency</code>")]},
        {"num": 5, "title": "Owned entity types", "tags": [T_CS, T_LEGACY], "pills": [TRAP],
         "what": "The older way to embed a value object — everywhere in codebases written before EF Core 8.",
         "lines": [("Looks", "Like <code>@Embeddable</code>: <code>OwnsOne(q =&gt; q.Total)</code>"),
                   ("Is", "An entity with a hidden key and reference semantics — one instance cannot be assigned "
                          "to two properties"),
                   ("Advice", "Microsoft now recommends complex types for value objects (" + EF10 + ")")]},
        {"num": 6, "title": "Value converters", "tags": [T_CS], "pills": [RENAMED],
         "what": "Store a property as another type: <code>HasConversion&lt;string&gt;()</code> on an enum.",
         "lines": [("JPA", "<code>@Enumerated(STRING)</code> · <code>AttributeConverter</code>"),
                   ("Watch", "Strings sort as text: <code>ORDER BY Coverage</code> puts <code>Class3</code> before "
                             "<code>Class3Plus</code> (6.1 output)"),
                   ("Sample", "<code>Coverage</code>, <code>Status</code> and <code>Use</code>")]},
    ]

    return [
        style_block(),
        {"type": "toc", "heading": "▤ Contents", "depth": 2},
        # a callout or story heading must not print alone at a page foot with its text on the next page
        {"type": "html", "html": "<style>.callout .ct, .story .ct { break-after:avoid; page-break-after:avoid; } "
                                 ".callout li:first-child, .story .ct + p { break-before:avoid; "
                                 "page-break-before:avoid; } .story p { orphans:3; widows:3; } "
                                 "h2 { break-after:avoid; page-break-after:avoid; } "
                                 "h2 + table.sum { break-before:avoid; page-break-before:avoid; } "
                                 "a.lnk { word-break:normal; overflow-wrap:normal; }</style>"},

        # ═══════════════════════════ 1 · WHY ═══════════════════════════
        {"type": "story", "heading": "1 · Why data access is where a .NET service shows its age",
         "html": (
             "<p><b>You have shipped JPA entities, TypeORM repositories, Flyway migrations and hand-tuned reporting "
             "SQL, so an ORM is not new to you — what is new is where EF Core draws its lines.</b> A quoting service "
             "for a motor-insurance platform with dozens of partner integrations lives or dies on its data layer: "
             "the premium lines, the quote status machine, the concurrent underwriter and broker edits. EF Core "
             "covers the same ground as Hibernate, but the persistence context is shorter-lived, lazy loading is off, "
             "queries never flush pending changes, and migrations are generated C# rather than hand-written SQL.</p>"
             "<p><b>The fastest way to learn EF Core is to count the SQL it sends.</b> Every sample in this lesson "
             "runs against SQLite in memory with an interceptor that records each command, so the N+1 problem, the "
             "cost of a tracked bulk update and the difference between <code>IQueryable</code> and "
             "<code>IEnumerable</code> are numbers you can assert in a test, not rules of thumb.</p>"
             "<p><b>EF Core is not the only tool, and choosing between the tools is the architecture work.</b> Dapper "
             "is the <code>JdbcTemplate</code> of .NET; <code>ExecuteUpdate</code> is the "
             "<code>@Modifying @Query</code>; DynamoDB has no EF Core provider, so the AWS SDK's own persistence model "
             "takes EF's place there. Section 6 lays the options side by side.</p>"
             "<p><b>Legacy estates add a VB dimension.</b> Visual Basic code can query a C# <code>DbContext</code> "
             "directly, but the EF Core design-time tools generate only C#. The practical architecture — model and "
             "migrations in a C# library, VB consumers — is shown in section 8.</p>")},

        {"type": "kpi", "heading": "1.1 · The numbers to leave this lesson with",
         "items": [
             {"label": "EF Core 10 · LTS", "value": "to Nov 2028", "tone": "teal",
              "sub": f"ends 10 Nov 2028 · {d_ef10} days from build · verified"},
             {"label": f"Load {n_max} quotes + lines", "value": f"{nplus1[n_max]} → {include[n_max]}",
              "tone": "red", "sub": "commands: N+1 vs Include · measured"},
             {"label": f"Expire {tracked_rows} quotes", "value": f"{tracked_cmds} → {bulk_cmds}", "tone": "amber",
              "sub": "commands: SaveChanges vs ExecuteUpdate · measured"},
             {"label": "Test cases", "value": str(n_tests), "tone": "indigo",
              "sub": "L09.Data.Tests on SQLite in-memory · measured"},
             {"label": "InMemory provider", "value": "discouraged", "tone": "slate",
              "sub": "for testing, per Microsoft · verified"}]},

        legend(T_CS, T_ARCH, T_LEGACY),

        {"type": "callout", "variant": "info", "heading": "ℹ Before you start",
         "items": [
             "<b>You need " + ref(4) + " for LINQ and expression trees, and " + ref(8) + " for dependency "
             "injection</b> — <code>AddDbContext</code> registers a context per request scope, which is the "
             "lifetime this lesson assumes.",
             f"<b>You will build five projects:</b> <code>L09.Data</code> (C# library: "
             f"<code>MotorQuoteDbContext</code>, entities, configuration, a committed migration, Dapper report), "
             f"<code>L09.Data.Tests</code> ({n_tests} xUnit cases on SQLite in-memory), "
             f"<code>L09.QueryConsole</code> (prints the SQL), <code>L09.VbReport</code> (VB console querying the C# "
             f"context) and <code>L09.VbModel</code> (a VB-declared context the tools refuse).",
             f"<b>Packages:</b> EF Core {ef_version} (SQLite provider), Dapper {dapper_version}, and the "
             f"<code>dotnet-ef</code> {tool_version} local tool pinned in <code>samples/dotnet-tools.json</code> — "
             "run <code>dotnet tool restore</code> once in the samples folder. No database server, Docker or cloud "
             "account is needed. EF Core 10 is supported until 10 November 2028, in step with .NET 10's "
             "long-term support (" + EF_RELEASES + ").",
             "Premiums in the seed data use <b>illustrative rates, not a real tariff</b>. Facts that change with "
             "releases are " + VERIFIED + " and linked; numbers from runs of the samples are " + MEASURED + "; "
             "judgements are " + ESTIMATE + ". Kotlin, Java and TypeScript panels are for comparison and are not "
             "compiled."]},

        # ═══════════════════════════ 2 · THE MODEL ═══════════════════════════
        {"type": "story", "heading": "2 · The model — DbContext, entities and value objects",
         "html": (
             "<p><b>A <code>DbContext</code> is a Hibernate <code>Session</code> you are expected to throw away after "
             "one unit of work.</b> It holds the identity map and change tracker, exposes <code>DbSet&lt;T&gt;</code> "
             "roots for queries, and writes everything in <code>SaveChanges</code>. It is not thread-safe, so a web "
             "app gets one per request from <code>AddDbContext</code>; a second operation started before the first "
             "completes throws (" + LIFETIME + "). Await every call at once (lesson 05). For "
             "parallel work or a <code>BackgroundService</code>, inject <code>IDbContextFactory&lt;T&gt;</code> and "
             "create one context per task; <code>AddDbContextPool</code> reuses instances under load (lesson 08).</p>"
             "<p><b>The mapping lives beside the entities, not on them.</b> JPA taught you to annotate the entity. EF "
             "Core can read attributes too, but the idiomatic shape is a plain class plus an "
             "<code>IEntityTypeConfiguration&lt;T&gt;</code> written with the Fluent API, which wins when both are "
             "present. The domain types stay persistence-ignorant, and what attributes cannot express — value conversions, "
             "query filters, seed data — sits in one place.</p>"
             "<p><b>Value objects are complex types, and EF Core 10 finally lets <code>Money</code> be a struct.</b> "
             "Complex types (EF Core 8) are the <code>@Embeddable</code> of EF: no key, value semantics, columns "
             "on the owner's table. EF Core 10 added struct complex types, optional complex types and JSON mapping, "
             "and Microsoft advises users of the older <i>owned entity types</i> to switch (" + EF10 + "). The "
             "samples map <code>Money</code> as a <code>readonly record struct</code>, stored as "
             "<code>Total_Amount</code> and <code>Total_Currency</code>.</p>")},

        mapping("2.1 · Concept map — JPA, Hibernate, TypeORM and Flyway → EF Core", [
            ("<code>EntityManager</code> / Hibernate <code>Session</code>", "<code>DbContext</code>", "renamed",
             "Short-lived unit of work; not thread-safe; scoped per request — " + ref(8)),
            ("<code>@Entity</code> + field annotations · TypeORM <code>@Entity</code>/<code>@Column</code>", "Plain class + <code>IEntityTypeConfiguration&lt;T&gt;</code>",
             "different", "Fluent API overrides attributes; no marker needed on the class"),
            ("<code>@Embeddable</code> / <code>@Embedded</code>", "Complex type — <code>ComplexProperty</code>", "same",
             "EF Core 10: structs and optional values; columns named <code>Total_Amount</code>"),
            ("<code>@Enumerated(EnumType.STRING)</code>", "<code>HasConversion&lt;string&gt;()</code>", "renamed",
             "The column sorts as text, not in declaration order"),
            ("<code>@Version</code> (Hibernate increments it)", "<code>IsConcurrencyToken()</code> / "
             "<code>[Timestamp]</code>", "trap",
             "EF never increments a token for you; only a database-generated one changes by itself — SQL Server "
             "<code>rowversion</code>, PostgreSQL <code>xmin</code> through Npgsql"),
            ("Lazy <code>@OneToMany</code> through proxies", "No lazy loading unless enabled — Proxies package or <code>ILazyLoader</code>",
             "trap", "A forgotten <code>Include</code> gives an empty list — no exception (" + LAZY + ")"),
            ("<code>JOIN FETCH</code> / <code>@EntityGraph</code>", "<code>Include</code> / <code>ThenInclude</code>",
             "renamed", "Add <code>AsSplitQuery</code> when several collections multiply rows"),
            ("JPQL · Criteria API · TypeORM <code>QueryBuilder</code>", "LINQ over <code>IQueryable&lt;T&gt;</code>",
             "different", "The same lambda typed as <code>IEnumerable</code> filters in memory"),
            ("Flush before a query (<code>FlushMode.AUTO</code>)", "No automatic flush", "trap",
             "Queries read the database; tracked instances keep their unsaved values (4.5)"),
            ("<code>@Transactional</code> (declarative)", "No declarative transactions — <code>SaveChanges</code> "
             "is one; else <code>BeginTransactionAsync()</code>", "different",
             "Write the transaction in code, commit explicitly, dispose to roll back (4.6)"),
            ("<code>@Modifying @Query(\"update …\")</code>", "<code>ExecuteUpdate</code> / <code>ExecuteDelete</code>",
             "same", "Skips the change tracker and concurrency tokens; Dapper is the <code>JdbcClient</code> (6.1)"),
            ("TypeORM <code>migration:generate</code> · Liquibase <code>diff-changelog</code>",
             "<code>dotnet ef migrations add</code>", "same",
             "Both write the migration from a model diff; EF diffs against a committed snapshot, TypeORM against the "
             "live schema"),
            ("Flyway <code>V1__init.sql</code> · Liquibase changelog", "Migrations: generated C# + model snapshot",
             "different", "Hand-written SQL becomes generated C#; SQL is derived, not authored"),
            ("H2 in-memory database for tests", "SQLite in-memory", "same",
             "The EF Core InMemory provider is not a database — avoid it"),
        ]),

        compare(from_text("""
            @Entity
            @Table(name = "quotes")
            class Quote(
                @Id @GeneratedValue
                var id: Long? = null,
                @Column(unique = true, length = 12)
                var reference: String,
                @Enumerated(EnumType.STRING)
                @Column(length = 12)
                var coverage: CoverageClass,
                @Embedded
                @AttributeOverride(name = "amount",
                    column = Column(precision = 12, scale = 2))
                var total: Money,
                @Embedded
                var driver: Driver,
                @ManyToOne(optional = false)
                var vehicle: Vehicle,
                @OneToMany(cascade = [CascadeType.ALL])
                @JoinColumn(name = "quote_id")
                val lines: MutableList<PremiumLine> = mutableListOf(),
                @Version
                var version: Long = 0,
            )
            """, "kotlin", file="JPA annotations on the entity"),
                from_sample(f"{DATA}/Configuration.cs", "quote-config"),
                heading="2.2 · The same mapping — JPA annotations vs an EF Core configuration class",
                note="<b>Line for line the same decisions, in a different place.</b> <code>HasIndex().IsUnique()</code> "
                     "is <code>unique = true</code>; <code>HasConversion&lt;string&gt;()</code> is "
                     "<code>EnumType.STRING</code>; <code>ComplexProperty</code> is <code>@Embedded</code>. Two lines "
                     "differ in behaviour: <code>OnDelete(Restrict)</code> is explicit because EF's default for a "
                     "required relationship is cascade, and <code>IsConcurrencyToken()</code> only adds the "
                     "<code>WHERE Version = @original</code> check — unlike <code>@Version</code>, nothing increments "
                     "it (4.3 does)."),

        code(from_sample(f"{DATA}/MotorQuoteDbContext.cs", "context"),
             heading="2.3 · The context — a primary constructor, four DbSets, configurations by assembly scan",
             note="<b>No connection string and no provider in the class.</b> The options arrive through the "
                  "constructor, so the same context runs on SQLite in tests and on another provider in production. "
                  "<code>partial</code> lets 4.3 add the token-stamping override in a second file."),

        code(from_sample(f"{DATA}/Domain.cs", "money"),
             heading="2.4 · Value objects — a record struct and a record, both complex types",
             note="<b>Value semantics are the point.</b> Assigning one quote's <code>Total</code> to another copies "
                  "the values; with an owned entity type the same assignment fails because the instance has an "
                  "identity (" + COMPLEX + "). <code>decimal</code>, never <code>double</code>, for money — "
                  + ref(2) + "."),

        {"type": "mermaid", "inline": True, "toc": False,
         "heading": "2.5 · The schema the committed migration creates",
         "caption": "tables from the InitialCreate migration · complex-type columns carry their owner's prefix "
                    "(Total_, Driver_, SumInsured_, Amount_) · decimals are TEXT because this is SQLite · selected columns "
                    "shown",
         "code": ('%%{init: {"theme":"base","themeVariables": {"primaryColor":"#E0E7FF","primaryBorderColor":'
                  '"#6366F1","primaryTextColor":"#1f2937","lineColor":"#475569","tertiaryColor":"#F8FAFC",'
                  '"attributeBackgroundColorOdd":"#FFFFFF","attributeBackgroundColorEven":"#F1F5F9"}}}%%\n'
                  "erDiagram\n"
                  "  direction LR\n"
                  '  VEHICLES ||--o{ QUOTES : "priced for"\n'
                  '  QUOTES ||--|{ PREMIUMLINES : "itemised by"\n'
                  '  QUOTES ||--o| POLICIES : "accepted as"\n'
                  "  VEHICLES {\n"
                  "    int Id PK\n"
                  "    text Make\n"
                  "    text Use \"enum as string\"\n"
                  "    text SumInsured_Amount \"Money\"\n"
                  "  }\n"
                  "  QUOTES {\n"
                  "    int Id PK\n"
                  "    text Reference UK\n"
                  "    int VehicleId FK\n"
                  "    text Coverage \"enum as string\"\n"
                  "    text Total_Amount \"Money\"\n"
                  "    text Total_Currency \"Money\"\n"
                  "    text Driver_DateOfBirth \"Driver\"\n"
                  "    text Status \"enum as string\"\n"
                  "    text ValidUntil\n"
                  "    text Version \"concurrency token\"\n"
                  "  }\n"
                  "  PREMIUMLINES {\n"
                  "    int Id PK\n"
                  "    int QuoteId FK\n"
                  "    text Kind\n"
                  "    text Amount_Amount \"Money\"\n"
                  "  }\n"
                  "  POLICIES {\n"
                  "    int Id PK\n"
                  "    int QuoteId FK\n"
                  "    text PolicyNumber UK\n"
                  "  }\n")},

        {"type": "cards",
         "band": {"title": "2.6 · Six mapping tools — which one a codebase uses tells you its era", "note": "model view",
                  "tone": "violet"},
         "cards": model_cards[:3]},
        {"type": "cards", "toc": False,
         "band": {"title": "2.6 · Six mapping tools (continued)", "note": "model view", "tone": "violet"},
         "cards": model_cards[3:]},

        # ═══════════════════════════ 3 · QUERYING ═══════════════════════════
        {"type": "story", "heading": "3 · Querying — LINQ becomes SQL, or it silently does not",
         "html": (
             "<p><b>A LINQ query over a <code>DbSet</code> is data, not code: the compiler builds an expression tree, "
             "and EF Core translates it to SQL when you enumerate.</b> This is " + ref(4) + " put to work. "
             "<code>ToQueryString()</code> shows the SQL without running it — use it the way you used Hibernate's "
             "<code>show_sql</code>, but per query and in a test.</p>"
             "<p><b>The static type decides where the filter runs.</b> Assign <code>db.Quotes</code> to an "
             "<code>IEnumerable&lt;Quote&gt;</code> — a repository return type, a helper parameter — and the next "
             "<code>Where</code> or <code>Count</code> binds to LINQ to Objects: EF sends <code>SELECT</code> of every "
             "column of every row, tracks each entity, and filters in memory. It compiles, it passes a small test, "
             "and it is the most common EF performance bug.</p>"
             "<p><b>Related data loads only when you ask for it.</b> There is no lazy loading unless you turn it "
             "on — the Proxies package with <code>virtual</code> navigations, or <code>ILazyLoader</code> injected "
             "into the entity (" + LAZY + ") — so without <code>Include</code>, <code>quote.Lines</code> is simply "
             "empty. Loading lines quote-by-quote is the N+1; "
             "<code>Include</code> is one JOIN; <code>AsSplitQuery</code> trades one query for one per collection to "
             "avoid the cartesian explosion of several collection JOINs (" + SPLIT + ").</p>"
             "<p><b>Reads should be projections or no-tracking.</b> A <code>Select</code> into a record reads only "
             "the named columns and is never tracked; <code>AsNoTracking()</code> keeps entities but skips the "
             "snapshot. Tracked queries are for data you are about to change.</p>")},

        {"type": "mermaid", "inline": True, "toc": False,
         "heading": "3.1 · Two paths for one lambda",
         "caption": "indigo = your query · amber = EF Core work · slate = the SQL sent · green = the database does "
                    "the work · red = the work happens in your process instead",
         "code": ("flowchart LR\n"
                  '  S["db.Quotes.Count(q =><br/>q.Coverage == Class1)"]:::code\n'
                  '  S -- "typed as IQueryable" --> Q1["EF Core translates<br/>the expression tree"]:::tool\n'
                  '  Q1 --> Q2["SELECT COUNT(*)<br/>WHERE Coverage = ..."]:::art\n'
                  '  Q2 --> Q3["The database counts<br/>one integer returns"]:::db\n'
                  '  S -- "typed as IEnumerable" --> E1["SELECT every column<br/>no WHERE"]:::art\n'
                  '  E1 --> E2["Materialise and<br/>track 20 entities"]:::tool\n'
                  '  E2 --> E3["LINQ to Objects<br/>counts in memory"]:::bad\n'
                  "  classDef code fill:#c7d2fe,color:#1f2937,stroke:#6366f1;\n"
                  "  classDef art fill:#e2e8f0,color:#1f2937,stroke:#475569;\n"
                  "  classDef tool fill:#fde68a,color:#1f2937,stroke:#d97706;\n"
                  "  classDef db fill:#bbf7d0,color:#1f2937,stroke:#16a34a;\n"
                  "  classDef bad fill:#fecaca,color:#1f2937,stroke:#dc2626;\n")},

        compare(from_sample(f"{DATA}/QuoteQueries.cs", "projection"),
                from_text("\n".join(ln[2:] for ln in _section(1) if ln.startswith("  ") and "Q-00" not in ln),
                          "sql", label="SQL — ToQueryString()", file="captured from L09.QueryConsole"),
                heading="3.2 · A projection and the SQL it becomes",
                note="<b>Three things to read in the SQL.</b> The navigation <code>q.Vehicle.Make</code> became an "
                     "<code>INNER JOIN</code> — no <code>Include</code> needed inside a projection. "
                     "<code>q.Lines.Count</code> became a correlated <code>COUNT(*)</code> subquery instead of loading "
                     "lines. The enum argument is a parameter, <code>@coverage</code>, so one cached plan serves every "
                     "coverage class. Nothing selected here is tracked."),

        code(from_sample(CONSOLE, "enumerable-vs-queryable"),
             heading="3.3 · The IEnumerable trap — the same Count, two static types",
             note=f"<b>Same answer, very different work.</b> Both print <code>count {shape['IEnumerable'][0]}</code>. "
                  f"The <code>IEnumerable</code> version sent a <code>SELECT</code> of all twelve columns with no "
                  f"<code>WHERE</code> and left <b>{shape['IEnumerable'][2]}</b> entities tracked; the "
                  f"<code>IQueryable</code> version sent <code>SELECT COUNT(*) … WHERE \"q\".\"Coverage\" = "
                  f"'Class1'</code> and tracked <b>{shape['IQueryable'][2]}</b>. An <code>AsNoTracking()</code> "
                  f"list of the same {shape['AsNoTracking'][0]} quotes also tracked "
                  f"{shape['AsNoTracking'][2]} " + MEASURED + ". Repository methods that return "
                  "<code>IEnumerable</code> are fine only once the query has already been materialised."),

        {"type": "chartrow", "charts": [
            {"heading": "3.4 · Commands to load N quotes with their lines", "kind": "grouped_bar",
             "args": {"categories": [f"{n} quote" + ("" if n == "1" else "s") for n in ns],
                      "series": [("N+1 (Load per quote)", [nplus1[int(n)] for n in ns]),
                                 ("Include", [include[int(n)] for n in ns]),
                                 ("AsSplitQuery", [split[int(n)] for n in ns])],
                      "width": 390, "height": 230},
             "caption": "SQL commands recorded by the SqlCommandLog interceptor · SQLite in-memory · measured",
             "note": f"<b>N+1 grows with the data; the other two do not.</b> Loading {n_max} quotes line-by-line "
                     f"cost {nplus1[n_max]} commands; <code>Include</code> stayed at {include[n_max]} and "
                     f"<code>AsSplitQuery</code> at {split[n_max]} (one per collection level). On a cloud database "
                     "every extra command is a network round trip. " + MEASURED},
            {"heading": "3.5 · Entities tracked after each 3.3 query", "kind": "bar",
             "args": {"data": [(k, shape[k][2]) for k in ("IEnumerable", "IQueryable", "AsNoTracking")],
                      "ylabel": "tracked entities", "tone": "red", "width": 390, "height": 230},
             "caption": "ChangeTracker.Entries() after each query in 3.3 · 20 seeded quotes · measured",
             "note": "<b>Tracking is memory and CPU you pay for on every read.</b> The <code>IEnumerable</code> count "
                     "materialised and snapshotted the whole table to return one integer. " + MEASURED}]},

        code(from_sample(f"{TESTS}/QueryShapeTests.cs", "command-counts"), keep=False,
             heading="3.6 · The N+1 as a failing test, not a code-review opinion",
             note="<b>Assert on the command count.</b> The theory proves the cost grows as <code>n + 1</code>; the "
                  "second test proves <code>Include</code> loads the same graph in one command. A later change that "
                  "drops the <code>Include</code> fails a test instead of a dashboard. The interceptor that counts is "
                  "shown in 7.2."),

        {"type": "table", "heading": "3.7 · Five ways to load a quote's premium lines",
         "cols": ["Approach", "JPA / Hibernate habit", f"Commands for {n_max} quotes", "Use it when"],
         "rows": [
             ["<b>Nothing</b> — no <code>Include</code>", "Lazy collection proxy",
              "1 · <code>Lines</code> stays empty " + pill("trap", "red"),
              "Never, if you read <code>Lines</code> — EF raises no error"],
             ["<code>Entry(q).Collection(…).LoadAsync()</code> in a loop", "Touching a lazy collection per row",
              f"{nplus1[n_max]} " + pill("measured", "indigo"), "One quote at a time, never in a loop"],
             ["<code>Include(q =&gt; q.Lines)</code>", "<code>JOIN FETCH</code> · <code>@EntityGraph</code>",
              f"{include[n_max]} " + pill("measured", "indigo"), "One collection level; the default choice"],
             ["<code>Include(…).AsSplitQuery()</code>", "Hibernate <code>@Fetch(SUBSELECT)</code>",
              f"{split[n_max]} " + pill("measured", "indigo"),
              "Several sibling collections; add a unique <code>OrderBy</code> with paging on EF Core 9 or older"],
             ["<code>Select</code> into a record", "DTO projection with <code>select new</code>",
              "1 · counts as subqueries", "Read-only screens, APIs and reports — no tracking at all"]]},

        code(from_sample(f"{DATA}/QuoteQueries.cs", "from-sql"),
             heading="3.8 · Raw SQL that stays parameterised",
             note="<b>The <code>$</code> is not string interpolation here.</b> <code>FromSql</code> takes a "
                  "<code>FormattableString</code> and sends <code>{make}</code> as a <code>DbParameter</code> "
                  "(" + SQLQ + "). Fed <code>Toyota' OR '1'='1</code>, the console captured "
                  "<code>SELECT * FROM Vehicles WHERE Make = @p0</code> and returned 0 rows. "
                  "<code>FromSqlRaw</code> with concatenation is the injectable variant; EF Core 10 ships an analyzer "
                  "warning for it (" + EF10 + ")."),

        # ═══════════════════════════ 4 · SAVING ═══════════════════════════
        {"type": "story", "heading": "4 · Saving — unit of work, transactions and optimistic concurrency",
         "html": (
             "<p><b><code>SaveChanges</code> is flush and commit in one call.</b> The change tracker compares each "
             "tracked entity with the snapshot taken when it was loaded, then sends every INSERT, UPDATE and DELETE "
             "inside one transaction. Accepting a quote — update the quote, insert the policy — is one "
             "<code>SaveChangesAsync</code>, and either both rows change or neither does. There is no "
             "<code>@Transactional</code>: several <code>SaveChanges</code> or <code>ExecuteUpdate</code> calls that "
             "must succeed together need an explicit <code>BeginTransactionAsync</code> (4.6).</p>"
             "<p><b>EF Core never flushes for you.</b> Hibernate flushes pending changes before a query so the query "
             "sees them; EF Core sends the query as-is. A tracked quote you changed but did not save is invisible to a "
             "<code>WHERE</code> clause — yet querying its row again hands back the same tracked instance with the "
             "unsaved value. Test 4.5 pins both behaviours down.</p>"
             "<p><b>Optimistic concurrency is a <code>WHERE</code> clause and a row count.</b> Mark a property as a "
             "concurrency token and EF adds <code>AND Version = @original</code> to UPDATE and DELETE; zero rows "
             "affected becomes <code>DbUpdateConcurrencyException</code> — Hibernate's "
             "<code>OptimisticLockException</code>. The token has to change on every write: SQL Server's "
             "<code>rowversion</code> and PostgreSQL's <code>xmin</code> (mapped by Npgsql, " + NPGSQL_TOKEN + ") do "
             "that in the database, but SQLite has no database-generated token "
             "(" + CONCURRENCY + "), so the sample stamps a new <code>Guid</code> inside "
             "<code>SaveChanges</code>.</p>")},

        {"type": "mermaid", "inline": True,
         "heading": "4.1 · Entity states in the change tracker",
         "caption": "indigo = not tracked · slate = in sync with the database · amber = a pending write that "
                    "SaveChanges will send",
         "code": ("stateDiagram-v2\n"
                  "  direction LR\n"
                  "  [*] --> Detached\n"
                  "  Detached --> Unchanged: query or Attach\n"
                  "  Detached --> Added: Add\n"
                  "  Unchanged --> Modified: set a property\n"
                  "  Unchanged --> Deleted: Remove\n"
                  "  Added --> Unchanged: SaveChanges INSERT\n"
                  "  Modified --> Unchanged: SaveChanges UPDATE\n"
                  "  Deleted --> Detached: SaveChanges DELETE\n"
                  "  Unchanged --> Detached: context disposed\n"
                  "  classDef idle fill:#c7d2fe,color:#1f2937,stroke:#6366f1\n"
                  "  classDef sync fill:#e2e8f0,color:#1f2937,stroke:#475569\n"
                  "  classDef pending fill:#fde68a,color:#1f2937,stroke:#d97706\n"
                  "  class Detached idle\n"
                  "  class Unchanged sync\n"
                  "  class Added, Modified, Deleted pending\n")},

        code(from_sample(f"{DATA}/QuoteWorkflow.cs", "unit-of-work"),
             heading="4.2 · Accepting a quote — two statements, one SaveChanges, one transaction",
             note="<b>No repository <code>save(quote)</code> call.</b> Changing <code>quote.Status</code> on a tracked "
                  "entity is enough for an UPDATE; <code>Policies.Add</code> queues the INSERT. The test "
                  "<code>Accepting_a_quote_writes_the_update_and_the_insert_together</code> reads both back through a "
                  "fresh context."),

        code(from_sample(f"{DATA}/MotorQuoteDbContext.Versioning.cs", "stamp-version"), keep=False,
             heading="4.3 · An application-managed concurrency token for a database without rowversion",
             note="<b>The original value is still what the UPDATE filters on.</b> EF captured <code>Version</code> when "
                  "the quote was read; replacing it just before saving writes the new value while the "
                  "<code>WHERE</code> clause keeps the old one. On SQL Server you would map a "
                  "<code>byte[]</code> with <code>IsRowVersion()</code> instead (on PostgreSQL a <code>uint</code> "
                  "for <code>xmin</code>) and delete this file. "
                  "<code>ExecuteUpdate</code> bypasses this override — which is why 6.2 rotates the token itself."),

        {"type": "mermaid", "inline": True,
         "heading": "4.4 · An underwriter and a broker edit the same quote",
         "caption": "two DbContext instances, one row · the second UPDATE matches zero rows because its WHERE still "
                    "carries the version it read · asserted by the test The_second_writer_gets_a_concurrency_exception",
         "code": ('%%{init: {"theme":"base","themeVariables": {"actorBkg":"#E0E7FF","actorBorder":"#6366F1",'
                  '"actorTextColor":"#1f2937","noteBkgColor":"#FEF3C7","noteBorderColor":"#D97706",'
                  '"noteTextColor":"#1f2937","signalColor":"#334155","signalTextColor":"#1f2937",'
                  '"sequenceNumberColor":"#ffffff"}}}%%\n'
                  "sequenceDiagram\n"
                  "  autonumber\n"
                  "  participant U as Underwriter context\n"
                  "  participant D as Quotes table\n"
                  "  participant B as Broker context\n"
                  "  U->>D: SELECT Q-0001 (Version v1)\n"
                  "  B->>D: SELECT Q-0001 (Version v1)\n"
                  "  U->>D: UPDATE Status Accepted, Version v2 WHERE Version = v1\n"
                  "  D-->>U: 1 row affected, commit\n"
                  "  B->>D: UPDATE Status Declined, Version v3 WHERE Version = v1\n"
                  "  D-->>B: 0 rows affected\n"
                  "  Note over B: DbUpdateConcurrencyException<br/>reload, merge or ask the user\n")},

        code(from_sample(f"{TESTS}/SavingTests.cs", "no-auto-flush"),
             heading="4.5 · No flush before a query — and identity resolution still applies",
             note="<b>Two Hibernate instincts, tested.</b> The count reads the database, where Q-0001 is still "
                  "<code>Quoted</code>, so it returns 0. Re-reading the row by id returns the <i>same</i> tracked "
                  "object with the unsaved <code>Declined</code> — the identity map you know from the persistence "
                  "context. Save before you query when the query must see your change."),

        code(from_sample(f"{DATA}/QuoteWorkflow.cs", "explicit-transaction"), keep=False,
             heading="4.6 · One explicit transaction — ExecuteUpdate and SaveChanges commit or roll back together",
             note="<b>This is the <code>@Transactional</code> you were looking for — in a few lines of code.</b> "
                  "<code>ExecuteUpdate</code> commits at once when it runs alone; inside the transaction it waits for "
                  "<code>CommitAsync</code>, and <code>SaveChanges</code> joins the transaction instead of starting "
                  "its own. Two tests pin it: <code>One_transaction_covers_ExecuteUpdate_and_SaveChanges</code> and "
                  "<code>A_failed_SaveChanges_rolls_back_the_ExecuteUpdate_too</code>, where a duplicate policy number "
                  "makes the INSERT fail and the rivals stay <code>Quoted</code>. Dapper joins the same transaction "
                  "through <code>db.Database.GetDbConnection()</code> and <code>tx.GetDbTransaction()</code> "
                  "(<code>Dapper_joins_the_transaction_of_an_EF_Core_context</code>). <b>One production trap:</b> with a "
                  "retrying execution strategy — SQL Server's <code>EnableRetryOnFailure</code>, for example — a "
                  "user-started transaction throws until the whole unit runs inside "
                  "<code>db.Database.CreateExecutionStrategy().ExecuteAsync(…)</code> so it can be replayed "
                  "(" + CONNRES + "). Not run here: SQLite has no retrying strategy."),

        figure_heading("4.7 · Persistence-context habits — what carries over from Hibernate, what to drop"),
        {"type": "twocol", "boxes": [
            {"heading": "Carries over", "tone": "teal",
             "items": ["Unit of work: load, change, write once — <code>SaveChanges</code> is flush plus commit",
                       "Identity map: one tracked instance per row per context (4.5)",
                       "Optimistic locking with a version column and a conflict exception (4.4)",
                       "Fetch plans chosen per use case — <code>Include</code> or a projection — not per entity",
                       "Short transactions that never span user think-time"]},
            {"heading": "Drop or change", "tone": "rose",
             "items": ["Lazy loading as the default — navigations stay empty until included",
                       "Flush-before-query — save first when a query must see the change",
                       "<code>@Version</code> incrementing itself — stamp the token yourself, or map a database-generated one "
                       "(<code>rowversion</code>, PostgreSQL <code>xmin</code>)",
                       "Open Session in View — there is no <code>LazyInitializationException</code> to rescue; one "
                       "context per request, never shared across threads",
                       "Annotations as the mapping — configuration classes with the Fluent API"]}]},

        # ═══════════════════════════ 5 · MIGRATIONS ═══════════════════════════
        {"type": "story", "heading": "5 · Migrations — dotnet ef instead of Flyway and Liquibase",
         "html": (
             "<p><b>Flyway runs SQL you wrote; EF Core writes the migration for you from a model diff — the idea behind "
             "TypeORM's <code>migration:generate</code>, except that EF diffs against a committed snapshot.</b> "
             "<code>dotnet ef migrations add</code> compares the current model with the committed "
             "<code>ModelSnapshot</code> and generates C# <code>Up</code> and <code>Down</code> methods. You review "
             "that C# in the pull request like any other code; SQL is produced from it for each provider. The three "
             "files per migration — migration, designer, updated snapshot — are all committed.</p>"
             "<p><b>The tool is a pinned local tool, and a class library needs a design-time factory.</b> "
             "<code>dotnet-ef</code> is restored from <code>dotnet-tools.json</code>, like a Gradle plugin version in "
             "the build. The tool builds your project and must create the context at design time; a library with no "
             "host provides an <code>IDesignTimeDbContextFactory</code> (" + EFCLI + "). The "
             "<code>Microsoft.EntityFrameworkCore.Design</code> package is marked <code>PrivateAssets=all</code> so it "
             "never ships.</p>"
             "<p><b>Two EF Core 9 changes make runtime migration safer and stricter.</b> <code>Migrate()</code> now "
             "takes a database-wide lock, and it throws when the model has changes no migration covers "
             "(" + EF9BREAK + "). Detect that earlier with <code>dotnet ef migrations "
             "has-pending-model-changes</code> in CI, or with a test like "
             "<code>Committed_migration_matches_the_model</code>, which asserts "
             "<code>Database.HasPendingModelChanges()</code> is false.</p>"
             "<p><b>For deployment, Microsoft recommends a migration bundle for automation and a SQL script when a "
             "person must review the SQL</b> (" + APPLYING + "). A bundle is a single-file executable built in CI "
             "and run as a one-shot job with schema-change credentials, while the application itself runs with "
             "least privilege — the same split you would make with a Flyway container before an ECS deploy.</p>")},

        code(from_sample(MIGRATION, "create-quotes"), keep=False,
             heading="5.1 · A generated migration — what you review in the pull request",
             note=f"<b>Read it as you would read a Flyway script — it is the contract with production.</b> The "
                  f"{migration_lines} lines above were generated, not typed: <code>maxLength</code>, "
                  "<code>precision</code> and the <code>Restrict</code> foreign key all come from 2.2, and the "
                  "complex-type columns are flattened with their prefixes. A rename in the model can appear as a drop "
                  "and an add; fixing that by hand in the generated C# is normal."),

        {"type": "table", "heading": "5.2 · Four ways to apply migrations, next to the Flyway habit",
         "cols": ["Strategy", "Flyway / Liquibase equivalent", "SQL reviewable", "SDK at deploy", "Use for"],
         "rows": [
             [cmd("dotnet ef migrations script"), "SQL handed to a DBA · Liquibase " + cmd("update-sql"), pill("yes", "green"), pill("no", "green"),
              "DBA-controlled or review-gated releases; add <code>--idempotent</code> where the provider supports it"],
             [cmd("dotnet ef migrations bundle"), "Flyway CLI in a one-shot container job", pill("no", "amber"),
              pill("no", "green"), "Automated pipelines — Microsoft's recommendation for automation"],
             [cmd("dotnet ef database update"), cmd("flyway migrate") + " from a laptop", pill("no", "amber"),
              pill("yes", "red"), "Local development and test databases only"],
             ["<code>Database.MigrateAsync()</code> at start-up", "<code>spring.flyway.enabled=true</code>",
              pill("no", "amber"), pill("no", "green"),
              "Simple deployments that accept start-up migration — the EF Core 9 lock makes several replicas safe, but the "
              "app then needs schema-change rights"]]},
        {"type": "html", "html": '<div class="fign" style="margin:-4px 0 10px">Pill colour: green = what you want in '
                                 'production · amber = a cost to weigh · red = avoid in production.</div>'},
        code(from_text(f"""
            $ dotnet ef migrations has-pending-model-changes
            No changes have been made to the model since the last migration.

            $ dotnet ef migrations script --idempotent
            Generating idempotent scripts for migrations is not currently supported for SQLite.

            $ dotnet ef migrations bundle -o efbundle.exe
            Building bundle...
            Done. Migrations Bundle: ...\\efbundle.exe

            $ ./efbundle.exe --connection "Data Source=mq.db"
            Acquiring an exclusive lock for migration application. ...
            Applying migration '20260914121532_InitialCreate'.
            Done.

            $ ./efbundle.exe --connection "Data Source=mq.db"
            Acquiring an exclusive lock for migration application. ...
            No migrations were applied. The database is already up to date.
            Done.
            """, "text", label="Terminal — dotnet ef in L09.Data",
                       file="captured · Build started/succeeded lines and long URLs left out"),
             heading="5.3 · The CI gate, a SQL script that SQLite cannot make idempotent, and a bundle run twice",
             note=f"<b>The bundle is idempotent even where the script is not.</b> It records applied migrations in "
                  f"<code>__EFMigrationsHistory</code>, takes the EF Core 9 migration lock, and does nothing on the "
                  f"second run. SQLite cannot generate an idempotent script because it has no procedural SQL "
                  f"(" + SQLITE_LIMITS + "); the SQL Server provider can. The framework-dependent bundle built here was "
                  f"{BUNDLE_BYTES / 1_048_576:.1f} MB " + MEASURED + "."),


        {"type": "mermaid", "inline": True, "toc": False,
         "heading": "5.4 · From a model change to production",
         "caption": "indigo = developer · amber = automated check · slate = deployment artefact · green = runs "
                    "against production · the app never holds schema-change credentials",
         "code": ("flowchart LR\n"
                  '  subgraph DEV["Developer"]\n'
                  '    M["Change model,<br/>migrations add"]:::dev --> R["Review Up and<br/>Down in the PR"]:::dev\n'
                  "  end\n"
                  '  subgraph CI["CI pipeline"]\n'
                  '    G["Model check<br/>and tests"]:::ci\n'
                  '    S["Script<br/>(SQL file)"]:::art\n'
                  '    B["Bundle<br/>(efbundle)"]:::art\n'
                  "  end\n"
                  '  subgraph PROD["Release"]\n'
                  '    DBA["DBA applies<br/>the script"]:::prod\n'
                  '    JOB["One-shot job<br/>runs the bundle"]:::prod\n'
                  '    APP["Deploy the app<br/>(no schema rights)"]:::prod\n'
                  "  end\n"
                  "  R --> G\n"
                  "  G --> S\n"
                  "  G --> B\n"
                  "  S --> DBA\n"
                  "  B --> JOB\n"
                  "  DBA --> APP\n"
                  "  JOB --> APP\n"
                  "  classDef dev fill:#c7d2fe,color:#1f2937,stroke:#6366f1;\n"
                  "  classDef ci fill:#fde68a,color:#1f2937,stroke:#d97706;\n"
                  "  classDef art fill:#e2e8f0,color:#1f2937,stroke:#475569;\n"
                  "  classDef prod fill:#bbf7d0,color:#1f2937,stroke:#16a34a;\n")},

        # ═══════════════════════════ 6 · BEYOND EF ═══════════════════════════
        {"type": "story", "heading": "6 · Beyond tracked entities — Dapper, bulk statements, providers and DynamoDB",
         "html": (
             "<p><b>Dapper is what you reach for when the SQL is the design.</b> A reporting query with "
             "<code>COUNT(DISTINCT …)</code>, a <code>LEFT JOIN</code> and a <code>GROUP BY</code> — the kind of "
             "query you kept by the hundred behind BI dashboards — reads best as SQL. Dapper (" + DAPPER + ") adds "
             "extension methods to any <code>DbConnection</code>, binds parameters from an anonymous object and maps "
             "columns to properties by name: Spring's <code>JdbcClient</code> without the template. It can share the "
             "connection, and the transaction, of an EF Core context (4.6).</p>"
             "<p><b><code>ExecuteUpdate</code> and <code>ExecuteDelete</code> are set-based writes inside EF.</b> They "
             "translate a LINQ filter into one UPDATE or DELETE, load nothing, and ignore the change tracker — so "
             "tracked instances go stale, no concurrency token is checked, no transaction is started for you, and "
             "they work only on relational providers (" + EXECUPD + "). Expiring stale quotes is their textbook "
             "case.</p>"
             "<p><b>Providers do not cross EF Core major versions, so the provider can pin your upgrade.</b> "
             "For Aurora PostgreSQL, Npgsql shipped EF Core 10 support in November 2025 (" + NPGSQL + "). For "
             "Aurora MySQL, Oracle's <code>MySql.EntityFrameworkCore</code> has a 10.0 line (" + MYSQL + "), while the "
             "long-popular Pomelo provider's latest stable release still targets EF Core 9 (" + POMELO + "). "
             "Check both before choosing a .NET version for a MySQL estate.</p>"
             "<p><b>DynamoDB has no EF Core provider.</b> Use the AWS SDK for .NET directly: its "
             "<code>DynamoDBContext</code> maps attributed classes to items and supports optimistic locking, but it "
             "has no table-management API and nothing like LINQ-to-SQL (" + DYNAMO + "). Your DynamoDB access "
             "patterns and key design transfer unchanged; the ORM expectations do not.</p>")},

        compare(from_text('''
            public List<CoverageRow> byCoverage(String status) {
                var sql = """
                    SELECT q.coverage, COUNT(DISTINCT q.id) AS quotes,
                           COUNT(l.id) AS lines
                    FROM quotes q
                    LEFT JOIN premium_lines l ON l.quote_id = q.id
                    WHERE q.status = :status
                    GROUP BY q.coverage
                    ORDER BY q.coverage
                    """;
                return jdbcClient.sql(sql)
                    .param("status", status)
                    .query(CoverageRow.class)
                    .list();
            }
            ''', "java", file="Spring JdbcClient"),
                from_sample(f"{DATA}/CoverageReport.cs", "dapper"),
                heading="6.1 · A reporting query — Spring JdbcClient vs Dapper",
                note=f"<b>Almost a transliteration.</b> <code>@status</code> is bound from the anonymous object "
                     f"<code>new {{ status }}</code>; rows map to the <code>CoverageRow</code> record by column name, "
                     f"as <code>query(CoverageRow.class)</code> does. The console ran this and the equivalent EF Core "
                     f"<code>GroupBy</code> on the same data and printed identical counts, and a test asserts that they "
                     f"agree. Note the order both printed — <code>Class3</code> before <code>Class3Plus</code> — "
                     f"because <code>Coverage</code> is stored as a string."),

        compare(from_sample(CONSOLE, "expire-tracked"), from_sample(f"{DATA}/QuoteQueries.cs", "bulk-expire"),
                heading="6.2 · Expiring stale quotes — tracked SaveChanges vs one ExecuteUpdate",
                note=f"<b>Same {tracked_rows} rows changed; {tracked_cmds} commands against {bulk_cmds}.</b> The tracked "
                     f"version loads every stale quote, then sends one UPDATE per row on SQLite; SQL Server would "
                     f"batch those statements into fewer round trips (" + BATCHING + "), but still loads and tracks "
                     "the rows. The <code>ExecuteUpdate</code> version is a single <code>UPDATE … WHERE Status = "
                     "'Quoted' AND ValidUntil &lt; @today</code>. Because it bypasses <code>SaveChanges</code>, it "
                     "rotates <code>Version</code> itself so concurrent editors still get their conflict."),

        {"type": "table", "heading": "6.3 · Providers you will meet — and whether they support EF Core 10",
         "cols": ["Database", "Package · maintainer", "EF Core 10", "Watch for"],
         "rows": [
             ["SQL Server · Azure SQL", "<code>Microsoft.EntityFrameworkCore.SqlServer</code> · Microsoft",
              pill("yes", "green"), "<code>rowversion</code> tokens; EF Core 10 adds the SQL Server 2025 "
                                    "<code>vector</code> and <code>json</code> types"],
             ["PostgreSQL · Aurora PostgreSQL", "<code>Npgsql.EntityFrameworkCore.PostgreSQL</code> · Npgsql team",
              pill("10.0.3", "green"), "<code>xmin</code> works as a concurrency token. " + PROVIDERS + " still lists 8 and 9 — NuGet has the "
              "10.0 line"],
             ["MySQL · Aurora MySQL", "<code>MySql.EntityFrameworkCore</code> · Oracle", pill("10.0.9", "green"),
              "Pomelo (<code>Pomelo.EntityFrameworkCore.MySql</code>): latest stable 9.0.0, EF Core 9 only"],
             ["Oracle Database", "<code>Oracle.EntityFrameworkCore</code> · Oracle", pill("yes", "green"),
              "Listed for EF Core 8, 9 and 10"],
             ["SQLite", "<code>Microsoft.EntityFrameworkCore.Sqlite</code> · Microsoft", pill("yes", "green"),
              "No schemas, sequences or database-generated tokens; <code>decimal</code> stored as TEXT"],
             ["Amazon DynamoDB", "none — AWS SDK for .NET <code>DynamoDBContext</code>", pill("no provider", "slate"),
              "Model access patterns and keys, not a relational schema"],
             ["EF Core InMemory", "<code>Microsoft.EntityFrameworkCore.InMemory</code> · Microsoft",
              pill("yes", "amber"), "Not a database: no transactions, no raw SQL, no <code>ExecuteUpdate</code>"]]},

        {"type": "chartrow", "charts": [
            {"heading": "6.4 · Commands to expire the stale quotes", "kind": "bar",
             "args": {"data": [("SaveChanges (tracked)", tracked_cmds), ("ExecuteUpdate", bulk_cmds)],
                      "ylabel": "SQL commands", "tone": "amber", "width": 390, "height": 230},
             "caption": f"{tracked_rows} of 20 seeded quotes expired · SQLite in-memory · measured",
             "note": "<b>The tracked path scales with the number of rows; the bulk path does not.</b> On SQLite that "
                     "is one SELECT plus one UPDATE per row. " + MEASURED},
            {"heading": "6.5 · Which tool gives you what", "kind": "heatmap",
             "args": {"rows": ["EF tracked", "EF no-tracking", "ExecuteUpdate", "Dapper", "DynamoDBContext"],
                      "cols": ["Typed", "Tracking", "Locking", "Raw SQL", "Schema"],
                      "matrix": [[2, 2, 2, 1, 2], [2, 0, 0, 1, 2], [2, 0, 1, 1, 2], [1, 0, 1, 2, 0],
                                 [1, 0, 2, 0, 0]],
                      "cell": 44, "width": 390, "tone": "teal",
                      "fmt": lambda v: {2: "yes", 1: "manual", 0: "—"}[int(v)]},
             "caption": "yes = built in · manual = you write or wire it · — = not offered · a rubric, not a benchmark",
             "note": "<b>No row is all green, so a service usually mixes them.</b> Tracked entities for the quote "
                     "workflow, projections for reads, <code>ExecuteUpdate</code> for housekeeping, Dapper for "
                     "reports. Each column is a capability, not a goal — a dash under Tracking is what a read path "
                     "wants. Typed = compiler-checked queries; Tracking = change tracking and <code>SaveChanges</code>; "
                     "Locking = optimistic concurrency (DynamoDBContext's version attribute); Raw SQL = hand-written "
                     "SQL is a supported way to use the tool; Schema = managed migrations. " + ESTIMATE}]},

        # ═══════════════════════════ 7 · TESTING ═══════════════════════════
        {"type": "story", "heading": "7 · Testing data access — choose the fake that lies least",
         "html": (
             "<p><b>Microsoft's own order of preference surprises most JVM engineers: test against your production "
             "database engine first.</b> The EF Core team recommends real-database tests (containers make that "
             "cheap), then stubbing a repository layer, then SQLite in-memory — and calls the EF Core InMemory "
             "provider <i>highly discouraged</i> as a test double (" + TESTING + "). "
             "Testcontainers for .NET (" + TESTCONTAINERS + ") is the Testcontainers you know; " + ref(10) + " covers "
             "it with the rest of the test tooling.</p>"
             "<p><b>The InMemory provider is a dictionary, not a database.</b> It ignores transactions, cannot run raw "
             "SQL, and does not support <code>ExecuteUpdate</code>. The 7.3 test proves the "
             "last point: code that is correct on every relational provider throws there.</p>"
             "<p><b>SQLite in-memory is the H2 of this lesson — relational, fast, and still not your production "
             "engine.</b> The connection <i>is</i> the database, so the fixture keeps one open for the test's "
             "lifetime and applies the committed migration. Differences remain: string comparison is "
             "case-sensitive where SQL Server is not, and <code>decimal</code> is TEXT (7.4). Use it for query shape "
             "and command counts; run the provider-specific behaviour against the real engine.</p>")},

        code(from_sample(f"{DATA}/SqliteDb.cs", "sqlite-in-memory"),
             heading="7.1 · The fixture — one open connection is one private database",
             note="<b>Close the connection and the database is gone</b>, which is exactly the per-test isolation you "
                  "want. <code>Migrate()</code> rather than <code>EnsureCreated()</code> means the schema under test "
                  "is the one 5.1 generates; <code>AddInterceptors(Log)</code> wires in the command counter."),

        code(from_sample(f"{DATA}/SqlCommandLog.cs", "interceptor"), keep=False,
             heading="7.2 · Counting commands with a DbCommandInterceptor",
             note="<b>An interceptor sees every <code>DbCommand</code> EF Core executes</b> — the same hook you would "
                  "put a Hibernate <code>StatementInspector</code> or a datasource proxy on. Override both the sync "
                  "and async variants, or a test that awaits will count nothing."),

        code(from_sample(f"{TESTS}/ProviderTrapTests.cs", "in-memory-trap"),
             heading="7.3 · The InMemory provider trap, pinned by a test",
             note="<b>Green on SQLite in this suite, an exception on InMemory</b> " + MEASURED + ". The message names "
                  "<code>ExecuteUpdate</code> because the provider cannot translate it — it is supported on "
                  "relational providers only (" + EXECUPD + "). A suite built on InMemory would have had to skip the one method that matters "
                  "most for bulk housekeeping."),

        code(from_sample(CONSOLE, "raw-text-order"),
             heading="7.4 · SQLite stores decimal as TEXT — raw SQL sorts it as text",
             note=f"<b>EF Core hides the difference; raw SQL does not.</b> EF Core translated "
                  f"<code>OrderByDescending(q =&gt; q.Total.Amount)</code> to <code>ORDER BY … COLLATE EF_DECIMAL "
                  f"DESC</code> and returned the three largest premiums ({raw7['ef']}). The raw SQL on the same TEXT "
                  f"column returned {raw7['top']} — <code>'9'</code> sorts after <code>'2'</code> as text — and "
                  f"<code>CAST(Total_Amount AS REAL)</code> restored numeric order, smallest first: {raw7['cast']} "
                  + MEASURED + ". The <code>CAST</code> is a workaround for this fixture only: on SQL Server and "
                  "PostgreSQL <code>decimal</code> is a native numeric type and the trap does not exist. "
                  + SQLITE_LIMITS + f" still says such comparisons run on the client; the SQL captured from EF Core "
                  f"{ef_version} shows them translated."),

        {"type": "chart", "toc": False, "heading": "7.5 · Test cases by class", "kind": "hbar",
         "args": {"data": sorted(cases.items(), key=lambda kv: -kv[1]), "labelw": 140, "tone": "indigo",
                  "width": 560},
         "caption": "[Fact] methods + [InlineData] rows in L09.Data.Tests · counted at build · measured",
         "note": f"<b>{n_tests} cases, and most assert a number of SQL commands or a translation — not just a "
                 "result.</b> That is what makes a data-access test catch an N+1 or an IEnumerable leak. "
                 + MEASURED},

        kept_table(
            "7.6 · What the application may still do — for each kind of test double",
            ["Test double", "Raw SQL", "Transactions", "Provider functions", "Exact query behaviour",
             "LINQ anywhere", "Verdict"],
            [["InMemory provider", pill("no", "red"), pill("no · ignored", "red"), pill("no", "red"),
              pill("depends", "amber"), pill("yes", "green"), "Highly discouraged by the EF Core team"],
             ["SQLite in-memory", pill("depends", "amber"), pill("yes", "green"), pill("no", "red"),
              pill("depends", "amber"), pill("yes", "green"),
              "Query shape, command counts, migrations — this lesson's fixture"],
             ["Stubbed repository", pill("yes", "green"), pill("yes", "green"), pill("yes", "green"),
              pill("yes", "green"), pill("no *", "amber"),
              "Unit tests above the data layer — the LINQ inside the repository is not tested"],
             ["Real engine (container)", pill("yes", "green"), pill("yes", "green"), pill("yes", "green"),
              pill("yes", "green"), pill("yes", "green"), "Microsoft's first recommendation — needs Docker in CI"]],
            note=("<b>How to read it.</b> A “yes” means the application may use that feature and the test still "
                  "works, not that the double verifies it: a stubbed repository replaces the LINQ, so nothing "
                  "translates it. <b>* The price of the repository:</b> every testable query must sit behind an "
                  "<code>IEnumerable</code>-returning method, and tests against the real database are still needed "
                  "for those queries. Rows and values follow Microsoft's overall comparison (" + TESTING + ").")),

        # ═══════════════════════════ 8 · VISUAL BASIC ═══════════════════════════
        {"type": "story", "heading": "8 · Visual Basic alongside — the runtime is shared, the tooling is not",
         "html": (
             "<p><b>EF Core's runtime does not care which language built the expression tree.</b> VB's query syntax "
             "compiles to the same <code>IQueryable</code> calls as C#, so a VB report can query the C# "
             "<code>MotorQuoteDbContext</code> directly — and VB's <code>Group By … Into</code> becomes "
             "<code>GROUP BY</code> in SQL. VB even compiles string <code>=</code> to a call to "
             "<code>Operators.CompareString</code>, and EF Core still translates it to a plain SQL <code>=</code>, "
             "as the captured output shows.</p>"
             "<p><b>The design-time tools generate C# only.</b> A VB project can declare a <code>DbContext</code> "
             "and run it, but <code>dotnet ef migrations add</code> and <code>dotnet ef dbcontext scaffold</code> "
             "both refuse a VB project (8.3). The community package that added VB generators stops at EF Core 8 "
             "(" + VBPKG + "). The tool's own advice is the architecture to use: keep the model and migrations in a "
             "C# library and reference it from VB — the migration path " + ref(6) + " recommends anyway.</p>"
             "<p><b>Estates on .NET Framework usually run EF6, not EF Core.</b> EF6 is stable and supported but no "
             "longer actively developed, and EF Core is not a drop-in replacement: EDMX models, Entity SQL and the "
             "designer have no EF Core equivalent (" + EF6 + "). Keep EF6 where the data code is stable; port the "
             "parts that must evolve (" + ref(12) + ").</p>")},

        compare(from_sample(CONSOLE, "cs-group"), from_sample(VB_REPORT, "vb-query"),
                heading="8.1 · One grouping query — C# method syntax vs VB query syntax",
                note="<b>Same SQL from both.</b> VB's <code>Group By q.Coverage Into Quotes = Count()</code> names the "
                     "aggregate inline, where C# needs a <code>Select</code> into an anonymous type. The VB query runs "
                     "when <code>For Each</code> enumerates it — deferred execution is identical. Both printed the "
                     "same four rows."),

        compare(from_sample(VB_REPORT, "vb-strings"),
                from_text("\n".join(ln for ln in VB_OUT.strip().splitlines()[5:] if not ln.startswith(" ")), "sql",
                          label="SQL — ToQueryString() from VB",
                          file="captured from L09.VbReport"),
                heading="8.2 · What EF Core receives from VB — and the SQL it sends",
                note="<b>The VB-specific call disappears in translation.</b> The first statement is the 8.1 query; the "
                     "second is the <code>Make = \"Toyota\"</code> filter, sent as <code>WHERE \"v\".\"Make\" = "
                     "'Toyota'</code> even though VB compiled the comparison to <code>CompareString</code>. Case rules "
                     "are the database's: case-sensitive on SQLite, case-insensitive under SQL Server's default "
                     "collation (" + TESTING + ")."),

        code(from_text("""
            $ cd L09.VbModel
            $ dotnet ef migrations add Initial
            The project language 'VB' isn't supported by the built-in
            IMigrationsCodeGenerator service. You can try looking for an additional
            NuGet package which supports this language; moving your DbContext type
            to a C# class library referenced by this project; or manually implementing
            and registering the design-time service for the programming language.
            # exit code 1

            $ dotnet ef dbcontext scaffold "Data Source=mq.db" Microsoft.EntityFrameworkCore.Sqlite
            The project language 'VB' isn't supported by the built-in
            IModelCodeGenerator service. ...
            # exit code 1
            """, "text", label="Terminal — dotnet ef in a VB project",
                       file="captured · long lines wrapped · build lines left out"),
             heading="8.3 · The EF Core tools refuse a VB project",
             note="<b>The context in <code>L09.VbModel</code> compiles and would run</b> — only the code generators "
                  "are missing. Both commands build the project first, then fail when they look for a VB code "
                  "generator. For a VB estate this settles where new schema work lives: a C# data library."),

        # ═══════════════════════════ 9 · HANDS-ON ═══════════════════════════
        {"type": "story", "heading": "9 · Hands-on — run the lesson-09 samples",
         "html": (
             "<p><b>Five projects, one data library.</b> <code>L09.Data</code> holds the context, configuration, "
             "committed migration, queries, the Dapper report and the SQLite fixture. The console prints the SQL "
             "behind each trap in this lesson; the tests turn the same traps into assertions; the two VB projects show "
             "what VB can and cannot do with EF Core.</p>"
             "<p><b>Read the console output against the sections.</b> Block 2 is chart 3.4, block 3 is 3.3, block 5 "
             "is 6.2, block 6 is 6.1 — and block 7 is 7.4, the decimal-as-TEXT trap.</p>")},

        code(from_text(f"""
            # from the repository root
            cd lesson-09-data-access-efcore/samples
            dotnet tool restore                      # dotnet-ef {tool_version} from dotnet-tools.json

            dotnet run --project L09.QueryConsole    # SQL for every trap in this lesson
            dotnet run --project L09.VbReport        # the C# context queried from VB
            dotnet test L09.Data.Tests               # {n_tests} cases on SQLite in-memory

            # migrations, from the data library
            cd L09.Data
            dotnet ef migrations has-pending-model-changes
            dotnet ef migrations script -o ../../../.build/l09/migrate.sql
            dotnet ef migrations bundle -o ../../../.build/l09/efbundle.exe

            # or, from the repository root: build, test and run every lesson-09 sample
            python 0-script/verify_samples.py --only 9
            """, "shell"),
             heading="9.1 · Commands",
             note="<b><code>dotnet tool restore</code> is the step people miss.</b> Without it <code>dotnet ef</code> "
                  "is not found, because the tool is pinned locally rather than installed globally. The script and "
                  "bundle outputs go to the git-ignored <code>.build</code> folder."),

        code(from_text("\n".join(["EF Core 10.0.12 on SQLite in-memory; illustrative rates", ""]
                                 + ["== 2. Commands to load N quotes with their premium lines"] + _section(2)
                                 + ["", "== 5. Expire stale quotes: tracked SaveChanges vs ExecuteUpdate"]
                                 + _section(5)[:2]
                                 + ["", "== 7. decimal is stored as TEXT on SQLite"]
                                 + [ln for ln in _section(7) if ln.startswith(("  EF Core", "  raw SQL"))]),
                       "text", label="Output — L09.QueryConsole (excerpt)", file="captured on the build machine"),
             heading="9.2 · What you should see",
             note="<b>Every number here is deterministic.</b> The seed data is fixed and SQLite runs in process, so "
                  "your counts must match; blocks 1, 3, 4 and 6 appear in 3.2, 3.3, 3.8 and 6.1, and block 7 is the trap "
                  "explained in 7.4 — EF Core's top three are the three largest premiums, raw SQL is not."),

        {"type": "chart", "toc": False, "heading": "9.3 · Lines of code in the lesson-09 samples", "kind": "hbar",
         "args": {"data": loc_rows, "labelw": 200, "tone": "navy", "width": 620},
         "caption": "non-blank, non-comment lines · measured from the sample files when this PDF was built",
         "note": f"<b>The first migration, its designer file and the model snapshot are {generated} lines — "
                 f"{generated / hand:.1f}× the hand-written data library ({hand} lines).</b> They are generated, but "
                 "you still review and commit them; a later migration adds only its own diff. " + MEASURED + " — a "
                 "size signal, not a quality score."},

        {"type": "callout", "variant": "warn", "heading": "⚠ Traps",
         "items": [
             "<b>“The collection will lazy-load.”</b> With lazy loading off — the default — a missing "
             "<code>Include</code> leaves <code>quote.Lines</code> empty — no proxy, no "
             "exception, just wrong totals (test <code>Missing_Include_leaves_Lines_empty</code>).",
             "<b>“A repository can return <code>IEnumerable</code>.”</b> Only after materialising. Any LINQ applied to "
             f"an <code>IEnumerable</code> view of a <code>DbSet</code> reads and tracks the whole table "
             f"({shape['IEnumerable'][2]} entities for one count in 3.3).",
             "<b>“The query will see what I just changed.”</b> EF Core does not flush before a query; save first "
             "(4.5).",
             "<b>“<code>IsConcurrencyToken</code> is <code>@Version</code>.”</b> It only adds the <code>WHERE</code> "
             "check. Something must change the value on every write — a database-generated token "
             "(<code>rowversion</code> on SQL Server, <code>xmin</code> on PostgreSQL) or your own code, as on "
             "SQLite — and <code>ExecuteUpdate</code> skips both the check and your override.",
             "<b>“Tests on the InMemory provider prove the data layer.”</b> It has no transactions, raw SQL or "
             "<code>ExecuteUpdate</code>; use SQLite in-memory for query shape and a real engine for the rest."]},

        {"type": "callout", "variant": "ok", "heading": "✔ Checkpoint — you are ready for lesson 10 when",
         "items": [
             f"<code>python 0-script/verify_samples.py --only 9</code> reports {n_proj}/{n_proj} passed on your "
             "machine.",
             "Given a LINQ query, you can predict its SQL and confirm it with <code>ToQueryString()</code>.",
             "You can explain every bar in chart 3.4 and write the test that keeps an N+1 from coming back.",
             "You can say which of script, bundle, <code>database update</code> and <code>MigrateAsync</code> you "
             "would use in a regulated production pipeline, and why.",
             "You can place a VB estate's data access: EF6 kept or ported, and new models in a C# library."]},

        {"type": "callout", "variant": "summary", "heading": "🔍 Check yourself",
         "items": [
             "Why is a <code>DbContext</code> registered per request scope, what happens when two tasks use one "
             "instance at the same time, and what do you inject for parallel or background work?",
             "What SQL does <code>Count</code> send when <code>db.Quotes</code> is typed as <code>IEnumerable</code>, "
             "and how many entities end up tracked?",
             "Why does 6.2's <code>ExecuteUpdate</code> set <code>Version</code> itself, when the "
             "<code>SaveChangesAsync</code> override in 4.3 stamps it on tracked writes?",
             "Which EF Core release made struct complex types possible, and what does Microsoft now advise for code "
             "that uses owned entity types?",
             "What two things does <code>Migrate()</code> do differently since EF Core 9?",
             "Name two things the InMemory provider cannot do that SQLite in-memory can (7.3, 7.6).",
             "A nightly job expires stale quotes and a dashboard needs a <code>GROUP BY</code> report — which tool for "
             "each, and what does each give up (6.5)?",
             "Two writes must succeed or fail together, and one of them is an <code>ExecuteUpdate</code> — what "
             "wraps them (4.6)?"]},

        {"type": "footer",
         "html": ("<b>Lesson 09 in one line:</b> EF Core is a short-lived unit of work that turns LINQ into SQL — "
                  "count the commands, project your reads, never flush-by-query, stamp your concurrency tokens, "
                  "generate and review migrations, and reach for <code>ExecuteUpdate</code>, Dapper or the AWS SDK "
                  "when tracked entities are the wrong tool. "
                  "<br/><b>Next:</b> " + ref(10) + " — xUnit, coverage gates and the integration tests that sit on "
                  "top of this data layer.")},
    ]
