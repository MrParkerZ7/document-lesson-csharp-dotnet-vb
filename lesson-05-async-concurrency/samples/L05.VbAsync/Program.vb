Imports System.Threading
Imports L05.PartnerRates

' The same rating desk as L05.RateDesk, in Visual Basic, calling the same C# library.
' Premiums are illustrative, not a real tariff.
Module Program
#Region "entry"
    ' VB cannot mark Sub Main as Async. A console app has no
    ' SynchronizationContext, so blocking once, here, is safe.
    ' Never copy this into a UI event handler or a web request.
    Sub Main()
        MainAsync().GetAwaiter().GetResult()
    End Sub
#End Region

    Private Async Function MainAsync() As Task
        Dim request As New QuoteRequest("Toyota", 2022, CoverageClass.Class1, New Money(650000D))
        Dim partners = PartnerCatalog.Create(TimeProvider.System)
        Dim timeout = TimeSpan.FromMilliseconds(250)
        Console.WriteLine($"VB  {partners.Count} partners, timeout {timeout.TotalMilliseconds} ms")

#Region "program"
        Dim fanOut As New RateFanOut(partners, TimeProvider.System,
                                     timeout)
        Dim clock = Stopwatch.StartNew()
        Dim outcomes = Await fanOut.QueryAllAsync(request)
        clock.Stop()

        Dim stats As New RateStats()
        For Each outcome In outcomes
            stats.Record(outcome)
        Next

        Console.WriteLine($"  quoted {stats.QuotedCount}" &
            $", timed out {stats.TimedOutCount}" &
            $", failed {stats.FailedCount}")
        Console.WriteLine($"  best   {stats.Best?.PartnerId}" &
            $" {stats.Best?.Premium}")
#End Region

        Dim sequential = partners.Sum(
            Function(p) If(p.Behaviour = PartnerBehaviour.Hangs OrElse p.Latency > timeout,
                           timeout.TotalMilliseconds, p.Latency.TotalMilliseconds))
        Console.WriteLine($"  wall   {clock.ElapsedMilliseconds} ms concurrently," &
                          $" {sequential:N0} ms one after another")
        Console.WriteLine($"  pool   {ThreadPool.ThreadCount} thread-pool threads")
        Console.WriteLine("  first answers, in completion order:")

#Region "stream"
        ' no Await For Each in VB: drive the enumerator by hand
        Using enough As New CancellationTokenSource()
            Dim e = fanOut.StreamAsync(request, enough.Token).
                GetAsyncEnumerator()
            Dim shown = 0
            While shown < 5 AndAlso Await e.MoveNextAsync()
                Console.WriteLine("    " & Describe(e.Current))
                shown += 1
            End While
            ' no Await inside Finally: dispose explicitly
            Await e.DisposeAsync()
            Await enough.CancelAsync()
        End Using
#End Region
        Console.WriteLine("  cancelled the partners still working")
    End Function

    Private Function Describe(outcome As PartnerOutcome) As String
        Dim q = TryCast(outcome, Quoted)
        If q IsNot Nothing Then Return $"{q.PartnerId} quoted {q.Premium}"
        Dim f = TryCast(outcome, Failed)
        If f IsNot Nothing Then Return $"{f.PartnerId} failed ({f.Reason})"
        Return $"{outcome.PartnerId} timed out"
    End Function
End Module
