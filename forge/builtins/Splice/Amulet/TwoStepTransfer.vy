from datetime import datetime
from typing import Annotated

from forge.models import ContractId, Decimal, Party
from forge.builtins import DamlName, no_derive
from Splice.Amulet import LockedAmulet
from Splice.AmuletRules import ExternalPartyTransferContext, TransferInput
from Splice.Api.Token.HoldingV1 import Holding
from Splice.Api.Token.MetadataV1 import ExtraArgs, Metadata
from Splice.Types import ForOwner


@no_derive
struct TwoStepTransfer:
    dso: Party
    sender: Party
    receiver: Party
    amount: Decimal
    lock_context: Annotated[str, DamlName("lockContext")]
    transfer_before: Annotated[datetime, DamlName("transferBefore")]
    transfer_before_deadline: Annotated[str, DamlName("transferBeforeDeadline")]
    provider: Party
    allow_featuring: Annotated[bool, DamlName("allowFeaturing")]


@DamlName("holdingToTransferInputs", is_ledger_effect=True)
def holding_to_transfer_inputs(for_owner: ForOwner, input_holding_cids: list[ContractId[Holding]]) -> list[TransferInput]:
    pass


@DamlName("prepareTwoStepTransfer", is_ledger_effect=True)
def prepare_two_step_transfer(two_step_transfer: TwoStepTransfer, requested_at: datetime, input_holding_cids: list[ContractId[Holding]], context: ExternalPartyTransferContext) -> tuple[ContractId[LockedAmulet], list[ContractId[Holding]], Metadata]:
    pass


@DamlName("executeTwoStepTransfer", is_ledger_effect=True)
def execute_two_step_transfer(two_step_transfer: TwoStepTransfer, locked_amulet_cid: ContractId[LockedAmulet], transfer_meta: Metadata, extra_args: ExtraArgs) -> tuple[list[ContractId[Holding]], list[ContractId[Holding]], Metadata]:
    pass


@DamlName("abortTwoStepTransfer", is_ledger_effect=True)
def abort_two_step_transfer(lock_expires_at: datetime, locked_amulet_cid: ContractId[LockedAmulet], extra_args: ExtraArgs) -> list[ContractId[Holding]]:
    pass
