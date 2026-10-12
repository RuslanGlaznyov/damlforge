from typing import TypeVar

from forge.builtins import DamlName

A = TypeVar("A")


def dedup(list_value: list[A]) -> list[A]:
    pass


@DamlName("dedupSort")
def dedup_sort(list_value: list[A]) -> list[A]:
    pass


def sort(list_value: list[A]) -> list[A]:
    pass


def unique(list_value: list[A]) -> bool:
    pass
