from datetime import datetime
from typing import Annotated

from forge.models import choice, ContractId, GenMap, ledger_effect, Optional, Party, variant, variant_record
from forge.builtins import DamlCaseAccessor, DamlName
from Splice.Api.Token.AllocationV1 import Allocation, AllocationSpecification
from Splice.Api.Token.HoldingV1 import Holding
from Splice.Api.Token.MetadataV1 import ExtraArgs, Metadata


@variant
class AllocationInstructionResult_Output:
    @variant_record
    def AllocationInstructionResult_Pending(allocation_instruction_cid: Annotated[ContractId[AllocationInstruction], DamlName("allocationInstructionCid")]): pass
    @variant_record
    def AllocationInstructionResult_Completed(allocation_cid: Annotated[ContractId[Allocation], DamlName("allocationCid")]): pass
    def AllocationInstructionResult_Failed(): pass


struct AllocationInstructionResult:
    output: AllocationInstructionResult_Output
    sender_change_cids: Annotated[list[ContractId[Holding]], DamlName("senderChangeCids")]
    meta: Metadata


struct AllocationFactoryView:
    admin: Party
    meta: Metadata


struct AllocationInstructionView:
    original_instruction_cid: Annotated[Optional[ContractId[AllocationInstruction]], DamlName("originalInstructionCid")]
    allocation: AllocationSpecification
    pending_actions: Annotated[GenMap[Party, str], DamlName("pendingActions")]
    requested_at: Annotated[datetime, DamlName("requestedAt")]
    input_holding_cids: Annotated[list[ContractId[Holding]], DamlName("inputHoldingCids")]
    meta: Metadata


interface AllocationFactory(view=AllocationFactoryView):
    @choice(controller=allocation.transfer_leg.sender, consuming="nonconsuming")
    def AllocationFactory_Allocate(self, expected_admin: Annotated[Party, DamlName("expectedAdmin")], allocation: AllocationSpecification, requested_at: Annotated[datetime, DamlName("requestedAt")], input_holding_cids: Annotated[list[ContractId[Holding]], DamlName("inputHoldingCids")], extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]) -> AllocationInstructionResult:
        pass

    @choice(controller=actor, consuming="nonconsuming")
    def AllocationFactory_PublicFetch(self, expected_admin: Annotated[Party, DamlName("expectedAdmin")], actor: Party) -> AllocationFactoryView:
        pass


interface AllocationInstruction(view=AllocationInstructionView):
    @choice(controller=view.allocation.transfer_leg.sender, consuming=True)
    def AllocationInstruction_Withdraw(self, extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]) -> AllocationInstructionResult:
        pass

    @choice(controller=extra_actors + [view.allocation.transfer_leg.instrument_id.admin], consuming=True)
    def AllocationInstruction_Update(self, extra_actors: Annotated[list[Party], DamlName("extraActors")], extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]) -> AllocationInstructionResult:
        pass


@DamlCaseAccessor("AllocationInstructionResult_Pending")
def allocation_instruction_result_pending(value: AllocationInstructionResult_Output) -> Optional[ContractId[AllocationInstruction]]:
    pass


@DamlCaseAccessor("AllocationInstructionResult_Completed")
def allocation_instruction_result_completed(value: AllocationInstructionResult_Output) -> Optional[ContractId[Allocation]]:
    pass


@DamlCaseAccessor("AllocationInstructionResult_Failed", arity=0)
def allocation_instruction_result_failed(value: AllocationInstructionResult_Output) -> Optional[None]:
    pass


@ledger_effect
@DamlName("allocationInstruction_withdrawImpl")
def allocation_instruction_withdraw_impl(i: AllocationInstruction, contract_id: ContractId[AllocationInstruction], allocation_instruction_withdraw: AllocationInstruction_Withdraw) -> AllocationInstructionResult:
    pass


@ledger_effect
@DamlName("allocationInstruction_updateImpl")
def allocation_instruction_update_impl(i: AllocationInstruction, contract_id: ContractId[AllocationInstruction], allocation_instruction_update: AllocationInstruction_Update) -> AllocationInstructionResult:
    pass


@ledger_effect
@DamlName("allocationFactory_allocateImpl")
def allocation_factory_allocate_impl(i: AllocationFactory, contract_id: ContractId[AllocationFactory], allocation_factory_allocate: AllocationFactory_Allocate) -> AllocationInstructionResult:
    pass


@ledger_effect
@DamlName("allocationFactory_publicFetchImpl")
def allocation_factory_public_fetch_impl(i: AllocationFactory, contract_id: ContractId[AllocationFactory], allocation_factory_public_fetch: AllocationFactory_PublicFetch) -> AllocationFactoryView:
    pass
