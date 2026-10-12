from typing import TypeVar

from forge.builtins import DamlName

E = TypeVar("E")


DamlException = None


def message(e: E) -> str:
    pass
