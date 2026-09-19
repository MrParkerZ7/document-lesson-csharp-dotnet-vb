Feature: No-claim bonus
  Careful drivers pay less. Illustrative rates, not a tariff.

  Background:
    Given a private car insured for 600000 THB, Class 1

  Scenario Outline: Claim-free years earn a discount
    Given a driver aged 36 with <years> claim-free years
    When the premium is calculated
    Then the net premium is <net> THB

    Examples:
      | years | net      |
      | 0     | 12000.00 |
      | 1     | 9600.00  |
      | 3     | 8400.00  |
      | 5     | 6000.00  |

  Scenario: A claim cancels the bonus and adds a loading
    Given a driver aged 36 with 10 claim-free years
    And the driver made 1 claim in the last 5 years
    When the premium is calculated
    Then the net premium is 13200.00 THB
