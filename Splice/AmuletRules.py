"""Stand-in for the real `Splice.AmuletRules` Daml module
(`splice/daml/splice-amulet/daml/Splice/AmuletRules.daml`) - IDE/authoring
support only, see `Splice/__init__.py`. Covers `AppTransferContext` and the
rest of the real transfer flow it's used with (`Transfer`, `TransferOutput`,
`exercise_app_transfer`, ...), analyzed directly against that real source.

Field/function names here are DamlForge's usual snake_case convention (the
`.vy` DSL is Python-syntax throughout); real Daml spells them camelCase
(`amuletRules`, `exerciseAppTransfer`, ...). `forge/codegen/emit.py`'s
`_EXTERNAL_BUILTIN_RENAMES`/`_EXTERNAL_FIELD_RENAMES` tables translate
between the two at codegen time - see the "Real dpm build validation
findings" Obsidian note for the full list and why real Daml needs this at
all (it doesn't share Python's `Optional`/casing conventions).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from forge.models.types import ContractId, GenMap, Party, RelTime, Text, Timestamp
from Splice.Amulet import (
    Amulet,
    AmuletCreateSummary,
    AppRewardCoupon,
    DevelopmentFundCoupon,
    FeaturedAppActivityMarker,
    FeaturedAppRight,
    LockedAmulet,
    RewardCouponV2,
    SvRewardCoupon,
    UnclaimedDevelopmentFundCoupon,
    UnclaimedReward,
    ValidatorRewardCoupon,
    ValidatorRight,
)
from Splice.Amulet.CryptoHash import Hash
from Splice.Amulet.RewardAccountingV2 import CalculateRewardsV2, ProcessRewardsV2
from Splice.AmuletConfig import USD, AmuletConfig
from Splice.Api.FeaturedAppRightV1 import AppRewardBeneficiary
from Splice.Api.Token.HoldingV1 import Holding
from Splice.Api.Token.MetadataV1 import Metadata
from Splice.Api.Token.TransferInstructionV1 import TransferInstruction, TransferInstructionResult
from Splice.DecentralizedSynchronizer import MemberTraffic
from Splice.Expiry import TimeLock
from Splice.ExternalPartyConfigState import ExternalPartyConfigState
from Splice.Issuance import OpenMiningRoundSummary
from Splice.Round import ClosedMiningRound, IssuingMiningRound, OpenMiningRound, SummarizingMiningRound
from Splice.Schedule import Schedule
from Splice.Types import Round
from Splice.ValidatorLicense import ValidatorFaucetCoupon, ValidatorLivenessActivityRecord

__all__ = [
    "AmuletRules",
    "OpenMiningRound",
    "FeaturedAppRight",
    "Round",
    "Metadata",
    "BalanceChange",
    "TransferSummary",
    "AppRewardBeneficiary",
    "TimeLock",
    "AppTransferContext",
    "TransferInput",
    "InputAmulet",
    "TransferOutput",
    "Transfer",
    "CreatedAmulet",
    "TransferResultAmulet",
    "TransferResultLockedAmulet",
    "TransferResult",
    "exercise_app_transfer",
    "created_amulet_to_holding",
    "TransferContext",
    "ExternalPartyTransferContext",
    "PaymentTransferContext",
    "OpenMiningRoundTriple",
    "ExternalPartySetupProposal",
    "ExternalPartySetupProposal_Accept",
    "ExternalPartySetupProposal_AcceptResult",
    "ExternalPartySetupProposal_Reject",
    "ExternalPartySetupProposal_RejectResult",
    "ExternalPartySetupProposal_Withdraw",
    "ExternalPartySetupProposal_WithdrawResult",
    "TransferPreapproval",
    "TransferPreapproval_Fetch",
    "TransferPreapproval_Send",
    "TransferPreapproval_SendResult",
    "TransferPreapproval_SendV2",
    "TransferPreapproval_SendV2Result",
    "TransferPreapproval_Renew",
    "TransferPreapproval_RenewResult",
    "TransferPreapproval_Expire",
    "TransferPreapproval_ExpireResult",
    "TransferPreapproval_Cancel",
    "TransferPreapproval_CancelResult",
    "AmuletRules_ExpireTransferInstructionInput",
    "AmuletRules_ComputeFees",
    "AmuletRules_ComputeFeesResult",
    "AmuletRules_Transfer",
    "AmuletRules_CreateExternalPartySetupProposal",
    "AmuletRules_CreateExternalPartySetupProposalResult",
    "AmuletRules_CreateTransferPreapproval",
    "AmuletRules_CreateTransferPreapprovalResult",
    "AmuletRules_BuyMemberTraffic",
    "AmuletRules_BuyMemberTrafficResult",
    "AmuletRules_MergeMemberTrafficContracts",
    "AmuletRules_MergeMemberTrafficContractsResult",
    "AmuletRules_Mint",
    "AmuletRules_MintResult",
    "AmuletRules_DevNet_Tap",
    "AmuletRules_DevNet_TapResult",
    "AmuletRules_DevNet_FeatureApp",
    "AmuletRules_DevNet_FeatureAppResult",
    "AmuletRules_Bootstrap_Rounds",
    "AmuletRules_Bootstrap_RoundsResult",
    "AmuletRules_BootstrapExternalPartyConfigState",
    "AmuletRules_BootstrapExternalPartyConfigStateResult",
    "AmuletRules_AdvanceOpenMiningRounds",
    "AmuletRules_AdvanceOpenMiningRoundsResult",
    "AmuletRules_MiningRound_StartIssuing",
    "AmuletRules_MiningRound_StartIssuingResult",
    "AmuletRules_MiningRound_Close",
    "AmuletRules_MiningRound_CloseResult",
    "AmuletRules_MiningRound_Archive",
    "AmuletRules_MiningRound_ArchiveResult",
    "AmuletRules_ClaimExpiredRewards",
    "AmuletRules_ClaimExpiredRewardsResult",
    "AmuletRules_ClaimExpiredRewardsV2",
    "AmuletRules_ClaimExpiredRewardsV2Result",
    "AmuletRules_StartProcessingRewardsV2",
    "AmuletRules_StartProcessingRewardsV2Result",
    "AmuletRules_UnhideRewardCouponsV2",
    "AmuletRules_UnhideRewardCouponsV2Result",
    "AmuletRules_ArchiveDryRunRewardAccountingV2",
    "AmuletRules_ArchiveDryRunRewardAccountingV2Result",
    "AmuletRules_MergeUnclaimedRewards",
    "AmuletRules_MergeUnclaimedRewardsResult",
    "AmuletRules_MergeUnclaimedDevelopmentFundCoupons",
    "AmuletRules_MergeUnclaimedDevelopmentFundCouponsResult",
    "AmuletRules_AllocateDevelopmentFundCoupon",
    "AmuletRules_AllocateDevelopmentFundCouponResult",
    "AmuletRules_Fetch",
    "AmuletRules_SetConfig",
    "AmuletRules_SetConfigResult",
    "AmuletRules_AddFutureAmuletConfigSchedule",
    "AmuletRules_AddFutureAmuletConfigScheduleResult",
    "AmuletRules_RemoveFutureAmuletConfigSchedule",
    "AmuletRules_RemoveFutureAmuletConfigScheduleResult",
    "AmuletRules_UpdateFutureAmuletConfigSchedule",
    "AmuletRules_UpdateFutureAmuletConfigScheduleResult",
    "AmuletRules_ConvertFeaturedAppActivityMarkers",
    "AmuletRules_ConvertFeaturedAppActivityMarkersResult",
    "AmuletRules_Amulet_ExpireTransferInstructions",
    "AmuletRules_Amulet_ExpireTransferInstructionsResult",
    "AmuletRules_UpdateExternalPartyConfigStates",
    "AmuletRules_UpdateExternalPartyConfigStatesResult",
]


@dataclass(frozen=True)
class AmuletRules:
    """The real Daml `AmuletRules` template - the network-wide config/rules
    contract every Amulet transfer runs against. Real Daml definition:

        template AmuletRules
          with
            dso : Party
            configSchedule : Schedule Time (AmuletConfig Unit.USD)
            isDevNet : Bool
            contractStateSchemaVersion : Optional Int
          where
            signatory dso

    All 31 real choices (`AmuletRules_Transfer`, `AmuletRules_Mint`,
    SV-governance/dev-net-tap/fee-schedule/reward-accounting operations,
    ...) are modeled below too, each as a dataclass matching its argument
    record plus a separate result type - the same pattern used throughout
    `Splice.Amulet`.
    """

    dso: Party
    config_schedule: Schedule[Timestamp, AmuletConfig[USD]]
    is_dev_net: bool
    contract_state_schema_version: Optional[int] = None


# Every type imported above (`OpenMiningRound`/`SummarizingMiningRound`/
# `IssuingMiningRound`/`ClosedMiningRound` from `Splice.Round`,
# `FeaturedAppRight`/`LockedAmulet`/`ValidatorRight`/reward-coupon templates
# from `Splice.Amulet`, `AppRewardBeneficiary` from
# `Splice.Api.FeaturedAppRightV1`, `TimeLock` from `Splice.Expiry`, `Round`
# from `Splice.Types`, `Metadata`/`Holding`/`TransferInstruction*` from
# `Splice.Api.Token.*`, `MemberTraffic` from
# `Splice.DecentralizedSynchronizer`, `OpenMiningRoundSummary` from
# `Splice.Issuance`, `ValidatorFaucetCoupon`/`ValidatorLivenessActivityRecord`
# from `Splice.ValidatorLicense`, `CalculateRewardsV2`/`ProcessRewardsV2`
# from `Splice.Amulet.RewardAccountingV2`) is imported rather than defined
# here, matching real Daml: `module Splice.AmuletRules where` has no
# explicit export list, so it re-exports everything it imports unqualified -
# `from Splice.AmuletRules import OpenMiningRound` genuinely works against
# the real compiler even though `OpenMiningRound` is truly defined
# elsewhere. Importing (not redefining) here keeps ONE real class per real
# Daml type, rather than two unrelated stand-ins that happen to share a name.


@dataclass(frozen=True)
class BalanceChange:
    """The real Daml `BalanceChange` record - one party's contribution to a
    `TransferSummary`'s balance accounting. Real Daml definition:

        data BalanceChange = BalanceChange with
            changeToInitialAmountAsOfRoundZero : Decimal
            changeToHoldingFeesRate : Decimal
          deriving (Show, Eq)
    """

    change_to_initial_amount_as_of_round_zero: Decimal
    change_to_holding_fees_rate: Decimal


@dataclass(frozen=True)
class TransferSummary:
    """The real Daml `TransferSummary` record - fee/amount accounting detail
    attached to a `TransferResult`. Real Daml definition:

        data TransferSummary = TransferSummary with
            inputAppRewardAmount : Decimal
            inputValidatorRewardAmount : Decimal
            inputSvRewardAmount : Decimal
            inputAmuletAmount : Decimal
            balanceChanges : Map Party BalanceChange
            holdingFees : Decimal
            outputFees : [Decimal]
            senderChangeFee : Decimal
          deriving (Show, Eq)
    """

    input_app_reward_amount: Decimal
    input_validator_reward_amount: Decimal
    input_sv_reward_amount: Decimal
    input_amulet_amount: Decimal
    balance_changes: GenMap[Party, BalanceChange]
    holding_fees: Decimal
    output_fees: list[Decimal]
    sender_change_fee: Decimal


@dataclass(frozen=True)
class AppTransferContext:
    """The real Daml `AppTransferContext` record - the ledger context an app
    provider passes into `exercise_app_transfer` to run an Amulet transfer
    ``as`` a featured app, if it has one. Real Daml definition:

        data AppTransferContext = AppTransferContext
          with
            amuletRules : ContractId AmuletRules
            openMiningRound : ContractId OpenMiningRound
            featuredAppRight : Optional (ContractId FeaturedAppRight)
          deriving (Show, Eq)

    Passed as a plain choice argument in every real usage in this codebase's
    examples (`loan_terms.vy`, `funding_campaign.vy`) - never constructed
    directly by DamlForge-compiled code, since it comes from the caller's
    off-ledger client, not from ledger data `.vy` code can read.
    """

    amulet_rules: ContractId[AmuletRules]
    open_mining_round: ContractId[OpenMiningRound]
    featured_app_right: Optional[ContractId[FeaturedAppRight]]


# `TransferInput` is a real Daml variant/sum type DamlForge has no syntax
# for (see "No variant/tagged-union types" in "Findings from porting real
# Daml contracts"). Modeled here as a plain marker type plus one function per
# constructor actually used by this codebase's real examples - each renders
# as an ordinary function call in generated Daml, which already happens to
# be valid syntax for applying a data constructor. Only `InputAmulet` is
# covered; add further constructors (`InputAppRewardCoupon`, `InputSvRewardCoupon`,
# ...) here the same way if/when a real `.vy` example needs them.
class TransferInput:
    """The real Daml `TransferInput` variant type - one input into a batch
    `Transfer`. Never constructed directly; use `InputAmulet(...)`."""


def InputAmulet(amulet_cid: ContractId[Amulet]) -> TransferInput:
    """The real Daml `TransferInput`'s `InputAmulet` constructor - an Amulet
    contract used as a transfer input."""
    raise NotImplementedError(
        "InputAmulet is a real Daml data constructor - only meaningful inside "
        "compiled .vy source, not callable directly from Python"
    )


@dataclass(frozen=True)
class TransferOutput:
    """The real Daml `TransferOutput` record - one output of a batch
    `Transfer`. Real Daml definition:

        data TransferOutput = TransferOutput with
            receiver : Party
            receiverFeeRatio : Decimal
            amount : Decimal
            lock : Optional TimeLock
            meta : Optional Metadata
          deriving (Eq, Ord, Show)
    """

    receiver: Party
    receiver_fee_ratio: Decimal
    amount: Decimal
    lock: Optional[TimeLock]
    meta: Optional[Metadata] = None


@dataclass(frozen=True)
class Transfer:
    """The real Daml `Transfer` record - a batch transfer of one or more
    `TransferInput`s to one or more `TransferOutput`s. Real Daml definition:

        data Transfer = Transfer with
            sender : Party
            provider : Party
            inputs : [TransferInput]
            outputs : [TransferOutput]
            beneficiaries : Optional [AppRewardBeneficiary]
          deriving (Eq, Ord, Show)
    """

    sender: Party
    provider: Party
    inputs: list[TransferInput]
    outputs: list[TransferOutput]
    beneficiaries: Optional[list[AppRewardBeneficiary]] = None


# `CreatedAmulet` is another real Daml variant type - same treatment as
# `TransferInput` above. Only the two constructors this codebase's real
# examples actually pattern-match toward are covered.
class CreatedAmulet:
    """The real Daml `CreatedAmulet` variant type - one amulet created as a
    result of a `Transfer`. Values of this type come from a `TransferResult`
    read off the ledger; never constructed directly by DamlForge code."""


def TransferResultAmulet(amulet_cid: ContractId[Amulet]) -> CreatedAmulet:
    """The real Daml `CreatedAmulet`'s `TransferResultAmulet` constructor."""
    raise NotImplementedError(
        "TransferResultAmulet is a real Daml data constructor - only meaningful "
        "inside compiled .vy source, not callable directly from Python"
    )


