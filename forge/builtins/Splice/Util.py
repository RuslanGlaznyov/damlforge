"""Authoring stubs for the ledger helpers exported by ``Splice.Util``."""

from typing import TypeVar

from forge.models.types import ContractId
from .. import DamlName

_T = TypeVar("_T")
_I = TypeVar("_I")
_G = TypeVar("_G")
_C = TypeVar("_C")


@DamlName("require")
def require(message: str, condition: bool) -> None:
    raise NotImplementedError


@DamlName("requireMatchingContract", is_ledger_effect=True)
def require_matching_contract(cid: ContractId[_T], expected: _T) -> None:
    raise NotImplementedError


@DamlName("fetchAndArchive", is_ledger_effect=True)
def fetch_and_archive(group: _G, cid: ContractId[_T]) -> _T:
    raise NotImplementedError


@DamlName("fetchPublicReferenceData", is_ledger_effect=True)
def fetch_public_reference_data(group: _G, cid: ContractId[_T], choice: _C) -> _T:
    raise NotImplementedError


@DamlName("fetchCheckedInterface", is_ledger_effect=True)
def fetch_checked_interface(group: _G, cid: ContractId[_I]) -> _I:
    raise NotImplementedError


@DamlName("fetchUncheckedButArchiveLater", is_ledger_effect=True)
def fetch_unchecked_but_archive_later(cid: ContractId[_T]) -> _T:
    raise NotImplementedError
