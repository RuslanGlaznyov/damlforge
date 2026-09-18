
@template
class Asset:
    owner: Party
    asset_id: Text

    signatory: list[Party] = [owner]
    maintainer: list[Party] = [owner]