def TransferResultLockedAmulet(locked_amulet_cid: ContractId[LockedAmulet]) -> CreatedAmulet:
    """The real Daml `CreatedAmulet`'s `TransferResultLockedAmulet`
    constructor - `LockedAmulet` lives in `Splice.Amulet`."""
    raise NotImplementedError(
        "TransferResultLockedAmulet is a real Daml data constructor - only "
        "meaningful inside compiled .vy source, not callable directly from Python"
    )


@dataclass(frozen=True)
class TransferResult:
    """The real Daml `TransferResult` record, returned by
    `exercise_app_transfer`. Real Daml definition:

        data TransferResult = TransferResult with
            round : Round
            summary : TransferSummary
            createdAmulets : [CreatedAmulet]
            senderChangeAmulet : Optional (ContractId Amulet)
            meta : Optional Metadata
          deriving (Show, Eq)
    """

    round: Round
    summary: TransferSummary
    created_amulets: list[CreatedAmulet]
    sender_change_amulet: Optional[ContractId[Amulet]]
    meta: Optional[Metadata] = None


def exercise_app_transfer(
    expected_dso: Party, context: AppTransferContext, transfer: Transfer
) -> ContractId[TransferResult]:
    """The real Daml `exerciseAppTransfer`, the canonical way to run a
    `Transfer` as a featured app provider:

        exerciseAppTransfer : Party -> AppTransferContext -> Transfer -> Update TransferResult

    A real ledger effect (`Update`) - only meaningful inside a
    `@ledger_effect`-decorated `.vy` function or a `@choice` body, matching
    every real usage in this codebase's examples."""
    raise NotImplementedError(
        "exercise_app_transfer is a real Daml ledger operation - only meaningful "
        "inside compiled .vy source, not callable directly from Python"
    )


