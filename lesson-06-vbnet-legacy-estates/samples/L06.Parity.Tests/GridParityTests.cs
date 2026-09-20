using L06.ModernRating;
using L06.Parity;
using Microsoft.VisualBasic;
using Microsoft.VisualBasic.CompilerServices;

namespace L06.Parity.Tests;

public class GridParityTests
{
    #region parity-tests
    [Fact]
    public void FaithfulPortMatchesLegacyOnEveryGridCase()
    {
        var result = ParityRunner.Compare(PremiumCalculator.Calculate);

        Assert.Equal(50_176, result.Cases);
        Assert.True(result.Mismatches == 0, result.FirstMismatch);
    }

    // The curriculum's worked example: 8,933.71 THB to the satang in the
    // canonical tariff; the legacy rule and its port price in whole baht.
    [Fact]
    public void WorkedExampleIsTheCanonicalTotalInWholeBaht()
    {
        var example = new QuoteRequest(
            "CLASS1", 550_000m, new(2002, 6, 15), new(2026, 1, 1), 48, 0);

        Assert.Equal(8_933.71m, CanonicalTariff.Total(example));
        Assert.Equal(8_933m, LegacyAdapter.Quote(example, out _));
        Assert.Equal(8_933m, PremiumCalculator.Calculate(example));
    }

    // Counts are pinned, so the numbers printed in the lesson stay true.
    [Theory]
    [InlineData(PortChange.TruncatingCasts, 22_520)]
    [InlineData(PortChange.HalfUpRounding, 11_324)]
    [InlineData(PortChange.IntegerDivision, 3_072)]
    [InlineData(PortChange.BirthdayAge, 8_064)]
    [InlineData(PortChange.CaseSensitiveCodes, 16_128)]
    [InlineData(PortChange.FiveElementTable, 3_072)]
    [InlineData(PortChange.DecimalRates, 304)]
    public void GridMeasuresEveryPortChange(PortChange change, int expected)
    {
        var result = ParityRunner.Compare(q => NaivePort.Calculate(q, change));

        Assert.Equal(expected, result.Mismatches);
    }
    #endregion

    #region vb-runtime
    // Microsoft.VisualBasic ships with .NET 10, so C# can ask the VB
    // runtime itself whether VbCompat reproduces it.
    [Fact]
    public void VbCompatAgreesWithTheVisualBasicRuntime()
    {
        foreach (double v in new[] { 0.5, 1.5, 2.5, 3.5, 3792.5, 17 / 12.0 })
            Assert.Equal(Conversions.ToInteger(v), VbCompat.CInt(v));

        foreach (var born in QuoteGrid.BirthDates)
            foreach (var start in QuoteGrid.StartDates)
                Assert.Equal(
                    DateAndTime.DateDiff(DateInterval.Year,
                        born.ToDateTime(TimeOnly.MinValue),
                        start.ToDateTime(TimeOnly.MinValue)),
                    VbCompat.DateDiffYears(born, start));

        foreach (var code in QuoteGrid.CoverCodes)
            Assert.Equal(
                Operators.CompareString(code, "CLASS1", TextCompare: true) == 0,
                VbCompat.TextEquals(code, "CLASS1"));
    }
    #endregion

    [Fact]
    public void AdapterTurnsMinusOneIntoNullWithAReason()
    {
        var request = new QuoteRequest("CLASS4", 287_500m, new(1990, 3, 10), new(2026, 1, 1), 120, 0);

        Assert.Null(LegacyAdapter.Quote(request, out var reason));
        Assert.Equal("unknown cover CLASS4", reason);
    }
}
