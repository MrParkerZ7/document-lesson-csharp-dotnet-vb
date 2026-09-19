namespace L03.Domain;

#region records
public sealed record Vehicle(
    string Make, string Model, int Year, int EngineCc,
    VehicleUse Use, Money SumInsured);

public sealed record Driver(
    DateOnly DateOfBirth, int LicenceYears, int ClaimsLast5Years)
{
    public int AgeOn(DateOnly day)
    {
        var age = day.Year - DateOfBirth.Year;
        return DateOfBirth > day.AddYears(-age) ? age - 1 : age;
    }
}

public sealed record QuoteRequest(
    Vehicle Vehicle, Driver Driver,
    CoverageClass Coverage, DateOnly StartDate);
#endregion

#region premium
/// <summary>Illustrative only: not a real tariff.</summary>
public sealed record Premium(Money Net)
{
    public Money StampDuty => Net * 0.004m;          // 0.4% of net
    public Money Vat => (Net + StampDuty) * 0.07m;   // 7% of net + duty
    public Money Total => Net + StampDuty + Vat;
}
#endregion

public sealed record Policy(
    PolicyNumber Number, QuoteId QuoteId, DateOnly Inception, DateOnly Expiry);
