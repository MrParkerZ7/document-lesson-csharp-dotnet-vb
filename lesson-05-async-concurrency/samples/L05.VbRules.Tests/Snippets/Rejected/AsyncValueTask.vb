Public Module AsyncValueTask
#Region "async-valuetask"
    Async Function CachedRateAsync() As ValueTask(Of Decimal)
        Await Task.Delay(10)
        Return 12090D
    End Function
#End Region
End Module
