from datetime import datetime
from typing import Annotated

from forge.models import choice, ContractId, ledger_effect, Optional, Party, template
from forge.builtins import DamlName
from Splice.Amulet import LockedAmulet
from Splice.Amulet.TwoStepTransfer import TwoStepTransfer
from Splice.Api.Token.AllocationV1 import AllocationSpecification, Allocation_ExecuteTransferResult, Reference
from Splice.Api.Token.HoldingV1 import Holding
from Splice.Api.Token.MetadataV1 import ExtraArgs, Metadata


struct AmuletAllocation_DsoExpireResult:
    sender_holding_cids: Annotated[list[ContractId[Holding]], DamlName("senderHoldingCids")]
    meta: Metadata


@template
class AmuletAllocation:
    locked_amulet: Annotated[ContractId[LockedAmulet], DamlName("lockedAmulet")]
    allocation: AllocationSpecification
    expires_at: Annotated[Optional[datetime], DamlName("expiresAt")]

    signatory: list[Party] = [allocation.transfer_leg.sender, allocation.transfer_leg.instrument_id.admin]
    observer: list[Party] = [allocation.settlement.executor]

    @choice(controller=allocation.transfer_leg.instrument_id.admin, consuming=True)
    def AmuletAllocation_DsoExpire(self, expire_lock: Annotated[bool, DamlName("expireLock")]) -> AmuletAllocation_DsoExpireResult:
        pass


@DamlName("mkAllocationLockContext")
def mk_allocation_lock_context(ref: Reference) -> str:
    pass


@DamlName("allocationInstrumentAdmin")
def allocation_instrument_admin(allocation_specification: AllocationSpecification) -> Party:
    pass


@DamlName("allocationToTwoStepTransfer")
def allocation_to_two_step_transfer(allocation: AllocationSpecification) -> TwoStepTransfer:
    pass


@ledger_effect
@DamlName("transferAmuletAllocation")
def transfer_amulet_allocation(amulet_allocation: AmuletAllocation, extra_args: ExtraArgs) -> Allocation_ExecuteTransferResult:
    pass


@ledger_effect
@DamlName("unlockAmuletAllocation")
def unlock_amulet_allocation(amulet_allocation: AmuletAllocation, extra_args: ExtraArgs) -> list[ContractId[Holding]]:
    pass
