"""Stand-in for the real `Splice.DecentralizedSynchronizer` Daml module
(`splice/daml/splice-amulet/daml/Splice/DecentralizedSynchronizer.daml`) -
IDE/authoring support only, see `Splice/__init__.py`.
"""

from dataclasses import dataclass
from decimal import Decimal

from forge.models.types import Party, RelTime, Text


@dataclass(frozen=True)
class BaseRateTrafficLimits:
    """The real Daml `BaseRateTrafficLimits` record - the free base rate of
    sequencing traffic a synchronizer delivers. Real Daml definition:

        data BaseRateTrafficLimits = BaseRateTrafficLimits with
            burstAmount: Int
            burstWindow: RelTime
          deriving (Eq, Show)
    """

    burst_amount: int
    burst_window: RelTime


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

    base_rate_traffic_limits: BaseRateTrafficLimits
    extra_traffic_price: Decimal
    read_vs_write_scaling_factor: int
    min_topup_amount: int


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

    required_synchronizers: frozenset[Text]
    active_synchronizer: Text
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
    member_id: Text
    synchronizer_id: Text
    migration_id: int
    total_purchased: int
    num_purchases: int
    amulet_spent: Decimal
    usd_spent: Decimal
