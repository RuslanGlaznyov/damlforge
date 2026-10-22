from datetime import datetime, timedelta
from typing import Annotated, Generic, TypeVar

from forge.models import choice, ContractId, Decimal, GenMap, Optional, Party, template, TextMap, variant, variant_record
from forge.builtins import DamlCaseAccessor, DamlName, no_derive
from Splice.Amulet import Amulet, AmuletExpireSummary, AmuletExpireV2Summary, Amulet_Expire, Amulet_ExpireV2, DevelopmentFundCoupon, DevelopmentFundCoupon_DsoExpireResult, FeaturedAppRight, FeaturedAppRight_Update, FeaturedAppRight_UpdateResult, LockedAmulet, LockedAmulet_ExpireAmulet, LockedAmulet_ExpireAmuletV2, SvRewardCoupon, UnclaimedActivityRecord, UnclaimedReward
from Splice.Amulet.RewardAccountingV2 import ProcessRewardsV2, ProcessRewardsV2_ProcessBatch, ProcessRewardsV2_ProcessBatchResult
from Splice.AmuletRules import AmuletRules, AmuletRules_AddFutureAmuletConfigSchedule, AmuletRules_Amulet_ExpireTransferInstructions, AmuletRules_Amulet_ExpireTransferInstructionsResult, AmuletRules_ArchiveDryRunRewardAccountingV2, AmuletRules_ArchiveDryRunRewardAccountingV2Result, AmuletRules_ClaimExpiredRewards, AmuletRules_ClaimExpiredRewardsV2, AmuletRules_ClaimExpiredRewardsV2Result, AmuletRules_ConvertFeaturedAppActivityMarkers, AmuletRules_ConvertFeaturedAppActivityMarkersResult, AmuletRules_MergeUnclaimedDevelopmentFundCoupons, AmuletRules_MergeUnclaimedDevelopmentFundCouponsResult, AmuletRules_MiningRound_Archive, AmuletRules_MiningRound_StartIssuing, AmuletRules_RemoveFutureAmuletConfigSchedule, AmuletRules_SetConfig, AmuletRules_StartProcessingRewardsV2, AmuletRules_StartProcessingRewardsV2Result, AmuletRules_UnhideRewardCouponsV2, AmuletRules_UnhideRewardCouponsV2Result, AmuletRules_UpdateFutureAmuletConfigSchedule, OpenMiningRoundTriple, TransferPreapproval
from Splice.Ans import AnsEntry, AnsEntryContext, AnsEntryContext_CollectEntryRenewalPayment, AnsEntryContext_CollectInitialEntryPayment, AnsEntryContext_RejectEntryInitialPayment, AnsEntry_Expire
from Splice.DSO.AmuletPrice import AmuletPriceVote
from Splice.DSO.DecentralizedSynchronizer import DsoDecentralizedSynchronizerConfig, SynchronizerNodeConfig, SynchronizerNodeConfigLimits
from Splice.DSO.SvState import SvNodeState, SvRewardState, SvStatus, SvStatusReport
from Splice.DecentralizedSynchronizer import MemberTraffic
from Splice.ExternalPartyAmuletRules import ExternalPartyAmuletRules, ExternalPartyAmuletRules_ExpireAmuletAllocations, ExternalPartyAmuletRules_ExpireAmuletAllocationsResult, ExternalPartyAmuletRules_ExpireAmuletAllocationsV2, ExternalPartyAmuletRules_ExpireAmuletAllocationsV2Result, TransferCommandCounter
from Splice.ExternalPartyConfigState import ExternalPartyConfigState
from Splice.Round import ClosedMiningRound, IssuingMiningRound, OpenMiningRound, SummarizingMiningRound
from Splice.Schedule import Schedule
from Splice.SvOnboarding import SvOnboardingConfirmed, SvOnboardingRequest
from Splice.Types import Round
from Splice.ValidatorLicense import ValidatorLicense
from Splice.Wallet.Subscriptions import SubscriptionIdleState, SubscriptionIdleState_ExpireSubscription, TerminatedSubscription

A = TypeVar("A")
T = TypeVar("T")


@variant
class VoteRequestOutcome:
    @variant_record
    def VRO_AcceptedButActionFailed(description: str): pass
    @variant_record
    def VRO_Accepted(effective_at: Annotated[datetime, DamlName("effectiveAt")]): pass
    def VRO_Rejected(): pass
    def VRO_Expired(): pass
    @variant_record
    def ExtVoteRequestOutcome(dummy_unit_field: Annotated[None, DamlName("dummyUnitField")]): pass


@no_derive
@variant
class DsoRules_BootstrapExternalPartyConfigStateResult:
    def DsoRules_BootstrapExternalPartyConfigStateResult(): pass


@variant
class ElectionRequestReason:
    def ERR_DsoDelegateUnavailable(): pass
    def ERR_OtherReason(value: str): pass
    @variant_record
    def ExtElectionRequestReason(dummy_unit_field: Annotated[None, DamlName("dummyUnitField")]): pass


@no_derive
@variant
class DsoRules_ExpireUnallocatedUnclaimedActivityRecordResult:
    def DsoRules_ExpireUnallocatedUnclaimedActivityRecordResult(): pass


@variant
class DsoRules_ExpireTransferPreapprovalResult:
    def DsoRules_ExpireTransferPreapprovalResult(): pass


@no_derive
@variant
class DsoRules_TerminateSubscriptionResult:
    def DsoRules_TerminateSubscriptionResult(): pass


@no_derive
@variant
class DsoRules_ExpireSubscriptionResult:
    def DsoRules_ExpireSubscriptionResult(): pass


@no_derive
@variant
class DsoRules_ExpireAnsEntryResult:
    def DsoRules_ExpireAnsEntryResult(): pass


@no_derive
@variant
class DsoRules_ArchiveSvOnboardingRequestResult:
    def DsoRules_ArchiveSvOnboardingRequestResult(): pass


@no_derive
@variant
class DsoRules_ExpireSvOnboardingRequestResult:
    def DsoRules_ExpireSvOnboardingRequestResult(): pass


@no_derive
@variant
class DsoRules_RevokeFeaturedAppRightResult:
    def DsoRules_RevokeFeaturedAppRightResult(): pass


@no_derive
@variant
class DsoRules_GarbageCollectAmuletPriceVotesResult:
    def DsoRules_GarbageCollectAmuletPriceVotesResult(): pass


@no_derive
@variant
class DsoRules_ExpireStaleConfirmationResult:
    def DsoRules_ExpireStaleConfirmationResult(): pass


@no_derive
@variant
class DsoRules_ExecuteConfirmedActionResult:
    def DsoRules_ExecuteConfirmedActionResult(): pass


@no_derive
@variant
class DsoRules_ArchiveOutdatedElectionRequestResult:
    def DsoRules_ArchiveOutdatedElectionRequestResult(): pass


@no_derive
@variant
class Confirmation_ExpireResult:
    def Confirmation_ExpireResult(): pass


@variant
class AnsEntryContext_ActionRequiringConfirmation:
    def ANSRARC_CollectInitialEntryPayment(value: AnsEntryContext_CollectInitialEntryPayment): pass
    def ANSRARC_RejectEntryInitialPayment(value: AnsEntryContext_RejectEntryInitialPayment): pass


