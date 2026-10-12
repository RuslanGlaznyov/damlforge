from datetime import datetime
from typing import Annotated

from forge.models import choice, ContractId, GenMap, ledger_effect, Optional, Party, template, TextMap, variant, variant_record
from forge.builtins import DamlCaseAccessor, DamlName, no_derive
from Splice.Api.Token.AllocationInstructionV2 import AllocationFactory, AllocationFactory_Allocate, AllocationInstructionResult
from Splice.Api.Token.AllocationV2 import Allocation, AllocationResult, AllocationSpecification, SettlementFactory, SettlementFactory_SettleBatchResult, SettlementInfo, TransferLeg, TransferLegSide
from Splice.Api.Token.HoldingV2 import Account
from Splice.Api.Token.MetadataV1 import ExtraArgs
import Splice.Api.Token.AllocationV1 as AllocationV1


@variant
class SettlementBatch:
    @variant_record
    def SettlementBatchV1(allocations_with_context: Annotated[TextMap[AllocationWithContextV1], DamlName("allocationsWithContext")]): pass
    @variant_record
    def SettlementBatchV2(allocation_cids: Annotated[list[ContractId[Allocation]], DamlName("allocationCids")], missing_allocations: Annotated[list[MissingAllocation], DamlName("missingAllocations")], factory_cid: Annotated[ContractId[SettlementFactory], DamlName("factoryCid")], extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]): pass


struct AllocationWithContextV1:
    allocation_cid: Annotated[ContractId[AllocationV1.Allocation], DamlName("allocationCid")]
    extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]
    sender_agreement_cid: Annotated[ContractId[TradeSettlementAgreement], DamlName("senderAgreementCid")]
    receiver_agreement_cid: Annotated[ContractId[TradeSettlementAgreement], DamlName("receiverAgreementCid")]


struct MissingAllocation:
    authorizer_agreement_cid: Annotated[Optional[ContractId[TradeSettlementAgreement]], DamlName("authorizerAgreementCid")]
    factory_cid: Annotated[ContractId[AllocationFactory], DamlName("factoryCid")]
    choice_arg: Annotated[AllocationFactory_Allocate, DamlName("choiceArg")]


struct TradeLeg:
    admin: Party
    leg: TransferLeg


@no_derive
struct OTCTrade_SettleResult:
    results_by_admin_v1: Annotated[GenMap[Party, TextMap[AllocationV1.Allocation_ExecuteTransferResult]], DamlName("resultsByAdminV1")]
    results_by_admin_v2: Annotated[GenMap[Party, SettlementFactory_SettleBatchResult], DamlName("resultsByAdminV2")]


@no_derive
struct OTCTrade_CancelResult:
    results_v1: Annotated[TextMap[AllocationV1.Allocation_CancelResult], DamlName("resultsV1")]
    results_v2: Annotated[list[tuple[Account, AllocationResult]], DamlName("resultsV2")]


@template
class OTCTradeAllocationRequest:
    settlement: SettlementInfo
    requested_at: Annotated[datetime, DamlName("requestedAt")]
    settle_at: Annotated[datetime, DamlName("settleAt")]
    allocations: list[AllocationSpecification]

    signatory: list[Party] = settlement.executors


@template
class OTCTrade:
    venue: Party
    trade_legs: Annotated[list[TradeLeg], DamlName("tradeLegs")]
    created_at: Annotated[datetime, DamlName("createdAt")]
    settle_at: Annotated[datetime, DamlName("settleAt")]
    settlement_deadline: Annotated[Optional[datetime], DamlName("settlementDeadline")]

    signatory: list[Party] = [venue]

    @choice(controller=venue, consuming=True)
    def OTCTrade_Settle(self, batches_by_admin: Annotated[GenMap[Party, SettlementBatch], DamlName("batchesByAdmin")], allocation_requests: Annotated[list[ContractId[OTCTradeAllocationRequest]], DamlName("allocationRequests")]) -> OTCTrade_SettleResult:
        pass

    @choice(controller=venue, consuming="nonconsuming")
    def OTCTrade_RequestAllocations(self) -> list[ContractId[OTCTradeAllocationRequest]]:
        pass

    @choice(controller=venue, consuming=True)
    def OTCTrade_Cancel(self, allocations_with_context_v1: Annotated[list[AllocationWithContextV1], DamlName("allocationsWithContextV1")], allocations_with_context_v2: Annotated[list[tuple[ContractId[Allocation], ExtraArgs]], DamlName("allocationsWithContextV2")], allocation_request_cids: Annotated[list[ContractId[OTCTradeAllocationRequest]], DamlName("allocationRequestCids")]) -> OTCTrade_CancelResult:
        pass


