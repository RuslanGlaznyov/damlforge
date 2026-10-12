from datetime import datetime, timedelta
from typing import Annotated

from forge.models import choice, ContractId, Decimal, ledger_effect, Optional, Party, template
from forge.builtins import DamlName, no_derive
from Splice.Amulet import Amulet, AmuletCreateSummary, LockedAmulet
from Splice.AmuletRules import AppTransferContext, PaymentTransferContext, TransferInput, TransferOutput
from Splice.Types import Round
from Splice.Wallet.Payment import PaymentAmount


struct SubscriptionData:
    sender: Party
    receiver: Party
    provider: Party
    dso: Party
    description: str


@no_derive
struct Subscription_ArchiveResult:
    terminated_subscription: Annotated[ContractId[TerminatedSubscription], DamlName("terminatedSubscription")]


@no_derive
struct SubscriptionRequest_AcceptAndMakePaymentResult:
    subscription_payment: Annotated[ContractId[SubscriptionInitialPayment], DamlName("subscriptionPayment")]
    sender_change: Annotated[Optional[ContractId[Amulet]], DamlName("senderChange")]


@no_derive
struct SubscriptionRequest_WithdrawResult:
    terminated_subscription: Annotated[ContractId[TerminatedSubscription], DamlName("terminatedSubscription")]


@no_derive
struct SubscriptionRequest_RejectResult:
    terminated_subscription: Annotated[ContractId[TerminatedSubscription], DamlName("terminatedSubscription")]


@no_derive
struct SubscriptionInitialPayment_CollectResult:
    subscription: ContractId[Subscription]
    subscription_state: Annotated[ContractId[SubscriptionIdleState], DamlName("subscriptionState")]
    amulet: ContractId[Amulet]


@no_derive
struct SubscriptionInitialPayment_RejectResult:
    amulet_sum: Annotated[AmuletCreateSummary[ContractId[Amulet]], DamlName("amuletSum")]


@no_derive
struct SubscriptionInitialPayment_ExpireResult:
    amulet_sum: Annotated[AmuletCreateSummary[ContractId[Amulet]], DamlName("amuletSum")]


@no_derive
struct SubscriptionIdleState_ExpireSubscriptionResult:
    terminated_subscription: Annotated[ContractId[TerminatedSubscription], DamlName("terminatedSubscription")]


@no_derive
struct SubscriptionIdleState_CancelSubscriptionResult:
    terminated_subscription: Annotated[ContractId[TerminatedSubscription], DamlName("terminatedSubscription")]


@no_derive
struct SubscriptionIdleState_MakePaymentResult:
    subscription_payment: Annotated[ContractId[SubscriptionPayment], DamlName("subscriptionPayment")]
    sender_change: Annotated[Optional[ContractId[Amulet]], DamlName("senderChange")]


@no_derive
struct SubscriptionPayment_CollectResult:
    subscription_state: Annotated[ContractId[SubscriptionIdleState], DamlName("subscriptionState")]
    amulet: ContractId[Amulet]


@no_derive
struct SubscriptionPayment_RejectResult:
    subscription_state: Annotated[ContractId[SubscriptionIdleState], DamlName("subscriptionState")]
    amulet_sum: Annotated[AmuletCreateSummary[ContractId[Amulet]], DamlName("amuletSum")]


@no_derive
struct SubscriptionPayment_ExpireResult:
    subscription_state: Annotated[ContractId[SubscriptionIdleState], DamlName("subscriptionState")]
    amulet_sum: Annotated[AmuletCreateSummary[ContractId[Amulet]], DamlName("amuletSum")]


struct SubscriptionPayData:
    payment_amount: Annotated[PaymentAmount, DamlName("paymentAmount")]
    payment_interval: Annotated[timedelta, DamlName("paymentInterval")]
    payment_duration: Annotated[timedelta, DamlName("paymentDuration")]


@template
class Subscription:
    subscription_data: Annotated[SubscriptionData, DamlName("subscriptionData")]
    reference: ContractId[SubscriptionRequest]

    signatory: list[Party] = [subscription_data.sender, subscription_data.receiver, subscription_data.provider]

    @choice(controller=[subscription_data.sender, subscription_data.receiver, subscription_data.provider], consuming=True)
    def Subscription_Archive(self) -> Subscription_ArchiveResult:
        pass


@template
class TerminatedSubscription:
    subscription_data: Annotated[SubscriptionData, DamlName("subscriptionData")]
    reference: ContractId[SubscriptionRequest]

    signatory: list[Party] = [subscription_data.sender, subscription_data.receiver, subscription_data.provider]


@template
class SubscriptionRequest:
    subscription_data: Annotated[SubscriptionData, DamlName("subscriptionData")]
    pay_data: Annotated[SubscriptionPayData, DamlName("payData")]

    signatory: list[Party] = [subscription_data.sender, subscription_data.receiver, subscription_data.provider]

    @choice(controller=[wallet_provider, subscription_data.sender], consuming=True)
    def SubscriptionRequest_AcceptAndMakePayment(self, inputs: list[TransferInput], context: PaymentTransferContext, wallet_provider: Annotated[Party, DamlName("walletProvider")]) -> SubscriptionRequest_AcceptAndMakePaymentResult:
        pass

    @choice(controller=subscription_data.receiver, consuming=True)
    def SubscriptionRequest_Withdraw(self) -> SubscriptionRequest_WithdrawResult:
        pass

    @choice(controller=subscription_data.sender, consuming=True)
    def SubscriptionRequest_Reject(self) -> SubscriptionRequest_RejectResult:
        pass


