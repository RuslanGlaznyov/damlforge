from typing import Annotated

from forge.models import ContractId, Party, template
from forge.builtins import DamlName
from Splice.Amulet import LockedAmulet
from Splice.Amulet.TwoStepTransfer import TwoStepTransfer
from Splice.Api.Token.MetadataV1 import ExtraArgs
from Splice.Api.Token.TransferInstructionV1 import Transfer, TransferInstructionResult


@template
class AmuletTransferInstruction:
    locked_amulet: Annotated[ContractId[LockedAmulet], DamlName("lockedAmulet")]
    transfer: Transfer

    signatory: list[Party] = [transfer.sender, transfer.instrument_id.admin]
    observer: list[Party] = [transfer.receiver]


@DamlName("standardTransferToTwoStepTransfer")
def standard_transfer_to_two_step_transfer(transfer: Transfer) -> TwoStepTransfer:
    pass


@DamlName("executeTransferInstr", is_ledger_effect=True)
def execute_transfer_instr(instr: AmuletTransferInstruction, extra_args: ExtraArgs) -> TransferInstructionResult:
    pass


@DamlName("abortAmuletTransferInstruction", is_ledger_effect=True)
def abort_amulet_transfer_instruction(instr: AmuletTransferInstruction, extra_args: ExtraArgs) -> TransferInstructionResult:
    pass


@DamlName("updateAmuletTransferInstruction", is_ledger_effect=True)
def update_amulet_transfer_instruction(instr: AmuletTransferInstruction, extra_actors: list[Party], extra_args: ExtraArgs) -> TransferInstructionResult:
    pass
