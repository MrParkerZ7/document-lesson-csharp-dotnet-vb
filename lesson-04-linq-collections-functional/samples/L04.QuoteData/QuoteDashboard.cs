using Issued = (string QuoteId, string Policy);
using Priced = (string QuoteId, decimal Amount);
using Summary = (int Policies, decimal Premium, decimal Largest);

namespace L04.QuoteData;

/// <summary>Dashboard-style queries over the quote book. Each returns a query or a materialised list.</summary>
public static class QuoteDashboard
{
    #region conversion
    public static IReadOnlyList<ClassConversion> Conversion(
        IEnumerable<Quote> quotes) =>
        quotes
            .Where(q => q.Status != QuoteStatus.Declined)
            .GroupBy(q => q.Coverage)
            .OrderBy(g => g.Key)
            .Select(g => new ClassConversion(
                g.Key,
                Quoted: g.Count(),
                Accepted: g.Count(q => q.IsAccepted)))
            .ToList();
    #endregion

    #region premium-bands
    public static readonly string[] BandOrder = ["< 3k", "3k-6k", "6k-9k", "9k-12k", "12k+"];

    public static string BandOf(Money premium) => premium.Amount switch
    {
        < 3_000m => "< 3k",
        < 6_000m => "3k-6k",
        < 9_000m => "6k-9k",
        < 12_000m => "9k-12k",
        _ => "12k+",
    };

    // .NET 9 CountBy: one pass, one counter per key. A band with no quotes gets no key,
    // so walk BandOrder and look each band up: an empty band shows 0, not a missing row
    public static IReadOnlyList<KeyValuePair<string, int>> Bands(
        IEnumerable<Quote> quotes)
    {
        var counts = quotes
            .Where(q => q.Status != QuoteStatus.Declined) // a declined quote has no premium
            .CountBy(q => BandOf(q.Total))
            .ToDictionary();
        return BandOrder
            .Select(band => KeyValuePair.Create(band, counts.GetValueOrDefault(band)))
            .ToList();
    }
    #endregion

    #region top-makes
    public static IEnumerable<MakeRank> TopMakes(
        IEnumerable<Quote> quotes, int take = 5) =>
        quotes
            .Where(q => q.IsAccepted)
            .CountBy(q => q.Vehicle.Make)
            .OrderByDescending(kv => kv.Value)
            .ThenBy(kv => kv.Key)
            .Take(take)
            .Index()
            .Select(x => new MakeRank(
                Rank: x.Index + 1, x.Item.Key, x.Item.Value));
    #endregion

    #region net9-additions
    // accepted premium per coverage class in one pass: no intermediate IGrouping objects
    public static IEnumerable<KeyValuePair<CoverageClass, decimal>> PremiumByClass(
        IEnumerable<Quote> quotes) =>
        quotes
            .Where(q => q.IsAccepted)
            .AggregateBy(
                keySelector: q => q.Coverage,
                seed: 0m,
                (total, q) => total + q.Total.Amount)
            .OrderBy(kv => kv.Key);
    #endregion

    #region left-join
    const string Unset = "(pending)"; // no policy issued yet

    // .NET 10: accepted quotes, with a policy if one exists
    public static IEnumerable<Issued> Issuance(
        IEnumerable<Quote> quotes,
        IEnumerable<Policy> policies) =>
        quotes
            .Where(q => q.IsAccepted)
            .LeftJoin(policies,
                q => q.QuoteId, p => p.QuoteId,
                (q, p) => (q.QuoteId, p?.PolicyNumber ?? Unset));
    #endregion

    #region left-join-query
    // before .NET 10: the same left join in query syntax
    public static IEnumerable<Issued> IssuanceQuery(
        IEnumerable<Quote> quotes,
        IEnumerable<Policy> policies) =>
        from q in quotes
        where q.IsAccepted
        join p in policies on q.QuoteId equals p.QuoteId
            into issued
        from p in issued.DefaultIfEmpty()
        select (q.QuoteId, p?.PolicyNumber ?? Unset);
    #endregion

    #region lookup-and-chunk
    // ToLookup runs NOW and can be read many times; GroupBy re-runs on every enumeration
    public static ILookup<string, Quote> ByMake(IEnumerable<Quote> quotes) =>
        quotes.ToLookup(q => q.Vehicle.Make);

    // a partner export in fixed-size batches; the last batch holds the remainder
    public static IEnumerable<Quote[]> ExportBatches(IEnumerable<Quote> quotes, int size = 100) =>
        quotes.Chunk(size);
    #endregion

    #region summary
    // C# port of Aggregate: one pass, three reads
    public static Summary Summarise(IEnumerable<Quote> quotes)
    {
        var amounts = quotes
            .Where(q => q.IsAccepted)
            .Select(q => q.Total.Amount)
            .ToList();
        return (amounts.Count, amounts.Sum(), amounts.Max());
    }
    #endregion

    #region window
    // C# port of Distinct, Skip While and Take While
    public static IEnumerable<string> Makes(
        IEnumerable<Quote> quotes) =>
        quotes.Select(q => q.Vehicle.Make).Distinct().Order();

    public static IEnumerable<Priced> Window(
        IEnumerable<Quote> quotes, decimal lo, decimal hi) =>
        quotes
            .OrderBy(q => q.Total.Amount)
            .SkipWhile(q => q.Total.Amount < lo)
            .TakeWhile(q => q.Total.Amount < hi)
            .Select(q => (q.QuoteId, q.Total.Amount));
    #endregion
}
