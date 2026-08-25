from forge.models import Party, choice, GenMap

template SimpleTemplate:
    platform: Party
    developer: Party
    dso: Party
    total_target: Decimal
    total_balance: Decimal

    signatory: list[Party] = [platform]
    mint_receiver: list[Party] = [platform, developer, dso]
    mint_balances: GenMap[Party, Decimal] = {platform: Decimal(0), developer: Decimal(0), dso: Decimal(0)}

    def __init__(
        self,
        platform: Party,
        developer: Party,
        dso: Party,
        total_target: Decimal,
        total_balance: Decimal
    ):
        ensure (total_target > Decimal(0) and total_balance >= Decimal(0))

        self.platform = platform
        self.developer = developer
        self.dso = dso
        self.total_target = total_target
        self.total_balance = total_balance

    @choice(controller=[developer, platform], consuming=True)
    def mint(self) -> bool:
        self.total_target = self.total_target + Decimal(1)
        self.total_balance = self.total_balance - Decimal(1)

        for party:Party in self.mint_receiver:
            if party in self.mint_balances:
                self.mint_balances[party] = self.mint_balances[party] + Decimal(1)
            else:
                self.mint_balances[party] = Decimal(1)

        return True
            