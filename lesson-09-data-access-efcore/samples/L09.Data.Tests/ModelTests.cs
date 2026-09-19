using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata;

namespace L09.Data.Tests;

public class ModelTests
{
    #region migration-in-sync
    [Fact]
    public void Committed_migration_matches_the_model()
    {
        // SqliteDb's constructor runs Database.Migrate(), which since
        // EF Core 9 throws if the model has changes no migration covers.
        using var sqlite = new SqliteDb();
        using var db = sqlite.NewContext();

        Assert.False(db.Database.HasPendingModelChanges());
        var applied = Assert.Single(db.Database.GetAppliedMigrations());
        Assert.EndsWith("_InitialCreate", applied);
    }
    #endregion

    [Fact]
    public void Money_and_Driver_are_complex_types_not_entities()
    {
        using var sqlite = new SqliteDb();
        using var db = sqlite.NewContext();

        var quote = db.Model.FindEntityType(typeof(Quote))!;
        var complex = quote.GetComplexProperties().Select(p => p.Name).Order();

        Assert.Equal(["Driver", "Total"], complex);
        Assert.Null(db.Model.FindEntityType(typeof(Money)));
        var amount = quote.FindComplexProperty("Total")!.ComplexType.FindProperty("Amount")!;
        Assert.Equal("Total_Amount", amount.GetColumnName(StoreObjectIdentifier.Table("Quotes")));
    }
}
