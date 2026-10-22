from datetime import datetime
from typing import TypeVar

from forge.models import ContractId, Decimal, GenMap, Optional, Party, TextMap
from forge.builtins import DamlName
from DA.Internal.Fail.Types import FailureStatus
from Splice.Api.Token.AllocationRequestV2 import AllocationRequest, AllocationRequestView, AllocationRequest_Accept, AllocationRequest_AcceptResult, AllocationRequest_Reject, AllocationRequest_RejectResult, AllocationRequest_Withdraw, AllocationRequest_WithdrawResult
from Splice.Api.Token.HoldingV2 import Account
from Splice.Api.Token.MetadataV1 import ChoiceExecutionMetadata, Metadata
import Splice.Api.Token.AllocationInstructionV1 as AllocationInstructionV1
import Splice.Api.Token.AllocationInstructionV2 as AllocationInstructionV2
import Splice.Api.Token.AllocationRequestV1 as AllocationRequestV1
import Splice.Api.Token.AllocationV1 as AllocationV1
import Splice.Api.Token.AllocationV2 as AllocationV2

T = TypeVar("T")


@DamlName("senderSide")
def sender_side(allocation_v2: AllocationV2.TransferLeg) -> AllocationV2.TransferLegSide:
    pass


@DamlName("receiverSide")
def receiver_side(allocation_v2: AllocationV2.TransferLeg) -> AllocationV2.TransferLegSide:
    pass


@DamlName("transferLegFromSide")
def transfer_leg_from_side(authorizer: Account, allocation_v2: AllocationV2.TransferLegSide) -> AllocationV2.TransferLeg:
    pass


@DamlName("transferLegSidesWithAuthorizer")
def transfer_leg_sides_with_authorizer(leg: AllocationV2.TransferLeg) -> list[tuple[Account, AllocationV2.TransferLegSide]]:
    pass


@DamlName("nonIteratedAllocation")
def non_iterated_allocation(allocation_cid: ContractId[AllocationV2.Allocation]) -> AllocationV2.FinalizedAllocation:
    pass


@DamlName("netAllocationCreditAmounts")
def net_allocation_credit_amounts(authorizer: Account, transfer_leg_sides: list[AllocationV2.TransferLegSide]) -> TextMap[Decimal]:
    pass


@DamlName("isValidSettlementInfoV1")
def is_valid_settlement_info_v1(allocation_v1: AllocationV1.SettlementInfo) -> bool:
    pass


@DamlName("isValidAllocationSpecificationV1")
def is_valid_allocation_specification_v1(allocation_v1: AllocationV1.AllocationSpecification) -> bool:
    pass


@DamlName("isValidSettlementInfoV2")
def is_valid_settlement_info_v2(allocation_v2: AllocationV2.SettlementInfo) -> bool:
    pass


@DamlName("ensureIsReceiptAllocation", is_ledger_effect=True)
def ensure_is_receipt_allocation(executors: list[Party], receiver: Party, receipt_account: Account, choice_arg: AllocationInstructionV2.AllocationFactory_Allocate) -> None:
    pass


@DamlName("cannotWithdrawCommittedAllocationFailure")
def cannot_withdraw_committed_allocation_failure(optional: Optional[datetime]) -> FailureStatus:
    pass


@DamlName("ensureWithdrawIsAllowed", is_ledger_effect=True)
def ensure_withdraw_is_allowed(allocation: AllocationV2.AllocationSpecification) -> None:
    pass


@DamlName("allocationV2_withdrawDefaultImplUsingV1", is_ledger_effect=True)
def allocation_v2_withdraw_default_impl_using_v1(this: AllocationV1.Allocation, self_: ContractId[AllocationV2.Allocation], allocation_v2: AllocationV2.Allocation_Withdraw) -> AllocationV2.AllocationResult:
    pass


@DamlName("settlementFactoryV2_publicAsset_settleBatchExtraObserversDefaultImpl")
def settlement_factory_v2_public_asset_settle_batch_extra_observers_default_impl(admin: Party, arg: AllocationV2.SettlementFactory_SettleBatch) -> list[Party]:
    pass


@DamlName("settlementFactoryV2_privateAsset_settleBatchExtraObserversDefaultImpl")
def settlement_factory_v2_private_asset_settle_batch_extra_observers_default_impl(allocation_v2: AllocationV2.SettlementFactory_SettleBatch) -> list[Party]:
    pass


