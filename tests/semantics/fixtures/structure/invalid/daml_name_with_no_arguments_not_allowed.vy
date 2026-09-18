
@template
class Asset:
    owner: Party
    balance: int

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    @DamlName()
    def withdraw(self, amount: int) -> bool:
        return True
