"""Stand-in for the real `Splice.Amulet.RewardAccountingV2` Daml module
(`splice/daml/splice-amulet/daml/Splice/Amulet/RewardAccountingV2.daml`) -
IDE/authoring support only, see `Splice/__init__.py`. Templates and support
code for reward accounting based on off-ledger calculations (CIP-104).
"""

from dataclasses import dataclass
from decimal import Decimal

from forge.models.types import Party, RelTime, Timestamp
from ..Amulet.CryptoHash import Hash
from ..Types import Round


@dataclass(frozen=True)
class CalculateRewardsV2:
    """The real Daml `CalculateRewardsV2` template - tracks the need to
    calculate and confirm off-ledger app reward amounts for a round. Real
    Daml definition:

        template CalculateRewardsV2 with
            dso : Party
            round : Round
            roundClosedAt : Time
            rewardCouponTimeToLive : RelTime
            dryRun : Bool
          where
            signatory dso
    """

    dso: Party
    round: Round
    round_closed_at: Timestamp
    reward_coupon_time_to_live: RelTime
    dry_run: bool


@dataclass(frozen=True)
class ProcessRewardsV2:
    """The real Daml `ProcessRewardsV2` template - tracks outstanding
    processing of rewards for a given round and batch hash. Real Daml
    definition:

        template ProcessRewardsV2 with
            dso : Party
            round : Round
            roundClosedAt : Time
            dryRun : Bool
            rewardCouponTimeToLive : RelTime
            batchHash : CryptoHash.Hash
          where
            signatory dso
    """

    dso: Party
    round: Round
    round_closed_at: Timestamp
    dry_run: bool
    reward_coupon_time_to_live: RelTime
    batch_hash: Hash


@dataclass(frozen=True)
class MintingAllowance:
    """The real Daml `MintingAllowance` record - a minting allowance for a
    service provider to mint Amulet. Real Daml definition:

        data MintingAllowance = MintingAllowance with
            provider : Party
            amount : Decimal
          deriving (Eq, Show)
    """

    provider: Party
    amount: Decimal


class Batch:
    """The real Daml `Batch` variant type - one batch of reward processing
    work, either more batches to fan out to (`BatchOfBatches`) or the
    minting allowances to actually process (`BatchOfMintingAllowances`).
    Never constructed directly; use `BatchOfBatches(...)` or
    `BatchOfMintingAllowances(...)`."""


def BatchOfBatches(batch_hashes: list[Hash]) -> Batch:
    """The real Daml `Batch`'s `BatchOfBatches` constructor - a batch that
    fans out into further sub-batches."""
    raise NotImplementedError(
        "BatchOfBatches is a real Daml data constructor - only meaningful "
        "inside compiled .vy source, not callable directly from Python"
    )


def BatchOfMintingAllowances(minting_allowances: list[MintingAllowance]) -> Batch:
    """The real Daml `Batch`'s `BatchOfMintingAllowances` constructor - the
    leaf batch of actual minting allowances to process."""
    raise NotImplementedError(
        "BatchOfMintingAllowances is a real Daml data constructor - only "
        "meaningful inside compiled .vy source, not callable directly from Python"
    )


@dataclass(frozen=True)
class ProcessRewardsV2_ProcessBatch:
    """`ProcessRewardsV2`'s `ProcessRewardsV2_ProcessBatch` choice -
    processes one `Batch`, either fanning out into further
    `ProcessRewardsV2` contracts or creating `RewardCouponV2`s for the
    minting allowances. Observers `batchProviders providersWithWrongVettingState batch`,
    controller `dso`. Real Daml:

        choice ProcessRewardsV2_ProcessBatch : ProcessRewardsV2_ProcessBatchResult
          with
            batch : Batch
            providersWithWrongVettingState : Set Party
    """

    batch: Batch
    providers_with_wrong_vetting_state: frozenset[Party]


@dataclass(frozen=True)
class ProcessRewardsV2_ProcessBatchResult:
    """Real Daml: `data ProcessRewardsV2_ProcessBatchResult =
    ProcessRewardsV2_ProcessBatchResult {}` - intentionally empty to save on
    computational/storage overhead."""
