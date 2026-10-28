namespace L13.DebugLab.Tests;

public class BatchTests
{
    [Fact, Trait("Category", "Batch")]
    public void The_batch_declines_exactly_the_quotes_with_three_claims()
    {
        var result = QuoteBatch.Run(240);

        Assert.Equal([47, 108, 169, 230], result.Declined);
        Assert.Equal(236, result.Quoted);
    }

    [Fact, Trait("Category", "Batch")]
    public void The_generator_is_deterministic() =>
        Assert.Equal(QuoteBatch.Request(137), QuoteBatch.Request(137));

    [Fact, Trait("Category", "Batch")]
    public void Every_priced_quote_adds_up()
    {
        for (var i = 0; i < 240; i++)
        {
            if (i % 61 == 47) continue;   // the declined ones
            var p = QuoteCalculator.Price(QuoteBatch.Request(i));
            Assert.Equal(p.Net.Amount + p.StampDuty.Amount + p.Vat.Amount, p.Total.Amount);
        }
    }
}
