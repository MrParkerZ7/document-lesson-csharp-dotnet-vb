using System.Globalization;
using System.Reflection;
using System.Runtime.CompilerServices;

namespace L03.Domain.Tests;

public class QuoteTests
{
    [Fact]
    public void A_new_quote_starts_quoted() =>
        Assert.Equal(QuoteStatus.Quoted, Samples.Quote(1, Samples.YoungDriver()).Status);

    [Fact]
    public void Accepting_issues_a_one_year_policy()
    {
        var quote = Samples.Quote(1, Samples.YoungDriver());
        var policy = quote.Accept(new PolicyNumber(7));
        Assert.Equal(QuoteStatus.Accepted, quote.Status);
        Assert.Equal(quote.Id, policy.QuoteId);
        Assert.Equal(new DateOnly(2027, 10, 1), policy.Expiry);
    }

    [Fact]
    public void An_accepted_quote_cannot_expire()
    {
        var quote = Samples.Quote(1, Samples.YoungDriver());
        quote.Accept(new PolicyNumber(7));
        var error = Assert.Throws<InvalidOperationException>(quote.Expire);
        Assert.Equal("Accepted -> Expired", error.Message);
    }

    [Fact]
    public void A_declined_quote_cannot_be_declined_again()
    {
        var quote = Samples.Quote(1, Samples.YoungDriver());
        quote.Decline();
        Assert.Throws<InvalidOperationException>(quote.Decline);
    }
}

public class PremiumTests
{
    [Fact]
    public void Young_driver_class_1_breaks_down_as_expected()
    {
        // 450,000 x 2.1% = 9,450.00 base; +20% young driver; -30% no-claim (3 claim-free years)
        var premium = Samples.Calculator().Calculate(Samples.YoungDriver());
        Assert.Equal(Money.Thb(7_938.00m), premium.Net);
        Assert.Equal(Money.Thb(31.75m), premium.StampDuty);
        Assert.Equal(Money.Thb(557.88m), premium.Vat);
        Assert.Equal(Money.Thb(8_527.63m), premium.Total);
    }

    [Fact]
    public void Commercial_pickup_with_one_claim_breaks_down_as_expected()
    {
        // 620,000 x 1.2% = 7,440.00 base; +10% one claim and +25% commercial added, not multiplied
        var premium = Samples.Calculator().Calculate(Samples.CommercialPickup());
        Assert.Equal(Money.Thb(10_044.00m), premium.Net);
        Assert.Equal(Money.Thb(10_790.07m), premium.Total);
    }

    [Fact]
    public void The_worked_example_of_the_curriculum_tariff_holds()
    {
        // Class 1, 550,000 THB, private, aged 23 with 4 claim-free licence years
        var request = new QuoteRequest(
            Samples.YoungDriver().Vehicle with { SumInsured = Money.Thb(550_000m) },
            new Driver(new DateOnly(2003, 5, 10), LicenceYears: 4, ClaimsLast5Years: 0),
            CoverageClass.Class1,
            Samples.StartDate);
        var premium = Samples.Calculator().Calculate(request);
        Assert.Equal(Money.Thb(8_316.00m), premium.Net);
        Assert.Equal(Money.Thb(33.26m), premium.StampDuty);
        Assert.Equal(Money.Thb(584.45m), premium.Vat);
        Assert.Equal(Money.Thb(8_933.71m), premium.Total);
    }

    [Fact]
    public void Three_claims_in_five_years_declines_the_quote()
    {
        var request = Samples.ThreeClaims();
        var declined = Assert.Throws<QuoteDeclinedException>(
            () => Samples.Calculator().Calculate(request));
        Assert.Equal("3+ claims in 5 years", declined.Message);
        Assert.Equal(request, declined.Request);
    }
}

public class DispatchTests
{
    private static readonly QuoteRequest Young = Samples.YoungDriver();

    [Fact]
    public void A_virtual_call_uses_the_runtime_type()
    {
        RatingRule rule = new YoungDriverLoading();
        Assert.Equal(1.20m, rule.Factor(Young));
    }

    [Fact]
    public void A_non_virtual_call_uses_the_static_type()
    {
        var derived = new YoungDriverLoading();
        RatingRule asBase = derived;
        Assert.Equal("young driver x1.20", asBase.Describe(Young));
        Assert.Equal("young driver (hidden copy)", derived.Describe(Young));
    }

    [Fact]
    public void A_default_interface_method_is_reached_through_the_interface()
    {
        IRateTable table = new StandardRateTable();
        Assert.Equal(Money.Thb(9_450m), table.BasePremium(Young));
    }

    [Fact]
    public void A_default_interface_method_is_not_inherited_by_the_class() =>
        Assert.Null(typeof(StandardRateTable).GetMethod(nameof(IRateTable.BasePremium)));

    [Theory]
    [InlineData(0, 0, "1.00")]
    [InlineData(0, 1, "0.80")]
    [InlineData(0, 3, "0.70")]
    [InlineData(0, 4, "0.60")]
    [InlineData(0, 9, "0.50")]
    [InlineData(2, 9, "1.00")]   // a claim resets the claim-free years to zero
    public void No_claim_bonus_follows_the_claim_free_ladder(int claims, int licenceYears, string expected)
    {
        var request = Young with
        {
            Driver = Young.Driver with { ClaimsLast5Years = claims, LicenceYears = licenceYears },
        };
        Assert.Equal(decimal.Parse(expected, CultureInfo.InvariantCulture), new NoClaimBonus().Factor(request));
    }

