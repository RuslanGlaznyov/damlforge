
@template
class Asset:
    owner: Party
    data: bytes

    signatory: list[Party] = [owner]
