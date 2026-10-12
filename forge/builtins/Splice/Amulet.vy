from datetime import datetime
from typing import Annotated, Generic, TypeVar

from forge.models import choice, ContractId, Decimal, ledger_effect, Optional, Party, template, variant
from forge.builtins import DamlName, no_derive
from Splice.Api.FeaturedAppRightV1 import AppRewardBeneficiary
from Splice.Api.RewardAssignmentV1 import RewardCoupon, RewardCoupon_AssignBeneficiaries, RewardCoupon_AssignBeneficiariesResult
from Splice.Api.Token.HoldingV2 import Holding
from Splice.Api.Token.MetadataV1 import Metadata
from Splice.Api.Token.TransferEventsV2 import EventLog
from Splice.Expiry import TimeLock
from Splice.ExternalPartyConfigState import ExternalPartyConfigState
from Splice.Fees import ExpiringAmount
from Splice.Round import ClosedMiningRound, OpenMiningRound
from Splice.Types import Round
import Splice.Api.FeaturedAppRightV2 as FeaturedAppRightV2

AmuletContractId = TypeVar("AmuletContractId")


@no_derive
@variant
class UnclaimedActivityRecord_ArchiveAsBeneficiaryResult:
    def UnclaimedActivityRecord_ArchiveAsBeneficiaryResult(): pass


@no_derive
@variant
class SvRewardCoupon_ArchiveAsBeneficiaryResult:
    def SvRewardCoupon_ArchiveAsBeneficiaryResult(): pass


@no_derive
@variant
class FeaturedAppRight_CancelResult:
    def FeaturedAppRight_CancelResult(): pass


@no_derive
@variant
class FeaturedAppRight_WithdrawResult:
    def FeaturedAppRight_WithdrawResult(): pass


@no_derive
@variant
class ValidatorRight_ArchiveAsUserResult:
    def ValidatorRight_ArchiveAsUserResult(): pass


@no_derive
@variant
class ValidatorRight_ArchiveAsValidatorResult:
    def ValidatorRight_ArchiveAsValidatorResult(): pass


struct AmuletExpireSummary:
    owner: Party
    round: Round
    change_to_initial_amount_as_of_round_zero: Annotated[Decimal, DamlName("changeToInitialAmountAsOfRoundZero")]
    change_to_holding_fees_rate: Annotated[Decimal, DamlName("changeToHoldingFeesRate")]


struct AmuletExpireV2Summary:
    owner: Party


struct AmuletCreateSummary(Generic[AmuletContractId]):
    amulet: AmuletContractId
    amulet_price: Annotated[Decimal, DamlName("amuletPrice")]
    round: Round


@no_derive
struct Amulet_ExpireResult:
    expire_sum: Annotated[AmuletExpireSummary, DamlName("expireSum")]
    meta: Optional[Metadata]


@no_derive
struct Amulet_ExpireV2Result:
    expire_sum: Annotated[AmuletExpireV2Summary, DamlName("expireSum")]
    meta: Metadata


@no_derive
struct LockedAmulet_UnlockResult:
    amulet_sum: Annotated[AmuletCreateSummary[ContractId[Amulet]], DamlName("amuletSum")]
    meta: Optional[Metadata]


@no_derive
struct LockedAmulet_UnlockV2Result:
    amulet_cid: Annotated[ContractId[Amulet], DamlName("amuletCid")]
    meta: Metadata


@no_derive
struct LockedAmulet_OwnerExpireLockResult:
    amulet_sum: Annotated[AmuletCreateSummary[ContractId[Amulet]], DamlName("amuletSum")]
    meta: Optional[Metadata]


@no_derive
struct LockedAmulet_OwnerExpireLockV2Result:
    amulet_cid: Annotated[ContractId[Amulet], DamlName("amuletCid")]
    meta: Metadata


@no_derive
struct LockedAmulet_ExpireAmuletResult:
    expire_sum: Annotated[AmuletExpireSummary, DamlName("expireSum")]
    meta: Optional[Metadata]


