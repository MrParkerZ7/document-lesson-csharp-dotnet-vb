Public Module AwaitForEach
#Region "await-for-each"
    Async Function CountAsync(quotes As IAsyncEnumerable(Of Decimal)) As Task(Of Integer)
        Dim n = 0
        Await For Each q In quotes     ' C# 8: await foreach
            n += 1
        Next
        Return n
    End Function
#End Region
End Module
