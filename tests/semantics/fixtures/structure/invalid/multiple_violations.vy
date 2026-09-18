

from forge.models import choice

@template
class Asset:
    owner: Party

    @choice(consuming=True)
    def transfer(new_owner: Party) -> bool:
        pass
