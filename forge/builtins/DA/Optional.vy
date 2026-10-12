from typing import TypeVar

from forge.models import Optional
from forge.builtins import DamlName

A = TypeVar("A")


@DamlName("fromSome")
def from_some(optional: Optional[A]) -> A:
    pass


@DamlName("fromSomeNote")
def from_some_note(str_value: str, optional: Optional[A]) -> A:
    pass


@DamlName("catOptionals")
def cat_optionals(list_value: list[Optional[A]]) -> list[A]:
    pass


@DamlName("listToOptional")
def list_to_optional(list_value: list[A]) -> Optional[A]:
    pass


@DamlName("optionalToList")
def optional_to_list(optional: Optional[A]) -> list[A]:
    pass


@DamlName("fromOptional")
def from_optional(d: A, x: Optional[A]) -> A:
    pass


@DamlName("isSome")
def is_some(optional: Optional[A]) -> bool:
    pass


@DamlName("isNone")
def is_none(optional: Optional[A]) -> bool:
    pass
