"""Stand-in for the real `Splice.Round` Daml module
(`splice/daml/splice-amulet/daml/Splice/Round.daml`) - IDE/authoring support
only, see `Splice/__init__.py`.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from forge.models.types import Party, RelTime, Timestamp
from Splice.AmuletConfig import USD, RewardConfig, TransferConfig
from Splice.Issuance import IssuanceConfig
from Splice.Types import Round


@dataclass(frozen=True)
class OpenMiningRound:
    """The real Daml `OpenMiningRound` template - a mining round for which
    new rewards can be registered; `AppTransferContext.open_mining_round`
    points to one of these. Real Daml definition:

        template OpenMiningRound
          with
            dso : Party
            round : Round
            amuletPrice : Decimal
            opensAt : Time
            targetClosesAt : Time
            issuingFor : RelTime
            transferConfigUsd : TransferConfig USD
            issuanceConfig : IssuanceConfig
            tickDuration : RelTime
            trafficPrice : Optional Decimal
            rewardConfig : Optional RewardConfig
          where
            signatory dso
            ensure isDefinedRound round
    """

    dso: Party
    round: Round
    amulet_price: Decimal
    opens_at: Timestamp
    target_closes_at: Timestamp
    issuing_for: RelTime
    transfer_config_usd: TransferConfig[USD]
    issuance_config: IssuanceConfig
    tick_duration: RelTime
    traffic_price: Optional[Decimal] = None
    reward_config: Optional[RewardConfig] = None


@dataclass(frozen=True)
class OpenMiningRound_Fetch:
    """`OpenMiningRound`'s `OpenMiningRound_Fetch` choice - a `nonconsuming`
    read of the round, used to force a specific party to be an informee of
    the read. Its result IS `OpenMiningRound` itself. Real Daml:

        nonconsuming choice OpenMiningRound_Fetch : OpenMiningRound
          with
            p : Party
          controller p
          do pure this
    """

    p: Party


@dataclass(frozen=True)
class SummarizingMiningRound:
    """The real Daml `SummarizingMiningRound` template - a mining round for
    which the total sum of registered rewards is being computed; rewards
    can no longer be registered against it. Real Daml definition:

        template SummarizingMiningRound
          with
            dso : Party
            round : Round
            amuletPrice : Decimal
            issuanceConfig : IssuanceConfig
            tickDuration : RelTime
            trafficPrice : Optional Decimal
            rewardConfig : Optional RewardConfig
          where
            signatory dso
    """

    dso: Party
    round: Round
    amulet_price: Decimal
    issuance_config: IssuanceConfig
    tick_duration: RelTime
    traffic_price: Optional[Decimal] = None
    reward_config: Optional[RewardConfig] = None


@dataclass(frozen=True)
class IssuingMiningRound:
    """The real Daml `IssuingMiningRound` template - a mining round for
    whose rewards Amulet is being issued. Real Daml definition:

        template IssuingMiningRound
          with
            dso : Party
            round : Round
            issuancePerValidatorRewardCoupon : Decimal
            issuancePerFeaturedAppRewardCoupon : Decimal
            issuancePerUnfeaturedAppRewardCoupon : Decimal
            issuancePerSvRewardCoupon : Decimal
            opensAt : Time
            targetClosesAt : Time
            optIssuancePerValidatorFaucetCoupon : Optional Decimal
          where
            signatory dso
    """

    dso: Party
    round: Round
    issuance_per_validator_reward_coupon: Decimal
    issuance_per_featured_app_reward_coupon: Decimal
    issuance_per_unfeatured_app_reward_coupon: Decimal
    issuance_per_sv_reward_coupon: Decimal
    opens_at: Timestamp
    target_closes_at: Timestamp
    opt_issuance_per_validator_faucet_coupon: Optional[Decimal] = None


@dataclass(frozen=True)
class ClosedMiningRound:
    """The real Daml `ClosedMiningRound` template - a record that a mining
    round has been closed, used to archive expired rewards. Real Daml
    definition:

        template ClosedMiningRound
          with
            dso : Party
            round : Round
            issuancePerValidatorRewardCoupon : Decimal
            issuancePerFeaturedAppRewardCoupon : Decimal
            issuancePerUnfeaturedAppRewardCoupon : Decimal
            issuancePerSvRewardCoupon : Decimal
            optIssuancePerValidatorFaucetCoupon : Optional Decimal
          where
            signatory dso
    """

    dso: Party
    round: Round
    issuance_per_validator_reward_coupon: Decimal
    issuance_per_featured_app_reward_coupon: Decimal
    issuance_per_unfeatured_app_reward_coupon: Decimal
    issuance_per_sv_reward_coupon: Decimal
    opt_issuance_per_validator_faucet_coupon: Optional[Decimal] = None
