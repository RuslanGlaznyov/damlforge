
flag Status:
    Pending
    PAID

@template
class Asset:
    owner: Party

    signatory: list[Party] = [owner]
