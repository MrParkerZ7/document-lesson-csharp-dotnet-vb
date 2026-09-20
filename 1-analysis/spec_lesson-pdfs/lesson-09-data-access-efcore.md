# Unit spec — lesson-09-data-access-efcore.pdf

Built to `_standard.md`. Content module `0-script/lessons/lesson_09.py`. Samples
`lesson-09-data-access-efcore/samples/` (with `dotnet-tools.json` pinning the `dotnet-ef` local tool).

## 1 · Purpose

Teach EF Core 10 data access to a JPA/Hibernate, TypeORM and Flyway engineer: the `DbContext` as a short-lived unit
of work, Fluent API mapping and complex types for `Money`, LINQ-to-SQL translation and its traps (IEnumerable,
missing `Include`, N+1), change tracking, explicit transactions (the answer to "where is `@Transactional`?") and
optimistic concurrency without `rowversion`, generated migrations and how to deploy them, when to use
`ExecuteUpdate`, Dapper or the AWS SDK instead, how to test data access, and what Visual Basic can and cannot do with
EF Core.

## 2 · Ownership & cadence

Owner **claude**, regenerable. Re-verify when EF Core 11 ships (scheduled November 2026 per the EF Core releases
page): the providers table 6.3 (Pomelo had no EF Core 10 release, Npgsql 10.0.3, MySql.EntityFrameworkCore 10.0.9 on
2026-09-16), the EntityFrameworkCore.VisualBasic claim (latest 8.0.0, EF Core 8 only), whether Learn's SQLite
limitations page still says decimal comparison is client-evaluated, and Learn's "Overall comparison" of test doubles
(table 7.6, page updated 2026-06-26). KPI "EF Core 10 · LTS" counts days to 10 Nov 2028 with `days_until()` at every
build; the date is cited in the "Before you start" callout (EF Core releases and planning), which also states the
*different* .NET 10 policy date (14 Nov 2028, `ref(1)`'s topic) so the two published tables are never conflated.
Re-capture `CONSOLE_OUT` / `VB_OUT` whenever a console sample changes (see § 8) — and whenever the canonical tariff in
`_curriculum.md` changes, because every premium, status count and expire count below comes from it.

## 3 · Structure

22 pages at the 2026-09-20 cross-review fix build (after the two single-lesson reviews and the cross-lesson review).

| § | Heading | Blocks |
|---|---|---|
| — | Contents | `toc` depth 2, no note (with the note and 61 rows the Contents did not fit under the title band, so page 1 printed empty; it now fills page 1). Code panels, `kept_table` and the twocol are listed through local `_listed()` / `kept_table()` / `figure_heading()`; the diagrams 2.5, 3.1 and 5.4 and the charts 7.5 and 9.3 carry `"toc": False` to keep it short · style block (headings kept with their first paragraph or table, `a.lnk` wraps at spaces instead of mid-word) |
| 1 | Why data access is where a .NET service shows its age | story (4 ¶) · `kpi` 1.1 (5 tiles: EF Core 10 LTS to Nov 2028 · N+1 21 → 1 · expire 10 → 1 · 25 test cases · InMemory provider discouraged) · `legend` (C#, architecture, legacy) · info callout "Before you start" (4 items: prerequisites ref(4)/ref(8) · the five projects · package and tool versions + `dotnet tool restore` + EF Core 10's support date **and** .NET 10's four days later, each with its own source · item 4: the seed is priced with the track's one illustrative tariff, 3+ claims is a decline stored as `QuoteStatus.Declined`, the worked example 8,933.71 THB is pinned by a test, then the honesty chips) |
| 2 | The model — DbContext, entities and value objects | story (3 ¶; ¶1 ends with `IDbContextFactory<T>` for parallel work and three sentences on `AddDbContextPool` — EF Core's own topic, taught here, not referred elsewhere — with the DbContext-pooling link; the DI-scope half carries ref(8) and the await rule ref(5)) · mapping 2.1 (14 rows: JPA/Hibernate/TypeORM/Flyway → EF Core, including `@Transactional` and TypeORM `migration:generate`) · compare 2.2 (Kotlin JPA entity ↔ C# `QuoteConfiguration`) · code 2.3 (`MotorQuoteDbContext`) · code 2.4 (`Money` record struct + `Driver` record) · mermaid 2.5 erDiagram `direction LR` (schema of the committed migration, all keys plus the columns later sections filter on, caption says "selected columns shown") · cards 2.6 (six mapping tools, 3 + 3 in a "(continued)" band; the data-annotations card says the five attributes are BCL types and that EF's own `[Index]` / `[Owned]` / `[Precision]` live in `Microsoft.EntityFrameworkCore.Abstractions`) |
| 3 | Querying — LINQ becomes SQL, or it silently does not | story (4 ¶) · mermaid 3.1 flowchart LR (one lambda, IQueryable vs IEnumerable path) · compare 3.2 (projection region ↔ captured SQL) · code 3.3 (IEnumerable vs IQueryable count, then the `AsNoTracking` block that the note's third figure comes from) · chartrow 3.4 grouped_bar (commands for N = 1/5/10/20: N+1 · Include · AsSplitQuery) + 3.5 bar (entities tracked after each 3.3 query) · code 3.6 (command-count tests, `keep=False`) · table 3.7 (five ways to load premium lines) · code 3.8 (`FromSql` parameterisation) |
| 4 | Saving — unit of work, transactions and optimistic concurrency | story (3 ¶; says there is no `@Transactional`) · mermaid 4.1 stateDiagram-v2 (EntityState, classDef colours) · code 4.2 (accept a quote) · code 4.3 (Guid token stamped in `SaveChangesAsync`, `keep=False`; note names SQL Server `byte[]` `IsRowVersion()` and PostgreSQL `uint` `xmin`) · mermaid 4.4 sequenceDiagram (underwriter vs broker conflict) · code 4.5 (no auto-flush + identity resolution test) · code 4.6 (`AcceptAndDeclineRivalsAsync`: one explicit transaction around `ExecuteUpdate` and `SaveChanges`, `keep=False`; the note names the two tests, the Dapper-joins-the-transaction test, and the retrying-execution-strategy trap with a link) · 4.7 twocol (Hibernate habits: carries over / drop or change) |
| 5 | Migrations — dotnet ef instead of Flyway and Liquibase | story (4 ¶; ¶1 ties EF's model diff to TypeORM's `migration:generate`) · code 5.1 (generated `CreateTable("Quotes")` region, `keep=False`) · table 5.2 (script · bundle · database update · MigrateAsync vs Flyway/Liquibase; the start-up row says the EF Core 9 lock makes several replicas safe) + a pill-colour legend line · code 5.3 (captured terminal: has-pending-model-changes, idempotent script refused on SQLite, bundle built and run twice) · mermaid 5.4 flowchart LR (developer → CI → release; three subgraphs **without** their own `direction`, so every arrow joins nodes: `R → G`, `G → S`, `G → B`, `S → DBA`, `B → JOB`, `DBA`/`JOB` → `APP`) |
| 6 | Beyond tracked entities — Dapper, bulk statements, providers and DynamoDB | story (4 ¶) · compare 6.1 (Spring `JdbcClient` ↔ Dapper) · compare 6.2 (tracked SaveChanges ↔ `ExecuteUpdate`, both C# samples) · table 6.3 (7 providers and EF Core 10 support; cites the Database providers page) · chartrow 6.4 bar (commands 11 vs 1) + 6.5 heatmap rubric (5 tools × Typed/Tracking/Locking/Raw SQL/Schema, cell 44; the note defines all five as capabilities) |
| 7 | Testing data access — choose the fake that lies least | story (3 ¶; ¶1 explains Testcontainers for .NET in two sentences **here** — what it does and that no lesson in the track runs one, because every sample must pass offline with no Docker; ref(10) is cited only for the true fact that it lists and declines it too) · code 7.1 (`SqliteDb` fixture) · code 7.2 (`SqlCommandLog` interceptor) · code 7.3 (InMemory `ExecuteUpdate` trap test) · code 7.4 (`raw-text-order`: raw SQL sorts SQLite's TEXT decimals as strings, `CAST(... AS REAL)` as the fixture workaround; figures parsed from `CONSOLE_OUT` block 7) · chart 7.5 hbar (test cases per class) · `kept_table` 7.6 (four test doubles × raw SQL / transactions / provider functions / exact query behaviour / LINQ anywhere, following Microsoft's overall comparison, with a reading line about the repository's `IEnumerable` cost) |
| 8 | Visual Basic alongside — the runtime is shared, the tooling is not | story (3 ¶) · compare 8.1 (C# `GroupBy` ↔ VB `Group By … Into`) · compare 8.2 (VB string filter ↔ captured SQL from VB) · code 8.3 (captured: `migrations add` and `dbcontext scaffold` refuse a VB project) |
| 9 | Hands-on — run the lesson-09 samples | story (2 ¶; block 7 points back to 7.4) · code 9.1 commands · code 9.2 captured console output (blocks 2, 5, 7) · chart 9.3 hbar (lines of code per project, generated migrations separate) · warn "Traps" (5) · ok checkpoint (5) · summary "Check yourself" (8 questions, including a tool-choice question and a transaction question) · footer (Next: ref(10)) |

Standard minimums as built: 9 numbered stories · 1 mapping (14 rows) · 2 card bands (3 + 3) · 5 mermaid (erDiagram,
flowchart ×2, stateDiagram-v2, sequenceDiagram) · 6 charts (grouped_bar, bar ×2, heatmap, hbar ×2) · 24 code panels
(18 `code` + 6 `compare`, 30 panel sides) · C# ↔ VB compare (8.1) · Kotlin ↔ C# (2.2) and Java ↔ C# (6.1) compares ·
1 twocol · 4 tables besides the mapping (3.7, 5.2, 6.3, 7.6) · 28 distinct source links (every `link()` defined in the
module is used at least once). Pagination at this build: the emptiest pages are 7 (34 % empty — the 3.4/3.5 chart row
cannot split), 11 and 16 (30 % each); every other page is more than 74 % full, the last page excepted.

## 4 · Derivation

- **Captured output.** `CONSOLE_OUT` (full `L09.QueryConsole` run) and `VB_OUT` (full `L09.VbReport` run) are pasted
  from real runs on the build machine (Windows x64, SDK 10.0.401, EF Core 10.0.12, SQLite in-memory). Panels 3.2
  (right), 8.2 (right) and 9.2 are cut from these constants, and the 7.4 note takes its three result lists from block 7;
  they were re-captured on 2026-09-20 from runs of the tariff-aligned samples (every premium, status count, coverage
  count and expire count in them moved). The terminal panels 5.3 and 8.3 were captured from `dotnet ef` 10.0.12 in
  `L09.Data` and `L09.VbModel`, re-run on 2026-09-20 (build-progress lines and long URLs left out, long lines
  wrapped — stated in the panel header); the model is unchanged, so `has-pending-model-changes` still reports none.
- **Tariff (the source of every premium here).** `QuoteSeed` implements the curriculum's canonical tariff exactly —
  base rate 2.1 / 1.2 / 0.9 / 0.4 % by class, loadings summed then applied (young driver +20 %, claims +0/+10/+25 %,
  commercial +25 % or +35 % over 3,000 cc), no-claim ladder 0/20/25/30/40/50 % on claim-free licence years, stamp duty
  0.4 %, VAT 7 %, 2 dp away from zero — and **3+ claims in five years is a decline**, stored the way the curriculum
  asks a data lesson to store it: `QuoteStatus.Declined`, `Total` 0 THB and a single `declined` premium line. Of the 20
  seeded quotes, 2 are declined (Q-0007, Q-0014), 3 accepted, 15 quoted; 9 of the quoted ones are stale. `TariffTests`
  pins the curriculum's worked example (8,933.71 THB) and the decline, so this lesson cannot drift from the track.
- **Charts and notes parsed from the captured output (MEASURED):** 3.4 and KPI "Load 20 quotes" = console block 2
  (N+1 2/6/11/21, Include 1, AsSplitQuery 2); 3.5 and the 3.3 note = block 3 (tracked 20 / 0 / 0, `AsNoTracking` block
  shown in the 3.3 panel); 6.4, KPI "Expire 9 quotes" and the 6.2 note = block 5 (10 vs 1 commands, 9 rows); the 7.4
  note = block 7 (its "smallest first" list starts with the two declined quotes at 0.0 — the note says so). The same
  numbers are asserted by `QueryShapeTests` and `SavingTests`, so a change in EF Core behaviour fails the tests before
  the PDF goes stale.
- **Computed at build (MEASURED):** KPI "Test cases" and chart 7.5 = `[Fact]` + `[InlineData]` rows per test class
  (25 at this build: QueryShapeTests 10, SavingTests 8, ProviderTrapTests 3, ModelTests 2, TariffTests 2); chart 9.3 =
  `loc()` per project with `Migrations/` split out (432 hand-written data library, 505 generated migration, 312 tests,
  157 console, 25 VB report, 13 VB model at this build), and its note computes the ratio and says what the 505 lines
  are (first migration, designer and snapshot, not the size of a later change); package versions in "Before you start"
  are read from `L09.Data.csproj` and `dotnet-tools.json`; the 5.1 note counts the region lines; checkpoint item 1
  counts the sample projects.
- **Bundle size** 33.0 MB (34,636,694 bytes, `BUNDLE_BYTES`) = the framework-dependent `efbundle.exe` produced by
  `dotnet ef migrations bundle` on the build machine, rebuilt and run twice on 2026-09-20 (MEASURED, captured).
- **VERIFIED facts (each linked in the PDF):** EF Core 10 requires .NET 10 and is supported to **10 Nov 2028** (EF Core
  releases and planning, re-read 2026-09-20), while the .NET support policy ends .NET 10 on **14 Nov 2028** (.NET
  support policy, re-read 2026-09-20 — lessons 01 and 12 quote that date and own it). The two dates are four days
  apart, so the callout states each with its own source instead of calling them one window; complex types since EF Core 8,
  struct/optional/JSON in EF Core 10, owned-type users advised to switch, not discovered by convention (What's new in
  EF Core 10, Complex types); `[Key]` / `[MaxLength]` / `[ConcurrencyCheck]` / `[Timestamp]` / `[ComplexType]` are BCL
  `System.ComponentModel.DataAnnotations` types — a scratch net10.0 library with no package reference builds with all
  five — while `[Index]` / `[Owned]` / `[Keyless]` / `[Precision]` / `[PrimaryKey]` / `[DeleteBehavior]` are in
  `Microsoft.EntityFrameworkCore.Abstractions` (NuGet package XML, 2026-09-20); Fluent API overrides data annotations
  (Creating and configuring a model); DbContext not thread-safe, scoped by `AddDbContext`, await async calls
  immediately, `AddDbContextFactory` for parallel work (DbContext lifetime — that page does **not** mention pooling);
  `AddDbContextPool` replaces `AddDbContext`, resets a disposed context and reuses the instance, which therefore
  outlives the scope, so `OnConfiguring` runs once and per-request state such as a tenant id needs a scoped factory
  over the pooled factory (DbContext pooling, read 2026-09-20); lazy loading is off unless the Proxies package or an injected `ILazyLoader`
  is used (Lazy loading, both variants documented there); split queries and the pre-EF 10 ordering warning (Single vs.
  split queries); `FromSql` parameters, EF Core 10 raw-SQL concatenation analyzer (SQL queries, What's new in EF Core
  10); concurrency tokens, SQLite has no database-generated token, PostgreSQL `xmin` mapped as a `uint` with
  `[Timestamp]` / `IsRowVersion()` (Handling concurrency conflicts, SQLite provider limitations, Npgsql concurrency
  page); `ExecuteUpdate` skips tracker/concurrency, starts no transaction, relational providers only (ExecuteUpdate and
  ExecuteDelete); a user-started transaction under a retrying execution strategy throws unless wrapped in
  `CreateExecutionStrategy().ExecuteAsync` (Connection resiliency); SQL Server batching 4–42 statements (Efficient
  updating); migration strategies, bundle recommendation, bundle SQL not inspectable, the EF Core 9 database-wide
  migration lock that makes start-up migration acceptable for several instances (Applying migrations); `Migrate()`
  throws on pending model changes since EF Core 9 (EF Core 9 breaking changes); `has-pending-model-changes` since
  EF Core 8, local-tool install, design-time factory (EF Core tools reference); idempotent scripts unsupported on
  SQLite (SQLite provider limitations, and the captured 5.3 error); testing-strategy order, InMemory "highly
  discouraged", SQLite case-sensitive vs SQL Server, and the overall comparison rows of table 7.6 (raw SQL:
  InMemory No / SQLite Depends / repository Yes / real Yes; transactions: No (ignored) / Yes / Yes / Yes; provider
  functions: No / No / Yes / Yes; exact query behaviour: Depends / Depends / Yes / Yes; LINQ anywhere: Yes / Yes /
  No* / Yes) (Choosing a testing strategy); providers table 6.3 (Database providers page + NuGet pages for Npgsql
  10.0.3 of 2026-07-10, first 10.0.0 2025-11-22; MySql.EntityFrameworkCore 10.0.9 of 2026-07-29; Pomelo latest stable
  9.0.0 of 2025-08-17 targeting EF Core 9); DynamoDB object persistence model, optimistic locking, no table API (AWS
  docs); EntityFrameworkCore.VisualBasic 8.0.0 depends on EF Core Design ≥ 8.0.2 < 9.0.0 (NuGet); EF6 stable,
  supported, not actively developed, no EDMX in EF Core (Compare EF6 and EF Core).
- **Verified by the samples (MEASURED, tests or captured output):** no auto-flush before a query and identity
  resolution (test `A_query_reads_the_database_not_unsaved_changes`, panel 4.5); one explicit transaction commits or
  rolls back an `ExecuteUpdate` and a `SaveChanges` together (tests
  `One_transaction_covers_ExecuteUpdate_and_SaveChanges`, `A_failed_SaveChanges_rolls_back_the_ExecuteUpdate_too`,
  panel 4.6, mutation-checked) and Dapper joins the EF Core transaction through `GetDbConnection()` /
  `GetDbTransaction()` (test `Dapper_joins_the_transaction_of_an_EF_Core_context`, named in the 4.6 note); required
  relationships cascade by default (generated script: `ON DELETE CASCADE` for PremiumLines and Policies); InMemory
  throws on `ExecuteUpdate` (test 7.3, whose comment and note claim green only on SQLite, the provider it ran on);
  `FromSql` hostile input sends `@p0` and returns 0 rows (console block 4, test
  `FromSql_sends_interpolated_values_as_parameters`); enum-as-string sorts `Class3` before `Class3Plus` (console
  block 6, VB output); EF Core translates decimal ORDER BY / comparison on SQLite via `EF_DECIMAL` and `ef_compare`
  while raw SQL sorts TEXT and `CAST(... AS REAL)` restores numeric order (console block 7, panel 7.4); VB string `=`
  translates to SQL `=` (VB output); both VB design-time commands fail with exit code 1 (8.3).
- **Not run (described from the linked documentation):** SQL Server `rowversion`, PostgreSQL `xmin`, a retrying
  execution strategy with a user transaction, SQL Server statement batching, PostgreSQL behaviour, `AddDbContextPool`,
  and Testcontainers — the § 7 story names the container tier as described-never-executed rather than promising it
  elsewhere (no lesson in the track runs a container; the offline-samples rule in `_standard.md` § 4 forbids it).
- **ESTIMATE:** heatmap 6.5 is a rubric (caption says so, note defines each column as a capability). Table 7.6 restates
  Microsoft's comparison table; "yes" is worded as "the application may still use it".

## 5 · Presentation

Format 00 via `brief_pdf.py`; code panels from `lesson_kit`. Local helpers in the module (as lessons 01/03/06):
`_listed()` puts code-panel headings in the Contents and strips Pygments' red error box on VB `$"` strings;
`figure_heading()` gives the twocol a numbered, kept heading; `kept_table()` prints a numbered table with its heading
and reading in one unbreakable group (used for 7.6, which otherwise split two rows / two rows across pages 18 and 19);
`cmd()` keeps table-cell commands unwrapped; `_section()` slices the captured console output by block; `_sources()`,
`_test_cases_by_class()` and `_package_version()` compute the measured figures. A lesson-local style block keeps
`.story .ct` / `.callout .ct` with their first paragraph/item, keeps `h2` headings with the following table or panel,
and lets `a.lnk` wrap at spaces (the kit's default `word-break:break-all` cut link labels mid-word). Layout decisions
from visual QA: 2.5 is an erDiagram with `direction LR` (the TB version filled a page); 3.1 is a flowchart LR with one
shared start node and two labelled branches; 5.4 is a flowchart LR whose subgraphs have no `direction` of their own —
with `direction TB` inside them Mermaid drew the cross-subgraph arrows to the subgraph borders, so the script and the
bundle were not visibly connected to the steps that use them — and its labels are two short lines so the text prints
larger; 5.2 (strategy table) comes before 5.3 (terminal capture) because the long terminal panel is unbreakable and
left page 13 a third empty when it came first; 6.3 (providers table) sits before the two charts for the same reason
(the chart row cannot split). Terminal panels use the `text` lexer (the shell lexer coloured everything after an
apostrophe). Chart 3.4 has no y-axis label because it collided with the grouped_bar legend.

## 6 · Inputs

- `roster.py`; samples (all project names start `L09.`):
  `L09.Data` (C# library: `MotorQuoteDbContext` + versioning partial, entities, `Money`/`Driver` complex types,
  `IEntityTypeConfiguration` classes, committed `20260914121532_InitialCreate` migration + snapshot,
  `DesignTimeFactory`, `QuoteQueries`, `QuoteWorkflow` (unit of work and the explicit-transaction workflow), Dapper
  `CoverageReport`, `SqlCommandLog` interceptor, `SqliteDb` fixture, deterministic `QuoteSeed` whose public
  `Price(reference, vehicle, driver, coverage, start)` applies the canonical tariff and is what `TariffTests` checks);
  `L09.Data.Tests` (xUnit, 25 cases in 5 classes — `QueryShapeTests`, `SavingTests`, `ProviderTrapTests`, `ModelTests`
  and `TariffTests` — on SQLite in-memory, plus the InMemory provider only for the trap test);
  `L09.QueryConsole` (C# console printing SQL and command counts; exits by itself); `L09.VbReport` (VB console
  querying the C# context); `L09.VbModel` (VB library declaring a context — the target of the refused `dotnet ef`
  commands); `samples/dotnet-tools.json` (`dotnet-ef` 10.0.12).
- Regions shown: `quote-config`, `context`, `money`, `projection`, `bulk-expire`, `from-sql`, `unit-of-work`,
  `explicit-transaction`, `stamp-version`, `create-quotes`, `sqlite-in-memory`, `interceptor`, `dapper` (L09.Data);
  `command-counts`, `no-auto-flush`, `in-memory-trap` (tests); `enumerable-vs-queryable` (three blocks: IEnumerable,
  IQueryable, `AsNoTracking`), `expire-tracked`, `cs-group`, `raw-text-order` (console); `vb-query`, `vb-strings`
  (VB report). Present but not shown: `design-time-factory`, `entities`, `missing-include`, `concurrency-conflict`,
  `transaction-tests`, `migration-in-sync`, `to-query-string`, `vb-model`.
- Sources: Microsoft Learn — EF Core releases and planning (https://learn.microsoft.com/en-us/ef/core/what-is-new/),
  What's new in EF Core 10 (…/ef-core-10.0/whatsnew), EF Core 9 breaking changes (…/ef-core-9.0/breaking-changes),
  Complex types (…/ef/core/modeling/complex-types), Creating and configuring a model (…/ef/core/modeling/), DbContext
  lifetime (…/ef/core/dbcontext-configuration/), DbContext pooling
  (…/ef/core/performance/advanced-performance-topics#dbcontext-pooling),
  Lazy loading (…/querying/related-data/lazy), Single vs. split
  queries (…/querying/single-split-queries), SQL queries (…/querying/sql-queries), Handling concurrency conflicts
  (…/saving/concurrency), ExecuteUpdate and ExecuteDelete (…/saving/execute-insert-update-delete), Efficient updating
  (…/performance/efficient-updating), Connection resiliency (…/ef/core/miscellaneous/connection-resiliency), Applying
  migrations (…/managing-schemas/migrations/applying), EF Core tools reference (…/ef/core/cli/dotnet), SQLite
  provider limitations (…/providers/sqlite/limitations), Choosing a testing strategy
  (…/testing/choosing-a-testing-strategy), Database providers (…/ef/core/providers/), Compare EF6 and EF Core
  (https://learn.microsoft.com/en-us/ef/efcore-and-ef6/); Npgsql — concurrency tokens
  (https://www.npgsql.org/efcore/modeling/concurrency.html); NuGet — Npgsql.EntityFrameworkCore.PostgreSQL,
  MySql.EntityFrameworkCore, Pomelo.EntityFrameworkCore.MySql, EntityFrameworkCore.VisualBasic
  (https://www.nuget.org/packages/<id>); the .NET support policy
  (https://dotnet.microsoft.com/platform/support/policy/dotnet-core) is where the 14 Nov 2028 date was verified — the
  PDF cites it through ref(1), which owns support policy; GitHub — Dapper (https://github.com/DapperLib/Dapper); Testcontainers for .NET
  (https://dotnet.testcontainers.org/); AWS — DynamoDB .NET object persistence model
  (https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DotNetSDKHighLevel.html).

## 7 · Invariants

- `CONSOLE_OUT` and `VB_OUT` must equal a fresh run of `L09.QueryConsole` / `L09.VbReport` (ignoring blank lines and
  trailing spaces); charts 3.4, 3.5, 6.4, the 7.4 note and three KPI tiles are parsed from them, so a stale capture
  misstates measured numbers.
- `QuoteSeed` must keep implementing the canonical tariff of `_curriculum.md` exactly, including the 3+ claims decline
  as `QuoteStatus.Declined` with a zero total; `TariffTests` pins the worked example (8,933.71 THB) and the decline. A
  tariff change moves every premium, coverage count and expire count in § 4, so re-run the console and VB samples and
  re-paste `CONSOLE_OUT` / `VB_OUT` in the same change.
- The command counts shown (N+1 = n + 1, Include = 1, AsSplitQuery = 2, tracked expire = 10 commands for 9 rows,
  ExecuteUpdate = 1) must stay asserted in `QueryShapeTests` / `SavingTests`.
- Every test runs against the committed migration (`SqliteDb` calls `Migrate()`, never `EnsureCreated()`), and
  `Committed_migration_matches_the_model` keeps the migration in sync with the model.
- `ExpireStaleAsync` must keep rotating `Version`, and the versioning partial must keep stamping it on save — 4.3, 6.2
  and trap 4 describe both. The 4.6 note names three tests by their exact method names; renaming one breaks the prose.
- `L09.VbModel` must stay a VB project with `Microsoft.EntityFrameworkCore.Design` so the 8.3 refusal stays
  reproducible.
- Compare regions stay ≤ 62 characters per line, code regions ≤ 100; the kit prints no width warning at this build.
- Contents must fit on page 1 under the title band; adding entries needs another `"toc": False` or a shorter list.
- No employer, client, insurer or bank names; experience is referenced generically ("a motor-insurance platform with
  dozens of partner integrations", "BI dashboards").

## 8 · Known gaps

- ⚠ Captured output (console, VB report, `dotnet ef` terminals) is pasted text; re-capture it when a sample's output
  format changes. The invariant above is checked by hand (a scratch comparison script), not by the build.
- ⚠ The bundle size and the EF Core patch number (10.0.12) reflect the build machine on 2026-09-20.
- ⚠ The canonical tariff's commercial +35 % band (over 3,000 cc) is implemented in `QuoteSeed` but not exercised: no
  seeded vehicle is over 3,000 cc, and no PDF figure depends on it.
- ⚠ Everything runs on SQLite; SQL Server `rowversion`, PostgreSQL `xmin`, a retrying execution strategy with a user
  transaction, SQL Server batching, PostgreSQL behaviour and Testcontainers are described from documentation, not run
  (no Docker or database server on the build machine). The 4.6 note and the 7.3 note say so.
- ⚠ Provider support in table 6.3 moves quickly (Pomelo's EF Core 10 release, Learn's provider table still listing 8
  and 9 for Npgsql and MySql.EntityFrameworkCore); re-check at every build after November 2026.
- ⚠ Learn's SQLite limitations page (updated 2026-04-16) says decimal comparison and ordering are client-evaluated;
  the SQL captured from EF Core 10.0.12 shows them translated (`EF_DECIMAL`, `ef_compare`). The lesson teaches the
  measured behaviour and names the discrepancy in the 7.4 note.
- ⚠ The Kotlin JPA entity (2.2) and Java `JdbcClient` method (6.1) are not compiled.
- ⚠ Heatmap 6.5 is a rubric; the claims behind its cells are in §6 prose and table 6.3, not measured.
- ⚠ Pages 7 (34 %), 11 and 16 (30 %) are partly empty because the next block (a chart row, a long code panel, a kept
  panel) cannot split; that is inside the standard's "about a third" but any content change can move it, so re-check
  `page-*.png` after edits.
