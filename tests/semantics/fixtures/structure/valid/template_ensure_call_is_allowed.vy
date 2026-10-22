
from forge.models import choice, template, view, interface
from forge.builtins import DamlName

@template
class Asset:
    owner: Party
    amount: Decimal

    signatory: list[Party] = [owner]
    ensure: bool = is_valid(amount)
