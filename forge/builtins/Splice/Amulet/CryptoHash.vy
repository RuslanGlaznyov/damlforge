from typing import TypeVar

from forge.models import Optional
from forge.builtins import DamlName

A = TypeVar("A")


struct Hash:
    value: str


@DamlName("hashRecord")
def hash_record(list_value: list[Hash]) -> Hash:
    pass


@DamlName("hashUpgradedRecord")
def hash_upgraded_record(old_field_hashes: list[Hash], new_field_hashes: list[Optional[Hash]]) -> Hash:
    pass


@DamlName("hashVariant")
def hash_variant(tag: str, field_hashes: list[Hash]) -> Hash:
    pass


@DamlName("hashUpgradedVariant")
def hash_upgraded_variant(tag: str, old_field_hashes: list[Hash], new_field_hashes: list[Optional[Hash]]) -> Hash:
    pass


def hash(a: A) -> Hash:
    pass


@DamlName("hashText")
def hash_text(str_value: str) -> Hash:
    pass


@DamlName("hashListInternal")
def hash_list_internal(list_value: list[str]) -> Hash:
    pass


@DamlName("hashVariantInternal")
def hash_variant_internal(str_value: str, list_value: list[str]) -> Hash:
    pass


@DamlName("hashOptionalInternal")
def hash_optional_internal(optional: Optional[Hash]) -> Hash:
    pass


@DamlName("dropTrailingNones")
def drop_trailing_nones(list_value: list[Optional[Hash]]) -> list[Optional[Hash]]:
    pass
