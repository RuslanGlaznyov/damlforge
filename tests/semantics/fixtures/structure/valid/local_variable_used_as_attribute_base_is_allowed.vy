from forge.models import choice, template, view, interface
from forge.builtins import DamlName

@template
class Asset:
    owner: Party
    balance: int

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def withdraw(self, amount: int) -> bool:
        other: Asset = self
        return other.balance >= amount