def created_amulet_to_holding(created_amulet: CreatedAmulet) -> ContractId[Holding]:
    """The real Daml `createdAmuletToHolding`, converting a `CreatedAmulet`
    into a `ContractId Splice.Api.Token.HoldingV1.Holding`:

        createdAmuletToHolding : CreatedAmulet -> ContractId Api.Token.HoldingV1.Holding
    """
    raise NotImplementedError(
        "created_amulet_to_holding is a real Daml function - only meaningful "
        "inside compiled .vy source, not callable directly from Python"
    )


# ---------------------------------------------------------------------------
# Contexts and standalone templates `AmuletRules`'s choices reference
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TransferContext:
    """The real Daml `TransferContext` record - contracts that need to be
    passed into a `Transfer` by contract id instead of by key. Real Daml
    definition:

        data TransferContext = TransferContext
          with
            openMiningRound : ContractId OpenMiningRound
            issuingMiningRounds : Map Round (ContractId IssuingMiningRound)
            validatorRights : Map Party (ContractId ValidatorRight)
            featuredAppRight : Optional (ContractId FeaturedAppRight)
          deriving (Show, Eq)
    """

    open_mining_round: ContractId[OpenMiningRound]
    issuing_mining_rounds: GenMap[Round, ContractId[IssuingMiningRound]]
    validator_rights: GenMap[Party, ContractId[ValidatorRight]]
    featured_app_right: Optional[ContractId[FeaturedAppRight]] = None


@dataclass(frozen=True)
class ExternalPartyTransferContext:
    """The real Daml `ExternalPartyTransferContext` record - contracts
    needed for a `Transfer` run by an external party without a validator of
    their own (`TransferPreapproval_SendV2` uses it); unlike
    `TransferContext`, it carries no `issuingMiningRounds`/`validatorRights`
    since those are only needed for minting rewards, which external-party
    transfers don't do. Real Daml definition:

        data ExternalPartyTransferContext = ExternalPartyTransferContext
          with
            externalPartyConfigState : ContractId ExternalPartyConfigState
            featuredAppRight : Optional (ContractId FeaturedAppRight)
          deriving (Show, Eq)
    """

    external_party_config_state: ContractId[ExternalPartyConfigState]
    featured_app_right: Optional[ContractId[FeaturedAppRight]] = None


@dataclass(frozen=True)
class PaymentTransferContext:
    """The real Daml `PaymentTransferContext` record - the context needed to
    run a `Transfer` via `exercisePaymentTransfer`
    (`AmuletRules_CreateExternalPartySetupProposal`/
    `AmuletRules_CreateTransferPreapproval` use it). Real Daml definition:

        data PaymentTransferContext = PaymentTransferContext
          with
            amuletRules : ContractId AmuletRules
            context : TransferContext
          deriving (Eq, Show)
    """

    amulet_rules: ContractId[AmuletRules]
    context: TransferContext


@dataclass(frozen=True)
class OpenMiningRoundTriple:
    """The real Daml `OpenMiningRoundTriple` record - the 3 simultaneously-
    open mining rounds bootstrapping/config-update choices operate over.
    Real Daml definition:

        data OpenMiningRoundTriple = OpenMiningRoundTriple
          with
            round0Cid : ContractId OpenMiningRound
            round1Cid : ContractId OpenMiningRound
            round2Cid : ContractId OpenMiningRound
          deriving (Show, Eq)
    """

    round0_cid: ContractId[OpenMiningRound]
    round1_cid: ContractId[OpenMiningRound]
    round2_cid: ContractId[OpenMiningRound]


@dataclass(frozen=True)
class ExternalPartySetupProposal:
    """The real Daml `ExternalPartySetupProposal` template (defined directly
    in `Splice.AmuletRules`) - a validator's proposal to host an external
    party, created by `AmuletRules_CreateExternalPartySetupProposal`. Real
    Daml definition:

        template ExternalPartySetupProposal
          with
            validator : Party
            user : Party
            dso : Party
            createdAt : Time
            preapprovalExpiresAt : Time
          where
            signatory validator, dso
            observer user
    """

    validator: Party
    user: Party
    dso: Party
    created_at: Timestamp
    preapproval_expires_at: Timestamp


@dataclass(frozen=True)
class ExternalPartySetupProposal_Accept:
    """`ExternalPartySetupProposal`'s `ExternalPartySetupProposal_Accept`
    choice - the user accepts, creating a `ValidatorRight` and a
    `TransferPreapproval`. No arguments. Controller `user`."""


@dataclass(frozen=True)
class ExternalPartySetupProposal_AcceptResult:
    """Real Daml: `data ExternalPartySetupProposal_AcceptResult` with
    `validatorRightCid`, `transferPreapprovalCid`."""

    validator_right_cid: ContractId[ValidatorRight]
    transfer_preapproval_cid: ContractId[TransferPreapproval]


@dataclass(frozen=True)
class ExternalPartySetupProposal_Reject:
    """`ExternalPartySetupProposal`'s `ExternalPartySetupProposal_Reject`
    choice - the user always may reject the proposal. Controller `user`.
    Real Daml:

        choice ExternalPartySetupProposal_Reject : ExternalPartySetupProposal_RejectResult
          with
            reason : Text
    """

    reason: Text


