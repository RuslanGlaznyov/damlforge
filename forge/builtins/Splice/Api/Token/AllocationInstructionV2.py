from dataclasses import dataclass
from datetime import datetime
from typing import Annotated

from forge.models.types import ContractId, Party
from .... import DamlName
from .AllocationV2 import AllocationSpecification, SettlementInfo
from .HoldingV2 import Holding
from .MetadataV1 import ExtraArgs, Metadata


class AllocationFactory:
    pass


class AllocationInstruction:
    pass


@dataclass(frozen=True)
class AllocationInstructionView:
    allocation: AllocationSpecification


@dataclass(frozen=True)
class AllocationFactory_Allocate:
    settlement: SettlementInfo
    allocation: AllocationSpecification
    requested_at: Annotated[datetime, DamlName("requestedAt")]
    input_holding_cids: Annotated[list[ContractId[Holding]], DamlName("inputHoldingCids")]
    extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]
    actors: list[Party]


@dataclass(frozen=True)
class AllocationInstruction_Accept:
    actors: list[Party]
    extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]


@dataclass(frozen=True)
class AllocationInstruction_Withdraw:
    actors: list[Party]
    extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]


@dataclass(frozen=True)
class AllocationInstructionResult:
    meta: Metadata
