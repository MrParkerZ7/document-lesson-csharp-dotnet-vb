using L07.Core;

namespace L07.Pricing;

#region internals
// internal = visible inside the L07.Pricing assembly only.
// L07.Pricing.Tests is another assembly: it sees these
// types because Directory.Build.targets adds
// [InternalsVisibleTo("L07.Pricing.Tests")] at build time.
internal static class BaseRates
{
    // share of the sum insured per year: illustrative only
    internal static decimal For(CoverageClass coverage) =>
        coverage switch
        {
            CoverageClass.Class1 => 0.018m,
            CoverageClass.Class2Plus => 0.011m,
            CoverageClass.Class3Plus => 0.008m,
            CoverageClass.Class3 => 0.004m,
            _ => throw new ArgumentOutOfRangeException(
                nameof(coverage)),
        };
}
#endregion

internal static class Taxes
{
    internal const decimal StampDutyRate = 0.004m; // 0.4% of net premium, illustrative
    internal const decimal VatRate = 0.07m; // 7% of net premium + stamp duty, illustrative
}