@dataclass(frozen=True)
class ExternalPartySetupProposal_RejectResult:
    """Real Daml: `data ExternalPartySetupProposal_RejectResult` with
    `dummyArg : ()` (kept only so the record can be upgraded later)."""

    dummy_arg: tuple = ()


@dataclass(frozen=True)
class ExternalPartySetupProposal_Withdraw:
    """`ExternalPartySetupProposal`'s `ExternalPartySetupProposal_Withdraw`
    choice - the validator always may withdraw the proposal, including
    after expiry. Controller `validator`. Real Daml:

        choice ExternalPartySetupProposal_Withdraw : ExternalPartySetupProposal_WithdrawResult
          with
            reason : Text
    """

    reason: Text


@dataclass(frozen=True)
class ExternalPartySetupProposal_WithdrawResult:
    """Real Daml: `data ExternalPartySetupProposal_WithdrawResult` with
    `dummyArg : ()` (kept only so the record can be upgraded later)."""

    dummy_arg: tuple = ()


@dataclass(frozen=True)
class TransferPreapproval:
    """The real Daml `TransferPreapproval` template (defined directly in
    `Splice.AmuletRules`) - a receiver's pre-approval to receive Amulet from
    anybody, created by `AmuletRules_CreateTransferPreapproval`. Real Daml
    definition:

        template TransferPreapproval
          with
            dso : Party
            receiver : Party
            provider : Party
            validFrom : Time
            lastRenewedAt : Time
            expiresAt : Time
          where
            signatory receiver, provider, dso
    """

    dso: Party
    receiver: Party
    provider: Party
    valid_from: Timestamp
    last_renewed_at: Timestamp
    expires_at: Timestamp


@dataclass(frozen=True)
class TransferPreapproval_Fetch:
    """`TransferPreapproval`'s `TransferPreapproval_Fetch` choice - a
    `nonconsuming` fetchByKey-style read; result IS `TransferPreapproval`
    itself. Controller `p`. Real Daml:

        nonconsuming choice TransferPreapproval_Fetch : TransferPreapproval
          with
            p : Party
          do pure this
    """

    p: Party


@dataclass(frozen=True)
class TransferPreapproval_Send:
    """DEPRECATED in real Daml - use `TransferPreapproval_SendV2` instead.
    Transfers `amount` of Amulet to `receiver` via this pre-approval.
    Controller `sender`. Real Daml:

        nonconsuming choice TransferPreapproval_Send : TransferPreapproval_SendResult
          with
            context : PaymentTransferContext
            inputs : [TransferInput]
            amount : Decimal
            sender : Party
            description : Optional Text
    """

    context: PaymentTransferContext
    inputs: list[TransferInput]
    amount: Decimal
    sender: Party
    description: Optional[Text] = None


@dataclass(frozen=True)
class TransferPreapproval_SendResult:
    """Real Daml: `data TransferPreapproval_SendResult` with `result :
    TransferResult`, `meta : Optional Metadata`."""

    result: TransferResult
    meta: Optional[Metadata] = None


@dataclass(frozen=True)
class TransferPreapproval_SendV2:
    """`TransferPreapproval`'s `TransferPreapproval_SendV2` choice -
    transfers `amount` of Amulet to `receiver` via this pre-approval, for an
    external party without a validator of their own. Controller `sender`.
    Real Daml:

        nonconsuming choice TransferPreapproval_SendV2 : TransferPreapproval_SendV2Result
          with
            context : ExternalPartyTransferContext
            inputs : [TransferInput]
            amount : Decimal
            sender : Party
            description : Optional Text
            meta : Optional Metadata
    """

    context: ExternalPartyTransferContext
    inputs: list[TransferInput]
    amount: Decimal
    sender: Party
    description: Optional[Text] = None
    meta: Optional[Metadata] = None


@dataclass(frozen=True)
class TransferPreapproval_SendV2Result:
    """Real Daml: `data TransferPreapproval_SendV2Result` with `result :
    TransferResult`, `meta : Metadata`."""

    result: TransferResult
    meta: Metadata


@dataclass(frozen=True)
class TransferPreapproval_Renew:
    """`TransferPreapproval`'s `TransferPreapproval_Renew` choice - the
    provider extends `expiresAt`, paying any renewal fee due. Controller
    `provider`. Real Daml:

        choice TransferPreapproval_Renew : TransferPreapproval_RenewResult
          with
            context : PaymentTransferContext
            inputs : [TransferInput]
            newExpiresAt : Time
    """

    context: PaymentTransferContext
    inputs: list[TransferInput]
    new_expires_at: Timestamp


@dataclass(frozen=True)
class TransferPreapproval_RenewResult:
    """Real Daml: `data TransferPreapproval_RenewResult` with
    `transferPreapprovalCid`, `transferResult`, `receiver`, `provider`,
    `amuletPaid`, `meta`."""

    transfer_preapproval_cid: ContractId[TransferPreapproval]
    transfer_result: TransferResult
    receiver: Party
    provider: Party
    amulet_paid: Decimal
    meta: Optional[Metadata] = None


@dataclass(frozen=True)
class TransferPreapproval_Expire:
    """`TransferPreapproval`'s `TransferPreapproval_Expire` choice - used by
    the DSO party to archive expired contracts. No arguments. Controller
    `dso`."""


@dataclass(frozen=True)
class TransferPreapproval_ExpireResult:
    """Real Daml: `data TransferPreapproval_ExpireResult =
    TransferPreapproval_ExpireResult {}` (no fields)."""


@dataclass(frozen=True)
class TransferPreapproval_Cancel:
    """`TransferPreapproval`'s `TransferPreapproval_Cancel` choice -
    cancels the contract as the receiver or provider. Controller `p`. Real
    Daml:

        choice TransferPreapproval_Cancel : TransferPreapproval_CancelResult
          with
            p : Party
    """

    p: Party


@dataclass(frozen=True)
class TransferPreapproval_CancelResult:
    """Real Daml: `data TransferPreapproval_CancelResult =
    TransferPreapproval_CancelResult` (no fields)."""


@dataclass(frozen=True)
class AmuletRules_ExpireTransferInstructionInput:
    """The real Daml `AmuletRules_ExpireTransferInstructionInput` record -
    one input to `AmuletRules_Amulet_ExpireTransferInstructions`. Real Daml
    definition:

        data AmuletRules_ExpireTransferInstructionInput = AmuletRules_ExpireTransferInstructionInput
          with
            transferInstructionCid : ContractId TransferInstruction
            expireLock : Bool
          deriving (Eq, Show)
    """

    transfer_instruction_cid: ContractId[TransferInstruction]
    expire_lock: bool


# ---------------------------------------------------------------------------
# AmuletRules's 31 real choices, in the order they appear in real Daml
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AmuletRules_ComputeFees:
    """DEPRECATED in real Daml (`deprecatedChoice`, which aborts) - use
    `AmuletRules_Transfer`'s result instead. Modeled for completeness. Real
    Daml: `choice AmuletRules_ComputeFees` with `context`, `sender`,
    `outputs`, `expectedDso`, controller `sender`."""

    context: TransferContext
    sender: Party
    outputs: list[TransferOutput]
    expected_dso: Optional[Party] = None


@dataclass(frozen=True)
class AmuletRules_ComputeFeesResult:
    """Real Daml: `data AmuletRules_ComputeFeesResult = ... with fees : [Decimal]`."""

    fees: list[Decimal]


