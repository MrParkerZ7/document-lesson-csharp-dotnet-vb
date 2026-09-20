using L06.LegacyRating;
using L06.ModernRating;

namespace L06.Parity;

public static class LegacyAdapter
{
    #region call-vb
    // A VB Module's members are static members to C#. An Optional
    // ByVal parameter stays optional; Optional ByRef arrives as a
    // required ref, so declineReason is always passed.
    public static decimal? Quote(QuoteRequest r, out string reason)
    {
        string declineReason = "";
        decimal premium = LegacyPremium.CalcPremium(
            r.CoverCode, r.SumInsured,
            r.DateOfBirth.ToDateTime(TimeOnly.MinValue),
            r.StartDate.ToDateTime(TimeOnly.MinValue),
            r.LicenceMonths, r.Claims,
            commercial: r.Commercial, engineCc: r.EngineCc,
            declineReason: ref declineReason);
        reason = declineReason;
        return premium == -1 ? null : premium;   // -1 meant "declined"
    }
    #endregion
}
