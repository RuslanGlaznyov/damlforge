from typing import Generic, TypeVar

from forge.builtins import no_derive

A = TypeVar("A")


@no_derive
struct NonEmpty(Generic[A]):
    hd: A
    tl: list[A]
