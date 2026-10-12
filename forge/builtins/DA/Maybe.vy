from typing import TypeVar

from forge.models import Optional
from forge.builtins import DamlName

A = TypeVar("A")


@DamlName("fromJust")
def from_just(optional: Optional[A]) -> A:
    pass


@DamlName("fromJustNote")
def from_just_note(str_value: str, optional: Optional[A]) -> A:
    pass


@DamlName("catMaybes")
def cat_maybes(list_value: list[Optional[A]]) -> list[A]:
    pass


@DamlName("listToMaybe")
def list_to_maybe(list_value: list[A]) -> Optional[A]:
    pass


@DamlName("maybeToList")
def maybe_to_list(optional: Optional[A]) -> list[A]:
    pass


@DamlName("fromMaybe")
def from_maybe(a: A, optional: Optional[A]) -> A:
    pass


@DamlName("isJust")
def is_just(optional: Optional[A]) -> bool:
    pass


@DamlName("isNothing")
def is_nothing(optional: Optional[A]) -> bool:
    pass
