"""Stand-in for the real `Splice.Issuance` Daml module
(`splice/daml/splice-amulet/daml/Splice/Issuance.daml`) - IDE/authoring
support only, see `Splice/__init__.py`.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class IssuanceConfig:
    """The real Daml `IssuanceConfig` record - the Amulet issuance curve
    configuration for a mining round. Real Daml definition:

        data IssuanceConfig = IssuanceConfig with
            amuletToIssuePerYear : Decimal
            validatorRewardPercentage : Decimal
            appRewardPercentage : Decimal
            validatorRewardCap : Decimal
            featuredAppRewardCap : Decimal
            unfeaturedAppRewardCap : Decimal
            optValidatorFaucetCap : Optional Decimal
            optDevelopmentFundPercentage : Optional Decimal
          deriving (Eq, Show)
    """

    amulet_to_issue_per_year: Decimal
    validator_reward_percentage: Decimal
    app_reward_percentage: Decimal
    validator_reward_cap: Decimal
    featured_app_reward_cap: Decimal
    unfeatured_app_reward_cap: Decimal
    opt_validator_faucet_cap: Optional[Decimal] = None
    opt_development_fund_percentage: Optional[Decimal] = None


@dataclass(frozen=True)
class OpenMiningRoundSummary:
    """The real Daml `OpenMiningRoundSummary` record - the off-ledger-
    computed totals passed into `AmuletRules_MiningRound_StartIssuing`
    (`Splice.AmuletRules`). Real Daml definition:

        data OpenMiningRoundSummary = OpenMiningRoundSummary with
            totalValidatorRewardCoupons : Decimal
            totalFeaturedAppRewardCoupons : Decimal
            totalUnfeaturedAppRewardCoupons : Decimal
            totalSvRewardWeight : Int
            optTotalValidatorFaucetCoupons : Optional Int
          deriving (Eq, Show)
    """

    total_validator_reward_coupons: Decimal
    total_featured_app_reward_coupons: Decimal
    total_unfeatured_app_reward_coupons: Decimal
    total_sv_reward_weight: int
    opt_total_validator_faucet_coupons: Optional[int] = None
