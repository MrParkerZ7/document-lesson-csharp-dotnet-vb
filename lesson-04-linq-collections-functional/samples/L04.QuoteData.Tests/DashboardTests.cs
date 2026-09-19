using System.Collections.Immutable;
using System.Linq.Expressions;

namespace L04.QuoteData.Tests;

public class DashboardTests
{
    private sealed record Tagged(string Id, ImmutableArray<string> Tags);

    private static readonly IReadOnlyList<Quote> Quotes = QuoteBook.Generate();

    [Fact]
    public void The_dataset_is_deterministic()
    {
        Assert.Equal(240, Quotes.Count);
        Assert.True(QuoteBook.Generate().SequenceEqual(Quotes)); // records compare by value
    }

    [Fact]
    public void Conversion_accounts_for_every_quote()
    {
        var conversion = QuoteDashboard.Conversion(Quotes);

        Assert.Equal(4, conversion.Count);
        Assert.Equal(Quotes.Count, conversion.Sum(c => c.Quoted));
        Assert.Equal(Quotes.Count(q => q.IsAccepted), conversion.Sum(c => c.Accepted));
    }

    [Fact]
    public void Bands_account_for_every_quote()
    {
        Assert.Equal(Quotes.Count, QuoteDashboard.Bands(Quotes).Sum(b => b.Value));
    }

    [Fact]
    public void Every_sixth_accepted_quote_is_pending_issuance()
    {
        var issuance = QuoteDashboard.Issuance(Quotes, QuoteBook.IssuePolicies(Quotes)).ToList();

        Assert.Equal(Quotes.Count(q => q.IsAccepted), issuance.Count);
        Assert.Equal(issuance.Count / 6, issuance.Count(x => x.Policy == "(pending)"));
    }

    [Fact]
    public void Dashboard_numbers_match_the_captured_lesson_output()
    {
        // lesson 04 prints these figures from a captured run: if a test here fails, re-capture it
        Assert.Equal("25,34,37,45",
            string.Join(",", QuoteDashboard.Conversion(Quotes).Select(c => c.Accepted)));
        Assert.Equal("< 3k 60,3k-6k 18,6k-9k 92,9k-12k 52,12k+ 18",
            string.Join(",", QuoteDashboard.Bands(Quotes).Select(b => $"{b.Key} {b.Value}")));
        Assert.Equal("Toyota 31,Honda 26,Isuzu 17,MG 17,Nissan 17",
            string.Join(",", QuoteDashboard.TopMakes(Quotes).Select(m => $"{m.Make} {m.Sold}")));
        Assert.Equal("198362,297928,348568,84600",
            string.Join(",", QuoteDashboard.PremiumByClass(Quotes)
                .Select(kv => kv.Value.ToString("0", System.Globalization.CultureInfo.InvariantCulture))));
        Assert.Equal(23, QuoteDashboard.Issuance(Quotes, QuoteBook.IssuePolicies(Quotes))
            .Count(x => x.Policy == "(pending)"));
    }

    [Fact]
    public void Three_passes_over_a_deferred_query_run_its_predicate_three_times()
    {
        var calls = 0;
        var accepted = Quotes.Where(q => { calls++; return q.IsAccepted; });

        _ = accepted.Count();
        _ = accepted.First();                        // Q-0002: stops after 2 calls
        foreach (var _ in accepted) { }

        Assert.Equal(240 + 2 + 240, calls);
    }

    [Fact]
    public void GroupBy_is_deferred_and_ToLookup_is_immediate()
    {
        var calls = 0;
        string Key(Quote q) { calls++; return q.Vehicle.Make; }

        var groups = Quotes.GroupBy(Key);
        Assert.Equal(0, calls);                      // nothing has run yet

        _ = Quotes.ToLookup(Key);
        Assert.Equal(Quotes.Count, calls);           // ran once, right now

        _ = groups.Count();
        _ = groups.Count();
        Assert.Equal(3 * Quotes.Count, calls);       // the GroupBy ran twice more
    }

