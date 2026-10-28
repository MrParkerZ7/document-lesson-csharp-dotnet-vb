Imports System.Diagnostics

Public Module QuoteCalculator

#Region "Price"
    Public Function Price(request As QuoteRequest) As Premium
        Dim vehicle = request.Vehicle
        If vehicle.SumInsured.Amount <= 0 Then
            Throw New ArgumentException("sum insured must be positive", NameOf(request))
        End If
        If Tariff.AgeOn(request.Driver.DateOfBirth, request.StartDate) < 18 Then
            Throw New ArgumentException("driver must be at least 18", NameOf(request))
        End If

        Dim basePremium = vehicle.SumInsured.Amount * Tariff.Rate(request.Coverage)
        Dim loading = Tariff.YoungDriverLoading(request.Driver, request.StartDate) +
                      Tariff.ClaimsLoading(request.Driver.ClaimsLast5Years) +
                      Tariff.CommercialLoading(vehicle)
        Dim discount = Tariff.NoClaimDiscount(request.Driver)

        Dim net = Tariff.Satang(basePremium * (1 + loading) * (1 - discount))
        Dim duty = Tariff.Satang(net * 0.004D)
        Dim vat = Tariff.Satang((net + duty) * 0.07D)
        Dim total = net + duty + vat

        ' Debug.Assert is <Conditional("DEBUG")>: the call vanishes from a Release build.
        Debug.Assert(total = net + duty + vat, "total must equal net + duty + VAT")
#If DEBUG Then
        Debug.WriteLine($"priced {request.Coverage}: net {net}, total {total}")
#End If

        Return New Premium(loading, discount, Money.Thb(net), Money.Thb(duty), Money.Thb(vat), Money.Thb(total))
    End Function
#End Region

#Region "AggregateLimit"
    ' Visual Basic only: Hot Reload and Edit and Continue cannot apply an edit to a member that
    ' contains an Aggregate, Group By or Join clause. Edit it in a stopped session instead.
    Public Function GrossTotal(premiums As IEnumerable(Of Premium)) As Decimal
        Return Aggregate p In premiums Into Sum(p.Total.Amount)
    End Function
#End Region

End Module
