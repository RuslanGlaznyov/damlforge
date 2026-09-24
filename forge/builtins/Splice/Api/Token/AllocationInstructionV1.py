from dataclasses import dataclass
from datetime import datetime
from typing import Annotated

from forge.models.types import ContractId, Party
from .... import DamlName
from .AllocationV1 import AllocationSpecification
from .HoldingV1 import Holding
from .MetadataV1 import ExtraArgs, Metadata


class AllocationFactory:
    pass


@dataclass(frozen=True)
class AllocationFactory_Allocate:
    expected_admin: Annotated[Party, DamlName("expectedAdmin")]
    allocation: AllocationSpecification
    requested_at: Annotated[datetime, DamlName("requestedAt")]
    input_holding_cids: Annotated[list[ContractId[Holding]], DamlName("inputHoldingCids")]
    extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]


@dataclass(frozen=True)
class AllocationInstructionResult:
    meta: Metadata
