from forge.models import choice, ledger_effect, template, view, interface
from forge.builtins import DamlName

@template
class Asset:
    owner: Party
    tags: set[Party]

    signatory: list[Party] = [owner]
