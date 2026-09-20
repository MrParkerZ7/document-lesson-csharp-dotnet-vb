Option Strict Off
Option Compare Text

' MotorQuote rating written the way many 2000s VB.NET estates were:
' loose file options, Double rates, a magic -1 for "declined" and
' Microsoft.VisualBasic helpers. The tariff VALUES are the track's
' canonical illustrative tariff (curriculum, "Canonical tariff");
' the whole-baht Integer rounding is this legacy code's own habit,
' kept on purpose - it is what the port must reproduce.
Public Module LegacyPremium

#Region "legacy-cover"
    Public Function CalcPremium(ByVal coverCode As String,
            ByVal sumInsured As Decimal, ByVal dateOfBirth As Date,
            ByVal startDate As Date, ByVal licenceMonths As Integer,
            ByVal claims As Integer,
            Optional ByVal commercial As Boolean = False,
            Optional ByVal engineCc As Integer = 1500,
            Optional ByRef declineReason As String = "") As Decimal
        Dim rate As Double
        Select Case coverCode.Trim()    ' Option Compare Text: "class1" matches
            Case "CLASS1" : rate = 0.021
            Case "CLASS2PLUS" : rate = 0.012
            Case "CLASS3PLUS" : rate = 0.009
            Case "CLASS3" : rate = 0.004
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
        If age < 25 Then loading += CInt(base * 0.2)
        Select Case claims
            Case 0
            Case 1 : loading += CInt(base * 0.1)
            Case 2 : loading += CInt(base * 0.25)
            Case Else
                declineReason = "3+ claims in 5 years"
                Return -1
        End Select
        If commercial Then
            loading += CInt(base * If(engineCc > 3000, 0.35, 0.25))
        End If
#End Region

#Region "legacy-discount-total"
        Dim claimFreeYears As Integer =
            If(claims = 0, licenceYears, 0)
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
        Dim duty As Integer = CInt(net * 0.004)
        Dim vat As Decimal = Math.Round((net + duty) * 0.07D)
        Return net + duty + vat
#End Region
    End Function

End Module
