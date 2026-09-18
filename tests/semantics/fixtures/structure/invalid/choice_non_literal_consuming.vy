
template Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=owner)
    def transfer(new_owner: Party) -> bool:
        pass
