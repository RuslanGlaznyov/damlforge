"""Stand-in for the real `Splice.Api.Token.TransferInstructionV1` Daml
module (the `splice-api-token-transfer-instruction-v1` package) -
IDE/authoring support only, see `Splice/__init__.py`. Only covers what
`AmuletRules_Amulet_ExpireTransferInstructions` (`Splice.AmuletRules`)
references - the full token-standard transfer-instruction interface (with
its own `TransferInstruction_Update`/`_Withdraw`/`_Reject`/`_Accept`
choices) is out of scope of the `AmuletRules` choice sweep.
"""

from dataclasses import dataclass
from typing import Annotated

from forge.models.types import ContractId
from ...Api.Token.HoldingV1 import Holding
from ...Api.Token.MetadataV1 import ExtraArgs, Metadata
from .... import DamlName


class TransferInstruction:
    """The real Daml `Splice.Api.Token.TransferInstructionV1.TransferInstruction`
    interface - referenced here only as a nominal type for
    `ContractId[TransferInstruction]`."""


class TransferInstructionResultOutput:
    """The real Daml `TransferInstructionResult_Output` variant type - one
    of `TransferInstructionResult_Pending(transferInstructionCid)`,
    `TransferInstructionResult_Completed(receiverHoldingCids)`, or
    `TransferInstructionResult_Failed`. Never constructed directly by
    DamlForge code - only ever read off a `TransferInstructionResult`
    returned from real Daml."""


@dataclass(frozen=True)
class TransferInstructionResult:
    """The real Daml `TransferInstructionResult` record, returned by
    exercising choices on a `TransferInstruction`. Real Daml definition:

        data TransferInstructionResult = TransferInstructionResult with
            output : TransferInstructionResult_Output
            senderChangeCids : [ContractId Holding]
            meta : Metadata
    """

    output: TransferInstructionResultOutput
    sender_change_cids: Annotated[list[ContractId[Holding]], DamlName("senderChangeCids")]
    meta: Metadata


@dataclass(frozen=True)
class TransferInstruction_Update:
    """`TransferInstruction`'s `TransferInstruction_Update` choice - used by
    `exercise_app_transfer`'s `AmuletRules_Amulet_ExpireTransferInstructions`
    to force-expire a lock via a `ChoiceContext`. Real Daml definition:

        data TransferInstruction_Update = TransferInstruction_Update with
            extraActors : [Party]
            extraArgs : ExtraArgs
    """

    extra_actors: Annotated[list, DamlName("extraActors")]
    extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]
