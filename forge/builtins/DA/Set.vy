from typing import TypeVar

from forge.models import GenMap
from forge.builtins import DamlName

K = TypeVar("K")


def empty() -> set[K]:
    pass


def size(set_value: set[K]) -> int:
    pass


@DamlName("toList")
def to_list(set_value: set[K]) -> list[K]:
    pass


@DamlName("fromList")
def from_list(ks: list[K]) -> set[K]:
    pass


@DamlName("toMap")
def to_map(set_value: set[K]) -> GenMap[K, None]:
    pass


@DamlName("fromMap")
def from_map(gen_map: GenMap[K, None]) -> set[K]:
    pass


def member(k1: K, set_value: set[K]) -> bool:
    pass


@DamlName("notMember")
def not_member(k1: K, s: set[K]) -> bool:
    pass


def null(set_value: set[K]) -> bool:
    pass


def insert(k1: K, set_value: set[K]) -> set[K]:
    pass


def delete(k1: K, set_value: set[K]) -> set[K]:
    pass


def singleton(k1: K) -> set[K]:
    pass


def union(set_value: set[K], set_value_1: set[K]) -> set[K]:
    pass


def intersection(s1: set[K], s2: set[K]) -> set[K]:
    pass


def difference(s1: set[K], s2: set[K]) -> set[K]:
    pass


@DamlName("isSubsetOf")
def is_subset_of(a: set[K], b: set[K]) -> bool:
    pass


@DamlName("isProperSubsetOf")
def is_proper_subset_of(set_value: set[K], set_value_1: set[K]) -> bool:
    pass
