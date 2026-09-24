from dataclasses import dataclass
from decimal import Decimal
from typing import Annotated

from forge.models.types import ContractId, Party
from .... import DamlName
from .HoldingV2 import Account, Holding, InstrumentId
from .MetadataV1 import ExtraArgs, Metadata


@dataclass(frozen=True)
class Transfer:
    sender: Account
    receiver: Account
    amount: Decimal
    instrument_id: Annotated[InstrumentId, DamlName("instrumentId")]


class TransferFactory:
    pass


class TransferInstruction:
    pass


@dataclass(frozen=True)
class TransferInstructionView:
    transfer: Transfer


@dataclass(frozen=True)
class TransferFactory_Transfer:
    transfer: Transfer
    actors: list[Party]
    extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]


@dataclass(frozen=True)
class TransferInstruction_Accept:
    actors: list[Party]
    extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]


@dataclass(frozen=True)
class TransferInstruction_Reject:
    actors: list[Party]
    extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]


@dataclass(frozen=True)
class TransferInstruction_Withdraw:
    actors: list[Party]
    extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]


@dataclass(frozen=True)
class TransferInstructionResult:
    sender_change_cids: Annotated[list[ContractId[Holding]], DamlName("senderChangeCids")]
    meta: Metadata
