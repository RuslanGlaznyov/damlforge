from typing import Generic, NewType, TypeVar

from forge.builtins.maps import GenMap, TextMap

__all__ = (
    "GenMap",
    "TextMap",
    "Party",
    "Text",
    "Int",
    "ContractId",
)

Party = NewType("Party", str)
Text = NewType("Text", str)
Int = NewType("Int", int)

T = TypeVar("T")


class ContractId(Generic[T]):
    pass
