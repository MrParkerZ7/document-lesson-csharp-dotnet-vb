using System.ComponentModel.DataAnnotations;

namespace L08.QuoteApi.Quotes;

/// <summary>Bound from the "Quotes" section — the @ConfigurationProperties of this API.</summary>
public sealed class QuoteOptions
{
    public const string SectionName = "Quotes";

    [Range(1, 90)]
    public int ValidityDays { get; set; } = 30;

    [Required, StringLength(3, MinimumLength = 3)]
    public string Currency { get; set; } = "THB";
}

public static class QuoteRegistration
{
    #region register
    public static IServiceCollection AddQuoteFeature(
        this IServiceCollection services,
        IConfiguration config)
    {
        services.AddOptions<QuoteOptions>()
            .Bind(config.GetSection(QuoteOptions.SectionName))
            .ValidateDataAnnotations()
            .ValidateOnStart();

        services.AddSingleton(TimeProvider.System);
        services.AddSingleton<IQuoteStore, InMemoryQuoteStore>();
        services.AddSingleton<PolicyNumbers>();
        services.AddScoped<QuoteService>();
        return services;
    }
    #endregion
}
