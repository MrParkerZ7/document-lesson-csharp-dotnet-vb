Imports L09.Data
Imports Microsoft.EntityFrameworkCore

Module Program
    Sub Main()
        Console.WriteLine("L09.VbReport: a C# DbContext queried from Visual Basic")

        Using sqlite As New SqliteDb()
            sqlite.Seed(20)
            Using db = sqlite.NewContext()
#Region "vb-query"
                ' VB query syntax. Group By ... Into becomes SQL GROUP BY;
                ' nothing runs until the For Each enumerates the query.
                Dim byCoverage = From q In db.Quotes
                                 Where q.Status = QuoteStatus.Quoted
                                 Group By q.Coverage Into Quotes = Count()
                                 Order By Coverage

                For Each row In byCoverage
                    Console.WriteLine($"  {row.Coverage,-11}{row.Quotes,3}")
                Next
#End Region
                Console.WriteLine(byCoverage.ToQueryString())

#Region "vb-strings"
                ' VB compiles = on two strings to Operators.CompareString.
                Dim toyotas = From v In db.Vehicles
                              Where v.Make = "Toyota"
                              Select v.Model
#End Region
                Console.WriteLine(toyotas.ToQueryString())
                Console.WriteLine("  models: " & String.Join(", ", toyotas))
            End Using
        End Using
    End Sub
End Module
