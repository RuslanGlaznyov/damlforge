from datetime import datetime, timedelta
from typing import Annotated, TypeVar

from forge.models import choice, ContractId, Decimal, GenMap, Optional, Party, template, variant, variant_record
from forge.builtins import DamlCaseAccessor, DamlName, no_derive
from DA.Internal.Fail.Types import FailureStatus
from DA.Types import Either
from Splice.Amulet import Amulet, AmuletCreateSummary, AppRewardCoupon, DevelopmentFundCoupon, FeaturedAppActivityMarker, FeaturedAppRight, LockedAmulet, RewardCouponV2, SvRewardCoupon, UnclaimedActivityRecord, UnclaimedDevelopmentFundCoupon, UnclaimedReward, ValidatorRewardCoupon, ValidatorRight
from Splice.Amulet.CryptoHash import Hash
from Splice.Amulet.RewardAccountingV2 import CalculateRewardsV2, ProcessRewardsV2
from Splice.AmuletConfig import AmuletConfig, RewardVersion, TransferConfig, TransferConfigV2, USD
from Splice.Api.FeaturedAppRightV1 import AppRewardBeneficiary
from Splice.Api.Token.HoldingV1 import Holding
from Splice.Api.Token.MetadataV1 import ChoiceContext, Metadata
from Splice.Api.Token.TransferEventsV2 import EventLog, EventLog_HoldingsChange
from Splice.Api.Token.TransferInstructionV1 import TransferInstruction, TransferInstructionResult
from Splice.DecentralizedSynchronizer import MemberTraffic
from Splice.Expiry import TimeLock
from Splice.ExternalPartyConfigState import ExternalPartyConfigState
from Splice.Issuance import OpenMiningRoundSummary
from Splice.Round import ClosedMiningRound, IssuingMiningRound, OpenMiningRound, SummarizingMiningRound
from Splice.Schedule import Schedule
from Splice.Types import Round
from Splice.ValidatorLicense import ValidatorFaucetCoupon, ValidatorLivenessActivityRecord

Unit = TypeVar("Unit")


TransferOutputsSummary = list[PreprocessedTransferOutput]


@variant
class TransferPreapproval_CancelResult:
    def TransferPreapproval_CancelResult(): pass


@variant
class TransferInput:
    def InputAppRewardCoupon(value: ContractId[AppRewardCoupon]): pass
    def InputValidatorRewardCoupon(value: ContractId[ValidatorRewardCoupon]): pass
    def InputSvRewardCoupon(value: ContractId[SvRewardCoupon]): pass
    def InputAmulet(value: ContractId[Amulet]): pass
    @variant_record
    def ExtTransferInput(dummy_unit_field: Annotated[None, DamlName("dummyUnitField")], opt_input_validator_faucet_coupon: Annotated[Optional[ContractId[ValidatorFaucetCoupon]], DamlName("optInputValidatorFaucetCoupon")]): pass
    def InputValidatorLivenessActivityRecord(value: ContractId[ValidatorLivenessActivityRecord]): pass
    def InputUnclaimedActivityRecord(value: ContractId[UnclaimedActivityRecord]): pass
    def InputDevelopmentFundCoupon(value: ContractId[DevelopmentFundCoupon]): pass
    def InputRewardCouponV2(value: ContractId[RewardCouponV2]): pass


@variant
class CreatedAmulet:
    def TransferResultAmulet(value: ContractId[Amulet]): pass
    def TransferResultLockedAmulet(value: ContractId[LockedAmulet]): pass
    @variant_record
    def ExtCreatedAmulet(dummy_unit_field: Annotated[None, DamlName("dummyUnitField")]): pass


@variant
class InvalidTransferReason:
    @variant_record
    def ITR_InsufficientFunds(missing_amount: Annotated[Decimal, DamlName("missingAmount")]): pass
    @variant_record
    def ITR_UnknownSynchronizer(synchronizer_id: Annotated[str, DamlName("synchronizerId")]): pass
    @variant_record
    def ITR_InsufficientTopupAmount(requested_topup_amount: Annotated[int, DamlName("requestedTopupAmount")], min_topup_amount: Annotated[int, DamlName("minTopupAmount")]): pass
    @variant_record
    def ITR_Other(description: str): pass
    @variant_record
    def ExtInvalidTransferReason(dummy_unit_field: Annotated[None, DamlName("dummyUnitField")]): pass


@no_derive
@variant
class AmuletRules_MiningRound_ArchiveResult:
    def AmuletRules_MiningRound_ArchiveResult(): pass


@variant
class AmuletRules_BootstrapExternalPartyConfigStateResult:
    def AmuletRules_BootstrapExternalPartyConfigStateResult(): pass


struct AmuletRules_Amulet_ExpireTransferInstructionsResult:
    results: list[TransferInstructionResult]


struct AmuletRules_ExpireTransferInstructionInput:
    transfer_instruction_cid: Annotated[ContractId[TransferInstruction], DamlName("transferInstructionCid")]
    expire_lock: Annotated[bool, DamlName("expireLock")]


@no_derive
struct AmuletRules_ComputeFeesResult:
    fees: list[Decimal]


@no_derive
struct AmuletRules_MergeMemberTrafficContractsResult:
    merged_traffic_cid: Annotated[ContractId[MemberTraffic], DamlName("mergedTrafficCid")]


@no_derive
struct AmuletRules_MintResult:
    amulet_sum: Annotated[AmuletCreateSummary[ContractId[Amulet]], DamlName("amuletSum")]


@no_derive
struct AmuletRules_DevNet_TapResult:
    amulet_sum: Annotated[AmuletCreateSummary[ContractId[Amulet]], DamlName("amuletSum")]
    meta: Optional[Metadata]


@no_derive
struct AmuletRules_DevNet_FeatureAppResult:
    featured_app_right_cid: Annotated[ContractId[FeaturedAppRight], DamlName("featuredAppRightCid")]


