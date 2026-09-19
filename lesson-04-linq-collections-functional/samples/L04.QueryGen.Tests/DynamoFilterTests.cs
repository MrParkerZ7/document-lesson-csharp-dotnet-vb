using System.Linq.Expressions;
using L04.QuoteData;

namespace L04.QueryGen.Tests;

public class DynamoFilterTests
{
    private sealed record Row(string Id, bool Renewal, int Year, DateOnly Start, string[] Tags);

    private sealed class Stored(string make)
    {
        public string Make { get; } = make; // get-only, but still a stored attribute
    }

    [Fact]
    public void Equality_uses_placeholders_for_names_and_values()
    {
        var f = DynamoFilter.From<Quote>(q => q.QuoteId == "Q-0001");

        Assert.Equal("#n0 = :v0", f.Expression);
        Assert.Equal("QuoteId", f.Names["#n0"]);
        Assert.Equal("Q-0001", f.Values[":v0"]);
    }

    #region tests
    [Fact]
    public void Captured_variables_are_read_when_the_filter_is_built()
    {
        var min = 10_000m;
        Expression<Func<Quote, bool>> predicate = q => q.Total.Amount >= min;

        var built = DynamoFilter.From(predicate);
        min = 99_999m; // too late for `built`: it was translated already

        Assert.Equal("#n0.#n1 >= :v0", built.Expression);
        Assert.Equal(10_000m, built.Values[":v0"]);
        Assert.Equal(99_999m, DynamoFilter.From(predicate).Values[":v0"]);
    }

    [Fact]
    public void A_computed_property_compiles_but_cannot_be_translated()
    {
        var ex = Assert.Throws<NotSupportedException>(
            () => DynamoFilter.From<Quote>(q => q.IsAccepted));

        Assert.Contains("IsAccepted", ex.Message);
    }
    #endregion

    [Fact]
    public void Enum_comparison_is_written_as_the_member_name()
    {
        var f = DynamoFilter.From<Quote>(q => q.Coverage == CoverageClass.Class3Plus);

        Assert.Equal("#n0 = :v0", f.Expression);
        Assert.Equal("Class3Plus", f.Values[":v0"]);
    }

    [Theory]
    [InlineData("eq", "#n0 = :v0")]
    [InlineData("ne", "#n0 <> :v0")]
    [InlineData("lt", "#n0 < :v0")]
    [InlineData("le", "#n0 <= :v0")]
    [InlineData("gt", "#n0 > :v0")]
    [InlineData("ge", "#n0 >= :v0")]
    public void Comparison_operators_map_to_DynamoDB_comparators(string op, string expected)
    {
        Expression<Func<Row, bool>> predicate = op switch
        {
            "eq" => r => r.Year == 2020,
            "ne" => r => r.Year != 2020,
            "lt" => r => r.Year < 2020,
            "le" => r => r.Year <= 2020,
            "gt" => r => r.Year > 2020,
            _ => r => r.Year >= 2020,
        };

        Assert.Equal(expected, DynamoFilter.From(predicate).Expression);
    }

    [Fact]
    public void A_constant_on_the_left_is_moved_to_the_right()
    {
        var f = DynamoFilter.From<Row>(r => 2020 < r.Year);

        Assert.Equal("#n0 > :v0", f.Expression);
    }

    [Fact]
    public void And_or_not_keep_their_grouping()
    {
        var f = DynamoFilter.From<Row>(r => (r.Year > 2020 || r.Renewal) && !(r.Id == "x"));

        Assert.Equal("((#n0 > :v0 OR #n1 = :v1) AND NOT (#n2 = :v2))", f.Expression);
        Assert.Equal(true, f.Values[":v1"]);
    }

    [Fact]
    public void The_same_attribute_reuses_one_name_placeholder()
    {
        var f = DynamoFilter.From<Quote>(q => q.Total.Amount > 1_000m && q.Total.Amount < 2_000m);

        Assert.Equal("(#n0.#n1 > :v0 AND #n0.#n1 < :v1)", f.Expression);
        Assert.Equal(2, f.Names.Count);
        Assert.Equal(2, f.Values.Count);
    }

    [Fact]
    public void StartsWith_becomes_begins_with()
    {
        var f = DynamoFilter.From<Quote>(q => q.Vehicle.Make.StartsWith("To"));

        Assert.Equal("begins_with(#n0.#n1, :v0)", f.Expression);
        Assert.Equal("Vehicle", f.Names["#n0"]);
        Assert.Equal("Make", f.Names["#n1"]);
    }

    [Fact]
    public void String_contains_becomes_contains()
    {
        var f = DynamoFilter.From<Quote>(q => q.Vehicle.Model.Contains("Revo"));

        Assert.Equal("contains(#n0.#n1, :v0)", f.Expression);
    }

    [Fact]
    public void A_local_array_contains_becomes_IN()
    {
        string[] makes = ["Toyota", "Honda"];

        var f = DynamoFilter.From<Quote>(q => makes.Contains(q.Vehicle.Make));

        Assert.Equal("#n0.#n1 IN (:v0, :v1)", f.Expression);
        Assert.Equal("Honda", f.Values[":v1"]);
    }

    [Fact]
    public void Dates_are_written_as_ISO_8601_strings()
    {
        var from = new DateOnly(2026, 11, 1);

        var f = DynamoFilter.From<Row>(r => r.Start >= from);

        Assert.Equal("2026-11-01", f.Values[":v0"]);
    }

    [Fact]
    public void A_method_the_translator_does_not_know_fails_at_run_time()
    {
        Assert.Throws<NotSupportedException>(
            () => DynamoFilter.From<Quote>(q => q.Vehicle.Make.ToUpperInvariant() == "TOYOTA"));
    }

    [Fact]
    public void A_get_only_auto_property_is_still_a_stored_attribute()
    {
        var f = DynamoFilter.From<Stored>(s => s.Make == "Toyota");

        Assert.Equal("#n0 = :v0", f.Expression);
        Assert.Equal("Make", f.Names["#n0"]);
    }

    [Fact]
    public void An_IN_list_of_exactly_100_values_is_accepted()
    {
        var makes = Enumerable.Range(0, 100).Select(i => $"Make{i}").ToArray();

        var f = DynamoFilter.From<Quote>(q => makes.Contains(q.Vehicle.Make));

        Assert.Equal(100, f.Values.Count);
    }

    [Theory]
    [InlineData(0)]
    [InlineData(101)]
    public void An_IN_list_outside_1_to_100_values_is_refused(int count)
    {
        var makes = Enumerable.Range(0, count).Select(i => $"Make{i}").ToArray();

        var ex = Assert.Throws<NotSupportedException>(
            () => DynamoFilter.From<Quote>(q => makes.Contains(q.Vehicle.Make)));

        Assert.Contains("1 to 100", ex.Message);
    }

    [Fact]
    public void Contains_on_a_list_attribute_is_not_translated()
    {
        Assert.Throws<NotSupportedException>(
            () => DynamoFilter.From<Row>(r => r.Tags.Contains("fleet")));
    }

    [Fact]
    public void A_method_DynamoDB_has_no_function_for_is_refused()
    {
        Assert.Throws<NotSupportedException>(
            () => DynamoFilter.From<Quote>(q => q.Vehicle.Make.EndsWith("a")));
    }
}
