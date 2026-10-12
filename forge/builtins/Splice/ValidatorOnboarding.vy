from datetime import datetime
from typing import Annotated

from forge.models import choice, ContractId, Party, template, variant
from forge.builtins import DamlName, no_derive


@no_derive
@variant
class ValidatorOnboarding_ExpireResult:
    def ValidatorOnboarding_ExpireResult(): pass


@no_derive
struct ValidatorOnboarding_MatchResult:
    used_secret: Annotated[ContractId[UsedSecret], DamlName("usedSecret")]


@template
class ValidatorOnboarding:
    sv: Party
    candidate_secret: Annotated[str, DamlName("candidateSecret")]
    expires_at: Annotated[datetime, DamlName("expiresAt")]

    signatory: list[Party] = [sv]

    @choice(controller=sv, consuming=True)
    def ValidatorOnboarding_Match(self, provided_secret: Annotated[str, DamlName("providedSecret")], validator: Party) -> ValidatorOnboarding_MatchResult:
        pass

    @choice(controller=sv, consuming=True)
    def ValidatorOnboarding_Expire(self) -> ValidatorOnboarding_ExpireResult:
        pass


@template
class UsedSecret:
    sv: Party
    secret: str
    validator: Party

    signatory: list[Party] = [sv]
