from datetime import datetime
from typing import Annotated

from forge.models import choice, ContractId, Decimal, ledger_effect, Optional, Party
from forge.builtins import DamlName
from Splice.Api.Token.HoldingV1 import Holding, InstrumentId
from Splice.Api.Token.MetadataV1 import AnyContract, ExtraArgs, Metadata


struct Allocation_WithdrawResult:
    sender_holding_cids: Annotated[list[ContractId[Holding]], DamlName("senderHoldingCids")]
    meta: Metadata


struct Allocation_CancelResult:
    sender_holding_cids: Annotated[list[ContractId[Holding]], DamlName("senderHoldingCids")]
    meta: Metadata


struct Allocation_ExecuteTransferResult:
    sender_holding_cids: Annotated[list[ContractId[Holding]], DamlName("senderHoldingCids")]
    receiver_holding_cids: Annotated[list[ContractId[Holding]], DamlName("receiverHoldingCids")]
    meta: Metadata


struct AllocationView:
    allocation: AllocationSpecification
    holding_cids: Annotated[list[ContractId[Holding]], DamlName("holdingCids")]
    meta: Metadata


struct AllocationSpecification:
    settlement: SettlementInfo
    transfer_leg_id: Annotated[str, DamlName("transferLegId")]
    transfer_leg: Annotated[TransferLeg, DamlName("transferLeg")]


struct TransferLeg:
    sender: Party
    receiver: Party
    amount: Decimal
    instrument_id: Annotated[InstrumentId, DamlName("instrumentId")]
    meta: Metadata


struct SettlementInfo:
    executor: Party
    settlement_ref: Annotated[Reference, DamlName("settlementRef")]
    requested_at: Annotated[datetime, DamlName("requestedAt")]
    allocate_before: Annotated[datetime, DamlName("allocateBefore")]
    settle_before: Annotated[datetime, DamlName("settleBefore")]
    meta: Metadata


struct Reference:
    id: str
    cid: Optional[ContractId[AnyContract]]


interface Allocation(view=AllocationView):
    @choice(controller=view.allocation.transfer_leg.sender, consuming=True)
    def Allocation_Withdraw(self, extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]) -> Allocation_WithdrawResult:
        pass

    @choice(controller=[view.allocation.settlement.executor, view.allocation.transfer_leg.sender, view.allocation.transfer_leg.receiver], consuming=True)
    def Allocation_Cancel(self, extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]) -> Allocation_CancelResult:
        pass

    @choice(controller=[view.allocation.settlement.executor, view.allocation.transfer_leg.sender, view.allocation.transfer_leg.receiver], consuming=True)
    def Allocation_ExecuteTransfer(self, extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]) -> Allocation_ExecuteTransferResult:
        pass


@DamlName("allocationControllers")
def allocation_controllers(allocation_view: AllocationView) -> list[Party]:
    pass


@ledger_effect
@DamlName("allocation_executeTransferImpl")
def allocation_execute_transfer_impl(i: Allocation, contract_id: ContractId[Allocation], allocation_execute_transfer: Allocation_ExecuteTransfer) -> Allocation_ExecuteTransferResult:
    pass


@ledger_effect
@DamlName("allocation_cancelImpl")
def allocation_cancel_impl(i: Allocation, contract_id: ContractId[Allocation], allocation_cancel: Allocation_Cancel) -> Allocation_CancelResult:
    pass


@ledger_effect
@DamlName("allocation_withdrawImpl")
def allocation_withdraw_impl(i: Allocation, contract_id: ContractId[Allocation], allocation_withdraw: Allocation_Withdraw) -> Allocation_WithdrawResult:
    pass
