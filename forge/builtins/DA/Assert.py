from datetime import datetime

from forge.builtins import DamlName
from forge.models.types import Text


@DamlName("assertWithinDeadline", is_ledger_effect=True)
def assert_within_deadline(label: Text, deadline: datetime) -> None:
    raise NotImplementedError