@template
class SubscriptionInitialPayment:
    subscription_data: Annotated[SubscriptionData, DamlName("subscriptionData")]
    pay_data: Annotated[SubscriptionPayData, DamlName("payData")]
    target_amount: Annotated[Decimal, DamlName("targetAmount")]
    locked_amulet: Annotated[ContractId[LockedAmulet], DamlName("lockedAmulet")]
    round: Round
    reference: ContractId[SubscriptionRequest]

    signatory: list[Party] = [subscription_data.sender, subscription_data.receiver, subscription_data.provider]

    @choice(controller=[subscription_data.sender, subscription_data.receiver, subscription_data.provider], consuming=True)
    def SubscriptionInitialPayment_Collect(self, transfer_context: Annotated[AppTransferContext, DamlName("transferContext")]) -> SubscriptionInitialPayment_CollectResult:
        pass

    @choice(controller=subscription_data.receiver, consuming=True)
    def SubscriptionInitialPayment_Reject(self, transfer_context: Annotated[AppTransferContext, DamlName("transferContext")]) -> SubscriptionInitialPayment_RejectResult:
        pass

    @choice(controller=actor, consuming=True)
    def SubscriptionInitialPayment_Expire(self, actor: Party, transfer_context: Annotated[AppTransferContext, DamlName("transferContext")]) -> SubscriptionInitialPayment_ExpireResult:
        pass


@template
class SubscriptionIdleState:
    subscription: ContractId[Subscription]
    subscription_data: Annotated[SubscriptionData, DamlName("subscriptionData")]
    pay_data: Annotated[SubscriptionPayData, DamlName("payData")]
    next_payment_due_at: Annotated[datetime, DamlName("nextPaymentDueAt")]
    reference: ContractId[SubscriptionRequest]

    signatory: list[Party] = [subscription_data.sender, subscription_data.receiver, subscription_data.provider]

    @choice(controller=[wallet_provider, subscription_data.sender], consuming=True)
    def SubscriptionIdleState_MakePayment(self, inputs: list[TransferInput], context: PaymentTransferContext, wallet_provider: Annotated[Party, DamlName("walletProvider")]) -> SubscriptionIdleState_MakePaymentResult:
        pass

    @choice(controller=actor, consuming=True)
    def SubscriptionIdleState_ExpireSubscription(self, actor: Party) -> SubscriptionIdleState_ExpireSubscriptionResult:
        pass

    @choice(controller=subscription_data.sender, consuming=True)
    def SubscriptionIdleState_CancelSubscription(self) -> SubscriptionIdleState_CancelSubscriptionResult:
        pass


@template
class SubscriptionPayment:
    subscription: ContractId[Subscription]
    subscription_data: Annotated[SubscriptionData, DamlName("subscriptionData")]
    pay_data: Annotated[SubscriptionPayData, DamlName("payData")]
    this_payment_due_at: Annotated[datetime, DamlName("thisPaymentDueAt")]
    target_amount: Annotated[Decimal, DamlName("targetAmount")]
    locked_amulet: Annotated[ContractId[LockedAmulet], DamlName("lockedAmulet")]
    round: Round
    reference: ContractId[SubscriptionRequest]

    signatory: list[Party] = [subscription_data.sender, subscription_data.receiver, subscription_data.provider]

    @choice(controller=[subscription_data.sender, subscription_data.receiver, subscription_data.provider], consuming=True)
    def SubscriptionPayment_Collect(self, transfer_context: Annotated[AppTransferContext, DamlName("transferContext")]) -> SubscriptionPayment_CollectResult:
        pass

    @choice(controller=subscription_data.receiver, consuming=True)
    def SubscriptionPayment_Reject(self, transfer_context: Annotated[AppTransferContext, DamlName("transferContext")]) -> SubscriptionPayment_RejectResult:
        pass

    @choice(controller=actor, consuming=True)
    def SubscriptionPayment_Expire(self, actor: Party, transfer_context: Annotated[AppTransferContext, DamlName("transferContext")]) -> SubscriptionPayment_ExpireResult:
        pass


@DamlName("subscriptionSignatories")
def subscription_signatories(subscription_data: SubscriptionData) -> list[Party]:
    pass


@DamlName("payDataIsValid")
def pay_data_is_valid(pay_data: SubscriptionPayData) -> bool:
    pass


@ledger_effect
@DamlName("lockAndMakeChange")
def lock_and_make_change(context: PaymentTransferContext, subscription_data: SubscriptionData, pay_data: SubscriptionPayData, inputs: list[TransferInput], now: datetime, wallet_provider: Party) -> tuple[ContractId[LockedAmulet], Optional[ContractId[Amulet]], Decimal, Round]:
    pass


@ledger_effect
@DamlName("unlockAndTransfer")
def unlock_and_transfer(transfer_context: AppTransferContext, subscription_data: SubscriptionData, target_amount: Decimal, locked_amulet: ContractId[LockedAmulet]) -> ContractId[Amulet]:
    pass


@DamlName("mkTransferOutput")
def mk_transfer_output(reason: str, receiver: Party, amount: Decimal) -> TransferOutput:
    pass
