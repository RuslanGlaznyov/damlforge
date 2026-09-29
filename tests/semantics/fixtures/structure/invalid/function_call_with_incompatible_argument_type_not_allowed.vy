
def sum_amounts(amounts: list[Decimal]) -> Decimal:
    return Decimal(0)

@template
class Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def transfer(self, new_owner: Party) -> bool:
        value: bool = True
        total = sum_amounts(value)
        return total > Decimal(0)
