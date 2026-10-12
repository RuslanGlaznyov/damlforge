from datetime import datetime
from typing import Annotated

from forge.models import Party, template
from forge.builtins import DamlName


@template
class ValidatorTopUpState:
    dso: Party
    validator: Party
    member_id: Annotated[str, DamlName("memberId")]
    synchronizer_id: Annotated[str, DamlName("synchronizerId")]
    migration_id: Annotated[int, DamlName("migrationId")]
    last_purchased_at: Annotated[datetime, DamlName("lastPurchasedAt")]

    signatory: list[Party] = [validator]


@DamlName("initialValidatorTopUpState")
def initial_validator_top_up_state(party: Party, validator: Party, member_id: str, synchronizer_id: str) -> ValidatorTopUpState:
    pass