    [Theory]
    [InlineData(24, 1.20)]
    [InlineData(25, 1.00)]
    public void The_young_driver_rule_is_a_pure_function(int age, double expectedFactor)
    {
        var youngDriver = Rating.Rules.Single(r => r.Name == "young driver").Apply;
        var input = new RatingInput(CoverageClass.Class1, 500_000m, age, 0, 3, VehicleUse.Private);

        Assert.Equal((decimal)expectedFactor * 10_000m, youngDriver(input, 10_000m));
        Assert.Equal(youngDriver(input, 10_000m), youngDriver(input, 10_000m));
    }

    [Fact]
    public void A_band_without_quotes_still_gets_a_row_with_zero()
    {
        var onlyMidBand = Quotes.Where(q => QuoteDashboard.BandOf(q.Total) == "3k-6k");

        var bands = QuoteDashboard.Bands(onlyMidBand);

        Assert.Equal(QuoteDashboard.BandOrder, bands.Select(b => b.Key));
        Assert.Equal([0, 18, 0, 0, 0], bands.Select(b => b.Value));
    }

    [Fact]
    public void CountBy_and_AggregateBy_are_deferred_and_run_again_on_every_enumeration()
    {
        var calls = 0;
        string Key(Quote q) { calls++; return q.Vehicle.Make; }

        var counted = Quotes.CountBy(Key);
        var summed = Quotes.AggregateBy(Key, 0, (n, _) => n + 1);
        Assert.Equal(0, calls);                      // declared, nothing has run

        _ = counted.Count();
        _ = counted.Count();
        _ = summed.Count();
        Assert.Equal(3 * Quotes.Count, calls);       // each enumeration counted all quotes again
    }

    [Fact]
    public void The_C_sharp_query_syntax_left_join_matches_LeftJoin()
    {
        var policies = QuoteBook.IssuePolicies(Quotes);

        Assert.Equal(
            QuoteDashboard.Issuance(Quotes, policies),
            QuoteDashboard.IssuanceQuery(Quotes, policies));
    }

    [Fact]
    public void The_C_sharp_ports_reproduce_the_captured_Visual_Basic_output()
    {
        // lesson 04 prints the Visual Basic console's output: these are the same figures in C#
        var summary = QuoteDashboard.Summarise(Quotes);
        Assert.Equal(141, summary.Policies);
        Assert.Equal("16759", summary.Largest.ToString("0", System.Globalization.CultureInfo.InvariantCulture));

        Assert.Equal("Q-0014,Q-0080,Q-0143,Q-0106",
            string.Join(",", QuoteDashboard.Window(Quotes, 8_400m, 8_600m).Select(x => x.QuoteId)));
        Assert.Equal(8, QuoteDashboard.Makes(Quotes).Count());
    }

    [Fact]
    public void A_record_holding_an_ImmutableArray_compares_the_array_reference()
    {
        var a = new Tagged("x", ["1", "2"]);
        var b = new Tagged("x", ["1", "2"]);

        Assert.False(a == b);                          // same elements, two arrays
        Assert.True(a.Tags.SequenceEqual(b.Tags));
        Assert.True(a == a with { });                  // the same array reference is equal
    }

    [Fact]
    public void AsReadOnly_refuses_the_cast_back_to_List_that_the_interface_view_allows()
    {
        var list = new List<string> { "Class1" };
        IReadOnlyList<string> view = list;
        IReadOnlyList<string> wrapper = list.AsReadOnly();

        Assert.Same(list, (List<string>)view);                        // compiles and works
        Assert.Throws<InvalidCastException>(() => (List<string>)wrapper);
        list.Add("Class3");
        Assert.Equal(2, wrapper.Count);                               // but the wrapper is still live
    }

    [Fact]
    public void MaxBy_on_an_empty_sequence_returns_null_for_classes_and_throws_for_structs()
    {
        Assert.Null(Array.Empty<Quote>().MaxBy(q => q.Total.Amount));
        Assert.Throws<InvalidOperationException>(
            () => Array.Empty<KeyValuePair<string, int>>().MaxBy(kv => kv.Value));
    }

    [Fact]
    public void An_interpolated_string_compiles_inside_an_expression_tree_as_string_Format()
    {
        Expression<Func<Quote, string>> tree = q => $"{q.QuoteId}!";

        var call = Assert.IsAssignableFrom<MethodCallExpression>(tree.Body);
        Assert.Equal("Format", call.Method.Name);
    }
}
