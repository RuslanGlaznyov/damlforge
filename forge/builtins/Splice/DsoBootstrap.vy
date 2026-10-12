from datetime import timedelta
from typing import Annotated

from forge.models import choice, Decimal, GenMap, Optional, Party, template, variant
from forge.builtins import DamlName, no_derive
from Splice.AmuletConfig import AmuletConfig, USD
from Splice.Ans import AnsRulesConfig
from Splice.DSO.DecentralizedSynchronizer import SynchronizerNodeConfig
from Splice.DsoRules import DsoRulesConfig, TrafficState


@no_derive
@variant
class DsoBootstrap_BootstrapResult:
    def DsoBootstrap_BootstrapResult(): pass


@template
class DsoBootstrap:
    dso: Party
    sv1_party: Annotated[Party, DamlName("sv1Party")]
    sv1_name: Annotated[str, DamlName("sv1Name")]
    sv1_reward_weight: Annotated[int, DamlName("sv1RewardWeight")]
    sv1_participant_id: Annotated[str, DamlName("sv1ParticipantId")]
    sv1_synchronizer_nodes: Annotated[GenMap[str, SynchronizerNodeConfig], DamlName("sv1SynchronizerNodes")]
    round0_duration: Annotated[timedelta, DamlName("round0Duration")]
    amulet_config: Annotated[AmuletConfig[USD], DamlName("amuletConfig")]
    amulet_price: Annotated[Decimal, DamlName("amuletPrice")]
    ans_rules_config: Annotated[AnsRulesConfig, DamlName("ansRulesConfig")]
    config: DsoRulesConfig
    initial_traffic_state: Annotated[GenMap[str, TrafficState], DamlName("initialTrafficState")]
    is_dev_net: Annotated[bool, DamlName("isDevNet")]
    initial_round: Annotated[Optional[int], DamlName("initialRound")]

    signatory: list[Party] = [dso]
    observer: list[Party] = [sv1_party]

    @choice(controller=dso, consuming=True)
    def DsoBootstrap_Bootstrap(self) -> DsoBootstrap_BootstrapResult:
        pass
