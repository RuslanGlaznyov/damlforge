from typing import TypeVar

from forge.models.types import ContractId, RelTime, Timestamp
from . import DamlName

_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")


@DamlName("fromInterfaceContractId")
def from_interface_contract_id(interface_cid: ContractId[_T1]) -> ContractId[_T2]:
    raise NotImplementedError(
        "from_interface_contract_id is a real Daml-language builtin - only "
        "meaningful inside compiled .vy source, not callable directly from Python"
    )


@DamlName("toInterfaceContractId")
def to_interface_contract_id(template_cid: ContractId[_T1]) -> ContractId[_T2]:
    raise NotImplementedError(
        "to_interface_contract_id is a real Daml-language builtin - only "
        "meaningful inside compiled .vy source, not callable directly from Python"
    )


@DamlName("toInterface")
def to_interface(value: _T1) -> _T2:
    raise NotImplementedError(
        "to_interface is a real Daml-language builtin - only meaningful "
        "inside compiled .vy source, not callable directly from Python"
    )


@DamlName("coerceInterfaceContractId")
def coerce_interface_contract_id(interface_cid: ContractId[_T1]) -> ContractId[_T2]:
    raise NotImplementedError(
        "coerce_interface_contract_id is a real Daml-language builtin - only "
        "meaningful inside compiled .vy source, not callable directly from Python"
    )


@DamlName("addRelTime", module="DA.Time")
def add_rel_time(time: Timestamp, rel: RelTime) -> Timestamp:
    raise NotImplementedError(
        "add_rel_time is a real DA.Time builtin - only meaningful inside "
        "compiled .vy source, not callable directly from Python"
    )


@DamlName("subTime", module="DA.Time")
def sub_time(t1: Timestamp, t2: Timestamp) -> RelTime:
    raise NotImplementedError(
        "sub_time is a real DA.Time builtin - only meaningful inside "
        "compiled .vy source, not callable directly from Python"
    )


@DamlName("days", module="DA.Time")
def days(n: int) -> RelTime:
    raise NotImplementedError(
        "days is a real DA.Time builtin - only meaningful inside compiled "
        ".vy source, not callable directly from Python"
    )
