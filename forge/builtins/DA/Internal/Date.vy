from datetime import date

from forge.builtins import DamlName


@DamlName("daysSinceEpochToDate")
def days_since_epoch_to_date(int_value: int) -> date:
    pass


@DamlName("dateToDaysSinceEpoch")
def date_to_days_since_epoch(date_value: date) -> int:
    pass
