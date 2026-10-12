from typing import Generic, TypeVar

from forge.builtins import no_derive

A = TypeVar("A")


@no_derive
struct Down(Generic[A]):
    unpack: A
