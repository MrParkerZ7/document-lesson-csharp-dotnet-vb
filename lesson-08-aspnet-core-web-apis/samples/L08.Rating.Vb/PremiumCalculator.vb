Imports Microsoft.Extensions.Options

''' <summary>The MotorQuote rating rules. All rates are illustrative, not a real tariff.</summary>
Public NotInheritable Class PremiumCalculator
    Private ReadOnly _rates As RatingOptions

    Public Sub New(options As IOptions(Of RatingOptions))
        _rates = options.Value
    End Sub

#Region "calculate"
    Public Function Calculate(input As RatingInput) As PremiumBreakdown
        Dim basePremium = input.SumInsured * BaseRateFor(input.Coverage)

        Dim loading = 0D
        If input.DriverAge < 25 Then loading += _rates.YoungDriverLoading
        loading += input.ClaimsLast5Years * _rates.ClaimLoading
        If input.Use = VehicleUse.Commercial Then loading += _rates.CommercialLoading

        Dim claimFreeYears = If(input.ClaimsLast5Years = 0, Math.Min(input.LicenceYears, 5), 0)
        Dim discount = claimFreeYears * _rates.NcbPerClaimFreeYear

        Dim net = RoundBaht(basePremium * (1D + loading) * (1D - discount))
        Dim duty = RoundBaht(net * _rates.StampDutyRate)
        Dim vat = RoundBaht((net + duty) * _rates.VatRate)
        Return New PremiumBreakdown(RoundBaht(basePremium), loading, discount, net, duty, vat)
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
