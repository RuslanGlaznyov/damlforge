
@template
class Asset:
    owner: Party
    balances: dict[Party, Decimal]

    signatory: list[Party] = [owner]
