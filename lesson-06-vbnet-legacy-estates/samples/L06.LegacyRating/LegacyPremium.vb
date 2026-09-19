Option Strict Off
Option Compare Text

' MotorQuote rating written the way many 2000s VB.NET estates were:
' loose file options, Double rates, a magic -1 for "declined" and
' Microsoft.VisualBasic helpers. Rates are illustrative, not a tariff.
Public Module LegacyPremium

#Region "legacy-cover"
    Public Function CalcPremium(ByVal coverCode As String,
            ByVal sumInsured As Decimal, ByVal dateOfBirth As Date,
            ByVal startDate As Date, ByVal licenceMonths As Integer,
            ByVal claimFreeYears As Integer, ByVal claims As Integer,
            Optional ByVal commercial As Boolean = False,
            Optional ByRef declineReason As String = "") As Decimal
        Dim rate As Double
        Select Case coverCode.Trim()    ' Option Compare Text: "class1" matches
            Case "CLASS1" : rate = 0.0185
            Case "CLASS2PLUS" : rate = 0.012
            Case "CLASS3PLUS" : rate = 0.0095
            Case "CLASS3" : rate = 0.0065
            Case Else
                declineReason = "unknown cover " & coverCode
                Return -1
        End Select
        Dim base As Integer = sumInsured * rate    ' Double -> Integer rounds
#End Region

#Region "legacy-loadings"
        Dim age As Integer = DateDiff(DateInterval.Year,
                                      dateOfBirth, startDate)
        Dim licenceYears As Integer = licenceMonths / 12

        Dim loading As Integer = 0
        If age < 25 Then loading += CInt(base * 0.25)
        If licenceYears < 2 Then loading += CInt(base * 0.1)
        loading += CInt(base * 0.2 * claims)
        If commercial Then loading += CInt(base * 0.3)
#End Region

#Region "legacy-discount-total"
        Dim ncb(5) As Decimal    ' six slots: 0 to 5 claim-free years
        ncb(1) = 0.2
        ncb(2) = 0.25
        ncb(3) = 0.3
        ncb(4) = 0.4
        ncb(5) = 0.5
        If claimFreeYears > 5 Then claimFreeYears = 5
        Dim discount As Integer =
            (base + loading) * ncb(claimFreeYears)

        Dim net As Integer = base + loading - discount
        If net < 1000 Then net = 1000
        Dim duty As Integer = CInt(net * 0.004)
        Dim vat As Decimal = Math.Round((net + duty) * 0.07D)
        Return net + duty + vat
#End Region
    End Function

End Module