    [Theory]
    [InlineData(0, "1.00")]
    [InlineData(1, "1.10")]
    [InlineData(2, "1.25")]
    public void The_claims_loading_follows_the_tariff(int claims, string expected)
    {
        var request = Young with { Driver = Young.Driver with { ClaimsLast5Years = claims } };
        Assert.Equal(decimal.Parse(expected, CultureInfo.InvariantCulture), new ClaimsLoading().Factor(request));
    }

    [Fact]
    public void Only_the_no_claim_bonus_discounts()
    {
        Assert.True(new NoClaimBonus().IsDiscount);
        Assert.False(new ClaimsLoading().IsDiscount);
        Assert.False(new YoungDriverLoading().IsDiscount);
        Assert.False(new CommercialUseLoading().IsDiscount);
    }
}

public class PrimaryConstructorTests
{
    private const BindingFlags Declared =
        BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.DeclaredOnly;

    [Fact]
    public void A_parameter_used_in_a_method_is_captured_in_a_mutable_hidden_field()
    {
        var captured = typeof(PremiumCalculator).GetFields(Declared)
            .Where(f => f.IsDefined(typeof(CompilerGeneratedAttribute)));
        var rates = Assert.Single(captured);
        Assert.Equal(typeof(IRateTable), rates.FieldType);
        Assert.False(rates.IsInitOnly); // not readonly: the class body could reassign it
    }

    [Fact]
    public void A_parameter_used_only_in_an_initializer_is_never_stored()
    {
        var fields = typeof(PremiumCalculator).GetFields(Declared);
        Assert.DoesNotContain(fields, f => f.FieldType == typeof(IEnumerable<RatingRule>));
        Assert.Contains(fields, f => f.FieldType == typeof(RatingRule[]) && f.IsInitOnly);
    }

    [Fact]
    public void Primary_constructor_parameters_are_not_properties() =>
        Assert.Empty(typeof(PremiumCalculator).GetProperties(Declared));
}

public class GenericsTests
{
    private static class Box<T>
    {
        public static int Created;
    }

    [Fact]
    public void ParseAll_calls_the_static_member_of_the_type_argument()
    {
        var ids = Ids.ParseAll<QuoteId>("Q-000042", "Q-000043");
        Assert.Equal(new[] { new QuoteId(42), new QuoteId(43) }, ids);
    }

    [Fact]
    public void The_type_argument_is_known_at_run_time() =>
        Assert.Equal("QuoteId Q- Q-000000", Ids.Describe<QuoteId>());

    [Fact]
    public void One_sum_serves_decimal_and_money()
    {
        Assert.Equal(6.50m, Totals.Sum([1.25m, 2.25m, 3.00m], 0m));
        Assert.Equal(Money.Thb(1_500m), Totals.Sum([Money.Thb(1_000m), Money.Thb(500m)], Money.Thb(0m)));
    }

    [Fact]
    public void Each_closed_generic_type_has_its_own_static_fields()
    {
        Box<int>.Created += 2;
        Box<string>.Created += 1;
        Assert.Equal(2, Box<int>.Created);
        Assert.Equal(1, Box<string>.Created);
    }
}

public class ExtensionTests
{
    [Theory]
    [InlineData(CoverageClass.Class1, "1", true)]
    [InlineData(CoverageClass.Class2Plus, "2+", true)]
    [InlineData(CoverageClass.Class3Plus, "3+", true)]
    [InlineData(CoverageClass.Class3, "3", false)]
    public void Extension_members_read_like_members_of_the_enum(CoverageClass coverage, string code, bool ownDamage)
    {
        Assert.Equal(code, coverage.Code);
        Assert.Equal(ownDamage, coverage.CoversOwnDamage);
        Assert.Equal(coverage, CoverageClass.FromCode(code));
    }

    [Fact]
    public void Enums_are_open_so_every_switch_needs_a_default_arm()
    {
        var bogus = (CoverageClass)42;
        Assert.False(Enum.IsDefined(bogus));
        Assert.Throws<ArgumentOutOfRangeException>(() => bogus.Code);
    }

    [Fact]
    public void An_extension_property_compiles_to_a_static_get_method()
    {
        var getter = typeof(CoverageClassExtensions).GetMethod("get_Code", BindingFlags.Public | BindingFlags.Static);
        Assert.NotNull(getter);
        Assert.Equal("2+", getter.Invoke(null, [CoverageClass.Class2Plus]));
    }

    [Fact]
    public void A_classic_extension_method_still_works() =>
        Assert.True(Samples.YoungDriver().Driver.IsYoungOn(Samples.StartDate));
}

public class EqualityTests
{
    private const string Upper = "MR0FZ22G801234567";
    private const string Lower = "mr0fz22g801234567";

    [Fact]
    public void Hand_written_equality_is_consistent_everywhere()
    {
        var a = new Vin(Upper);
        var b = new Vin(Lower);
        Assert.True(a == b);
        Assert.True(a.Equals((object)b));
        Assert.Equal(a.GetHashCode(), b.GetHashCode());
        Assert.Contains(b, new HashSet<Vin> { a });
    }

    [Fact]
    public void A_record_with_replaced_equality_keeps_the_generated_operators()
    {
        Assert.True(new VinRecord(Upper) == new VinRecord(Lower));
        Assert.Contains(new VinRecord(Lower), new HashSet<VinRecord> { new(Upper) });
    }

    [Fact]
    public void Equal_objects_with_different_hash_codes_get_lost_in_a_set()
    {
        var set = new HashSet<BrokenVin> { new(Upper) };
        Assert.True(new BrokenVin(Upper).Equals(new BrokenVin(Lower)));
        var found = set.Contains(new BrokenVin(Lower));
        Assert.False(found);
    }
}
