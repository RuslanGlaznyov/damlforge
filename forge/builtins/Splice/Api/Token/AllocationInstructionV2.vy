from datetime import datetime
from typing import Annotated

from forge.models import choice, ContractId, GenMap, ledger_effect, Optional, Party, TextMap, variant, variant_record
from forge.builtins import DamlCaseAccessor, DamlName
from Splice.Api.Token.AllocationV2 import Allocation, AllocationSpecification, SettlementInfo
from Splice.Api.Token.HoldingV2 import Holding
from Splice.Api.Token.MetadataV1 import ExtraArgs, Metadata


@variant
class AllocationInstructionResult_Output:
    @variant_record
    def AllocationInstructionResult_Pending(allocation_instruction_cid: Annotated[ContractId[AllocationInstruction], DamlName("allocationInstructionCid")]): pass
    @variant_record
    def AllocationInstructionResult_Completed(allocation_cid: Annotated[ContractId[Allocation], DamlName("allocationCid")]): pass
    def AllocationInstructionResult_Failed(): pass


@variant
class AllocationInstructionAction:
    def AIA_Withdraw(): pass
    def AIA_Accept(): pass
    @variant_record
    def AIA_Custom(id: str): pass


struct AllocationInstructionView:
    original_instruction_cid: Annotated[Optional[ContractId[AllocationInstruction]], DamlName("originalInstructionCid")]
    settlement: SettlementInfo
    allocation: AllocationSpecification
    requested_at: Annotated[datetime, DamlName("requestedAt")]
    input_holding_cids: Annotated[list[ContractId[Holding]], DamlName("inputHoldingCids")]
    expires_at: Annotated[Optional[datetime], DamlName("expiresAt")]
    available_actions: Annotated[GenMap[AllocationInstructionAction, list[list[Party]]], DamlName("availableActions")]
    meta: Metadata


struct AllocationFactoryView:
    admin: Party
    meta: Metadata


struct AllocationInstructionResult:
    output: AllocationInstructionResult_Output
    authorizer_change_cids: Annotated[TextMap[list[ContractId[Holding]]], DamlName("authorizerChangeCids")]
    meta: Metadata


interface AllocationFactory(view=AllocationFactoryView):
    @choice(controller=actors, consuming="nonconsuming")
    def AllocationFactory_Allocate(self, settlement: SettlementInfo, allocation: AllocationSpecification, requested_at: Annotated[datetime, DamlName("requestedAt")], input_holding_cids: Annotated[list[ContractId[Holding]], DamlName("inputHoldingCids")], extra_args: Annotated[ExtraArgs, DamlName("extraArgs")], actors: list[Party]) -> AllocationInstructionResult:
        pass

    @choice(controller=actors, consuming="nonconsuming")
    def AllocationFactory_PublicFetch(self, actors: list[Party]) -> AllocationFactoryView:
        pass


interface AllocationInstruction(view=AllocationInstructionView):
    @choice(controller=actors, consuming="nonconsuming")
    def AllocationInstruction_Withdraw(self, actors: list[Party], extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]) -> AllocationInstructionResult:
        pass

    @choice(controller=actors, consuming="nonconsuming")
    def AllocationInstruction_Accept(self, actors: list[Party], extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]) -> AllocationInstructionResult:
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


@DamlCaseAccessor("AIA_Withdraw", arity=0)
def aia_withdraw(value: AllocationInstructionAction) -> Optional[None]:
    pass


@DamlCaseAccessor("AIA_Accept", arity=0)
def aia_accept(value: AllocationInstructionAction) -> Optional[None]:
    pass


@DamlCaseAccessor("AIA_Custom")
def aia_custom(value: AllocationInstructionAction) -> Optional[str]:
    pass


@ledger_effect
@DamlName("allocationInstruction_withdrawImpl")
def allocation_instruction_withdraw_impl(i: AllocationInstruction, contract_id: ContractId[AllocationInstruction], allocation_instruction_withdraw: AllocationInstruction_Withdraw) -> AllocationInstructionResult:
    pass


@DamlName("allocationInstruction_withdrawExtraObservers")
def allocation_instruction_withdraw_extra_observers(i: AllocationInstruction, allocation_instruction_withdraw: AllocationInstruction_Withdraw) -> list[Party]:
    pass


@ledger_effect
@DamlName("allocationInstruction_acceptImpl")
def allocation_instruction_accept_impl(i: AllocationInstruction, contract_id: ContractId[AllocationInstruction], allocation_instruction_accept: AllocationInstruction_Accept) -> AllocationInstructionResult:
    pass


@DamlName("allocationInstruction_acceptExtraObservers")
def allocation_instruction_accept_extra_observers(i: AllocationInstruction, allocation_instruction_accept: AllocationInstruction_Accept) -> list[Party]:
    pass


@DamlName("allocationFactory_allocateExtraObservers")
def allocation_factory_allocate_extra_observers(i: AllocationFactory, allocation_factory_allocate: AllocationFactory_Allocate) -> list[Party]:
    pass


@ledger_effect
@DamlName("allocationFactory_allocateImpl")
def allocation_factory_allocate_impl(i: AllocationFactory, contract_id: ContractId[AllocationFactory], allocation_factory_allocate: AllocationFactory_Allocate) -> AllocationInstructionResult:
    pass


@ledger_effect
@DamlName("allocationFactory_publicFetchImpl")
def allocation_factory_public_fetch_impl(i: AllocationFactory, contract_id: ContractId[AllocationFactory], allocation_factory_public_fetch: AllocationFactory_PublicFetch) -> AllocationFactoryView:
    pass
