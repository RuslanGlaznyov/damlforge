from datetime import datetime
from typing import Annotated

from forge.models import choice, ContractId, Decimal, GenMap, Optional, Party, variant, variant_record
from forge.builtins import DamlCaseAccessor, DamlName
from Splice.Api.Token.HoldingV2 import Account, Holding, InstrumentId
from Splice.Api.Token.MetadataV1 import ExtraArgs, Metadata


@variant
class TransferInstructionAction:
    def TIA_Accept(): pass
    def TIA_Reject(): pass
    def TIA_Withdraw(): pass
    @variant_record
    def TIA_Custom(id: str): pass


@variant
class TransferInstructionResult_Output:
    @variant_record
    def TransferInstructionResult_Pending(transfer_instruction_cid: Annotated[ContractId[TransferInstruction], DamlName("transferInstructionCid")]): pass
    @variant_record
    def TransferInstructionResult_Completed(receiver_holding_cids: Annotated[list[ContractId[Holding]], DamlName("receiverHoldingCids")]): pass
    def TransferInstructionResult_Failed(): pass


struct Transfer:
    sender: Account
    receiver: Account
    amount: Decimal
    instrument_id: Annotated[InstrumentId, DamlName("instrumentId")]
    requested_at: Annotated[datetime, DamlName("requestedAt")]
    execute_before: Annotated[datetime, DamlName("executeBefore")]
    input_holding_cids: Annotated[list[ContractId[Holding]], DamlName("inputHoldingCids")]
    meta: Metadata


struct TransferInstructionResult:
    output: TransferInstructionResult_Output
    sender_change_cids: Annotated[list[ContractId[Holding]], DamlName("senderChangeCids")]
    meta: Metadata


struct TransferInstructionView:
    original_instruction_cid: Annotated[Optional[ContractId[TransferInstruction]], DamlName("originalInstructionCid")]
    transfer: Transfer
    expires_at: Annotated[Optional[datetime], DamlName("expiresAt")]
    available_actions: Annotated[GenMap[TransferInstructionAction, list[list[Party]]], DamlName("availableActions")]
    meta: Metadata


struct TransferFactoryView:
    admin: Party
    meta: Metadata


interface TransferFactory(view=TransferFactoryView):
    @choice(controller=actors, consuming="nonconsuming")
    def TransferFactory_Transfer(self, transfer: Transfer, actors: list[Party], extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]) -> TransferInstructionResult:
        pass

    @choice(controller=actors, consuming="nonconsuming")
    def TransferFactory_PublicFetch(self, actors: list[Party]) -> TransferFactoryView:
        pass


interface TransferInstruction(view=TransferInstructionView):
    @choice(controller=actors, consuming="nonconsuming")
    def TransferInstruction_Accept(self, actors: list[Party], extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]) -> TransferInstructionResult:
        pass

    @choice(controller=actors, consuming="nonconsuming")
    def TransferInstruction_Reject(self, actors: list[Party], extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]) -> TransferInstructionResult:
        pass

    @choice(controller=actors, consuming="nonconsuming")
    def TransferInstruction_Withdraw(self, actors: list[Party], extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]) -> TransferInstructionResult:
        pass


@DamlCaseAccessor("TIA_Accept", arity=0)
def tia_accept(value: TransferInstructionAction) -> Optional[None]:
    pass


@DamlCaseAccessor("TIA_Reject", arity=0)
def tia_reject(value: TransferInstructionAction) -> Optional[None]:
    pass


@DamlCaseAccessor("TIA_Withdraw", arity=0)
def tia_withdraw(value: TransferInstructionAction) -> Optional[None]:
    pass


@DamlCaseAccessor("TIA_Custom")
def tia_custom(value: TransferInstructionAction) -> Optional[str]:
    pass


@DamlCaseAccessor("TransferInstructionResult_Pending")
def transfer_instruction_result_pending(value: TransferInstructionResult_Output) -> Optional[ContractId[TransferInstruction]]:
    pass


@DamlCaseAccessor("TransferInstructionResult_Completed")
def transfer_instruction_result_completed(value: TransferInstructionResult_Output) -> Optional[list[ContractId[Holding]]]:
    pass


@DamlCaseAccessor("TransferInstructionResult_Failed", arity=0)
def transfer_instruction_result_failed(value: TransferInstructionResult_Output) -> Optional[None]:
    pass


@DamlName("transferInstruction_acceptImpl", is_ledger_effect=True)
def transfer_instruction_accept_impl(i: TransferInstruction, contract_id: ContractId[TransferInstruction], transfer_instruction_accept: TransferInstruction_Accept) -> TransferInstructionResult:
    pass


@DamlName("transferInstruction_rejectImpl", is_ledger_effect=True)
def transfer_instruction_reject_impl(i: TransferInstruction, contract_id: ContractId[TransferInstruction], transfer_instruction_reject: TransferInstruction_Reject) -> TransferInstructionResult:
    pass


@DamlName("transferInstruction_withdrawImpl", is_ledger_effect=True)
def transfer_instruction_withdraw_impl(i: TransferInstruction, contract_id: ContractId[TransferInstruction], transfer_instruction_withdraw: TransferInstruction_Withdraw) -> TransferInstructionResult:
    pass


@DamlName("transferInstruction_acceptExtraObservers")
def transfer_instruction_accept_extra_observers(i: TransferInstruction, transfer_instruction_accept: TransferInstruction_Accept) -> list[Party]:
    pass


@DamlName("transferInstruction_rejectExtraObservers")
def transfer_instruction_reject_extra_observers(i: TransferInstruction, transfer_instruction_reject: TransferInstruction_Reject) -> list[Party]:
    pass


@DamlName("transferInstruction_withdrawExtraObservers")
def transfer_instruction_withdraw_extra_observers(i: TransferInstruction, transfer_instruction_withdraw: TransferInstruction_Withdraw) -> list[Party]:
    pass


@DamlName("transferFactory_transferExtraObservers")
def transfer_factory_transfer_extra_observers(i: TransferFactory, transfer_factory_transfer: TransferFactory_Transfer) -> list[Party]:
    pass


@DamlName("transferFactory_transferImpl", is_ledger_effect=True)
def transfer_factory_transfer_impl(i: TransferFactory, contract_id: ContractId[TransferFactory], transfer_factory_transfer: TransferFactory_Transfer) -> TransferInstructionResult:
    pass


@DamlName("transferFactory_publicFetchImpl", is_ledger_effect=True)
def transfer_factory_public_fetch_impl(i: TransferFactory, contract_id: ContractId[TransferFactory], transfer_factory_public_fetch: TransferFactory_PublicFetch) -> TransferFactoryView:
    pass