@no_derive
struct AmuletRules_Bootstrap_RoundsResult:
    open_mining_round_cid: Annotated[ContractId[OpenMiningRound], DamlName("openMiningRoundCid")]
    initial_round: Annotated[Optional[Round], DamlName("initialRound")]


@no_derive
struct AmuletRules_AdvanceOpenMiningRoundsResult:
    summarizing_round_cid: Annotated[ContractId[SummarizingMiningRound], DamlName("summarizingRoundCid")]
    open_round_cid: Annotated[ContractId[OpenMiningRound], DamlName("openRoundCid")]


@no_derive
struct AmuletRules_MiningRound_StartIssuingResult:
    issuing_round_cid: Annotated[ContractId[IssuingMiningRound], DamlName("issuingRoundCid")]
    unclaimed_development_fund_coupon_cid: Annotated[Optional[ContractId[UnclaimedDevelopmentFundCoupon]], DamlName("unclaimedDevelopmentFundCouponCid")]


@no_derive
struct AmuletRules_MiningRound_CloseResult:
    closed_round_cid: Annotated[ContractId[ClosedMiningRound], DamlName("closedRoundCid")]


@no_derive
struct AmuletRules_ClaimExpiredRewardsResult:
    unclaimed_reward_cid: Annotated[Optional[ContractId[UnclaimedReward]], DamlName("unclaimedRewardCid")]


@no_derive
struct AmuletRules_ClaimExpiredRewardsV2Result:
    pass


@no_derive
struct AmuletRules_StartProcessingRewardsV2Result:
    pass


@no_derive
struct AmuletRules_UnhideRewardCouponsV2Result:
    pass


@no_derive
struct AmuletRules_ArchiveDryRunRewardAccountingV2Result:
    pass


@no_derive
struct AmuletRules_MergeUnclaimedRewardsResult:
    unclaimed_reward_cid: Annotated[ContractId[UnclaimedReward], DamlName("unclaimedRewardCid")]


@no_derive
struct AmuletRules_MergeUnclaimedDevelopmentFundCouponsResult:
    unclaimed_development_fund_coupon_cid: Annotated[ContractId[UnclaimedDevelopmentFundCoupon], DamlName("unclaimedDevelopmentFundCouponCid")]


@no_derive
struct AmuletRules_AllocateDevelopmentFundCouponResult:
    development_fund_coupon_cid: Annotated[ContractId[DevelopmentFundCoupon], DamlName("developmentFundCouponCid")]
    opt_unclaimed_development_fund_coupon_cid: Annotated[Optional[ContractId[UnclaimedDevelopmentFundCoupon]], DamlName("optUnclaimedDevelopmentFundCouponCid")]


@no_derive
struct AmuletRules_SetConfigResult:
    new_amulet_rules: Annotated[ContractId[AmuletRules], DamlName("newAmuletRules")]


@no_derive
struct AmuletRules_AddFutureAmuletConfigScheduleResult:
    new_amulet_rules: Annotated[ContractId[AmuletRules], DamlName("newAmuletRules")]


@no_derive
struct AmuletRules_RemoveFutureAmuletConfigScheduleResult:
    new_amulet_rules: Annotated[ContractId[AmuletRules], DamlName("newAmuletRules")]


@no_derive
struct AmuletRules_UpdateFutureAmuletConfigScheduleResult:
    new_amulet_rules: Annotated[ContractId[AmuletRules], DamlName("newAmuletRules")]


@no_derive
struct AmuletRules_ConvertFeaturedAppActivityMarkersResult:
    app_reward_coupon_cids: Annotated[list[ContractId[AppRewardCoupon]], DamlName("appRewardCouponCids")]


struct AmuletRules_UpdateExternalPartyConfigStatesResult:
    new_external_party_config_state_cid: Annotated[ContractId[ExternalPartyConfigState], DamlName("newExternalPartyConfigStateCid")]


struct OpenMiningRoundTriple:
    round0_cid: Annotated[ContractId[OpenMiningRound], DamlName("round0Cid")]
    round1_cid: Annotated[ContractId[OpenMiningRound], DamlName("round1Cid")]
    round2_cid: Annotated[ContractId[OpenMiningRound], DamlName("round2Cid")]


struct ValidatedOpenMiningRounds:
    oldest_round: Annotated[OpenMiningRound, DamlName("oldestRound")]
    latest_usable_round: Annotated[OpenMiningRound, DamlName("latestUsableRound")]


@no_derive
struct RewardsIssuanceConfig:
    issue_app_rewards: Annotated[bool, DamlName("issueAppRewards")]
    issue_validator_rewards: Annotated[bool, DamlName("issueValidatorRewards")]


struct TransferContextSummary:
    featured_app_provider: Annotated[Optional[Party], DamlName("featuredAppProvider")]
    config: TransferConfig[Amulet]
    open_round: Annotated[OpenMiningRound, DamlName("openRound")]
    issuing_mining_rounds: Annotated[GenMap[Round, IssuingMiningRound], DamlName("issuingMiningRounds")]
    validator_rights: Annotated[GenMap[Party, ContractId[ValidatorRight]], DamlName("validatorRights")]


struct TransferContextSummaryV2:
    dso: Party
    featured_app_provider: Annotated[Optional[Party], DamlName("featuredAppProvider")]
    config: TransferConfigV2[Amulet]
    open_round_number: Annotated[Round, DamlName("openRoundNumber")]
    amulet_price: Annotated[Decimal, DamlName("amuletPrice")]
    issuing_mining_rounds: Annotated[GenMap[Round, IssuingMiningRound], DamlName("issuingMiningRounds")]
    validator_rights: Annotated[GenMap[Party, ContractId[ValidatorRight]], DamlName("validatorRights")]
    reward_calculation_version: Annotated[Optional[RewardVersion], DamlName("rewardCalculationVersion")]
    event_log_cid: Annotated[Optional[ContractId[EventLog]], DamlName("eventLogCid")]
    development_fund_manager_blacklist: Annotated[Optional[list[Party]], DamlName("developmentFundManagerBlacklist")]


