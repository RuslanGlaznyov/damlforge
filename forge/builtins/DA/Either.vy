from typing import TypeVar

from forge.models import Optional
from forge.builtins import DamlName
from DA.Types import Either

A = TypeVar("A")
B = TypeVar("B")


def lefts(x: list[Either[A, B]]) -> list[A]:
    pass


def rights(x: list[Either[A, B]]) -> list[B]:
    pass


@DamlName("partitionEithers")
def partition_eithers(list_value: list[Either[A, B]]) -> tuple[list[A], list[B]]:
    pass


@DamlName("isLeft")
def is_left(either: Either[A, B]) -> bool:
    pass


@DamlName("isRight")
def is_right(either: Either[A, B]) -> bool:
    pass


@DamlName("fromLeft")
def from_left(a: A, either: Either[A, B]) -> A:
    pass


@DamlName("fromRight")
def from_right(b: B, either: Either[A, B]) -> B:
    pass


@DamlName("optionalToEither")
def optional_to_either(l: A, optional: Optional[B]) -> Either[A, B]:
    pass


@DamlName("eitherToOptional")
def either_to_optional(either: Either[A, B]) -> Optional[B]:
    pass


@DamlName("maybeToEither")
def maybe_to_either(a: A, optional: Optional[B]) -> Either[A, B]:
    pass


@DamlName("eitherToMaybe")
def either_to_maybe(either: Either[A, B]) -> Optional[B]:
    pass
