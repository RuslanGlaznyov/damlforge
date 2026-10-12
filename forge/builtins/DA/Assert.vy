from datetime import datetime
from typing import TypeVar

from forge.models import ledger_effect
from forge.builtins import DamlName

A = TypeVar("A")


@ledger_effect
@DamlName("assertEq")
def assert_eq(a: A, a_1: A) -> None:
    pass


@ledger_effect
@DamlName("assertNotEq")
def assert_not_eq(a: A, a_1: A) -> None:
    pass


@ledger_effect
@DamlName("assertAfterMsg")
def assert_after_msg(str_value: str, datetime_value: datetime) -> None:
    pass


@ledger_effect
@DamlName("assertBeforeMsg")
def assert_before_msg(str_value: str, datetime_value: datetime) -> None:
    pass


@ledger_effect
@DamlName("assertWithinDeadline")
def assert_within_deadline(str_value: str, datetime_value: datetime) -> None:
    pass


@ledger_effect
@DamlName("assertDeadlineExceeded")
def assert_deadline_exceeded(str_value: str, datetime_value: datetime) -> None:
    pass
