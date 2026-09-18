
struct HoldingView:
    owner: Party

interface Holding(view=HoldingView):
    @view(True)
    def get_view() -> bool:
        pass
