using System.Reflection;
using Dapper;
using L09.Data;
using Microsoft.EntityFrameworkCore;

var efVersion = typeof(DbContext).Assembly
    .GetCustomAttribute<AssemblyInformationalVersionAttribute>()!
    .InformationalVersion.Split('+')[0];
Console.WriteLine($"EF Core {efVersion} on SQLite in-memory; illustrative rates");

using var sqlite = new SqliteDb().Seed(20);

Title("1. ToQueryString: a projection");
#region to-query-string
await using (var db = sqlite.NewContext())
{
    var query = db.Summaries(CoverageClass.Class1);
    Print(query.ToQueryString());           // SQL, without running it
    foreach (var s in await query.ToListAsync())
        Console.WriteLine($"  {s.Reference}  {s.Make,-7}{s.Total,10:N2}  {s.Lines} lines");
}
#endregion

Title("2. Commands to load N quotes with their premium lines");
Console.WriteLine("  quotes   N+1   Include   AsSplitQuery");
foreach (var n in new[] { 1, 5, 10, 20 })
{
    using var sized = new SqliteDb().Seed(n);
    var nPlusOne = await Commands(sized, async db =>
    {
        foreach (var q in await db.Quotes.ToListAsync())
            await db.Entry(q).Collection(x => x.Lines).LoadAsync();
    });
    var include = await Commands(sized, db =>
        db.Quotes.Include(q => q.Lines).ToListAsync());
    var split = await Commands(sized, db =>
        db.Quotes.Include(q => q.Lines).AsSplitQuery().ToListAsync());
    Console.WriteLine($"  {n,6}  {nPlusOne,4}  {include,8}  {split,13}");
}

Title("3. One Count as IEnumerable, as IQueryable; then AsNoTracking");
sqlite.Log.Reset();
#region enumerable-vs-queryable
await using (var db = sqlite.NewContext())
{
    IEnumerable<Quote> all = db.Quotes;   // LINQ to Objects
    var n = all.Count(q => q.Coverage == CoverageClass.Class1);
    Report("IEnumerable", n, db);
}
await using (var db = sqlite.NewContext())
{
    IQueryable<Quote> query = db.Quotes;  // LINQ to SQL
    var n = query.Count(q => q.Coverage == CoverageClass.Class1);
    Report("IQueryable", n, db);
}
await using (var db = sqlite.NewContext())
{
    var rows = await db.Quotes.AsNoTracking()   // entities, no snapshot
        .Where(q => q.Coverage == CoverageClass.Class1)
        .ToListAsync();
    Report("AsNoTracking", rows.Count, db, printSql: false);
}
#endregion

Title("4. FromSql with hostile input");
await using (var db = sqlite.NewContext())
{
    sqlite.Log.Reset();
    var hostile = "Toyota' OR '1'='1";
    var rows = await db.VehiclesByMake(hostile).ToListAsync();
    Console.WriteLine($"  input  {hostile}");
    Console.WriteLine($"  rows   {rows.Count}");
    Print(sqlite.Log.Sql[0]);
}

Title("5. Expire stale quotes: tracked SaveChanges vs ExecuteUpdate");
using (var tracked = new SqliteDb().Seed(20))
{
    var expired = 0;
    var commands = await Commands(tracked, async db =>
    {
        #region expire-tracked
        // SELECT: 10 rows loaded and tracked
        var stale = await db.Quotes
            .Where(q => q.Status == QuoteStatus.Quoted
                     && q.ValidUntil < QuoteSeed.Today)
            .ToListAsync();
        foreach (var q in stale)
            q.Status = QuoteStatus.Expired;  // in memory
        // SaveChanges: one UPDATE statement per row
        expired = await db.SaveChangesAsync();
        #endregion
    });
    Console.WriteLine($"  tracked + SaveChanges  rows {expired,2}  commands {commands,2}");
}
using (var bulk = new SqliteDb().Seed(20))
{
    var expired = 0;
    var commands = await Commands(bulk, async db =>
        expired = await db.ExpireStaleAsync(QuoteSeed.Today));
    Console.WriteLine($"  ExecuteUpdate          rows {expired,2}  commands {commands,2}");
    Print(bulk.Log.Sql[0]);
}

Title("6. Quoted quotes by coverage: EF Core LINQ and Dapper SQL");
await using (var db = sqlite.NewContext())
{
    #region cs-group
    var byCoverage = await db.Quotes
        .Where(q => q.Status == QuoteStatus.Quoted)
        .GroupBy(q => q.Coverage)
        .Select(g => new { Coverage = g.Key, Quotes = g.Count() })
        .OrderBy(x => x.Coverage)
        .ToListAsync();
    #endregion
    foreach (var row in byCoverage)
        Console.WriteLine($"  LINQ    {row.Coverage,-11}{row.Quotes,3}");
}
foreach (var row in await CoverageReport.ByCoverageAsync(sqlite.Connection, "Quoted"))
    Console.WriteLine($"  Dapper  {row.Coverage,-11}{row.Quotes,3}  lines {row.Lines}");

Title("7. decimal is stored as TEXT on SQLite");
await using (var db = sqlite.NewContext())
{
    var top = db.Quotes
        .OrderByDescending(q => q.Total.Amount)
        .Select(q => q.Reference)
        .Take(3);
    Console.WriteLine($"  EF Core  top 3 by total  {string.Join(", ", top.ToList())}");
    Print(top.ToQueryString());
    var overQuery = db.Quotes.Where(q => q.Total.Amount > 20_000m);
    Console.WriteLine($"  EF Core  totals over 20,000: {overQuery.Count()}");
    Print(overQuery.Select(q => q.Reference).ToQueryString());
}
#region raw-text-order
var raw = await sqlite.Connection.QueryAsync<string>("""
    SELECT Reference || ' ' || Total_Amount FROM Quotes
    ORDER BY Total_Amount DESC LIMIT 3
    """);   // the column holds TEXT: this sorts strings

var smallest = await sqlite.Connection.QueryAsync<string>("""
    SELECT Reference || ' ' || Total_Amount FROM Quotes
    ORDER BY CAST(Total_Amount AS REAL) LIMIT 3
    """);   // the workaround: sort as a number
#endregion
Console.WriteLine($"  raw SQL  top 3 by total  {string.Join(", ", raw)}");
Console.WriteLine($"  raw SQL  3 smallest (CAST AS REAL)  {string.Join(", ", smallest)}");

static void Title(string text) => Console.WriteLine($"{Environment.NewLine}== {text}");

static void Print(string sql)
{
    foreach (var raw in sql.Split('\n'))
    {
        var line = raw.TrimEnd('\r');
        while (line.Length > 90)
        {
            var cut = line.LastIndexOf(", ", 90, StringComparison.Ordinal);
            if (cut < 20)
                break;
            Console.WriteLine("  " + line[..(cut + 1)]);
            line = "      " + line[(cut + 2)..];
        }
        Console.WriteLine("  " + line);
    }
}

static async Task<int> Commands(SqliteDb sqlite, Func<MotorQuoteDbContext, Task> work)
{
    await using var db = sqlite.NewContext();
    sqlite.Log.Reset();
    await work(db);
    return sqlite.Log.Count;
}

void Report(string label, int count, MotorQuoteDbContext db, bool printSql = true)
{
    Console.WriteLine($"  {label,-12} count {count}  commands {sqlite.Log.Count}"
        + $"  tracked {db.ChangeTracker.Entries().Count()}");
    if (printSql)
        Print(sqlite.Log.Sql[^1]);
    sqlite.Log.Reset();
}
