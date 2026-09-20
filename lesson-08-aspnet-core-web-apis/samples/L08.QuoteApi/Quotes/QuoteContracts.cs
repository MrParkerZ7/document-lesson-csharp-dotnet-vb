using System.ComponentModel.DataAnnotations;
using MotorQuote.Rating;

namespace L08.QuoteApi.Quotes;

#region contracts
public sealed record QuoteRequest(
    [Required] VehicleDto Vehicle,
    [Required] DriverDto Driver,
    CoverageClass Coverage,
    DateOnly StartDate,
    [AllowedValues("sms", "email", "line")] string NotifyVia = "email");

public sealed record VehicleDto(
    [Required, StringLength(40)] string Make,
    [Required, StringLength(40)] string Model,
    [Range(1990, 2035)] int Year,
    [Range(50, 8000)] int EngineCc,
    VehicleUse Use,
    [Range(typeof(decimal), "50000", "20000000")] decimal SumInsured);

public sealed record DriverDto(
    DateOnly DateOfBirth,
    [Range(0, 70)] int LicenceYears,
    [Range(0, 20)] int ClaimsLast5Years);
#endregion

/// <summary>THB by default; decimal, never double.</summary>
public readonly record struct Money(decimal Amount, string Currency = "THB");

public sealed record PremiumDto(
    Money Base, decimal LoadingRate, decimal DiscountRate,
    Money Net, Money StampDuty, Money Vat, Money Total);

public sealed record QuoteResponse(
    Guid QuoteId, QuoteStatus Status, PremiumDto? Premium, DateTimeOffset ValidUntil,
    string? DeclineReason = null);

public sealed record PolicyResponse(
    string PolicyNumber, Guid QuoteId, DateOnly Inception, DateOnly Expiry);
