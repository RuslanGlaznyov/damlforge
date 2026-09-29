from enum import Enum, auto
from forge.models import choice, ledger_effect, template, view, interface
from forge.builtins import DamlName

class Status(Enum):
    PENDING = auto()
    PAID = auto()

@template
class Asset:
    owner: Party
    status: Status

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def mark_paid(self) -> bool:
        return self.status == Status.PENDING
