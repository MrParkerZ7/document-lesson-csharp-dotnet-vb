Imports Microsoft.Extensions.Options

''' <summary>The MotorQuote rating rules — the track's canonical illustrative tariff, not a real one.</summary>
Public NotInheritable Class PremiumCalculator
    Private ReadOnly _rates As RatingOptions

    Public Sub New(options As IOptions(Of RatingOptions))
        _rates = options.Value
    End Sub

#Region "calculate"
    Public Function Calculate(input As RatingInput) As PremiumBreakdown
        ' Past the last rung of the claims ladder the tariff declines the quote instead of pricing it.
        If input.ClaimsLast5Years >= _rates.ClaimLoadings.Length Then
            Return PremiumBreakdown.Declined(
                $"{_rates.ClaimLoadings.Length}+ claims in 5 years")
        End If

        Dim basePremium = input.SumInsured * BaseRateFor(input.Coverage)

        Dim loading = _rates.ClaimLoadings(input.ClaimsLast5Years)
        If input.DriverAge < 25 Then loading += _rates.YoungDriverLoading
        If input.Use = VehicleUse.Commercial Then
            loading += If(input.EngineCc > _rates.LargeEngineCc,
                          _rates.LargeEngineLoading, _rates.CommercialLoading)
        End If

        Dim discount = NoClaimDiscountFor(input)
        Dim net = RoundBaht(basePremium * (1D + loading) * (1D - discount))
        Dim duty = RoundBaht(net * _rates.StampDutyRate)
        Dim vat = RoundBaht((net + duty) * _rates.VatRate)
        Return New PremiumBreakdown(RoundBaht(basePremium), loading, discount, net, duty, vat)
    End Function

    ' The no-claim ladder rewards claim-free licence years; its last rung covers 5 years and more.
    Private Function NoClaimDiscountFor(input As RatingInput) As Decimal
        If input.ClaimsLast5Years > 0 Then Return 0D
        Return _rates.NoClaimDiscounts(
            Math.Min(input.LicenceYears, _rates.NoClaimDiscounts.Length - 1))
    End Function

    ' Math.Round defaults to banker's rounding (half to even): money needs AwayFromZero.
    Private Shared Function RoundBaht(amount As Decimal) As Decimal
        Return Math.Round(amount, 2, MidpointRounding.AwayFromZero)
    End Function
#End Region

    Public Function BaseRateFor(coverage As CoverageClass) As Decimal
        Select Case coverage
            Case CoverageClass.Class1 : Return _rates.Class1Rate
            Case CoverageClass.Class2Plus : Return _rates.Class2PlusRate
            Case CoverageClass.Class3Plus : Return _rates.Class3PlusRate
            Case Else : Return _rates.Class3Rate
        End Select
    End Function
End Class