struct TransferInputsSummary:
    total_amulet_amount: Annotated[Decimal, DamlName("totalAmuletAmount")]
    total_app_reward_amount: Annotated[Decimal, DamlName("totalAppRewardAmount")]
    total_validator_reward_amount: Annotated[Decimal, DamlName("totalValidatorRewardAmount")]
    total_validator_faucet_amount: Annotated[Decimal, DamlName("totalValidatorFaucetAmount")]
    total_sv_reward_amount: Annotated[Decimal, DamlName("totalSvRewardAmount")]
    total_holding_fees: Annotated[Decimal, DamlName("totalHoldingFees")]
    amount_archived_as_of_round_zero: Annotated[Decimal, DamlName("amountArchivedAsOfRoundZero")]
    change_to_holding_fees_rate: Annotated[Decimal, DamlName("changeToHoldingFeesRate")]
    total_unclaimed_activity_record_amount: Annotated[Optional[Decimal], DamlName("totalUnclaimedActivityRecordAmount")]
    total_development_fund_amount: Annotated[Optional[Decimal], DamlName("totalDevelopmentFundAmount")]


struct PreprocessedTransferOutput:
    owner: Party
    output_fee: Annotated[Decimal, DamlName("outputFee")]
    amount: Decimal
    lock: Optional[TimeLock]
    meta: Optional[Metadata]


struct AppTransferContext:
    amulet_rules: Annotated[ContractId[AmuletRules], DamlName("amuletRules")]
    open_mining_round: Annotated[ContractId[OpenMiningRound], DamlName("openMiningRound")]
    featured_app_right: Annotated[Optional[ContractId[FeaturedAppRight]], DamlName("featuredAppRight")]


struct PaymentTransferContext:
    amulet_rules: Annotated[ContractId[AmuletRules], DamlName("amuletRules")]
    context: TransferContext


struct TransferContext:
    open_mining_round: Annotated[ContractId[OpenMiningRound], DamlName("openMiningRound")]
    issuing_mining_rounds: Annotated[GenMap[Round, ContractId[IssuingMiningRound]], DamlName("issuingMiningRounds")]
    validator_rights: Annotated[GenMap[Party, ContractId[ValidatorRight]], DamlName("validatorRights")]
    featured_app_right: Annotated[Optional[ContractId[FeaturedAppRight]], DamlName("featuredAppRight")]


struct ExternalPartyTransferContext:
    external_party_config_state: Annotated[ContractId[ExternalPartyConfigState], DamlName("externalPartyConfigState")]
    featured_app_right: Annotated[Optional[ContractId[FeaturedAppRight]], DamlName("featuredAppRight")]


struct Transfer:
    sender: Party
    provider: Party
    inputs: list[TransferInput]
    outputs: list[TransferOutput]
    beneficiaries: Optional[list[AppRewardBeneficiary]]


struct TransferOutput:
    receiver: Party
    receiver_fee_ratio: Annotated[Decimal, DamlName("receiverFeeRatio")]
    amount: Decimal
    lock: Optional[TimeLock]
    meta: Optional[Metadata]


struct TransferResult:
    round: Round
    summary: TransferSummary
    created_amulets: Annotated[list[CreatedAmulet], DamlName("createdAmulets")]
    sender_change_amulet: Annotated[Optional[ContractId[Amulet]], DamlName("senderChangeAmulet")]
    meta: Optional[Metadata]


struct AmuletRules_BuyMemberTrafficResult:
    round: Round
    summary: TransferSummary
    amulet_paid: Annotated[Decimal, DamlName("amuletPaid")]
    purchased_traffic: Annotated[ContractId[MemberTraffic], DamlName("purchasedTraffic")]
    sender_change_amulet: Annotated[Optional[ContractId[Amulet]], DamlName("senderChangeAmulet")]
    meta: Optional[Metadata]


struct AmuletRules_CreateExternalPartySetupProposalResult:
    proposal_cid: Annotated[ContractId[ExternalPartySetupProposal], DamlName("proposalCid")]
    user: Party
    validator: Party
    transfer_result: Annotated[TransferResult, DamlName("transferResult")]
    amulet_paid: Annotated[Decimal, DamlName("amuletPaid")]
    meta: Optional[Metadata]


struct AmuletRules_CreateTransferPreapprovalResult:
    transfer_preapproval_cid: Annotated[ContractId[TransferPreapproval], DamlName("transferPreapprovalCid")]
    transfer_result: Annotated[TransferResult, DamlName("transferResult")]
    amulet_paid: Annotated[Decimal, DamlName("amuletPaid")]
    meta: Optional[Metadata]


struct TransferSummary:
    input_app_reward_amount: Annotated[Decimal, DamlName("inputAppRewardAmount")]
    input_validator_reward_amount: Annotated[Decimal, DamlName("inputValidatorRewardAmount")]
    input_sv_reward_amount: Annotated[Decimal, DamlName("inputSvRewardAmount")]
    input_amulet_amount: Annotated[Decimal, DamlName("inputAmuletAmount")]
    balance_changes: Annotated[GenMap[Party, BalanceChange], DamlName("balanceChanges")]
    holding_fees: Annotated[Decimal, DamlName("holdingFees")]
    output_fees: Annotated[list[Decimal], DamlName("outputFees")]
    sender_change_fee: Annotated[Decimal, DamlName("senderChangeFee")]
    sender_change_amount: Annotated[Decimal, DamlName("senderChangeAmount")]
    amulet_price: Annotated[Decimal, DamlName("amuletPrice")]
    input_validator_faucet_amount: Annotated[Optional[Decimal], DamlName("inputValidatorFaucetAmount")]
    input_unclaimed_activity_record_amount: Annotated[Optional[Decimal], DamlName("inputUnclaimedActivityRecordAmount")]
    input_development_fund_amount: Annotated[Optional[Decimal], DamlName("inputDevelopmentFundAmount")]


