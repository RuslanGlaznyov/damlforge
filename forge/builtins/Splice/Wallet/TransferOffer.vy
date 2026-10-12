from datetime import datetime
from typing import Annotated

from forge.models import choice, ContractId, Optional, Party, template
from forge.builtins import DamlName, no_derive
from Splice.Amulet import Amulet
from Splice.AmuletRules import PaymentTransferContext, TransferInput, TransferResult
from Splice.Wallet.Payment import PaymentAmount


@no_derive
struct TransferOffer_AcceptResult:
    accepted_transfer_offer: Annotated[ContractId[AcceptedTransferOffer], DamlName("acceptedTransferOffer")]


@no_derive
struct TransferOffer_RejectResult:
    tracking_info: Annotated[TransferOfferTrackingInfo, DamlName("trackingInfo")]


@no_derive
struct TransferOffer_WithdrawResult:
    tracking_info: Annotated[TransferOfferTrackingInfo, DamlName("trackingInfo")]


@no_derive
struct TransferOffer_ExpireResult:
    tracking_info: Annotated[TransferOfferTrackingInfo, DamlName("trackingInfo")]


@no_derive
struct AcceptedTransferOffer_WithdrawResult:
    tracking_info: Annotated[TransferOfferTrackingInfo, DamlName("trackingInfo")]


@no_derive
struct AcceptedTransferOffer_AbortResult:
    tracking_info: Annotated[TransferOfferTrackingInfo, DamlName("trackingInfo")]


@no_derive
struct AcceptedTransferOffer_ExpireResult:
    tracking_info: Annotated[TransferOfferTrackingInfo, DamlName("trackingInfo")]


struct TransferOfferTrackingInfo:
    tracking_id: Annotated[str, DamlName("trackingId")]
    sender: Party
    receiver: Party


@no_derive
struct AcceptedTransferOffer_CompleteResult:
    transfer_result: Annotated[TransferResult, DamlName("transferResult")]
    tracking_info: Annotated[TransferOfferTrackingInfo, DamlName("trackingInfo")]
    sender_change_amulet: Annotated[Optional[ContractId[Amulet]], DamlName("senderChangeAmulet")]


@template
class TransferOffer:
    sender: Party
    receiver: Party
    dso: Party
    amount: PaymentAmount
    description: str
    expires_at: Annotated[datetime, DamlName("expiresAt")]
    tracking_id: Annotated[str, DamlName("trackingId")]

    signatory: list[Party] = [sender]
    observer: list[Party] = [receiver]

    @choice(controller=receiver, consuming=True)
    def TransferOffer_Accept(self) -> TransferOffer_AcceptResult:
        pass

    @choice(controller=receiver, consuming=True)
    def TransferOffer_Reject(self) -> TransferOffer_RejectResult:
        pass

    @choice(controller=sender, consuming=True)
    def TransferOffer_Withdraw(self, reason: str) -> TransferOffer_WithdrawResult:
        pass

    @choice(controller=actor, consuming=True)
    def TransferOffer_Expire(self, actor: Party) -> TransferOffer_ExpireResult:
        pass


@template
class AcceptedTransferOffer:
    sender: Party
    receiver: Party
    dso: Party
    amount: PaymentAmount
    expires_at: Annotated[datetime, DamlName("expiresAt")]
    tracking_id: Annotated[str, DamlName("trackingId")]

    signatory: list[Party] = [sender, receiver]

    @choice(controller=[sender, wallet_provider], consuming=True)
    def AcceptedTransferOffer_Complete(self, inputs: list[TransferInput], transfer_context: Annotated[PaymentTransferContext, DamlName("transferContext")], wallet_provider: Annotated[Party, DamlName("walletProvider")]) -> AcceptedTransferOffer_CompleteResult:
        pass

    @choice(controller=receiver, consuming=True)
    def AcceptedTransferOffer_Withdraw(self, reason: str) -> AcceptedTransferOffer_WithdrawResult:
        pass

    @choice(controller=sender, consuming=True)
    def AcceptedTransferOffer_Abort(self, reason: str) -> AcceptedTransferOffer_AbortResult:
        pass

    @choice(controller=actor, consuming=True)
    def AcceptedTransferOffer_Expire(self, actor: Party) -> AcceptedTransferOffer_ExpireResult:
        pass
