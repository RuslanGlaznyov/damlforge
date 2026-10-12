from typing import TypeVar

from forge.models import Optional

A = TypeVar("A")


def head(list_value: list[A]) -> Optional[A]:
    pass


def tail(list_value: list[A]) -> Optional[list[A]]:
    pass


def last(list_value: list[A]) -> Optional[A]:
    pass


def init(list_value: list[A]) -> Optional[list[A]]:
    pass