struct BalanceChange:
    change_to_initial_amount_as_of_round_zero: Annotated[Decimal, DamlName("changeToInitialAmountAsOfRoundZero")]
    change_to_holding_fees_rate: Annotated[Decimal, DamlName("changeToHoldingFeesRate")]


struct ExternalPartySetupProposal_AcceptResult:
    validator_right_cid: Annotated[ContractId[ValidatorRight], DamlName("validatorRightCid")]
    transfer_preapproval_cid: Annotated[ContractId[TransferPreapproval], DamlName("transferPreapprovalCid")]


struct ExternalPartySetupProposal_RejectResult:
    dummy_arg: Annotated[None, DamlName("dummyArg")]


struct ExternalPartySetupProposal_WithdrawResult:
    dummy_arg: Annotated[None, DamlName("dummyArg")]


struct TransferPreapproval_SendResult:
    result: TransferResult
    meta: Optional[Metadata]


struct TransferPreapproval_SendV2Result:
    result: TransferResult
    meta: Metadata


struct TransferPreapproval_RenewResult:
    transfer_preapproval_cid: Annotated[ContractId[TransferPreapproval], DamlName("transferPreapprovalCid")]
    transfer_result: Annotated[TransferResult, DamlName("transferResult")]
    receiver: Party
    provider: Party
    amulet_paid: Annotated[Decimal, DamlName("amuletPaid")]
    meta: Optional[Metadata]


struct TransferPreapproval_ExpireResult:
    pass