@variant
class DsoRules_ActionRequiringConfirmation:
    def SRARC_AddSv(value: DsoRules_AddSv): pass
    def SRARC_OffboardSv(value: DsoRules_OffboardSv): pass
    def SRARC_ConfirmSvOnboarding(value: DsoRules_ConfirmSvOnboarding): pass
    def SRARC_GrantFeaturedAppRight(value: DsoRules_GrantFeaturedAppRight): pass
    def SRARC_RevokeFeaturedAppRight(value: DsoRules_RevokeFeaturedAppRight): pass
    def SRARC_SetConfig(value: DsoRules_SetConfig): pass
    def SRARC_UpdateSvRewardWeight(value: DsoRules_UpdateSvRewardWeight): pass
    def SRARC_CreateExternalPartyAmuletRules(value: DsoRules_CreateExternalPartyAmuletRules): pass
    def SRARC_CreateTransferCommandCounter(value: DsoRules_CreateTransferCommandCounter): pass
    def SRARC_CreateUnallocatedUnclaimedActivityRecord(value: DsoRules_CreateUnallocatedUnclaimedActivityRecord): pass
    def SRARC_CreateBootstrapExternalPartyConfigStateInstruction(value: DsoRules_CreateBootstrapExternalPartyConfigStateInstruction): pass
    def SRARC_UpdateFeaturedAppRight(value: DsoRules_UpdateFeaturedAppRight): pass


@variant
class AmuletRules_ActionRequiringConfirmation:
    def CRARC_MiningRound_StartIssuing(value: AmuletRules_MiningRound_StartIssuing): pass
    def CRARC_MiningRound_Archive(value: AmuletRules_MiningRound_Archive): pass
    def CRARC_AddFutureAmuletConfigSchedule(value: AmuletRules_AddFutureAmuletConfigSchedule): pass
    def CRARC_RemoveFutureAmuletConfigSchedule(value: AmuletRules_RemoveFutureAmuletConfigSchedule): pass
    def CRARC_UpdateFutureAmuletConfigSchedule(value: AmuletRules_UpdateFutureAmuletConfigSchedule): pass
    def CRARC_SetConfig(value: AmuletRules_SetConfig): pass
    def CRARC_StartProcessingRewardsV2(value: AmuletRules_StartProcessingRewardsV2): pass


@variant
class ActionRequiringConfirmation:
    @variant_record
    def ARC_DsoRules(dso_action: Annotated[DsoRules_ActionRequiringConfirmation, DamlName("dsoAction")]): pass
    @variant_record
    def ARC_AmuletRules(amulet_rules_action: Annotated[AmuletRules_ActionRequiringConfirmation, DamlName("amuletRulesAction")]): pass
    @variant_record
    def ARC_AnsEntryContext(ans_entry_context_cid: Annotated[ContractId[AnsEntryContext], DamlName("ansEntryContextCid")], ans_entry_context_action: Annotated[AnsEntryContext_ActionRequiringConfirmation, DamlName("ansEntryContextAction")]): pass
    @variant_record
    def ExtActionRequiringConformation(dummy_unit_field: Annotated[None, DamlName("dummyUnitField")]): pass


struct SvInfo:
    name: str
    joined_as_of_round: Annotated[Round, DamlName("joinedAsOfRound")]
    sv_reward_weight: Annotated[int, DamlName("svRewardWeight")]
    participant_id: Annotated[str, DamlName("participantId")]


struct OffboardedSvInfo:
    name: str
    participant_id: Annotated[str, DamlName("participantId")]


struct DsoSummary:
    dso_delegate: Annotated[Party, DamlName("dsoDelegate")]
    num_svs: Annotated[int, DamlName("numSvs")]
    required_num_votes: Annotated[int, DamlName("requiredNumVotes")]


@no_derive
struct DsoRules_AddSvResult:
    new_dso_rules: Annotated[ContractId[DsoRules], DamlName("newDsoRules")]


@no_derive
struct DsoRules_OffboardSvResult:
    new_dso_rules: Annotated[ContractId[DsoRules], DamlName("newDsoRules")]


@no_derive
struct DsoRules_SubmitStatusReportResult:
    new_report: Annotated[ContractId[SvStatusReport], DamlName("newReport")]


@no_derive
struct DsoRules_AddConfirmedSvResult:
    new_dso_rules: Annotated[ContractId[DsoRules], DamlName("newDsoRules")]


@no_derive
struct DsoRules_SetSynchronizerNodeConfigResult:
    sv_node_state: Annotated[ContractId[SvNodeState], DamlName("svNodeState")]


@no_derive
struct DsoRules_RequestElectionResult:
    election_request_cid: Annotated[ContractId[ElectionRequest], DamlName("electionRequestCid")]


@no_derive
struct DsoRules_ElectDsoDelegateResult:
    new_dso_rules: Annotated[ContractId[DsoRules], DamlName("newDsoRules")]


@no_derive
struct DsoRules_ConfirmActionResult:
    confirmation: ContractId[Confirmation]


@no_derive
struct DsoRules_RequestVoteResult:
    vote_request: Annotated[ContractId[VoteRequest], DamlName("voteRequest")]


@no_derive
struct DsoRules_CastVoteResult:
    vote_request: Annotated[ContractId[VoteRequest], DamlName("voteRequest")]


@no_derive
struct DsoRules_UpdateAmuletPriceVoteResult:
    amulet_price_vote: Annotated[ContractId[AmuletPriceVote], DamlName("amuletPriceVote")]


@no_derive
struct DsoRules_SetConfigResult:
    new_dso_rules: Annotated[ContractId[DsoRules], DamlName("newDsoRules")]


@no_derive
struct DsoRules_UpdateSvRewardWeightResult:
    new_dso_rules: Annotated[ContractId[DsoRules], DamlName("newDsoRules")]


@no_derive
struct DsoRules_GrantFeaturedAppRightResult:
    featured_app_right: Annotated[ContractId[FeaturedAppRight], DamlName("featuredAppRight")]


@no_derive
struct DsoRules_UpdateFeaturedAppRightResult:
    result: FeaturedAppRight_UpdateResult


@no_derive
struct DsoRules_OnboardValidatorResult:
    validator_license: Annotated[ContractId[ValidatorLicense], DamlName("validatorLicense")]


@no_derive
struct DsoRules_MergeValidatorLicenseResult:
    validator_license: Annotated[ContractId[ValidatorLicense], DamlName("validatorLicense")]


@no_derive
struct DsoRules_StartSvOnboardingResult:
    onboarding_request: Annotated[ContractId[SvOnboardingRequest], DamlName("onboardingRequest")]


@no_derive
struct DsoRules_ConfirmSvOnboardingResult:
    onboarding_confirmed: Annotated[ContractId[SvOnboardingConfirmed], DamlName("onboardingConfirmed")]


@no_derive
struct DsoRules_ExpireSvOnboardingConfirmedResult:
    new_dso_rules: Annotated[ContractId[DsoRules], DamlName("newDsoRules")]


struct DsoRules_Amulet_ExpireTransferInstructionsResult:
    result: AmuletRules_Amulet_ExpireTransferInstructionsResult


@no_derive
struct DsoRules_Amulet_ExpireResult:
    expire_sum: Annotated[AmuletExpireSummary, DamlName("expireSum")]


@no_derive
struct DsoRules_Amulet_ExpireV2Result:
    expire_sum: Annotated[AmuletExpireV2Summary, DamlName("expireSum")]


@no_derive
struct DsoRules_LockedAmulet_ExpireAmuletResult:
    expire_sum: Annotated[AmuletExpireSummary, DamlName("expireSum")]


@no_derive
struct DsoRules_LockedAmulet_ExpireAmuletV2Result:
    expire_sum: Annotated[AmuletExpireV2Summary, DamlName("expireSum")]


@no_derive
struct DsoRules_AdvanceOpenMiningRoundsResult:
    summarizing_round: Annotated[ContractId[SummarizingMiningRound], DamlName("summarizingRound")]
    open_round: Annotated[ContractId[OpenMiningRound], DamlName("openRound")]


