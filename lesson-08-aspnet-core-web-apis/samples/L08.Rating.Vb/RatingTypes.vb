''' <summary>Thai motor classes: 1 = comprehensive ... 3 = third-party only.</summary>
Public Enum CoverageClass
    Class1
    Class2Plus
    Class3Plus
    Class3
End Enum

Public Enum VehicleUse
    [Private]   ' Private is a VB keyword: square brackets escape it
    Commercial
End Enum

''' <summary>What the rating engine needs. VB cannot declare a record, so this is a class.</summary>
Public NotInheritable Class RatingInput
    Public Sub New(coverage As CoverageClass, sumInsured As Decimal, driverAge As Integer,
                   licenceYears As Integer, claimsLast5Years As Integer, use As VehicleUse,
                   engineCc As Integer)
        Me.Coverage = coverage
        Me.SumInsured = sumInsured
        Me.DriverAge = driverAge
        Me.LicenceYears = licenceYears
        Me.ClaimsLast5Years = claimsLast5Years
        Me.Use = use
        Me.EngineCc = engineCc
    End Sub

    Public ReadOnly Property Coverage As CoverageClass
    Public ReadOnly Property SumInsured As Decimal
    Public ReadOnly Property DriverAge As Integer
    Public ReadOnly Property LicenceYears As Integer
    Public ReadOnly Property ClaimsLast5Years As Integer
    Public ReadOnly Property Use As VehicleUse
    Public ReadOnly Property EngineCc As Integer
End Class

''' <summary>The result of rating one request. Amounts in THB; rates are illustrative.</summary>
Public NotInheritable Class PremiumBreakdown
    Public Sub New(basePremium As Decimal, loadingRate As Decimal, discountRate As Decimal,
                   netPremium As Decimal, stampDuty As Decimal, vat As Decimal,
                   Optional declineReason As String = Nothing)
        Me.BasePremium = basePremium
        Me.LoadingRate = loadingRate
        Me.DiscountRate = discountRate
        Me.NetPremium = netPremium
        Me.StampDuty = stampDuty
        Me.Vat = vat
        Me.DeclineReason = declineReason
    End Sub

    ''' <summary>A declined quote is a domain outcome, not a crash: nothing is priced.</summary>
    Public Shared Function Declined(reason As String) As PremiumBreakdown
        Return New PremiumBreakdown(0D, 0D, 0D, 0D, 0D, 0D, reason)
    End Function

    Public ReadOnly Property DeclineReason As String

    Public ReadOnly Property IsDeclined As Boolean
        Get
            Return DeclineReason IsNot Nothing
        End Get
    End Property

    Public ReadOnly Property BasePremium As Decimal
    Public ReadOnly Property LoadingRate As Decimal
    Public ReadOnly Property DiscountRate As Decimal
    Public ReadOnly Property NetPremium As Decimal
    Public ReadOnly Property StampDuty As Decimal
    Public ReadOnly Property Vat As Decimal

    Public ReadOnly Property Total As Decimal
        Get
            Return NetPremium + StampDuty + Vat
        End Get
    End Property
End Class

''' <summary>One row of the published tariff, served by the VB endpoint.</summary>
Public NotInheritable Class TariffRow
    Public Sub New(coverage As CoverageClass, baseRate As Decimal)
        Me.Coverage = coverage
        Me.BaseRate = baseRate
    End Sub

    Public ReadOnly Property Coverage As CoverageClass
    Public ReadOnly Property BaseRate As Decimal
End Class