@dataclass(frozen=True)
class AmuletRules_Transfer:
    """`AmuletRules`'s `AmuletRules_Transfer` choice - the canonical way to
    run a batch `Transfer`; result type is `TransferResult` itself (no
    separate result record). Controller: the transfer's controllers
    (sender, and any lock holders on locked-amulet outputs). Real Daml:

        nonconsuming choice AmuletRules_Transfer : TransferResult
          with
            transfer : Transfer
            context : TransferContext
            expectedDso : Optional Party
    """

    transfer: Transfer
    context: TransferContext
    expected_dso: Optional[Party] = None


@dataclass(frozen=True)
class AmuletRules_CreateExternalPartySetupProposal:
    """`AmuletRules`'s `AmuletRules_CreateExternalPartySetupProposal` choice
    - a validator proposes to host an external party, pre-paying the fees
    for the `TransferPreapproval` created on acceptance. Controller
    `validator`. Real Daml:

        nonconsuming choice AmuletRules_CreateExternalPartySetupProposal : AmuletRules_CreateExternalPartySetupProposalResult
          with
            context : PaymentTransferContext
            inputs : [TransferInput]
            user : Party
            validator : Party
            preapprovalExpiresAt : Time
            expectedDso : Optional Party
            optCreatedAt : Optional Time
    """

    context: PaymentTransferContext
    inputs: list[TransferInput]
    user: Party
    validator: Party
    preapproval_expires_at: Timestamp
    expected_dso: Optional[Party] = None
    opt_created_at: Optional[Timestamp] = None


@dataclass(frozen=True)
class AmuletRules_CreateExternalPartySetupProposalResult:
    """Real Daml: `data AmuletRules_CreateExternalPartySetupProposalResult`
    with `proposalCid`, `user`, `validator`, `transferResult`,
    `amuletPaid`, `meta`."""

    proposal_cid: ContractId[ExternalPartySetupProposal]
    user: Party
    validator: Party
    transfer_result: TransferResult
    amulet_paid: Decimal
    meta: Optional[Metadata] = None


@dataclass(frozen=True)
class AmuletRules_CreateTransferPreapproval:
    """`AmuletRules`'s `AmuletRules_CreateTransferPreapproval` choice - pre-
    approve incoming Amulet transfers for `receiver`. Controller `provider`,
    `receiver`. Real Daml:

        nonconsuming choice AmuletRules_CreateTransferPreapproval : AmuletRules_CreateTransferPreapprovalResult
          with
            context : PaymentTransferContext
            inputs : [TransferInput]
            receiver : Party
            provider : Party
            expiresAt : Time
            expectedDso : Optional Party
            optCreatedAt : Optional Time
    """

    context: PaymentTransferContext
    inputs: list[TransferInput]
    receiver: Party
    provider: Party
    expires_at: Timestamp
    expected_dso: Optional[Party] = None
    opt_created_at: Optional[Timestamp] = None


@dataclass(frozen=True)
class AmuletRules_CreateTransferPreapprovalResult:
    """Real Daml: `data AmuletRules_CreateTransferPreapprovalResult` with
    `transferPreapprovalCid`, `transferResult`, `amuletPaid`, `meta`."""

    transfer_preapproval_cid: ContractId[TransferPreapproval]
    transfer_result: TransferResult
    amulet_paid: Decimal
    meta: Optional[Metadata] = None


@dataclass(frozen=True)
class AmuletRules_BuyMemberTraffic:
    """`AmuletRules`'s `AmuletRules_BuyMemberTraffic` choice - purchases
    extra sequencer traffic for a synchronizer member. Controller
    `provider`. Real Daml:

        nonconsuming choice AmuletRules_BuyMemberTraffic : AmuletRules_BuyMemberTrafficResult
          with
            inputs : [TransferInput]
            context : TransferContext
            provider : Party
            memberId : Text
            synchronizerId : Text
            migrationId : Int
            trafficAmount : Int
            expectedDso : Optional Party
    """

    inputs: list[TransferInput]
    context: TransferContext
    provider: Party
    member_id: Text
    synchronizer_id: Text
    migration_id: int
    traffic_amount: int
    expected_dso: Optional[Party] = None


@dataclass(frozen=True)
class AmuletRules_BuyMemberTrafficResult:
    """Real Daml: `data AmuletRules_BuyMemberTrafficResult` with `round`,
    `summary`, `amuletPaid`, `purchasedTraffic`, `senderChangeAmulet`,
    `meta`."""

    round: Round
    summary: TransferSummary
    amulet_paid: Decimal
    purchased_traffic: ContractId[MemberTraffic]
    sender_change_amulet: Optional[ContractId[Amulet]] = None
    meta: Optional[Metadata] = None


@dataclass(frozen=True)
class AmuletRules_MergeMemberTrafficContracts:
    """`AmuletRules`'s `AmuletRules_MergeMemberTrafficContracts` choice -
    batch-merges several `MemberTraffic` contracts for the same member into
    one. Controller `dso`. Real Daml:

        nonconsuming choice AmuletRules_MergeMemberTrafficContracts : AmuletRules_MergeMemberTrafficContractsResult
          with
            trafficCids : [ContractId MemberTraffic]
    """

    traffic_cids: list[ContractId[MemberTraffic]]


@dataclass(frozen=True)
class AmuletRules_MergeMemberTrafficContractsResult:
    """Real Daml: `data AmuletRules_MergeMemberTrafficContractsResult` with
    `mergedTrafficCid`."""

    merged_traffic_cid: ContractId[MemberTraffic]


@dataclass(frozen=True)
class AmuletRules_Mint:
    """DEPRECATED in real Daml - use `AmuletRules_DevNet_Tap` instead. Mints
    Amulet in a DevNet setup. Controller `dso`, `receiver`. Real Daml:

        nonconsuming choice AmuletRules_Mint : AmuletRules_MintResult
          with
            receiver : Party
            amount : Decimal
            openRound : ContractId OpenMiningRound
            reason : Optional Text
    """

    receiver: Party
    amount: Decimal
    open_round: ContractId[OpenMiningRound]
    reason: Optional[Text] = None


@dataclass(frozen=True)
class AmuletRules_MintResult:
    """Real Daml: `data AmuletRules_MintResult` with `amuletSum`."""

    amulet_sum: AmuletCreateSummary[ContractId[Amulet]]


@dataclass(frozen=True)
class AmuletRules_DevNet_Tap:
    """`AmuletRules`'s `AmuletRules_DevNet_Tap` choice - the DevNet faucet;
    mints up to 100,000,000 Amulet for `receiver`. Controller `receiver`.
    Real Daml:

        nonconsuming choice AmuletRules_DevNet_Tap : AmuletRules_DevNet_TapResult
          with
            receiver : Party
            amount : Decimal
            openRound : ContractId OpenMiningRound
    """

    receiver: Party
    amount: Decimal
    open_round: ContractId[OpenMiningRound]


@dataclass(frozen=True)
class AmuletRules_DevNet_TapResult:
    """Real Daml: `data AmuletRules_DevNet_TapResult` with `amuletSum`,
    `meta`."""

    amulet_sum: AmuletCreateSummary[ContractId[Amulet]]
    meta: Optional[Metadata] = None


@dataclass(frozen=True)
class AmuletRules_DevNet_FeatureApp:
    """`AmuletRules`'s `AmuletRules_DevNet_FeatureApp` choice - grants
    `provider` a `FeaturedAppRight` in a DevNet setup, bypassing normal SV
    governance. Controller `provider`. Real Daml:

        nonconsuming choice AmuletRules_DevNet_FeatureApp : AmuletRules_DevNet_FeatureAppResult
          with
            provider : Party
    """

    provider: Party


