from datetime import datetime, timedelta
from typing import Annotated

from forge.models import choice, ContractId, Decimal, ledger_effect, Optional, Party, template, variant, variant_record
from forge.builtins import DamlCaseAccessor, DamlName, no_derive
from Splice.Amulet import Amulet, FeaturedAppRight
from Splice.AmuletRules import AmuletRules, ExternalPartySetupProposal, InvalidTransferReason, PaymentTransferContext, Transfer, TransferInput, TransferPreapproval, TransferResult
from Splice.Api.Token.AllocationInstructionV1 import AllocationFactory, AllocationFactory_Allocate, AllocationInstructionResult
from Splice.Api.Token.AllocationRequestV2 import AllocationRequest
from Splice.Api.Token.AllocationV1 import Allocation, Allocation_Withdraw, Allocation_WithdrawResult
from Splice.Api.Token.MetadataV1 import AnyContract, AnyValue
from Splice.Api.Token.TransferInstructionV1 import TransferFactory, TransferFactory_Transfer, TransferInstruction, TransferInstructionResult, TransferInstruction_Accept, TransferInstruction_Reject, TransferInstruction_Withdraw
from Splice.DecentralizedSynchronizer import MemberTraffic
from Splice.Wallet.BuyTrafficRequest import BuyTrafficRequest, BuyTrafficRequestTrackingInfo
from Splice.Wallet.Payment import AcceptedAppPayment, AppPaymentRequest, PaymentAmount, TerminatedAppPayment
from Splice.Wallet.Subscriptions import SubscriptionIdleState, SubscriptionInitialPayment, SubscriptionPayment, SubscriptionRequest, TerminatedSubscription
from Splice.Wallet.TopUpState import ValidatorTopUpState
from Splice.Wallet.TransferOffer import AcceptedTransferOffer, TransferOffer, TransferOfferTrackingInfo
from Splice.Wallet.TransferPreapproval import TransferPreapprovalProposal
import Splice.Api.Token.AllocationInstructionV2 as AllocationInstructionV2
import Splice.Api.Token.AllocationV2 as AllocationV2
import Splice.Api.Token.TransferInstructionV2 as TransferInstructionV2


@no_derive
@variant
class WalletAppInstall_FeaturedAppRights_CancelResult:
    def WalletAppInstall_FeaturedAppRights_CancelResult(): pass


@variant
class AmuletOperationOutcome:
    def COO_AcceptedAppPayment(value: ContractId[AcceptedAppPayment]): pass
    def COO_CompleteAcceptedTransfer(value: tuple[TransferResult, TransferOfferTrackingInfo]): pass
    def COO_SubscriptionInitialPayment(value: ContractId[SubscriptionInitialPayment]): pass
    def COO_SubscriptionPayment(value: ContractId[SubscriptionPayment]): pass
    def COO_MergeTransferInputs(value: Optional[ContractId[Amulet]]): pass
    def COO_BuyMemberTraffic(value: ContractId[MemberTraffic]): pass
    def COO_CompleteBuyTrafficRequest(value: tuple[ContractId[MemberTraffic], BuyTrafficRequestTrackingInfo]): pass
    def COO_Tap(value: ContractId[Amulet]): pass
    def COO_Error(value: InvalidTransferReason): pass
    @variant_record
    def ExtAmuletOperationOutcome(dummy_unit_field: Annotated[None, DamlName("dummyUnitField")]): pass
    def COO_CreateExternalPartySetupProposal(value: ContractId[ExternalPartySetupProposal]): pass
    def COO_AcceptTransferPreapprovalProposal(value: ContractId[TransferPreapproval]): pass
    def COO_RenewTransferPreapproval(value: ContractId[TransferPreapproval]): pass
    def COO_TransferPreapprovalSend(value: Optional[ContractId[Amulet]]): pass


