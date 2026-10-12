from typing import TypeVar


A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


def swap(tuple_value: tuple[A, B]) -> tuple[B, A]:
    pass


def dupe(x: A) -> tuple[A, A]:
    pass


def fst3(tuple_value: tuple[A, B, C]) -> A:
    pass


def snd3(tuple_value: tuple[A, B, C]) -> B:
    pass


def thd3(tuple_value: tuple[A, B, C]) -> C:
    pass
