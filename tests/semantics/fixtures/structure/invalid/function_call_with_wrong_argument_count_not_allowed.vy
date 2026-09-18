
def add_two(a: int, b: int) -> int:
    return a + b

@template
class Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def transfer(self, new_owner: Party) -> bool:
        total = add_two(1)
        return total > 0
