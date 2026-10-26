from forge.models import ContractId, Party, choice, template

@template
class Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def give(self, new_owner: Party) -> ContractId[Asset]:
        return create(Asset(owner=new_owner))
