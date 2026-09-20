' MotorQuote rating rules: the one illustrative tariff of the whole track
' (curriculum, "Canonical tariff"). ILLUSTRATIVE rates only — not a real motor tariff.

Public Enum CoverageClass
    Class1       ' comprehensive
    Class2Plus
    Class3Plus
    Class3       ' third-party only
End Enum

''' <summary>Net premium, stamp duty, VAT and total, in THB.</summary>
Public Structure PremiumBreakdown
    Public ReadOnly Property Net As Decimal
    Public ReadOnly Property StampDuty As Decimal
    Public ReadOnly Property Vat As Decimal
    Public ReadOnly Property Total As Decimal

    Public Sub New(net As Decimal, stampDuty As Decimal, vat As Decimal)
        Me.Net = net
        Me.StampDuty = stampDuty
        Me.Vat = vat
        Total = net + stampDuty + vat
    End Sub
End Structure

''' <summary>
''' Three or more claims in five years: the quote is declined. A domain outcome, not a crash,
''' so every host answers it with HTTP 422. (Exceptions are lesson 02's subject, not this one's.)
''' </summary>
Public NotInheritable Class QuoteDeclinedException
    Inherits Exception

    Public Sub New()
        MyBase.New("declined: 3 or more claims in the last 5 years")
    End Sub
End Class

Public Module Rating
#Region "rating"
    ' A Module compiles to a static class: C# calls Rating.Quote(...).
    ' driverAge is the driver's age on the quote start date.
    Public Function Quote(coverage As CoverageClass, sumInsured As Decimal,
                          driverAge As Integer, licenceYears As Integer,
                          claimsLast5Years As Integer, commercial As Boolean,
                          engineCc As Integer) As PremiumBreakdown
        If claimsLast5Years >= 3 Then Throw New QuoteDeclinedException()

        Dim rate As Decimal
        Select Case coverage
            Case CoverageClass.Class1 : rate = 0.021D
            Case CoverageClass.Class2Plus : rate = 0.012D
            Case CoverageClass.Class3Plus : rate = 0.009D
            Case Else : rate = 0.004D
        End Select

        ' loadings add up, then apply to the base premium
        Dim loadings = 0D
        If driverAge < 25 Then loadings += 0.2D
        If claimsLast5Years = 1 Then loadings += 0.1D
        If claimsLast5Years = 2 Then loadings += 0.25D
        If commercial Then loadings += If(engineCc > 3000, 0.35D, 0.25D)

        ' the no-claim ladder counts claim-free licence years
        Dim claimFree = If(claimsLast5Years = 0, licenceYears, 0)
        Dim discount As Decimal
        Select Case claimFree
            Case Is <= 0 : discount = 0D
            Case 1 : discount = 0.2D
            Case 2 : discount = 0.25D
            Case 3 : discount = 0.3D
            Case 4 : discount = 0.4D
            Case Else : discount = 0.5D
        End Select

        Dim net = Satang(sumInsured * rate * (1D + loadings) * (1D - discount))
        Dim duty = Satang(net * 0.004D)
        Dim vat = Satang((net + duty) * 0.07D)
        Return New PremiumBreakdown(net, duty, vat)
    End Function

    ' the satang: 2 decimals, halves round away from zero
    Private Function Satang(amount As Decimal) As Decimal
        Return Math.Round(amount, 2, MidpointRounding.AwayFromZero)
    End Function
#End Region
End Module
