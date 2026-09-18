
from forge.models import choice, ledger_effect, template, view, interface
from forge.builtins import DamlName

@template
class Asset:
    owner: Party

    @choice(controller=owner, consuming=True)
    def transfer(new_owner: Party) -> bool:
        pass
