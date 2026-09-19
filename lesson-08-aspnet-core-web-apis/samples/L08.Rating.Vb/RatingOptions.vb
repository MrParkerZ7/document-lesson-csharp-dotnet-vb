Imports System.ComponentModel.DataAnnotations

''' <summary>
''' Bound from the "Rating" configuration section. Illustrative rates, not a real tariff:
''' stamp duty 0.4% of net premium, VAT 7% on net + duty.
''' </summary>
Public NotInheritable Class RatingOptions
    Public Const SectionName As String = "Rating"

    <Range(0.001, 0.1)> Public Property Class1Rate As Decimal = 0.025D
    <Range(0.001, 0.1)> Public Property Class2PlusRate As Decimal = 0.018D
    <Range(0.001, 0.1)> Public Property Class3PlusRate As Decimal = 0.012D
    <Range(0.001, 0.1)> Public Property Class3Rate As Decimal = 0.006D

    <Range(0.0, 1.0)> Public Property YoungDriverLoading As Decimal = 0.25D
    <Range(0.0, 1.0)> Public Property ClaimLoading As Decimal = 0.1D
    <Range(0.0, 1.0)> Public Property CommercialLoading As Decimal = 0.15D
    <Range(0.0, 0.1)> Public Property NcbPerClaimFreeYear As Decimal = 0.05D

    <Range(0.0, 0.1)> Public Property StampDutyRate As Decimal = 0.004D
    <Range(0.0, 0.5)> Public Property VatRate As Decimal = 0.07D
End Class
