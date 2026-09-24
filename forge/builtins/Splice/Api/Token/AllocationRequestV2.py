from dataclasses import dataclass
from typing import Annotated

from forge.models.types import Party
from .... import DamlName
from .AllocationV2 import SettlementInfo
from .MetadataV1 import ExtraArgs


class AllocationRequest:
    pass


@dataclass(frozen=True)
class AllocationRequestView:
    settlement: SettlementInfo


@dataclass(frozen=True)
class AllocationRequest_Accept:
    actors: list[Party]
    extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]
