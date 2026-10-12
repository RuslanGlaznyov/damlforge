from forge.models import Decimal, Party, template


@template
class DummyHolding:
    owner: Party
    issuer: Party
    amount: Decimal

    signatory: list[Party] = [owner, issuer]