@no_derive
struct LockedAmulet_ExpireAmuletV2Result:
    expire_sum: Annotated[AmuletExpireV2Summary, DamlName("expireSum")]
    meta: Metadata


@no_derive
struct FeaturedAppRight_UpdateResult:
    featured_app_right_cid: Annotated[ContractId[FeaturedAppRight], DamlName("featuredAppRightCid")]


@no_derive
struct AppRewardCoupon_DsoExpireResult:
    featured: bool
    amount: Decimal


@no_derive
struct ValidatorRewardCoupon_DsoExpireResult:
    amount: Decimal


@no_derive
struct ValidatorRewardCoupon_ArchiveAsValidatorResult:
    pass


@no_derive
struct SvRewardCoupon_DsoExpireResult:
    weight: int


@no_derive
struct UnclaimedActivityRecord_DsoExpireResult:
    unclaimed_reward_cid: Annotated[ContractId[UnclaimedReward], DamlName("unclaimedRewardCid")]


@no_derive
struct DevelopmentFundCoupon_WithdrawResult:
    unclaimed_development_fund_coupon_cid: Annotated[ContractId[UnclaimedDevelopmentFundCoupon], DamlName("unclaimedDevelopmentFundCouponCid")]


@no_derive
struct DevelopmentFundCoupon_RejectResult:
    unclaimed_development_fund_coupon_cid: Annotated[ContractId[UnclaimedDevelopmentFundCoupon], DamlName("unclaimedDevelopmentFundCouponCid")]


@no_derive
struct DevelopmentFundCoupon_DsoExpireResult:
    unclaimed_development_fund_coupon_cid: Annotated[ContractId[UnclaimedDevelopmentFundCoupon], DamlName("unclaimedDevelopmentFundCouponCid")]


@template
class Amulet:
    dso: Party
    owner: Party
    amount: ExpiringAmount

    signatory: list[Party] = [dso, owner]

    @choice(controller=dso, consuming=True)
    def Amulet_ExpireV2(self, external_party_config_state0_cid: Annotated[ContractId[ExternalPartyConfigState], DamlName("externalPartyConfigState0Cid")], external_party_config_state1_cid: Annotated[ContractId[ExternalPartyConfigState], DamlName("externalPartyConfigState1Cid")]) -> Amulet_ExpireV2Result:
        pass

    @choice(controller=dso, consuming=True)
    def Amulet_Expire(self, round_cid: Annotated[ContractId[OpenMiningRound], DamlName("roundCid")]) -> Amulet_ExpireResult:
        pass


@template
class LockedAmulet:
    amulet: Amulet
    lock: TimeLock

    signatory: list[Party] = [amulet.dso, amulet.owner] + lock.holders

    @choice(controller=amulet.dso, consuming=True)
    def LockedAmulet_ExpireAmuletV2(self, external_party_config_state0_cid: Annotated[ContractId[ExternalPartyConfigState], DamlName("externalPartyConfigState0Cid")], external_party_config_state1_cid: Annotated[ContractId[ExternalPartyConfigState], DamlName("externalPartyConfigState1Cid")]) -> LockedAmulet_ExpireAmuletV2Result:
        pass

    @choice(controller=[amulet.owner] + lock.holders, consuming=True)
    def LockedAmulet_UnlockV2(self) -> LockedAmulet_UnlockV2Result:
        pass

    @choice(controller=amulet.owner, consuming=True)
    def LockedAmulet_OwnerExpireLockV2(self) -> LockedAmulet_OwnerExpireLockV2Result:
        pass

    @choice(controller=amulet.dso, consuming=True)
    def LockedAmulet_ExpireAmulet(self, round_cid: Annotated[ContractId[OpenMiningRound], DamlName("roundCid")]) -> LockedAmulet_ExpireAmuletResult:
        pass

    @choice(controller=amulet.owner, consuming=True)
    def LockedAmulet_OwnerExpireLock(self, open_round_cid: Annotated[ContractId[OpenMiningRound], DamlName("openRoundCid")]) -> LockedAmulet_OwnerExpireLockResult:
        pass

    @choice(controller=[amulet.owner] + lock.holders, consuming=True)
    def LockedAmulet_Unlock(self, open_round_cid: Annotated[ContractId[OpenMiningRound], DamlName("openRoundCid")]) -> LockedAmulet_UnlockResult:
        pass


