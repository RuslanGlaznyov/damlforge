from forge.models import choice, template, view, interface
from forge.builtins import DamlName

@template
class Asset:
    owner: Party
    balance: int

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    @DamlName("Asset_Withdraw")
    def withdraw(self, amount: int) -> bool:
        return True
