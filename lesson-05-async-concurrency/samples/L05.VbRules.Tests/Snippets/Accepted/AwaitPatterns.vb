Public Module AwaitPatterns
#Region "accepted"
    ' Await inside Try, inside a While condition, and on a ValueTask(Of T)
    Async Function FirstQuoteAsync(quotes As IAsyncEnumerable(Of Decimal),
                                   ct As CancellationToken) As Task(Of Decimal)
        Dim e = quotes.GetAsyncEnumerator(ct)
        Dim failure As Exception = Nothing
        Dim first = 0D
        Try
            While first = 0D AndAlso Await e.MoveNextAsync()   ' ValueTask(Of Boolean)
                first = e.Current
            End While
        Catch ex As Exception
            failure = ex                                        ' no Await here...
        End Try
        Await e.DisposeAsync()                                  ' ...so clean up after the Try
        If failure IsNot Nothing Then Runtime.ExceptionServices.ExceptionDispatchInfo.Throw(failure)
        Return first
    End Function

    ' Await in a lambda, and a lock that is safe across awaits
    Private ReadOnly Gate As New SemaphoreSlim(1, 1)

    Async Function RecordAsync(save As Func(Of Task)) As Task
        Await Gate.WaitAsync()
        Try
            Await save()
        Finally
            Gate.Release()
        End Try
    End Function
#End Region
End Module
