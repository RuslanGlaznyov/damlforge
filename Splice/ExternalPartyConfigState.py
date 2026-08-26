"""Stand-in for the real `Splice.ExternalPartyConfigState` Daml module
(`splice/daml/splice-amulet/daml/Splice/ExternalPartyConfigState.daml`) -
IDE/authoring support only, see `Splice/__init__.py`.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from forge.models.types import Party, Timestamp
from Splice.AmuletConfig import USD, RewardVersion, TransferConfigV2
from Splice.Types import Round


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
    holding_fees_open_round_number: Round
    amulet_price: Decimal
    transfer_config: TransferConfigV2[USD]
    target_archive_after: Timestamp
    reward_calculation_version: Optional[RewardVersion] = None
