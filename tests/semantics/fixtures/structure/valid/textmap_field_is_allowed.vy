
from forge.models import choice, template, view, interface
from forge.builtins import DamlName

@template
class Asset:
    owner: Party
    balances: TextMap[Decimal]

    signatory: list[Party] = [owner]
