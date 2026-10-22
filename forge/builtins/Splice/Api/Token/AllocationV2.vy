from datetime import datetime
from typing import Annotated

from forge.models import choice, ContractId, Decimal, GenMap, Optional, Party, TextMap, variant, variant_record
from forge.builtins import DamlCaseAccessor, DamlName
from Splice.Api.Token.HoldingV2 import Account, Holding
from Splice.Api.Token.MetadataV1 import AnyContract, ExtraArgs, Metadata


@variant
class AllocationResult_Output:
    @variant_record
    def AllocationResult_Pending(allocation_cid: Annotated[ContractId[Allocation], DamlName("allocationCid")]): pass
    @variant_record
    def AllocationResult_Settled(next_iteration_allocation_cid: Annotated[Optional[ContractId[Allocation]], DamlName("nextIterationAllocationCid")]): pass
    def AllocationResult_Cancelled(): pass
    def AllocationResult_Withdrawn(): pass


@variant
class AllocationAction:
    def AA_Settle(): pass
    def AA_Cancel(): pass
    def AA_Withdraw(): pass
    @variant_record
    def AA_Custom(id: str): pass


@variant
class TransferSide:
    def SenderSide(): pass
    def ReceiverSide(): pass


struct SettlementInfo:
    executors: list[Party]
    id: str
    cid: Optional[ContractId[AnyContract]]
    meta: Metadata


struct TransferLeg:
    transfer_leg_id: Annotated[str, DamlName("transferLegId")]
    sender: Account
    receiver: Account
    amount: Decimal
    instrument_id: Annotated[str, DamlName("instrumentId")]
    meta: Metadata


struct TransferLegSide:
    transfer_leg_id: Annotated[str, DamlName("transferLegId")]
    side: TransferSide
    otherside: Account
    amount: Decimal
    instrument_id: Annotated[str, DamlName("instrumentId")]
    meta: Metadata


struct AllocationSpecification:
    admin: Party
    authorizer: Account
    transfer_leg_sides: Annotated[list[TransferLegSide], DamlName("transferLegSides")]
    settlement_deadline: Annotated[Optional[datetime], DamlName("settlementDeadline")]
    next_iteration_funding: Annotated[Optional[TextMap[Decimal]], DamlName("nextIterationFunding")]
    committed: bool
    meta: Metadata


struct AllocationView:
    original_allocation_cid: Annotated[Optional[ContractId[Allocation]], DamlName("originalAllocationCid")]
    settlement: SettlementInfo
    allocation: AllocationSpecification
    holding_cids: Annotated[list[ContractId[Holding]], DamlName("holdingCids")]
    created_at: Annotated[datetime, DamlName("createdAt")]
    num_iterations: Annotated[int, DamlName("numIterations")]
    expires_at: Annotated[Optional[datetime], DamlName("expiresAt")]
    available_actions: Annotated[GenMap[AllocationAction, list[list[Party]]], DamlName("availableActions")]
    meta: Metadata


struct FinalizedAllocation:
    allocation_cid: Annotated[ContractId[Allocation], DamlName("allocationCid")]
    extra_transfer_leg_sides: Annotated[list[TransferLegSide], DamlName("extraTransferLegSides")]
    next_iteration_funding: Annotated[Optional[TextMap[Decimal]], DamlName("nextIterationFunding")]


struct AllocationResult:
    output: AllocationResult_Output
    authorizer_holding_cids: Annotated[TextMap[list[ContractId[Holding]]], DamlName("authorizerHoldingCids")]
    meta: Metadata


struct SettlementFactoryView:
    admin: Party
    meta: Metadata


struct SettlementFactory_SettleBatchResult:
    allocation_settle_results: Annotated[list[AllocationResult], DamlName("allocationSettleResults")]
    meta: Metadata


interface Allocation(view=AllocationView):
    @choice(controller=actors, consuming="nonconsuming")
    def Allocation_Settle(self, actors: list[Party], extra_transfer_leg_sides: Annotated[list[TransferLegSide], DamlName("extraTransferLegSides")], next_iteration_funding: Annotated[Optional[TextMap[Decimal]], DamlName("nextIterationFunding")], extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]) -> AllocationResult:
        pass

    @choice(controller=actors, consuming="nonconsuming")
    def Allocation_Cancel(self, actors: list[Party], extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]) -> AllocationResult:
        pass

    @choice(controller=actors, consuming="nonconsuming")
    def Allocation_Withdraw(self, actors: list[Party], extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]) -> AllocationResult:
        pass


