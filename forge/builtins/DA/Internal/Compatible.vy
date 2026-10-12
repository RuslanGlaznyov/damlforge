from datetime import datetime
from typing import TypeVar

from forge.models import Decimal, Optional, Party
from forge.builtins import DamlName

A = TypeVar("A")
Artificial0 = TypeVar("Artificial0")
B = TypeVar("B")
C = TypeVar("C")


Maybe = Optional[Artificial0]


String = str


Integer = int


List = list[A]


Tuple3 = tuple[A, B, C]


Tuple = tuple[A, B]


Datetime = datetime


def tuple(a: A, b: B) -> tuple[A, B]:
    pass


def tuple3(a: A, b: B, c: C) -> tuple[A, B, C]:
    pass


def nil() -> list[A]:
    pass


def cons(a: A, list_value: list[A]) -> list[A]:
    pass


@DamlName("toText")
def to_text(a: A) -> str:
    pass


@DamlName("toInteger")
def to_integer(decimal: Decimal) -> int:
    pass
