Feature: No-claim bonus
  Careful drivers pay less. The track's canonical tariff,
  illustrative rates, not a real tariff.

  Background:
    Given a private car insured for 600000 THB, Class 1

  Scenario Outline: Claim-free years earn a discount
    Given a driver aged 36 with <years> claim-free years
    When the premium is calculated
    Then the net premium is <net> THB

    Examples:
      | years | net      |
      | 0     | 12600.00 |
      | 1     | 10080.00 |
      | 3     | 8820.00  |
      | 5     | 6300.00  |

  Scenario: A claim cancels the bonus and adds a loading
    Given a driver aged 36 with 10 claim-free years
    And the driver made 1 claim in the last 5 years
    When the premium is calculated
    Then the net premium is 13860.00 THB
