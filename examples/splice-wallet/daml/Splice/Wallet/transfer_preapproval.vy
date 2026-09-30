from datetime import datetime
from typing import Optional

from forge.builtins import DamlName
from forge.builtins.daml_lang import exercise
from forge.models import ContractId, Decimal, Party, choice, template
from DA.Assert import assert_within_deadline
from Splice.AmuletRules import (
    AmuletRules_CreateTransferPreapproval,
    PaymentTransferContext,
    TransferInput,
    TransferPreapproval,
    TransferResult,
)


struct TransferPreapprovalProposal_AcceptResult:
    transferPreapprovalCid: ContractId[TransferPreapproval]
    transferResult: TransferResult
    amuletPaid: Decimal


@template
class TransferPreapprovalProposal:
    receiver: Party
    provider: Party
    expectedDso: Optional[Party]

    signatory: Party = receiver
    observer: Party = provider

    @DamlName("TransferPreapprovalProposal_Accept")
    @choice(controller=provider, consuming=True)
    def accept(
        self,
        context: PaymentTransferContext,
        inputs: list[TransferInput],
        expiresAt: datetime,
    ) -> TransferPreapprovalProposal_AcceptResult:
        now = datetime.now()
        assert_within_deadline("expiresAt is not in the past", expiresAt)
        result = exercise(
            context.amulet_rules,
            AmuletRules_CreateTransferPreapproval(
                context=context,
                inputs=inputs,
                receiver=self.receiver,
                provider=self.provider,
                expires_at=expiresAt,
                expected_dso=self.expectedDso,
                opt_created_at=now,
            ),
        )
        return TransferPreapprovalProposal_AcceptResult(
            transferPreapprovalCid=result.transfer_preapproval_cid,
            transferResult=result.transfer_result,
            amuletPaid=result.amulet_paid,
        )
