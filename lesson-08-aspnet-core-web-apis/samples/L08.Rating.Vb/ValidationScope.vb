Imports System.ComponentModel.DataAnnotations
Imports System.Runtime.CompilerServices
Imports Microsoft.AspNetCore.Builder
Imports Microsoft.AspNetCore.Http
Imports Microsoft.AspNetCore.Routing

''' <summary>
''' What a C# host's AddValidation reaches in a VB library, pinned by ValidationScopeTests:
''' its filter runs on VB endpoints, but its C# source generator never sees VB-declared types.
''' </summary>
Public Module ValidationScope
#Region "validation-scope"
    <Extension>
    Public Function MapRatingChecks(app As IEndpointRouteBuilder) As RouteGroupBuilder
        Dim group = app.MapGroup("/checks")

        ' <Range> on a handler parameter: enforced, 400 ValidationProblem
        group.MapGet("/years/{years}",
            New Func(Of Integer, IResult)(AddressOf CheckYears))

        ' <Range> on a property of a VB class: never discovered, 200
        group.MapPost("/vehicle",
            New Func(Of VehicleCheck, IResult)(AddressOf CheckVehicle))

        Return group
    End Function

    Private Function CheckYears(<Range(1, 3)> years As Integer) As IResult
        Return TypedResults.Ok(years)
    End Function

    Private Function CheckVehicle(vehicle As VehicleCheck) As IResult
        Return TypedResults.Ok(vehicle.Years)
    End Function
#End Region
End Module

Public NotInheritable Class VehicleCheck
    <Range(1, 3)>
    Public Property Years As Integer
End Class