struct DsoRules_UpdateExternalPartyConfigStatesResult:
    new_external_party_config_state_cid: Annotated[ContractId[ExternalPartyConfigState], DamlName("newExternalPartyConfigStateCid")]


@no_derive
struct DsoRules_CollectEntryRenewalPaymentResult:
    ans_entry: Annotated[ContractId[AnsEntry], DamlName("ansEntry")]
    subscription_state: Annotated[ContractId[SubscriptionIdleState], DamlName("subscriptionState")]


@no_derive
struct DsoRules_ReceiveSvRewardCouponResult:
    sv_reward_state: Annotated[ContractId[SvRewardState], DamlName("svRewardState")]
    sv_reward_coupons: Annotated[list[ContractId[SvRewardCoupon]], DamlName("svRewardCoupons")]


@no_derive
struct DsoRules_ClaimExpiredRewardsResult:
    unclaimed_reward: Annotated[Optional[ContractId[UnclaimedReward]], DamlName("unclaimedReward")]


@no_derive
struct DsoRules_ClaimExpiredRewardsV2Result:
    result: AmuletRules_ClaimExpiredRewardsV2Result


@no_derive
struct DsoRules_StartProcessingRewardsV2Result:
    result: AmuletRules_StartProcessingRewardsV2Result


@no_derive
struct DsoRules_ProcessRewardsV2_ProcessBatchResult:
    result: ProcessRewardsV2_ProcessBatchResult


@no_derive
struct DsoRules_UnhideRewardCouponsV2Result:
    result: AmuletRules_UnhideRewardCouponsV2Result


@no_derive
struct DsoRules_ArchiveDryRunRewardAccountingV2Result:
    result: AmuletRules_ArchiveDryRunRewardAccountingV2Result


@no_derive
struct DsoRules_MergeUnclaimedRewardsResult:
    unclaimed_reward: Annotated[ContractId[UnclaimedReward], DamlName("unclaimedReward")]


@no_derive
struct DsoRules_MergeUnclaimedDevelopmentFundCouponsResult:
    result: AmuletRules_MergeUnclaimedDevelopmentFundCouponsResult


@no_derive
struct DsoRules_ExpireDevelopmentFundCouponResult:
    result: DevelopmentFundCoupon_DsoExpireResult


@no_derive
struct DsoRules_MiningRound_CloseResult:
    closed_round: Annotated[ContractId[ClosedMiningRound], DamlName("closedRound")]


@no_derive
struct DsoRules_MergeMemberTrafficContractsResult:
    member_traffic: Annotated[ContractId[MemberTraffic], DamlName("memberTraffic")]


@no_derive
struct DsoRules_MergeSvRewardStateResult:
    sv_reward_state: Annotated[ContractId[SvRewardState], DamlName("svRewardState")]


@no_derive
struct DsoRules_PruneAmuletConfigScheduleResult:
    amulet_rules_cid: Annotated[ContractId[AmuletRules], DamlName("amuletRulesCid")]


struct DsoRules_CreateExternalPartyAmuletRulesResult:
    external_party_amulet_rules_cid: Annotated[ContractId[ExternalPartyAmuletRules], DamlName("externalPartyAmuletRulesCid")]


struct DsoRules_CreateTransferCommandCounterResult:
    transfer_command_counter_cid: Annotated[ContractId[TransferCommandCounter], DamlName("transferCommandCounterCid")]


@no_derive
struct DsoRules_AmuletRules_ConvertFeaturedAppActivityMarkersResult:
    result: AmuletRules_ConvertFeaturedAppActivityMarkersResult


@no_derive
struct DsoRules_CreateUnallocatedUnclaimedActivityRecordResult:
    unallocated_unclaimed_activity_record_cid: Annotated[ContractId[UnallocatedUnclaimedActivityRecord], DamlName("unallocatedUnclaimedActivityRecordCid")]


@no_derive
struct DsoRules_AllocateUnallocatedUnclaimedActivityRecordResult:
    unclaimed_activity_record_cid: Annotated[ContractId[UnclaimedActivityRecord], DamlName("unclaimedActivityRecordCid")]
    opt_unclaimed_reward_cid: Annotated[Optional[ContractId[UnclaimedReward]], DamlName("optUnclaimedRewardCid")]


@no_derive
struct DsoRules_ExpireUnclaimedActivityRecordResult:
    unclaimed_reward_cid: Annotated[ContractId[UnclaimedReward], DamlName("unclaimedRewardCid")]


struct DsoRules_CreateBootstrapExternalPartyConfigStateInstructionResult:
    instruction_cid: Annotated[ContractId[BootstrapExternalPartyConfigStateInstruction], DamlName("instructionCid")]


struct DsoRules_ExpireAmuletAllocationsResult:
    result: ExternalPartyAmuletRules_ExpireAmuletAllocationsResult


struct DsoRules_ExpireAmuletAllocationsV2Result:
    result: ExternalPartyAmuletRules_ExpireAmuletAllocationsV2Result


struct DsoRules_CloseVoteRequestResult:
    request: VoteRequest
    completed_at: Annotated[datetime, DamlName("completedAt")]
    offboarded_voters: Annotated[list[str], DamlName("offboardedVoters")]
    abstaining_svs: Annotated[list[str], DamlName("abstainingSvs")]
    outcome: VoteRequestOutcome


struct Vote:
    sv: Party
    accept: bool
    reason: Reason
    opt_cast_at: Annotated[Optional[datetime], DamlName("optCastAt")]


struct Reason:
    url: str
    body: str


struct DsoRulesConfig:
    num_unclaimed_rewards_threshold: Annotated[int, DamlName("numUnclaimedRewardsThreshold")]
    num_member_traffic_contracts_threshold: Annotated[int, DamlName("numMemberTrafficContractsThreshold")]
    action_confirmation_timeout: Annotated[timedelta, DamlName("actionConfirmationTimeout")]
    sv_onboarding_request_timeout: Annotated[timedelta, DamlName("svOnboardingRequestTimeout")]
    sv_onboarding_confirmed_timeout: Annotated[timedelta, DamlName("svOnboardingConfirmedTimeout")]
    vote_request_timeout: Annotated[timedelta, DamlName("voteRequestTimeout")]
    dso_delegate_inactive_timeout: Annotated[timedelta, DamlName("dsoDelegateInactiveTimeout")]
    synchronizer_node_config_limits: Annotated[SynchronizerNodeConfigLimits, DamlName("synchronizerNodeConfigLimits")]
    max_text_length: Annotated[int, DamlName("maxTextLength")]
    decentralized_synchronizer: Annotated[DsoDecentralizedSynchronizerConfig, DamlName("decentralizedSynchronizer")]
    next_scheduled_synchronizer_upgrade: Annotated[Optional[SynchronizerUpgradeSchedule], DamlName("nextScheduledSynchronizerUpgrade")]
    vote_cooldown_time: Annotated[Optional[timedelta], DamlName("voteCooldownTime")]
    next_scheduled_logical_synchronizer_upgrade: Annotated[Optional[LogicalSynchronizerUpgradeSchedule], DamlName("nextScheduledLogicalSynchronizerUpgrade")]
    sv_operations_switch_over_times: Annotated[Optional[TextMap[datetime]], DamlName("svOperationsSwitchOverTimes")]


struct SynchronizerUpgradeSchedule:
    time: datetime
    migration_id: Annotated[int, DamlName("migrationId")]


