from datetime import datetime

from forge.models import ledger_effect
from forge.builtins import DamlName


@ledger_effect
@DamlName("assert")
def assert_(bool_value: bool) -> None:
    pass


@ledger_effect
@DamlName("assertMsg")
def assert_msg(str_value: str, bool_value: bool) -> None:
    pass


@ledger_effect
@DamlName("assertAfter")
def assert_after(datetime_value: datetime) -> None:
    pass


@ledger_effect
@DamlName("assertBefore")
def assert_before(datetime_value: datetime) -> None:
    pass
