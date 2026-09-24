from forge.builtins import DamlName
from typing import TypeVar

from forge.models.types import Party, Text
from ..Api.Token.MetadataV1 import Metadata
from ..Api.Token.HoldingV2 import Account

_T = TypeVar("_T")


@DamlName("reasonToMeta")
def reason_to_meta(reason: Text, metadata: Metadata) -> Metadata:
    raise NotImplementedError


@DamlName("checkActors", is_ledger_effect=True)
def check_actors(actors: list[Party], expected: list[list[Party]]) -> None:
    raise NotImplementedError


@DamlName("requireMatchExpected", is_ledger_effect=True)
def require_match_expected(actual: tuple[Text, _T], expected: _T) -> None:
    raise NotImplementedError


@DamlName("basicAccount")
def basic_account(owner: Party) -> Account:
    raise NotImplementedError
