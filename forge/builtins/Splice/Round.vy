from datetime import datetime, timedelta
from typing import Annotated

from forge.models import choice, Decimal, Optional, Party, template
from forge.builtins import DamlName
from Splice.AmuletConfig import RewardConfig, TransferConfig, USD
from Splice.Issuance import IssuanceConfig
from Splice.Types import Round


@template
class OpenMiningRound:
    dso: Party
    round: Round
    amulet_price: Annotated[Decimal, DamlName("amuletPrice")]
    opens_at: Annotated[datetime, DamlName("opensAt")]
    target_closes_at: Annotated[datetime, DamlName("targetClosesAt")]
    issuing_for: Annotated[timedelta, DamlName("issuingFor")]
    transfer_config_usd: Annotated[TransferConfig[USD], DamlName("transferConfigUsd")]
    issuance_config: Annotated[IssuanceConfig, DamlName("issuanceConfig")]
    tick_duration: Annotated[timedelta, DamlName("tickDuration")]
    traffic_price: Annotated[Optional[Decimal], DamlName("trafficPrice")]
    reward_config: Annotated[Optional[RewardConfig], DamlName("rewardConfig")]

    signatory: list[Party] = [dso]

    @choice(controller=p, consuming="nonconsuming")
    def OpenMiningRound_Fetch(self, p: Party) -> OpenMiningRound:
        pass


@template
class SummarizingMiningRound:
    dso: Party
    round: Round
    amulet_price: Annotated[Decimal, DamlName("amuletPrice")]
    issuance_config: Annotated[IssuanceConfig, DamlName("issuanceConfig")]
    tick_duration: Annotated[timedelta, DamlName("tickDuration")]
    traffic_price: Annotated[Optional[Decimal], DamlName("trafficPrice")]
    reward_config: Annotated[Optional[RewardConfig], DamlName("rewardConfig")]

    signatory: list[Party] = [dso]


@template
class IssuingMiningRound:
    dso: Party
    round: Round
    issuance_per_validator_reward_coupon: Annotated[Decimal, DamlName("issuancePerValidatorRewardCoupon")]
    issuance_per_featured_app_reward_coupon: Annotated[Decimal, DamlName("issuancePerFeaturedAppRewardCoupon")]
    issuance_per_unfeatured_app_reward_coupon: Annotated[Decimal, DamlName("issuancePerUnfeaturedAppRewardCoupon")]
    issuance_per_sv_reward_coupon: Annotated[Decimal, DamlName("issuancePerSvRewardCoupon")]
    opens_at: Annotated[datetime, DamlName("opensAt")]
    target_closes_at: Annotated[datetime, DamlName("targetClosesAt")]
    opt_issuance_per_validator_faucet_coupon: Annotated[Optional[Decimal], DamlName("optIssuancePerValidatorFaucetCoupon")]

    signatory: list[Party] = [dso]


@template
class ClosedMiningRound:
    dso: Party
    round: Round
    issuance_per_validator_reward_coupon: Annotated[Decimal, DamlName("issuancePerValidatorRewardCoupon")]
    issuance_per_featured_app_reward_coupon: Annotated[Decimal, DamlName("issuancePerFeaturedAppRewardCoupon")]
    issuance_per_unfeatured_app_reward_coupon: Annotated[Decimal, DamlName("issuancePerUnfeaturedAppRewardCoupon")]
    issuance_per_sv_reward_coupon: Annotated[Decimal, DamlName("issuancePerSvRewardCoupon")]
    opt_issuance_per_validator_faucet_coupon: Annotated[Optional[Decimal], DamlName("optIssuancePerValidatorFaucetCoupon")]

    signatory: list[Party] = [dso]


@DamlName("getIssuingMiningRoundIssuancePerValidatorFaucetCoupon")
def get_issuing_mining_round_issuance_per_validator_faucet_coupon(issuing_mining_round: IssuingMiningRound) -> Decimal:
    pass


@DamlName("getClosedMiningRoundIssuancePerValidatorFaucetCoupon")
def get_closed_mining_round_issuance_per_validator_faucet_coupon(issuing_mining_round: ClosedMiningRound) -> Decimal:
    pass
