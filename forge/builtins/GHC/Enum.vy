from typing import TypeVar

from forge.builtins import DamlName

A = TypeVar("A")


@DamlName("minBound")
def min_bound() -> A:
    pass


@DamlName("maxBound")
def max_bound() -> A:
    pass


def succ(a: A) -> A:
    pass


def pred(a: A) -> A:
    pass


@DamlName("toEnum")
def to_enum(int_value: int) -> A:
    pass


@DamlName("fromEnum")
def from_enum(a: A) -> int:
    pass


@DamlName("enumFrom")
def enum_from(a: A) -> list[A]:
    pass


@DamlName("enumFromThen")
def enum_from_then(a: A, a_1: A) -> list[A]:
    pass


@DamlName("enumFromTo")
def enum_from_to(a: A, a_1: A) -> list[A]:
    pass


@DamlName("enumFromThenTo")
def enum_from_then_to(a: A, a_1: A, a_2: A) -> list[A]:
    pass


@DamlName("eftInt")
def eft_int(x: int, y: int) -> list[int]:
    pass


@DamlName("efdInt")
def efd_int(x1: int, x2: int) -> list[int]:
    pass


@DamlName("efdtInt")
def efdt_int(x1: int, x2: int, y: int) -> list[int]:
    pass


@DamlName("efdtIntUp")
def efdt_int_up(x1: int, x2: int, y: int) -> list[int]:
    pass


def go_up(delta: int, int_value: int, x: int) -> list[int]:
    pass


@DamlName("efdtIntDn")
def efdt_int_dn(x1: int, x2: int, y: int) -> list[int]:
    pass


def go_dn(delta: int, int_value: int, x: int) -> list[int]:
    pass
