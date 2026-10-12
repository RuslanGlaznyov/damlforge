from typing import TypeVar


A = TypeVar("A")


def aunit() -> A:
    pass


def negate(a: A) -> A:
    pass


def subtract(x: A, y: A) -> A:
    pass


def munit() -> A:
    pass


def signum(a: A) -> A:
    pass


def abs(a: A) -> A:
    pass


def recip(a: A) -> A:
    pass
