
struct HoldingView:
    owner: Party

interface Holding(view=HoldingView):
    @choice(controller=owner, consuming="preconsuming")
    def archive_holding() -> bool:
        pass
