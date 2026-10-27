from forge.models import Party, choice, GenMap, view, template
from forge.builtins import DamlName
from forge.builtins.daml_lang import exercise_by_key, fetch_by_key, lookup_by_key, visible_by_key
from typing import Optional
from Splice.AmuletRules import AppTransferContext
from models import CrossTemplate
from interfaces import SimpleTemplateInterface, SimpleTemplateView


@template
class SimpleTemplate(SimpleTemplateInterface):
    platform: Party
    developer: Party
    dso: Party
    total_target: Decimal
    total_balance: Decimal
    test_balance: int
    cross_template: Optional[CrossTemplate]
    comment: str

    signatory: list[Party] = [platform]
    key: tuple[Party, str] = (platform, comment)
    maintainer: Party = key[0]
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
        cross_template: Optional[CrossTemplate],
        comment: str = "This is a simple template for testing purposes"
    ):
        assert total_target > Decimal(0), "total_target must be greater than 0"
        assert total_balance >= Decimal(0), "total_balance must be a non-negative value"
        assert test_balance > 0, "test_balance must be greater than 0"
        
        assert len(comment) <= 128

        self.platform = platform
        self.developer = developer
        self.dso = dso
        self.total_target = total_target
        self.total_balance = total_balance
        self.cross_template = cross_template
        self.comment = comment

    @view
    def get_view(self) -> SimpleTemplateView:
        return SimpleTemplateView(
            platform=self.platform,
            comment=self.comment,
        )

    @choice(controller=actors, consuming="nonconsuming")
    def interface_test(self, actors: list[Party]) -> bool:
        return True

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
    
    @DamlName("SimpleTemplate_Test")
    @choice(controller=[platform], consuming=False)
    def test(self) -> bool:
        return True

    @choice(controller=[platform], consuming=False)
    def SimpleTemplate_FindByKey(self, label: str) -> bool:
        found: Optional[ContractId[SimpleTemplate]] = lookup_by_key((self.platform, label))
        if found is None:
            return False
        pair: tuple[ContractId[SimpleTemplate], SimpleTemplate] = fetch_by_key(
            (self.platform, label)
        )
        if not visible_by_key(SimpleTemplate, (self.platform, label)):
            return False
        return pair[1].test_balance > 0 and exercise_by_key(
            SimpleTemplate, (self.platform, label), SimpleTemplate.test()
        )
