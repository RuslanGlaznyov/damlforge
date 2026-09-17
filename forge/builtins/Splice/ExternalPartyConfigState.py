"""Stand-in for the real `Splice.ExternalPartyConfigState` Daml module
(`splice/daml/splice-amulet/daml/Splice/ExternalPartyConfigState.daml`) -
IDE/authoring support only, see `Splice/__init__.py`.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Annotated, Optional

from forge.models.types import Party, Timestamp
from .AmuletConfig import USD, RewardVersion, TransferConfigV2
from .Types import Round
from .. import DamlName


@dataclass(frozen=True)
class ExternalPartyConfigState:
    """The real Daml `ExternalPartyConfigState` template - config state
    snapshot for parties without a validator of their own. Real Daml
    definition:

        template ExternalPartyConfigState
          with
            dso : Party
            holdingFeesOpenRoundNumber : Round
            amuletPrice : Decimal
            transferConfig : TransferConfigV2 Unit.USD
            targetArchiveAfter : Time
            rewardCalculationVersion : Optional RewardVersion
          where
            signatory dso
    """

    dso: Party
    holding_fees_open_round_number: Annotated[Round, DamlName("holdingFeesOpenRoundNumber")]
    amulet_price: Annotated[Decimal, DamlName("amuletPrice")]
    transfer_config: Annotated[TransferConfigV2[USD], DamlName("transferConfig")]
    target_archive_after: Annotated[Timestamp, DamlName("targetArchiveAfter")]
    reward_calculation_version: Annotated[
        Optional[RewardVersion], DamlName("rewardCalculationVersion")
    ] = None
