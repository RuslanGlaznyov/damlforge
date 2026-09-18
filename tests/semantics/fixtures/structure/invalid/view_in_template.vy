
@template
class Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @view
    def get_view() -> bool:
        pass
