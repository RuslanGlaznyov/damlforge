from typing import TypeVar

from forge.models import ContractId, GenMap, TextMap
from forge.builtins import DamlName

A = TypeVar("A")
B = TypeVar("B")
Cgid = TypeVar("Cgid")
Ch = TypeVar("Ch")
I = TypeVar("I")
K = TypeVar("K")
T = TypeVar("T")


@DamlName("requireMatchingContract", is_ledger_effect=True)
def require_matching_contract(cid: ContractId[T], expected_co: T) -> None:
    pass


@DamlName("require", is_ledger_effect=True)
def require(msg: str, invariant: bool) -> None:
    pass


@DamlName("contractGroupId")
def contract_group_id(t: T) -> Cgid:
    pass


@DamlName("fetchChecked", is_ledger_effect=True)
def fetch_checked(expectedcgid: Cgid, cid: ContractId[T]) -> T:
    pass


@DamlName("fetchCheckedInterface", is_ledger_effect=True)
def fetch_checked_interface(cgid: Cgid, contract_id: ContractId[I]) -> I:
    pass


@DamlName("fetchAndArchive", is_ledger_effect=True)
def fetch_and_archive(cgid1: Cgid, cid: ContractId[T]) -> T:
    pass


@DamlName("fetchReferenceData", is_ledger_effect=True)
def fetch_reference_data(cgid: Cgid, contract_id: ContractId[T]) -> T:
    pass


@DamlName("fetchButArchiveLater", is_ledger_effect=True)
def fetch_but_archive_later(cgid: Cgid, contract_id: ContractId[T]) -> T:
    pass


@DamlName("fetchPublicReferenceData", is_ledger_effect=True)
def fetch_public_reference_data(expected_cgid: Cgid, cid: ContractId[T], arg: Ch) -> T:
    pass


@DamlName("fetchUncheckedAndArchive", is_ledger_effect=True)
def fetch_unchecked_and_archive(cid: ContractId[B]) -> B:
    pass


@DamlName("fetchUncheckedReferenceData", is_ledger_effect=True)
def fetch_unchecked_reference_data(contract_id: ContractId[T]) -> T:
    pass


@DamlName("fetchUncheckedButArchiveLater", is_ledger_effect=True)
def fetch_unchecked_but_archive_later(contract_id: ContractId[T]) -> T:
    pass


@DamlName("potentiallyUnsafeArchive", is_ledger_effect=True)
def potentially_unsafe_archive(contract_id: ContractId[T]) -> None:
    pass


@DamlName("checkContractGroupId", is_ledger_effect=True)
def check_contract_group_id(cgid: Cgid, contract_id: ContractId[I], t: T) -> T:
    pass


def patch(a: A, a_1: A, a_2: A) -> A:
    pass


@DamlName("patchScalar")
def patch_scalar(new: A, base: A, current: A) -> A:
    pass


@DamlName("patchListAsScalar")
def patch_list_as_scalar(list_value: list[A], list_value_1: list[A], list_value_2: list[A]) -> list[A]:
    pass


@DamlName("patchListAsSet")
def patch_list_as_set(list_value: list[A], list_value_1: list[A], list_value_2: list[A]) -> list[A]:
    pass


@DamlName("mapDifference")
def map_difference(gen_map: GenMap[K, A], gen_map_1: GenMap[K, A]) -> GenMap[K, K]:
    pass


@DamlName("textMapDifference")
def text_map_difference(text_map: TextMap[A], text_map_1: TextMap[A]) -> TextMap[str]:
    pass


@DamlName("deprecatedChoice", is_ledger_effect=True)
def deprecated_choice(package: str, version: str, choice: str) -> A:
    pass
