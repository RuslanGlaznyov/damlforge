
def sum_amounts(amounts: list[Decimal]) -> Decimal:
    return Decimal(0)

template Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def transfer(self, new_owner: Party) -> bool:
        flag: bool = True
        total = sum_amounts(flag)
        return total > Decimal(0)
