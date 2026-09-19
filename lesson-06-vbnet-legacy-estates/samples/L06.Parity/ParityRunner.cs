using L06.ModernRating;

namespace L06.Parity;

public sealed record ParityResult(int Cases, int Mismatches, int Exceptions, string? FirstMismatch);

public static class ParityRunner
{
    static readonly Lazy<(QuoteRequest Request, decimal? Premium)[]> Legacy =
        new(() => QuoteGrid.All().Select(r => (r, LegacyAdapter.Quote(r, out _))).ToArray());

    #region parity-loop
    public static ParityResult Compare(Func<QuoteRequest, decimal?> port)
    {
        int mismatches = 0, exceptions = 0;
        string? first = null;
        foreach (var (request, legacy) in Legacy.Value)
        {
            string ported;
            try
            {
                decimal? premium = port(request);
                if (premium == legacy) continue;     // same number or both declined
                ported = premium?.ToString("0") ?? "declined";
            }
            catch (IndexOutOfRangeException)
            {
                exceptions++;
                ported = "IndexOutOfRangeException";
            }
            mismatches++;
            first ??= $"{Describe(request)}: legacy {legacy:0}, port {ported}";
        }
        return new ParityResult(Legacy.Value.Length, mismatches, exceptions, first);
    }
    #endregion

    public static string Describe(QuoteRequest r) =>
        $"{r.CoverCode} {r.SumInsured:0} born {r.DateOfBirth:yyyy-MM-dd} " +
        $"start {r.StartDate:yyyy-MM-dd} {r.LicenceMonths}m {r.ClaimFreeYears}ncb {r.Claims}cl" +
        (r.Commercial ? " com" : "");
}
