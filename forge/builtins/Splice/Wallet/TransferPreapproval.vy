from datetime import datetime
from typing import Annotated

from forge.models import choice, ContractId, Decimal, Optional, Party, template
from forge.builtins import DamlName, no_derive
from Splice.AmuletRules import PaymentTransferContext, TransferInput, TransferPreapproval, TransferResult


@no_derive
struct TransferPreapprovalProposal_AcceptResult:
    transfer_preapproval_cid: Annotated[ContractId[TransferPreapproval], DamlName("transferPreapprovalCid")]
    transfer_result: Annotated[TransferResult, DamlName("transferResult")]
    amulet_paid: Annotated[Decimal, DamlName("amuletPaid")]


@template
class TransferPreapprovalProposal:
    receiver: Party
    provider: Party
    expected_dso: Annotated[Optional[Party], DamlName("expectedDso")]

    signatory: list[Party] = [receiver]
    observer: list[Party] = [provider]

    @choice(controller=provider, consuming=True)
    def TransferPreapprovalProposal_Accept(self, context: PaymentTransferContext, inputs: list[TransferInput], expires_at: Annotated[datetime, DamlName("expiresAt")]) -> TransferPreapprovalProposal_AcceptResult:
        pass
