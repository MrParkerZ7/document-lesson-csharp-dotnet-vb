using System.Globalization;

namespace L03.Domain.Tests;

public class MoneyTests
{
    [Fact]
    public void Adding_the_same_currency_adds_the_amounts() =>
        Assert.Equal(Money.Thb(1_500m), Money.Thb(1_000m) + Money.Thb(500m));

    [Fact]
    public void Adding_different_currencies_throws() =>
        Assert.Throws<InvalidOperationException>(() => Money.Thb(1m) + new Money(1m, "USD"));

    [Theory]
    [InlineData("9450", "1.20", "11340.00")]
    [InlineData("0.125", "1", "0.13")]
    [InlineData("0.135", "1", "0.14")]
    public void Multiplying_rounds_to_two_places_away_from_zero(string amount, string factor, string expected)
    {
        var result = Money.Thb(Parse(amount)) * Parse(factor);
        Assert.Equal(Parse(expected), result.Amount);
    }

    [Fact]
    public void A_record_struct_compares_by_value_and_hashes_by_value()
    {
        var a = Money.Thb(10m);
        var b = Money.Thb(10m);
        Assert.True(a == b);
        Assert.Equal(a.GetHashCode(), b.GetHashCode());
    }

    [Fact]
    public void Default_money_never_ran_its_constructor()
    {
        var blank = default(Money);
        Assert.Null(blank.Currency);
        Assert.Equal(0m, blank.Amount);
    }

    private static decimal Parse(string s) => decimal.Parse(s, CultureInfo.InvariantCulture);
}

public class CopySemanticsTests
{
    private struct Tally
    {
        public int Count;
        public void Add() => Count++;
    }

    [Fact]
    public void Reading_a_struct_out_of_a_list_returns_a_copy()
    {
        var tallies = new List<Tally> { new() };
        var copy = tallies[0];
        copy.Add();
        Assert.Equal(1, copy.Count);
        Assert.Equal(0, tallies[0].Count);
    }

    [Fact]
    public void An_array_element_is_a_variable_so_it_mutates_in_place()
    {
        var tallies = new Tally[1];
        tallies[0].Add();
        Assert.Equal(1, tallies[0].Count);
    }

    [Fact]
    public void Two_boxes_of_the_same_int_are_two_objects()
    {
        object five = 5, alsoFive = 5;
        var sameReference = five == alsoFive;
        Assert.False(sameReference);
        Assert.Equal(five, alsoFive);
    }
}

public class RecordTests
{
    [Fact]
    public void Records_compare_by_value_and_with_makes_a_new_object()
    {
        var request = Samples.YoungDriver();
        var copy = request with { };
        Assert.Equal(request, copy);
        Assert.NotSame(request, copy);
    }

    [Fact]
    public void With_is_a_shallow_copy()
    {
        var request = Samples.YoungDriver();
        var class3 = request with { Coverage = CoverageClass.Class3 };
        Assert.NotEqual(request, class3);
        Assert.Same(request.Vehicle, class3.Vehicle);
    }
}
