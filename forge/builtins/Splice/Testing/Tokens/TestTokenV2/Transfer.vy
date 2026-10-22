from typing import Annotated

from forge.models import ContractId, Decimal, GenMap, Optional, Party, template
from forge.builtins import DamlName
from Splice.Api.Token.HoldingV2 import Account, Holding, HoldingView
from Splice.Api.Token.MetadataV1 import ExtraArgs
from Splice.Api.Token.TransferInstructionV2 import Transfer, TransferInstruction, TransferInstructionAction, TransferInstructionResult, TransferInstruction_Accept, TransferInstruction_Reject, TransferInstruction_Withdraw
from Splice.Testing.Tokens.TestTokenV2.AccountConfig import AccountConfig, TransferInstructionState
from Splice.Testing.Tokens.TestTokenV2.Util import CallSource


@template
class TokenTransferOffer:
    action_authorizers: Annotated[GenMap[TransferInstructionAction, list[Party]], DamlName("actionAuthorizers")]
    available_actions: Annotated[GenMap[TransferInstructionAction, list[list[Party]]], DamlName("availableActions")]
    transfer: Transfer
    original_instruction_cid: Annotated[Optional[ContractId[TransferInstruction]], DamlName("originalInstructionCid")]
    mint_amount: Annotated[Decimal, DamlName("mintAmount")]

    signatory: list[Party] = [transfer.instrument_id.admin]


@DamlName("token_transferInstruction_withdrawImplV2", is_ledger_effect=True)
def token_transfer_instruction_withdraw_impl_v2(call_source: CallSource, this: TokenTransferOffer, self_: ContractId[TransferInstruction], arg: TransferInstruction_Withdraw) -> TransferInstructionResult:
    pass


@DamlName("token_transferInstruction_acceptImplV2", is_ledger_effect=True)
def token_transfer_instruction_accept_impl_v2(call_source: CallSource, this: TokenTransferOffer, self_: ContractId[TransferInstruction], arg: TransferInstruction_Accept) -> TransferInstructionResult:
    pass


@DamlName("token_transferInstruction_rejectImplV2", is_ledger_effect=True)
def token_transfer_instruction_reject_impl_v2(call_source: CallSource, this: TokenTransferOffer, self_: ContractId[TransferInstruction], arg: TransferInstruction_Reject) -> TransferInstructionResult:
    pass


@DamlName("transferInstructionTransition", is_ledger_effect=True)
def transfer_instruction_transition(this: TokenTransferOffer, optional: Optional[ContractId[TransferInstruction]], list_value: list[Party], gen_map: GenMap[Account, tuple[AccountConfig, Optional[ContractId[AccountConfig]]]], extra_args: ExtraArgs, transfer_instruction_state: TransferInstructionState, transfer_instruction_state_6: TransferInstructionState) -> TransferInstructionResult:
    pass


@DamlName("applyTransferInstructionTransitions", is_ledger_effect=True)
def apply_transfer_instruction_transitions(call_source: CallSource, this: TokenTransferOffer, o_self: Optional[ContractId[TransferInstruction]], actors: list[Party], action: TransferInstructionAction, extra_args: ExtraArgs) -> TransferInstructionResult:
    pass


@DamlName("createLockedInputs", is_ledger_effect=True)
def create_locked_inputs(transfer: Transfer) -> list[ContractId[Holding]]:
    pass


@DamlName("unlockTokenTransferOffer", is_ledger_effect=True)
def unlock_token_transfer_offer(reason: str, offer: TokenTransferOffer, extra_args: ExtraArgs) -> list[ContractId[Holding]]:
    pass


@DamlName("senderHoldingFromTransfer")
def sender_holding_from_transfer(transfer: Transfer) -> HoldingView:
    pass
