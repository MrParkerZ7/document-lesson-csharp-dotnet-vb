using System.Text;
using L13.DebugLab;

namespace L13.PerfLab;

/// <summary>One report routine three ways. Each returns the same text; only the allocations differ.</summary>
public static class Report
{
    // Counts the calls of one measured pass (Program.cs resets it after the warm-up pass), so it is not a
    // profiler total: a profiler over the whole run also counts the warm-up pass.
    public static int PriceCalls;

    private static Premium Price(QuoteRequest request)
    {
        PriceCalls++;
        return QuoteCalculator.Price(request);
    }

    // The floor: pricing alone, no report. Everything above this line is the report's own cost.
    public static string PricingOnly(IReadOnlyList<QuoteRequest> requests)
    {
        foreach (var request in requests) Price(request);
        return "";
    }

    #region HeavyVersion
    // Allocates on every line: a closure, boxed arguments for string.Format, a formatted string per
    // line, a List<string>, and the Join. It also prices every quote twice.
    public static string Heavy(IReadOnlyList<QuoteRequest> requests) =>
        string.Join("\n", requests
            .Select((r, i) => string.Format("{0},{1},{2},{3}", i, r.Coverage,
                Price(r).Net.Amount, Price(r).Total.Amount))
            .ToList());
    #endregion

    #region BuilderVersion
    public static string Builder(IReadOnlyList<QuoteRequest> requests)
    {
        var sb = new StringBuilder();
        for (var i = 0; i < requests.Count; i++)
        {
            var p = Price(requests[i]);
            if (i > 0) sb.Append('\n');
            sb.Append(i).Append(',').Append(requests[i].Coverage).Append(',')
              .Append(p.Net.Amount).Append(',').Append(p.Total.Amount);
        }
        return sb.ToString();
    }
    #endregion

    #region PresizedVersion
    private static readonly string[] CoverageNames = Enum.GetNames<CoverageClass>();

    // Prices once, reuses the enum names, and reserves the builder's capacity up front.
    public static string Presized(IReadOnlyList<QuoteRequest> requests)
    {
        var sb = new StringBuilder(requests.Count * 36);
        for (var i = 0; i < requests.Count; i++)
        {
            var p = Price(requests[i]);
            if (i > 0) sb.Append('\n');
            sb.Append(i).Append(',').Append(CoverageNames[(int)requests[i].Coverage]).Append(',')
              .Append(p.Net.Amount).Append(',').Append(p.Total.Amount);
        }
        return sb.ToString();
    }
    #endregion
}
