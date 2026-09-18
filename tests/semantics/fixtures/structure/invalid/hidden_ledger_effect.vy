
template Asset:
    owner: Party

    signatory: list[Party] = [owner]

    def replace(new_owner: Party) -> bool:
        archive(self)
