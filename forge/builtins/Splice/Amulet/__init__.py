"""Stand-in for the real `Splice.Amulet` Daml module
(`splice/daml/splice-amulet/daml/Splice/Amulet.daml`) - IDE/authoring support
only, see `Splice/__init__.py`. Covers `Amulet`, `LockedAmulet`, and
`FeaturedAppRight` with their real fields AND real choices (a choice is
modeled as a dataclass matching its argument record - exactly the value
real Daml expects as `exercise`'s second argument, e.g.
`exercise(locked_cid, LockedAmulet_UnlockV2())` - plus its separate result
type), not just as nominal markers. A choice CAN be exercised on a contract
from code that doesn't define its template, exactly like
`exercise_app_transfer` does internally (`exercise amuletRules
AmuletRules_Transfer with ...`) - there's no real restriction against it.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Annotated, Generic, Optional, TypeVar

from forge.models.types import ContractId, Party, Text
from ..Api.Token.MetadataV1 import Metadata
from ..ExternalPartyConfigState import ExternalPartyConfigState
from ..Expiry import TimeLock
from ..Fees import ExpiringAmount
from ..Round import ClosedMiningRound, OpenMiningRound
from ..Types import Round
from ... import DamlName

T = TypeVar("T")


@dataclass(frozen=True)
class AmuletCreateSummary(Generic[T]):
    """The real Daml `AmuletCreateSummary amuletContractId` record - result
    shape shared by every operation that creates a new `Amulet` (minting,
    unlocking, ...). Real Daml definition:

        data AmuletCreateSummary amuletContractId = AmuletCreateSummary with
            amulet : amuletContractId
            amuletPrice : Decimal
            round: Round
          deriving (Eq, Show)
    """

    amulet: T
    amulet_price: Annotated[Decimal, DamlName("amuletPrice")]
    round: Round


@dataclass(frozen=True)
class AmuletExpireSummary:
    """The real Daml `AmuletExpireSummary` record - accounting detail for an
    `Amulet_Expire`/`LockedAmulet_ExpireAmulet` result. Real Daml definition:

        data AmuletExpireSummary = AmuletExpireSummary with
            owner : Party
            round: Round
            changeToInitialAmountAsOfRoundZero : Decimal
            changeToHoldingFeesRate : Decimal
    """

    owner: Party
    round: Round
    change_to_initial_amount_as_of_round_zero: Annotated[
        Decimal, DamlName("changeToInitialAmountAsOfRoundZero")
    ]
    change_to_holding_fees_rate: Annotated[Decimal, DamlName("changeToHoldingFeesRate")]


@dataclass(frozen=True)
class AmuletExpireV2Summary:
    """The real Daml `AmuletExpireV2Summary` record. Real Daml definition:

    data AmuletExpireV2Summary = AmuletExpireV2Summary
      with
        owner : Party
      deriving (Eq, Show)
    """

    owner: Party


@dataclass(frozen=True)
class Amulet:
    """The real Daml `Amulet` template - a holding of Amulet, Splice's
    native token. Real Daml definition:

        template Amulet
          with
            dso : Party
            owner : Party
            amount : ExpiringAmount
          where
            signatory dso, owner
            ensure validExpiringAmount amount
    """

    dso: Party
    owner: Party
    amount: ExpiringAmount


@dataclass(frozen=True)
class Amulet_Expire:
    """`Amulet`'s `Amulet_Expire` choice - DEPRECATED in real Daml (its body
    is just `deprecatedChoice ...`, which aborts); use `Amulet_ExpireV2`.
    Modeled for completeness/fidelity, not because it's expected to be used.
    Real Daml: `choice Amulet_Expire with roundCid : ContractId OpenMiningRound`.
    """

    round_cid: Annotated[ContractId[OpenMiningRound], DamlName("roundCid")]


@dataclass(frozen=True)
class Amulet_ExpireResult:
    """Real Daml: `data Amulet_ExpireResult = Amulet_ExpireResult with
    expireSum : AmuletExpireSummary; meta : Optional Api.Token.MetadataV1.Metadata`."""

    expire_sum: Annotated[AmuletExpireSummary, DamlName("expireSum")]
    meta: Optional[Metadata] = None


@dataclass(frozen=True)
class Amulet_ExpireV2:
    """`Amulet`'s `Amulet_ExpireV2` choice - archives a fully-decayed
    ("dust") `Amulet` once proven expired for all active rounds. Real Daml:

        choice Amulet_ExpireV2
          with
            externalPartyConfigState0Cid : ContractId ExternalPartyConfigState
            externalPartyConfigState1Cid : ContractId ExternalPartyConfigState
          controller dso
    """

    external_party_config_state0_cid: Annotated[
        ContractId[ExternalPartyConfigState], DamlName("externalPartyConfigState0Cid")
    ]
    external_party_config_state1_cid: Annotated[
        ContractId[ExternalPartyConfigState], DamlName("externalPartyConfigState1Cid")
    ]


@dataclass(frozen=True)
class Amulet_ExpireV2Result:
    """Real Daml: `data Amulet_ExpireV2Result = Amulet_ExpireV2Result with
    expireSum : AmuletExpireV2Summary; meta : Api.Token.MetadataV1.Metadata`."""

    expire_sum: Annotated[AmuletExpireV2Summary, DamlName("expireSum")]
    meta: Metadata


@dataclass(frozen=True)
class LockedAmulet:
    """The real Daml `LockedAmulet` template - an `Amulet` locked to a set
    of holders until a `TimeLock` expires. Real Daml definition:

        template LockedAmulet
          with
            amulet : Amulet
            lock : TimeLock
          where
            signatory lock.holders, signatory amulet
    """

    amulet: Amulet
    lock: TimeLock


@dataclass(frozen=True)
class LockedAmulet_Unlock:
    """`LockedAmulet`'s `LockedAmulet_Unlock` choice - DEPRECATED, use
    `LockedAmulet_UnlockV2`. Real Daml:
    `choice LockedAmulet_Unlock with openRoundCid : ContractId OpenMiningRound`,
    controller `amulet.owner :: lock.holders`."""

    open_round_cid: Annotated[ContractId[OpenMiningRound], DamlName("openRoundCid")]


@dataclass(frozen=True)
class LockedAmulet_UnlockResult:
    """Real Daml: `data LockedAmulet_UnlockResult = LockedAmulet_UnlockResult
    with amuletSum : AmuletCreateSummary (ContractId Amulet); meta : Optional Metadata`."""

    amulet_sum: Annotated[AmuletCreateSummary[ContractId[Amulet]], DamlName("amuletSum")]
    meta: Optional[Metadata] = None


@dataclass(frozen=True)
class LockedAmulet_UnlockV2:
    """`LockedAmulet`'s `LockedAmulet_UnlockV2` choice - releases the lock
    and creates a fresh unlocked `Amulet` for the original holders. No
    arguments. Controller `amulet.owner :: lock.holders`."""


@dataclass(frozen=True)
class LockedAmulet_UnlockV2Result:
    """Real Daml: `data LockedAmulet_UnlockV2Result = LockedAmulet_UnlockV2Result
    with amuletCid : ContractId Amulet; meta : Metadata`."""

    amulet_cid: Annotated[ContractId[Amulet], DamlName("amuletCid")]
    meta: Metadata


@dataclass(frozen=True)
class LockedAmulet_OwnerExpireLock:
    """`LockedAmulet`'s `LockedAmulet_OwnerExpireLock` choice - DEPRECATED,
    use `LockedAmulet_OwnerExpireLockV2`. Real Daml:
    `choice LockedAmulet_OwnerExpireLock with openRoundCid : ContractId OpenMiningRound`,
    controller `amulet.owner`."""

    open_round_cid: Annotated[ContractId[OpenMiningRound], DamlName("openRoundCid")]


@dataclass(frozen=True)
class LockedAmulet_OwnerExpireLockResult:
    """Real Daml: `data LockedAmulet_OwnerExpireLockResult = ... with
    amuletSum : AmuletCreateSummary (ContractId Amulet); meta : Optional Metadata`."""

    amulet_sum: Annotated[AmuletCreateSummary[ContractId[Amulet]], DamlName("amuletSum")]
    meta: Optional[Metadata] = None


@dataclass(frozen=True)
class LockedAmulet_OwnerExpireLockV2:
    """`LockedAmulet`'s `LockedAmulet_OwnerExpireLockV2` choice - the owner
    reclaims a `LockedAmulet` once its lock's `expiresAt` has passed. No
    arguments. Controller `amulet.owner`."""


@dataclass(frozen=True)
class LockedAmulet_OwnerExpireLockV2Result:
    """Real Daml: `data LockedAmulet_OwnerExpireLockV2Result = ... with
    amuletCid : ContractId Amulet; meta : Metadata`."""

    amulet_cid: Annotated[ContractId[Amulet], DamlName("amuletCid")]
    meta: Metadata


@dataclass(frozen=True)
class LockedAmulet_ExpireAmulet:
    """`LockedAmulet`'s `LockedAmulet_ExpireAmulet` choice - DEPRECATED, use
    `LockedAmulet_ExpireAmuletV2`. Real Daml:
    `choice LockedAmulet_ExpireAmulet with roundCid : ContractId OpenMiningRound`,
    controller `amulet.dso`."""

    round_cid: Annotated[ContractId[OpenMiningRound], DamlName("roundCid")]


@dataclass(frozen=True)
class LockedAmulet_ExpireAmuletResult:
    """Real Daml: `data LockedAmulet_ExpireAmuletResult = ... with
    expireSum : AmuletExpireSummary; meta : Optional Metadata`."""

    expire_sum: Annotated[AmuletExpireSummary, DamlName("expireSum")]
    meta: Optional[Metadata] = None


@dataclass(frozen=True)
class LockedAmulet_ExpireAmuletV2:
    """`LockedAmulet`'s `LockedAmulet_ExpireAmuletV2` choice - archives a
    fully-decayed locked "dust" amulet. Real Daml:

        choice LockedAmulet_ExpireAmuletV2
          with
            externalPartyConfigState0Cid : ContractId ExternalPartyConfigState
            externalPartyConfigState1Cid : ContractId ExternalPartyConfigState
          controller amulet.dso
    """

    external_party_config_state0_cid: Annotated[
        ContractId[ExternalPartyConfigState], DamlName("externalPartyConfigState0Cid")
    ]
    external_party_config_state1_cid: Annotated[
        ContractId[ExternalPartyConfigState], DamlName("externalPartyConfigState1Cid")
    ]


@dataclass(frozen=True)
class LockedAmulet_ExpireAmuletV2Result:
    """Real Daml: `data LockedAmulet_ExpireAmuletV2Result = ... with
    expireSum : AmuletExpireV2Summary; meta : Metadata`."""

    expire_sum: Annotated[AmuletExpireV2Summary, DamlName("expireSum")]
    meta: Metadata


@dataclass(frozen=True)
class FeaturedAppRight:
    """The real Daml `FeaturedAppRight` template - proof that `provider` is
    a DSO-featured app; `AppTransferContext.featured_app_right` optionally
    points to one of these. Real Daml definition:

        template FeaturedAppRight with
            dso : Party
            provider : Party
          where
            signatory dso
            observer provider
    """

    dso: Party
    provider: Party


@dataclass(frozen=True)
class FeaturedAppRight_Withdraw:
    """`FeaturedAppRight`'s `FeaturedAppRight_Withdraw` choice - the DSO
    revokes featured-app status. Real Daml:
    `choice FeaturedAppRight_Withdraw with reason : Text`, controller `dso`."""

    reason: Text


@dataclass(frozen=True)
class FeaturedAppRight_WithdrawResult:
    """Real Daml: `data FeaturedAppRight_WithdrawResult = FeaturedAppRight_WithdrawResult`
    (no fields)."""


@dataclass(frozen=True)
class FeaturedAppRight_Cancel:
    """`FeaturedAppRight`'s `FeaturedAppRight_Cancel` choice - the provider
    gives up featured-app status voluntarily. No arguments. Controller
    `provider`."""


@dataclass(frozen=True)
class FeaturedAppRight_CancelResult:
    """Real Daml: `data FeaturedAppRight_CancelResult = FeaturedAppRight_CancelResult`
    (no fields)."""


@dataclass(frozen=True)
class ValidatorRight:
    """The real Daml `ValidatorRight` template - proof that `validator`
    hosts `user`. Referenced by `TransferContext.validator_rights`. Real
    Daml definition:

        template ValidatorRight with
            dso : Party
            user : Party
            validator : Party
          where
            signatory user, validator

    Real choices (`ValidatorRight_ArchiveAsValidator`,
    `ValidatorRight_ArchiveAsUser`) are `ValidatorRight`'s own, not
    `AmuletRules`'s - out of scope here, not modeled.
    """

    dso: Party
    user: Party
    validator: Party


@dataclass(frozen=True)
class ValidatorRight_ArchiveAsValidator:
    """`ValidatorRight`'s `ValidatorRight_ArchiveAsValidator` choice - the
    validator archives the right. No arguments. Controller `validator`."""


@dataclass(frozen=True)
class ValidatorRight_ArchiveAsValidatorResult:
    """Real Daml: `data ValidatorRight_ArchiveAsValidatorResult = ...`
    (no fields)."""


@dataclass(frozen=True)
class ValidatorRight_ArchiveAsUser:
    """`ValidatorRight`'s `ValidatorRight_ArchiveAsUser` choice - the user
    archives the right. No arguments. Controller `user`."""


@dataclass(frozen=True)
class ValidatorRight_ArchiveAsUserResult:
    """Real Daml: `data ValidatorRight_ArchiveAsUserResult = ...`
    (no fields)."""


@dataclass(frozen=True)
class FeaturedAppActivityMarker:
    """The real Daml `FeaturedAppActivityMarker` template - records that a
    featured app provider (and optionally a collaborating beneficiary)
    performed activity eligible for a reward, converted into an
    `AppRewardCoupon` by SV automation. Real Daml definition:

        template FeaturedAppActivityMarker
          with
            dso : Party
            provider : Party
            beneficiary : Party
            weight : Decimal
          where
            signatory dso
            observer provider, beneficiary
            ensure 0.0 < weight && weight <= 10000.0
    """

    dso: Party
    provider: Party
    beneficiary: Party
    weight: Decimal


@dataclass(frozen=True)
class AppRewardCoupon:
    """The real Daml `AppRewardCoupon` template - a coupon for app rewards
    proportional to the usage fee paid as part of an Amulet transfer. Real
    Daml definition:

        template AppRewardCoupon
          with
            dso : Party
            provider : Party
            featured : Bool
            amount : Decimal
            round : Round
            beneficiary : Optional Party
          where
            signatory dso
            observer provider, beneficiary
    """

    dso: Party
    provider: Party
    featured: bool
    amount: Decimal
    round: Round
    beneficiary: Optional[Party] = None


@dataclass(frozen=True)
class AppRewardCoupon_DsoExpire:
    """`AppRewardCoupon`'s `AppRewardCoupon_DsoExpire` choice - archives the
    coupon once its round has closed. Controller `dso`. Real Daml:

        choice AppRewardCoupon_DsoExpire : AppRewardCoupon_DsoExpireResult
          with
            closedRoundCid : ContractId ClosedMiningRound
    """

    closed_round_cid: Annotated[ContractId[ClosedMiningRound], DamlName("closedRoundCid")]


@dataclass(frozen=True)
class AppRewardCoupon_DsoExpireResult:
    """Real Daml: `data AppRewardCoupon_DsoExpireResult` with `featured`,
    `amount`."""

    featured: bool
    amount: Decimal


@dataclass(frozen=True)
class RewardCouponV2:
    """The real Daml `RewardCouponV2` template - a coupon for rewards based
    on off-ledger calculations (currently traffic-based app rewards, see
    `Splice.Amulet.RewardAccountingV2`). Real Daml definition:

        template RewardCouponV2
          with
            dso : Party
            provider : Party
            round : Round
            amount : Decimal
            expiresAt : Time
            providerIsObserver : Bool
            beneficiary : Optional Party
          where
            signatory dso
    """

    dso: Party
    provider: Party
    round: Round
    amount: Decimal
    expires_at: Annotated[datetime, DamlName("expiresAt")]
    provider_is_observer: Annotated[bool, DamlName("providerIsObserver")]
    beneficiary: Optional[Party] = None


@dataclass(frozen=True)
class ValidatorRewardCoupon:
    """The real Daml `ValidatorRewardCoupon` template - a coupon for
    validator rewards proportional to the usage fee paid by a hosted user.
    Real Daml definition:

        template ValidatorRewardCoupon
          with
            dso : Party
            user : Party
            amount : Decimal
            round : Round
          where
            signatory dso
            observer user

    """

    dso: Party
    user: Party
    amount: Decimal
    round: Round


@dataclass(frozen=True)
class ValidatorRewardCoupon_DsoExpire:
    """`ValidatorRewardCoupon`'s `ValidatorRewardCoupon_DsoExpire` choice -
    archives the coupon once its round has closed. Controller `dso`. Real
    Daml:

        choice ValidatorRewardCoupon_DsoExpire : ValidatorRewardCoupon_DsoExpireResult
          with
            closedRoundCid : ContractId ClosedMiningRound
    """

    closed_round_cid: Annotated[ContractId[ClosedMiningRound], DamlName("closedRoundCid")]


@dataclass(frozen=True)
class ValidatorRewardCoupon_DsoExpireResult:
    """Real Daml: `data ValidatorRewardCoupon_DsoExpireResult` with
    `amount`."""

    amount: Decimal


@dataclass(frozen=True)
class ValidatorRewardCoupon_ArchiveAsValidator:
    """`ValidatorRewardCoupon`'s `ValidatorRewardCoupon_ArchiveAsValidator`
    choice - used by validators to archive the coupon upon claiming its
    corresponding issuance. Controller `dso`, `validator`. Real Daml:

        choice ValidatorRewardCoupon_ArchiveAsValidator :
          ValidatorRewardCoupon_ArchiveAsValidatorResult
          with
            validator : Party
            rightCid : ContractId ValidatorRight
    """

    validator: Party
    right_cid: Annotated[ContractId[ValidatorRight], DamlName("rightCid")]


@dataclass(frozen=True)
class ValidatorRewardCoupon_ArchiveAsValidatorResult:
    """Real Daml: `data ValidatorRewardCoupon_ArchiveAsValidatorResult = ...`
    (no fields)."""


@dataclass(frozen=True)
class SvRewardCoupon:
    """The real Daml `SvRewardCoupon` template - a coupon for a beneficiary
    to receive part of the SV issuance for a specific SV node and round.
    Real Daml definition:

        template SvRewardCoupon with
            dso : Party
            sv : Party
            beneficiary : Party
            round : Round
            weight : Int
          where
            signatory dso
            observer beneficiary, sv
    """

    dso: Party
    sv: Party
    beneficiary: Party
    round: Round
    weight: int


@dataclass(frozen=True)
class SvRewardCoupon_DsoExpire:
    """`SvRewardCoupon`'s `SvRewardCoupon_DsoExpire` choice - archives the
    coupon once its round has closed. Controller `dso`. Real Daml:

        choice SvRewardCoupon_DsoExpire : SvRewardCoupon_DsoExpireResult
          with
            closedRoundCid : ContractId ClosedMiningRound
    """

    closed_round_cid: Annotated[ContractId[ClosedMiningRound], DamlName("closedRoundCid")]


@dataclass(frozen=True)
class SvRewardCoupon_DsoExpireResult:
    """Real Daml: `data SvRewardCoupon_DsoExpireResult` with `weight`."""

    weight: int


@dataclass(frozen=True)
class SvRewardCoupon_ArchiveAsBeneficiary:
    """`SvRewardCoupon`'s `SvRewardCoupon_ArchiveAsBeneficiary` choice -
    called by the beneficiary as part of an `AmuletRules_Transfer` to claim
    the reward. No arguments. Controller `beneficiary`."""


@dataclass(frozen=True)
class SvRewardCoupon_ArchiveAsBeneficiaryResult:
    """Real Daml: `data SvRewardCoupon_ArchiveAsBeneficiaryResult = ...`
    (no fields)."""


@dataclass(frozen=True)
class UnclaimedDevelopmentFundCoupon:
    """The real Daml `UnclaimedDevelopmentFundCoupon` template - a
    Development Fund emission (CIP-0082) not yet assigned to a specific
    beneficiary. Real Daml definition:

        template UnclaimedDevelopmentFundCoupon
          with
            dso : Party
            amount : Decimal
          where
            signatory dso
    """

    dso: Party
    amount: Decimal


@dataclass(frozen=True)
class DevelopmentFundCoupon:
    """The real Daml `DevelopmentFundCoupon` template - a Development Fund
    emission (CIP-0082) assigned to `beneficiary`. Real Daml definition:

        template DevelopmentFundCoupon
          with
            dso : Party
            beneficiary : Party
            fundManager : Party
            amount : Decimal
            expiresAt : Time
            reason : Text
          where
            signatory dso
            observer beneficiary, fundManager
    """

    dso: Party
    beneficiary: Party
    fund_manager: Annotated[Party, DamlName("fundManager")]
    amount: Decimal
    expires_at: Annotated[datetime, DamlName("expiresAt")]
    reason: Text


@dataclass(frozen=True)
class DevelopmentFundCoupon_Withdraw:
    """`DevelopmentFundCoupon`'s `DevelopmentFundCoupon_Withdraw` choice -
    the fund manager withdraws the coupon, returning its amount to
    `UnclaimedDevelopmentFundCoupon`. Controller `fundManager`. Real Daml:

        choice DevelopmentFundCoupon_Withdraw : DevelopmentFundCoupon_WithdrawResult
          with
            reason : Text
    """

    reason: Text


@dataclass(frozen=True)
class DevelopmentFundCoupon_WithdrawResult:
    """Real Daml: `data DevelopmentFundCoupon_WithdrawResult` with
    `unclaimedDevelopmentFundCouponCid`."""

    unclaimed_development_fund_coupon_cid: Annotated[
        ContractId[UnclaimedDevelopmentFundCoupon], DamlName("unclaimedDevelopmentFundCouponCid")
    ]


@dataclass(frozen=True)
class DevelopmentFundCoupon_Reject:
    """`DevelopmentFundCoupon`'s `DevelopmentFundCoupon_Reject` choice - the
    beneficiary rejects the coupon, returning its amount to
    `UnclaimedDevelopmentFundCoupon`. Controller `beneficiary`. Real Daml:

        choice DevelopmentFundCoupon_Reject : DevelopmentFundCoupon_RejectResult
          with
            reason : Text
    """

    reason: Text


@dataclass(frozen=True)
class DevelopmentFundCoupon_RejectResult:
    """Real Daml: `data DevelopmentFundCoupon_RejectResult` with
    `unclaimedDevelopmentFundCouponCid`."""

    unclaimed_development_fund_coupon_cid: Annotated[
        ContractId[UnclaimedDevelopmentFundCoupon], DamlName("unclaimedDevelopmentFundCouponCid")
    ]


@dataclass(frozen=True)
class DevelopmentFundCoupon_DsoExpire:
    """`DevelopmentFundCoupon`'s `DevelopmentFundCoupon_DsoExpire` choice -
    the DSO expires the coupon past its deadline, returning its amount to
    `UnclaimedDevelopmentFundCoupon`. No arguments. Controller `dso`."""


@dataclass(frozen=True)
class DevelopmentFundCoupon_DsoExpireResult:
    """Real Daml: `data DevelopmentFundCoupon_DsoExpireResult` with
    `unclaimedDevelopmentFundCouponCid`."""

    unclaimed_development_fund_coupon_cid: Annotated[
        ContractId[UnclaimedDevelopmentFundCoupon], DamlName("unclaimedDevelopmentFundCouponCid")
    ]


@dataclass(frozen=True)
class UnclaimedReward:
    """The real Daml `UnclaimedReward` template - rewards not claimed by
    anyone, at the disposal of the foundation. Real Daml definition:

        template UnclaimedReward with
            dso : Party
            amount : Decimal
          where
            signatory dso
    """

    dso: Party
    amount: Decimal
