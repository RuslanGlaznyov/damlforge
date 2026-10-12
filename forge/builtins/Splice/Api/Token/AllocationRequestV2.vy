from datetime import datetime
from typing import Annotated

from forge.models import choice, ContractId, GenMap, ledger_effect, Optional, Party, variant, variant_record
from forge.builtins import DamlCaseAccessor, DamlName
from Splice.Api.Token.AllocationV2 import AllocationSpecification, SettlementInfo
from Splice.Api.Token.MetadataV1 import ExtraArgs, Metadata


@variant
class AllocationRequestAction:
    def ARA_Accept(): pass
    def ARA_Reject(): pass
    @variant_record
    def ARA_Custom(id: str): pass


struct AllocationRequestView:
    original_request_cid: Annotated[Optional[ContractId[AllocationRequest]], DamlName("originalRequestCid")]
    settlement: SettlementInfo
    allocations: list[AllocationSpecification]
    requested_at: Annotated[datetime, DamlName("requestedAt")]
    settle_at: Annotated[Optional[datetime], DamlName("settleAt")]
    available_actions: Annotated[GenMap[AllocationRequestAction, list[list[Party]]], DamlName("availableActions")]
    meta: Metadata


struct AllocationRequest_AcceptResult:
    meta: Metadata


struct AllocationRequest_RejectResult:
    meta: Metadata


struct AllocationRequest_WithdrawResult:
    meta: Metadata


interface AllocationRequest(view=AllocationRequestView):
    @choice(controller=actors, consuming="nonconsuming")
    def AllocationRequest_Accept(self, actors: list[Party], extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]) -> AllocationRequest_AcceptResult:
        pass

    @choice(controller=actors, consuming="nonconsuming")
    def AllocationRequest_Reject(self, actors: list[Party], extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]) -> AllocationRequest_RejectResult:
        pass

    @choice(controller=actors, consuming="nonconsuming")
    def AllocationRequest_Withdraw(self, actors: list[Party], extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]) -> AllocationRequest_WithdrawResult:
        pass


@DamlCaseAccessor("ARA_Accept", arity=0)
def ara_accept(value: AllocationRequestAction) -> Optional[None]:
    pass


@DamlCaseAccessor("ARA_Reject", arity=0)
def ara_reject(value: AllocationRequestAction) -> Optional[None]:
    pass


@DamlCaseAccessor("ARA_Custom")
def ara_custom(value: AllocationRequestAction) -> Optional[str]:
    pass


@ledger_effect
@DamlName("allocationRequest_acceptImpl")
def allocation_request_accept_impl(i: AllocationRequest, contract_id: ContractId[AllocationRequest], allocation_request_accept: AllocationRequest_Accept) -> AllocationRequest_AcceptResult:
    pass


@ledger_effect
@DamlName("allocationRequest_rejectImpl")
def allocation_request_reject_impl(i: AllocationRequest, contract_id: ContractId[AllocationRequest], allocation_request_reject: AllocationRequest_Reject) -> AllocationRequest_RejectResult:
    pass


@ledger_effect
@DamlName("allocationRequest_withdrawImpl")
def allocation_request_withdraw_impl(i: AllocationRequest, contract_id: ContractId[AllocationRequest], allocation_request_withdraw: AllocationRequest_Withdraw) -> AllocationRequest_WithdrawResult:
    pass


@DamlName("allocationRequest_acceptExtraObservers")
def allocation_request_accept_extra_observers(i: AllocationRequest, allocation_request_accept: AllocationRequest_Accept) -> list[Party]:
    pass


@DamlName("allocationRequest_rejectExtraObservers")
def allocation_request_reject_extra_observers(i: AllocationRequest, allocation_request_reject: AllocationRequest_Reject) -> list[Party]:
    pass


@DamlName("allocationRequest_withdrawExtraObservers")
def allocation_request_withdraw_extra_observers(i: AllocationRequest, allocation_request_withdraw: AllocationRequest_Withdraw) -> list[Party]:
    pass