struct LogicalSynchronizerUpgradeSchedule:
    topology_freeze_time: Annotated[datetime, DamlName("topologyFreezeTime")]
    upgrade_time: Annotated[datetime, DamlName("upgradeTime")]
    new_physical_synchronizer_serial: Annotated[int, DamlName("newPhysicalSynchronizerSerial")]
    new_physical_synchronizer_protocol_version: Annotated[str, DamlName("newPhysicalSynchronizerProtocolVersion")]


struct TrafficState:
    consumed_traffic: Annotated[int, DamlName("consumedTraffic")]


struct VotingState(Generic[A]):
    rankings: GenMap[A, list[list[A]]]
    loosers: set[A]


@template
class ElectionRequest:
    dso: Party
    requester: Party
    epoch: int
    reason: ElectionRequestReason
    ranking: list[Party]

    signatory: list[Party] = [dso]


@template
class Confirmation:
    dso: Party
    confirmer: Party
    action: ActionRequiringConfirmation
    expires_at: Annotated[datetime, DamlName("expiresAt")]

    signatory: list[Party] = [dso]

    @choice(controller=dso, consuming=True)
    def Confirmation_Expire(self) -> Confirmation_ExpireResult:
        pass


@template
class VoteRequest:
    dso: Party
    requester: str
    action: ActionRequiringConfirmation
    reason: Reason
    vote_before: Annotated[datetime, DamlName("voteBefore")]
    votes: GenMap[str, Vote]
    tracking_cid: Annotated[Optional[ContractId[VoteRequest]], DamlName("trackingCid")]
    target_effective_at: Annotated[Optional[datetime], DamlName("targetEffectiveAt")]

    signatory: list[Party] = [dso]


