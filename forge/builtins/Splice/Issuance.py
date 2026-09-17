"""Stand-in for the real `Splice.Issuance` Daml module
(`splice/daml/splice-amulet/daml/Splice/Issuance.daml`) - IDE/authoring
support only, see `Splice/__init__.py`.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Annotated, Optional
from .. import DamlName


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

    amulet_to_issue_per_year: Annotated[Decimal, DamlName("amuletToIssuePerYear")]
    validator_reward_percentage: Annotated[Decimal, DamlName("validatorRewardPercentage")]
    app_reward_percentage: Annotated[Decimal, DamlName("appRewardPercentage")]
    validator_reward_cap: Annotated[Decimal, DamlName("validatorRewardCap")]
    featured_app_reward_cap: Annotated[Decimal, DamlName("featuredAppRewardCap")]
    unfeatured_app_reward_cap: Annotated[Decimal, DamlName("unfeaturedAppRewardCap")]
    opt_validator_faucet_cap: Annotated[Optional[Decimal], DamlName("optValidatorFaucetCap")] = None
    opt_development_fund_percentage: Annotated[
        Optional[Decimal], DamlName("optDevelopmentFundPercentage")
    ] = None


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

    total_validator_reward_coupons: Annotated[Decimal, DamlName("totalValidatorRewardCoupons")]
    total_featured_app_reward_coupons: Annotated[Decimal, DamlName("totalFeaturedAppRewardCoupons")]
    total_unfeatured_app_reward_coupons: Annotated[
        Decimal, DamlName("totalUnfeaturedAppRewardCoupons")
    ]
    total_sv_reward_weight: Annotated[int, DamlName("totalSvRewardWeight")]
    opt_total_validator_faucet_coupons: Annotated[
        Optional[int], DamlName("optTotalValidatorFaucetCoupons")
    ] = None
