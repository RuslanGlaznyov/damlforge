from typing import TypeVar

from forge.models import Optional
from forge.builtins import DamlName

A = TypeVar("A")


def sort(list_value: list[A]) -> list[A]:
    pass


def group(list_value: list[A]) -> list[list[A]]:
    pass


def dedup(list_value: list[A]) -> list[A]:
    pass


@DamlName("dedupSort")
def dedup_sort(list_value: list[A]) -> list[A]:
    pass


def unique(list_value: list[A]) -> bool:
    pass


def replace(list_value: list[A], list_value_1: list[A], xs: list[A]) -> list[A]:
    pass


@DamlName("dropPrefix")
def drop_prefix(a1: list[A], b: list[A]) -> list[A]:
    pass


@DamlName("dropSuffix")
def drop_suffix(a1: list[A], b: list[A]) -> list[A]:
    pass


@DamlName("stripPrefix")
def strip_prefix(list_value: list[A], ys: list[A]) -> Optional[list[A]]:
    pass


@DamlName("stripSuffix")
def strip_suffix(a1: list[A], b: list[A]) -> Optional[list[A]]:
    pass


@DamlName("stripInfix")
def strip_infix(a1: list[A], b: list[A]) -> Optional[tuple[list[A], list[A]]]:
    pass


@DamlName("isPrefixOf")
def is_prefix_of(list_value: list[A], list_value_1: list[A]) -> bool:
    pass


@DamlName("isSuffixOf")
def is_suffix_of(xs: list[A], ys: list[A]) -> bool:
    pass


@DamlName("isInfixOf")
def is_infix_of(needle: list[A], haystack: list[A]) -> bool:
    pass


def inits(list_value: list[A]) -> list[list[A]]:
    pass


def intersperse(sep: A, list_value: list[A]) -> list[A]:
    pass


def intercalate(xs: list[A], list_value: list[list[A]]) -> list[A]:
    pass


def tails(list_value: list[A]) -> list[list[A]]:
    pass


def transpose(list_value: list[list[A]]) -> list[list[A]]:
    pass


@DamlName("breakOn")
def break_on(needle: list[A], haystack: list[A]) -> tuple[list[A], list[A]]:
    pass


@DamlName("breakOnEnd")
def break_on_end(needle: list[A], haystack: list[A]) -> tuple[list[A], list[A]]:
    pass


def head(list_value: list[A]) -> A:
    pass


def tail(list_value: list[A]) -> list[A]:
    pass


def last(list_value: list[A]) -> A:
    pass


def init(list_value: list[A]) -> list[A]:
    pass


@DamlName("chunksOf")
def chunks_of(int_value: int, list_value: list[A]) -> list[list[A]]:
    pass


def delete(a: A, list_value: list[A]) -> list[A]:
    pass


def singleton(x: A) -> list[A]:
    pass


@DamlName("elemIndex")
def elem_index(x: A, list_value: list[A]) -> Optional[int]:
    pass
