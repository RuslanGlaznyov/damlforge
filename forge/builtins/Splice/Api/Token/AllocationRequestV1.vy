from typing import Annotated

from forge.models import choice, ContractId, ledger_effect, Party, TextMap
from forge.builtins import DamlName
from Splice.Api.Token.AllocationV1 import SettlementInfo, TransferLeg
from Splice.Api.Token.MetadataV1 import ChoiceExecutionMetadata, ExtraArgs, Metadata


struct AllocationRequestView:
    settlement: SettlementInfo
    transfer_legs: Annotated[TextMap[TransferLeg], DamlName("transferLegs")]
    meta: Metadata


interface AllocationRequest(view=AllocationRequestView):
    @choice(controller=actor, consuming=True)
    def AllocationRequest_Reject(self, actor: Party, extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]) -> ChoiceExecutionMetadata:
        pass

    @choice(controller=view.settlement.executor, consuming=True)
    def AllocationRequest_Withdraw(self, extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]) -> ChoiceExecutionMetadata:
        pass


@ledger_effect
@DamlName("allocationRequest_RejectImpl")
def allocation_request_reject_impl(i: AllocationRequest, contract_id: ContractId[AllocationRequest], allocation_request_reject: AllocationRequest_Reject) -> ChoiceExecutionMetadata:
    pass


@ledger_effect
@DamlName("allocationRequest_WithdrawImpl")
def allocation_request_withdraw_impl(i: AllocationRequest, contract_id: ContractId[AllocationRequest], allocation_request_withdraw: AllocationRequest_Withdraw) -> ChoiceExecutionMetadata:
    pass
