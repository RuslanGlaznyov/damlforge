
flag Status:
    pending
    PAID

template Asset:
    owner: Party

    signatory: list[Party] = [owner]
