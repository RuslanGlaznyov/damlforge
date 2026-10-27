from forge.models import Party, template


@template
class Account:
    bank: Party
    number: str

    signatory: Party = bank
    key: tuple[Party, str] = (bank, number)
    maintainer: Party = bank
