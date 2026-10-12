from typing import TypeVar

from forge.models import Decimal, ledger_effect, Optional, Party, TextMap, variant
from forge.builtins import DamlName, no_derive
from DA.Types import Either
from Splice.Api.FeaturedAppRightV1 import AppRewardBeneficiary
from Splice.Api.Token.HoldingV1 import InstrumentId
from Splice.Api.Token.MetadataV1 import AnyValue, ChoiceContext, Metadata
import Splice.Api.Token.HoldingV2 as HoldingV2

A = TypeVar("A")


@no_derive
@variant
class TxKind:
    def TxKind_Transfer(): pass
    def TxKind_Unlock(): pass
    def TxKind_MergeSplit(): pass
    def TxKind_Burn(): pass
    def TxKind_Mint(): pass
    def TxKind_ExpireDust(): pass


@DamlName("splicePrefix")
def splice_prefix() -> str:
    pass


@DamlName("amuletPrefix")
def amulet_prefix() -> str:
    pass


@DamlName("amuletInstrumentId")
def amulet_instrument_id(party: Party) -> InstrumentId:
    pass


@DamlName("amuletInstrumentIdV2")
def amulet_instrument_id_v2(party: Party) -> HoldingV2.InstrumentId:
    pass


@DamlName("amuletInstrumentIdName")
def amulet_instrument_id_name() -> str:
    pass


@DamlName("nonZeroMetadata")
def non_zero_metadata(k: str, n: A, m: TextMap[str]) -> TextMap[str]:
    pass


@DamlName("optionalNonZeroMetadata")
def optional_non_zero_metadata(k: str, opt_n: Optional[A], m: TextMap[str]) -> TextMap[str]:
    pass


@DamlName("createdInRoundMetaKey")
def created_in_round_meta_key() -> str:
    pass


@DamlName("ratePerRoundMetaKey")
def rate_per_round_meta_key() -> str:
    pass


@DamlName("svRewardAmountMetaKey")
def sv_reward_amount_meta_key() -> str:
    pass


@DamlName("appRewardAmountMetaKey")
def app_reward_amount_meta_key() -> str:
    pass


@DamlName("unclaimedActivityRecordAmountMetaKey")
def unclaimed_activity_record_amount_meta_key() -> str:
    pass


@DamlName("validatorRewardAmountMetaKey")
def validator_reward_amount_meta_key() -> str:
    pass


@DamlName("appRewardBeneficiariesMetaKey")
def app_reward_beneficiaries_meta_key() -> str:
    pass


@DamlName("appRewardBeneficiaryWeightsMetaKey")
def app_reward_beneficiary_weights_meta_key() -> str:
    pass


@DamlName("developmentFundAmountMetaKey")
def development_fund_amount_meta_key() -> str:
    pass


@DamlName("reasonMetaKey")
def reason_meta_key() -> str:
    pass


@DamlName("txKindMetaKey")
def tx_kind_meta_key() -> str:
    pass


@DamlName("senderMetaKey")
def sender_meta_key() -> str:
    pass


@DamlName("burnedMetaKey")
def burned_meta_key() -> str:
    pass


@DamlName("holdingTxMeta")
def holding_tx_meta(kind: TxKind, reason: Optional[str], sender: Optional[Party], burned: Optional[Decimal]) -> Metadata:
    pass


@DamlName("txKindToText")
def tx_kind_to_text(kind: TxKind) -> str:
    pass


@DamlName("simpleHoldingTxMeta")
def simple_holding_tx_meta(kind: TxKind, reason: Optional[str], burned: Optional[Decimal]) -> Metadata:
    pass


@DamlName("externalPartyConfigStateContextKey")
def external_party_config_state_context_key() -> str:
    pass


@DamlName("featuredAppRightContextKey")
def featured_app_right_context_key() -> str:
    pass


@DamlName("transferPreapprovalContextKey")
def transfer_preapproval_context_key() -> str:
    pass


@DamlName("lockContextKey")
def lock_context_key() -> str:
    pass


@DamlName("lockExpiresAtContextKey")
def lock_expires_at_context_key() -> str:
    pass


@DamlName("lockHoldersContextKey")
def lock_holders_context_key() -> str:
    pass


@DamlName("lockContextContextKey")
def lock_context_context_key() -> str:
    pass


@DamlName("expireLockKey")
def expire_lock_key() -> str:
    pass


@DamlName("beneficiariesFromMetadata")
def beneficiaries_from_metadata(metadata: Metadata) -> Either[str, Optional[list[AppRewardBeneficiary]]]:
    pass


@DamlName("toAnyValue")
def to_any_value(a: A) -> AnyValue:
    pass


@DamlName("addOptionalAnyValue")
def add_optional_any_value(str_value: str, optional: Optional[A], m: TextMap[AnyValue]) -> TextMap[AnyValue]:
    pass


@DamlName("fromAnyValue")
def from_any_value(any_value: AnyValue) -> Either[str, A]:
    pass


@DamlName("lookupFromContext")
def lookup_from_context(context: ChoiceContext, k: str) -> Either[str, Optional[A]]:
    pass


@DamlName("getFromContext")
def get_from_context(context: ChoiceContext, k: str) -> Either[str, A]:
    pass


@ledger_effect
@DamlName("lookupFromContextU")
def lookup_from_context_u(context: ChoiceContext, k: str) -> Optional[A]:
    pass


@ledger_effect
@DamlName("getFromContextU")
def get_from_context_u(context: ChoiceContext, k: str) -> A:
    pass
