namespace L10.Pricing.TestData;

/// <summary>
/// Test data builder shared by the C# test projects of lesson 10. It is linked into each project
/// (Compile Include=...), not referenced, so it is never counted as production code.
/// </summary>
public static class Requests
{
    public static readonly DateOnly Start = new(2026, 10, 1);

    #region builder
    public static QuoteRequest Standard(
        CoverageClass coverage = CoverageClass.Class1,
        decimal sumInsured = 600_000m,
        int age = 36,
        int licenceYears = 10,
        int claims = 0,
        VehicleUse use = VehicleUse.Private) =>
        new(new Vehicle("Toyota", "Yaris", 2023, 1200, use, new Money(sumInsured, "THB")),
            new Driver(Start.AddYears(-age), licenceYears, claims),
            coverage,
            Start);
    #endregion
}
