from forge.models import ContractId, Party, template, view

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

def as_holding(cid: ContractId[Coin]) -> ContractId[Holding]:
    return to_interface_contract_id(cid)
