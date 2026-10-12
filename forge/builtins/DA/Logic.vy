from typing import TypeVar

from forge.models import Optional
from forge.builtins import DamlName
from DA.Logic.Types import Formula

S = TypeVar("S")
T = TypeVar("T")


def true() -> Formula[T]:
    pass


def false() -> Formula[T]:
    pass


def neg(formula: Formula[T]) -> Formula[T]:
    pass


def conj(list_value: list[Formula[T]]) -> Formula[T]:
    pass


def disj(list_value: list[Formula[T]]) -> Formula[T]:
    pass


@DamlName("fromBool")
def from_bool(x: bool) -> Formula[T]:
    pass


@DamlName("toNNF")
def to_nnf(formula: Formula[T]) -> Formula[T]:
    pass


@DamlName("toDNF")
def to_dnf(f: Formula[T]) -> Formula[T]:
    pass


@DamlName("zipFormulas")
def zip_formulas(formula: Formula[T], formula_1: Formula[S]) -> Formula[tuple[T, S]]:
    pass


def reduce(f: Formula[T]) -> Formula[T]:
    pass


@DamlName("isBool")
def is_bool(x: Formula[T]) -> Optional[bool]:
    pass
