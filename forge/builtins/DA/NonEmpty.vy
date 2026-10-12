from typing import TypeVar

from forge.models import Optional
from forge.builtins import DamlName
from DA.NonEmpty.Types import NonEmpty

A = TypeVar("A")


def cons(a1: A, ne: NonEmpty[A]) -> NonEmpty[A]:
    pass


def append(l: NonEmpty[A], r: NonEmpty[A]) -> NonEmpty[A]:
    pass


@DamlName("nonEmpty")
def non_empty(list_value: list[A]) -> Optional[NonEmpty[A]]:
    pass


def singleton(head: A) -> NonEmpty[A]:
    pass


@DamlName("toList")
def to_list(non_empty: NonEmpty[A]) -> list[A]:
    pass


def reverse(l: NonEmpty[A]) -> NonEmpty[A]:
    pass


def delete(a: A, non_empty: NonEmpty[A]) -> list[A]:
    pass
