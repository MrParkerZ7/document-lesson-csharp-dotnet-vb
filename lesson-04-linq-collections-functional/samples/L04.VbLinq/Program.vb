Imports System.Globalization
Imports L04.QuoteData

Module Program
    Sub Main()
        CultureInfo.CurrentCulture = CultureInfo.InvariantCulture
        Dim quotes = QuoteBook.Generate()
        Console.WriteLine($"VB dashboard: {quotes.Count} quotes, illustrative rates")

        Console.WriteLine("conversion by coverage class   quoted accepted rate")
#Region "conversion"
        Dim conversion =
            From q In quotes
            Where q.Status <> QuoteStatus.Declined
            Group By q.Coverage Into
                Quoted = Count(),
                Accepted = Count(q.IsAccepted)
            Order By Coverage
#End Region
        For Each c In conversion
            Dim rate = CDec(c.Accepted) * 100D / c.Quoted
            Console.WriteLine($"  {c.Coverage,-11}{c.Quoted,20}{c.Accepted,9}{rate,7:0.0}%")
        Next

        Console.WriteLine("top makes, accepted quotes")
#Region "top-makes"
        Dim topMakes = From q In quotes
                       Where q.IsAccepted
                       Group By q.Vehicle.Make Into Sold = Count()
                       Order By Sold Descending, Make
                       Take 5
#End Region
        Dim rank = 0
        For Each m In topMakes
            rank += 1
            Console.WriteLine($"  {rank}. {m.Make,-8}{m.Sold,4}")
        Next

#Region "aggregate"
        Dim book = Aggregate q In quotes
                   Where q.IsAccepted
                   Into Policies = Count(),
                        Premium = Sum(q.Total.Amount),
                        Largest = Max(q.Total.Amount)
#End Region
        Console.WriteLine($"accepted       {book.Policies} quotes, {book.Premium:N0} THB, largest {book.Largest:N0}")

#Region "distinct-skip-while"
        Dim makes = From q In quotes
                    Select q.Vehicle.Make
                    Distinct
                    Order By Make

        Dim window = From q In quotes
                     Order By q.Total.Amount
                     Skip While q.Total.Amount < 8600D
                     Take While q.Total.Amount < 8900D
                     Select q.QuoteId, q.Total.Amount
#End Region
        Console.WriteLine($"makes          {String.Join(",", makes)}")
        Console.WriteLine("premiums from 8,600 to under 8,900 THB")
        For Each x In window
            Console.WriteLine($"  {x.QuoteId}  {x.Amount,9:N2}")
        Next
    End Sub
End Module
