
template Asset:
    owner: Party
    amount: Decimal

    signatory: list[Party] = [owner]
    ensure: Decimal = amount
