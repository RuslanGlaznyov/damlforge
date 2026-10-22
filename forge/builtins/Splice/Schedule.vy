from datetime import datetime
from typing import Annotated, Generic, TypeVar

from forge.models import Optional
from forge.builtins import DamlName

A = TypeVar("A")
T = TypeVar("T")


struct Schedule(Generic[T, A]):
    initial_value: Annotated[A, DamlName("initialValue")]
    future_values: Annotated[list[tuple[T, A]], DamlName("futureValues")]


@DamlName("getValueAsOf")
def get_value_as_of(time: T, schedule: Schedule[T, A]) -> A:
    pass


@DamlName("getValueAsOfLedgerTime", is_ledger_effect=True)
def get_value_as_of_ledger_time(schedule: Schedule[datetime, A]) -> A:
    pass


@DamlName("allValues")
def all_values(schedule: Schedule[T, A]) -> list[A]:
    pass


@DamlName("nextChangeScheduledAt")
def next_change_scheduled_at(schedule: Schedule[T, A]) -> Optional[T]:
    pass


def prune(now: T, schedule: Schedule[T, A]) -> Schedule[T, A]:
    pass


@DamlName("splitAtTime")
def split_at_time(list_value: list[tuple[T, A]], t: T) -> tuple[list[tuple[T, A]], Optional[tuple[T, A]], list[tuple[T, A]]]:
    pass


def insert(item: tuple[T, A], schedule: Schedule[T, A]) -> Schedule[T, A]:
    pass


def remove(time: T, schedule: Schedule[T, A]) -> Schedule[T, A]:
    pass


def update(item: tuple[T, A], schedule: Schedule[T, A]) -> Schedule[T, A]:
    pass
