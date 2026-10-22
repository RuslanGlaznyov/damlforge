from forge.models import Decimal, Party, template


@template
class Iou:
    issuer: Party
    owner: Party
    amount: Decimal

    signatory: list[Party] = [issuer]
    observer: list[Party] = [owner]

    def fee(self) -> Decimal:
        return self.amount / Decimal(100)
