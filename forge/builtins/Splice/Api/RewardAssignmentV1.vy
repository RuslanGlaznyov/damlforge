from datetime import datetime
from typing import Annotated

from forge.models import choice, ContractId, Decimal, ledger_effect, Optional, Party
from forge.builtins import DamlName
from Splice.Api.Token.MetadataV1 import ExtraArgs, Metadata


struct RewardCoupon_AssignBeneficiariesResult:
    new_beneficiaries_coupon_cids: Annotated[list[tuple[Party, list[ContractId[RewardCoupon]]]], DamlName("newBeneficiariesCouponCids")]


struct RewardBeneficiary:
    beneficiary: Party
    percentage: Decimal


struct RewardCouponView:
    dso: Party
    provider: Party
    beneficiary: Optional[Party]
    amount: Decimal
    expires_at: Annotated[datetime, DamlName("expiresAt")]
    max_num_new_beneficiaries: Annotated[int, DamlName("maxNumNewBeneficiaries")]
    meta: Metadata


interface RewardCoupon(view=RewardCouponView):
    @choice(controller=view.provider, consuming=True)
    def RewardCoupon_AssignBeneficiaries(self, additional_coupons: Annotated[list[ContractId[RewardCoupon]], DamlName("additionalCoupons")], new_beneficiaries: Annotated[list[RewardBeneficiary], DamlName("newBeneficiaries")], extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]) -> RewardCoupon_AssignBeneficiariesResult:
        pass


@ledger_effect
@DamlName("rewardCoupon_assignBeneficiariesImpl")
def reward_coupon_assign_beneficiaries_impl(i: RewardCoupon, contract_id: ContractId[RewardCoupon], reward_coupon_assign_beneficiaries: RewardCoupon_AssignBeneficiaries) -> RewardCoupon_AssignBeneficiariesResult:
    pass
