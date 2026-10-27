from typing import TypeVar

from forge.models import ContractId, Optional, Party
from forge.builtins import DamlName
from DA.Internal.Any import AnyChoice, AnyTemplate, TemplateTypeRep

A = TypeVar("A")
C = TypeVar("C")
K = TypeVar("K")
R = TypeVar("R")
T = TypeVar("T")


def signatory(t: T) -> list[Party]:
    pass


def observer(t: T) -> list[Party]:
    pass


def ensure(t: T) -> bool:
    pass


@DamlName("create", is_ledger_effect=True)
def create(t: T) -> ContractId[T]:
    pass


@DamlName("fetch", is_ledger_effect=True)
def fetch(contract_id: ContractId[T]) -> T:
    pass


@DamlName("softFetch", is_ledger_effect=True)
def soft_fetch(contract_id: ContractId[T]) -> T:
    pass


@DamlName("softExercise", is_ledger_effect=True)
def soft_exercise(contract_id: ContractId[T], c: C) -> R:
    pass


@DamlName("archive", is_ledger_effect=True)
def archive(contract_id: ContractId[T]) -> None:
    pass


def stakeholder(t1: T) -> list[Party]:
    pass


@DamlName("exercise", is_ledger_effect=True)
def exercise(contract_id: ContractId[T], c: C) -> R:
    pass


def key(t: T) -> K:
    pass


def maintainer(k: K) -> list[Party]:
    pass


@DamlName("lookupNByKey", is_ledger_effect=True)
def lookup_n_by_key(int_value: int, k: K) -> list[tuple[ContractId[T], T]]:
    pass


@DamlName("lookupAllByKey", is_ledger_effect=True)
def lookup_all_by_key(k: K) -> list[tuple[ContractId[T], T]]:
    pass


@DamlName("lookupByKey", is_ledger_effect=True)
def lookup_by_key(k1: K) -> Optional[ContractId[T]]:
    pass


@DamlName("fetchByKey", is_ledger_effect=True)
def fetch_by_key(k: K) -> tuple[ContractId[T], T]:
    pass


@DamlName("exerciseByKey", is_ledger_effect=True)
def exercise_by_key(k: K, c: C) -> R:
    pass


@DamlName("createAndExercise", is_ledger_effect=True)
def create_and_exercise(t1: T, c1: C) -> R:
    pass


@DamlName("toParties")
def to_parties(a: A) -> list[Party]:
    pass


@DamlName("templateTypeRep")
def template_type_rep() -> TemplateTypeRep:
    pass


@DamlName("toAnyTemplate")
def to_any_template(x: T) -> AnyTemplate:
    pass


@DamlName("fromAnyTemplate")
def from_any_template(any_template: AnyTemplate) -> Optional[T]:
    pass


@DamlName("toAnyChoice")
def to_any_choice(c1: C) -> AnyChoice:
    pass


@DamlName("fromAnyChoice")
def from_any_choice(any_choice: AnyChoice) -> Optional[C]:
    pass


@DamlName("visibleByKey", is_ledger_effect=True)
def visible_by_key(k1: K) -> bool:
    pass
