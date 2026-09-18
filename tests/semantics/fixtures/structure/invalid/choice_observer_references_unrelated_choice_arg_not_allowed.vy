
template Asset:
    owner: Party
    issuer: Party

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def transfer(new_owner: Party) -> bool:
        pass

    @choice(controller=owner, consuming=True, observer=new_owner)
    def rename(self, label: str) -> bool:
        pass
