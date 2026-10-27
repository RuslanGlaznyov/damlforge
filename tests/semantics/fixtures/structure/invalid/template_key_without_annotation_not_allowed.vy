from forge.models import Party, template


@template
class Account:
    bank: Party
    number: str

    signatory: Party = bank
    key = (bank, number)
    maintainer: Party = key[0]
