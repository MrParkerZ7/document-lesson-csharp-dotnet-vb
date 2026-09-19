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

        Assert.Equal(94_080, result.Cases);
        Assert.True(result.Mismatches == 0, result.FirstMismatch);
    }

    // Counts are pinned, so the numbers printed in the lesson stay true.
    [Theory]
    [InlineData(PortChange.TruncatingCasts, 56_540)]
    [InlineData(PortChange.HalfUpRounding, 14_920)]
    [InlineData(PortChange.IntegerDivision, 16_076)]
    [InlineData(PortChange.BirthdayAge, 20_122)]
    [InlineData(PortChange.CaseSensitiveCodes, 40_320)]
    [InlineData(PortChange.FiveElementTable, 23_040)]
    [InlineData(PortChange.DecimalRates, 0)]
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
        var request = new QuoteRequest("CLASS4", 287_500m, new(1990, 3, 10), new(2026, 1, 1), 120, 0, 0);

        Assert.Null(LegacyAdapter.Quote(request, out var reason));
        Assert.Equal("unknown cover CLASS4", reason);
    }
}
