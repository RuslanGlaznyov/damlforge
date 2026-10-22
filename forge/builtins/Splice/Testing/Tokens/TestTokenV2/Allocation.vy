from datetime import datetime
from typing import Annotated

from forge.models import ContractId, Decimal, GenMap, Optional, Party, template, TextMap, variant
from forge.builtins import DamlName, no_derive
from Splice.Api.Token.AllocationInstructionV2 import AllocationInstruction, AllocationInstructionAction, AllocationInstructionResult, AllocationInstruction_Accept, AllocationInstruction_Withdraw
from Splice.Api.Token.AllocationV2 import Allocation, AllocationAction, AllocationResult, AllocationSpecification, Allocation_Cancel, Allocation_Settle, Allocation_Withdraw, SettlementInfo
from Splice.Api.Token.HoldingV2 import Account, Holding
from Splice.Api.Token.MetadataV1 import ExtraArgs
from Splice.Api.Token.TransferEventsV2 import EventLog
from Splice.Testing.Tokens.TestTokenV2.AccountConfig import AccountConfig
from Splice.Testing.Tokens.TestTokenV2.Util import CallSource


@no_derive
@variant
class AllocationKind:
    def CreateV1Allocation(): pass
    def CreateV2Allocation(): pass


@template
class TokenAllocationInstructionV2:
    original_instruction_cid: Annotated[Optional[ContractId[AllocationInstruction]], DamlName("originalInstructionCid")]
    action_authorizers: Annotated[GenMap[AllocationInstructionAction, list[Party]], DamlName("actionAuthorizers")]
    available_actions: Annotated[GenMap[AllocationInstructionAction, list[list[Party]]], DamlName("availableActions")]
    input_holding_cids: Annotated[TextMap[list[ContractId[Holding]]], DamlName("inputHoldingCids")]
    settlement: SettlementInfo
    allocation: AllocationSpecification
    admin: Party
    requested_at: Annotated[datetime, DamlName("requestedAt")]
    allocate_before: Annotated[Optional[datetime], DamlName("allocateBefore")]

    signatory: list[Party] = [admin]


@template
class TokenAllocationV2:
    original_allocation_cid: Annotated[Optional[ContractId[Allocation]], DamlName("originalAllocationCid")]
    action_authorizers: Annotated[GenMap[AllocationAction, list[Party]], DamlName("actionAuthorizers")]
    available_actions: Annotated[GenMap[AllocationAction, list[list[Party]]], DamlName("availableActions")]
    locked_tokens: Annotated[TextMap[list[ContractId[Holding]]], DamlName("lockedTokens")]
    settlement: SettlementInfo
    allocation: AllocationSpecification
    requested_at: Annotated[datetime, DamlName("requestedAt")]
    allocate_before: Annotated[Optional[datetime], DamlName("allocateBefore")]
    num_iterations: Annotated[int, DamlName("numIterations")]

    signatory: list[Party] = [allocation.admin]
    observer: list[Party] = settlement.executors


@template
class TokenAllocationInstructionV1:
    instr_v2: Annotated[TokenAllocationInstructionV2, DamlName("instrV2")]

    signatory: list[Party] = [instr_v2.admin]


@template
class TokenAllocationV1:
    allocation_v2: Annotated[TokenAllocationV2, DamlName("allocationV2")]

    signatory: list[Party] = [allocation_v2.allocation.admin]
    observer: list[Party] = allocation_v2.settlement.executors


@DamlName("validAllocateBefore")
def valid_allocate_before(requested_at: datetime, opt_allocate_before: Optional[datetime], opt_settlement_deadline: Optional[datetime]) -> bool:
    pass


@DamlName("applyAllocationInstructionTransitions", is_ledger_effect=True)
def apply_allocation_instruction_transitions(call_source: CallSource, allocation_kind: AllocationKind, this: TokenAllocationInstructionV2, o_self: Optional[ContractId[AllocationInstruction]], actors: list[Party], action: AllocationInstructionAction, extra_args: ExtraArgs) -> AllocationInstructionResult:
    pass


