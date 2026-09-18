
@template
class Asset:
    owner: Party
    data: complex

    signatory: list[Party] = [owner]