@template
class DsoRules:
    dso: Party
    epoch: int
    svs: GenMap[Party, SvInfo]
    offboarded_svs: Annotated[GenMap[Party, OffboardedSvInfo], DamlName("offboardedSvs")]
    dso_delegate: Annotated[Party, DamlName("dsoDelegate")]
    config: DsoRulesConfig
    initial_traffic_state: Annotated[GenMap[str, TrafficState], DamlName("initialTrafficState")]
    is_dev_net: Annotated[bool, DamlName("isDevNet")]

    signatory: list[Party] = [dso]

    @choice(controller=dso, consuming=True)
    def DsoRules_AddSv(self, new_sv_party: Annotated[Party, DamlName("newSvParty")], new_sv_name: Annotated[str, DamlName("newSvName")], new_sv_reward_weight: Annotated[int, DamlName("newSvRewardWeight")], new_sv_participant_id: Annotated[str, DamlName("newSvParticipantId")], joined_as_of_round: Annotated[Round, DamlName("joinedAsOfRound")]) -> DsoRules_AddSvResult:
        pass

    @choice(controller=sv, consuming="nonconsuming")
    def DsoRules_UpdateAmuletPriceVote(self, sv: Party, vote_cid: Annotated[ContractId[AmuletPriceVote], DamlName("voteCid")], amulet_price: Annotated[Decimal, DamlName("amuletPrice")]) -> DsoRules_UpdateAmuletPriceVoteResult:
        pass

    @choice(controller=vote.sv, consuming="nonconsuming")
    def DsoRules_CastVote(self, request_cid: Annotated[ContractId[VoteRequest], DamlName("requestCid")], vote: Vote) -> DsoRules_CastVoteResult:
        pass

    @choice(controller=dso, consuming=True)
    def DsoRules_OffboardSv(self, sv: Party) -> DsoRules_OffboardSvResult:
        pass

    @choice(controller=sv, consuming="nonconsuming")
    def DsoRules_SubmitStatusReport(self, sv: Party, previous_report_cid: Annotated[ContractId[SvStatusReport], DamlName("previousReportCid")], status: SvStatus) -> DsoRules_SubmitStatusReportResult:
        pass

    @choice(controller=sv, consuming="nonconsuming")
    def DsoRules_AddConfirmedSv(self, sv: Party, sv_onboarding_confirmed_cid: Annotated[ContractId[SvOnboardingConfirmed], DamlName("svOnboardingConfirmedCid")], earliest_round_cid: Annotated[ContractId[OpenMiningRound], DamlName("earliestRoundCid")], middle_round_cid: Annotated[ContractId[OpenMiningRound], DamlName("middleRoundCid")], latest_round_cid: Annotated[ContractId[OpenMiningRound], DamlName("latestRoundCid")], amulet_rules_cid: Annotated[ContractId[AmuletRules], DamlName("amuletRulesCid")]) -> DsoRules_AddConfirmedSvResult:
        pass

    @choice(controller=sv, consuming="nonconsuming")
    def DsoRules_SetSynchronizerNodeConfig(self, sv: Party, synchronizer_id: Annotated[str, DamlName("synchronizerId")], new_node_config: Annotated[SynchronizerNodeConfig, DamlName("newNodeConfig")], node_state_cid: Annotated[ContractId[SvNodeState], DamlName("nodeStateCid")]) -> DsoRules_SetSynchronizerNodeConfigResult:
        pass

    @choice(controller=confirmer, consuming="nonconsuming")
    def DsoRules_ConfirmAction(self, confirmer: Party, action: ActionRequiringConfirmation) -> DsoRules_ConfirmActionResult:
        pass

    @choice(controller=[dso], consuming="nonconsuming")
    def DsoRules_ExecuteConfirmedAction(self, action: ActionRequiringConfirmation, amulet_rules_cid: Annotated[Optional[ContractId[AmuletRules]], DamlName("amuletRulesCid")], confirmation_cids: Annotated[list[ContractId[Confirmation]], DamlName("confirmationCids")], sv: Optional[Party]) -> DsoRules_ExecuteConfirmedActionResult:
        pass

    @choice(controller=requester, consuming="nonconsuming")
    def DsoRules_RequestVote(self, requester: Party, action: ActionRequiringConfirmation, reason: Reason, vote_request_timeout: Annotated[Optional[timedelta], DamlName("voteRequestTimeout")], target_effective_at: Annotated[Optional[datetime], DamlName("targetEffectiveAt")]) -> DsoRules_RequestVoteResult:
        pass

    @choice(controller=[dso], consuming="nonconsuming")
    def DsoRules_CloseVoteRequest(self, request_cid: Annotated[ContractId[VoteRequest], DamlName("requestCid")], amulet_rules_cid: Annotated[Optional[ContractId[AmuletRules]], DamlName("amuletRulesCid")], sv: Optional[Party]) -> DsoRules_CloseVoteRequestResult:
        pass

    @choice(controller=[dso], consuming="nonconsuming")
    def DsoRules_GarbageCollectAmuletPriceVotes(self, non_sv_vote_cids: Annotated[list[ContractId[AmuletPriceVote]], DamlName("nonSvVoteCids")], duplicate_vote_cids: Annotated[list[list[ContractId[AmuletPriceVote]]], DamlName("duplicateVoteCids")], sv: Optional[Party]) -> DsoRules_GarbageCollectAmuletPriceVotesResult:
        pass

    @choice(controller=dso, consuming=True)
    def DsoRules_SetConfig(self, new_config: Annotated[DsoRulesConfig, DamlName("newConfig")], base_config: Annotated[Optional[DsoRulesConfig], DamlName("baseConfig")]) -> DsoRules_SetConfigResult:
        pass

    @choice(controller=dso, consuming=True)
    def DsoRules_UpdateSvRewardWeight(self, sv_party: Annotated[Party, DamlName("svParty")], new_reward_weight: Annotated[int, DamlName("newRewardWeight")]) -> DsoRules_UpdateSvRewardWeightResult:
        pass

    @choice(controller=dso, consuming="nonconsuming")
    def DsoRules_GrantFeaturedAppRight(self, provider: Party, activity_weight: Annotated[Optional[Decimal], DamlName("activityWeight")]) -> DsoRules_GrantFeaturedAppRightResult:
        pass

    @choice(controller=dso, consuming="nonconsuming")
    def DsoRules_RevokeFeaturedAppRight(self, right_cid: Annotated[ContractId[FeaturedAppRight], DamlName("rightCid")]) -> DsoRules_RevokeFeaturedAppRightResult:
        pass

    @choice(controller=dso, consuming="nonconsuming")
    def DsoRules_UpdateFeaturedAppRight(self, right_cid: Annotated[ContractId[FeaturedAppRight], DamlName("rightCid")], update: FeaturedAppRight_Update) -> DsoRules_UpdateFeaturedAppRightResult:
        pass

    @choice(controller=sponsor, consuming="nonconsuming")
    def DsoRules_OnboardValidator(self, sponsor: Party, validator: Party, version: Optional[str], contact_point: Annotated[Optional[str], DamlName("contactPoint")]) -> DsoRules_OnboardValidatorResult:
        pass

    @choice(controller=[dso], consuming="nonconsuming")
    def DsoRules_MergeValidatorLicense(self, validator_license_cids: Annotated[list[ContractId[ValidatorLicense]], DamlName("validatorLicenseCids")], sv: Optional[Party]) -> DsoRules_MergeValidatorLicenseResult:
        pass

    @choice(controller=sponsor, consuming="nonconsuming")
    def DsoRules_StartSvOnboarding(self, candidate_name: Annotated[str, DamlName("candidateName")], candidate_party: Annotated[Party, DamlName("candidateParty")], candidate_participant_id: Annotated[str, DamlName("candidateParticipantId")], token: str, sponsor: Party) -> DsoRules_StartSvOnboardingResult:
        pass

    @choice(controller=[dso], consuming="nonconsuming")
    def DsoRules_ExpireSvOnboardingRequest(self, cid: ContractId[SvOnboardingRequest], sv: Optional[Party]) -> DsoRules_ExpireSvOnboardingRequestResult:
        pass

    @choice(controller=[dso], consuming="nonconsuming")
    def DsoRules_ArchiveSvOnboardingRequest(self, sv_onboarding_request_cid: Annotated[ContractId[SvOnboardingRequest], DamlName("svOnboardingRequestCid")], sv: Optional[Party]) -> DsoRules_ArchiveSvOnboardingRequestResult:
        pass

    @choice(controller=dso, consuming="nonconsuming")
    def DsoRules_ConfirmSvOnboarding(self, new_sv_party: Annotated[Party, DamlName("newSvParty")], new_sv_name: Annotated[str, DamlName("newSvName")], new_participant_id: Annotated[str, DamlName("newParticipantId")], new_sv_reward_weight: Annotated[int, DamlName("newSvRewardWeight")], reason: str) -> DsoRules_ConfirmSvOnboardingResult:
        pass

    @choice(controller=[dso], consuming=True)
    def DsoRules_ExpireSvOnboardingConfirmed(self, cid: ContractId[SvOnboardingConfirmed], sv: Optional[Party]) -> DsoRules_ExpireSvOnboardingConfirmedResult:
        pass

    @choice(controller=sv, consuming="nonconsuming")
    def DsoRules_ExpireAmuletAllocations(self, ext_amulet_rules_cid: Annotated[ContractId[ExternalPartyAmuletRules], DamlName("extAmuletRulesCid")], expire_allocations: Annotated[ExternalPartyAmuletRules_ExpireAmuletAllocations, DamlName("expireAllocations")], sv: Party) -> DsoRules_ExpireAmuletAllocationsResult:
        pass

    @choice(controller=sv, consuming="nonconsuming")
    def DsoRules_ExpireAmuletAllocationsV2(self, ext_amulet_rules_cid: Annotated[ContractId[ExternalPartyAmuletRules], DamlName("extAmuletRulesCid")], choice_arg: Annotated[ExternalPartyAmuletRules_ExpireAmuletAllocationsV2, DamlName("choiceArg")], sv: Party) -> DsoRules_ExpireAmuletAllocationsV2Result:
        pass

    @choice(controller=sv, consuming="nonconsuming")
    def DsoRules_Amulet_ExpireTransferInstructions(self, amulet_rules_cid: Annotated[ContractId[AmuletRules], DamlName("amuletRulesCid")], transfer_insts: Annotated[AmuletRules_Amulet_ExpireTransferInstructions, DamlName("transferInsts")], sv: Party) -> DsoRules_Amulet_ExpireTransferInstructionsResult:
        pass

    @choice(controller=[dso], consuming="nonconsuming")
    def DsoRules_Amulet_ExpireV2(self, cid: ContractId[Amulet], choice_arg: Annotated[Amulet_ExpireV2, DamlName("choiceArg")], sv: Optional[Party]) -> DsoRules_Amulet_ExpireV2Result:
        pass

    @choice(controller=[dso], consuming="nonconsuming")
    def DsoRules_LockedAmulet_ExpireAmulet(self, cid: ContractId[LockedAmulet], choice_arg: Annotated[LockedAmulet_ExpireAmulet, DamlName("choiceArg")], sv: Optional[Party]) -> DsoRules_LockedAmulet_ExpireAmuletResult:
        pass

    @choice(controller=[dso], consuming="nonconsuming")
    def DsoRules_LockedAmulet_ExpireAmuletV2(self, cid: ContractId[LockedAmulet], choice_arg: Annotated[LockedAmulet_ExpireAmuletV2, DamlName("choiceArg")], sv: Optional[Party]) -> DsoRules_LockedAmulet_ExpireAmuletV2Result:
        pass

    @choice(controller=[dso], consuming="nonconsuming")
    def DsoRules_AdvanceOpenMiningRounds(self, amulet_rules_cid: Annotated[ContractId[AmuletRules], DamlName("amuletRulesCid")], round_to_archive_cid: Annotated[ContractId[OpenMiningRound], DamlName("roundToArchiveCid")], middle_round_cid: Annotated[ContractId[OpenMiningRound], DamlName("middleRoundCid")], latest_round_cid: Annotated[ContractId[OpenMiningRound], DamlName("latestRoundCid")], amulet_price_vote_cids: Annotated[list[ContractId[AmuletPriceVote]], DamlName("amuletPriceVoteCids")], sv: Optional[Party]) -> DsoRules_AdvanceOpenMiningRoundsResult:
        pass

    @choice(controller=sv, consuming="nonconsuming")
    def DsoRules_UpdateExternalPartyConfigStates(self, amulet_rules_cid: Annotated[ContractId[AmuletRules], DamlName("amuletRulesCid")], external_party_config_state_cid0: Annotated[ContractId[ExternalPartyConfigState], DamlName("externalPartyConfigStateCid0")], external_party_config_state_cid1: Annotated[ContractId[ExternalPartyConfigState], DamlName("externalPartyConfigStateCid1")], open_mining_round_triple: Annotated[OpenMiningRoundTriple, DamlName("openMiningRoundTriple")], sv: Party) -> DsoRules_UpdateExternalPartyConfigStatesResult:
        pass

    @choice(controller=[dso], consuming="nonconsuming")
    def DsoRules_CollectEntryRenewalPayment(self, ans_entry_context_cid: Annotated[ContractId[AnsEntryContext], DamlName("ansEntryContextCid")], choice_arg: Annotated[AnsEntryContext_CollectEntryRenewalPayment, DamlName("choiceArg")], sv: Optional[Party]) -> DsoRules_CollectEntryRenewalPaymentResult:
        pass

    @choice(controller=[dso], consuming="nonconsuming")
    def DsoRules_ExpireAnsEntry(self, ans_entry_cid: Annotated[ContractId[AnsEntry], DamlName("ansEntryCid")], choice_arg: Annotated[AnsEntry_Expire, DamlName("choiceArg")], sv: Optional[Party]) -> DsoRules_ExpireAnsEntryResult:
        pass

    @choice(controller=[dso], consuming="nonconsuming")
    def DsoRules_ExpireSubscription(self, ans_entry_context_cid: Annotated[ContractId[AnsEntryContext], DamlName("ansEntryContextCid")], subscription_idle_state_cid: Annotated[ContractId[SubscriptionIdleState], DamlName("subscriptionIdleStateCid")], choice_arg: Annotated[SubscriptionIdleState_ExpireSubscription, DamlName("choiceArg")], sv: Optional[Party]) -> DsoRules_ExpireSubscriptionResult:
        pass

    @choice(controller=[dso], consuming="nonconsuming")
    def DsoRules_TerminateSubscription(self, ans_entry_context_cid: Annotated[ContractId[AnsEntryContext], DamlName("ansEntryContextCid")], terminated_subscription_cid: Annotated[ContractId[TerminatedSubscription], DamlName("terminatedSubscriptionCid")], sv: Optional[Party]) -> DsoRules_TerminateSubscriptionResult:
        pass

    @choice(controller=sv, consuming="nonconsuming")
    def DsoRules_ReceiveSvRewardCoupon(self, sv: Party, open_round_cid: Annotated[ContractId[OpenMiningRound], DamlName("openRoundCid")], reward_state_cid: Annotated[ContractId[SvRewardState], DamlName("rewardStateCid")], beneficiaries: list[tuple[Party, int]]) -> DsoRules_ReceiveSvRewardCouponResult:
        pass

    @choice(controller=[dso], consuming="nonconsuming")
    def DsoRules_ClaimExpiredRewards(self, amulet_rules_cid: Annotated[ContractId[AmuletRules], DamlName("amuletRulesCid")], choice_arg: Annotated[AmuletRules_ClaimExpiredRewards, DamlName("choiceArg")], sv: Optional[Party]) -> DsoRules_ClaimExpiredRewardsResult:
        pass

    @choice(controller=sv, consuming="nonconsuming")
    def DsoRules_ClaimExpiredRewardsV2(self, amulet_rules_cid: Annotated[ContractId[AmuletRules], DamlName("amuletRulesCid")], choice_arg: Annotated[AmuletRules_ClaimExpiredRewardsV2, DamlName("choiceArg")], sv: Party) -> DsoRules_ClaimExpiredRewardsV2Result:
        pass

    @choice(controller=sv, consuming="nonconsuming")
    def DsoRules_ProcessRewardsV2_ProcessBatch(self, process_rewards_cid: Annotated[ContractId[ProcessRewardsV2], DamlName("processRewardsCid")], choice_arg: Annotated[ProcessRewardsV2_ProcessBatch, DamlName("choiceArg")], sv: Party) -> DsoRules_ProcessRewardsV2_ProcessBatchResult:
        pass

    @choice(controller=sv, consuming="nonconsuming")
    def DsoRules_UnhideRewardCouponsV2(self, amulet_rules_cid: Annotated[ContractId[AmuletRules], DamlName("amuletRulesCid")], choice_arg: Annotated[AmuletRules_UnhideRewardCouponsV2, DamlName("choiceArg")], sv: Party) -> DsoRules_UnhideRewardCouponsV2Result:
        pass

    @choice(controller=sv, consuming="nonconsuming")
    def DsoRules_ArchiveDryRunRewardAccountingV2(self, amulet_rules_cid: Annotated[ContractId[AmuletRules], DamlName("amuletRulesCid")], choice_arg: Annotated[AmuletRules_ArchiveDryRunRewardAccountingV2, DamlName("choiceArg")], sv: Party) -> DsoRules_ArchiveDryRunRewardAccountingV2Result:
        pass

    @choice(controller=[dso], consuming="nonconsuming")
    def DsoRules_MergeUnclaimedRewards(self, amulet_rules_cid: Annotated[ContractId[AmuletRules], DamlName("amuletRulesCid")], unclaimed_reward_cids: Annotated[list[ContractId[UnclaimedReward]], DamlName("unclaimedRewardCids")], sv: Optional[Party]) -> DsoRules_MergeUnclaimedRewardsResult:
        pass

    @choice(controller=sv, consuming="nonconsuming")
    def DsoRules_MergeUnclaimedDevelopmentFundCoupons(self, amulet_rules_cid: Annotated[ContractId[AmuletRules], DamlName("amuletRulesCid")], choice_arg: Annotated[AmuletRules_MergeUnclaimedDevelopmentFundCoupons, DamlName("choiceArg")], sv: Party) -> DsoRules_MergeUnclaimedDevelopmentFundCouponsResult:
        pass

    @choice(controller=sv, consuming="nonconsuming")
    def DsoRules_ExpireDevelopmentFundCoupon(self, development_fund_coupon_cid: Annotated[ContractId[DevelopmentFundCoupon], DamlName("developmentFundCouponCid")], sv: Party) -> DsoRules_ExpireDevelopmentFundCouponResult:
        pass

    @choice(controller=[dso], consuming="nonconsuming")
    def DsoRules_MiningRound_Close(self, amulet_rules_cid: Annotated[ContractId[AmuletRules], DamlName("amuletRulesCid")], issuing_round_cid: Annotated[ContractId[IssuingMiningRound], DamlName("issuingRoundCid")], sv: Optional[Party]) -> DsoRules_MiningRound_CloseResult:
        pass

    @choice(controller=[dso], consuming="nonconsuming")
    def DsoRules_ExpireStaleConfirmation(self, stale_confirmation_cid: Annotated[ContractId[Confirmation], DamlName("staleConfirmationCid")], sv: Optional[Party]) -> DsoRules_ExpireStaleConfirmationResult:
        pass

    @choice(controller=[dso], consuming="nonconsuming")
    def DsoRules_MergeMemberTrafficContracts(self, amulet_rules_cid: Annotated[ContractId[AmuletRules], DamlName("amuletRulesCid")], traffic_cids: Annotated[list[ContractId[MemberTraffic]], DamlName("trafficCids")], sv: Optional[Party]) -> DsoRules_MergeMemberTrafficContractsResult:
        pass

    @choice(controller=[dso], consuming="nonconsuming")
    def DsoRules_MergeSvRewardState(self, sv_name: Annotated[str, DamlName("svName")], reward_state_cids: Annotated[list[ContractId[SvRewardState]], DamlName("rewardStateCids")], sv: Optional[Party]) -> DsoRules_MergeSvRewardStateResult:
        pass

    @choice(controller=dso, consuming="nonconsuming")
    def DsoRules_CreateExternalPartyAmuletRules(self) -> DsoRules_CreateExternalPartyAmuletRulesResult:
        pass

    @choice(controller=dso, consuming="nonconsuming")
    def DsoRules_CreateTransferCommandCounter(self, sender: Party) -> DsoRules_CreateTransferCommandCounterResult:
        pass

    @choice(controller=[dso], consuming="nonconsuming")
    def DsoRules_ExpireTransferPreapproval(self, transfer_preapproval_cid: Annotated[ContractId[TransferPreapproval], DamlName("transferPreapprovalCid")], sv: Optional[Party]) -> DsoRules_ExpireTransferPreapprovalResult:
        pass

    @choice(controller=[dso], consuming="nonconsuming")
    def DsoRules_AmuletRules_ConvertFeaturedAppActivityMarkers(self, amulet_rules_cid: Annotated[ContractId[AmuletRules], DamlName("amuletRulesCid")], argument: AmuletRules_ConvertFeaturedAppActivityMarkers, sv: Optional[Party]) -> DsoRules_AmuletRules_ConvertFeaturedAppActivityMarkersResult:
        pass

    @choice(controller=dso, consuming="nonconsuming")
    def DsoRules_CreateUnallocatedUnclaimedActivityRecord(self, beneficiary: Party, amount: Decimal, reason: str, expires_at: Annotated[datetime, DamlName("expiresAt")]) -> DsoRules_CreateUnallocatedUnclaimedActivityRecordResult:
        pass

    @choice(controller=sv, consuming="nonconsuming")
    def DsoRules_AllocateUnallocatedUnclaimedActivityRecord(self, unallocated_unclaimed_activity_record_cid: Annotated[ContractId[UnallocatedUnclaimedActivityRecord], DamlName("unallocatedUnclaimedActivityRecordCid")], amulet_rules_cid: Annotated[ContractId[AmuletRules], DamlName("amuletRulesCid")], unclaimed_rewards_to_burn_cids: Annotated[list[ContractId[UnclaimedReward]], DamlName("unclaimedRewardsToBurnCids")], sv: Party) -> DsoRules_AllocateUnallocatedUnclaimedActivityRecordResult:
        pass

    @choice(controller=sv, consuming="nonconsuming")
    def DsoRules_ExpireUnallocatedUnclaimedActivityRecord(self, unallocated_unclaimed_activity_record_cid: Annotated[ContractId[UnallocatedUnclaimedActivityRecord], DamlName("unallocatedUnclaimedActivityRecordCid")], sv: Party) -> DsoRules_ExpireUnallocatedUnclaimedActivityRecordResult:
        pass

    @choice(controller=sv, consuming="nonconsuming")
    def DsoRules_ExpireUnclaimedActivityRecord(self, unclaimed_activity_record_cid: Annotated[ContractId[UnclaimedActivityRecord], DamlName("unclaimedActivityRecordCid")], sv: Party) -> DsoRules_ExpireUnclaimedActivityRecordResult:
        pass

    @choice(controller=dso, consuming="nonconsuming")
    def DsoRules_CreateBootstrapExternalPartyConfigStateInstruction(self) -> DsoRules_CreateBootstrapExternalPartyConfigStateInstructionResult:
        pass

    @choice(controller=sv, consuming="nonconsuming")
    def DsoRules_BootstrapExternalPartyConfigState(self, amulet_rules_cid: Annotated[ContractId[AmuletRules], DamlName("amuletRulesCid")], instruction_cid: Annotated[ContractId[BootstrapExternalPartyConfigStateInstruction], DamlName("instructionCid")], open_mining_round_triple: Annotated[OpenMiningRoundTriple, DamlName("openMiningRoundTriple")], sv: Party) -> DsoRules_BootstrapExternalPartyConfigStateResult:
        pass

    @choice(controller=[dso], consuming="nonconsuming")
    def DsoRules_PruneAmuletConfigSchedule(self, amulet_rules_cid: Annotated[ContractId[AmuletRules], DamlName("amuletRulesCid")], sv: Optional[Party]) -> DsoRules_PruneAmuletConfigScheduleResult:
        pass

    @choice(controller=requester, consuming="nonconsuming")
    def DsoRules_RequestElection(self, requester: Party, reason: ElectionRequestReason, ranking: list[Party]) -> DsoRules_RequestElectionResult:
        pass

    @choice(controller=actor, consuming=True)
    def DsoRules_ElectDsoDelegate(self, actor: Party, request_cids: Annotated[list[ContractId[ElectionRequest]], DamlName("requestCids")]) -> DsoRules_ElectDsoDelegateResult:
        pass

    @choice(controller=[dso], consuming="nonconsuming")
    def DsoRules_ArchiveOutdatedElectionRequest(self, request_cid: Annotated[ContractId[ElectionRequest], DamlName("requestCid")], sv: Optional[Party]) -> DsoRules_ArchiveOutdatedElectionRequestResult:
        pass

    @choice(controller=[dso], consuming="nonconsuming")
    def DsoRules_Amulet_Expire(self, cid: ContractId[Amulet], choice_arg: Annotated[Amulet_Expire, DamlName("choiceArg")], sv: Optional[Party]) -> DsoRules_Amulet_ExpireResult:
        pass


