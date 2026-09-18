
template Asset:
    owner: Party

    signatory: list[Party] = [owner]
    ensure: bool
