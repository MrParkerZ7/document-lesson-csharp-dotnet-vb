Imports System.Globalization
Imports System.Text
Imports L03.Domain
Imports L03.Reports

Module Program
    Sub Main()
        ' one culture, so the output is the same on every machine
        CultureInfo.CurrentCulture = CultureInfo.InvariantCulture
        Console.WriteLine("L03.VbInterop - Visual Basic using the lesson-03 C# types")

#Region "vb-consume"
        ' C# records: construct, read and compare them
        Dim young = Samples.YoungDriver()
        Dim sameRequest = Samples.YoungDriver()
        Console.WriteLine($"records    equal? {young = sameRequest}")

        ' no `with` in VB: build the changed copy by hand
        Dim class3 = New QuoteRequest(young.Vehicle, young.Driver,
                                      CoverageClass.Class3, young.StartDate)
        Console.WriteLine($"copy       equal? {young = class3}")

        ' C# operators on a record struct
        Dim sum = Money.Thb(1000D) + Money.Thb(500D)
        Console.WriteLine($"operators  {sum}, same? {sum = Money.Thb(1500D)}")

        ' required + init members: set them inside With { } only
        Dim quote As New Quote With {
            .Id = New QuoteId(7),
            .Request = young,
            .Premium = Samples.Calculator().Calculate(young)}
        Console.WriteLine($"required   {quote.Id} total {quote.Premium.Total}")

        ' a C# 14 extension property has no VB syntax: call its method
        Dim code = CoverageClassExtensions.get_Code(CoverageClass.Class2Plus)
        Console.WriteLine($"extension  get_Code(Class2Plus) = {code}")
#End Region

        Dim loading As New YoungDriverLoading()
        Dim asBase As RatingRule = loading
        Console.WriteLine($"dispatch   {asBase.Factor(young)} | {asBase.Describe(young)} | {loading.Describe(young)}")

        Dim ids = ParseBoth(Of QuoteId)("Q-000042", "Q-000043")
        Console.WriteLine($"generics   {String.Join(", ", ids)}")

#Region "vb-render"
        Dim quotes = {Samples.Quote(42, Samples.YoungDriver()),
                      Samples.Quote(43, Samples.CommercialPickup())}
        Dim report = New QuoteReportSource(quotes, Samples.StartDate).Load()

        ' C# renderers and a VB renderer behind one C# contract
        Dim renderers As IReportRenderer(Of QuoteReport)() = {
            New CsvRenderer(), New VbCsvRenderer(),
            New TextTableRenderer(), New SummaryCardRenderer()}
        Dim service As New ReportService(Of QuoteReport)(renderers)

        Dim fromCs = service.Render(report, "csv")
        Dim fromVb = service.Render(report, "VB")
        Console.WriteLine($"same CSV from C# and VB? {fromCs = fromVb}")
        Console.WriteLine(service.Render(report, "text"))
#End Region
    End Sub

#Region "vb-generic"
    ' (Of T As constraint) is C#'s <T> where T : constraint
    Function ParseBoth(Of T As IIdentifier(Of T))(
            first As String, second As String) As List(Of T)
        Return Ids.ParseAll(Of T)(first, second)
    End Function
#End Region
End Module

#Region "vb-keywords"
' panel 4.1's C# hierarchy, keyword for keyword (L03.VbInterop.RatingRule)
Public MustInherit Class RatingRule                                   ' abstract
    Public MustOverride ReadOnly Property Name As String

    Public Overridable Function Factor(r As QuoteRequest) As Decimal  ' virtual
        Return 1.00D
    End Function

    Public Function Describe(r As QuoteRequest) As String             ' not virtual
        Return $"{Name} x{Factor(r)}"
    End Function
End Class

Public NotInheritable Class YoungDriverLoading                        ' sealed
    Inherits RatingRule

    Public Overrides ReadOnly Property Name As String = "young driver"

    Public Overrides Function Factor(r As QuoteRequest) As Decimal    ' override
        Return If(r.Driver.AgeOn(r.StartDate) < 25, 1.20D, 1.00D)
    End Function

    Public Shadows Function Describe(r As QuoteRequest) As String     ' new
        Return $"{Name} (hidden copy)"
    End Function
End Class
#End Region

#Region "vb-csv"
' the same CSV renderer in VB, on the C# generic base class
Public NotInheritable Class VbCsvRenderer
    Inherits ReportRenderer(Of QuoteReport)

    Private Shared ReadOnly Inv As CultureInfo =
        CultureInfo.InvariantCulture

    Public Overrides ReadOnly Property Format As String = "vb"

    Protected Overrides Sub WriteHeader(
            text As StringBuilder, report As QuoteReport)
        text.AppendLine("quote,vehicle,class,total_thb")
    End Sub

    Protected Overrides Sub WriteBody(
            text As StringBuilder, report As QuoteReport)
        For Each q In report.Lines
            text.AppendLine(String.Join(",",
                q.Id, q.Vehicle,
                CoverageClassExtensions.get_Code(q.Coverage),
                q.Total.Amount.ToString(Inv)))
        Next
    End Sub
End Class
#End Region
