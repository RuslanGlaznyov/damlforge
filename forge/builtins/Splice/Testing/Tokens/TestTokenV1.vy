from forge.models import ContractId, Decimal, Optional, Party, template
from forge.builtins import DamlName
from Splice.Api.Token.AllocationV1 import AllocationSpecification
from Splice.Api.Token.HoldingV1 import Holding, HoldingView, InstrumentId
from Splice.Api.Token.TransferInstructionV1 import Transfer


@template
class Token:
    holding: HoldingView

    signatory: list[Party] = [holding.instrument_id.admin, holding.owner]


@template
class TokenTransferOffer:
    transfer: Transfer

    signatory: list[Party] = [transfer.instrument_id.admin, transfer.sender]
    observer: list[Party] = [transfer.receiver]


@template
class TokenAllocation:
    allocation: AllocationSpecification

    signatory: list[Party] = [allocation.transfer_leg.instrument_id.admin, allocation.transfer_leg.sender]
    observer: list[Party] = [allocation.settlement.executor]


@template
class TokenRules:
    admin: Party

    signatory: list[Party] = [admin]


@DamlName("consumeHoldingAmount", is_ledger_effect=True)
def consume_holding_amount(sender: Party, input_cids: list[ContractId[Holding]], amount: Decimal, instrument_id: InstrumentId) -> Optional[ContractId[Holding]]:
    pass


@DamlName("allocationHoldingView")
def allocation_holding_view(allocation_specification: AllocationSpecification) -> HoldingView:
    pass


@DamlName("transferHoldingView")
def transfer_holding_view(transfer: Transfer) -> HoldingView:
    pass
