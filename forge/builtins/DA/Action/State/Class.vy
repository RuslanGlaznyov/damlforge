from typing import TypeVar

from forge.models import ledger_effect

S = TypeVar("S")


@ledger_effect
def get() -> S:
    pass


@ledger_effect
def put(s: S) -> None:
    pass
