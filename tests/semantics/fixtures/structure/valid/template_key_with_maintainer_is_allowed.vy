
from forge.models import choice, template, view, interface
from forge.builtins import DamlName

@template
class Asset:
    owner: Party
    asset_id: Text

    signatory: list[Party] = [owner]
    key: tuple[Party, Text] = (owner, asset_id)
    maintainer: list[Party] = [owner]