@DamlName("validateNextIterationArgs", is_ledger_effect=True)
def validate_next_iteration_args(name: str, iterated_settlement_allowed: bool, extra_transfer_leg_sides: list[AllocationV2.TransferLegSide], next_iteration_funding: Optional[TextMap[Decimal]]) -> None:
    pass


@DamlName("fetchAndValidateAllocations", is_ledger_effect=True)
def fetch_and_validate_allocations(admin: Party, allocation_v2: AllocationV2.SettlementFactory_SettleBatch) -> list[tuple[AllocationV2.FinalizedAllocation, AllocationV2.AllocationView]]:
    pass


@DamlName("extraExecutorsMetaKey")
def extra_executors_meta_key() -> str:
    pass


@DamlName("executorsFromSettlementInfoV1")
def executors_from_settlement_info_v1(info: AllocationV1.SettlementInfo) -> list[Party]:
    pass


@DamlName("downcast_v2_v1_TransferLeg")
def downcast_v2_v1_transfer_leg(admin: Party, allocation_v2: AllocationV2.TransferLeg) -> AllocationV1.TransferLeg:
    pass


@DamlName("upcast_v1_v2_TransferLeg")
def upcast_v1_v2_transfer_leg(transfer_leg_id: str, allocation_v1: AllocationV1.TransferLeg) -> AllocationV2.TransferLeg:
    pass


@DamlName("downcast_v2_v1_SettlementInfo")
def downcast_v2_v1_settlement_info(requested_at: datetime, allocate_before: Optional[datetime], settlement_deadline: Optional[datetime], allocation_v2: AllocationV2.SettlementInfo) -> AllocationV1.SettlementInfo:
    pass


@DamlName("upcast_v1_v2_AllocationView")
def upcast_v1_v2_allocation_view(original_allocation_cid: Optional[ContractId[AllocationV2.Allocation]], expires_at: Optional[datetime], available_actions: GenMap[AllocationV2.AllocationAction, list[list[Party]]], allocation_v1: AllocationV1.AllocationView) -> AllocationV2.AllocationView:
    pass


@DamlName("allocationV1_availableActionsDefault")
def allocation_v1_available_actions_default(alloc_view: AllocationV1.AllocationView) -> GenMap[AllocationV2.AllocationAction, list[list[Party]]]:
    pass


@DamlName("allocationV2_availableActionsDefault")
def allocation_v2_available_actions_default(executors: list[Party], allocation: AllocationV2.AllocationSpecification) -> GenMap[AllocationV2.AllocationAction, list[list[Party]]]:
    pass


@DamlName("upcast_v1_v2_AllocationInstructionView")
def upcast_v1_v2_allocation_instruction_view(expires_at: Optional[datetime], available_actions: GenMap[AllocationInstructionV2.AllocationInstructionAction, list[list[Party]]], allocation_instruction_v1: AllocationInstructionV1.AllocationInstructionView) -> AllocationInstructionV2.AllocationInstructionView:
    pass


@DamlName("viewAsAllocationInstructionV1")
def view_as_allocation_instruction_v1(tuple_value: tuple[Optional[datetime], T]) -> AllocationInstructionV1.AllocationInstructionView:
    pass


@DamlName("canViewAsAllocationInstructionV1")
def can_view_as_allocation_instruction_v1(tuple_value: tuple[Optional[datetime], T]) -> bool:
    pass


@DamlName("tryDowncast_v2_v1_AllocationInstructionView")
def try_downcast_v2_v1_allocation_instruction_view(allocate_before: Optional[datetime], v2_view: AllocationInstructionV2.AllocationInstructionView) -> Optional[AllocationInstructionV1.AllocationInstructionView]:
    pass


@DamlName("downcast_v2_v1_AllocationInstructionPendingActions")
def downcast_v2_v1_allocation_instruction_pending_actions(gen_map: GenMap[AllocationInstructionV2.AllocationInstructionAction, list[list[Party]]]) -> GenMap[Party, str]:
    pass


@DamlName("allocationInstructionV1_updateDefaultImplUsingV2", is_ledger_effect=True)
def allocation_instruction_v1_update_default_impl_using_v2(contract_id: ContractId[AllocationInstructionV1.AllocationInstruction], allocation_instruction_v1: AllocationInstructionV1.AllocationInstruction_Update) -> AllocationInstructionV1.AllocationInstructionResult:
    pass


@DamlName("allocationSettlementTxHistoryV1ToMeta")
def allocation_settlement_tx_history_v1_to_meta(alloc: AllocationV2.AllocationSpecification, meta: Metadata) -> Metadata:
    pass


