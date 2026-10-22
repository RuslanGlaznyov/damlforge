from forge.models import choice, template, view, interface
from forge.builtins import DamlName

@template
class Asset:
    owner: Party
    tags: set[Party]

    signatory: list[Party] = [owner]
