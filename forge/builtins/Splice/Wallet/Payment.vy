from datetime import datetime
from typing import Annotated

from forge.models import choice, ContractId, Decimal, Optional, Party, template, variant
from forge.builtins import DamlName, no_derive
from Splice.Amulet import Amulet, AmuletCreateSummary, LockedAmulet
from Splice.AmuletRules import AppTransferContext, PaymentTransferContext, TransferInput, TransferOutput
from Splice.Round import OpenMiningRound
from Splice.Types import Round


@variant
class Unit:
    def USDUnit(): pass
    def AmuletUnit(): pass
    def ExtUnit(): pass


@no_derive
struct AppPaymentRequest_ExpireResult:
    terminated_app_payment: Annotated[ContractId[TerminatedAppPayment], DamlName("terminatedAppPayment")]


@no_derive
struct AppPaymentRequest_AcceptResult:
    accepted_payment: Annotated[ContractId[AcceptedAppPayment], DamlName("acceptedPayment")]
    sender_change_amulet: Annotated[Optional[ContractId[Amulet]], DamlName("senderChangeAmulet")]


@no_derive
struct AppPaymentRequest_WithdrawResult:
    terminated_app_payment: Annotated[ContractId[TerminatedAppPayment], DamlName("terminatedAppPayment")]


@no_derive
struct AppPaymentRequest_RejectResult:
    terminated_app_payment: Annotated[ContractId[TerminatedAppPayment], DamlName("terminatedAppPayment")]


@no_derive
struct AcceptedAppPayment_RejectResult:
    amulet: AmuletCreateSummary[ContractId[Amulet]]


@no_derive
struct AcceptedAppPayment_ExpireResult:
    amulet: AmuletCreateSummary[ContractId[Amulet]]


struct PaymentAmount:
    amount: Decimal
    unit: Unit


struct ReceiverAmount:
    receiver: Party
    amount: PaymentAmount


struct ReceiverAmuletAmount:
    receiver: Party
    amulet_amount: Annotated[Decimal, DamlName("amuletAmount")]


struct ReceiverAmulet:
    receiver: Party
    locked_amulet: Annotated[ContractId[LockedAmulet], DamlName("lockedAmulet")]


@no_derive
struct AcceptedAppPayment_CollectResult:
    receiver_amulets: Annotated[list[tuple[Party, ContractId[Amulet]]], DamlName("receiverAmulets")]


@template
class AppPaymentRequest:
    sender: Party
    receiver_amounts: Annotated[list[ReceiverAmount], DamlName("receiverAmounts")]
    provider: Party
    dso: Party
    expires_at: Annotated[datetime, DamlName("expiresAt")]
    description: str

    signatory: list[Party] = [sender, provider]

    @choice(controller=[sender, wallet_provider], consuming=True)
    def AppPaymentRequest_Accept(self, inputs: list[TransferInput], context: PaymentTransferContext, wallet_provider: Annotated[Party, DamlName("walletProvider")]) -> AppPaymentRequest_AcceptResult:
        pass

    @choice(controller=actor, consuming=True)
    def AppPaymentRequest_Expire(self, actor: Party) -> AppPaymentRequest_ExpireResult:
        pass

    @choice(controller=sender, consuming=True)
    def AppPaymentRequest_Reject(self) -> AppPaymentRequest_RejectResult:
        pass

    @choice(controller=[sender, provider], consuming=True)
    def AppPaymentRequest_Withdraw(self) -> AppPaymentRequest_WithdrawResult:
        pass


@template
class TerminatedAppPayment:
    sender: Party
    provider: Party
    receivers: list[Party]
    reference: ContractId[AppPaymentRequest]

    signatory: list[Party] = [sender, provider] + receivers


@template
class AcceptedAppPayment:
    sender: Party
    amulet_receiver_amounts: Annotated[list[ReceiverAmuletAmount], DamlName("amuletReceiverAmounts")]
    provider: Party
    dso: Party
    locked_amulet: Annotated[ContractId[LockedAmulet], DamlName("lockedAmulet")]
    round: Round
    reference: ContractId[AppPaymentRequest]

    signatory: list[Party] = [sender, provider]

    @choice(controller=[sender, provider], consuming=True)
    def AcceptedAppPayment_Collect(self, context: AppTransferContext) -> AcceptedAppPayment_CollectResult:
        pass

    @choice(controller=sender, consuming=True)
    def AcceptedAppPayment_Expire(self, context: AppTransferContext) -> AcceptedAppPayment_ExpireResult:
        pass

    @choice(controller=[sender, provider], consuming=True)
    def AcceptedAppPayment_Reject(self, context: AppTransferContext) -> AcceptedAppPayment_RejectResult:
        pass


@DamlName("paymentAmountToAmulet", is_ledger_effect=True)
def payment_amount_to_amulet(party: Party, open_mining_round: OpenMiningRound, pq: PaymentAmount) -> Decimal:
    pass


@DamlName("receiverAmountToAmuletReceiverAmount", is_ledger_effect=True)
def receiver_amount_to_amulet_receiver_amount(party: Party, open_mining_round: OpenMiningRound, rq: ReceiverAmount) -> ReceiverAmuletAmount:
    pass


@DamlName("appPaymentRequest_receivers")
def app_payment_request_receivers(app_payment_request: AppPaymentRequest) -> list[Party]:
    pass


@DamlName("unzipReceiverAmulets")
def unzip_receiver_amulets(list_value: list[ReceiverAmulet]) -> tuple[list[Party], list[ContractId[LockedAmulet]]]:
    pass


@DamlName("mkReceiverOutput")
def mk_receiver_output(receiver_amount: ReceiverAmuletAmount) -> TransferOutput:
    pass
