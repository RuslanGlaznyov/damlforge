from typing import Annotated

from forge.models import choice, ContractId, Decimal, Party, variant
from forge.builtins import DamlName, no_derive
from Splice.Api.Token.HoldingV2 import Account, Holding
from Splice.Api.Token.MetadataV1 import ExtraArgs, Metadata


@variant
class TransferSide:
    def SenderSide(): pass
    def ReceiverSide(): pass


struct TransferLegSide:
    transfer_leg_id: Annotated[str, DamlName("transferLegId")]
    side: TransferSide
    otherside: Account
    amount: Decimal
    instrument_id: Annotated[str, DamlName("instrumentId")]
    meta: Metadata


struct EventLogView:
    admin: Party
    meta: Metadata


@no_derive
struct EventLog_HoldingsChangeResult:
    pass


interface EventLog(view=EventLogView):
    @choice(controller=admin, consuming="nonconsuming", observer=observers)
    def EventLog_HoldingsChange(self, admin: Party, account: Account, input_holding_cids: Annotated[list[ContractId[Holding]], DamlName("inputHoldingCids")], transfer_leg_sides: Annotated[list[TransferLegSide], DamlName("transferLegSides")], output_holding_cids: Annotated[list[ContractId[Holding]], DamlName("outputHoldingCids")], observers: list[Party], extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]) -> EventLog_HoldingsChangeResult:
        pass


@DamlName("eventLog_holdingsChangeImpl", is_ledger_effect=True)
def event_log_holdings_change_impl(i: EventLog, contract_id: ContractId[EventLog], event_log_holdings_change: EventLog_HoldingsChange) -> EventLog_HoldingsChangeResult:
    pass
