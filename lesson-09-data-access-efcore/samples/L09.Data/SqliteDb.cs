using Microsoft.Data.Sqlite;
using Microsoft.EntityFrameworkCore;

namespace L09.Data;

#region sqlite-in-memory
// A private SQLite database in memory. The CONNECTION is the database:
// close it and the data is gone, so it stays open for this object's life.
public sealed class SqliteDb : IDisposable
{
    private readonly SqliteConnection _connection = new("Data Source=:memory:");

    public SqlCommandLog Log { get; } = new();
    public SqliteConnection Connection => _connection;

    public SqliteDb()
    {
        _connection.Open();
        using var db = NewContext();
        db.Database.Migrate();   // the committed migration, not EnsureCreated()
    }

    public MotorQuoteDbContext NewContext() =>
        new(new DbContextOptionsBuilder<MotorQuoteDbContext>()
            .UseSqlite(_connection)
            .AddInterceptors(Log)
            .Options);

    public void Dispose() => _connection.Dispose();
}
#endregion

public static class SqliteDbSeeding
{
    /// <summary>Adds <paramref name="quotes"/> deterministic quotes, then clears the command log.</summary>
    public static SqliteDb Seed(this SqliteDb sqlite, int quotes)
    {
        using (var db = sqlite.NewContext())
        {
            db.Quotes.AddRange(QuoteSeed.Build(quotes));
            db.SaveChanges();
        }
        sqlite.Log.Reset();
        return sqlite;
    }
}
