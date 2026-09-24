"""Stand-in for the real `Splice.DecentralizedSynchronizer` Daml module
(`splice/daml/splice-amulet/daml/Splice/DecentralizedSynchronizer.daml`) -
IDE/authoring support only, see `Splice/__init__.py`.
"""

from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal

from forge.models.types import Party, Text
from typing import Annotated
from .. import DamlName


@dataclass(frozen=True)
class BaseRateTrafficLimits:
    """The real Daml `BaseRateTrafficLimits` record - the free base rate of
    sequencing traffic a synchronizer delivers. Real Daml definition:

        data BaseRateTrafficLimits = BaseRateTrafficLimits with
            burstAmount: Int
            burstWindow: RelTime
          deriving (Eq, Show)
    """

    burst_amount: Annotated[int, DamlName("burstAmount")]
    burst_window: Annotated[timedelta, DamlName("burstWindow")]


@dataclass(frozen=True)
class SynchronizerFeesConfig:
    """The real Daml `SynchronizerFeesConfig` record - fees charged for
    using the decentralized synchronizer. Real Daml definition:

        data SynchronizerFeesConfig = SynchronizerFeesConfig with
            baseRateTrafficLimits: BaseRateTrafficLimits
            extraTrafficPrice: Decimal
            readVsWriteScalingFactor: Int
            minTopupAmount: Int
    """

    base_rate_traffic_limits: Annotated[BaseRateTrafficLimits, DamlName("baseRateTrafficLimits")]
    extra_traffic_price: Annotated[Decimal, DamlName("extraTrafficPrice")]
    read_vs_write_scaling_factor: Annotated[int, DamlName("readVsWriteScalingFactor")]
    min_topup_amount: Annotated[int, DamlName("minTopupAmount")]


@dataclass(frozen=True)
class AmuletDecentralizedSynchronizerConfig:
    """The real Daml `AmuletDecentralizedSynchronizerConfig` record - which
    synchronizer(s) Amulet/ANS users must be connected to, and at what fees.
    Real Daml definition:

        data AmuletDecentralizedSynchronizerConfig = AmuletDecentralizedSynchronizerConfig with
            requiredSynchronizers : Set.Set Text
            activeSynchronizer : Text
            fees : SynchronizerFeesConfig
          deriving (Eq, Show)
    """

    required_synchronizers: Annotated[frozenset[Text], DamlName("requiredSynchronizers")]
    active_synchronizer: Annotated[Text, DamlName("activeSynchronizer")]
    fees: SynchronizerFeesConfig


@dataclass(frozen=True)
class MemberTraffic:
    """The real Daml `MemberTraffic` template - tracks extra sequencer
    traffic purchased for one synchronizer member. Real Daml definition:

        template MemberTraffic with
            dso : Party
            memberId : Text
            synchronizerId : Text
            migrationId : Int
            totalPurchased : Int
            numPurchases : Int
            amuletSpent : Decimal
            usdSpent : Decimal
          where
            signatory dso

    No real choices - archived only via `fetchAndArchive` inside
    `AmuletRules_MergeMemberTrafficContracts`.
    """

    dso: Party
    member_id: Annotated[Text, DamlName("memberId")]
    synchronizer_id: Annotated[Text, DamlName("synchronizerId")]
    migration_id: Annotated[int, DamlName("migrationId")]
    total_purchased: Annotated[int, DamlName("totalPurchased")]
    num_purchases: Annotated[int, DamlName("numPurchases")]
    amulet_spent: Annotated[Decimal, DamlName("amuletSpent")]
    usd_spent: Annotated[Decimal, DamlName("usdSpent")]


@dataclass(frozen=True)
class ForMemberTraffic:
    dso: Party
    member_id: Annotated[Text, DamlName("memberId")]
    synchronizer_id: Annotated[Text, DamlName("synchronizerId")]
    migration_id: Annotated[int, DamlName("migrationId")]
