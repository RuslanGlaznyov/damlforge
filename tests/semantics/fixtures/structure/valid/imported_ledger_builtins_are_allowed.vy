from forge.builtins.daml_lang import archive, create, exercise, fetch, to_interface_contract_id
from forge.models import ContractId, Party, choice, template, view

struct HoldingView:
    owner: Party

interface Holding(view=HoldingView):
    pass

@template
class Coin(Holding):
    owner: Party

    signatory: list[Party] = [owner]

    @view
    def get_view(self) -> HoldingView:
        return HoldingView(owner=self.owner)

    @choice(controller=owner, consuming=True)
    def give(self, new_owner: Party) -> ContractId[Coin]:
        return create(Coin(owner=new_owner))

    @choice(controller=owner, consuming=False)
    def burn(self, cid: ContractId[Coin]) -> bool:
        archive(cid)
        return True

def as_holding(cid: ContractId[Coin]) -> ContractId[Holding]:
    return to_interface_contract_id(cid)

def owner_of(cid: ContractId[Coin]) -> Party:
    coin = fetch(cid)
    return coin.owner

def pass_on(cid: ContractId[Coin], new_owner: Party) -> ContractId[Coin]:
    return exercise(cid, cid.give(new_owner=new_owner))
