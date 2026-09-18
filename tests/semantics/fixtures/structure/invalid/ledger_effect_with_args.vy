
@template
class Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @ledger_effect(True)
    def replace(new_owner: Party) -> bool:
        pass
