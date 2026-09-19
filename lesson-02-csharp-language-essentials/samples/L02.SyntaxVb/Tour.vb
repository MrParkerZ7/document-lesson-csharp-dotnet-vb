Imports L02.Rating

Public NotInheritable Class QuoteDraft
    Public Property Note As String
    Public Property Loading As Decimal
End Class

Public NotInheritable Class AuditScope
    Implements IDisposable

    Private ReadOnly _name As String

    Public Sub New(name As String)
        _name = name
    End Sub

    Public Sub Dispose() Implements IDisposable.Dispose
        Console.WriteLine($"dispose {_name}")
    End Sub
End Class

Public Module Tour
    Private Function LookUpNote(quoteId As String) As String
        Return If(quoteId = "Q-0001", "renewal", Nothing)
    End Function

    Private Function FindDraft(quoteId As String) As QuoteDraft
        Return If(quoteId = "Q-0001", New QuoteDraft(), Nothing)
    End Function

    Public Sub Types()
        Console.WriteLine()
        Console.WriteLine("[types]")
#Region "numbers"
        Dim engineCc As Integer = 1_200     ' Integer = System.Int32
        Dim year = 2024                     ' Option Infer: Integer
        Const MaxClaims As Integer = 2
        Console.WriteLine($"{GetType(Integer).FullName} {engineCc} {year} {MaxClaims}")

#Region "overflow"
        Dim big = Integer.MaxValue
        Try
            Console.WriteLine(big + 1)   ' checked by default
        Catch ex As OverflowException
            Console.WriteLine("VB: OverflowException without checked")
        End Try
        ' the constant Integer.MaxValue + 1: compile error BC30439
#End Region
#End Region

#Region "money"
        Dim sumInsured As Decimal = 550_000D   ' D suffix = Decimal
        Dim rate = 0.021D
        Dim basePremium = sumInsured * rate

        Dim d As Double = 0
        Dim m As Decimal = 0
        For i = 1 To 10
            d += 0.1
            m += 0.1D
        Next
        Console.WriteLine(d)
        Console.WriteLine(m)

        ' Option Strict On: Double -> Decimal needs CDec
        Dim vat = basePremium * CDec(0.07)
        Console.WriteLine($"{basePremium} {vat}")
#End Region
    End Sub

    Public Sub Nulls()
        Console.WriteLine()
        Console.WriteLine("[nulls]")
#Region "nulls"
        Dim note As String = LookUpNote("Q-0002") ' no String?
        Dim length = If(note?.Length, 0)          ' If(a, b) = ??
        If note Is Nothing Then note = "no note"  ' no ??= in VB
        Console.WriteLine($"{note} ({length})")

        Dim sure As String = LookUpNote("Q-0001") ' no ! to write
        Console.WriteLine(sure.ToUpperInvariant())

        Dim draft = FindDraft("Q-0001")
        If draft IsNot Nothing Then               ' no ?. on the left
            draft.Note = "young driver"
            draft.Loading += 0.2D
        End If
        Console.WriteLine($"{draft?.Note} {draft?.Loading}")
#End Region

        Dim claims As Integer? = Nothing          ' Nullable(Of T)
        Console.WriteLine(claims.GetValueOrDefault())
    End Sub

#Region "select-case"
    Function AgeLoading(age As Integer) As Decimal
        Select Case age
            Case Is < 18
                Throw New NotSupportedException("under 18")
            Case Is < 25
                Return 0.2D
            Case 25 To 29
                Return 0.1D
            Case Is >= 70
                Return 0.15D
            Case Else
                Return 0D
        End Select
    End Function
#End Region

    Public Sub Patterns()
        Console.WriteLine()
        Console.WriteLine("[patterns]")
        Dim age = Examples.YoungDriver().Driver.AgeOn(Examples.StartDate)
        Console.WriteLine($"age {age} loading {AgeLoading(age)}")

#Region "type-check"
        Dim input As Object = Examples.YoungDriver().Vehicle
        If TypeOf input Is Vehicle Then           ' no property patterns
            Dim v = DirectCast(input, Vehicle)
            Console.WriteLine($"{v.Make} {v.EngineCc} cc")
        End If
#End Region
    End Sub

#Region "methods"
    Function Discount(amount As Decimal, Optional rate As Decimal = 0.3D,
                      Optional roundUp As Boolean = False) As Decimal
        Return If(roundUp, Math.Ceiling(amount * rate), amount * rate)
    End Function

    Function Sum(ParamArray parts As Decimal()) As Decimal
        Dim total As Decimal = 0
        For Each part In parts
            total += part
        Next
        Return total
    End Function

    Function Bonus(d As Driver) As (Bonus As Decimal, Reason As String)
        Return If(d.ClaimsLast5Years = 0,
                  (RatingRules.NoClaimBonus(d), "claim-free"),
                  (0D, "has claims"))
    End Function

    Sub AddLoading(ByRef premium As Decimal, rate As Decimal)
        premium += premium * rate
    End Sub
#End Region

    Public Sub Methods()
        Console.WriteLine()
        Console.WriteLine("[methods]")
#Region "calls"
        Dim d1 = Discount(13_860D, roundUp:=True)
        Dim total = Sum(9_702D, 38.81D, 681.86D)
        Dim result = Bonus(Examples.YoungDriver().Driver)   ' no deconstruction
        Dim premium = 11_550D
        AddLoading(premium, 0.2D)                           ' ByRef is not repeated
        Console.WriteLine($"{d1:N2} {total:N2} {result.Bonus} {result.Reason} {premium:N2}")
#End Region
    End Sub

    Public Sub Errors()
        Console.WriteLine()
        Console.WriteLine("[errors]")
#Region "errors"
        Using audit As New AuditScope("audit"),
              trace As New AuditScope("trace")
            Try
                Dim request = Examples.YoungDriver(claims:=3)
                Dim premium = PremiumCalculator.Calculate(request)
                Console.WriteLine(premium.Total)
            Catch e As QuoteDeclinedException _
                When e.Reason.Contains("claims")
                Console.WriteLine($"declined: {e.Reason}")
            End Try
        End Using                     ' trace, then audit, disposed
#End Region
    End Sub
End Module
