from typing import TypeVar


S = TypeVar("S")


@DamlName("get", is_ledger_effect=True)
def get() -> S:
    pass


@DamlName("put", is_ledger_effect=True)
def put(s: S) -> None:
    pass
