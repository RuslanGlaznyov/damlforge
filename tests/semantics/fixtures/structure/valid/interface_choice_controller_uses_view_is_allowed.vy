from forge.models import Party, choice

struct AssetView:
    owner: Party

interface AssetInterface(view=AssetView):
    @choice(controller=view.owner, consuming="nonconsuming")
    def ping(self) -> bool:
        pass
