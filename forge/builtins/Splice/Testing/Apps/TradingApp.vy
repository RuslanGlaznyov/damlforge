from datetime import datetime
from typing import Annotated, TypeVar

from forge.models import choice, ContractId, Optional, Party, template, TextMap
from forge.builtins import DamlName
from Splice.Api.Token.AllocationV1 import Allocation, AllocationSpecification, Allocation_CancelResult, Allocation_ExecuteTransferResult, Reference, SettlementInfo, TransferLeg
from Splice.Api.Token.MetadataV1 import ExtraArgs

A = TypeVar("A")
B = TypeVar("B")


@template
class OTCTradeProposal:
    venue: Party
    trade_cid: Annotated[Optional[ContractId[OTCTradeProposal]], DamlName("tradeCid")]
    transfer_legs: Annotated[TextMap[TransferLeg], DamlName("transferLegs")]
    approvers: list[Party]

    signatory: list[Party] = approvers
    observer: list[Party] = [venue]

    @choice(controller=approver, consuming=True)
    def OTCTradeProposal_Accept(self, approver: Party) -> ContractId[OTCTradeProposal]:
        pass

    @choice(controller=trader, consuming=True)
    def OTCTradeProposal_Reject(self, trader: Party) -> None:
        pass

    @choice(controller=venue, consuming=True)
    def OTCTradeProposal_InitiateSettlement(self, prepare_until: Annotated[datetime, DamlName("prepareUntil")], settle_before: Annotated[datetime, DamlName("settleBefore")]) -> ContractId[OTCTrade]:
        pass


@template
class OTCTrade:
    venue: Party
    transfer_legs: Annotated[TextMap[TransferLeg], DamlName("transferLegs")]
    trade_cid: Annotated[ContractId[OTCTradeProposal], DamlName("tradeCid")]
    created_at: Annotated[datetime, DamlName("createdAt")]
    prepare_until: Annotated[datetime, DamlName("prepareUntil")]
    settle_before: Annotated[datetime, DamlName("settleBefore")]

    signatory: list[Party] = [venue]

    @choice(controller=venue, consuming=True)
    def OTCTrade_Cancel(self, allocations_with_context: Annotated[TextMap[tuple[ContractId[Allocation], ExtraArgs]], DamlName("allocationsWithContext")]) -> TextMap[Optional[Allocation_CancelResult]]:
        pass

    @choice(controller=venue, consuming=True)
    def OTCTrade_Settle(self, allocations_with_context: Annotated[TextMap[tuple[ContractId[Allocation], ExtraArgs]], DamlName("allocationsWithContext")]) -> TextMap[Allocation_ExecuteTransferResult]:
        pass


@DamlName("tradeAllocations")
def trade_allocations(settlement_info: SettlementInfo, transfer_legs: TextMap[TransferLeg]) -> TextMap[AllocationSpecification]:
    pass


@DamlName("tradingParties")
def trading_parties(text_map: TextMap[TransferLeg]) -> set[Party]:
    pass


@DamlName("require", is_ledger_effect=True)
def require(msg: str, invariant: bool) -> None:
    pass


@DamlName("makeTradeRef")
def make_trade_ref(trade_cid: ContractId[OTCTradeProposal]) -> Reference:
    pass


@DamlName("zipTextMaps")
def zip_text_maps(m1: TextMap[A], m2: TextMap[B]) -> TextMap[tuple[Optional[A], Optional[B]]]:
    pass
