Public Module AsyncIterator
#Region "async-iterator"
    Async Iterator Function QuotesAsync() As IAsyncEnumerable(Of Decimal)
        Await Task.Delay(10)
        Yield 12090D
    End Function
#End Region
End Module
