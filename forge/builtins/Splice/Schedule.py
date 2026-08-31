"""Stand-in for the real `Splice.Schedule` Daml module
(`splice/daml/splice-amulet/daml/Splice/Schedule.daml`) - IDE/authoring
support only, see `Splice/__init__.py`.
"""

from dataclasses import dataclass
from typing import Annotated, Generic, TypeVar
from .. import DamlName

T = TypeVar("T")
A = TypeVar("A")


@dataclass(frozen=True)
class Schedule(Generic[T, A]):
    """The real Daml `Schedule t a` record - a value that changes at known
    future points in time. Real Daml definition:

        data Schedule t a = Schedule with
            initialValue : a
            futureValues : [(t, a)]
          deriving (Eq, Show)
    """

    initial_value: Annotated[A, DamlName("initialValue")]
    future_values: Annotated[list[tuple[T, A]], DamlName("futureValues")]
