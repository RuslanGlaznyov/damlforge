from typing import TypeVar

from forge.models import GenMap, Optional
from forge.builtins import DamlName

K = TypeVar("K")
V = TypeVar("V")


@DamlName("fromList")
def from_list(list_value: list[tuple[K, V]]) -> GenMap[K, V]:
    pass


def keys(gen_map: GenMap[K, V]) -> list[K]:
    pass


def values(gen_map: GenMap[K, V]) -> list[V]:
    pass


@DamlName("toList")
def to_list(x: GenMap[K, V]) -> list[tuple[K, V]]:
    pass


def empty() -> GenMap[K, V]:
    pass


def size(gen_map: GenMap[K, V]) -> int:
    pass


def null(m: GenMap[K, V]) -> bool:
    pass


def lookup(k: K, gen_map: GenMap[K, V]) -> Optional[V]:
    pass


def member(x: K, m: GenMap[K, V]) -> bool:
    pass


def delete(k: K, gen_map: GenMap[K, V]) -> GenMap[K, V]:
    pass


def singleton(k1: K, v1: V) -> GenMap[K, V]:
    pass


def insert(k: K, v: V, gen_map: GenMap[K, V]) -> GenMap[K, V]:
    pass


def union(m1: GenMap[K, V], m2: GenMap[K, V]) -> GenMap[K, V]:
    pass
