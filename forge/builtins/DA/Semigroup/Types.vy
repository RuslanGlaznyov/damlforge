from typing import Generic, TypeVar

from forge.builtins import no_derive

A = TypeVar("A")


@no_derive
struct Min(Generic[A]):
    unpack: A


@no_derive
struct Max(Generic[A]):
    unpack: A
