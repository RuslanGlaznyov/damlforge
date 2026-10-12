from datetime import datetime
from typing import TypeVar

from forge.models import ContractId, ledger_effect, Optional, Party, TextMap
from forge.builtins import DamlName
from Splice.Api.Token.HoldingV2 import Account
from Splice.Api.Token.MetadataV1 import AnyContract, Metadata

A = TypeVar("A")
T = TypeVar("T")
V1 = TypeVar("V1")
V2 = TypeVar("V2")


def epoch() -> datetime:
    pass


@DamlName("maxTime")
def max_time() -> datetime:
    pass


@DamlName("encodeTime")
def encode_time(datetime_value: datetime) -> str:
    pass


@DamlName("decodeTime")
def decode_time(t: str) -> datetime:
    pass


@DamlName("fromAnyContractId")
def from_any_contract_id(contract_id: ContractId[AnyContract]) -> ContractId[T]:
    pass


@DamlName("toAnyContractId")
def to_any_contract_id(contract_id: ContractId[T]) -> ContractId[AnyContract]:
    pass


@DamlName("tokenStandardV2Namespace")
def token_standard_v2_namespace() -> str:
    pass


@DamlName("insertOptional")
def insert_optional(k: str, ov: Optional[A], m: TextMap[A]) -> TextMap[A]:
    pass


@DamlName("timeToMeta")
def time_to_meta(field: str, t: datetime, meta: Metadata) -> Metadata:
    pass


@DamlName("timeFromMeta")
def time_from_meta(field: str, meta: Metadata) -> Optional[datetime]:
    pass


@DamlName("specialAccountOwnerStubV1")
def special_account_owner_stub_v1() -> Party:
    pass


@DamlName("accountOwnerForV1")
def account_owner_for_v1(account: Account) -> Party:
    pass


@DamlName("accountPrincipal")
def account_principal(admin: Party, account: Account) -> Party:
    pass


@DamlName("basicAccount")
def basic_account(owner: Party) -> Account:
    pass


@DamlName("isBasicAccount")
def is_basic_account(account: Account) -> bool:
    pass


@DamlName("isRegularAccount")
def is_regular_account(account: Account) -> bool:
    pass


@DamlName("accountParties")
def account_parties(admin: Party, account: Account) -> list[Party]:
    pass


@DamlName("regularAccountParties")
def regular_account_parties(account: Account) -> list[Party]:
    pass


@DamlName("regularAccountOwner")
def regular_account_owner(account: Account) -> Party:
    pass


@DamlName("providerMetaKey")
def provider_meta_key(field: str) -> str:
    pass


@DamlName("accountIdMetaKey")
def account_id_meta_key(field: str) -> str:
    pass


@DamlName("expiresAtMetaKey")
def expires_at_meta_key() -> str:
    pass


@DamlName("accountToMeta")
def account_to_meta(field: str, account: Account, meta: Metadata) -> Metadata:
    pass


@DamlName("accountFromMeta")
def account_from_meta(owner: Party, field: str, meta: Metadata) -> Account:
    pass


@DamlName("dropAccountMeta")
def drop_account_meta(field_name: str, meta: Metadata) -> Metadata:
    pass


@ledger_effect
@DamlName("ensureNoAccountMeta")
def ensure_no_account_meta(path: str, field_name: str, meta: Metadata) -> None:
    pass


@ledger_effect
@DamlName("ensureBasicAccount")
def ensure_basic_account(field_name: str, account: Account) -> None:
    pass


@DamlName("validateNoAccountMeta")
def validate_no_account_meta(field_name: str, meta: Metadata) -> bool:
    pass


@DamlName("validateNoMeta")
def validate_no_meta(field_name: str, meta: Metadata) -> bool:
    pass


@DamlName("dropMeta")
def drop_meta(field: str, meta: Metadata) -> Metadata:
    pass


@DamlName("partiesToMeta")
def parties_to_meta(field: str, parties: list[Party], meta: Metadata) -> Metadata:
    pass


@DamlName("partiesFromMeta")
def parties_from_meta(field: str, meta: Metadata) -> list[Party]:
    pass


@DamlName("expiresAtToMeta")
def expires_at_to_meta(optional: Optional[datetime], meta: Metadata) -> Metadata:
    pass


@DamlName("cip56Prefix")
def cip56_prefix() -> str:
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


@DamlName("receiverMetaKey")
def receiver_meta_key() -> str:
    pass


@DamlName("reasonFromMeta")
def reason_from_meta(metadata: Metadata) -> str:
    pass


@DamlName("reasonToMeta")
def reason_to_meta(reason: str, metadata: Metadata) -> Metadata:
    pass


@DamlName("mkMetaTransferFrom")
def mk_meta_transfer_from(sender: Party, reason: str) -> Metadata:
    pass


@DamlName("v1HistoryTagAsUnlockV1")
def v1_history_tag_as_unlock_v1(metadata: Metadata) -> Metadata:
    pass


def upcast(v1: V1) -> V2:
    pass


def downcast(v2: V2) -> V1:
    pass
