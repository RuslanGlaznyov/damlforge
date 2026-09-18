
@template
class Asset:
    owner: Party
    balances: Map[Party, Decimal]

    signatory: list[Party] = [owner]
