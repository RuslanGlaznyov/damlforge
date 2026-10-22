from forge.models import choice, template, view, interface
from forge.builtins import DamlName

def maybe_double(value: Optional[int]) -> int:
    return 0

@template
class Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def transfer(self, new_owner: Party) -> bool:
        amount: int = 5
        doubled = maybe_double(amount)
        return doubled > 0
