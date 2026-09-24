"""Stand-in for the real `Splice.Wallet.Subscriptions` Daml module
(`splice/daml/splice-wallet-payments/daml/Splice/Wallet/Subscriptions.daml`)
- IDE/authoring support only, see `Splice/__init__.py`. Covers
`SubscriptionData` and `unlock_and_transfer`, the second real production
function (besides `Splice.AmuletRules.exercise_app_transfer`) that consumes
an `AppTransferContext` - found by grepping the full real Splice checkout
for every `AppTransferContext` reference, not just this codebase's own two
example files.
"""

from dataclasses import dataclass
from decimal import Decimal

from typing import Annotated, Optional

from forge.models.types import ContractId, Party, Text
from ..Amulet import Amulet, LockedAmulet
from ..AmuletRules import AppTransferContext, PaymentTransferContext, TransferInput
from ... import DamlName


@dataclass(frozen=True)
class SubscriptionData:
    """The real Daml `SubscriptionData` record - identifies the parties and
    reason behind a recurring subscription payment. Real Daml definition:

        data SubscriptionData = SubscriptionData
          with
            sender : Party
            receiver : Party
            provider : Party
            dso : Party
            description : Text
          deriving (Show, Eq)
    """

    sender: Party
    receiver: Party
    provider: Party
    dso: Party
    description: Text


@dataclass(frozen=True)
class SubscriptionRequest:
    subscription_data: Annotated[SubscriptionData, DamlName("subscriptionData")]


@dataclass(frozen=True)
class SubscriptionInitialPayment:
    subscription_data: Annotated[SubscriptionData, DamlName("subscriptionData")]


@dataclass(frozen=True)
class SubscriptionIdleState:
    subscription_data: Annotated[SubscriptionData, DamlName("subscriptionData")]


@dataclass(frozen=True)
class SubscriptionPayment:
    subscription_data: Annotated[SubscriptionData, DamlName("subscriptionData")]


@dataclass(frozen=True)
class TerminatedSubscription:
    subscription_data: Annotated[SubscriptionData, DamlName("subscriptionData")]


@dataclass(frozen=True)
class SubscriptionRequest_AcceptAndMakePayment:
    inputs: list[TransferInput]
    context: PaymentTransferContext
    wallet_provider: Annotated[Party, DamlName("walletProvider")]


@dataclass(frozen=True)
class SubscriptionRequest_AcceptAndMakePaymentResult:
    subscription_payment: Annotated[
        ContractId[SubscriptionInitialPayment], DamlName("subscriptionPayment")
    ]
    sender_change: Annotated[Optional[ContractId[Amulet]], DamlName("senderChange")]


@dataclass(frozen=True)
class SubscriptionRequest_Reject:
    pass


@dataclass(frozen=True)
class SubscriptionRequest_RejectResult:
    terminated_subscription: Annotated[
        ContractId[TerminatedSubscription], DamlName("terminatedSubscription")
    ]


@dataclass(frozen=True)
class SubscriptionIdleState_MakePayment:
    inputs: list[TransferInput]
    context: PaymentTransferContext
    wallet_provider: Annotated[Party, DamlName("walletProvider")]


@dataclass(frozen=True)
class SubscriptionIdleState_MakePaymentResult:
    subscription_payment: Annotated[
        ContractId[SubscriptionPayment], DamlName("subscriptionPayment")
    ]
    sender_change: Annotated[Optional[ContractId[Amulet]], DamlName("senderChange")]


@dataclass(frozen=True)
class SubscriptionIdleState_CancelSubscription:
    pass


@dataclass(frozen=True)
class SubscriptionIdleState_CancelSubscriptionResult:
    terminated_subscription: Annotated[
        ContractId[TerminatedSubscription], DamlName("terminatedSubscription")
    ]


@DamlName("unlockAndTransfer", is_ledger_effect=True)
def unlock_and_transfer(
    transfer_context: AppTransferContext,
    subscription_data: SubscriptionData,
    target_amount: Decimal,
    locked_amulet: ContractId[LockedAmulet],
) -> ContractId[Amulet]:
    """The real Daml `unlockAndTransfer` - unlocks a `LockedAmulet` and
    transfers the target amount to the subscription's receiver as an
    `exercise_app_transfer`-mediated payment:

        unlockAndTransfer : AppTransferContext -> SubscriptionData -> Decimal
                             -> ContractId LockedAmulet -> Update (ContractId Amulet)

    A real ledger effect (`Update`) - only meaningful inside a
    `@ledger_effect`-decorated `.vy` function or a `@choice` body."""
    raise NotImplementedError(
        "unlock_and_transfer is a real Daml ledger operation - only meaningful "
        "inside compiled .vy source, not callable directly from Python"
    )
