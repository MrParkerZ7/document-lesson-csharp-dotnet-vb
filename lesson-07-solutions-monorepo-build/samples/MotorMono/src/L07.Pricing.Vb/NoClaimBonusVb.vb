Imports L07.Core

#Region "ncb-rule"
''' <summary>The original rule, still in Visual Basic,
''' in the same build graph as its C# port.</summary>
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

        Dim years = Math.Clamp(request.ClaimFreeYears, 0, 5)
        Return -0.1D * years
    End Function
End Class
#End Region
