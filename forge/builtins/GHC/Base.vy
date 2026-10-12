from typing import TypeVar


A = TypeVar("A")
B = TypeVar("B")


def otherwise() -> bool:
    pass


def const(x: A, b: B) -> A:
    pass
