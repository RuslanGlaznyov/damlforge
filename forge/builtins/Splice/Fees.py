"""Stand-in for the real `Splice.Fees` Daml module
(`splice/daml/splice-amulet/daml/Splice/Fees.daml`) - IDE/authoring support
only, see `Splice/__init__.py`.
"""

from dataclasses import dataclass
from decimal import Decimal

from .Types import Round
from typing import Annotated
from .. import DamlName


@dataclass(frozen=True)
class FixedFee:
    """The real Daml `FixedFee` newtype - a flat fee. Real Daml definition:

        newtype FixedFee = FixedFee with fee : Decimal
    """

    fee: Decimal


@dataclass(frozen=True)
class RatePerRound:
    """The real Daml `RatePerRound` newtype - a fee rate charged per round a
    holding exists. Real Daml definition:

        newtype RatePerRound = RatePerRound with rate : Decimal
    """

    rate: Decimal


@dataclass(frozen=True)
class SteppedRate:
    """The real Daml `SteppedRate` record - a fee rate that decreases in
    steps as the transferred amount grows. Real Daml definition:

        data SteppedRate = SteppedRate
          with
            initialRate : Decimal
            steps : [(Decimal, Decimal)]
          deriving (Eq, Ord, Show)
    """

    initial_rate: Annotated[Decimal, DamlName("initialRate")]
    steps: list[tuple[Decimal, Decimal]]


@dataclass(frozen=True)
class ExpiringAmount:
    """The real Daml `ExpiringAmount` record - an `Amulet`'s holding amount,
    which decays over time via `rate_per_round`. Real Daml definition:

        data ExpiringAmount = ExpiringAmount with
            initialAmount : Decimal
            createdAt : Round
            ratePerRound : RatePerRound
          deriving (Eq, Ord, Show)

    Already accessed by this codebase's own real example
    (`loan_terms.vy`'s `verify_amulets`: `amulet.amount.initial_amount`).
    """

    initial_amount: Annotated[Decimal, DamlName("initialAmount")]
    created_at: Annotated[Round, DamlName("createdAt")]
    rate_per_round: Annotated[RatePerRound, DamlName("ratePerRound")]
