from typing import Annotated

from forge.models import choice, ContractId, Decimal, ledger_effect, Party
from forge.builtins import DamlName, no_derive


struct FeaturedAppActivityMarkerView:
    dso: Party
    provider: Party
    beneficiary: Party
    weight: Decimal


struct FeaturedAppRightView:
    dso: Party
    provider: Party


@no_derive
struct FeaturedAppRight_CreateActivityMarkerResult:
    activity_marker_cids: Annotated[list[ContractId[FeaturedAppActivityMarker]], DamlName("activityMarkerCids")]


struct AppRewardBeneficiary:
    beneficiary: Party
    weight: Decimal


interface FeaturedAppActivityMarker(view=FeaturedAppActivityMarkerView):
    pass


interface FeaturedAppRight(view=FeaturedAppRightView):
    @choice(controller=view.provider, consuming="nonconsuming")
    def FeaturedAppRight_CreateActivityMarker(self, beneficiaries: list[AppRewardBeneficiary]) -> FeaturedAppRight_CreateActivityMarkerResult:
        pass


@ledger_effect
@DamlName("featuredAppRight_CreateActivityMarkerImpl")
def featured_app_right_create_activity_marker_impl(i: FeaturedAppRight, contract_id: ContractId[FeaturedAppRight], featured_app_right_create_activity_marker: FeaturedAppRight_CreateActivityMarker) -> FeaturedAppRight_CreateActivityMarkerResult:
    pass
