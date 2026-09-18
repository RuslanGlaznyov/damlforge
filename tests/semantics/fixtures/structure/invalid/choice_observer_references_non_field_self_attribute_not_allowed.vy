
@template
class Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True, observer=self.signatory)
    def transfer(self, new_owner: Party) -> bool:
        pass
