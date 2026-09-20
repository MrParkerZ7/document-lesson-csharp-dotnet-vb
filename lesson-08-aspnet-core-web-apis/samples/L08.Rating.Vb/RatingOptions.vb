Imports System.ComponentModel.DataAnnotations

''' <summary>
''' Bound from the "Rating" configuration section. These are the track's canonical illustrative rates
''' (_curriculum.md, "Canonical tariff"), not a real tariff: stamp duty 0.4% of the net premium,
''' VAT 7% on net + duty, every amount rounded to the satang away from zero.
''' </summary>
Public NotInheritable Class RatingOptions
    Public Const SectionName As String = "Rating"

    <Range(0.001, 0.1)> Public Property Class1Rate As Decimal = 0.021D
    <Range(0.001, 0.1)> Public Property Class2PlusRate As Decimal = 0.012D
    <Range(0.001, 0.1)> Public Property Class3PlusRate As Decimal = 0.009D
    <Range(0.001, 0.1)> Public Property Class3Rate As Decimal = 0.004D

    <Range(0.0, 1.0)> Public Property YoungDriverLoading As Decimal = 0.2D
    <Range(0.0, 1.0)> Public Property CommercialLoading As Decimal = 0.25D
    <Range(0.0, 1.0)> Public Property LargeEngineLoading As Decimal = 0.35D
    <Range(1000, 10000)> Public Property LargeEngineCc As Integer = 3000

    ' Two ladders, indexed by claims and by claim-free licence years. Past the claims ladder the quote
    ' is declined. They stay in code; appsettings.json overrides only the scalar rates.
    <MinLength(1)> Public Property ClaimLoadings As Decimal() = {0D, 0.1D, 0.25D}
    <MinLength(1)> Public Property NoClaimDiscounts As Decimal() = {0D, 0.2D, 0.25D, 0.3D, 0.4D, 0.5D}

    <Range(0.0, 0.1)> Public Property StampDutyRate As Decimal = 0.004D
    <Range(0.0, 0.5)> Public Property VatRate As Decimal = 0.07D
End Class
