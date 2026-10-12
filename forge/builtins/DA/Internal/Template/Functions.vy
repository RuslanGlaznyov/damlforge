from typing import TypeVar

from forge.models import ContractId, ledger_effect, Optional, Party
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


@ledger_effect
def create(t: T) -> ContractId[T]:
    pass


@ledger_effect
def fetch(contract_id: ContractId[T]) -> T:
    pass


@ledger_effect
@DamlName("softFetch")
def soft_fetch(contract_id: ContractId[T]) -> T:
    pass


@ledger_effect
@DamlName("softExercise")
def soft_exercise(contract_id: ContractId[T], c: C) -> R:
    pass


@ledger_effect
def archive(contract_id: ContractId[T]) -> None:
    pass


def stakeholder(t1: T) -> list[Party]:
    pass


@ledger_effect
def exercise(contract_id: ContractId[T], c: C) -> R:
    pass


def key(t: T) -> K:
    pass


def maintainer(k: K) -> list[Party]:
    pass


@ledger_effect
@DamlName("createAndExercise")
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
