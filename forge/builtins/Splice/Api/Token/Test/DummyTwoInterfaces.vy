from datetime import datetime

from forge.models import Decimal, Party, template


@template
class DummyTwoInterfaces:
    owner: Party
    issuer: Party
    amount: Decimal
    date: datetime

    signatory: list[Party] = [owner, issuer]
