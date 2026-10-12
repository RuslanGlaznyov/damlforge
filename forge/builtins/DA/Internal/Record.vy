from typing import TypeVar

from forge.builtins import DamlName

A = TypeVar("A")
R = TypeVar("R")


@DamlName("getField")
def get_field(r: R) -> A:
    pass


@DamlName("setField")
def set_field(a: A, r: R) -> R:
    pass
