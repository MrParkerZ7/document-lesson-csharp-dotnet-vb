namespace L06.ModernRating;

#region request
// The loose VB parameter list becomes one immutable record.
public sealed record QuoteRequest(
    string CoverCode,
    decimal SumInsured,
    DateOnly DateOfBirth,
    DateOnly StartDate,
    int LicenceMonths,
    int Claims,
    bool Commercial = false,
    int EngineCc = 1_500);
#endregion