@variant
class AmuletOperation:
    def CO_AppPayment(value: ContractId[AppPaymentRequest]): pass
    def CO_CompleteAcceptedTransfer(value: ContractId[AcceptedTransferOffer]): pass
    def CO_SubscriptionAcceptAndMakeInitialPayment(value: ContractId[SubscriptionRequest]): pass
    def CO_SubscriptionMakePayment(value: ContractId[SubscriptionIdleState]): pass
    def CO_MergeTransferInputs(): pass
    @variant_record
    def CO_BuyMemberTraffic(traffic_amount: Annotated[int, DamlName("trafficAmount")], member_id: Annotated[str, DamlName("memberId")], synchronizer_id: Annotated[str, DamlName("synchronizerId")], migration_id: Annotated[int, DamlName("migrationId")], min_topup_interval: Annotated[timedelta, DamlName("minTopupInterval")], topup_state_cid: Annotated[Optional[ContractId[ValidatorTopUpState]], DamlName("topupStateCid")]): pass
    @variant_record
    def CO_CompleteBuyTrafficRequest(traffic_request_cid: Annotated[ContractId[BuyTrafficRequest], DamlName("trafficRequestCid")]): pass
    @variant_record
    def CO_Tap(tap_amount: Annotated[Decimal, DamlName("tapAmount")]): pass
    @variant_record
    def ExtAmuletOperation(dummy_unit_field: Annotated[None, DamlName("dummyUnitField")]): pass
    @variant_record
    def CO_CreateExternalPartySetupProposal(external_party: Annotated[Party, DamlName("externalParty")], preapproval_expires_at: Annotated[datetime, DamlName("preapprovalExpiresAt")]): pass
    @variant_record
    def CO_AcceptTransferPreapprovalProposal(preapproval_proposal_cid: Annotated[ContractId[TransferPreapprovalProposal], DamlName("preapprovalProposalCid")], expires_at: Annotated[datetime, DamlName("expiresAt")]): pass
    @variant_record
    def CO_RenewTransferPreapproval(previous_approval_cid: Annotated[ContractId[TransferPreapproval], DamlName("previousApprovalCid")], new_expires_at: Annotated[datetime, DamlName("newExpiresAt")]): pass
    @variant_record
    def CO_TransferPreapprovalSend(transfer_preapproval_cid: Annotated[ContractId[TransferPreapproval], DamlName("transferPreapprovalCid")], provider_featured_app_right_cid: Annotated[Optional[ContractId[FeaturedAppRight]], DamlName("providerFeaturedAppRightCid")], amount: Decimal, description: Optional[str]): pass


@no_derive
struct ExecutionContext:
    dso: Party
    end_user: Annotated[Party, DamlName("endUser")]
    validator: Party
    payment_context: Annotated[PaymentTransferContext, DamlName("paymentContext")]


struct WalletAppInstall_ExecuteBatchResult:
    end_user_name: Annotated[str, DamlName("endUserName")]
    outcomes: list[AmuletOperationOutcome]
    opt_end_user_party: Annotated[Optional[Party], DamlName("optEndUserParty")]


@no_derive
struct WalletAppInstall_AppPaymentRequest_RejectResult:
    terminated_app_payment: Annotated[ContractId[TerminatedAppPayment], DamlName("terminatedAppPayment")]


@no_derive
struct WalletAppInstall_AppPaymentRequest_ExpireResult:
    terminated_app_payment: Annotated[ContractId[TerminatedAppPayment], DamlName("terminatedAppPayment")]


@no_derive
struct WalletAppInstall_SubscriptionRequest_RejectResult:
    terminated_subscription: Annotated[ContractId[TerminatedSubscription], DamlName("terminatedSubscription")]


@no_derive
struct WalletAppInstall_SubscriptionIdleState_CancelSubscriptionResult:
    terminated_subscription: Annotated[ContractId[TerminatedSubscription], DamlName("terminatedSubscription")]


@no_derive
struct WalletAppInstall_CreateTransferOfferResult:
    transfer_offer: Annotated[ContractId[TransferOffer], DamlName("transferOffer")]


@no_derive
struct WalletAppInstall_TransferOffer_AcceptResult:
    accepted_transfer_offer: Annotated[ContractId[AcceptedTransferOffer], DamlName("acceptedTransferOffer")]


@no_derive
struct WalletAppInstall_TransferOffer_RejectResult:
    tracking_info: Annotated[TransferOfferTrackingInfo, DamlName("trackingInfo")]


