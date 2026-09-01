from forge.models import Party, choice, GenMap
from typing import Optional
from Splice.AmuletRules import AppTransferContext
from models import CrossTemplate

template SimpleTemplate:
    platform: Party
    developer: Party
    dso: Party
    total_target: Decimal
    total_balance: Decimal
    test_balance: int
    cross_template: Optional[CrossTemplate]

    signatory: list[Party] = [platform]
    mint_receiver: list[Party] = [platform, developer, dso]
    mint_balances: GenMap[Party, Decimal] = {platform: Decimal(0), developer: Decimal(0), dso: Decimal(0)}

    def __init__(
        self,
        platform: Party,
        developer: Party,
        dso: Party,
        total_target: Decimal,
        total_balance: Decimal,
        test_balance: int,
        cross_template: Optional[CrossTemplate]
    ):
        ensure (total_target > Decimal(0) and total_balance >= Decimal(0))
        assert total_target > Decimal(0), "total_target must be greater than 0"
        assert total_balance >= Decimal(0), "total_balance must be a non-negative value"
        assert test_balance > 0, "test_balance must be greater than 0"

        self.platform = platform
        self.developer = developer
        self.dso = dso
        self.total_target = total_target
        self.total_balance = total_balance
        self.cross_template = cross_template

    @choice(controller=[developer, platform], consuming=True)
    def SimpleTemplate_Mint(self) -> ContractId[SimpleTemplate]:
        self.total_target = self.total_target + Decimal(1)
        self.total_balance = self.total_balance - Decimal(1)

        for party:Party in self.mint_receiver:
            if party in self.mint_balances:
                self.mint_balances[party] = self.mint_balances[party] + Decimal(1)
            else:
                self.mint_balances[party] = Decimal(1)

        return True
    
    @choice(controller=[platform], consuming=False)
    def SimpleTemplate_CreateAppMarkers(
        self, 
        beneficiary: list[Party], 
        amount: int,
        app_transfer_context : AppTransferContext) -> bool:
        
        if self.cross_template is not None:
            self.cross_template.CrossTemplate_Cross()
        return True