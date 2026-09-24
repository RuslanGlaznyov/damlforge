from dataclasses import dataclass
from typing import Optional

from forge.models.types import Party, Text


@dataclass(frozen=True)
class InstrumentId:
    admin: Party
    id: Text


@dataclass(frozen=True)
class Account:
    owner: Optional[Party]
    provider: Optional[Party]
    id: Text


class Holding:
    pass
