from datetime import timedelta
from typing import Annotated

from forge.models import Decimal, Party, template
from forge.builtins import DamlName


struct AmuletDecentralizedSynchronizerConfig:
    required_synchronizers: Annotated[set[str], DamlName("requiredSynchronizers")]
    active_synchronizer: Annotated[str, DamlName("activeSynchronizer")]
    fees: SynchronizerFeesConfig


struct BaseRateTrafficLimits:
    burst_amount: Annotated[int, DamlName("burstAmount")]
    burst_window: Annotated[timedelta, DamlName("burstWindow")]


struct SynchronizerFeesConfig:
    base_rate_traffic_limits: Annotated[BaseRateTrafficLimits, DamlName("baseRateTrafficLimits")]
    extra_traffic_price: Annotated[Decimal, DamlName("extraTrafficPrice")]
    read_vs_write_scaling_factor: Annotated[int, DamlName("readVsWriteScalingFactor")]
    min_topup_amount: Annotated[int, DamlName("minTopupAmount")]


struct ForMemberTraffic:
    dso: Party
    member_id: Annotated[str, DamlName("memberId")]
    synchronizer_id: Annotated[str, DamlName("synchronizerId")]
    migration_id: Annotated[int, DamlName("migrationId")]


@template
class MemberTraffic:
    dso: Party
    member_id: Annotated[str, DamlName("memberId")]
    synchronizer_id: Annotated[str, DamlName("synchronizerId")]
    migration_id: Annotated[int, DamlName("migrationId")]
    total_purchased: Annotated[int, DamlName("totalPurchased")]
    num_purchases: Annotated[int, DamlName("numPurchases")]
    amulet_spent: Annotated[Decimal, DamlName("amuletSpent")]
    usd_spent: Annotated[Decimal, DamlName("usdSpent")]

    signatory: list[Party] = [dso]


@DamlName("validAmuletDecentralizedSynchronizerConfig")
def valid_amulet_decentralized_synchronizer_config(config: AmuletDecentralizedSynchronizerConfig) -> bool:
    pass


@DamlName("initialMemberTraffic")
def initial_member_traffic(party: Party, member_id: str, synchronizer_id: str, migration_id: int) -> MemberTraffic:
    pass