@template
class TradeSettlementAgreement:
    venue: Party
    trader: Party

    signatory: list[Party] = [venue, trader]

    @choice(controller=venue, consuming="nonconsuming")
    def TradeSettlementAgreement_ExecuteTransferAsSender(self, receiver_agreement_cid: Annotated[ContractId[TradeSettlementAgreement], DamlName("receiverAgreementCid")], allocation_cid: Annotated[ContractId[AllocationV1.Allocation], DamlName("allocationCid")], extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]) -> AllocationV1.Allocation_ExecuteTransferResult:
        pass

    @choice(controller=[venue, sender], consuming="nonconsuming")
    def TradeSettlementAgreement_ExecuteTransferAsReceiver(self, sender: Party, allocation_cid: Annotated[ContractId[AllocationV1.Allocation], DamlName("allocationCid")], extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]) -> AllocationV1.Allocation_ExecuteTransferResult:
        pass

    @choice(controller=venue, consuming="nonconsuming")
    def TradeSettlementAgreement_CancelAsSender(self, receiver_agreement_cid: Annotated[ContractId[TradeSettlementAgreement], DamlName("receiverAgreementCid")], allocation_cid: Annotated[ContractId[AllocationV1.Allocation], DamlName("allocationCid")], extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]) -> AllocationV1.Allocation_CancelResult:
        pass

    @choice(controller=[venue, sender], consuming="nonconsuming")
    def TradeSettlementAgreement_CancelAsReceiver(self, sender: Party, allocation_cid: Annotated[ContractId[AllocationV1.Allocation], DamlName("allocationCid")], extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]) -> AllocationV1.Allocation_CancelResult:
        pass

    @choice(controller=venue, consuming="nonconsuming")
    def TradeSettlementAgreement_CreateReceiptAllocation(self, factory_cid: Annotated[ContractId[AllocationFactory], DamlName("factoryCid")], choice_arg: Annotated[AllocationFactory_Allocate, DamlName("choiceArg")]) -> ContractId[Allocation]:
        pass


@DamlCaseAccessor("SettlementBatchV1")
def settlement_batch_v1(value: SettlementBatch) -> Optional[TextMap[AllocationWithContextV1]]:
    pass


@DamlCaseAccessor("SettlementBatchV2", arity=4)
def settlement_batch_v2(value: SettlementBatch) -> Optional[tuple[list[ContractId[Allocation]], list[MissingAllocation], ContractId[SettlementFactory], ExtraArgs]]:
    pass


@DamlName("affectedAccountParties")
def affected_account_parties(req: OTCTradeAllocationRequest) -> list[Party]:
    pass


@DamlName("splitTradeLegsByAuthorizer")
def split_trade_legs_by_authorizer(legs: list[TradeLeg]) -> GenMap[Account, list[tuple[Party, TransferLegSide]]]:
    pass


@DamlName("mkOtcTradeSettlementInfoV2")
def mk_otc_trade_settlement_info_v2(otc_trade_cid: ContractId[OTCTrade], otc_trade: OTCTrade) -> SettlementInfo:
    pass


@DamlName("mkOtcTradeSettlementInfoV1")
def mk_otc_trade_settlement_info_v1(otc_trade_cid: ContractId[OTCTrade], otc_trade: OTCTrade) -> AllocationV1.SettlementInfo:
    pass


@DamlName("expectedTradeAllocationsV1")
def expected_trade_allocations_v1(settlement_info: AllocationV1.SettlementInfo, transfer_legs: list[TradeLeg]) -> TextMap[AllocationV1.AllocationSpecification]:
    pass


@ledger_effect
@DamlName("extractAllocationCidFromResult")
def extract_allocation_cid_from_result(result: AllocationInstructionResult) -> ContractId[Allocation]:
    pass


@ledger_effect
@DamlName("validateAllocationAsSender")
def validate_allocation_as_sender(this: TradeSettlementAgreement, receiver_agreement_cid: ContractId[TradeSettlementAgreement], allocation_cid: ContractId[AllocationV1.Allocation]) -> None:
    pass


@ledger_effect
@DamlName("validateAllocationAsReceiver")
def validate_allocation_as_receiver(this: TradeSettlementAgreement, sender: Party, allocation_cid: ContractId[AllocationV1.Allocation]) -> None:
    pass
