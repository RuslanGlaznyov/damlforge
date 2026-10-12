from datetime import datetime, timedelta
from typing import Annotated, Generic, TypeVar

from forge.models import Decimal, Optional, Party, TextMap, variant
from forge.builtins import DamlName
from Splice.DecentralizedSynchronizer import AmuletDecentralizedSynchronizerConfig
from Splice.Fees import FixedFee, RatePerRound, SteppedRate
from Splice.Issuance import IssuanceConfig
from Splice.Schedule import Schedule

A = TypeVar("A")
Unit = TypeVar("Unit")


@variant
class RewardVersion:
    def RewardVersion_FeaturedAppMarkers(): pass
    def RewardVersion_TrafficBasedAppRewards(): pass


@variant
class USD:
    def USD(): pass


@variant
class Amulet:
    def Amulet(): pass


struct TransferConfig(Generic[Unit]):
    create_fee: Annotated[FixedFee, DamlName("createFee")]
    holding_fee: Annotated[RatePerRound, DamlName("holdingFee")]
    transfer_fee: Annotated[SteppedRate, DamlName("transferFee")]
    lock_holder_fee: Annotated[FixedFee, DamlName("lockHolderFee")]
    extra_featured_app_reward_amount: Annotated[Decimal, DamlName("extraFeaturedAppRewardAmount")]
    max_num_inputs: Annotated[int, DamlName("maxNumInputs")]
    max_num_outputs: Annotated[int, DamlName("maxNumOutputs")]
    max_num_lock_holders: Annotated[int, DamlName("maxNumLockHolders")]
    token_standard_max_ttl: Annotated[Optional[timedelta], DamlName("tokenStandardMaxTTL")]


struct TransferConfigV2(Generic[Unit]):
    holding_fee: Annotated[RatePerRound, DamlName("holdingFee")]
    max_num_inputs: Annotated[int, DamlName("maxNumInputs")]
    max_num_outputs: Annotated[int, DamlName("maxNumOutputs")]
    max_num_lock_holders: Annotated[int, DamlName("maxNumLockHolders")]
    token_standard_max_ttl: Annotated[Optional[timedelta], DamlName("tokenStandardMaxTTL")]


struct RewardConfig:
    minting_version: Annotated[RewardVersion, DamlName("mintingVersion")]
    dry_run_version: Annotated[Optional[RewardVersion], DamlName("dryRunVersion")]
    batch_size: Annotated[int, DamlName("batchSize")]
    reward_coupon_time_to_live: Annotated[timedelta, DamlName("rewardCouponTimeToLive")]
    app_reward_coupon_threshold: Annotated[Decimal, DamlName("appRewardCouponThreshold")]


struct AmuletConfig(Generic[Unit]):
    transfer_config: Annotated[TransferConfig[Unit], DamlName("transferConfig")]
    issuance_curve: Annotated[Schedule[timedelta, IssuanceConfig], DamlName("issuanceCurve")]
    decentralized_synchronizer: Annotated[AmuletDecentralizedSynchronizerConfig, DamlName("decentralizedSynchronizer")]
    tick_duration: Annotated[timedelta, DamlName("tickDuration")]
    package_config: Annotated[PackageConfig, DamlName("packageConfig")]
    transfer_preapproval_fee: Annotated[Optional[Decimal], DamlName("transferPreapprovalFee")]
    featured_app_activity_marker_amount: Annotated[Optional[Decimal], DamlName("featuredAppActivityMarkerAmount")]
    opt_development_fund_manager: Annotated[Optional[Party], DamlName("optDevelopmentFundManager")]
    external_party_config_state_tick_duration: Annotated[Optional[timedelta], DamlName("externalPartyConfigStateTickDuration")]
    reward_config: Annotated[Optional[RewardConfig], DamlName("rewardConfig")]
    transfer_preapproval_base_duration: Annotated[Optional[timedelta], DamlName("transferPreapprovalBaseDuration")]
    development_fund_manager_blacklist: Annotated[Optional[list[Party]], DamlName("developmentFundManagerBlacklist")]
    min_development_fund_minting_delay: Annotated[Optional[timedelta], DamlName("minDevelopmentFundMintingDelay")]
    amulet_switch_over_times: Annotated[Optional[TextMap[datetime]], DamlName("amuletSwitchOverTimes")]


struct PackageConfig:
    amulet: str
    amulet_name_service: Annotated[str, DamlName("amuletNameService")]
    dso_governance: Annotated[str, DamlName("dsoGovernance")]
    validator_lifecycle: Annotated[str, DamlName("validatorLifecycle")]
    wallet: str
    wallet_payments: Annotated[str, DamlName("walletPayments")]


@DamlName("transferConfigToTransferConfigV2")
def transfer_config_to_transfer_config_v2(tc: TransferConfig[Unit]) -> TransferConfigV2[Unit]:
    pass


@DamlName("getTokenStandardMaxTTL")
def get_token_standard_max_ttl(config: TransferConfigV2[Unit]) -> timedelta:
    pass


@DamlName("useTrafficBasedAppRewards")
def use_traffic_based_app_rewards(rv: Optional[RewardVersion]) -> bool:
    pass


@DamlName("useFeaturedAppMarkers")
def use_featured_app_markers(optional: Optional[RewardVersion]) -> bool:
    pass


@DamlName("getExternalPartyConfigStateTickDuration")
def get_external_party_config_state_tick_duration(config: AmuletConfig[A]) -> timedelta:
    pass


@DamlName("getDevelopmentFundManagerBlacklist")
def get_development_fund_manager_blacklist(config: AmuletConfig[Unit]) -> list[Party]:
    pass


@DamlName("defaultTransferPreapprovalFee")
def default_transfer_preapproval_fee() -> Decimal:
    pass


@DamlName("defaultTransferPreapprovalBaseDuration")
def default_transfer_preapproval_base_duration() -> timedelta:
    pass


@DamlName("getTransferPreapprovalBaseDuration")
def get_transfer_preapproval_base_duration(config: AmuletConfig[Unit]) -> timedelta:
    pass


@DamlName("validAmuletConfig")
def valid_amulet_config(amulet_config: AmuletConfig[Unit]) -> bool:
    pass


@DamlName("validTransferConfig")
def valid_transfer_config(transfer_config: TransferConfig[Unit]) -> bool:
    pass


@DamlName("validRewardConfig")
def valid_reward_config(reward_config: RewardConfig) -> bool:
    pass


@DamlName("validPackageConfig")
def valid_package_config(package_config: PackageConfig) -> bool:
    pass
