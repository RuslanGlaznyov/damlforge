from forge.models import choice, ledger_effect, template, view, interface
from forge.builtins import DamlName

flag Status:
    PENDING
    PAID

@template
class Asset:
    owner: Party
    status: Status

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def mark_paid(self) -> bool:
        return self.status == Status.PENDING
