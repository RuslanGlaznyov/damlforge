from typing import TypeVar

from forge.models import ContractId, Optional, Party, TextMap
from forge.builtins import DamlName

A = TypeVar("A")
Arg = TypeVar("Arg")
B = TypeVar("B")
I = TypeVar("I")
T = TypeVar("T")
V = TypeVar("V")


@DamlName("require", is_ledger_effect=True)
def require(msg: str, invariant: bool) -> None:
    pass


@DamlName("requireMatchExpected", is_ledger_effect=True)
def require_match_expected(actual: tuple[str, A], expected: A) -> None:
    pass


@DamlName("requireUnique", is_ledger_effect=True)
def require_unique(description: str, xs: list[A]) -> None:
    pass


@DamlName("checkActor", is_ledger_effect=True)
def check_actor(actor: Party, allowed_actors: list[Party]) -> None:
    pass


@DamlName("checkActors", is_ledger_effect=True)
def check_actors(actors: list[Party], allowed_actors: list[list[Party]]) -> None:
    pass


@DamlName("archiveAndCheckActors", is_ledger_effect=True)
def archive_and_check_actors(cid: ContractId[I], arg: list[Party], allowed_actors: list[list[Party]]) -> None:
    pass


@DamlName("publicFetchDefaultImpl", is_ledger_effect=True)
def public_fetch_default_impl(this: T, contract_id: ContractId[I], arg: Arg) -> V:
    pass


@DamlName("textMapSingleton")
def text_map_singleton(k: str, v: A) -> TextMap[A]:
    pass


@DamlName("textMapValues")
def text_map_values(text_map: TextMap[A]) -> list[A]:
    pass


@DamlName("textMapKeys")
def text_map_keys(text_map: TextMap[A]) -> list[str]:
    pass


@DamlName("textMapMergeWithDefault")
def text_map_merge_with_default(tuple_value: tuple[A, B], text_map: TextMap[A], text_map_2: TextMap[B]) -> TextMap[tuple[A, B]]:
    pass


@DamlName("textMapZip")
def text_map_zip(text_map: TextMap[A], text_map_1: TextMap[B]) -> TextMap[tuple[Optional[A], Optional[B]]]:
    pass
