
@template
class RecursionTemplate:
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
    
    @choice(controller=[developer, platform], consuming=True)
    def recursion(self) -> bool:
        return self.recursion()
