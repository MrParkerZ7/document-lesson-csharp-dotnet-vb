using System.Diagnostics;

namespace L13.DebugLab;

public static class QuoteCalculator
{
    #region Price
    public static Premium Price(QuoteRequest request)
    {
        var vehicle = request.Vehicle;
        if (vehicle.SumInsured.Amount <= 0)
            throw new ArgumentException("sum insured must be positive", nameof(request));
        if (Tariff.AgeOn(request.Driver.DateOfBirth, request.StartDate) < 18)
            throw new ArgumentException("driver must be at least 18", nameof(request));

        var basePremium = vehicle.SumInsured.Amount * Tariff.Rate(request.Coverage);
        var loading = Tariff.YoungDriverLoading(request.Driver, request.StartDate)
                    + Tariff.ClaimsLoading(request.Driver.ClaimsLast5Years)
                    + Tariff.CommercialLoading(vehicle);
        var discount = Tariff.NoClaimDiscount(request.Driver);

        var net = Tariff.Satang(basePremium * (1 + loading) * (1 - discount));
        var duty = Tariff.Satang(net * 0.004m);
        var vat = Tariff.Satang((net + duty) * 0.07m);
        var total = net + duty + vat;

        // Compiled out of Release builds: the check costs nothing in production.
        Debug.Assert(total == net + duty + vat, "total must equal net + duty + VAT");
        Debug.Assert(net > 0, "a priced quote has a positive net premium");
        DebugTrace($"priced {request.Coverage}: net {net}, total {total}");

        return new Premium(Money.Thb(basePremium), loading, discount, Money.Thb(net),
                           Money.Thb(duty), Money.Thb(vat), Money.Thb(total));
    }
    #endregion

    // A [Conditional] method and every call to it disappear when DEBUG is not defined.
    [Conditional("DEBUG")]
    private static void DebugTrace(string message) => Debug.WriteLine(message);
}
