Imports System.Globalization

Public Module Program

    Private ReadOnly StartDate As New DateOnly(2026, 1, 1)

#Region "Generator"
    ' Deterministic and identical to QuoteBatch.Request in the C# twin.
    Public Function MakeRequest(i As Integer) As QuoteRequest
        Dim age = 19 + (i * 7) Mod 41
        Dim claims = If(i Mod 61 = 47, 3, If(i Mod 4 = 1, 1, If(i Mod 9 = 4, 2, 0)))
        Dim use = If(i Mod 6 = 3, VehicleUse.Commercial, VehicleUse.Private)
        Dim vehicle As New Vehicle($"Make{i Mod 5}", $"Model{i Mod 7}", 1200 + (i * 130) Mod 3400, use,
                                   Money.Thb(250000 + (i Mod 37) * 15000))
        Dim driver As New Driver(StartDate.AddYears(-age).AddDays(-(i Mod 300)),
                                 Math.Min(age - 18, (i * 3) Mod 12), claims)
        Return New QuoteRequest(vehicle, driver, CType(i Mod 4, CoverageClass), StartDate)
    End Function
#End Region

    Public Sub Main(args As String())
        CultureInfo.CurrentCulture = CultureInfo.InvariantCulture
        Const batchSize = 240
        Console.WriteLine("MotorQuote DebugLab (Visual Basic twin) — illustrative tariff, not a real one")

        Dim example As New QuoteRequest(
            New Vehicle("Make0", "Model0", 1500, VehicleUse.Private, Money.Thb(550000)),
            New Driver(New DateOnly(2002, 6, 15), 4, 0), CoverageClass.Class1, StartDate)
        Dim p = QuoteCalculator.Price(example)
        Console.WriteLine($"worked example: net {p.Net.Amount:F2} · stamp duty {p.StampDuty.Amount:F2}" &
                          $" · VAT {p.Vat.Amount:F2} · total {p.Total.Amount:F2} THB")

#Region "BatchLoop"
        Dim priced As New List(Of Premium)
        Dim declined As New List(Of Integer)
        For i = 0 To batchSize - 1
            Try
                priced.Add(QuoteCalculator.Price(MakeRequest(i)))
            Catch ex As QuoteDeclinedException
                declined.Add(i)
            End Try
        Next
#End Region

        Console.WriteLine($"batch of {batchSize} quotes: {priced.Count} quoted, {declined.Count} declined")
        Console.WriteLine($"declined at index: {String.Join(", ", declined)}")
        Console.WriteLine($"gross premium of the quoted policies: {QuoteCalculator.GrossTotal(priced):F2} THB")
    End Sub

End Module
