from datetime import datetime, timedelta
from typing import Annotated

from forge.models import choice, ContractId, Optional, Party, template, variant
from forge.builtins import DamlName, no_derive
from Splice.Round import ClosedMiningRound, OpenMiningRound
from Splice.Types import Round


@no_derive
@variant
class ValidatorLivenessActivityRecord_DsoExpireResult:
    def ValidatorLivenessActivityRecord_DsoExpireResult(): pass


@no_derive
@variant
class ValidatorFaucetCoupon_DsoExpireResult:
    def ValidatorFaucetCoupon_DsoExpireResult(): pass


@no_derive
@variant
class ValidatorLicense_CancelResult:
    def ValidatorLicense_CancelResult(): pass


@no_derive
@variant
class ValidatorLicense_WithdrawResult:
    def ValidatorLicense_WithdrawResult(): pass


struct FaucetState:
    first_received_for: Annotated[Round, DamlName("firstReceivedFor")]
    last_received_for: Annotated[Round, DamlName("lastReceivedFor")]
    num_coupons_missed: Annotated[int, DamlName("numCouponsMissed")]


@no_derive
struct ValidatorLicense_ReceiveFaucetCouponResult:
    license_cid: Annotated[ContractId[ValidatorLicense], DamlName("licenseCid")]
    coupon_cid: Annotated[ContractId[ValidatorFaucetCoupon], DamlName("couponCid")]


@no_derive
struct ValidatorLicense_RecordValidatorLivenessActivityResult:
    license_cid: Annotated[ContractId[ValidatorLicense], DamlName("licenseCid")]
    coupon_cid: Annotated[ContractId[ValidatorLivenessActivityRecord], DamlName("couponCid")]


@no_derive
struct ValidatorLicense_UpdateMetadataResult:
    license_cid: Annotated[ContractId[ValidatorLicense], DamlName("licenseCid")]


@no_derive
struct ValidatorLicense_ReportActiveResult:
    license_cid: Annotated[ContractId[ValidatorLicense], DamlName("licenseCid")]


struct ValidatorLicenseMetadata:
    last_updated_at: Annotated[datetime, DamlName("lastUpdatedAt")]
    version: str
    contact_point: Annotated[str, DamlName("contactPoint")]


@template
class ValidatorLicense:
    validator: Party
    sponsor: Party
    dso: Party
    faucet_state: Annotated[Optional[FaucetState], DamlName("faucetState")]
    metadata: Optional[ValidatorLicenseMetadata]
    last_active_at: Annotated[Optional[datetime], DamlName("lastActiveAt")]

    signatory: list[Party] = [dso]
    observer: list[Party] = [validator]

    @choice(controller=validator, consuming=True)
    def ValidatorLicense_ReceiveFaucetCoupon(self, open_round_cid: Annotated[ContractId[OpenMiningRound], DamlName("openRoundCid")]) -> ValidatorLicense_ReceiveFaucetCouponResult:
        pass

    @choice(controller=validator, consuming=True)
    def ValidatorLicense_RecordValidatorLivenessActivity(self, open_round_cid: Annotated[ContractId[OpenMiningRound], DamlName("openRoundCid")]) -> ValidatorLicense_RecordValidatorLivenessActivityResult:
        pass

    @choice(controller=dso, consuming=True)
    def ValidatorLicense_Withdraw(self, reason: str) -> ValidatorLicense_WithdrawResult:
        pass

    @choice(controller=validator, consuming=True)
    def ValidatorLicense_Cancel(self, reason: str) -> ValidatorLicense_CancelResult:
        pass

    @choice(controller=validator, consuming=True)
    def ValidatorLicense_UpdateMetadata(self, version: str, contact_point: Annotated[str, DamlName("contactPoint")]) -> ValidatorLicense_UpdateMetadataResult:
        pass

    @choice(controller=validator, consuming=True)
    def ValidatorLicense_ReportActive(self) -> ValidatorLicense_ReportActiveResult:
        pass


@template
class ValidatorFaucetCoupon:
    dso: Party
    validator: Party
    round: Round

    signatory: list[Party] = [dso, validator]

    @choice(controller=dso, consuming=True)
    def ValidatorFaucetCoupon_DsoExpire(self, closed_round_cid: Annotated[ContractId[ClosedMiningRound], DamlName("closedRoundCid")]) -> ValidatorFaucetCoupon_DsoExpireResult:
        pass


@template
class ValidatorLivenessActivityRecord:
    dso: Party
    validator: Party
    round: Round

    signatory: list[Party] = [dso]
    observer: list[Party] = [validator]

    @choice(controller=dso, consuming=True)
    def ValidatorLivenessActivityRecord_DsoExpire(self, closed_round_cid: Annotated[ContractId[ClosedMiningRound], DamlName("closedRoundCid")]) -> ValidatorLivenessActivityRecord_DsoExpireResult:
        pass


@DamlName("metadataUpdateMinInterval")
def metadata_update_min_interval() -> timedelta:
    pass


@DamlName("activityReportMinInterval")
def activity_report_min_interval() -> timedelta:
    pass


@DamlName("metadataUpdateAllowed")
def metadata_update_allowed(previous: datetime, now: datetime) -> bool:
    pass


@DamlName("activityReportAllowed")
def activity_report_allowed(previous: datetime, now: datetime) -> bool:
    pass


@DamlName("validValidatorLicense")
def valid_validator_license(license: ValidatorLicense) -> bool:
    pass


@DamlName("maxIdentifierLength")
def max_identifier_length() -> int:
    pass


@DamlName("validValidatorLicenseMetadata")
def valid_validator_license_metadata(metadata: ValidatorLicenseMetadata) -> bool:
    pass
