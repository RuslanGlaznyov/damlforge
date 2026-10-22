from datetime import timedelta
from typing import Annotated

from forge.models import Decimal, Optional
from forge.builtins import DamlName, no_derive
from Splice.Schedule import Schedule


struct IssuanceConfig:
    amulet_to_issue_per_year: Annotated[Decimal, DamlName("amuletToIssuePerYear")]
    validator_reward_percentage: Annotated[Decimal, DamlName("validatorRewardPercentage")]
    app_reward_percentage: Annotated[Decimal, DamlName("appRewardPercentage")]
    validator_reward_cap: Annotated[Decimal, DamlName("validatorRewardCap")]
    featured_app_reward_cap: Annotated[Decimal, DamlName("featuredAppRewardCap")]
    unfeatured_app_reward_cap: Annotated[Decimal, DamlName("unfeaturedAppRewardCap")]
    opt_validator_faucet_cap: Annotated[Optional[Decimal], DamlName("optValidatorFaucetCap")]
    opt_development_fund_percentage: Annotated[Optional[Decimal], DamlName("optDevelopmentFundPercentage")]


struct OpenMiningRoundSummary:
    total_validator_reward_coupons: Annotated[Decimal, DamlName("totalValidatorRewardCoupons")]
    total_featured_app_reward_coupons: Annotated[Decimal, DamlName("totalFeaturedAppRewardCoupons")]
    total_unfeatured_app_reward_coupons: Annotated[Decimal, DamlName("totalUnfeaturedAppRewardCoupons")]
    total_sv_reward_weight: Annotated[int, DamlName("totalSvRewardWeight")]
    opt_total_validator_faucet_coupons: Annotated[Optional[int], DamlName("optTotalValidatorFaucetCoupons")]


struct IssuingRoundParameters:
    issuance_per_validator_reward_coupon: Annotated[Decimal, DamlName("issuancePerValidatorRewardCoupon")]
    issuance_per_featured_app_reward_coupon: Annotated[Decimal, DamlName("issuancePerFeaturedAppRewardCoupon")]
    issuance_per_unfeatured_app_reward_coupon: Annotated[Decimal, DamlName("issuancePerUnfeaturedAppRewardCoupon")]
    issuance_per_sv_reward_coupon: Annotated[Decimal, DamlName("issuancePerSvRewardCoupon")]
    unclaimed_app_rewards: Annotated[Decimal, DamlName("unclaimedAppRewards")]
    unclaimed_validator_rewards: Annotated[Decimal, DamlName("unclaimedValidatorRewards")]
    unclaimed_sv_rewards: Annotated[Decimal, DamlName("unclaimedSvRewards")]
    issuance_per_validator_faucet_coupon: Annotated[Decimal, DamlName("issuancePerValidatorFaucetCoupon")]
    opt_amulets_to_issue_to_development_fund: Annotated[Optional[Decimal], DamlName("optAmuletsToIssueToDevelopmentFund")]


@no_derive
struct IssuanceTranche:
    rewards_to_issue: Annotated[Decimal, DamlName("rewardsToIssue")]
    issuance_per_coupon: Annotated[Decimal, DamlName("issuancePerCoupon")]
    unclaimed_rewards: Annotated[Decimal, DamlName("unclaimedRewards")]


@DamlName("getValidatorFaucetCap")
def get_validator_faucet_cap(issuance_config: IssuanceConfig) -> Decimal:
    pass


@DamlName("validIssuanceCurve")
def valid_issuance_curve(config_schedule: Schedule[timedelta, IssuanceConfig]) -> bool:
    pass


@DamlName("validIssuanceConfig")
def valid_issuance_config(this: IssuanceConfig) -> bool:
    pass


@DamlName("getTotalValidatorFaucetCoupons")
def get_total_validator_faucet_coupons(open_mining_round_summary: OpenMiningRoundSummary) -> int:
    pass


@DamlName("validateOpenMiningRoundSummary", is_ledger_effect=True)
def validate_open_mining_round_summary(open_mining_round_summary: OpenMiningRoundSummary) -> None:
    pass


@DamlName("computeIssuingRoundParameters")
def compute_issuing_round_parameters(tick_duration: timedelta, amulet_price: Decimal, config: IssuanceConfig, summary: OpenMiningRoundSummary) -> IssuingRoundParameters:
    pass


@DamlName("computeIssuanceTranche")
def compute_issuance_tranche(rewards_to_issue: Decimal, cap_per_coupon: Decimal, total_coupons: Decimal) -> IssuanceTranche:
    pass
