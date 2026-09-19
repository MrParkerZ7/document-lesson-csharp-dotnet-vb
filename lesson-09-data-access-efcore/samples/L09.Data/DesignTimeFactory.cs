using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Design;

namespace L09.Data;

#region design-time-factory
// `dotnet ef` must build a context at design time. A class library has
// no host (no Program.cs, no DI) to ask, so the tool finds this instead.
public sealed class DesignTimeFactory : IDesignTimeDbContextFactory<MotorQuoteDbContext>
{
    public MotorQuoteDbContext CreateDbContext(string[] args) =>
        new(new DbContextOptionsBuilder<MotorQuoteDbContext>()
            .UseSqlite("Data Source=motorquote.db")
            .Options);
}
#endregion
