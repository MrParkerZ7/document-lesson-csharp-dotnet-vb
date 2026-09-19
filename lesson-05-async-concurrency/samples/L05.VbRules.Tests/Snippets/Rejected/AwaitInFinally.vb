Public Module AwaitInFinally
#Region "await-in-finally"
    Async Function SendAsync(connection As IAsyncDisposable) As Task
        Try
            Await Task.Delay(10)
        Finally
            Await connection.DisposeAsync()   ' async cleanup
        End Try
    End Function
#End Region
End Module