@template
class UnallocatedUnclaimedActivityRecord:
    dso: Party
    beneficiary: Party
    amount: Decimal
    reason: str
    expires_at: Annotated[datetime, DamlName("expiresAt")]

    signatory: list[Party] = [dso]


@template
class BootstrapExternalPartyConfigStateInstruction:
    dso: Party

    signatory: list[Party] = [dso]


@DamlCaseAccessor("VRO_AcceptedButActionFailed")
def vro_accepted_but_action_failed(value: VoteRequestOutcome) -> Optional[str]:
    pass


@DamlCaseAccessor("VRO_Accepted")
def vro_accepted(value: VoteRequestOutcome) -> Optional[datetime]:
    pass


@DamlCaseAccessor("VRO_Rejected", arity=0)
def vro_rejected(value: VoteRequestOutcome) -> Optional[None]:
    pass


@DamlCaseAccessor("VRO_Expired", arity=0)
def vro_expired(value: VoteRequestOutcome) -> Optional[None]:
    pass


@DamlCaseAccessor("ExtVoteRequestOutcome")
def ext_vote_request_outcome(value: VoteRequestOutcome) -> Optional[None]:
    pass


@DamlCaseAccessor("ERR_DsoDelegateUnavailable", arity=0)
def err_dso_delegate_unavailable(value: ElectionRequestReason) -> Optional[None]:
    pass


