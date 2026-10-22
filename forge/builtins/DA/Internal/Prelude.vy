from typing import TypeVar

from forge.models import Decimal, Optional
from forge.builtins import DamlName

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


@DamlName("return", is_ledger_effect=True)
def return_(a: A) -> A:
    pass


def identity(x: A) -> A:
    pass


@DamlName("guard", is_ledger_effect=True)
def guard(bool_value: bool) -> None:
    pass


def length(list_value: list[A]) -> int:
    pass


@DamlName("or")
def or_(list_value: list[bool]) -> bool:
    pass


@DamlName("and")
def and_(list_value: list[bool]) -> bool:
    pass


def elem(x: A, list_value: list[A]) -> bool:
    pass


@DamlName("notElem")
def not_elem(x: A, list_value: list[A]) -> bool:
    pass


def mempty() -> A:
    pass


def mconcat(list_value: list[A]) -> A:
    pass


def concat(list_value: list[list[A]]) -> list[A]:
    pass


def reverse(list_value: list[A]) -> list[A]:
    pass


def replicate(i: int, x: A) -> list[A]:
    pass


def take(n: int, list_value: list[A]) -> list[A]:
    pass


def drop(n: int, xs: list[A]) -> list[A]:
    pass


@DamlName("splitAt")
def split_at(int_value: int, list_value: list[A]) -> tuple[list[A], list[A]]:
    pass


def lookup(a: A, list_value: list[tuple[A, B]]) -> Optional[B]:
    pass


def enumerate() -> list[A]:
    pass


def zip(list_value: list[A], list_value_1: list[B]) -> list[tuple[A, B]]:
    pass


def zip3(list_value: list[A], list_value_1: list[B], list_value_2: list[C]) -> list[tuple[A, B, C]]:
    pass


def unzip(list_value: list[tuple[A, B]]) -> tuple[list[A], list[B]]:
    pass


def unzip3(list_value: list[tuple[A, B, C]]) -> tuple[list[A], list[B], list[C]]:
    pass


@DamlName("traceRaw")
def trace_raw(str_value: str, a: A) -> A:
    pass


def trace(b: B, a: A) -> A:
    pass


@DamlName("traceId")
def trace_id(x: B) -> B:
    pass


@DamlName("debug", is_ledger_effect=True)
def debug(x: B) -> None:
    pass


@DamlName("debugRaw", is_ledger_effect=True)
def debug_raw(str_value: str) -> None:
    pass


def fst(tuple_value: tuple[A, B]) -> A:
    pass


def snd(tuple_value: tuple[A, B]) -> B:
    pass


def truncate(decimal: Decimal) -> int:
    pass


@DamlName("intToNumeric")
def int_to_numeric(int_value: int) -> Decimal:
    pass


@DamlName("intToDecimal")
def int_to_decimal(int_value: int) -> Decimal:
    pass


@DamlName("roundBankers")
def round_bankers(int_value: int, decimal: Decimal) -> Decimal:
    pass


@DamlName("roundCommercial")
def round_commercial(int_value: int, decimal: Decimal) -> Decimal:
    pass


def round(decimal: Decimal) -> int:
    pass


def floor(x: Decimal) -> int:
    pass


def ceiling(x: Decimal) -> int:
    pass


def null(list_value: list[A]) -> bool:
    pass


def sum(list_value: list[A]) -> A:
    pass


def product(list_value: list[A]) -> A:
    pass


def undefined() -> A:
    pass
