
@template
class Asset:
    owner: Party
    asset_id: Text

    signatory: list[Party] = [owner]
    key: tuple[Party, Text] = (owner, asset_id)
