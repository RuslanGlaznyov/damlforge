from datetime import datetime
from typing import Annotated

from forge.models import GenMap, Optional, Party, template
from forge.builtins import DamlName
from Splice.DSO.DecentralizedSynchronizer import SynchronizerNodeConfig
from Splice.Types import Round


struct ForSv:
    dso: Party
    sv_name: Annotated[str, DamlName("svName")]


struct ForSvNode:
    dso: Party
    sv: Party
    sv_name: Annotated[str, DamlName("svName")]


struct RewardState:
    num_rounds_missed: Annotated[int, DamlName("numRoundsMissed")]
    num_rounds_collected: Annotated[int, DamlName("numRoundsCollected")]
    last_round_collected: Annotated[Round, DamlName("lastRoundCollected")]
    num_coupons_issued: Annotated[int, DamlName("numCouponsIssued")]


struct NodeState:
    synchronizer_nodes: Annotated[GenMap[str, SynchronizerNodeConfig], DamlName("synchronizerNodes")]


struct SvStatus:
    created_at: Annotated[datetime, DamlName("createdAt")]
    comet_bft_height: Annotated[int, DamlName("cometBftHeight")]
    mediator_synchronizer_time: Annotated[datetime, DamlName("mediatorSynchronizerTime")]
    participant_synchronizer_time: Annotated[datetime, DamlName("participantSynchronizerTime")]
    latest_open_round: Annotated[Round, DamlName("latestOpenRound")]


@template
class SvRewardState:
    dso: Party
    sv_name: Annotated[str, DamlName("svName")]
    state: RewardState

    signatory: list[Party] = [dso]


@template
class SvNodeState:
    dso: Party
    sv: Party
    sv_name: Annotated[str, DamlName("svName")]
    state: NodeState

    signatory: list[Party] = [dso]


@template
class SvStatusReport:
    dso: Party
    sv: Party
    sv_name: Annotated[str, DamlName("svName")]
    number: int
    status: Optional[SvStatus]

    signatory: list[Party] = [dso]
