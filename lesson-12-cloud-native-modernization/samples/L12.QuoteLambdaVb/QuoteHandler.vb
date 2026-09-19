Imports System.Text.Json
Imports Amazon.Lambda.APIGatewayEvents
Imports Amazon.Lambda.Core
Imports Amazon.Lambda.Serialization.SystemTextJson
Imports L12.RatingVb

' Lambda deserializes the API Gateway event with this serializer.
<Assembly: LambdaSerializer(GetType(DefaultLambdaJsonSerializer))>

''' <summary>
''' A class-library handler written by hand — Lambda Annotations is a C# source generator.
''' Handler string: L12.QuoteLambdaVb::L12.QuoteLambdaVb.QuoteHandler::FunctionHandler
''' </summary>
Public NotInheritable Class QuoteHandler
#Region "raw-vb"
    Private Shared ReadOnly Json As JsonSerializerOptions =
        JsonSerializerOptions.Web

    Public Function FunctionHandler(
            request As APIGatewayHttpApiV2ProxyRequest,
            context As ILambdaContext) _
            As APIGatewayHttpApiV2ProxyResponse
        Dim input = JsonSerializer.Deserialize(Of QuoteInput)(
            If(request.Body, "{}"), Json)
        Dim coverage As CoverageClass
        If input Is Nothing OrElse Not [Enum].TryParse(
                input.Coverage, True, coverage) Then
            Return Respond(400, """unknown coverage""")
        End If

        Dim p = Rating.Quote(coverage, input.SumInsured,
            input.DriverAge, input.ClaimsLast5Years,
            input.Commercial)
        Return Respond(201, JsonSerializer.Serialize(p, Json))
    End Function

    Private Shared Function Respond(status As Integer,
            body As String) As APIGatewayHttpApiV2ProxyResponse
        Return New APIGatewayHttpApiV2ProxyResponse With {
            .StatusCode = status,
            .Body = body,
            .Headers = New Dictionary(Of String, String) From {
                {"Content-Type", "application/json"}}
        }
    End Function
#End Region
End Class

''' <summary>The JSON body of POST /quotes.</summary>
Public NotInheritable Class QuoteInput
    Public Property Coverage As String = ""
    Public Property SumInsured As Decimal
    Public Property DriverAge As Integer
    Public Property ClaimsLast5Years As Integer
    Public Property Commercial As Boolean
End Class
