from datetime import datetime
from typing import Annotated, Generic, TypeVar

from forge.models import Decimal, Optional, Party, variant
from forge.builtins import DamlCaseAccessor, DamlName
from Splice.Fees import ExpiringAmount, RatePerRound
from Splice.RelRound import RelRound
from Splice.Types import Round

A = TypeVar("A")


@variant
class BoundedSet(Generic[A]):
    def Singleton(value: A): pass
    def AfterMaxBound(): pass


struct TimeLock:
    holders: list[Party]
    expires_at: Annotated[datetime, DamlName("expiresAt")]
    opt_context: Annotated[Optional[str], DamlName("optContext")]


@DamlCaseAccessor("Singleton")
def singleton(value: BoundedSet[A]) -> Optional[A]:
    pass


@DamlCaseAccessor("AfterMaxBound", arity=0)
def after_max_bound(value: BoundedSet[A]) -> Optional[None]:
    pass


@DamlName("maxInt")
def max_int() -> int:
    pass


@DamlName("addBoundedInt")
def add_bounded_int(int_value: int, bounded_set: BoundedSet[int]) -> BoundedSet[int]:
    pass


@DamlName("maxDecimalDiv10")
def max_decimal_div10() -> Decimal:
    pass


@DamlName("boundedDivDecimal")
def bounded_div_decimal(x: Decimal, y: Decimal) -> BoundedSet[Decimal]:
    pass


@DamlName("maxIntAsDecimal")
def max_int_as_decimal() -> Decimal:
    pass


@DamlName("boundedCeiling")
def bounded_ceiling(bounded_set: BoundedSet[Decimal]) -> BoundedSet[int]:
    pass


@DamlName("addBoundedRelRound")
def add_bounded_rel_round(round: Round, y: BoundedSet[RelRound]) -> BoundedSet[Round]:
    pass


@DamlName("minTime")
def min_time() -> datetime:
    pass


@DamlName("maxTime")
def max_time() -> datetime:
    pass


@DamlName("spentWithRatePerRound")
def spent_with_rate_per_round(rate: RatePerRound, amount: Decimal) -> BoundedSet[RelRound]:
    pass


@DamlName("amountExpiresAt")
def amount_expires_at(e: ExpiringAmount) -> BoundedSet[Round]:
    pass


@DamlName("isAmuletExpired")
def is_amulet_expired(round: Round, amulet_amount: ExpiringAmount) -> bool:
    pass
