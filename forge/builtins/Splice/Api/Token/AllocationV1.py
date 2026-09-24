from dataclasses import dataclass
from decimal import Decimal
from typing import Annotated

from forge.models.types import ContractId, Party, Text
from .... import DamlName
from .HoldingV1 import Holding, InstrumentId
from .MetadataV1 import ExtraArgs, Metadata


@dataclass(frozen=True)
class TransferLeg:
    sender: Party
    receiver: Party
    amount: Decimal
    instrument_id: Annotated[InstrumentId, DamlName("instrumentId")]
    meta: Metadata


@dataclass(frozen=True)
class AllocationSpecification:
    transfer_leg_id: Annotated[Text, DamlName("transferLegId")]
    transfer_leg: Annotated[TransferLeg, DamlName("transferLeg")]


@dataclass(frozen=True)
class AllocationView:
    allocation: AllocationSpecification


class Allocation:
    pass


@dataclass(frozen=True)
class Allocation_Withdraw:
    extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]


@dataclass(frozen=True)
class Allocation_WithdrawResult:
    sender_holding_cids: Annotated[
        list[ContractId[Holding]], DamlName("senderHoldingCids")
    ]
    meta: Metadata
