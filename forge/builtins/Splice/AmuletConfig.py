"""Stand-in for the real `Splice.AmuletConfig` Daml module
(`splice/daml/splice-amulet/daml/Splice/AmuletConfig.daml`) - IDE/authoring
support only, see `Splice/__init__.py`.
"""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Annotated, Generic, Optional, TypeVar

from forge.models.types import RelTime, Text
from .DecentralizedSynchronizer import AmuletDecentralizedSynchronizerConfig
from .Fees import FixedFee, RatePerRound, SteppedRate
from .Issuance import IssuanceConfig
from .Schedule import Schedule
from .. import DamlName


class USD:
    """The real Daml `USD` singleton - a "unit tag" used only as
    `TransferConfig`'s type parameter (`TransferConfig USD`), never
    constructed with any data of its own. Real Daml definition:

        data USD = USD deriving (Show, Eq)
    """


Unit = TypeVar("Unit")


@dataclass(frozen=True)
class TransferConfig(Generic[Unit]):
    """The real Daml `TransferConfig unit` record - fee/limit configuration
    for Amulet transfers, denominated in a currency unit given by the type
    parameter (`TransferConfig[USD]` in every real usage). Real Daml
    definition:

        data TransferConfig unit = TransferConfig with
            createFee : FixedFee
            holdingFee : RatePerRound
            transferFee : SteppedRate
            lockHolderFee : FixedFee
            extraFeaturedAppRewardAmount : Decimal
            maxNumInputs : Int
            maxNumOutputs : Int
            maxNumLockHolders : Int
            tokenStandardMaxTTL : Optional RelTime
          deriving (Eq, Show)
    """

    create_fee: Annotated[FixedFee, DamlName("createFee")]
    holding_fee: Annotated[RatePerRound, DamlName("holdingFee")]
    transfer_fee: Annotated[SteppedRate, DamlName("transferFee")]
    lock_holder_fee: Annotated[FixedFee, DamlName("lockHolderFee")]
    extra_featured_app_reward_amount: Annotated[Decimal, DamlName("extraFeaturedAppRewardAmount")]
    max_num_inputs: Annotated[int, DamlName("maxNumInputs")]
    max_num_outputs: Annotated[int, DamlName("maxNumOutputs")]
    max_num_lock_holders: Annotated[int, DamlName("maxNumLockHolders")]
    token_standard_max_ttl: Annotated[Optional[RelTime], DamlName("tokenStandardMaxTTL")] = None


@dataclass(frozen=True)
class TransferConfigV2(Generic[Unit]):
    """The real Daml `TransferConfigV2 unit` record - a leaner successor to
    `TransferConfig` (drops `createFee`/`transferFee`/
    `extraFeaturedAppRewardAmount`, kept for contracts already using it, e.g.
    `ExternalPartyConfigState`). Real Daml definition:

        data TransferConfigV2 unit = TransferConfigV2 with
            holdingFee : RatePerRound
            maxNumInputs : Int
            maxNumOutputs : Int
            maxNumLockHolders : Int
            tokenStandardMaxTTL : Optional RelTime
          deriving (Eq, Show)
    """

    holding_fee: Annotated[RatePerRound, DamlName("holdingFee")]
    max_num_inputs: Annotated[int, DamlName("maxNumInputs")]
    max_num_outputs: Annotated[int, DamlName("maxNumOutputs")]
    max_num_lock_holders: Annotated[int, DamlName("maxNumLockHolders")]
    token_standard_max_ttl: Annotated[Optional[RelTime], DamlName("tokenStandardMaxTTL")] = None


@dataclass(frozen=True)
class PackageConfig:
    """The real Daml `PackageConfig` record - which package version each
    Splice app should target for command submissions. Real Daml definition:

        data PackageConfig = PackageConfig
          with
            amulet : Text
            amuletNameService : Text
            dsoGovernance : Text
            validatorLifecycle : Text
            wallet : Text
            walletPayments : Text
          deriving (Show, Eq)
    """

    amulet: Text
    amulet_name_service: Annotated[Text, DamlName("amuletNameService")]
    dso_governance: Annotated[Text, DamlName("dsoGovernance")]
    validator_lifecycle: Annotated[Text, DamlName("validatorLifecycle")]
    wallet: Text
    wallet_payments: Annotated[Text, DamlName("walletPayments")]


@dataclass(frozen=True)
class AmuletConfig(Generic[Unit]):
    """The real Daml `AmuletConfig unit` record - the full network
    configuration `AmuletRules.config_schedule` schedules over time. Real
    Daml definition:

        data AmuletConfig unit = AmuletConfig with
            transferConfig : TransferConfig unit
            issuanceCurve : Schedule RelTime IssuanceConfig
            decentralizedSynchronizer : AmuletDecentralizedSynchronizerConfig
            tickDuration : RelTime
            packageConfig : PackageConfig
            transferPreapprovalFee : Optional Decimal
            featuredAppActivityMarkerAmount : Optional Decimal
          deriving (Show, Eq)
    """

    transfer_config: Annotated[TransferConfig[Unit], DamlName("transferConfig")]
    issuance_curve: Annotated[Schedule[RelTime, IssuanceConfig], DamlName("issuanceCurve")]
    decentralized_synchronizer: Annotated[AmuletDecentralizedSynchronizerConfig, DamlName("decentralizedSynchronizer")]
    tick_duration: Annotated[RelTime, DamlName("tickDuration")]
    package_config: Annotated[PackageConfig, DamlName("packageConfig")]
    transfer_preapproval_fee: Annotated[Optional[Decimal], DamlName("transferPreapprovalFee")] = None
    featured_app_activity_marker_amount: Annotated[Optional[Decimal], DamlName("featuredAppActivityMarkerAmount")] = None


class RewardVersion(Enum):
    """Mirrors the real Daml `RewardVersion` variant - which scheme is used
    for minting app/validator rewards. Real Daml definition:

        data RewardVersion
          = RewardVersion_FeaturedAppMarkers
          | RewardVersion_TrafficBasedAppRewards
          deriving (Eq, Show)
    """

    FEATURED_APP_MARKERS = "RewardVersion_FeaturedAppMarkers"
    TRAFFIC_BASED_APP_REWARDS = "RewardVersion_TrafficBasedAppRewards"


@dataclass(frozen=True)
class RewardConfig:
    """The real Daml `RewardConfig` record - off-ledger reward calculation
    configuration for a mining round. Real Daml definition:

        data RewardConfig = RewardConfig with
            mintingVersion : RewardVersion
            dryRunVersion : Optional RewardVersion
            batchSize : Int
            rewardCouponTimeToLive : RelTime
            appRewardCouponThreshold : Decimal
          deriving (Eq, Show)
    """

    minting_version: Annotated[RewardVersion, DamlName("mintingVersion")]
    dry_run_version: Annotated[Optional[RewardVersion], DamlName("dryRunVersion")]
    batch_size: Annotated[int, DamlName("batchSize")]
    reward_coupon_time_to_live: Annotated[RelTime, DamlName("rewardCouponTimeToLive")]
    app_reward_coupon_threshold: Annotated[Decimal, DamlName("appRewardCouponThreshold")]
