using Microsoft.EntityFrameworkCore;

namespace L09.Data;

#region stamp-version
// SQLite has no rowversion, so the token is application-managed:
// every quote that SaveChanges is about to write gets a new Guid.
// The UPDATE still filters on the ORIGINAL value that was read.
public sealed partial class MotorQuoteDbContext
{
    public override Task<int> SaveChangesAsync(
        bool acceptAllChangesOnSuccess,
        CancellationToken cancellationToken = default)
    {
        StampVersions();
        return base.SaveChangesAsync(acceptAllChangesOnSuccess, cancellationToken);
    }

    private void StampVersions()
    {
        foreach (var entry in ChangeTracker.Entries<Quote>())
        {
            if (entry.State is EntityState.Added or EntityState.Modified)
                entry.Entity.Version = Guid.NewGuid();
        }
    }

    // ...and the synchronous SaveChanges(bool) override calls StampVersions() too.
#endregion

    public override int SaveChanges(bool acceptAllChangesOnSuccess)
    {
        StampVersions();
        return base.SaveChanges(acceptAllChangesOnSuccess);
    }
}
