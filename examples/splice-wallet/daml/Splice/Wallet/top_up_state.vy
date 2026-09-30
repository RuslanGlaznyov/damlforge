from datetime import date, datetime, time

from forge.builtins import DamlName
from forge.models import Party, checked_fetch, template
from Splice.DecentralizedSynchronizer import ForMemberTraffic


@DamlName("initialValidatorTopUpState")
def initial_validator_top_up_state(
    dso: Party, validator: Party, memberId: str, synchronizerId: str
) -> ValidatorTopUpState:
    return ValidatorTopUpState(
        dso=dso,
        validator=validator,
        memberId=memberId,
        synchronizerId=synchronizerId,
        migrationId=0,
        lastPurchasedAt=datetime.combine(date(1, 1, 1), time()),
    )


@template
class ValidatorTopUpState:
    dso: Party
    validator: Party
    memberId: str
    synchronizerId: str
    migrationId: int
    lastPurchasedAt: datetime

    signatory: Party = validator

    @checked_fetch
    def contract_group_id(self) -> ForMemberTraffic:
        return ForMemberTraffic(
            dso=self.dso,
            member_id=self.memberId,
            synchronizer_id=self.synchronizerId,
            migration_id=self.migrationId,
        )