@template
class ValidatorRight:
    dso: Party
    user: Party
    validator: Party

    signatory: list[Party] = [user, validator]

    @choice(controller=validator, consuming=True)
    def ValidatorRight_ArchiveAsValidator(self) -> ValidatorRight_ArchiveAsValidatorResult:
        pass

    @choice(controller=user, consuming=True)
    def ValidatorRight_ArchiveAsUser(self) -> ValidatorRight_ArchiveAsUserResult:
        pass


@template
class FeaturedAppRight:
    dso: Party
    provider: Party
    activity_weight: Annotated[Optional[Decimal], DamlName("activityWeight")]

    signatory: list[Party] = [dso]
    observer: list[Party] = [provider]

    @choice(controller=dso, consuming=True)
    def FeaturedAppRight_Update(self, reason: str, new_activity_weight: Annotated[Decimal, DamlName("newActivityWeight")]) -> FeaturedAppRight_UpdateResult:
        pass

    @choice(controller=dso, consuming=True)
    def FeaturedAppRight_Withdraw(self, reason: str) -> FeaturedAppRight_WithdrawResult:
        pass

    @choice(controller=provider, consuming=True)
    def FeaturedAppRight_Cancel(self) -> FeaturedAppRight_CancelResult:
        pass


@template
class FeaturedAppActivityMarker:
    dso: Party
    provider: Party
    beneficiary: Party
    weight: Decimal

    signatory: list[Party] = [dso]
    observer: list[Party] = [provider, beneficiary]


@template
class AppRewardCoupon:
    dso: Party
    provider: Party
    featured: bool
    amount: Decimal
    round: Round
    beneficiary: Optional[Party]

    signatory: list[Party] = [dso]
    observer: list[Party] = [provider]

    @choice(controller=dso, consuming=True)
    def AppRewardCoupon_DsoExpire(self, closed_round_cid: Annotated[ContractId[ClosedMiningRound], DamlName("closedRoundCid")]) -> AppRewardCoupon_DsoExpireResult:
        pass


@template
class RewardCouponV2:
    dso: Party
    provider: Party
    round: Round
    amount: Decimal
    expires_at: Annotated[datetime, DamlName("expiresAt")]
    provider_is_observer: Annotated[bool, DamlName("providerIsObserver")]
    beneficiary: Optional[Party]

    signatory: list[Party] = [dso]
    observer: list[Party] = [provider]


@template
class ValidatorRewardCoupon:
    dso: Party
    user: Party
    amount: Decimal
    round: Round

    signatory: list[Party] = [dso]
    observer: list[Party] = [user]

    @choice(controller=dso, consuming=True)
    def ValidatorRewardCoupon_DsoExpire(self, closed_round_cid: Annotated[ContractId[ClosedMiningRound], DamlName("closedRoundCid")]) -> ValidatorRewardCoupon_DsoExpireResult:
        pass

    @choice(controller=[dso, validator], consuming=True)
    def ValidatorRewardCoupon_ArchiveAsValidator(self, validator: Party, right_cid: Annotated[ContractId[ValidatorRight], DamlName("rightCid")]) -> ValidatorRewardCoupon_ArchiveAsValidatorResult:
        pass


@template
class SvRewardCoupon:
    dso: Party
    sv: Party
    beneficiary: Party
    round: Round
    weight: int

    signatory: list[Party] = [dso]
    observer: list[Party] = [sv, beneficiary]

    @choice(controller=dso, consuming=True)
    def SvRewardCoupon_DsoExpire(self, closed_round_cid: Annotated[ContractId[ClosedMiningRound], DamlName("closedRoundCid")]) -> SvRewardCoupon_DsoExpireResult:
        pass

    @choice(controller=beneficiary, consuming=True)
    def SvRewardCoupon_ArchiveAsBeneficiary(self) -> SvRewardCoupon_ArchiveAsBeneficiaryResult:
        pass


