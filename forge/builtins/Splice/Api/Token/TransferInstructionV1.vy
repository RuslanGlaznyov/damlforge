from datetime import datetime
from typing import Annotated

from forge.models import choice, ContractId, Decimal, GenMap, Optional, Party, variant, variant_record
from forge.builtins import DamlCaseAccessor, DamlName
from Splice.Api.Token.HoldingV1 import Holding, InstrumentId
from Splice.Api.Token.MetadataV1 import ExtraArgs, Metadata


struct TransferFactoryView:
    admin: Party
    meta: Metadata


struct TransferInstructionView:
    original_instruction_cid: Annotated[Optional[ContractId[TransferInstruction]], DamlName("originalInstructionCid")]
    transfer: Transfer
    status: TransferInstructionStatus
    meta: Metadata


@variant
class TransferInstructionStatus:
    def TransferPendingReceiverAcceptance(): pass
    @variant_record
    def TransferPendingInternalWorkflow(pending_actions: Annotated[GenMap[Party, str], DamlName("pendingActions")]): pass


@variant
class TransferInstructionResult_Output:
    @variant_record
    def TransferInstructionResult_Pending(transfer_instruction_cid: Annotated[ContractId[TransferInstruction], DamlName("transferInstructionCid")]): pass
    @variant_record
    def TransferInstructionResult_Completed(receiver_holding_cids: Annotated[list[ContractId[Holding]], DamlName("receiverHoldingCids")]): pass
    def TransferInstructionResult_Failed(): pass


struct TransferInstructionResult:
    output: TransferInstructionResult_Output
    sender_change_cids: Annotated[list[ContractId[Holding]], DamlName("senderChangeCids")]
    meta: Metadata


struct Transfer:
    sender: Party
    receiver: Party
    amount: Decimal
    instrument_id: Annotated[InstrumentId, DamlName("instrumentId")]
    requested_at: Annotated[datetime, DamlName("requestedAt")]
    execute_before: Annotated[datetime, DamlName("executeBefore")]
    input_holding_cids: Annotated[list[ContractId[Holding]], DamlName("inputHoldingCids")]
    meta: Metadata


interface TransferFactory(view=TransferFactoryView):
    @choice(controller=transfer.sender, consuming="nonconsuming")
    def TransferFactory_Transfer(self, expected_admin: Annotated[Party, DamlName("expectedAdmin")], transfer: Transfer, extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]) -> TransferInstructionResult:
        pass

    @choice(controller=actor, consuming="nonconsuming")
    def TransferFactory_PublicFetch(self, expected_admin: Annotated[Party, DamlName("expectedAdmin")], actor: Party) -> TransferFactoryView:
        pass


interface TransferInstruction(view=TransferInstructionView):
    @choice(controller=view.transfer.receiver, consuming=True)
    def TransferInstruction_Accept(self, extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]) -> TransferInstructionResult:
        pass

    @choice(controller=view.transfer.receiver, consuming=True)
    def TransferInstruction_Reject(self, extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]) -> TransferInstructionResult:
        pass

    @choice(controller=view.transfer.sender, consuming=True)
    def TransferInstruction_Withdraw(self, extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]) -> TransferInstructionResult:
        pass

    @choice(controller=extra_actors + [view.transfer.instrument_id.admin], consuming=True)
    def TransferInstruction_Update(self, extra_actors: Annotated[list[Party], DamlName("extraActors")], extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]) -> TransferInstructionResult:
        pass


@DamlCaseAccessor("TransferPendingReceiverAcceptance", arity=0)
def transfer_pending_receiver_acceptance(value: TransferInstructionStatus) -> Optional[None]:
    pass


@DamlCaseAccessor("TransferPendingInternalWorkflow")
def transfer_pending_internal_workflow(value: TransferInstructionStatus) -> Optional[GenMap[Party, str]]:
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


@DamlName("transferInstruction_updateImpl", is_ledger_effect=True)
def transfer_instruction_update_impl(i: TransferInstruction, contract_id: ContractId[TransferInstruction], transfer_instruction_update: TransferInstruction_Update) -> TransferInstructionResult:
    pass


@DamlName("transferFactory_transferImpl", is_ledger_effect=True)
def transfer_factory_transfer_impl(i: TransferFactory, contract_id: ContractId[TransferFactory], transfer_factory_transfer: TransferFactory_Transfer) -> TransferInstructionResult:
    pass


@DamlName("transferFactory_publicFetchImpl", is_ledger_effect=True)
def transfer_factory_public_fetch_impl(i: TransferFactory, contract_id: ContractId[TransferFactory], transfer_factory_public_fetch: TransferFactory_PublicFetch) -> TransferFactoryView:
    pass
