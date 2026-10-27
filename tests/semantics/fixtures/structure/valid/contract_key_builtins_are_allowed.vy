from typing import Optional

from forge.builtins.daml_lang import (
    exercise_by_key,
    fetch_by_key,
    lookup_all_by_key,
    lookup_by_key,
    lookup_n_by_key,
    visible_by_key,
)
from forge.models import ContractId, Party, choice, template


@template
class Account:
    bank: Party
    owner: Party
    number: str

    signatory: Party = bank
    key: tuple[Party, str] = (bank, number)
    maintainer: Party = key[0]

    @choice(controller=bank, consuming="nonconsuming")
    def GetOwner(self) -> Party:
        return self.owner


@template
class Registry:
    bank: Party

    signatory: Party = bank

    @choice(controller=bank, consuming="nonconsuming")
    def Find(self, number: str) -> Optional[Party]:
        found: Optional[ContractId[Account]] = lookup_by_key((self.bank, number))
        if found is None:
            return None
        return exercise_by_key(Account, (self.bank, number), Account.GetOwner())

    @choice(controller=bank, consuming="nonconsuming")
    def Owner(self, number: str) -> Party:
        pair: tuple[ContractId[Account], Account] = fetch_by_key((self.bank, number))
        return pair[1].owner

    @choice(controller=bank, consuming="nonconsuming")
    def Count(self, number: str) -> int:
        rows: list[tuple[ContractId[Account], Account]] = lookup_all_by_key((self.bank, number))
        first: list[tuple[ContractId[Account], Account]] = lookup_n_by_key(1, (self.bank, number))
        return len(rows) + len(first)

    @choice(controller=bank, consuming="nonconsuming")
    def Visible(self, number: str) -> bool:
        return visible_by_key(Account, (self.bank, number))
