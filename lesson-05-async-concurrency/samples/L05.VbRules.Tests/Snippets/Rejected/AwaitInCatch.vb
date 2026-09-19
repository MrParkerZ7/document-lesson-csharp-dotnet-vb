Imports System.Net.Http

Public Module AwaitInCatch
#Region "await-in-catch"
    Async Function RateAsync(primary As Func(Of Task(Of Decimal)),
                             backup As Func(Of Task(Of Decimal))) As Task(Of Decimal)
        Try
            Return Await primary()
        Catch ex As HttpRequestException
            Return Await backup()       ' fall back to a second partner
        End Try
    End Function
#End Region
End Module
