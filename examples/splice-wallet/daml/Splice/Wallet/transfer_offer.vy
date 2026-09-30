from decimal import Decimal
from datetime import datetime
from typing import Optional

from forge.builtins import DamlName
from forge.builtins.daml_lang import create, exercise, stakeholder, text_length
from forge.models import ContractId, Party, choice, template
from Splice.Amulet import Amulet
from Splice.AmuletRules import (
    PaymentTransferContext,
    Transfer,
    TransferInput,
    TransferOutput,
    TransferResult,
    exercise_payment_transfer,
)
from Splice.Api.Token.MetadataV1 import Metadata
from Splice.Round import OpenMiningRound_Fetch
from Splice.TokenStandard.Utils import reason_to_meta
from Splice.Types import ForDso
from Splice.Util import fetch_public_reference_data
from Splice.Wallet.Payment import PaymentAmount, payment_amount_to_amulet


struct TransferOffer_AcceptResult:
    acceptedTransferOffer: ContractId[AcceptedTransferOffer]


struct TransferOffer_RejectResult:
    trackingInfo: TransferOfferTrackingInfo


struct TransferOffer_WithdrawResult:
    trackingInfo: TransferOfferTrackingInfo


struct TransferOffer_ExpireResult:
    trackingInfo: TransferOfferTrackingInfo


struct AcceptedTransferOffer_WithdrawResult:
    trackingInfo: TransferOfferTrackingInfo


struct AcceptedTransferOffer_AbortResult:
    trackingInfo: TransferOfferTrackingInfo


struct AcceptedTransferOffer_ExpireResult:
    trackingInfo: TransferOfferTrackingInfo


struct TransferOfferTrackingInfo:
    trackingId: str
    sender: Party
    receiver: Party


struct AcceptedTransferOffer_CompleteResult:
    transferResult: TransferResult
    trackingInfo: TransferOfferTrackingInfo
    senderChangeAmulet: Optional[ContractId[Amulet]]


@template
class TransferOffer:
    sender: Party
    receiver: Party
    dso: Party
    amount: PaymentAmount
    description: str
    expiresAt: datetime
    trackingId: str

    signatory: list[Party] = [sender]
    observer: list[Party] = [receiver]
    ensure: bool = text_length(description) < 280 and text_length(trackingId) < 280

    @DamlName("TransferOffer_Accept")
    @choice(controller=receiver, consuming=True)
    def accept(self) -> TransferOffer_AcceptResult:
        now = datetime.now()
        assert now < self.expiresAt, "TransferOffer has not expired"
        accepted = create(
            AcceptedTransferOffer(
                sender=self.sender,
                receiver=self.receiver,
                dso=self.dso,
                amount=self.amount,
                expiresAt=self.expiresAt,
                trackingId=self.trackingId,
            )
        )
        return TransferOffer_AcceptResult(acceptedTransferOffer=accepted)

    @DamlName("TransferOffer_Reject")
    @choice(controller=receiver, consuming=True)
    def reject(self) -> TransferOffer_RejectResult:
        return TransferOffer_RejectResult(
            trackingInfo=TransferOfferTrackingInfo(
                trackingId=self.trackingId, sender=self.sender, receiver=self.receiver
            )
        )

    @DamlName("TransferOffer_Withdraw")
    @choice(controller=sender, consuming=True)
    def withdraw(self, reason: str) -> TransferOffer_WithdrawResult:
        return TransferOffer_WithdrawResult(
            trackingInfo=TransferOfferTrackingInfo(
                trackingId=self.trackingId, sender=self.sender, receiver=self.receiver
            )
        )

    @DamlName("TransferOffer_Expire")
    @choice(controller=actor, consuming=True)
    def expire(self, actor: Party) -> TransferOffer_ExpireResult:
        now = datetime.now()
        assert self.expiresAt <= now, "TransferOffer has expired"
        assert actor in stakeholder(self), "Actor is a stakeholder"
        return TransferOffer_ExpireResult(
            trackingInfo=TransferOfferTrackingInfo(
                trackingId=self.trackingId, sender=self.sender, receiver=self.receiver
            )
        )


@template
class AcceptedTransferOffer:
    sender: Party
    receiver: Party
    dso: Party
    amount: PaymentAmount
    expiresAt: datetime
    trackingId: str

    signatory: list[Party] = [sender, receiver]

    @DamlName("AcceptedTransferOffer_Complete")
    @choice(controller=[sender, walletProvider], consuming=True)
    def complete(
        self,
        inputs: list[TransferInput],
        transferContext: PaymentTransferContext,
        walletProvider: Party,
    ) -> AcceptedTransferOffer_CompleteResult:
        now = datetime.now()
        assert now < self.expiresAt, "AcceptedTransferOffer has not expired"
        context_round = fetch_public_reference_data(
            ForDso(dso=self.dso),
            transferContext.context.open_mining_round,
            OpenMiningRound_Fetch(p=self.sender),
        )
        amulet_amount = payment_amount_to_amulet(self.dso, context_round, self.amount)
        transfer = Transfer(
            sender=self.sender,
            provider=walletProvider,
            inputs=inputs,
            outputs=[
                TransferOutput(
                    receiver=self.receiver,
                    receiver_fee_ratio=Decimal(0),
                    amount=amulet_amount,
                    lock=None,
                    meta=reason_to_meta("transfer offer accepted", Metadata(values={})),
                )
            ],
            beneficiaries=None,
        )
        result = exercise_payment_transfer(self.dso, transferContext, transfer)
        return AcceptedTransferOffer_CompleteResult(
            transferResult=result,
            trackingInfo=TransferOfferTrackingInfo(
                trackingId=self.trackingId, sender=self.sender, receiver=self.receiver
            ),
            senderChangeAmulet=result.sender_change_amulet,
        )

    @DamlName("AcceptedTransferOffer_Withdraw")
    @choice(controller=receiver, consuming=True)
    def withdraw(self, reason: str) -> AcceptedTransferOffer_WithdrawResult:
        return AcceptedTransferOffer_WithdrawResult(
            trackingInfo=TransferOfferTrackingInfo(
                trackingId=self.trackingId, sender=self.sender, receiver=self.receiver
            )
        )

    @DamlName("AcceptedTransferOffer_Abort")
    @choice(controller=sender, consuming=True)
    def abort(self, reason: str) -> AcceptedTransferOffer_AbortResult:
        return AcceptedTransferOffer_AbortResult(
            trackingInfo=TransferOfferTrackingInfo(
                trackingId=self.trackingId, sender=self.sender, receiver=self.receiver
            )
        )

    @DamlName("AcceptedTransferOffer_Expire")
    @choice(controller=actor, consuming=True)
    def expire(self, actor: Party) -> AcceptedTransferOffer_ExpireResult:
        now = datetime.now()
        assert self.expiresAt <= now, "AcceptedTransferOffer has expired"
        assert actor in stakeholder(self), "Actor is a stakeholder"
        return AcceptedTransferOffer_ExpireResult(
            trackingInfo=TransferOfferTrackingInfo(
                trackingId=self.trackingId, sender=self.sender, receiver=self.receiver
            )
        )
