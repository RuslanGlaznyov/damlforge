from datetime import datetime
from typing import TypeVar

from forge.models import ContractId, Optional, Party
from forge.builtins import DamlName

A = TypeVar("A")
B = TypeVar("B")


@DamlName("partyToText")
def party_to_text(party: Party) -> str:
    pass


@DamlName("partyFromText")
def party_from_text(str_value: str) -> Optional[Party]:
    pass


@DamlName("coerceContractId")
def coerce_contract_id(contract_id: ContractId[A]) -> ContractId[B]:
    pass


@DamlName("getTime", is_ledger_effect=True)
def get_time() -> datetime:
    pass
