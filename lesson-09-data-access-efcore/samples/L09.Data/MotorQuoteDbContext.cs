using Microsoft.EntityFrameworkCore;

namespace L09.Data;

#region context
// The EntityManager of .NET: a short-lived unit of work that owns the
// change tracker. Create one per request (DI scope) — never share it.
public sealed partial class MotorQuoteDbContext(
    DbContextOptions<MotorQuoteDbContext> options) : DbContext(options)
{
    public DbSet<Vehicle> Vehicles => Set<Vehicle>();
    public DbSet<Quote> Quotes => Set<Quote>();
    public DbSet<PremiumLine> PremiumLines => Set<PremiumLine>();
    public DbSet<Policy> Policies => Set<Policy>();

    protected override void OnModelCreating(ModelBuilder model) =>
        model.ApplyConfigurationsFromAssembly(GetType().Assembly);
}
#endregion
