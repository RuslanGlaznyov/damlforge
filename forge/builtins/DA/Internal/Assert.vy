from datetime import datetime

from forge.builtins import DamlName


@DamlName("assert", is_ledger_effect=True)
def assert_(bool_value: bool) -> None:
    pass


@DamlName("assertMsg", is_ledger_effect=True)
def assert_msg(str_value: str, bool_value: bool) -> None:
    pass


@DamlName("assertAfter", is_ledger_effect=True)
def assert_after(datetime_value: datetime) -> None:
    pass


@DamlName("assertBefore", is_ledger_effect=True)
def assert_before(datetime_value: datetime) -> None:
    pass
