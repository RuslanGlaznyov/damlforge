from typing import TypeVar

from forge.models import ContractId, Optional
from forge.builtins import DamlName
from DA.Internal.Any import TemplateTypeRep

I = TypeVar("I")
J = TypeVar("J")
T = TypeVar("T")
V = TypeVar("V")


@DamlName("interfaceTypeRep")
def interface_type_rep(x: I) -> TemplateTypeRep:
    pass


@DamlName("toInterface")
def to_interface(t: T) -> I:
    pass


@DamlName("fromInterface")
def from_interface(i: I) -> Optional[T]:
    pass


@DamlName("unsafeFromInterface")
def unsafe_from_interface(contract_id: ContractId[I], i: I) -> T:
    pass


@DamlName("toInterfaceContractId")
def to_interface_contract_id(contract_id: ContractId[T]) -> ContractId[I]:
    pass


@DamlName("fromInterfaceContractId")
def from_interface_contract_id(contract_id: ContractId[I]) -> ContractId[T]:
    pass


@DamlName("coerceInterfaceContractId")
def coerce_interface_contract_id(contract_id: ContractId[I]) -> ContractId[J]:
    pass


@DamlName("fetchFromInterface", is_ledger_effect=True)
def fetch_from_interface(cid: ContractId[I]) -> Optional[tuple[ContractId[T], T]]:
    pass


def view(i: I) -> V:
    pass
