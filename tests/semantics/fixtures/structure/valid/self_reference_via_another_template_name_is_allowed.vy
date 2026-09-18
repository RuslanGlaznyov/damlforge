from forge.models import choice, ledger_effect, template, view, interface
from forge.builtins import DamlName

@template
class Other:
    owner: Party

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def noop(self) -> bool:
        return True

@template
class Asset:
    owner: Party
    balance: int

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def withdraw(self, amount: int) -> bool:
        return self.balance >= amount