@no_derive
struct WalletAppInstall_TransferOffer_WithdrawResult:
    tracking_info: Annotated[TransferOfferTrackingInfo, DamlName("trackingInfo")]


@no_derive
struct WalletAppInstall_TransferOffer_ExpireResult:
    tracking_info: Annotated[TransferOfferTrackingInfo, DamlName("trackingInfo")]


@no_derive
struct WalletAppInstall_AcceptedTransferOffer_AbortResult:
    tracking_info: Annotated[TransferOfferTrackingInfo, DamlName("trackingInfo")]


@no_derive
struct WalletAppInstall_AcceptedTransferOffer_WithdrawResult:
    tracking_info: Annotated[TransferOfferTrackingInfo, DamlName("trackingInfo")]


@no_derive
struct WalletAppInstall_AcceptedTransferOffer_ExpireResult:
    tracking_info: Annotated[TransferOfferTrackingInfo, DamlName("trackingInfo")]


@no_derive
struct WalletAppInstall_CreateBuyTrafficRequestResult:
    buy_traffic_request: Annotated[ContractId[BuyTrafficRequest], DamlName("buyTrafficRequest")]


@no_derive
struct WalletAppInstall_BuyTrafficRequest_CancelResult:
    tracking_info: Annotated[BuyTrafficRequestTrackingInfo, DamlName("trackingInfo")]


@no_derive
struct WalletAppInstall_BuyTrafficRequest_ExpireResult:
    tracking_info: Annotated[BuyTrafficRequestTrackingInfo, DamlName("trackingInfo")]


@no_derive
struct WalletAppInstall_FeaturedAppRights_SelfGrantResult:
    featured_app_right: Annotated[ContractId[FeaturedAppRight], DamlName("featuredAppRight")]


@no_derive
struct WalletAppInstall_TransferPreapprovalProposal_CreateResult:
    preapproval_proposal_cid: Annotated[ContractId[TransferPreapprovalProposal], DamlName("preapprovalProposalCid")]


