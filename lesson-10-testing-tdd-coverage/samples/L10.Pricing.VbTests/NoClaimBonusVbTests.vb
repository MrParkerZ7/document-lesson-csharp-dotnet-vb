Imports L10.Pricing
Imports Xunit

Namespace L10.Pricing.VbTests

    ' The same no-claim-bonus rule, tested from Visual Basic against the C# library.
    Public Class NoClaimBonusVbTests

#Region "vb-theory"
        Public Shared ReadOnly Property Table As _
            New TheoryData(Of Integer, Decimal) From {
                {1, 0.2D}, {2, 0.25D}, {3, 0.3D},
                {4, 0.4D}, {5, 0.5D}, {9, 0.5D}
            }

        <Theory>
        <MemberData(NameOf(Table))>
        Public Sub Discount_grows_with_claim_free_years(
                years As Integer, expected As Decimal)
            Dim discount = NoClaimBonus.DiscountFor(years)

            Assert.Equal(expected, discount)
        End Sub
#End Region

#Region "vb-throws"
        <Fact>
        Public Sub Negative_years_are_rejected()
            Dim ex = Assert.Throws(Of ArgumentOutOfRangeException)(
                Function() NoClaimBonus.DiscountFor(-1))

            Assert.Equal("claimFreeYears", ex.ParamName)
        End Sub
#End Region

    End Class

End Namespace
