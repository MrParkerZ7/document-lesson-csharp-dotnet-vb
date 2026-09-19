Imports System.Runtime.CompilerServices
Imports Microsoft.AspNetCore.Builder
Imports Microsoft.AspNetCore.Http
Imports Microsoft.AspNetCore.Routing
Imports Microsoft.Extensions.Configuration
Imports Microsoft.Extensions.DependencyInjection
Imports Microsoft.Extensions.Options

''' <summary>How the C# host plugs the VB rating module in: services, then endpoints.</summary>
Public Module RatingModule
#Region "register"
    <Extension>
    Public Function AddMotorRating(
            services As IServiceCollection,
            config As IConfiguration) As IServiceCollection
        services.AddOptions(Of RatingOptions)() _
            .Bind(config.GetSection(RatingOptions.SectionName)) _
            .ValidateDataAnnotations() _
            .ValidateOnStart()

        services.AddSingleton(Of PremiumCalculator)()
        Return services
    End Function
#End Region

#Region "tariff-endpoint"
    ' A minimal API endpoint written in VB and mapped into the C# host.
    <Extension>
    Public Function MapTariff(app As IEndpointRouteBuilder) As RouteGroupBuilder
        Dim group = app.MapGroup("/tariff").WithTags("Tariff")

        group.MapGet("/{coverage}",
            Function(coverage As CoverageClass, calculator As PremiumCalculator)
                Return TypedResults.Ok(New TariffRow(coverage, calculator.BaseRateFor(coverage)))
            End Function)

        Return group
    End Function
#End Region
End Module
