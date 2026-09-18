
@template
class Asset:
    owner: Party
    balance: int

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def withdraw(self, amount: int) -> bool:
        return some_undeclared_function(amount) > 0
