from typing import TypeVar

from forge.models import Decimal
from forge.builtins import DamlName
from GHC.Types import Ordering

A = TypeVar("A")


def ip() -> A:
    pass


def compare(a: A, a_1: A) -> Ordering:
    pass


def min(a: A, a_1: A) -> A:
    pass


def max(a: A, a_1: A) -> A:
    pass


@DamlName("not")
def not_(bool_value: bool) -> bool:
    pass


@DamlName("numericScale")
def numeric_scale() -> int:
    pass


@DamlName("numericOne")
def numeric_one() -> Decimal:
    pass


@DamlName("privateUnit")
def private_unit() -> None:
    pass
