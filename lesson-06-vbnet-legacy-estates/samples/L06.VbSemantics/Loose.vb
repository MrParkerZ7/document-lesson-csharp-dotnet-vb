Option Strict Off
Option Compare Text

' The project says Option Strict On. This file opts out, which is
' exactly how loose legacy files survive inside "strict" projects.
Public Module Loose

    Public Sub LateBindingAndText()
#Region "late-binding"
        Dim card As Object = New L06.PartnerSdk.PartnerRateCard()
        Console.WriteLine($"late bound LoadingFor(2)  {card.LoadingFor(2)}")
        Try
            Console.WriteLine(card.Discount)         ' compiles, fails at run time
        Catch ex As MissingMemberException
            Console.WriteLine($"late bound Discount       {ex.GetType().Name}")
        End Try
        Console.WriteLine($"""42"" + 1  = {"42" + 1}      ""42"" & 1  = {"42" & 1}")
#End Region

#Region "option-compare"
        Console.WriteLine($"""CLASS1"" = ""class1""     {"CLASS1" = "class1"}")
        Dim age = DateDiff(DateInterval.Year, #12/31/2001#, #1/1/2026#)
        Console.WriteLine($"DateDiff(Year, 31 Dec 2001, 1 Jan 2026)  {age}")
        Dim years As Integer = 11 / 12
        Console.WriteLine($"Dim years As Integer = 11 / 12           {years}")
#End Region
    End Sub

    Public Sub OnErrorResumeNext()
#Region "on-error"
        Dim zero = 0
        On Error Resume Next
        Dim ratio = 1 \ zero                         ' raises, execution continues
        Console.WriteLine($"On Error Resume Next   Err.Number {Err.Number}, ratio {ratio}")
        On Error GoTo 0
#End Region
    End Sub

End Module