@template
class AmuletRules:
    dso: Party
    config_schedule: Annotated[Schedule[datetime, AmuletConfig[USD]], DamlName("configSchedule")]
    is_dev_net: Annotated[bool, DamlName("isDevNet")]
    contract_state_schema_version: Annotated[Optional[int], DamlName("contractStateSchemaVersion")]

    signatory: list[Party] = [dso]

    @choice(controller=[transfer.sender, transfer.provider], consuming="nonconsuming")
    def AmuletRules_Transfer(self, transfer: Transfer, context: TransferContext, expected_dso: Annotated[Optional[Party], DamlName("expectedDso")]) -> TransferResult:
        pass

    @choice(controller=provider, consuming="nonconsuming")
    def AmuletRules_BuyMemberTraffic(self, inputs: list[TransferInput], context: TransferContext, provider: Party, member_id: Annotated[str, DamlName("memberId")], synchronizer_id: Annotated[str, DamlName("synchronizerId")], migration_id: Annotated[int, DamlName("migrationId")], traffic_amount: Annotated[int, DamlName("trafficAmount")], expected_dso: Annotated[Optional[Party], DamlName("expectedDso")]) -> AmuletRules_BuyMemberTrafficResult:
        pass

    @choice(controller=validator, consuming="nonconsuming")
    def AmuletRules_CreateExternalPartySetupProposal(self, context: PaymentTransferContext, inputs: list[TransferInput], user: Party, validator: Party, preapproval_expires_at: Annotated[datetime, DamlName("preapprovalExpiresAt")], expected_dso: Annotated[Optional[Party], DamlName("expectedDso")], opt_created_at: Annotated[Optional[datetime], DamlName("optCreatedAt")]) -> AmuletRules_CreateExternalPartySetupProposalResult:
        pass

    @choice(controller=[receiver, provider], consuming="nonconsuming")
    def AmuletRules_CreateTransferPreapproval(self, context: PaymentTransferContext, inputs: list[TransferInput], receiver: Party, provider: Party, expires_at: Annotated[datetime, DamlName("expiresAt")], expected_dso: Annotated[Optional[Party], DamlName("expectedDso")], opt_created_at: Annotated[Optional[datetime], DamlName("optCreatedAt")]) -> AmuletRules_CreateTransferPreapprovalResult:
        pass

    @choice(controller=dso, consuming="nonconsuming", observer=expiry_observers)
    def AmuletRules_ClaimExpiredRewardsV2(self, reward_coupon_cids: Annotated[list[ContractId[RewardCouponV2]], DamlName("rewardCouponCids")], expiry_observers: Annotated[list[Party], DamlName("expiryObservers")]) -> AmuletRules_ClaimExpiredRewardsV2Result:
        pass

    @choice(controller=dso, consuming="nonconsuming", observer=providers)
    def AmuletRules_UnhideRewardCouponsV2(self, reward_coupon_cids: Annotated[list[ContractId[RewardCouponV2]], DamlName("rewardCouponCids")], providers: list[Party]) -> AmuletRules_UnhideRewardCouponsV2Result:
        pass

    @choice(controller=dso, consuming="nonconsuming")
    def AmuletRules_ConvertFeaturedAppActivityMarkers(self, marker_cids: Annotated[list[ContractId[FeaturedAppActivityMarker]], DamlName("markerCids")], open_mining_round_cid: Annotated[ContractId[OpenMiningRound], DamlName("openMiningRoundCid")], observers: Optional[list[Party]]) -> AmuletRules_ConvertFeaturedAppActivityMarkersResult:
        pass

    @choice(controller=dso, consuming="nonconsuming")
    def AmuletRules_ClaimExpiredRewards(self, closed_round_cid: Annotated[ContractId[ClosedMiningRound], DamlName("closedRoundCid")], validator_reward_coupon_cids: Annotated[list[ContractId[ValidatorRewardCoupon]], DamlName("validatorRewardCouponCids")], app_coupon_cids: Annotated[list[ContractId[AppRewardCoupon]], DamlName("appCouponCids")], sv_reward_coupon_cids: Annotated[list[ContractId[SvRewardCoupon]], DamlName("svRewardCouponCids")], opt_validator_faucet_coupon_cids: Annotated[Optional[list[ContractId[ValidatorFaucetCoupon]]], DamlName("optValidatorFaucetCouponCids")], opt_validator_liveness_activity_record_cids: Annotated[Optional[list[ContractId[ValidatorLivenessActivityRecord]]], DamlName("optValidatorLivenessActivityRecordCids")]) -> AmuletRules_ClaimExpiredRewardsResult:
        pass

    @choice(controller=dso, consuming="nonconsuming")
    def AmuletRules_Bootstrap_Rounds(self, amulet_price: Annotated[Decimal, DamlName("amuletPrice")], round0_duration: Annotated[timedelta, DamlName("round0Duration")], initial_round: Annotated[Optional[int], DamlName("initialRound")]) -> AmuletRules_Bootstrap_RoundsResult:
        pass

    @choice(controller=dso, consuming="nonconsuming")
    def AmuletRules_AdvanceOpenMiningRounds(self, amulet_price: Annotated[Decimal, DamlName("amuletPrice")], round_to_archive_cid: Annotated[ContractId[OpenMiningRound], DamlName("roundToArchiveCid")], middle_round_cid: Annotated[ContractId[OpenMiningRound], DamlName("middleRoundCid")], latest_round_cid: Annotated[ContractId[OpenMiningRound], DamlName("latestRoundCid")]) -> AmuletRules_AdvanceOpenMiningRoundsResult:
        pass

    @choice(controller=dso, consuming="nonconsuming")
    def AmuletRules_MiningRound_StartIssuing(self, mining_round_cid: Annotated[ContractId[SummarizingMiningRound], DamlName("miningRoundCid")], summary: OpenMiningRoundSummary) -> AmuletRules_MiningRound_StartIssuingResult:
        pass

    @choice(controller=dso, consuming="nonconsuming")
    def AmuletRules_MiningRound_Close(self, issuing_round_cid: Annotated[ContractId[IssuingMiningRound], DamlName("issuingRoundCid")]) -> AmuletRules_MiningRound_CloseResult:
        pass

    @choice(controller=dso, consuming="nonconsuming")
    def AmuletRules_UpdateExternalPartyConfigStates(self, external_party_config_state_cid0: Annotated[ContractId[ExternalPartyConfigState], DamlName("externalPartyConfigStateCid0")], external_party_config_state_cid1: Annotated[ContractId[ExternalPartyConfigState], DamlName("externalPartyConfigStateCid1")], open_mining_round_triple: Annotated[OpenMiningRoundTriple, DamlName("openMiningRoundTriple")]) -> AmuletRules_UpdateExternalPartyConfigStatesResult:
        pass

    @choice(controller=dso, consuming="nonconsuming")
    def AmuletRules_BootstrapExternalPartyConfigState(self, open_mining_round_triple: Annotated[OpenMiningRoundTriple, DamlName("openMiningRoundTriple")], expected_dso: Annotated[Party, DamlName("expectedDso")]) -> AmuletRules_BootstrapExternalPartyConfigStateResult:
        pass

    @choice(controller=dso, consuming="nonconsuming")
    def AmuletRules_MergeMemberTrafficContracts(self, traffic_cids: Annotated[list[ContractId[MemberTraffic]], DamlName("trafficCids")]) -> AmuletRules_MergeMemberTrafficContractsResult:
        pass

    @choice(controller=[dso, receiver], consuming="nonconsuming")
    def AmuletRules_Mint(self, receiver: Party, amount: Decimal, open_round: Annotated[ContractId[OpenMiningRound], DamlName("openRound")], reason: Optional[str]) -> AmuletRules_MintResult:
        pass

    @choice(controller=receiver, consuming="nonconsuming")
    def AmuletRules_DevNet_Tap(self, receiver: Party, amount: Decimal, open_round: Annotated[ContractId[OpenMiningRound], DamlName("openRound")]) -> AmuletRules_DevNet_TapResult:
        pass

    @choice(controller=provider, consuming="nonconsuming")
    def AmuletRules_DevNet_FeatureApp(self, provider: Party, activity_weight: Annotated[Optional[Decimal], DamlName("activityWeight")]) -> AmuletRules_DevNet_FeatureAppResult:
        pass

    @choice(controller=dso, consuming="nonconsuming")
    def AmuletRules_MiningRound_Archive(self, closed_round_cid: Annotated[ContractId[ClosedMiningRound], DamlName("closedRoundCid")]) -> AmuletRules_MiningRound_ArchiveResult:
        pass

    @choice(controller=dso, consuming="nonconsuming")
    def AmuletRules_StartProcessingRewardsV2(self, calculate_rewards_cid: Annotated[ContractId[CalculateRewardsV2], DamlName("calculateRewardsCid")], batch_hash: Annotated[Hash, DamlName("batchHash")]) -> AmuletRules_StartProcessingRewardsV2Result:
        pass

    @choice(controller=dso, consuming="nonconsuming")
    def AmuletRules_ArchiveDryRunRewardAccountingV2(self, calculate_rewards_cids: Annotated[list[ContractId[CalculateRewardsV2]], DamlName("calculateRewardsCids")], process_rewards_cids: Annotated[list[ContractId[ProcessRewardsV2]], DamlName("processRewardsCids")]) -> AmuletRules_ArchiveDryRunRewardAccountingV2Result:
        pass

    @choice(controller=dso, consuming="nonconsuming")
    def AmuletRules_MergeUnclaimedRewards(self, unclaimed_reward_cids: Annotated[list[ContractId[UnclaimedReward]], DamlName("unclaimedRewardCids")]) -> AmuletRules_MergeUnclaimedRewardsResult:
        pass

    @choice(controller=dso, consuming="nonconsuming")
    def AmuletRules_MergeUnclaimedDevelopmentFundCoupons(self, unclaimed_development_fund_coupon_cids: Annotated[list[ContractId[UnclaimedDevelopmentFundCoupon]], DamlName("unclaimedDevelopmentFundCouponCids")]) -> AmuletRules_MergeUnclaimedDevelopmentFundCouponsResult:
        pass

    @choice(controller=fund_manager, consuming="nonconsuming")
    def AmuletRules_AllocateDevelopmentFundCoupon(self, unclaimed_development_fund_coupon_cids: Annotated[list[ContractId[UnclaimedDevelopmentFundCoupon]], DamlName("unclaimedDevelopmentFundCouponCids")], beneficiary: Party, amount: Decimal, expires_at: Annotated[datetime, DamlName("expiresAt")], reason: str, fund_manager: Annotated[Party, DamlName("fundManager")], mint_after: Annotated[Optional[datetime], DamlName("mintAfter")]) -> AmuletRules_AllocateDevelopmentFundCouponResult:
        pass

    @choice(controller=dso, consuming=True)
    def AmuletRules_SetConfig(self, new_config: Annotated[AmuletConfig[USD], DamlName("newConfig")], base_config: Annotated[AmuletConfig[USD], DamlName("baseConfig")]) -> AmuletRules_SetConfigResult:
        pass

    @choice(controller=dso, consuming="nonconsuming", observer=observers)
    def AmuletRules_Amulet_ExpireTransferInstructions(self, expected_dso: Annotated[Party, DamlName("expectedDso")], inputs: list[AmuletRules_ExpireTransferInstructionInput], observers: list[Party]) -> AmuletRules_Amulet_ExpireTransferInstructionsResult:
        pass

    @choice(controller=p, consuming="nonconsuming")
    def AmuletRules_Fetch(self, p: Party) -> AmuletRules:
        pass

    @choice(controller=sender, consuming="nonconsuming")
    def AmuletRules_ComputeFees(self, context: TransferContext, sender: Party, outputs: list[TransferOutput], expected_dso: Annotated[Optional[Party], DamlName("expectedDso")]) -> AmuletRules_ComputeFeesResult:
        pass

    @choice(controller=dso, consuming=True)
    def AmuletRules_AddFutureAmuletConfigSchedule(self, new_schedule_item: Annotated[tuple[datetime, AmuletConfig[USD]], DamlName("newScheduleItem")]) -> AmuletRules_AddFutureAmuletConfigScheduleResult:
        pass

    @choice(controller=dso, consuming=True)
    def AmuletRules_RemoveFutureAmuletConfigSchedule(self, schedule_time: Annotated[datetime, DamlName("scheduleTime")]) -> AmuletRules_RemoveFutureAmuletConfigScheduleResult:
        pass

    @choice(controller=dso, consuming=True)
    def AmuletRules_UpdateFutureAmuletConfigSchedule(self, schedule_item: Annotated[tuple[datetime, AmuletConfig[USD]], DamlName("scheduleItem")]) -> AmuletRules_UpdateFutureAmuletConfigScheduleResult:
        pass


