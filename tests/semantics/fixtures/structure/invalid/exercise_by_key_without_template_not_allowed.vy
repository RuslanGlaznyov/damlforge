from forge.builtins.daml_lang import exercise_by_key
from forge.models import Party, choice, template


@template
class Account:
    bank: Party
    number: str

    signatory: Party = bank
    key: tuple[Party, str] = (bank, number)
    maintainer: Party = key[0]

    @choice(controller=bank, consuming="nonconsuming")
    def GetBank(self) -> Party:
        return self.bank


def owner_of(bank: Party, number: str) -> Party:
    return exercise_by_key((bank, number), Account.GetBank())