@template
class WalletAppInstall:
    dso_party: Annotated[Party, DamlName("dsoParty")]
    validator_party: Annotated[Party, DamlName("validatorParty")]
    end_user_name: Annotated[str, DamlName("endUserName")]
    end_user_party: Annotated[Party, DamlName("endUserParty")]

    signatory: list[Party] = [validator_party, end_user_party]

    @choice(controller=validator_party, consuming="nonconsuming")
    def WalletAppInstall_ExecuteBatch(self, context: PaymentTransferContext, inputs: list[TransferInput], operations: list[AmuletOperation]) -> WalletAppInstall_ExecuteBatchResult:
        pass

    @choice(controller=validator_party, consuming="nonconsuming")
    def WalletAppInstall_AppPaymentRequest_Reject(self, cid: ContractId[AppPaymentRequest]) -> WalletAppInstall_AppPaymentRequest_RejectResult:
        pass

    @choice(controller=validator_party, consuming="nonconsuming")
    def WalletAppInstall_AppPaymentRequest_Expire(self, cid: ContractId[AppPaymentRequest]) -> WalletAppInstall_AppPaymentRequest_ExpireResult:
        pass

    @choice(controller=validator_party, consuming="nonconsuming")
    def WalletAppInstall_SubscriptionRequest_Reject(self, cid: ContractId[SubscriptionRequest]) -> WalletAppInstall_SubscriptionRequest_RejectResult:
        pass

    @choice(controller=validator_party, consuming="nonconsuming")
    def WalletAppInstall_SubscriptionIdleState_CancelSubscription(self, cid: ContractId[SubscriptionIdleState]) -> WalletAppInstall_SubscriptionIdleState_CancelSubscriptionResult:
        pass

    @choice(controller=validator_party, consuming="nonconsuming")
    def WalletAppInstall_CreateTransferOffer(self, receiver: Party, amount: PaymentAmount, description: str, expires_at: Annotated[datetime, DamlName("expiresAt")], tracking_id: Annotated[str, DamlName("trackingId")]) -> WalletAppInstall_CreateTransferOfferResult:
        pass

    @choice(controller=validator_party, consuming="nonconsuming")
    def WalletAppInstall_TransferOffer_Accept(self, cid: ContractId[TransferOffer]) -> WalletAppInstall_TransferOffer_AcceptResult:
        pass

    @choice(controller=validator_party, consuming="nonconsuming")
    def WalletAppInstall_TransferOffer_Reject(self, cid: ContractId[TransferOffer]) -> WalletAppInstall_TransferOffer_RejectResult:
        pass

    @choice(controller=validator_party, consuming="nonconsuming")
    def WalletAppInstall_TransferOffer_Withdraw(self, cid: ContractId[TransferOffer], reason: str) -> WalletAppInstall_TransferOffer_WithdrawResult:
        pass

    @choice(controller=validator_party, consuming="nonconsuming")
    def WalletAppInstall_TransferOffer_Expire(self, cid: ContractId[TransferOffer]) -> WalletAppInstall_TransferOffer_ExpireResult:
        pass

    @choice(controller=validator_party, consuming="nonconsuming")
    def WalletAppInstall_AcceptedTransferOffer_Abort(self, cid: ContractId[AcceptedTransferOffer], reason: str) -> WalletAppInstall_AcceptedTransferOffer_AbortResult:
        pass

    @choice(controller=validator_party, consuming="nonconsuming")
    def WalletAppInstall_AcceptedTransferOffer_Withdraw(self, cid: ContractId[AcceptedTransferOffer], reason: str) -> WalletAppInstall_AcceptedTransferOffer_WithdrawResult:
        pass

    @choice(controller=validator_party, consuming="nonconsuming")
    def WalletAppInstall_AcceptedTransferOffer_Expire(self, cid: ContractId[AcceptedTransferOffer]) -> WalletAppInstall_AcceptedTransferOffer_ExpireResult:
        pass

    @choice(controller=validator_party, consuming="nonconsuming")
    def WalletAppInstall_CreateBuyTrafficRequest(self, member_id: Annotated[str, DamlName("memberId")], synchronizer_id: Annotated[str, DamlName("synchronizerId")], migration_id: Annotated[int, DamlName("migrationId")], traffic_amount: Annotated[int, DamlName("trafficAmount")], expires_at: Annotated[datetime, DamlName("expiresAt")], tracking_id: Annotated[str, DamlName("trackingId")]) -> WalletAppInstall_CreateBuyTrafficRequestResult:
        pass

    @choice(controller=validator_party, consuming="nonconsuming")
    def WalletAppInstall_BuyTrafficRequest_Cancel(self, request_cid: Annotated[ContractId[BuyTrafficRequest], DamlName("requestCid")], reason: str) -> WalletAppInstall_BuyTrafficRequest_CancelResult:
        pass

    @choice(controller=validator_party, consuming="nonconsuming")
    def WalletAppInstall_BuyTrafficRequest_Expire(self, request_cid: Annotated[ContractId[BuyTrafficRequest], DamlName("requestCid")]) -> WalletAppInstall_BuyTrafficRequest_ExpireResult:
        pass

    @choice(controller=validator_party, consuming="nonconsuming")
    def WalletAppInstall_FeaturedAppRights_Cancel(self, cid: ContractId[FeaturedAppRight]) -> WalletAppInstall_FeaturedAppRights_CancelResult:
        pass

    @choice(controller=validator_party, consuming="nonconsuming")
    def WalletAppInstall_FeaturedAppRights_SelfGrant(self, amulet_rules_cid: Annotated[ContractId[AmuletRules], DamlName("amuletRulesCid")]) -> WalletAppInstall_FeaturedAppRights_SelfGrantResult:
        pass

    @choice(controller=validator_party, consuming="nonconsuming")
    def WalletAppInstall_TransferFactory_Transfer(self, transfer_factory_cid: Annotated[ContractId[TransferFactory], DamlName("transferFactoryCid")], transfer_arg: Annotated[TransferFactory_Transfer, DamlName("transferArg")]) -> TransferInstructionResult:
        pass

    @choice(controller=validator_party, consuming="nonconsuming")
    def WalletAppInstall_TransferInstruction_Accept(self, transfer_instruction_cid: Annotated[ContractId[TransferInstruction], DamlName("transferInstructionCid")], accept_arg: Annotated[TransferInstruction_Accept, DamlName("acceptArg")]) -> TransferInstructionResult:
        pass

    @choice(controller=validator_party, consuming="nonconsuming")
    def WalletAppInstall_TransferInstruction_Reject(self, transfer_instruction_cid: Annotated[ContractId[TransferInstruction], DamlName("transferInstructionCid")], reject_arg: Annotated[TransferInstruction_Reject, DamlName("rejectArg")]) -> TransferInstructionResult:
        pass

    @choice(controller=validator_party, consuming="nonconsuming")
    def WalletAppInstall_TransferInstruction_Withdraw(self, transfer_instruction_cid: Annotated[ContractId[TransferInstruction], DamlName("transferInstructionCid")], withdraw_arg: Annotated[TransferInstruction_Withdraw, DamlName("withdrawArg")]) -> TransferInstructionResult:
        pass

    @choice(controller=validator_party, consuming="nonconsuming")
    def WalletAppInstall_AllocationFactory_Allocate(self, allocation_factory: Annotated[ContractId[AllocationFactory], DamlName("allocationFactory")], allocate_arg: Annotated[AllocationFactory_Allocate, DamlName("allocateArg")]) -> AllocationInstructionResult:
        pass

    @choice(controller=validator_party, consuming="nonconsuming")
    def WalletAppInstall_Allocation_Withdraw(self, allocation_cid: Annotated[ContractId[Allocation], DamlName("allocationCid")], withdraw_arg: Annotated[Allocation_Withdraw, DamlName("withdrawArg")]) -> Allocation_WithdrawResult:
        pass

    @choice(controller=validator_party, consuming="nonconsuming")
    def WalletAppInstall_TransferFactoryV2_Transfer(self, transfer_factory_cid: Annotated[ContractId[TransferInstructionV2.TransferFactory], DamlName("transferFactoryCid")], transfer_arg: Annotated[TransferInstructionV2.TransferFactory_Transfer, DamlName("transferArg")]) -> TransferInstructionV2.TransferInstructionResult:
        pass

    @choice(controller=validator_party, consuming="nonconsuming")
    def WalletAppInstall_TransferInstructionV2_Accept(self, transfer_instruction_cid: Annotated[ContractId[TransferInstructionV2.TransferInstruction], DamlName("transferInstructionCid")], accept_arg: Annotated[TransferInstructionV2.TransferInstruction_Accept, DamlName("acceptArg")]) -> TransferInstructionV2.TransferInstructionResult:
        pass

    @choice(controller=validator_party, consuming="nonconsuming")
    def WalletAppInstall_TransferInstructionV2_Reject(self, transfer_instruction_cid: Annotated[ContractId[TransferInstructionV2.TransferInstruction], DamlName("transferInstructionCid")], reject_arg: Annotated[TransferInstructionV2.TransferInstruction_Reject, DamlName("rejectArg")]) -> TransferInstructionV2.TransferInstructionResult:
        pass

    @choice(controller=validator_party, consuming="nonconsuming")
    def WalletAppInstall_TransferInstructionV2_Withdraw(self, transfer_instruction_cid: Annotated[ContractId[TransferInstructionV2.TransferInstruction], DamlName("transferInstructionCid")], withdraw_arg: Annotated[TransferInstructionV2.TransferInstruction_Withdraw, DamlName("withdrawArg")]) -> TransferInstructionV2.TransferInstructionResult:
        pass

    @choice(controller=validator_party, consuming="nonconsuming")
    def WalletAppInstall_AllocationFactoryV2_Allocate(self, allocation_factory: Annotated[ContractId[AllocationInstructionV2.AllocationFactory], DamlName("allocationFactory")], allocate_arg: Annotated[AllocationInstructionV2.AllocationFactory_Allocate, DamlName("allocateArg")], allocation_req_cid: Annotated[Optional[ContractId[AllocationRequest]], DamlName("allocationReqCid")]) -> AllocationInstructionV2.AllocationInstructionResult:
        pass

    @choice(controller=validator_party, consuming="nonconsuming")
    def WalletAppInstall_AllocationV2_Withdraw(self, allocation_cid: Annotated[ContractId[AllocationV2.Allocation], DamlName("allocationCid")], withdraw_arg: Annotated[AllocationV2.Allocation_Withdraw, DamlName("withdrawArg")]) -> AllocationV2.AllocationResult:
        pass

    @choice(controller=validator_party, consuming="nonconsuming")
    def WalletAppInstall_AllocationInstructionV2_Accept(self, allocation_instruction_cid: Annotated[ContractId[AllocationInstructionV2.AllocationInstruction], DamlName("allocationInstructionCid")], accept_arg: Annotated[AllocationInstructionV2.AllocationInstruction_Accept, DamlName("acceptArg")]) -> AllocationInstructionV2.AllocationInstructionResult:
        pass

    @choice(controller=validator_party, consuming="nonconsuming")
    def WalletAppInstall_AllocationInstructionV2_Withdraw(self, allocation_instruction_cid: Annotated[ContractId[AllocationInstructionV2.AllocationInstruction], DamlName("allocationInstructionCid")], withdraw_arg: Annotated[AllocationInstructionV2.AllocationInstruction_Withdraw, DamlName("withdrawArg")]) -> AllocationInstructionV2.AllocationInstructionResult:
        pass