@dataclass(frozen=True)
class AmuletRules_DevNet_FeatureAppResult:
    """Real Daml: `data AmuletRules_DevNet_FeatureAppResult` with
    `featuredAppRightCid`."""

    featured_app_right_cid: ContractId[FeaturedAppRight]


@dataclass(frozen=True)
class AmuletRules_Bootstrap_Rounds:
    """`AmuletRules`'s `AmuletRules_Bootstrap_Rounds` choice - bootstraps
    the first 3 `OpenMiningRound`s at network genesis; should only be
    called once. Controller `dso`. Real Daml:

        nonconsuming choice AmuletRules_Bootstrap_Rounds : AmuletRules_Bootstrap_RoundsResult
          with
            amuletPrice : Decimal
            round0Duration : RelTime
            initialRound : Optional Int
    """

    amulet_price: Decimal
    round0_duration: RelTime
    initial_round: Optional[int] = None


@dataclass(frozen=True)
class AmuletRules_Bootstrap_RoundsResult:
    """Real Daml: `data AmuletRules_Bootstrap_RoundsResult` with
    `openMiningRoundCid`, `initialRound`."""

    open_mining_round_cid: ContractId[OpenMiningRound]
    initial_round: Optional[Round] = None


@dataclass(frozen=True)
class AmuletRules_BootstrapExternalPartyConfigState:
    """`AmuletRules`'s `AmuletRules_BootstrapExternalPartyConfigState`
    choice - bootstraps the initial `ExternalPartyConfigState` contracts.
    Controller `dso`. Real Daml:

        nonconsuming choice AmuletRules_BootstrapExternalPartyConfigState : AmuletRules_BootstrapExternalPartyConfigStateResult
          with
            openMiningRoundTriple : OpenMiningRoundTriple
            expectedDso : Party
    """

    open_mining_round_triple: OpenMiningRoundTriple
    expected_dso: Party


@dataclass(frozen=True)
class AmuletRules_BootstrapExternalPartyConfigStateResult:
    """Real Daml: `data AmuletRules_BootstrapExternalPartyConfigStateResult
    = AmuletRules_BootstrapExternalPartyConfigStateResult` (no fields)."""


@dataclass(frozen=True)
class AmuletRules_AdvanceOpenMiningRounds:
    """`AmuletRules`'s `AmuletRules_AdvanceOpenMiningRounds` choice -
    archives the oldest open round, opens a new one, and starts summarizing
    the archived one. Controller `dso`. Real Daml:

        nonconsuming choice AmuletRules_AdvanceOpenMiningRounds : AmuletRules_AdvanceOpenMiningRoundsResult
          with
            amuletPrice : Decimal
            roundToArchiveCid : ContractId OpenMiningRound
            middleRoundCid : ContractId OpenMiningRound
            latestRoundCid : ContractId OpenMiningRound
    """

    amulet_price: Decimal
    round_to_archive_cid: ContractId[OpenMiningRound]
    middle_round_cid: ContractId[OpenMiningRound]
    latest_round_cid: ContractId[OpenMiningRound]


@dataclass(frozen=True)
class AmuletRules_AdvanceOpenMiningRoundsResult:
    """Real Daml: `data AmuletRules_AdvanceOpenMiningRoundsResult` with
    `summarizingRoundCid`, `openRoundCid`."""

    summarizing_round_cid: ContractId[SummarizingMiningRound]
    open_round_cid: ContractId[OpenMiningRound]


@dataclass(frozen=True)
class AmuletRules_MiningRound_StartIssuing:
    """`AmuletRules`'s `AmuletRules_MiningRound_StartIssuing` choice - turns
    a `SummarizingMiningRound` into an `IssuingMiningRound` once its
    off-ledger reward totals (`summary`) are known. Controller `dso`. Real
    Daml:

        nonconsuming choice AmuletRules_MiningRound_StartIssuing : AmuletRules_MiningRound_StartIssuingResult
          with
            miningRoundCid : ContractId SummarizingMiningRound
            summary : OpenMiningRoundSummary
    """

    mining_round_cid: ContractId[SummarizingMiningRound]
    summary: OpenMiningRoundSummary


@dataclass(frozen=True)
class AmuletRules_MiningRound_StartIssuingResult:
    """Real Daml: `data AmuletRules_MiningRound_StartIssuingResult` with
    `issuingRoundCid`, `unclaimedDevelopmentFundCouponCid`."""

    issuing_round_cid: ContractId[IssuingMiningRound]
    unclaimed_development_fund_coupon_cid: Optional[ContractId[UnclaimedDevelopmentFundCoupon]] = None


@dataclass(frozen=True)
class AmuletRules_MiningRound_Close:
    """`AmuletRules`'s `AmuletRules_MiningRound_Close` choice - closes an
    `IssuingMiningRound` once past `targetClosesAt`. Controller `dso`. Real
    Daml:

        nonconsuming choice AmuletRules_MiningRound_Close : AmuletRules_MiningRound_CloseResult
          with
            issuingRoundCid : ContractId IssuingMiningRound
    """

    issuing_round_cid: ContractId[IssuingMiningRound]


@dataclass(frozen=True)
class AmuletRules_MiningRound_CloseResult:
    """Real Daml: `data AmuletRules_MiningRound_CloseResult` with
    `closedRoundCid`."""

    closed_round_cid: ContractId[ClosedMiningRound]


@dataclass(frozen=True)
class AmuletRules_MiningRound_Archive:
    """`AmuletRules`'s `AmuletRules_MiningRound_Archive` choice - archives a
    `ClosedMiningRound` once all its rewards have expired. Controller
    `dso`. Real Daml:

        nonconsuming choice AmuletRules_MiningRound_Archive : AmuletRules_MiningRound_ArchiveResult
          with
            closedRoundCid : ContractId ClosedMiningRound
    """

    closed_round_cid: ContractId[ClosedMiningRound]


@dataclass(frozen=True)
class AmuletRules_MiningRound_ArchiveResult:
    """Real Daml: `data AmuletRules_MiningRound_ArchiveResult =
    AmuletRules_MiningRound_ArchiveResult` (no fields)."""


@dataclass(frozen=True)
class AmuletRules_ClaimExpiredRewards:
    """`AmuletRules`'s `AmuletRules_ClaimExpiredRewards` choice - batch
    expiry of unclaimed pre-CIP-104 reward coupons for a closed round.
    Controller `dso`. Real Daml:

        nonconsuming choice AmuletRules_ClaimExpiredRewards : AmuletRules_ClaimExpiredRewardsResult
          with
            closedRoundCid : ContractId ClosedMiningRound
            validatorRewardCouponCids : [ContractId ValidatorRewardCoupon]
            appCouponCids : [ContractId AppRewardCoupon]
            svRewardCouponCids : [ContractId SvRewardCoupon]
            optValidatorFaucetCouponCids : Optional [ContractId ValidatorFaucetCoupon]
            optValidatorLivenessActivityRecordCids : Optional [ContractId ValidatorLivenessActivityRecord]
    """

    closed_round_cid: ContractId[ClosedMiningRound]
    validator_reward_coupon_cids: list[ContractId[ValidatorRewardCoupon]]
    app_coupon_cids: list[ContractId[AppRewardCoupon]]
    sv_reward_coupon_cids: list[ContractId[SvRewardCoupon]]
    opt_validator_faucet_coupon_cids: Optional[list[ContractId[ValidatorFaucetCoupon]]] = None
    opt_validator_liveness_activity_record_cids: Optional[
        list[ContractId[ValidatorLivenessActivityRecord]]
    ] = None


