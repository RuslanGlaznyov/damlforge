from forge.models.types import Text, Timestamp
from forge.builtins import DamlName


@DamlName("assertWithinDeadline", is_ledger_effect=True)
def assert_within_deadline(label: Text, deadline: Timestamp) -> None:
    raise NotImplementedError