@DamlCaseAccessor("COO_AcceptedAppPayment")
def coo_accepted_app_payment(value: AmuletOperationOutcome) -> Optional[ContractId[AcceptedAppPayment]]:
    pass


@DamlCaseAccessor("COO_CompleteAcceptedTransfer")
def coo_complete_accepted_transfer(value: AmuletOperationOutcome) -> Optional[tuple[TransferResult, TransferOfferTrackingInfo]]:
    pass


@DamlCaseAccessor("COO_SubscriptionInitialPayment")
def coo_subscription_initial_payment(value: AmuletOperationOutcome) -> Optional[ContractId[SubscriptionInitialPayment]]:
    pass


@DamlCaseAccessor("COO_SubscriptionPayment")
def coo_subscription_payment(value: AmuletOperationOutcome) -> Optional[ContractId[SubscriptionPayment]]:
    pass


@DamlCaseAccessor("COO_MergeTransferInputs")
def coo_merge_transfer_inputs(value: AmuletOperationOutcome) -> Optional[Optional[ContractId[Amulet]]]:
    pass


@DamlCaseAccessor("COO_BuyMemberTraffic")
def coo_buy_member_traffic(value: AmuletOperationOutcome) -> Optional[ContractId[MemberTraffic]]:
    pass


@DamlCaseAccessor("COO_CompleteBuyTrafficRequest")
def coo_complete_buy_traffic_request(value: AmuletOperationOutcome) -> Optional[tuple[ContractId[MemberTraffic], BuyTrafficRequestTrackingInfo]]:
    pass


