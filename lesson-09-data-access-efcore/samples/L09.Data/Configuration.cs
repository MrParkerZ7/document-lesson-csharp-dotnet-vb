using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace L09.Data;

#region quote-config
internal sealed class QuoteConfiguration
    : IEntityTypeConfiguration<Quote>
{
    public void Configure(EntityTypeBuilder<Quote> b)
    {
        b.HasIndex(q => q.Reference).IsUnique();
        b.Property(q => q.Reference).HasMaxLength(12);
        b.Property(q => q.Coverage)
            .HasConversion<string>().HasMaxLength(12);
        b.Property(q => q.Status)
            .HasConversion<string>().HasMaxLength(10);
        b.ComplexProperty(q => q.Total, m =>
        {
            m.Property(x => x.Amount).HasPrecision(12, 2);
            m.Property(x => x.Currency).HasMaxLength(3);
        });
        b.ComplexProperty(q => q.Driver);
        b.HasOne(q => q.Vehicle).WithMany()
            .OnDelete(DeleteBehavior.Restrict);
        b.HasMany(q => q.Lines).WithOne()
            .HasForeignKey(l => l.QuoteId);
        b.Property(q => q.Version).IsConcurrencyToken();
    }
}
#endregion

internal sealed class VehicleConfiguration : IEntityTypeConfiguration<Vehicle>
{
    public void Configure(EntityTypeBuilder<Vehicle> b)
    {
        b.Property(v => v.Make).HasMaxLength(40);
        b.Property(v => v.Model).HasMaxLength(40);
        b.Property(v => v.Use).HasConversion<string>().HasMaxLength(10);
        b.ComplexProperty(v => v.SumInsured, m =>
        {
            m.Property(x => x.Amount).HasPrecision(12, 2);
            m.Property(x => x.Currency).HasMaxLength(3);
        });
    }
}

internal sealed class PremiumLineConfiguration : IEntityTypeConfiguration<PremiumLine>
{
    public void Configure(EntityTypeBuilder<PremiumLine> b)
    {
        b.Property(l => l.Kind).HasMaxLength(16);
        b.ComplexProperty(l => l.Amount, m =>
        {
            m.Property(x => x.Amount).HasPrecision(12, 2);
            m.Property(x => x.Currency).HasMaxLength(3);
        });
    }
}

internal sealed class PolicyConfiguration : IEntityTypeConfiguration<Policy>
{
    public void Configure(EntityTypeBuilder<Policy> b)
    {
        b.Property(p => p.PolicyNumber).HasMaxLength(12);
        b.HasIndex(p => p.PolicyNumber).IsUnique();
        b.HasOne(p => p.Quote).WithOne().HasForeignKey<Policy>(p => p.QuoteId);
    }
}
