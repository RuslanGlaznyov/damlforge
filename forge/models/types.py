from typing import Generic, NewType, TypeVar

Party = NewType("Party", str)
Text = NewType("Text", str)
Int = NewType("Int", int)
Date = NewType("Date", str)
Timestamp = NewType("Timestamp", str)
RelTime = NewType("RelTime", str)

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


class ContractId(Generic[T]):
    pass


class TextMap(Generic[T]):
    pass


class GenMap(Generic[K, V]):
    pass
