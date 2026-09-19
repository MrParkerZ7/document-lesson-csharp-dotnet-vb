using System.Diagnostics.CodeAnalysis;
using static L02.Rating.RatingRules;   // static import (C# 6): call rules without the class name

namespace L02.Rating;

public static class PremiumCalculator
{
    #region calculate
    public static Premium Calculate(QuoteRequest request)
    {
        ArgumentNullException.ThrowIfNull(request);
        var (vehicle, driver, coverage, start) = request;   // positional deconstruction

        decimal basePremium = Round(BaseRate(coverage, vehicle.SumInsured));
        decimal loadingRate = AgeLoading(driver.AgeOn(start))
                            + ClaimsLoading(driver.ClaimsLast5Years)
                            + UseLoading(vehicle);
        decimal loadings = Round(basePremium * loadingRate);
        decimal discount = Round((basePremium + loadings) * NoClaimBonus(driver));
        decimal net = basePremium + loadings - discount;
        decimal stampDuty = Round(net * StampDutyRate);        // 0.4% of net
        decimal vat = Round((net + stampDuty) * VatRate);      // 7% of net + duty

        return new Premium(basePremium, loadings, discount, net,
                           stampDuty, vat, net + stampDuty + vat);
    }
    #endregion

    #region try-calculate
    // The Try pattern: a bool result plus out parameters. The attributes tell
    // the compiler which out value is non-null for each result.
    public static bool TryCalculate(
        QuoteRequest request,
        [NotNullWhen(true)] out Premium? premium,
        [NotNullWhen(false)] out string? declineReason)
    {
        try
        {
            premium = Calculate(request);
            declineReason = null;
            return true;
        }
        catch (QuoteDeclinedException e)
        {
            (premium, declineReason) = (null, e.Reason);
            return false;
        }
    }
    #endregion
}
