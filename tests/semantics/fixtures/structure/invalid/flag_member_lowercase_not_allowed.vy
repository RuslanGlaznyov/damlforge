
flag Status:
    pending
    PAID

@template
class Asset:
    owner: Party

    signatory: list[Party] = [owner]