@dataclass(frozen=True)
class AmuletRules_ClaimExpiredRewardsResult:
    """Real Daml: `data AmuletRules_ClaimExpiredRewardsResult` with
    `unclaimedRewardCid`."""

    unclaimed_reward_cid: Optional[ContractId[UnclaimedReward]] = None


@dataclass(frozen=True)
class AmuletRules_ClaimExpiredRewardsV2:
    """`AmuletRules`'s `AmuletRules_ClaimExpiredRewardsV2` choice - batch
    claim of expired CIP-104 reward coupons using time-based expiry.
    Observers `expiryObservers`, controller `dso`. Real Daml:

        nonconsuming choice AmuletRules_ClaimExpiredRewardsV2 : AmuletRules_ClaimExpiredRewardsV2Result
          with
            rewardCouponCids : [ContractId RewardCouponV2]
            expiryObservers : [Party]
    """

    reward_coupon_cids: list[ContractId[RewardCouponV2]]
    expiry_observers: list[Party]


@dataclass(frozen=True)
class AmuletRules_ClaimExpiredRewardsV2Result:
    """Real Daml: intentionally empty (`AmuletRules_ClaimExpiredRewardsV2Result {}`)
    to save on Scan storage cost - the result is read indirectly via the
    updates to the archived coupons' backing stores."""


@dataclass(frozen=True)
class AmuletRules_StartProcessingRewardsV2:
    """`AmuletRules`'s `AmuletRules_StartProcessingRewardsV2` choice -
    starts processing a `CalculateRewardsV2` batch. Controller `dso`. Real
    Daml:

        nonconsuming choice AmuletRules_StartProcessingRewardsV2 : AmuletRules_StartProcessingRewardsV2Result
          with
            calculateRewardsCid : ContractId CalculateRewardsV2
            batchHash : CryptoHash.Hash
    """

    calculate_rewards_cid: ContractId[CalculateRewardsV2]
    batch_hash: Hash


@dataclass(frozen=True)
class AmuletRules_StartProcessingRewardsV2Result:
    """Real Daml: intentionally empty (`AmuletRules_StartProcessingRewardsV2Result {}`)."""


@dataclass(frozen=True)
class AmuletRules_UnhideRewardCouponsV2:
    """`AmuletRules`'s `AmuletRules_UnhideRewardCouponsV2` choice - batch
    conversion of coupons not yet observable by their providers. Observers
    `providers`, controller `dso`. Real Daml:

        nonconsuming choice AmuletRules_UnhideRewardCouponsV2 : AmuletRules_UnhideRewardCouponsV2Result
          with
            rewardCouponCids : [ContractId RewardCouponV2]
            providers : [Party]
    """

    reward_coupon_cids: list[ContractId[RewardCouponV2]]
    providers: list[Party]


@dataclass(frozen=True)
class AmuletRules_UnhideRewardCouponsV2Result:
    """Real Daml: intentionally empty (`AmuletRules_UnhideRewardCouponsV2Result {}`)."""


@dataclass(frozen=True)
class AmuletRules_ArchiveDryRunRewardAccountingV2:
    """`AmuletRules`'s `AmuletRules_ArchiveDryRunRewardAccountingV2` choice
    - cleans up stuck dry-run reward-accounting state. Controller `dso`.
    Real Daml:

        nonconsuming choice AmuletRules_ArchiveDryRunRewardAccountingV2 : AmuletRules_ArchiveDryRunRewardAccountingV2Result
          with
            calculateRewardsCids : [ContractId CalculateRewardsV2]
            processRewardsCids : [ContractId ProcessRewardsV2]
    """

    calculate_rewards_cids: list[ContractId[CalculateRewardsV2]]
    process_rewards_cids: list[ContractId[ProcessRewardsV2]]


@dataclass(frozen=True)
class AmuletRules_ArchiveDryRunRewardAccountingV2Result:
    """Real Daml: intentionally empty (`AmuletRules_ArchiveDryRunRewardAccountingV2Result {}`)."""


@dataclass(frozen=True)
class AmuletRules_MergeUnclaimedRewards:
    """`AmuletRules`'s `AmuletRules_MergeUnclaimedRewards` choice - batch
    merge of several `UnclaimedReward` contracts into one. Controller
    `dso`. Real Daml:

        nonconsuming choice AmuletRules_MergeUnclaimedRewards : AmuletRules_MergeUnclaimedRewardsResult
          with
            unclaimedRewardCids : [ContractId UnclaimedReward]
    """

    unclaimed_reward_cids: list[ContractId[UnclaimedReward]]


@dataclass(frozen=True)
class AmuletRules_MergeUnclaimedRewardsResult:
    """Real Daml: `data AmuletRules_MergeUnclaimedRewardsResult` with
    `unclaimedRewardCid`."""

    unclaimed_reward_cid: ContractId[UnclaimedReward]


@dataclass(frozen=True)
class AmuletRules_MergeUnclaimedDevelopmentFundCoupons:
    """`AmuletRules`'s `AmuletRules_MergeUnclaimedDevelopmentFundCoupons`
    choice - batch merge of several `UnclaimedDevelopmentFundCoupon`
    contracts into one. Controller `dso`. Real Daml:

        nonconsuming choice AmuletRules_MergeUnclaimedDevelopmentFundCoupons : AmuletRules_MergeUnclaimedDevelopmentFundCouponsResult
          with
            unclaimedDevelopmentFundCouponCids : [ContractId UnclaimedDevelopmentFundCoupon]
    """

    unclaimed_development_fund_coupon_cids: list[ContractId[UnclaimedDevelopmentFundCoupon]]


@dataclass(frozen=True)
class AmuletRules_MergeUnclaimedDevelopmentFundCouponsResult:
    """Real Daml: `data AmuletRules_MergeUnclaimedDevelopmentFundCouponsResult`
    with `unclaimedDevelopmentFundCouponCid`."""

    unclaimed_development_fund_coupon_cid: ContractId[UnclaimedDevelopmentFundCoupon]


@dataclass(frozen=True)
class AmuletRules_AllocateDevelopmentFundCoupon:
    """`AmuletRules`'s `AmuletRules_AllocateDevelopmentFundCoupon` choice -
    the configured Development Fund manager allocates an amount from a
    collection of `UnclaimedDevelopmentFundCoupon`s to a beneficiary.
    Controller `fundManager`. Real Daml:

        nonconsuming choice AmuletRules_AllocateDevelopmentFundCoupon : AmuletRules_AllocateDevelopmentFundCouponResult
          with
            unclaimedDevelopmentFundCouponCids : [ContractId UnclaimedDevelopmentFundCoupon]
            beneficiary : Party
            amount : Decimal
            expiresAt : Time
            reason : Text
            fundManager : Party
    """

    unclaimed_development_fund_coupon_cids: list[ContractId[UnclaimedDevelopmentFundCoupon]]
    beneficiary: Party
    amount: Decimal
    expires_at: Timestamp
    reason: Text
    fund_manager: Party


@dataclass(frozen=True)
class AmuletRules_AllocateDevelopmentFundCouponResult:
    """Real Daml: `data AmuletRules_AllocateDevelopmentFundCouponResult`
    with `developmentFundCouponCid`, `optUnclaimedDevelopmentFundCouponCid`."""

    development_fund_coupon_cid: ContractId[DevelopmentFundCoupon]
    opt_unclaimed_development_fund_coupon_cid: Optional[ContractId[UnclaimedDevelopmentFundCoupon]] = None


