from forge.models import choice, template, view, interface
from forge.builtins import DamlName

@template
class Asset:
    owner: Party
    issuer: Party

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming="consuming")
    def transfer(new_owner: Party) -> bool:
        pass
