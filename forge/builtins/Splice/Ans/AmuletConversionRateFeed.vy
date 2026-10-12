from datetime import datetime
from typing import Annotated

from forge.models import choice, ContractId, Decimal, Optional, Party, template, variant
from forge.builtins import DamlName, no_derive
from Splice.AmuletRules import AmuletRules
from Splice.Api.FeaturedAppRightV1 import AppRewardBeneficiary, FeaturedAppRight


@no_derive
@variant
class AmuletConversionRateFeed_ArchiveAsDsoResult:
    def AmuletConversionRateFeed_ArchiveAsDsoResult(): pass


struct MarkerContext:
    featured_app_right_cid: Annotated[ContractId[FeaturedAppRight], DamlName("featuredAppRightCid")]
    beneficiaries: list[AppRewardBeneficiary]


@no_derive
struct AmuletConversionRateFeed_UpdateResult:
    cid: ContractId[AmuletConversionRateFeed]


@template
class AmuletConversionRateFeed:
    publisher: Party
    dso: Party
    next_update_after: Annotated[Optional[datetime], DamlName("nextUpdateAfter")]
    amulet_conversion_rate: Annotated[Decimal, DamlName("amuletConversionRate")]

    signatory: list[Party] = [publisher]
    observer: list[Party] = [dso]

    @choice(controller=dso, consuming=True)
    def AmuletConversionRateFeed_ArchiveAsDso(self, reason: str) -> AmuletConversionRateFeed_ArchiveAsDsoResult:
        pass

    @choice(controller=publisher, consuming=True)
    def AmuletConversionRateFeed_Update(self, amulet_conversion_rate: Annotated[Decimal, DamlName("amuletConversionRate")], amulet_rules_cid: Annotated[ContractId[AmuletRules], DamlName("amuletRulesCid")], marker_context_o: Annotated[Optional[MarkerContext], DamlName("markerContextO")], new_next_update_after: Annotated[datetime, DamlName("newNextUpdateAfter")]) -> AmuletConversionRateFeed_UpdateResult:
        pass
