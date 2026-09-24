from typing import Optional, TypeVar

from forge.models.types import (
    ContractId,
    Party,
    Text,
)
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
def to_interface(value: _T1) -> _T2:  # type: ignore[type-var]
    raise NotImplementedError(
        "to_interface is a real Daml-language builtin - only meaningful "
        "inside compiled .vy source, not callable directly from Python"
    )


@DamlName("view")
def view(interface_value: _T1) -> _T2:  # type: ignore[type-var]
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


@DamlName("stakeholder")
def stakeholder(value: _T1) -> list[Party]:
    raise NotImplementedError


@DamlName("reverse")
def reverse(values: list[_T1]) -> list[_T1]:
    raise NotImplementedError


@DamlName("DA.Text.length", module="DA.Text")
def text_length(value: Text) -> int:
    raise NotImplementedError


@DamlName("error")
def error(message: Text) -> _T1:
    raise NotImplementedError
