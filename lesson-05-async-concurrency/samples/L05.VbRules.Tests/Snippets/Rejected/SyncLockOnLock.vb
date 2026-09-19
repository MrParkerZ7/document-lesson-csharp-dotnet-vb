Public Class Stats
#Region "synclock-lock"
    Private ReadOnly _gate As New System.Threading.Lock()
    Private _quoted As Integer

    Sub Record()
        SyncLock _gate          ' C# lock() would call _gate.EnterScope()
            _quoted += 1
        End SyncLock
    End Sub
#End Region
End Class
