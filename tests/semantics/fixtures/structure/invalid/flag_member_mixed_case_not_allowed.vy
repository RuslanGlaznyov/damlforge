
flag Status:
    Pending
    PAID

template Asset:
    owner: Party

    signatory: list[Party] = [owner]
