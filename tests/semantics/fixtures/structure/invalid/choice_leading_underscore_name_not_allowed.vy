
@template
class Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def _mint(self) -> bool:
        return True