@DamlCaseAccessor("ERR_OtherReason")
def err_other_reason(value: ElectionRequestReason) -> Optional[str]:
    pass


@DamlCaseAccessor("ExtElectionRequestReason")
def ext_election_request_reason(value: ElectionRequestReason) -> Optional[None]:
    pass


@DamlCaseAccessor("ANSRARC_CollectInitialEntryPayment")
def ansrarc_collect_initial_entry_payment(value: AnsEntryContext_ActionRequiringConfirmation) -> Optional[AnsEntryContext_CollectInitialEntryPayment]:
    pass


@DamlCaseAccessor("ANSRARC_RejectEntryInitialPayment")
def ansrarc_reject_entry_initial_payment(value: AnsEntryContext_ActionRequiringConfirmation) -> Optional[AnsEntryContext_RejectEntryInitialPayment]:
    pass


@DamlCaseAccessor("SRARC_AddSv")
def srarc_add_sv(value: DsoRules_ActionRequiringConfirmation) -> Optional[DsoRules_AddSv]:
    pass


@DamlCaseAccessor("SRARC_OffboardSv")
def srarc_offboard_sv(value: DsoRules_ActionRequiringConfirmation) -> Optional[DsoRules_OffboardSv]:
    pass


@DamlCaseAccessor("SRARC_ConfirmSvOnboarding")
def srarc_confirm_sv_onboarding(value: DsoRules_ActionRequiringConfirmation) -> Optional[DsoRules_ConfirmSvOnboarding]:
    pass


@DamlCaseAccessor("SRARC_GrantFeaturedAppRight")
def srarc_grant_featured_app_right(value: DsoRules_ActionRequiringConfirmation) -> Optional[DsoRules_GrantFeaturedAppRight]:
    pass


@DamlCaseAccessor("SRARC_RevokeFeaturedAppRight")
def srarc_revoke_featured_app_right(value: DsoRules_ActionRequiringConfirmation) -> Optional[DsoRules_RevokeFeaturedAppRight]:
    pass


