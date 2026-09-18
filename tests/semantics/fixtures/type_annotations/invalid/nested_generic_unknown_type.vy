
@template
class Asset:
    owner: Party
    holdings: list[ContractId[NotARealHolding]]

    signatory: list[Party] = [owner]