interface SettlementFactory(view=SettlementFactoryView):
    @choice(controller=actors, consuming="nonconsuming")
    def SettlementFactory_PublicFetch(self, actors: list[Party]) -> SettlementFactoryView:
        pass

    @choice(controller=actors, consuming="nonconsuming")
    def SettlementFactory_SettleBatch(self, settlement: SettlementInfo, transfer_legs: Annotated[list[TransferLeg], DamlName("transferLegs")], allocations: list[FinalizedAllocation], actors: list[Party], extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]) -> SettlementFactory_SettleBatchResult:
        pass


@DamlCaseAccessor("AllocationResult_Pending")
def allocation_result_pending(value: AllocationResult_Output) -> Optional[ContractId[Allocation]]:
    pass


@DamlCaseAccessor("AllocationResult_Settled")
def allocation_result_settled(value: AllocationResult_Output) -> Optional[Optional[ContractId[Allocation]]]:
    pass


@DamlCaseAccessor("AllocationResult_Cancelled", arity=0)
def allocation_result_cancelled(value: AllocationResult_Output) -> Optional[None]:
    pass


@DamlCaseAccessor("AllocationResult_Withdrawn", arity=0)
def allocation_result_withdrawn(value: AllocationResult_Output) -> Optional[None]:
    pass


@DamlCaseAccessor("AA_Settle", arity=0)
def aa_settle(value: AllocationAction) -> Optional[None]:
    pass


@DamlCaseAccessor("AA_Cancel", arity=0)
def aa_cancel(value: AllocationAction) -> Optional[None]:
    pass


@DamlCaseAccessor("AA_Withdraw", arity=0)
def aa_withdraw(value: AllocationAction) -> Optional[None]:
    pass


@DamlCaseAccessor("AA_Custom")
def aa_custom(value: AllocationAction) -> Optional[str]:
    pass


@DamlName("allocation_settleImpl", is_ledger_effect=True)
def allocation_settle_impl(i: Allocation, contract_id: ContractId[Allocation], allocation_settle: Allocation_Settle) -> AllocationResult:
    pass


@DamlName("allocation_cancelImpl", is_ledger_effect=True)
def allocation_cancel_impl(i: Allocation, contract_id: ContractId[Allocation], allocation_cancel: Allocation_Cancel) -> AllocationResult:
    pass


@DamlName("allocation_withdrawImpl", is_ledger_effect=True)
def allocation_withdraw_impl(i: Allocation, contract_id: ContractId[Allocation], allocation_withdraw: Allocation_Withdraw) -> AllocationResult:
    pass


@DamlName("allocation_settleExtraObservers")
def allocation_settle_extra_observers(i: Allocation, allocation_settle: Allocation_Settle) -> list[Party]:
    pass


@DamlName("allocation_cancelExtraObservers")
def allocation_cancel_extra_observers(i: Allocation, allocation_cancel: Allocation_Cancel) -> list[Party]:
    pass


@DamlName("allocation_withdrawExtraObservers")
def allocation_withdraw_extra_observers(i: Allocation, allocation_withdraw: Allocation_Withdraw) -> list[Party]:
    pass


@DamlName("settlementFactory_publicFetchImpl", is_ledger_effect=True)
def settlement_factory_public_fetch_impl(i: SettlementFactory, contract_id: ContractId[SettlementFactory], settlement_factory_public_fetch: SettlementFactory_PublicFetch) -> SettlementFactoryView:
    pass


@DamlName("settlementFactory_settleBatchImpl", is_ledger_effect=True)
def settlement_factory_settle_batch_impl(i: SettlementFactory, contract_id: ContractId[SettlementFactory], settlement_factory_settle_batch: SettlementFactory_SettleBatch) -> SettlementFactory_SettleBatchResult:
    pass


@DamlName("settlementFactory_settleBatchExtraObservers")
def settlement_factory_settle_batch_extra_observers(i: SettlementFactory, settlement_factory_settle_batch: SettlementFactory_SettleBatch) -> list[Party]:
    pass
