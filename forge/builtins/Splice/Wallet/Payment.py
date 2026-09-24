"""Authoring stubs for ``Splice.Wallet.Payment``."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Annotated, Optional

from forge.models.types import ContractId, Party
from ... import DamlName
from ..Amulet import Amulet
from ..AmuletRules import PaymentTransferContext, TransferInput
from ..Round import OpenMiningRound


class Unit:
    pass


@dataclass(frozen=True)
class PaymentAmount:
    amount: Decimal
    unit: Unit


@dataclass(frozen=True)
class AppPaymentRequest:
    sender: Party


@dataclass(frozen=True)
class AcceptedAppPayment:
    sender: Party


@dataclass(frozen=True)
class TerminatedAppPayment:
    sender: Party


@dataclass(frozen=True)
class AppPaymentRequest_Accept:
    inputs: list[TransferInput]
    context: PaymentTransferContext
    wallet_provider: Annotated[Party, DamlName("walletProvider")]


@dataclass(frozen=True)
class AppPaymentRequest_AcceptResult:
    accepted_payment: Annotated[ContractId[AcceptedAppPayment], DamlName("acceptedPayment")]
    sender_change_amulet: Annotated[
        Optional[ContractId[Amulet]], DamlName("senderChangeAmulet")
    ]


@dataclass(frozen=True)
class AppPaymentRequest_Reject:
    pass


@dataclass(frozen=True)
class AppPaymentRequest_RejectResult:
    terminated_app_payment: Annotated[
        ContractId[TerminatedAppPayment], DamlName("terminatedAppPayment")
    ]


@dataclass(frozen=True)
class AppPaymentRequest_Expire:
    actor: Party


@dataclass(frozen=True)
class AppPaymentRequest_ExpireResult:
    terminated_app_payment: Annotated[
        ContractId[TerminatedAppPayment], DamlName("terminatedAppPayment")
    ]


@DamlName("paymentAmountToAmulet", is_ledger_effect=True)
def payment_amount_to_amulet(
    dso: Party, open_mining_round: OpenMiningRound, amount: PaymentAmount
) -> Decimal:
    raise NotImplementedError