@DamlCaseAccessor("COO_Tap")
def coo_tap(value: AmuletOperationOutcome) -> Optional[ContractId[Amulet]]:
    pass


@DamlCaseAccessor("COO_Error")
def coo_error(value: AmuletOperationOutcome) -> Optional[InvalidTransferReason]:
    pass


@DamlCaseAccessor("ExtAmuletOperationOutcome")
def ext_amulet_operation_outcome(value: AmuletOperationOutcome) -> Optional[None]:
    pass


@DamlCaseAccessor("COO_CreateExternalPartySetupProposal")
def coo_create_external_party_setup_proposal(value: AmuletOperationOutcome) -> Optional[ContractId[ExternalPartySetupProposal]]:
    pass


@DamlCaseAccessor("COO_AcceptTransferPreapprovalProposal")
def coo_accept_transfer_preapproval_proposal(value: AmuletOperationOutcome) -> Optional[ContractId[TransferPreapproval]]:
    pass


@DamlCaseAccessor("COO_RenewTransferPreapproval")
def coo_renew_transfer_preapproval(value: AmuletOperationOutcome) -> Optional[ContractId[TransferPreapproval]]:
    pass


@DamlCaseAccessor("COO_TransferPreapprovalSend")
def coo_transfer_preapproval_send(value: AmuletOperationOutcome) -> Optional[Optional[ContractId[Amulet]]]:
    pass