@DamlName("extractTransferLegForV1")
def extract_transfer_leg_for_v1(v2_allocation: AllocationV2.AllocationSpecification) -> Optional[AllocationV2.TransferLeg]:
    pass


@DamlName("viewAsAllocationV1")
def view_as_allocation_v1(tuple_value: tuple[Optional[datetime], T]) -> AllocationV1.AllocationView:
    pass


@DamlName("canViewAsAllocationV1")
def can_view_as_allocation_v1(tuple_value: tuple[Optional[datetime], T]) -> bool:
    pass


@DamlName("tryDowncast_v2_v1_AllocationView")
def try_downcast_v2_v1_allocation_view(allocate_before: Optional[datetime], v2_view: AllocationV2.AllocationView) -> Optional[AllocationV1.AllocationView]:
    pass


@DamlName("allocationV1_executeTransferDefaultImplUsingV2", is_ledger_effect=True)
def allocation_v1_execute_transfer_default_impl_using_v2(allocation_factory_cid: ContractId[AllocationInstructionV2.AllocationFactory], settlement_factory_cid: ContractId[AllocationV2.SettlementFactory], v2_sender_allocation: AllocationV2.Allocation, v1_sender_alloc_cid: ContractId[AllocationV1.Allocation], arg: AllocationV1.Allocation_ExecuteTransfer) -> AllocationV1.Allocation_ExecuteTransferResult:
    pass


@DamlName("allocationRequestV2_rejectDefaultImplUsingV1", is_ledger_effect=True)
def allocation_request_v2_reject_default_impl_using_v1(allowed_actors: list[list[Party]], self_: ContractId[AllocationRequest], arg: AllocationRequest_Reject) -> AllocationRequest_RejectResult:
    pass


@DamlName("allocationRequestV2_withdrawDefaultImplUsingV1", is_ledger_effect=True)
def allocation_request_v2_withdraw_default_impl_using_v1(this: AllocationRequest, self_: ContractId[AllocationRequest], arg: AllocationRequest_Withdraw) -> AllocationRequest_WithdrawResult:
    pass


@DamlName("allocationRequestV1_rejectDefaultImpl", is_ledger_effect=True)
def allocation_request_v1_reject_default_impl(allowed_actors: list[Party], contract_id: ContractId[AllocationRequestV1.AllocationRequest], arg: AllocationRequestV1.AllocationRequest_Reject) -> ChoiceExecutionMetadata:
    pass


@DamlName("allocationRequestV1_withdrawDefaultImpl", is_ledger_effect=True)
def allocation_request_v1_withdraw_default_impl(allocation_request_v1: AllocationRequestV1.AllocationRequest, contract_id: ContractId[AllocationRequestV1.AllocationRequest], allocation_request_v1_2: AllocationRequestV1.AllocationRequest_Withdraw) -> ChoiceExecutionMetadata:
    pass


@DamlName("allocationRequestV2_acceptDefaultImpl", is_ledger_effect=True)
def allocation_request_v2_accept_default_impl(allowed_actors: list[list[Party]], self_: ContractId[AllocationRequest], arg: AllocationRequest_Accept) -> AllocationRequest_AcceptResult:
    pass


@DamlName("allocationRequestV2_rejectDefaultImplV2Only", is_ledger_effect=True)
def allocation_request_v2_reject_default_impl_v2_only(allowed_actors: list[list[Party]], self_: ContractId[AllocationRequest], arg: AllocationRequest_Reject) -> AllocationRequest_RejectResult:
    pass


@DamlName("allocationRequestV2_withdrawDefaultImplV2Only", is_ledger_effect=True)
def allocation_request_v2_withdraw_default_impl_v2_only(this: AllocationRequest, self_: ContractId[AllocationRequest], arg: AllocationRequest_Withdraw) -> AllocationRequest_WithdrawResult:
    pass


@DamlName("downcast_v2_v1_AllocationRequestView")
def downcast_v2_v1_allocation_request_view(settlement_deadline: Optional[datetime], req: AllocationRequestView) -> AllocationRequestV1.AllocationRequestView:
    pass


@DamlName("allocationFactoryV2_publicAsset_allocateExtraObserversDefaultImpl")
def allocation_factory_v2_public_asset_allocate_extra_observers_default_impl(arg: AllocationInstructionV2.AllocationFactory_Allocate) -> list[Party]:
    pass


@DamlName("allocationFactoryV2_privateAsset_allocateExtraObserversDefaultImpl")
def allocation_factory_v2_private_asset_allocate_extra_observers_default_impl(arg: AllocationInstructionV2.AllocationFactory_Allocate) -> list[Party]:
    pass
