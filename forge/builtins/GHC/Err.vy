from typing import TypeVar

from forge.builtins import DamlName

A = TypeVar("A")


@DamlName("error")
def error_(msg: str) -> A:
    pass
