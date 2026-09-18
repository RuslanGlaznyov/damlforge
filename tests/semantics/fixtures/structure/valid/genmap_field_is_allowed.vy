from forge.models import choice, ledger_effect, template, view, interface
from forge.builtins import DamlName

@template
class Asset:
    owner: Party
    balances: GenMap[Party, Decimal]

    signatory: list[Party] = [owner]
