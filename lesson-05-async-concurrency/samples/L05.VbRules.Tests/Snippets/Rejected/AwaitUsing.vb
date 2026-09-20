' a connection that can only be disposed asynchronously (what a partner client often is)
Public Class PartnerConnection
    Implements IAsyncDisposable

    Public Function SendAsync() As Task
        Return Task.CompletedTask
    End Function

    Public Function DisposeAsync() As ValueTask Implements IAsyncDisposable.DisposeAsync
        Return ValueTask.CompletedTask
    End Function
End Class

Public Module AwaitUsing
#Region "await-using"
    Async Function SendAsync() As Task
        Await Using c As New PartnerConnection()    ' C# 8: await using var c = new PartnerConnection();
            Await c.SendAsync()
        End Using
    End Function
#End Region
End Module
