from datetime import datetime
from typing import TypeVar

from forge.builtins import DamlName

A = TypeVar("A")


@DamlName("assertEq", is_ledger_effect=True)
def assert_eq(a: A, a_1: A) -> None:
    pass


@DamlName("assertNotEq", is_ledger_effect=True)
def assert_not_eq(a: A, a_1: A) -> None:
    pass


@DamlName("assertAfterMsg", is_ledger_effect=True)
def assert_after_msg(str_value: str, datetime_value: datetime) -> None:
    pass


@DamlName("assertBeforeMsg", is_ledger_effect=True)
def assert_before_msg(str_value: str, datetime_value: datetime) -> None:
    pass


@DamlName("assertWithinDeadline", is_ledger_effect=True)
def assert_within_deadline(str_value: str, datetime_value: datetime) -> None:
    pass


@DamlName("assertDeadlineExceeded", is_ledger_effect=True)
def assert_deadline_exceeded(str_value: str, datetime_value: datetime) -> None:
    pass
