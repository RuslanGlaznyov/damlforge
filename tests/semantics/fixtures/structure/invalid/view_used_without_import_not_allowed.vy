from forge.models import choice

struct AssetView:
    owner: Party

interface AssetInterface(view=AssetView):
    pass

@template
class Asset(AssetInterface):
    owner: Party

    signatory: list[Party] = [owner]

    @view
    def get_view(self) -> AssetView:
        return AssetView(owner=self.owner)