@DamlCaseAccessor("CO_AppPayment")
def co_app_payment(value: AmuletOperation) -> Optional[ContractId[AppPaymentRequest]]:
    pass


@DamlCaseAccessor("CO_CompleteAcceptedTransfer")
def co_complete_accepted_transfer(value: AmuletOperation) -> Optional[ContractId[AcceptedTransferOffer]]:
    pass


@DamlCaseAccessor("CO_SubscriptionAcceptAndMakeInitialPayment")
def co_subscription_accept_and_make_initial_payment(value: AmuletOperation) -> Optional[ContractId[SubscriptionRequest]]:
    pass


@DamlCaseAccessor("CO_SubscriptionMakePayment")
def co_subscription_make_payment(value: AmuletOperation) -> Optional[ContractId[SubscriptionIdleState]]:
    pass


@DamlCaseAccessor("CO_MergeTransferInputs", arity=0)
def co_merge_transfer_inputs(value: AmuletOperation) -> Optional[None]:
    pass


@DamlCaseAccessor("CO_BuyMemberTraffic", arity=6)
def co_buy_member_traffic(value: AmuletOperation) -> Optional[tuple[int, str, str, int, timedelta, Optional[ContractId[ValidatorTopUpState]]]]:
    pass


@DamlCaseAccessor("CO_CompleteBuyTrafficRequest")
def co_complete_buy_traffic_request(value: AmuletOperation) -> Optional[ContractId[BuyTrafficRequest]]:
    pass


@DamlCaseAccessor("CO_Tap")
def co_tap(value: AmuletOperation) -> Optional[Decimal]:
    pass


@DamlCaseAccessor("ExtAmuletOperation")
def ext_amulet_operation(value: AmuletOperation) -> Optional[None]:
    pass


@DamlCaseAccessor("CO_CreateExternalPartySetupProposal", arity=2)
def co_create_external_party_setup_proposal(value: AmuletOperation) -> Optional[tuple[Party, datetime]]:
    pass


@DamlCaseAccessor("CO_AcceptTransferPreapprovalProposal", arity=2)
def co_accept_transfer_preapproval_proposal(value: AmuletOperation) -> Optional[tuple[ContractId[TransferPreapprovalProposal], datetime]]:
    pass


@DamlCaseAccessor("CO_RenewTransferPreapproval", arity=2)
def co_renew_transfer_preapproval(value: AmuletOperation) -> Optional[tuple[ContractId[TransferPreapproval], datetime]]:
    pass


@DamlCaseAccessor("CO_TransferPreapprovalSend", arity=4)
def co_transfer_preapproval_send(value: AmuletOperation) -> Optional[tuple[ContractId[TransferPreapproval], Optional[ContractId[FeaturedAppRight]], Decimal, Optional[str]]]:
    pass


@ledger_effect
@DamlName("executeAmuletOperationRec")
def execute_amulet_operation_rec(execution_context: ExecutionContext, inputs: list[TransferInput], prev_results: list[AmuletOperationOutcome], list_value: list[AmuletOperation]) -> list[AmuletOperationOutcome]:
    pass


@DamlName("mkMergeAmuletAndRewardsTransfer")
def mk_merge_amulet_and_rewards_transfer(end_user_p: Party, inputs: list[TransferInput]) -> Transfer:
    pass


@ledger_effect
@DamlName("checkTransferInstructionV2")
def check_transfer_instruction_v2(party: Party, transfer_instruction_cid: ContractId[TransferInstructionV2.TransferInstruction], actors: list[Party], end_user_party: Party) -> None:
    pass


@ledger_effect
@DamlName("checkAllocationSpecificationV2")
def check_allocation_specification_v2(allocation: AllocationV2.AllocationSpecification, end_user_party: Party) -> None:
    pass


@DamlName("unpackCid")
def unpack_cid(any_value: AnyValue) -> ContractId[AnyContract]:
    pass
