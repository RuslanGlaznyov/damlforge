from datetime import datetime, timedelta
from typing import Annotated

from forge.models import choice, Decimal, Optional, Party, template, variant
from forge.builtins import DamlCaseAccessor, DamlName
from Splice.Amulet.CryptoHash import Hash
from Splice.Types import Round


MintingAllowances = list[MintingAllowance]


@variant
class Batch:
    def BatchOfBatches(value: list[Hash]): pass
    def BatchOfMintingAllowances(value: list[MintingAllowance]): pass


struct MintingAllowance:
    provider: Party
    amount: Decimal


struct ProcessRewardsV2_ProcessBatchResult:
    pass


@template
class CalculateRewardsV2:
    dso: Party
    round: Round
    round_closed_at: Annotated[datetime, DamlName("roundClosedAt")]
    reward_coupon_time_to_live: Annotated[timedelta, DamlName("rewardCouponTimeToLive")]
    dry_run: Annotated[bool, DamlName("dryRun")]

    signatory: list[Party] = [dso]


@template
class ProcessRewardsV2:
    dso: Party
    round: Round
    round_closed_at: Annotated[datetime, DamlName("roundClosedAt")]
    dry_run: Annotated[bool, DamlName("dryRun")]
    reward_coupon_time_to_live: Annotated[timedelta, DamlName("rewardCouponTimeToLive")]
    batch_hash: Annotated[Hash, DamlName("batchHash")]

    signatory: list[Party] = [dso]

    @choice(controller=dso, consuming=True)
    def ProcessRewardsV2_ProcessBatch(self, batch: Batch, providers_with_wrong_vetting_state: Annotated[set[Party], DamlName("providersWithWrongVettingState")]) -> ProcessRewardsV2_ProcessBatchResult:
        pass


@DamlCaseAccessor("BatchOfBatches")
def batch_of_batches(value: Batch) -> Optional[list[Hash]]:
    pass


@DamlCaseAccessor("BatchOfMintingAllowances")
def batch_of_minting_allowances(value: Batch) -> Optional[list[MintingAllowance]]:
    pass


@DamlName("batchProviders")
def batch_providers(ignored_providers: set[Party], batch: Batch) -> list[Party]:
    pass
