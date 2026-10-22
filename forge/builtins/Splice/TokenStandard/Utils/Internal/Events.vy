from forge.models import ContractId, Decimal, Party
from forge.builtins import DamlName
from Splice.Api.Token.AllocationV2 import AllocationSpecification, TransferLegSide, TransferSide
from Splice.Api.Token.HoldingV2 import Account, Holding, InstrumentId
from Splice.Api.Token.MetadataV1 import ExtraArgs, Metadata
from Splice.Api.Token.TransferInstructionV2 import Transfer
import Splice.Api.Token.TransferEventsV2 as TransferEventsV2


@DamlName("eventLog_holdingsChangeDefaultImpl", is_ledger_effect=True)
def event_log_holdings_change_default_impl(admin: Party, contract_id: ContractId[TransferEventsV2.EventLog], arg: TransferEventsV2.EventLog_HoldingsChange) -> TransferEventsV2.EventLog_HoldingsChangeResult:
    pass


@DamlName("mintAccountId")
def mint_account_id() -> str:
    pass


@DamlName("burnAccountId")
def burn_account_id() -> str:
    pass


@DamlName("mintAccount")
def mint_account() -> Account:
    pass


@DamlName("burnAccount")
def burn_account() -> Account:
    pass


@DamlName("allocationToTransferEventSide")
def allocation_to_transfer_event_side(side: TransferSide) -> TransferEventsV2.TransferSide:
    pass


@DamlName("allocationToTransferEventLegSide")
def allocation_to_transfer_event_leg_side(transfer_leg_side: TransferLegSide) -> TransferEventsV2.TransferLegSide:
    pass


@DamlName("logHoldingsChange", is_ledger_effect=True)
def log_holdings_change(event_log_cid: ContractId[TransferEventsV2.EventLog], arg: TransferEventsV2.EventLog_HoldingsChange) -> None:
    pass


@DamlName("logMint", is_ledger_effect=True)
def log_mint(factory_cid: ContractId[TransferEventsV2.EventLog], receiver: Account, amount: Decimal, instrument_id: InstrumentId, meta: Metadata, output_holding_cids: list[ContractId[Holding]]) -> None:
    pass


@DamlName("logBurn", is_ledger_effect=True)
def log_burn(factory_cid: ContractId[TransferEventsV2.EventLog], sender: Account, amount: Decimal, instrument_id: InstrumentId, meta: Metadata, input_holding_cids: list[ContractId[Holding]]) -> None:
    pass


@DamlName("logAllocationSettlement", is_ledger_effect=True)
def log_allocation_settlement(event_log_cid: ContractId[TransferEventsV2.EventLog], input_holding_cids: list[ContractId[Holding]], allocation: AllocationSpecification, output_holding_cids: list[ContractId[Holding]]) -> None:
    pass


@DamlName("logTransfer", is_ledger_effect=True)
def log_transfer(event_log_cid: ContractId[TransferEventsV2.EventLog], transfer: Transfer, sender_output_holding_cids: list[ContractId[Holding]], receiver_output_holding_cids: list[ContractId[Holding]]) -> None:
    pass


@DamlName("logMergeSplit", is_ledger_effect=True)
def log_merge_split(event_log_cid: ContractId[TransferEventsV2.EventLog], admin: Party, account: Account, input_holding_cids: list[ContractId[Holding]], reason: str, output_holding_cids: list[ContractId[Holding]]) -> None:
    pass


@DamlName("emptyExtraArgs")
def empty_extra_args() -> ExtraArgs:
    pass
