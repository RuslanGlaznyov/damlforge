from typing import Annotated

from forge.models import choice, ContractId, Decimal, ledger_effect, Party, template
from forge.builtins import DamlName, no_derive
from Splice.Api.FeaturedAppRightV1 import AppRewardBeneficiary, FeaturedAppRight, FeaturedAppRight_CreateActivityMarkerResult
import Splice.Api.FeaturedAppRightV2 as FeaturedAppRightV2


@no_derive
struct BatchedMarkersProxy_CreateMarkersResult:
    results: list[list[FeaturedAppRight_CreateActivityMarkerResult]]


@no_derive
struct BatchedMarkersProxy_CreateMarkersV2Result:
    results: list[FeaturedAppRightV2.FeaturedAppRight_CreateActivityMarkerResult]


struct RewardBatch:
    beneficiaries: list[AppRewardBeneficiary]
    num_markers: Annotated[int, DamlName("numMarkers")]


struct RewardBatchV2:
    beneficiaries: list[FeaturedAppRightV2.AppRewardBeneficiary]
    marker_weight: Annotated[Decimal, DamlName("markerWeight")]


@template
class BatchedMarkersProxy:
    provider: Party
    dso: Party

    signatory: list[Party] = [provider]

    @choice(controller=provider, consuming="nonconsuming", observer=[dso])
    def BatchedMarkersProxy_CreateMarkers(self, featured_app_right_cid: Annotated[ContractId[FeaturedAppRight], DamlName("featuredAppRightCid")], batches: list[RewardBatch]) -> BatchedMarkersProxy_CreateMarkersResult:
        pass

    @choice(controller=provider, consuming="nonconsuming", observer=[dso])
    def BatchedMarkersProxy_CreateMarkersV2(self, featured_app_right_cid: Annotated[ContractId[FeaturedAppRightV2.FeaturedAppRight], DamlName("featuredAppRightCid")], batches: list[RewardBatchV2]) -> BatchedMarkersProxy_CreateMarkersV2Result:
        pass


@ledger_effect
def require(msg: str, invariant: bool) -> None:
    pass
