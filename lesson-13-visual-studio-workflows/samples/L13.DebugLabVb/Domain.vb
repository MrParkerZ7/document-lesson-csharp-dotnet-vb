Imports System.Diagnostics

Public Enum CoverageClass
    Class1
    Class2Plus
    Class3Plus
    Class3
End Enum

Public Enum VehicleUse
    [Private]
    Commercial
End Enum

#Region "MoneyDisplay"
' The attribute is identical to C#'s. The type around it is
' longer: Visual Basic has no record struct.
<DebuggerDisplay("{Amount} {Currency,nq}")>
Public Structure Money
    Public ReadOnly Property Amount As Decimal
    Public ReadOnly Property Currency As String

    Public Sub New(amount As Decimal, currency As String)
        Me.Amount = amount
        Me.Currency = currency
    End Sub

    Public Shared Function Thb(amount As Decimal) As Money
        Return New Money(amount, "THB")
    End Function
End Structure
#End Region

Public NotInheritable Class Vehicle
    Public ReadOnly Property Make As String
    Public ReadOnly Property Model As String
    Public ReadOnly Property EngineCc As Integer
    Public ReadOnly Property Use As VehicleUse
    Public ReadOnly Property SumInsured As Money

    Public Sub New(make As String, model As String, engineCc As Integer, use As VehicleUse, sumInsured As Money)
        Me.Make = make
        Me.Model = model
        Me.EngineCc = engineCc
        Me.Use = use
        Me.SumInsured = sumInsured
    End Sub
End Class

Public NotInheritable Class Driver
    Public ReadOnly Property DateOfBirth As DateOnly
    Public ReadOnly Property LicenceYears As Integer
    Public ReadOnly Property ClaimsLast5Years As Integer

    Public Sub New(dateOfBirth As DateOnly, licenceYears As Integer, claimsLast5Years As Integer)
        Me.DateOfBirth = dateOfBirth
        Me.LicenceYears = licenceYears
        Me.ClaimsLast5Years = claimsLast5Years
    End Sub
End Class

<DebuggerDisplay("{Coverage} · {Vehicle.Make} · sum {Vehicle.SumInsured}")>
Public NotInheritable Class QuoteRequest
    Public ReadOnly Property Vehicle As Vehicle
    Public ReadOnly Property Driver As Driver
    Public ReadOnly Property Coverage As CoverageClass
    Public ReadOnly Property StartDate As DateOnly

    Public Sub New(vehicle As Vehicle, driver As Driver, coverage As CoverageClass, startDate As DateOnly)
        Me.Vehicle = vehicle
        Me.Driver = driver
        Me.Coverage = coverage
        Me.StartDate = startDate
    End Sub
End Class

<DebuggerDisplay("net {Net} · total {Total}")>
Public NotInheritable Class Premium
    Public ReadOnly Property LoadingRate As Decimal
    Public ReadOnly Property DiscountRate As Decimal
    Public ReadOnly Property Net As Money
    Public ReadOnly Property StampDuty As Money
    Public ReadOnly Property Vat As Money
    Public ReadOnly Property Total As Money

    Public Sub New(loadingRate As Decimal, discountRate As Decimal, net As Money,
                   stampDuty As Money, vat As Money, total As Money)
        Me.LoadingRate = loadingRate
        Me.DiscountRate = discountRate
        Me.Net = net
        Me.StampDuty = stampDuty
        Me.Vat = vat
        Me.Total = total
    End Sub
End Class

''' <summary>A domain outcome, not a crash: the tariff declines 3 or more claims in 5 years.</summary>
Public NotInheritable Class QuoteDeclinedException
    Inherits Exception

    Public Sub New(reason As String)
        MyBase.New(reason)
    End Sub
End Class