@DamlName("applyAllocationTransitions", is_ledger_effect=True)
def apply_allocation_transitions(call_source: CallSource, allocation_kind: AllocationKind, this: TokenAllocationV2, o_self: Optional[ContractId[Allocation]], actors: list[Party], action: AllocationAction, o_settle: Optional[Allocation_Settle], extra_args: ExtraArgs) -> AllocationResult:
    pass


@DamlName("allocateTokenAllocation", is_ledger_effect=True)
def allocate_token_allocation(event_log_cid: ContractId[EventLog], account_map: GenMap[Account, tuple[AccountConfig, Optional[ContractId[AccountConfig]]]], this: TokenAllocationInstructionV2, allocation_kind: AllocationKind) -> AllocationInstructionResult:
    pass


@DamlName("settleTokenAllocationV2", is_ledger_effect=True)
def settle_token_allocation_v2(account_map: GenMap[Account, tuple[AccountConfig, Optional[ContractId[AccountConfig]]]], this: TokenAllocationV2, self_: ContractId[Allocation], arg: Allocation_Settle) -> AllocationResult:
    pass


@DamlName("lockAllocationFunds", is_ledger_effect=True)
def lock_allocation_funds(settlement: SettlementInfo, settlement_deadline: Optional[datetime], admin: Party, authorizer: Account, input_amounts: TextMap[Decimal], lock_amounts: TextMap[Decimal]) -> tuple[TextMap[list[ContractId[Holding]]], TextMap[list[ContractId[Holding]]]]:
    pass


@DamlName("unlockTokenAllocationV2", is_ledger_effect=True)
def unlock_token_allocation_v2(reason: str, token_allocation: TokenAllocationV2, extra_args: ExtraArgs) -> TextMap[list[ContractId[Holding]]]:
    pass


@DamlName("mkAvailableAllocationActions")
def mk_available_allocation_actions(settlement: SettlementInfo, allocation: AllocationSpecification, account_map: GenMap[Account, tuple[AccountConfig, Optional[ContractId[AccountConfig]]]]) -> GenMap[AllocationAction, list[list[Party]]]:
    pass


@DamlName("token_allocationInstruction_withdrawImplV2", is_ledger_effect=True)
def token_allocation_instruction_withdraw_impl_v2(call_source: CallSource, allocation_kind: AllocationKind, this: TokenAllocationInstructionV2, self_: ContractId[AllocationInstruction], arg: AllocationInstruction_Withdraw) -> AllocationInstructionResult:
    pass


@DamlName("token_allocationInstruction_acceptImplV2", is_ledger_effect=True)
def token_allocation_instruction_accept_impl_v2(call_source: CallSource, allocation_kind: AllocationKind, this: TokenAllocationInstructionV2, self_: ContractId[AllocationInstruction], arg: AllocationInstruction_Accept) -> AllocationInstructionResult:
    pass


@DamlName("token_allocation_withdrawImplV2", is_ledger_effect=True)
def token_allocation_withdraw_impl_v2(call_source: CallSource, allocation_kind: AllocationKind, this: TokenAllocationV2, self_: ContractId[Allocation], arg: Allocation_Withdraw) -> AllocationResult:
    pass


@DamlName("token_allocation_cancelImplV2", is_ledger_effect=True)
def token_allocation_cancel_impl_v2(call_source: CallSource, allocation_kind: AllocationKind, this: TokenAllocationV2, self_: ContractId[Allocation], arg: Allocation_Cancel) -> AllocationResult:
    pass


@DamlName("token_allocation_settleImplV2", is_ledger_effect=True)
def token_allocation_settle_impl_v2(call_source: CallSource, allocation_kind: AllocationKind, this: TokenAllocationV2, self_: ContractId[Allocation], arg: Allocation_Settle) -> AllocationResult:
    pass


@DamlName("createTokenAllocation", is_ledger_effect=True)
def create_token_allocation(allocation_kind: AllocationKind, allocation_v2: TokenAllocationV2) -> ContractId[Allocation]:
    pass


@DamlName("createTokenAllocationInstruction", is_ledger_effect=True)
def create_token_allocation_instruction(allocation_kind: AllocationKind, allocation_instruction_v2: TokenAllocationInstructionV2) -> ContractId[AllocationInstruction]:
    pass
