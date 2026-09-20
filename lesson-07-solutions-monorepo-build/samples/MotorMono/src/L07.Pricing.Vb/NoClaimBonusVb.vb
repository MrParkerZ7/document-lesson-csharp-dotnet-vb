Imports L07.Core

#Region "ncb-rule"
''' <summary>The original rule, still in Visual Basic,
''' the same ladder, in the same build graph.</summary>
Public NotInheritable Class NoClaimBonusVb
    Implements IRatingRule

    Public ReadOnly Property Name As String _
        Implements IRatingRule.Name
        Get
            Return "no-claim bonus"
        End Get
    End Property

    Public Function Factor(request As QuoteRequest) _
        As Decimal Implements IRatingRule.Factor
        ArgumentNullException.ThrowIfNull(request)
        If request.ClaimsLast5Years > 0 Then Return 0D

        Select Case request.ClaimFreeYears
            Case Is <= 0 : Return 0D
            Case 1 : Return -0.2D
            Case 2 : Return -0.25D
            Case 3 : Return -0.3D
            Case 4 : Return -0.4D
            Case Else : Return -0.5D
        End Select
    End Function
End Class
#End Region