@template
class ExternalPartySetupProposal:
    validator: Party
    user: Party
    dso: Party
    created_at: Annotated[datetime, DamlName("createdAt")]
    preapproval_expires_at: Annotated[datetime, DamlName("preapprovalExpiresAt")]

    signatory: list[Party] = [validator, dso]
    observer: list[Party] = [user]

    @choice(controller=user, consuming=True)
    def ExternalPartySetupProposal_Accept(self) -> ExternalPartySetupProposal_AcceptResult:
        pass

    @choice(controller=user, consuming=True)
    def ExternalPartySetupProposal_Reject(self, reason: str) -> ExternalPartySetupProposal_RejectResult:
        pass

    @choice(controller=validator, consuming=True)
    def ExternalPartySetupProposal_Withdraw(self, reason: str) -> ExternalPartySetupProposal_WithdrawResult:
        pass


@template
class TransferPreapproval:
    dso: Party
    receiver: Party
    provider: Party
    valid_from: Annotated[datetime, DamlName("validFrom")]
    last_renewed_at: Annotated[datetime, DamlName("lastRenewedAt")]
    expires_at: Annotated[datetime, DamlName("expiresAt")]

    signatory: list[Party] = [dso, receiver, provider]

    @choice(controller=sender, consuming="nonconsuming")
    def TransferPreapproval_SendV2(self, context: ExternalPartyTransferContext, inputs: list[TransferInput], amount: Decimal, sender: Party, description: Optional[str], meta: Optional[Metadata]) -> TransferPreapproval_SendV2Result:
        pass

    @choice(controller=provider, consuming=True)
    def TransferPreapproval_Renew(self, context: PaymentTransferContext, inputs: list[TransferInput], new_expires_at: Annotated[datetime, DamlName("newExpiresAt")]) -> TransferPreapproval_RenewResult:
        pass

    @choice(controller=sender, consuming="nonconsuming")
    def TransferPreapproval_Send(self, context: PaymentTransferContext, inputs: list[TransferInput], amount: Decimal, sender: Party, description: Optional[str]) -> TransferPreapproval_SendResult:
        pass

    @choice(controller=dso, consuming=True)
    def TransferPreapproval_Expire(self) -> TransferPreapproval_ExpireResult:
        pass

    @choice(controller=p, consuming=True)
    def TransferPreapproval_Cancel(self, p: Party) -> TransferPreapproval_CancelResult:
        pass

    @choice(controller=p, consuming="nonconsuming")
    def TransferPreapproval_Fetch(self, p: Party) -> TransferPreapproval:
        pass


@DamlCaseAccessor("InputAppRewardCoupon")
def input_app_reward_coupon(value: TransferInput) -> Optional[ContractId[AppRewardCoupon]]:
    pass


@DamlCaseAccessor("InputValidatorRewardCoupon")
def input_validator_reward_coupon(value: TransferInput) -> Optional[ContractId[ValidatorRewardCoupon]]:
    pass


@DamlCaseAccessor("InputSvRewardCoupon")
def input_sv_reward_coupon(value: TransferInput) -> Optional[ContractId[SvRewardCoupon]]:
    pass


@DamlCaseAccessor("InputAmulet")
def input_amulet(value: TransferInput) -> Optional[ContractId[Amulet]]:
    pass


@DamlCaseAccessor("ExtTransferInput", arity=2)
def ext_transfer_input(value: TransferInput) -> Optional[tuple[None, Optional[ContractId[ValidatorFaucetCoupon]]]]:
    pass


