
struct Terms:
    label: str

def sum_amounts(amounts: list[Decimal]) -> Decimal:
    return Decimal(0)

@template
class Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def transfer(self, new_owner: Party, items: list[Terms]) -> bool:
        total = sum_amounts(items)
        return total > Decimal(0)
