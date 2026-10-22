from datetime import datetime
from typing import Annotated

from forge.models import ContractId, Decimal, Optional, Party, template, TextMap
from forge.builtins import DamlName
from Splice.Amulet import Amulet, LockedAmulet
from Splice.AmuletConfig import TransferConfigV2
from Splice.Api.Token.AllocationV2 import AllocationSpecification, SettlementInfo, TransferLegSide
from Splice.Api.Token.HoldingV2 import Account, Holding
from Splice.Api.Token.MetadataV1 import ExtraArgs


@template
class AmuletAllocationV2:
    locked_amulet: Annotated[Optional[ContractId[LockedAmulet]], DamlName("lockedAmulet")]
    settlement: SettlementInfo
    allocation: AllocationSpecification
    expires_at: Annotated[datetime, DamlName("expiresAt")]
    num_iterations: Annotated[int, DamlName("numIterations")]
    created_at: Annotated[datetime, DamlName("createdAt")]

    signatory: list[Party] = [allocation.admin]
    observer: list[Party] = settlement.executors


@DamlName("unlockAmuletAllocationV2", is_ledger_effect=True)
def unlock_amulet_allocation_v2(amulet_allocation: AmuletAllocationV2, extra_args: ExtraArgs) -> TextMap[list[ContractId[Holding]]]:
    pass


@DamlName("netAmuletCreditAmount")
def net_amulet_credit_amount(authorizer: Account, transfer_legs: list[TransferLegSide]) -> Decimal:
    pass


@DamlName("validateAmuletNextIterationFunding", is_ledger_effect=True)
def validate_amulet_next_iteration_funding(optional: Optional[TextMap[Decimal]]) -> Decimal:
    pass


@DamlName("validateAmuletTransferLegSides", is_ledger_effect=True)
def validate_amulet_transfer_leg_sides(transfer_legs: list[TransferLegSide]) -> None:
    pass


@DamlName("computeAllocationExpiryInternal")
def compute_allocation_expiry_internal(transfer_config: TransferConfigV2[Amulet], old_expires_at: datetime, settlement_deadline: Optional[datetime]) -> datetime:
    pass


@DamlName("computeAllocationExpiry", is_ledger_effect=True)
def compute_allocation_expiry(transfer_config: TransferConfigV2[Amulet], old_expires_at: datetime, settlement_deadline: Optional[datetime]) -> datetime:
    pass
