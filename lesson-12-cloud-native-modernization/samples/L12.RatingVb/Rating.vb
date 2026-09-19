' MotorQuote rating rules. ILLUSTRATIVE rates only — not a real motor tariff.

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

Public Module Rating
#Region "rating"
    ' A Module compiles to a static class: C# calls Rating.Quote(...)
    Public Function Quote(coverage As CoverageClass, sumInsured As Decimal,
                          driverAge As Integer, claimsLast5Years As Integer,
                          commercial As Boolean) As PremiumBreakdown
        Dim rate As Decimal
        Select Case coverage
            Case CoverageClass.Class1 : rate = 0.021D
            Case CoverageClass.Class2Plus : rate = 0.014D
            Case CoverageClass.Class3Plus : rate = 0.011D
            Case Else : rate = 0.006D
        End Select

        Dim net = sumInsured * rate
        If driverAge < 25 Then net *= 1.2D                  ' young-driver loading
        net *= 1D + 0.1D * Math.Min(claimsLast5Years, 3)    ' claims loading
        If claimsLast5Years = 0 Then net *= 0.9D            ' no-claim bonus
        If commercial Then net *= 1.15D                     ' commercial use

        net = Math.Round(net, 2, MidpointRounding.AwayFromZero)
        Dim duty = Math.Round(net * 0.004D, 2, MidpointRounding.AwayFromZero)
        Dim vat = Math.Round((net + duty) * 0.07D, 2, MidpointRounding.AwayFromZero)
        Return New PremiumBreakdown(net, duty, vat)
    End Function
#End Region
End Module
