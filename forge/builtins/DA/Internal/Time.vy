from datetime import date, datetime

from forge.builtins import DamlName


@DamlName("microsecondsPerDay")
def microseconds_per_day() -> int:
    pass


@DamlName("timeToMicrosecondsSinceEpoch")
def time_to_microseconds_since_epoch(datetime_value: datetime) -> int:
    pass


@DamlName("microsecondsSinceEpochToTime")
def microseconds_since_epoch_to_time(int_value: int) -> datetime:
    pass


def time(d: date, h: int, m: int, s: int) -> datetime:
    pass
