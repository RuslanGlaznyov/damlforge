from forge.models import choice, ledger_effect, template, view, interface
from forge.builtins import DamlName

struct Terms:
    label: Text

@template
class Asset:
    owner: Party
    balance: int

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def withdraw(self, amount: int) -> bool:
        terms = Terms(label="ok")
        rounded = ceil(Decimal(amount))
        return len(terms.label) > 0 and rounded > 0
