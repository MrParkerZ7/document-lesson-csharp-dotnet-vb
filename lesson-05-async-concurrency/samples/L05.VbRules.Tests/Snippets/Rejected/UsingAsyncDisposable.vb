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

Public Module UsingAsyncDisposable
#Region "using-async-disposable"
    Async Function SendAsync() As Task
        Using c As New PartnerConnection()          ' Using needs IDisposable, and this type has only IAsyncDisposable
            Await c.SendAsync()
        End Using
    End Function
#End Region
End Module