@DamlCaseAccessor("SRARC_SetConfig")
def srarc_set_config(value: DsoRules_ActionRequiringConfirmation) -> Optional[DsoRules_SetConfig]:
    pass


@DamlCaseAccessor("SRARC_UpdateSvRewardWeight")
def srarc_update_sv_reward_weight(value: DsoRules_ActionRequiringConfirmation) -> Optional[DsoRules_UpdateSvRewardWeight]:
    pass


@DamlCaseAccessor("SRARC_CreateExternalPartyAmuletRules")
def srarc_create_external_party_amulet_rules(value: DsoRules_ActionRequiringConfirmation) -> Optional[DsoRules_CreateExternalPartyAmuletRules]:
    pass


@DamlCaseAccessor("SRARC_CreateTransferCommandCounter")
def srarc_create_transfer_command_counter(value: DsoRules_ActionRequiringConfirmation) -> Optional[DsoRules_CreateTransferCommandCounter]:
    pass


@DamlCaseAccessor("SRARC_CreateUnallocatedUnclaimedActivityRecord")
def srarc_create_unallocated_unclaimed_activity_record(value: DsoRules_ActionRequiringConfirmation) -> Optional[DsoRules_CreateUnallocatedUnclaimedActivityRecord]:
    pass


@DamlCaseAccessor("SRARC_CreateBootstrapExternalPartyConfigStateInstruction")
def srarc_create_bootstrap_external_party_config_state_instruction(value: DsoRules_ActionRequiringConfirmation) -> Optional[DsoRules_CreateBootstrapExternalPartyConfigStateInstruction]:
    pass


@DamlCaseAccessor("SRARC_UpdateFeaturedAppRight")
def srarc_update_featured_app_right(value: DsoRules_ActionRequiringConfirmation) -> Optional[DsoRules_UpdateFeaturedAppRight]:
    pass


@DamlCaseAccessor("CRARC_MiningRound_StartIssuing")
def crarc_mining_round_start_issuing(value: AmuletRules_ActionRequiringConfirmation) -> Optional[AmuletRules_MiningRound_StartIssuing]:
    pass


@DamlCaseAccessor("CRARC_MiningRound_Archive")
def crarc_mining_round_archive(value: AmuletRules_ActionRequiringConfirmation) -> Optional[AmuletRules_MiningRound_Archive]:
    pass


@DamlCaseAccessor("CRARC_AddFutureAmuletConfigSchedule")
def crarc_add_future_amulet_config_schedule(value: AmuletRules_ActionRequiringConfirmation) -> Optional[AmuletRules_AddFutureAmuletConfigSchedule]:
    pass


@DamlCaseAccessor("CRARC_RemoveFutureAmuletConfigSchedule")
def crarc_remove_future_amulet_config_schedule(value: AmuletRules_ActionRequiringConfirmation) -> Optional[AmuletRules_RemoveFutureAmuletConfigSchedule]:
    pass


@DamlCaseAccessor("CRARC_UpdateFutureAmuletConfigSchedule")
def crarc_update_future_amulet_config_schedule(value: AmuletRules_ActionRequiringConfirmation) -> Optional[AmuletRules_UpdateFutureAmuletConfigSchedule]:
    pass


@DamlCaseAccessor("CRARC_SetConfig")
def crarc_set_config(value: AmuletRules_ActionRequiringConfirmation) -> Optional[AmuletRules_SetConfig]:
    pass


@DamlCaseAccessor("CRARC_StartProcessingRewardsV2")
def crarc_start_processing_rewards_v2(value: AmuletRules_ActionRequiringConfirmation) -> Optional[AmuletRules_StartProcessingRewardsV2]:
    pass


@DamlCaseAccessor("ARC_DsoRules")
def arc_dso_rules(value: ActionRequiringConfirmation) -> Optional[DsoRules_ActionRequiringConfirmation]:
    pass


@DamlCaseAccessor("ARC_AmuletRules")
def arc_amulet_rules(value: ActionRequiringConfirmation) -> Optional[AmuletRules_ActionRequiringConfirmation]:
    pass


@DamlCaseAccessor("ARC_AnsEntryContext", arity=2)
def arc_ans_entry_context(value: ActionRequiringConfirmation) -> Optional[tuple[ContractId[AnsEntryContext], AnsEntryContext_ActionRequiringConfirmation]]:
    pass


@DamlCaseAccessor("ExtActionRequiringConformation")
def ext_action_requiring_conformation(value: ActionRequiringConfirmation) -> Optional[None]:
    pass


@DamlName("getVoteCooldownTime")
def get_vote_cooldown_time(config: DsoRulesConfig) -> timedelta:
    pass


@DamlName("pruneAtLeastOne")
def prune_at_least_one(now: T, schedule: Schedule[T, A]) -> Optional[Schedule[T, A]]:
    pass


@DamlName("summarizeDso")
def summarize_dso(dso_rules: DsoRules) -> DsoSummary:
    pass


@DamlName("executeActionRequiringConfirmation", is_ledger_effect=True)
def execute_action_requiring_confirmation(party: Party, contract_id: ContractId[DsoRules], amulet_rules_cid: Optional[ContractId[AmuletRules]], act: ActionRequiringConfirmation) -> None:
    pass


@DamlName("requireWellformedReason", is_ledger_effect=True)
def require_wellformed_reason(config: DsoRulesConfig, reason: Reason) -> None:
    pass


@DamlName("requireWellformedVote", is_ledger_effect=True)
def require_wellformed_vote(config: DsoRulesConfig, vote: Vote) -> None:
    pass


@DamlName("ensureNotExpired", is_ledger_effect=True)
def ensure_not_expired(expires_at: datetime) -> None:
    pass


@DamlName("actionRequiringConfirmationEffectiveAt")
def action_requiring_confirmation_effective_at(action: ActionRequiringConfirmation) -> Optional[datetime]:
    pass


@DamlName("getSvInfo", is_ledger_effect=True)
def get_sv_info(operator: Party, this: DsoRules) -> SvInfo:
    pass


@DamlName("lookupSvInfoByName")
def lookup_sv_info_by_name(sv_name: str, dso_rules: DsoRules) -> Optional[tuple[Party, SvInfo]]:
    pass


@DamlName("svHasBeenOnboardedBefore")
def sv_has_been_onboarded_before(sv_name: str, this: DsoRules) -> bool:
    pass


@DamlName("ensureNeverOperatedNode", is_ledger_effect=True)
def ensure_never_operated_node(new_sv_party: Party, this: DsoRules) -> None:
    pass


@DamlName("dsoRules_addSv", is_ledger_effect=True)
def dso_rules_add_sv(this0: DsoRules, arg: DsoRules_AddSv) -> ContractId[DsoRules]:
    pass


@DamlName("createPerSvContracts", is_ledger_effect=True)
def create_per_sv_contracts(dso_rules: DsoRules, dso_rules_add_sv: DsoRules_AddSv) -> None:
    pass


@DamlName("createPerSvPartyContracts", is_ledger_effect=True)
def create_per_sv_party_contracts(party: Party, new_sv_party: Party, new_sv_name: str, synchronizer_nodes: GenMap[str, SynchronizerNodeConfig], amulet_price: Optional[Decimal], vote_cooldown_time: timedelta) -> None:
    pass


@DamlName("getAndValidateSvParty", is_ledger_effect=True)
def get_and_validate_sv_party(dso_rules: DsoRules, optional: Optional[Party]) -> Party:
    pass


@DamlName("enforceCooldown", is_ledger_effect=True)
def enforce_cooldown(cooldown_name: str, cooldown: timedelta, last_action_time: Optional[datetime]) -> None:
    pass
