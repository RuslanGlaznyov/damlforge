from typing import TypeVar

from forge.models import Optional, TextMap
from forge.builtins import DamlName

A = TypeVar("A")
V = TypeVar("V")


@DamlName("fromList")
def from_list(list_value: list[tuple[str, A]]) -> TextMap[A]:
    pass


@DamlName("toList")
def to_list(text_map: TextMap[A]) -> list[tuple[str, A]]:
    pass


def empty() -> TextMap[A]:
    pass


def size(text_map: TextMap[A]) -> int:
    pass


def null(m: TextMap[V]) -> bool:
    pass


def lookup(str_value: str, text_map: TextMap[A]) -> Optional[A]:
    pass


def member(x: str, m: TextMap[V]) -> bool:
    pass


def delete(str_value: str, text_map: TextMap[A]) -> TextMap[A]:
    pass


def singleton(k: str, v: A) -> TextMap[A]:
    pass


def insert(str_value: str, a: A, text_map: TextMap[A]) -> TextMap[A]:
    pass


def union(m1: TextMap[A], m2: TextMap[A]) -> TextMap[A]:
    pass
