from datetime import datetime, timedelta

from forge.models import ledger_effect
from forge.builtins import DamlName


@DamlName("addRelTime")
def add_rel_time(d: datetime, rt: timedelta) -> datetime:
    pass


@DamlName("subTime")
def sub_time(d1: datetime, d2: datetime) -> timedelta:
    pass


@DamlName("wholeDays")
def whole_days(rt: timedelta) -> int:
    pass


def days(x: int) -> timedelta:
    pass


def hours(x: int) -> timedelta:
    pass


def minutes(x: int) -> timedelta:
    pass


def seconds(x: int) -> timedelta:
    pass


def milliseconds(x: int) -> timedelta:
    pass


def microseconds(x: int) -> timedelta:
    pass


@DamlName("convertRelTimeToMicroseconds")
def convert_rel_time_to_microseconds(timedelta_value: timedelta) -> int:
    pass


@DamlName("convertMicrosecondsToRelTime")
def convert_microseconds_to_rel_time(msec: int) -> timedelta:
    pass


@ledger_effect
@DamlName("isLedgerTimeLT")
def is_ledger_time_lt(v1: datetime) -> bool:
    pass


@ledger_effect
@DamlName("isLedgerTimeLE")
def is_ledger_time_le(time: datetime) -> bool:
    pass


@ledger_effect
@DamlName("isLedgerTimeGT")
def is_ledger_time_gt(time: datetime) -> bool:
    pass


@ledger_effect
@DamlName("isLedgerTimeGE")
def is_ledger_time_ge(time: datetime) -> bool:
    pass
