from datetime import date, datetime

from forge.builtins import DamlName
from DA.Date.Types import DayOfWeek, Month


@DamlName("fromEnumOffset")
def from_enum_offset() -> int:
    pass


@DamlName("addDays")
def add_days(d: date, r: int) -> date:
    pass


@DamlName("subtractDays")
def subtract_days(d: date, r: int) -> date:
    pass


@DamlName("subDate")
def sub_date(d1: date, d2: date) -> int:
    pass


@DamlName("dayOfWeek")
def day_of_week(d: date) -> DayOfWeek:
    pass


@DamlName("fromGregorian")
def from_gregorian(tuple_value: tuple[int, Month, int]) -> date:
    pass


@DamlName("toGregorian")
def to_gregorian(date1: date) -> tuple[int, Month, int]:
    pass


def date(int_value: int, month: Month, int_value_2: int) -> date:
    pass


@DamlName("isLeapYear")
def is_leap_year(year: int) -> bool:
    pass


@DamlName("fromMonth")
def from_month(m: Month) -> int:
    pass


@DamlName("monthDayCount")
def month_day_count(year: int, month: Month) -> int:
    pass


def datetime(year: int, month: Month, day: int, h: int, m: int, s: int) -> datetime:
    pass


@DamlName("toDateUTC")
def to_date_utc(t: datetime) -> date:
    pass
