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

from forge.models.types import ContractId, Party, Text
from ..Amulet import Amulet, LockedAmulet
from ..AmuletRules import AppTransferContext
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