@dataclass(frozen=True)
class AmuletRules_Fetch:
    """`AmuletRules`'s `AmuletRules_Fetch` choice - a `nonconsuming`
    fetchByKey-style read for parties with `readAs` but not `actAs`. Its
    result IS `AmuletRules` itself (no separate result type). Controller
    `p`. Real Daml:

        nonconsuming choice AmuletRules_Fetch : AmuletRules
          with
            p : Party
          do pure this
    """

    p: Party


@dataclass(frozen=True)
class AmuletRules_SetConfig:
    """`AmuletRules`'s `AmuletRules_SetConfig` choice - updates the current
    `AmuletConfig`, patching `newConfig`'s changes vs. `baseConfig` onto the
    live value (requires no scheduled future values). Controller `dso`.
    Real Daml:

        choice AmuletRules_SetConfig : AmuletRules_SetConfigResult
          with
            newConfig : AmuletConfig Unit.USD
            baseConfig : AmuletConfig Unit.USD
    """

    new_config: AmuletConfig[USD]
    base_config: AmuletConfig[USD]


@dataclass(frozen=True)
class AmuletRules_SetConfigResult:
    """Real Daml: `data AmuletRules_SetConfigResult` with `newAmuletRules`."""

    new_amulet_rules: ContractId[AmuletRules]


@dataclass(frozen=True)
class AmuletRules_AddFutureAmuletConfigSchedule:
    """DEPRECATED in real Daml (`deprecatedChoice`, which aborts) - use
    `AmuletRules_SetConfig` and governance votes with effective dating
    instead. Modeled for completeness. Controller `dso`. Real Daml:

        choice AmuletRules_AddFutureAmuletConfigSchedule : AmuletRules_AddFutureAmuletConfigScheduleResult
          with
            newScheduleItem : (Time, AmuletConfig Unit.USD)
    """

    new_schedule_item: tuple[Timestamp, AmuletConfig[USD]]


@dataclass(frozen=True)
class AmuletRules_AddFutureAmuletConfigScheduleResult:
    """Real Daml: `data AmuletRules_AddFutureAmuletConfigScheduleResult`
    with `newAmuletRules`."""

    new_amulet_rules: ContractId[AmuletRules]


@dataclass(frozen=True)
class AmuletRules_RemoveFutureAmuletConfigSchedule:
    """DEPRECATED in real Daml (`deprecatedChoice`, which aborts) - use
    `AmuletRules_SetConfig` and governance votes with effective dating
    instead. Modeled for completeness. Controller `dso`. Real Daml:

        choice AmuletRules_RemoveFutureAmuletConfigSchedule : AmuletRules_RemoveFutureAmuletConfigScheduleResult
          with
            scheduleTime : Time
    """

    schedule_time: Timestamp


@dataclass(frozen=True)
class AmuletRules_RemoveFutureAmuletConfigScheduleResult:
    """Real Daml: `data AmuletRules_RemoveFutureAmuletConfigScheduleResult`
    with `newAmuletRules`."""

    new_amulet_rules: ContractId[AmuletRules]


@dataclass(frozen=True)
class AmuletRules_UpdateFutureAmuletConfigSchedule:
    """DEPRECATED in real Daml (`deprecatedChoice`, which aborts) - use
    `AmuletRules_SetConfig` and governance votes with effective dating
    instead. Modeled for completeness. Controller `dso`. Real Daml:

        choice AmuletRules_UpdateFutureAmuletConfigSchedule : AmuletRules_UpdateFutureAmuletConfigScheduleResult
          with
            scheduleItem : (Time, AmuletConfig Unit.USD)
    """

    schedule_item: tuple[Timestamp, AmuletConfig[USD]]


@dataclass(frozen=True)
class AmuletRules_UpdateFutureAmuletConfigScheduleResult:
    """Real Daml: `data AmuletRules_UpdateFutureAmuletConfigScheduleResult`
    with `newAmuletRules`."""

    new_amulet_rules: ContractId[AmuletRules]


@dataclass(frozen=True)
class AmuletRules_ConvertFeaturedAppActivityMarkers:
    """`AmuletRules`'s `AmuletRules_ConvertFeaturedAppActivityMarkers`
    choice - converts `FeaturedAppActivityMarker`s into `AppRewardCoupon`s
    for a mining round, if that round still uses on-ledger issuance.
    Observers `observers` (defaults to none), controller `dso`. Real Daml:

        nonconsuming choice AmuletRules_ConvertFeaturedAppActivityMarkers : AmuletRules_ConvertFeaturedAppActivityMarkersResult
          with
            markerCids : [ContractId FeaturedAppActivityMarker]
            openMiningRoundCid : ContractId OpenMiningRound
            observers : Optional [Party]
    """

    marker_cids: list[ContractId[FeaturedAppActivityMarker]]
    open_mining_round_cid: ContractId[OpenMiningRound]
    observers: Optional[list[Party]] = None


@dataclass(frozen=True)
class AmuletRules_ConvertFeaturedAppActivityMarkersResult:
    """Real Daml: `data AmuletRules_ConvertFeaturedAppActivityMarkersResult`
    with `appRewardCouponCids`."""

    app_reward_coupon_cids: list[ContractId[AppRewardCoupon]]


@dataclass(frozen=True)
class AmuletRules_Amulet_ExpireTransferInstructions:
    """`AmuletRules`'s `AmuletRules_Amulet_ExpireTransferInstructions`
    choice - force-expires the lock on a batch of token-standard
    `TransferInstruction`s once their deadline has passed. Observers
    `observers`, controller `dso`. Real Daml:

        nonconsuming choice AmuletRules_Amulet_ExpireTransferInstructions : AmuletRules_Amulet_ExpireTransferInstructionsResult
          with
            expectedDso : Party
            inputs : [AmuletRules_ExpireTransferInstructionInput]
            observers : [Party]
    """

    expected_dso: Party
    inputs: list[AmuletRules_ExpireTransferInstructionInput]
    observers: list[Party]


@dataclass(frozen=True)
class AmuletRules_Amulet_ExpireTransferInstructionsResult:
    """Real Daml: `data AmuletRules_Amulet_ExpireTransferInstructionsResult`
    with `results : [TransferInstructionResult]`."""

    results: list[TransferInstructionResult]


@dataclass(frozen=True)
class AmuletRules_UpdateExternalPartyConfigStates:
    """`AmuletRules`'s `AmuletRules_UpdateExternalPartyConfigStates` choice
    - refreshes the pair of `ExternalPartyConfigState` snapshots for the
    given `OpenMiningRoundTriple`. Controller `dso`. Real Daml:

        nonconsuming choice AmuletRules_UpdateExternalPartyConfigStates : AmuletRules_UpdateExternalPartyConfigStatesResult
          with
            externalPartyConfigStateCid0 : ContractId ExternalPartyConfigState
            externalPartyConfigStateCid1 : ContractId ExternalPartyConfigState
            openMiningRoundTriple : OpenMiningRoundTriple
    """

    external_party_config_state_cid0: ContractId[ExternalPartyConfigState]
    external_party_config_state_cid1: ContractId[ExternalPartyConfigState]
    open_mining_round_triple: OpenMiningRoundTriple


@dataclass(frozen=True)
class AmuletRules_UpdateExternalPartyConfigStatesResult:
    """Real Daml: `data AmuletRules_UpdateExternalPartyConfigStatesResult`
    with `newExternalPartyConfigStateCid`."""

    new_external_party_config_state_cid: ContractId[ExternalPartyConfigState]
