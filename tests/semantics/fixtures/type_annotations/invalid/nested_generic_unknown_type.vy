
from forge.models import template

@template
class Asset:
    owner: Party
    holdings: list[ContractId[NotARealHolding]]

    signatory: list[Party] = [owner]
