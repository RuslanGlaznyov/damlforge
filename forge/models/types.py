from typing import Generic, NewType, TypeVar

from forge.builtins.maps import GenMap, TextMap

__all__ = (
    "GenMap",
    "TextMap",
    "Party",
    "Text",
    "Int",
    "Date",
    "Timestamp",
    "RelTime",
    "ContractId",
)

Party = NewType("Party", str)
Text = NewType("Text", str)
Int = NewType("Int", int)
Date = NewType("Date", str)
Timestamp = NewType("Timestamp", str)
RelTime = NewType("RelTime", str)

T = TypeVar("T")


class ContractId(Generic[T]):
    pass
