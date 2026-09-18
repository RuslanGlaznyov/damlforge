
struct HoldingView:
    owner: Party

interface Holding(view=HoldingView):
    @choice(controller=owner, consuming="postconsuming")
    def archive_holding() -> bool:
        pass

@template
class Asset(Holding):
    owner: Party

    signatory: list[Party] = [owner]

    @view
    def get_view() -> HoldingView:
        pass

    @choice(controller=owner, consuming="postconsuming")
    def archive_holding() -> bool:
        pass
