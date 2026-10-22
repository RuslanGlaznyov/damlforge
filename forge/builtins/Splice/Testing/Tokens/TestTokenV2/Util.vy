from typing import TypeVar

from forge.models import ContractId, GenMap, Optional, variant
from forge.builtins import DamlName, no_derive
from Splice.Api.Token.MetadataV1 import AnyContract, ChoiceContext
from Splice.Api.Token.TransferEventsV2 import EventLog

A = TypeVar("A")
K = TypeVar("K")
T = TypeVar("T")
V = TypeVar("V")


@no_derive
@variant
class CallSource:
    def CalledFromV1(): pass
    def CalledFromV2(): pass


def union(x: list[A], y: list[A]) -> list[A]:
    pass


@DamlName("insertWithUnion")
def insert_with_union(k: K, list_value: list[V], gen_map: GenMap[K, list[V]]) -> GenMap[K, list[V]]:
    pass


@DamlName("tokenRulesContextKey")
def token_rules_context_key() -> str:
    pass


@DamlName("getTokenRulesFromContext", is_ledger_effect=True)
def get_token_rules_from_context(context: ChoiceContext) -> ContractId[AnyContract]:
    pass


@DamlName("getEventLogFromContext", is_ledger_effect=True)
def get_event_log_from_context(context: ChoiceContext) -> ContractId[EventLog]:
    pass


@DamlName("archiveIfCalledFromV2", is_ledger_effect=True)
def archive_if_called_from_v2(call_source: CallSource, optional: Optional[ContractId[T]]) -> None:
    pass
