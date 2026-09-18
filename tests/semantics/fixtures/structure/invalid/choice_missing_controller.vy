
template Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @choice(consuming=True)
    def transfer(new_owner: Party) -> bool:
        pass