@DamlCaseAccessor("InputValidatorLivenessActivityRecord")
def input_validator_liveness_activity_record(value: TransferInput) -> Optional[ContractId[ValidatorLivenessActivityRecord]]:
    pass


@DamlCaseAccessor("InputUnclaimedActivityRecord")
def input_unclaimed_activity_record(value: TransferInput) -> Optional[ContractId[UnclaimedActivityRecord]]:
    pass


@DamlCaseAccessor("InputDevelopmentFundCoupon")
def input_development_fund_coupon(value: TransferInput) -> Optional[ContractId[DevelopmentFundCoupon]]:
    pass


@DamlCaseAccessor("InputRewardCouponV2")
def input_reward_coupon_v2(value: TransferInput) -> Optional[ContractId[RewardCouponV2]]:
    pass


@DamlCaseAccessor("TransferResultAmulet")
def transfer_result_amulet(value: CreatedAmulet) -> Optional[ContractId[Amulet]]:
    pass


@DamlCaseAccessor("TransferResultLockedAmulet")
def transfer_result_locked_amulet(value: CreatedAmulet) -> Optional[ContractId[LockedAmulet]]:
    pass


@DamlCaseAccessor("ExtCreatedAmulet")
def ext_created_amulet(value: CreatedAmulet) -> Optional[None]:
    pass


@DamlCaseAccessor("ITR_InsufficientFunds")
def itr_insufficient_funds(value: InvalidTransferReason) -> Optional[Decimal]:
    pass


@DamlCaseAccessor("ITR_UnknownSynchronizer")
def itr_unknown_synchronizer(value: InvalidTransferReason) -> Optional[str]:
    pass


@DamlCaseAccessor("ITR_InsufficientTopupAmount", arity=2)
def itr_insufficient_topup_amount(value: InvalidTransferReason) -> Optional[tuple[int, int]]:
    pass


@DamlCaseAccessor("ITR_Other")
def itr_other(value: InvalidTransferReason) -> Optional[str]:
    pass


@DamlCaseAccessor("ExtInvalidTransferReason")
def ext_invalid_transfer_reason(value: InvalidTransferReason) -> Optional[None]:
    pass


@DamlName("validateOpenMiningRoundTriple", is_ledger_effect=True)
def validate_open_mining_round_triple(party: Party, round_triple: OpenMiningRoundTriple) -> ValidatedOpenMiningRounds:
    pass


@DamlName("miningRoundTripleCids")
def mining_round_triple_cids(open_mining_round_triple: OpenMiningRoundTriple) -> list[ContractId[OpenMiningRound]]:
    pass


@DamlName("transferControllers")
def transfer_controllers(t: Transfer) -> set[Party]:
    pass


@DamlName("mkUnknownSynchronizerFailure")
def mk_unknown_synchronizer_failure(synchronizer_id: str) -> FailureStatus:
    pass


@DamlName("mkInsufficientTopupAmountFailure")
def mk_insufficient_topup_amount_failure(int_value: int, int_value_1: int) -> FailureStatus:
    pass


@DamlName("mkMaximumInputsExceededFailure")
def mk_maximum_inputs_exceeded_failure() -> FailureStatus:
    pass


@DamlName("mkMaximumOutputsExceededFailure")
def mk_maximum_outputs_exceeded_failure() -> FailureStatus:
    pass


@DamlName("mkInsufficientFundsFailure")
def mk_insufficient_funds_failure(missing_amount: Decimal) -> FailureStatus:
    pass


@DamlName("spliceErrorId")
def splice_error_id(t: str) -> str:
    pass


@DamlName("checkTransferConstraints")
def check_transfer_constraints(transfer: Transfer, summary: TransferSummary, transfer_config_amulet: TransferConfigV2[Unit]) -> Either[FailureStatus, None]:
    pass


@DamlName("executeTransfer", is_ledger_effect=True)
def execute_transfer(event_log_cid: ContractId[EventLog], config: RewardsIssuanceConfig, context: TransferContext, party: Party, development_fund_manager_blacklist: list[Party], t: Transfer) -> TransferResult:
    pass


@DamlName("executeExternalPartyTransfer", is_ledger_effect=True)
def execute_external_party_transfer(party: Party, context: ExternalPartyTransferContext, t: Transfer) -> TransferResult:
    pass


@DamlName("summarizeAndValidateContext", is_ledger_effect=True)
def summarize_and_validate_context(contract_id: ContractId[EventLog], transfer_context: TransferContext, party: Party, list_value: list[Party], transfer: Transfer) -> TransferContextSummaryV2:
    pass


@DamlName("summarizeAndValidateExternalPartyContext", is_ledger_effect=True)
def summarize_and_validate_external_party_context(context: ExternalPartyTransferContext, party: Party, tf: Transfer) -> TransferContextSummaryV2:
    pass


@DamlName("getValidatorRight", is_ledger_effect=True)
def get_validator_right(csum: TransferContextSummaryV2, user: Party) -> ContractId[ValidatorRight]:
    pass


@DamlName("getIssuingMiningRound", is_ledger_effect=True)
def get_issuing_mining_round(csum: TransferContextSummaryV2, round: Round) -> IssuingMiningRound:
    pass


@DamlName("summarizeAndConsumeInputs", is_ledger_effect=True)
def summarize_and_consume_inputs(csum: TransferContextSummaryV2, party: Party, sender: Party, inps: list[TransferInput]) -> TransferInputsSummary:
    pass


@DamlName("dedupOutputLockHolders")
def dedup_output_lock_holders(out: TransferOutput) -> TransferOutput:
    pass


@DamlName("preprocessOutputs", is_ledger_effect=True)
def preprocess_outputs(transfer_config_amulet: TransferConfigV2[Amulet], outs: list[TransferOutput]) -> list[PreprocessedTransferOutput]:
    pass


@DamlName("summarizeTransfer", is_ledger_effect=True)
def summarize_transfer(sender: Party, open_round_number: Round, amulet_price: Decimal, transfer_config_amulet: TransferConfigV2[Amulet], inp: TransferInputsSummary, preprocessed_outputs: list[PreprocessedTransferOutput]) -> TransferSummary:
    pass


