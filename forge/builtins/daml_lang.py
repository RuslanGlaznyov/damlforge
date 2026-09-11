from typing import Optional, TypeVar

from forge.models.types import ContractId, RelTime, Timestamp
from . import DamlName

_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")


@DamlName("fetch", is_ledger_effect=True)
def fetch(cid: ContractId[_T1]) -> _T1:
    raise NotImplementedError(
        "fetch is a real Daml-language builtin - only meaningful inside "
        "compiled .vy source, not callable directly from Python"
    )


@DamlName("exercise", is_ledger_effect=True)
def exercise(cid: ContractId[_T1], choice_args: _T2):
    raise NotImplementedError(
        "exercise is a real Daml-language builtin - only meaningful inside "
        "compiled .vy source, not callable directly from Python"
    )


@DamlName("create", is_ledger_effect=True)
def create(payload: _T1) -> ContractId[_T1]:
    raise NotImplementedError(
        "create is a real Daml-language builtin - only meaningful inside "
        "compiled .vy source, not callable directly from Python"
    )


@DamlName("archive", is_ledger_effect=True)
def archive(cid: ContractId[_T1]) -> None:
    raise NotImplementedError(
        "archive is a real Daml-language builtin - only meaningful inside "
        "compiled .vy source, not callable directly from Python"
    )


@DamlName("lookup", is_ledger_effect=True)
def lookup(key: _T1) -> Optional[ContractId[_T2]]:
    raise NotImplementedError(
        "lookup is a real Daml-language builtin - only meaningful inside "
        "compiled .vy source, not callable directly from Python"
    )


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


@DamlName("view")
def view(interface_value: _T1) -> _T2:
    raise NotImplementedError(
        "view is a real Daml-language builtin - only meaningful inside "
        "compiled .vy source, not callable directly from Python"
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
