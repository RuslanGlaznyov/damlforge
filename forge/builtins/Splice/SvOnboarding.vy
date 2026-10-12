from datetime import datetime
from typing import Annotated

from forge.models import choice, Party, template, variant
from forge.builtins import DamlName, no_derive


@no_derive
@variant
class SvOnboardingConfirmed_ExpireResult:
    def SvOnboardingConfirmed_ExpireResult(): pass


@no_derive
@variant
class SvOnboardingRequest_ExpireResult:
    def SvOnboardingRequest_ExpireResult(): pass


@template
class SvOnboardingRequest:
    candidate_name: Annotated[str, DamlName("candidateName")]
    candidate_party: Annotated[Party, DamlName("candidateParty")]
    candidate_participant_id: Annotated[str, DamlName("candidateParticipantId")]
    token: str
    sponsor: Party
    dso: Party
    expires_at: Annotated[datetime, DamlName("expiresAt")]

    signatory: list[Party] = [dso]
    observer: list[Party] = [candidate_party]

    @choice(controller=dso, consuming=True)
    def SvOnboardingRequest_Expire(self) -> SvOnboardingRequest_ExpireResult:
        pass


@template
class SvOnboardingConfirmed:
    sv_party: Annotated[Party, DamlName("svParty")]
    sv_name: Annotated[str, DamlName("svName")]
    sv_reward_weight: Annotated[int, DamlName("svRewardWeight")]
    sv_participant_id: Annotated[str, DamlName("svParticipantId")]
    reason: str
    dso: Party
    expires_at: Annotated[datetime, DamlName("expiresAt")]

    signatory: list[Party] = [dso]
    observer: list[Party] = [sv_party]

    @choice(controller=dso, consuming=True)
    def SvOnboardingConfirmed_Expire(self) -> SvOnboardingConfirmed_ExpireResult:
        pass
