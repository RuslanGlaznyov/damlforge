"""Stand-in for the real `Splice.AmuletConfig` Daml module
(`splice/daml/splice-amulet/daml/Splice/AmuletConfig.daml`) - IDE/authoring
support only, see `Splice/__init__.py`.
"""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Generic, Optional, TypeVar

from forge.models.types import RelTime, Text
from .DecentralizedSynchronizer import AmuletDecentralizedSynchronizerConfig
from .Fees import FixedFee, RatePerRound, SteppedRate
from .Issuance import IssuanceConfig
from .Schedule import Schedule


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

    create_fee: FixedFee
    holding_fee: RatePerRound
    transfer_fee: SteppedRate
    lock_holder_fee: FixedFee
    extra_featured_app_reward_amount: Decimal
    max_num_inputs: int
    max_num_outputs: int
    max_num_lock_holders: int
    token_standard_max_ttl: Optional[RelTime] = None


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

    holding_fee: RatePerRound
    max_num_inputs: int
    max_num_outputs: int
    max_num_lock_holders: int
    token_standard_max_ttl: Optional[RelTime] = None


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
    amulet_name_service: Text
    dso_governance: Text
    validator_lifecycle: Text
    wallet: Text
    wallet_payments: Text


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

    transfer_config: TransferConfig[Unit]
    issuance_curve: Schedule[RelTime, IssuanceConfig]
    decentralized_synchronizer: AmuletDecentralizedSynchronizerConfig
    tick_duration: RelTime
    package_config: PackageConfig
    transfer_preapproval_fee: Optional[Decimal] = None
    featured_app_activity_marker_amount: Optional[Decimal] = None


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

    minting_version: RewardVersion
    dry_run_version: Optional[RewardVersion]
    batch_size: int
    reward_coupon_time_to_live: RelTime
    app_reward_coupon_threshold: Decimal