@template
class UnclaimedDevelopmentFundCoupon:
    dso: Party
    amount: Decimal

    signatory: list[Party] = [dso]


@template
class DevelopmentFundCoupon:
    dso: Party
    beneficiary: Party
    fund_manager: Annotated[Party, DamlName("fundManager")]
    amount: Decimal
    expires_at: Annotated[datetime, DamlName("expiresAt")]
    reason: str
    mint_after: Annotated[Optional[datetime], DamlName("mintAfter")]

    signatory: list[Party] = [dso]
    observer: list[Party] = [beneficiary, fund_manager]

    @choice(controller=fund_manager, consuming=True)
    def DevelopmentFundCoupon_Withdraw(self, reason: str) -> DevelopmentFundCoupon_WithdrawResult:
        pass

    @choice(controller=beneficiary, consuming=True)
    def DevelopmentFundCoupon_Reject(self, reason: str) -> DevelopmentFundCoupon_RejectResult:
        pass

    @choice(controller=dso, consuming=True)
    def DevelopmentFundCoupon_DsoExpire(self) -> DevelopmentFundCoupon_DsoExpireResult:
        pass


@template
class UnclaimedReward:
    dso: Party
    amount: Decimal

    signatory: list[Party] = [dso]


@template
class UnclaimedActivityRecord:
    dso: Party
    beneficiary: Party
    amount: Decimal
    reason: str
    expires_at: Annotated[datetime, DamlName("expiresAt")]

    signatory: list[Party] = [dso]
    observer: list[Party] = [beneficiary]

    @choice(controller=dso, consuming=True)
    def UnclaimedActivityRecord_DsoExpire(self) -> UnclaimedActivityRecord_DsoExpireResult:
        pass


@DamlName("amuletMetadata")
def amulet_metadata(amulet: Amulet) -> Metadata:
    pass


@DamlName("defaultAppActivityWeight")
def default_app_activity_weight() -> Decimal:
    pass


@ledger_effect
@DamlName("validateAppRewardBeneficiaries")
def validate_app_reward_beneficiaries(beneficiaries: list[AppRewardBeneficiary]) -> None:
    pass


@ledger_effect
@DamlName("validateAppRewardBeneficiariesV2")
def validate_app_reward_beneficiaries_v2(beneficiaries: list[FeaturedAppRightV2.AppRewardBeneficiary]) -> None:
    pass


@ledger_effect
@DamlName("requireAmuletExpiredForAllRounds")
def require_amulet_expired_for_all_rounds(external_party_config_state0_cid: ContractId[ExternalPartyConfigState], external_party_config_state1_cid: ContractId[ExternalPartyConfigState], amulet: Amulet) -> None:
    pass


@DamlName("maxNumNewCouponV2Beneficiaries")
def max_num_new_coupon_v2_beneficiaries() -> int:
    pass


@ledger_effect
@DamlName("rewardCouponV2_assignBeneficiariesImpl")
def reward_coupon_v2_assign_beneficiaries_impl(coupon: RewardCouponV2, contract_id: ContractId[RewardCoupon], arg: RewardCoupon_AssignBeneficiaries) -> RewardCoupon_AssignBeneficiariesResult:
    pass


@ledger_effect
@DamlName("logAmuletMint")
def log_amulet_mint(party: Party, factory_cid: ContractId[EventLog], receiver: Party, amount: Decimal, meta: Metadata, minted_amulet_cid: ContractId[Amulet]) -> None:
    pass


@ledger_effect
@DamlName("logAmuletBurn")
def log_amulet_burn(party: Party, factory_cid: ContractId[EventLog], sender: Party, amount: Decimal, reason: str, burned_amulet_cid: ContractId[Holding]) -> None:
    pass


@ledger_effect
@DamlName("logAmuletUnlock")
def log_amulet_unlock(party: Party, reason: str, owner: Party, locked_amulet_cid: ContractId[LockedAmulet], unlocked_amulet_cid: ContractId[Amulet]) -> None:
    pass
