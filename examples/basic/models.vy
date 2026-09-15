from forge.models import Party, choice
from forge.builtins import DamlName

template CrossTemplate:
    platform: Party
    developer: Party
    dso: Party

    signatory: list[Party] = [platform]

    def __init__(
        self,
        platform: Party,
        developer: Party,
        dso: Party
    ):
        self.platform = platform
        self.developer = developer
        self.dso = dso
    
    @DamlName("CrossTemplate_Cross")
    @choice(controller=[developer, platform], consuming=True)
    def CrossTemplate_Cross(self) -> bool:
        return false
    
    @DamlName11("CrossTemplate_Cross2")
    @choice(controller=[platform], consuming=True)
    def cross2(self) -> bool:
        return false
