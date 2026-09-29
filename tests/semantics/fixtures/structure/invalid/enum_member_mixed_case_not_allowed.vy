
from enum import Enum, auto

class Status(Enum):
    Pending = auto()
    PAID = auto()

@template
class Asset:
    owner: Party

    signatory: list[Party] = [owner]