@DamlName("issueRewards", is_ledger_effect=True)
def issue_rewards(config: RewardsIssuanceConfig, csum: TransferContextSummaryV2, provider: Party, beneficiaries: Optional[list[AppRewardBeneficiary]]) -> None:
    pass


@DamlName("createTransferOutputs", is_ledger_effect=True)
def create_transfer_outputs(round: Round, transfer_config_v2: TransferConfigV2[Amulet], party: Party, party_3: Party, transfer_summary: TransferSummary, list_value: list[PreprocessedTransferOutput]) -> tuple[list[CreatedAmulet], Optional[ContractId[Amulet]], list[EventLog_HoldingsChange]]:
    pass


@DamlName("scaleFees")
def scale_fees(s: Decimal, c: TransferConfig[USD]) -> TransferConfig[Amulet]:
    pass


@DamlName("scaleFees2")
def scale_fees2(s: Decimal, c: TransferConfigV2[USD]) -> TransferConfigV2[Amulet]:
    pass


@DamlName("transferConfigAmuletFromOpenRound")
def transfer_config_amulet_from_open_round(open_round: OpenMiningRound) -> TransferConfig[Amulet]:
    pass


@DamlName("transferConfigAmuletFromExternalPartyConfigState")
def transfer_config_amulet_from_external_party_config_state(external_party_config_state: ExternalPartyConfigState) -> TransferConfigV2[Amulet]:
    pass


@DamlName("validateBuyMemberTrafficInputs")
def validate_buy_member_traffic_inputs(config_usd: AmuletConfig[USD], synchronizer_id: str, traffic_amount: int) -> Either[FailureStatus, None]:
    pass


@DamlName("computeSynchronizerFees", is_ledger_effect=True)
def compute_synchronizer_fees(party: Party, validator: Party, traffic_amount: int, amulet_rules: AmuletRules, context: TransferContext) -> tuple[Decimal, Decimal]:
    pass


@DamlName("legacyAmuletCreateSummary", is_ledger_effect=True)
def legacy_amulet_create_summary(party: Party, p: Party, mining_round_cid: ContractId[OpenMiningRound], amulet: ContractId[Amulet]) -> AmuletCreateSummary[ContractId[Amulet]]:
    pass


@DamlName("checkExpectedDso", is_ledger_effect=True)
def check_expected_dso(actual_dso: Party, opt_expected_dso: Optional[Party]) -> None:
    pass


@DamlName("exerciseAppTransfer", is_ledger_effect=True)
def exercise_app_transfer(expected_dso: Party, app_transfer_context: AppTransferContext, transfer: Transfer) -> TransferResult:
    pass


@DamlName("exercisePaymentTransfer", is_ledger_effect=True)
def exercise_payment_transfer(expected_dso: Party, payment_transfer_context: PaymentTransferContext, transfer: Transfer) -> TransferResult:
    pass


@DamlName("amuletTransferContext")
def amulet_transfer_context(open_mining_round: ContractId[OpenMiningRound], featured_app_right: Optional[ContractId[FeaturedAppRight]]) -> TransferContext:
    pass


@DamlName("createdAmuletToHolding")
def created_amulet_to_holding(created_amulet: CreatedAmulet) -> ContractId[Holding]:
    pass


@DamlName("mkInputValidatorFaucetCoupon")
def mk_input_validator_faucet_coupon(cid: ContractId[ValidatorFaucetCoupon]) -> TransferInput:
    pass


@DamlName("computeTransferPreapprovalFee", is_ledger_effect=True)
def compute_transfer_preapproval_fee(duration: timedelta, amulet_config: AmuletConfig[USD], context: TransferContext, party: Party) -> tuple[Decimal, Decimal]:
    pass


@DamlName("splitAndBurn", is_ledger_effect=True)
def split_and_burn(event_log_cid: ContractId[EventLog], sender: Party, amount: Decimal, inputs: list[TransferInput], context: TransferContext, party: Party, development_fund_manager_blacklist: list[Party], usage: str) -> tuple[TransferResult, Metadata]:
    pass


@DamlName("totalBurnFromSummary")
def total_burn_from_summary(transfer_summary: TransferSummary) -> Decimal:
    pass


@DamlName("payForTransferPreapproval", is_ledger_effect=True)
def pay_for_transfer_preapproval(reason: str, party: Party, provider: Party, context: PaymentTransferContext, inputs: list[TransferInput], expires_at: datetime, new_expires_at: datetime) -> tuple[Decimal, TransferResult, Metadata]:
    pass


@DamlName("externalPartyTransferFromChoiceContext", is_ledger_effect=True)
def external_party_transfer_from_choice_context(party: Party, context: ChoiceContext) -> ExternalPartyTransferContext:
    pass


@DamlName("unfeaturedPaymentContextFromChoiceContext", is_ledger_effect=True)
def unfeatured_payment_context_from_choice_context(party: Party, choice_context: ChoiceContext) -> ExternalPartyTransferContext:
    pass


@DamlName("getExternalPartyConfigStateFromChoiceContext", is_ledger_effect=True)
def get_external_party_config_state_from_choice_context(party: Party, context: ChoiceContext) -> tuple[ContractId[ExternalPartyConfigState], ExternalPartyConfigState]:
    pass


@DamlName("bootstrapExternalPartyConfigState", is_ledger_effect=True)
def bootstrap_external_party_config_state(amulet_rules: AmuletRules, open_mining_round_triple: OpenMiningRoundTriple) -> None:
    pass


@DamlName("getAndValidateCreatedAt", is_ledger_effect=True)
def get_and_validate_created_at(optional: Optional[datetime]) -> datetime:
    pass


@DamlName("mergeHoldingsChangeEventsByAccount")
def merge_holdings_change_events_by_account(events: list[EventLog_HoldingsChange]) -> list[EventLog_HoldingsChange]:
    pass
