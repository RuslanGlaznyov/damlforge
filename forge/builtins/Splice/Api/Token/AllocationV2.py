from dataclasses import dataclass
from typing import Annotated

from forge.models.types import Party, Text
from .... import DamlName
from .HoldingV2 import Account
from .MetadataV1 import ExtraArgs, Metadata


@dataclass(frozen=True)
class SettlementInfo:
    executors: list[Party]


@dataclass(frozen=True)
class TransferLegSide:
    transfer_leg_id: Annotated[Text, DamlName("transferLegId")]
    instrument_id: Annotated[Text, DamlName("instrumentId")]


@dataclass(frozen=True)
class AllocationSpecification:
    admin: Party
    authorizer: Account
    transfer_leg_sides: Annotated[list[TransferLegSide], DamlName("transferLegSides")]


@dataclass(frozen=True)
class AllocationView:
    allocation: AllocationSpecification


class Allocation:
    pass


@dataclass(frozen=True)
class Allocation_Withdraw:
    actors: list[Party]
    extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]


@dataclass(frozen=True)
class AllocationResult:
    meta: Metadata
