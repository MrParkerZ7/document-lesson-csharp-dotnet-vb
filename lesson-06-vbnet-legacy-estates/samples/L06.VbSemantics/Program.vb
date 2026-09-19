Imports System.Globalization
Imports L06.PartnerSdk

' The project default: Option Strict On, Option Compare Binary.
Module Program
    Private calls As Integer

    Sub Main()
        CultureInfo.CurrentCulture = CultureInfo.InvariantCulture
        AndVersusAndAlso()
        ArraysAndDivision()
        Rounding()
        NothingAndStrings()
        CallingCSharp()
        Loose.LateBindingAndText()
        Loose.OnErrorResumeNext()
    End Sub

    Private Function Touch() As Boolean
        calls += 1
        Return True
    End Function

    Sub AndVersusAndAlso()
#Region "and-andalso"
        Dim hasPolicy = False
        calls = 0
        If hasPolicy And Touch() Then Console.WriteLine("unreachable")
        Console.WriteLine($"And        right side ran {calls}x")
        calls = 0
        If hasPolicy AndAlso Touch() Then Console.WriteLine("unreachable")
        Console.WriteLine($"AndAlso    right side ran {calls}x")
        calls = 0
        Dim label = IIf(hasPolicy, Touch(), "none")    ' a function: both run
        Console.WriteLine($"IIf        right side ran {calls}x -> {label}")
        calls = 0
        Dim label2 = If(hasPolicy, Touch().ToString(), "none")
        Console.WriteLine($"If()       right side ran {calls}x -> {label2}")
#End Region
    End Sub

    Sub ArraysAndDivision()
#Region "arrays-division"
        Dim ncb(5) As Decimal                ' upper bound 5, not length 5
        Console.WriteLine($"Dim ncb(5)          Length {ncb.Length}")
        ReDim Preserve ncb(7)
        Console.WriteLine($"ReDim Preserve (7)  Length {ncb.Length}")

        Dim months = 18
        Console.WriteLine($"18 / 12 = {months / 12}   18 \ 12 = {months \ 12}")
        Console.WriteLine($"18 Mod 12 = {months Mod 12}")
        Console.WriteLine($"CInt(18 / 12) = {CInt(months / 12)}   CInt(11 / 12) = {CInt(11 / 12)}")
#End Region
    End Sub

    Sub Rounding()
#Region "rounding"
        For Each v In {0.5, 1.5, 2.5, 3.5}
            Console.WriteLine($"{v}  CInt {CInt(v)}  Fix {Fix(v)}  Math.Round {Math.Round(v)}" &
                              $"  AwayFromZero {Math.Round(v, MidpointRounding.AwayFromZero)}")
        Next
#End Region
    End Sub

    Sub NothingAndStrings()
#Region "nothing"
        Dim reason As String = Nothing
        Console.WriteLine($"reason = """"            {reason = ""}")
        Console.WriteLine($"reason Is Nothing      {reason Is Nothing}")
        Dim claims As Integer = Nothing              ' the default value: 0
        Console.WriteLine($"Integer = Nothing      {claims}")
        Console.WriteLine($"""CLASS1"" = ""class1""    {"CLASS1" = "class1"}")
#End Region
    End Sub

    Sub CallingCSharp()
#Region "byref-property"
        Dim line As New QuoteLine With {.Total = 1000D}
        Dim before = line.Total
        PartnerRateCard.AddFee(line.Total)           ' property, ByRef
        Console.WriteLine($"AddFee(line.Total)     {before} -> {line.Total}")
        before = line.Total
        PartnerRateCard.AddFee((line.Total))         ' ( ) passes a copy
        Console.WriteLine($"AddFee((line.Total))   {before} -> {line.Total}")
#End Region

#Region "case-collision"
        Dim card As New PartnerRateCard()
#If SHOW_CASE_COLLISION Then
        Console.WriteLine(card.Loading)              ' BC31429 in VB
#End If
        Console.WriteLine($"card.LoadingFor(2)     {card.LoadingFor(2)}")
#End Region
    End Sub

    ' Not called: exists so SHOW_MY_COMPUTER can reproduce BC30456.
    Sub MyNamespace()
#Region "my-namespace"
#If SHOW_MY_COMPUTER Then
        Console.WriteLine(My.Computer.Name)          ' BC30456 in a console
#End If
#End Region
    End Sub
End Module

Public Class QuoteLine
    Public Property Total As Decimal
End Class
