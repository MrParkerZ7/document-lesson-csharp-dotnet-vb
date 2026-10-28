Imports System.Diagnostics

' The canonical MotorQuote tariff — illustrative, not a real tariff. Same numbers as the C# twin.
Public Module Tariff

#Region "ClassRate"
    Public Function Rate(coverage As CoverageClass) As Decimal
        Select Case coverage
            Case CoverageClass.Class1 : Return 0.021D
            Case CoverageClass.Class2Plus : Return 0.012D
            Case CoverageClass.Class3Plus : Return 0.009D
            Case CoverageClass.Class3 : Return 0.004D
            Case Else : Throw New ArgumentOutOfRangeException(NameOf(coverage))
        End Select
    End Function
#End Region

#Region "ClaimsLoading"
    ' Exception Settings work the same for VB: tick L13.DebugLabVb.QuoteDeclinedException.
    Public Function ClaimsLoading(claims As Integer) As Decimal
        Select Case claims
            Case Is < 0 : Throw New ArgumentOutOfRangeException(NameOf(claims))
            Case 0 : Return 0D
            Case 1 : Return 0.1D
            Case 2 : Return 0.25D
            Case Else : Throw New QuoteDeclinedException("3+ claims in 5 years")
        End Select
    End Function
#End Region

    Public Function YoungDriverLoading(driver As Driver, start As DateOnly) As Decimal
        Return If(AgeOn(driver.DateOfBirth, start) < 25, 0.2D, 0D)
    End Function

    Public Function CommercialLoading(vehicle As Vehicle) As Decimal
        If vehicle.Use = VehicleUse.Private Then Return 0D
        Return If(vehicle.EngineCc > 3000, 0.35D, 0.25D)
    End Function

    Public Function NoClaimDiscount(driver As Driver) As Decimal
        Dim claimFreeYears = If(driver.ClaimsLast5Years = 0, driver.LicenceYears, 0)
        Select Case claimFreeYears
            Case 0 : Return 0D
            Case 1 : Return 0.2D
            Case 2 : Return 0.25D
            Case 3 : Return 0.3D
            Case 4 : Return 0.4D
            Case Else : Return 0.5D
        End Select
    End Function

    Public Function AgeOn(dateOfBirth As DateOnly, day As DateOnly) As Integer
        Dim age = day.Year - dateOfBirth.Year
        Return If(dateOfBirth.AddYears(age) > day, age - 1, age)
    End Function

#Region "StepThrough"
    <DebuggerStepThrough>
    Public Function Satang(value As Decimal) As Decimal
        Return Math.Round(value, 2, MidpointRounding.AwayFromZero)
    End Function
#End Region

End Module
