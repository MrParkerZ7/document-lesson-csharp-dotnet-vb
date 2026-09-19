Public Module AwaitInSyncLock
    Private ReadOnly Gate As New Object()

#Region "await-in-synclock"
    Async Function RecordAsync() As Task
        SyncLock Gate
            Await Task.Delay(10)   ' C# rejects await inside lock too
        End SyncLock
    End Function
#End Region
End Module
