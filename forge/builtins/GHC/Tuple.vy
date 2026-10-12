from typing import Generic, TypeVar

from forge.builtins import no_derive

A = TypeVar("A")


@no_derive
struct Unit(Generic[A]):
    _1: A
