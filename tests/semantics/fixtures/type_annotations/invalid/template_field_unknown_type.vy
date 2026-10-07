from forge.models import template

@template
class Asset:
    owner: TotallyBogusType

    signatory: list[Party] = [owner]
