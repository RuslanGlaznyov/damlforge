from datetime import datetime
from typing import Annotated

from forge.models import Decimal, Optional, Party, template, TextMap
from forge.builtins import DamlName
from Splice.AmuletConfig import RewardVersion, TransferConfigV2, USD
from Splice.Types import Round


@template
class ExternalPartyConfigState:
    dso: Party
    holding_fees_open_round_number: Annotated[Round, DamlName("holdingFeesOpenRoundNumber")]
    amulet_price: Annotated[Decimal, DamlName("amuletPrice")]
    transfer_config: Annotated[TransferConfigV2[USD], DamlName("transferConfig")]
    target_archive_after: Annotated[datetime, DamlName("targetArchiveAfter")]
    reward_calculation_version: Annotated[Optional[RewardVersion], DamlName("rewardCalculationVersion")]
    amulet_switch_over_times: Annotated[Optional[TextMap[datetime]], DamlName("amuletSwitchOverTimes")]

    signatory: list[Party] = [dso]
