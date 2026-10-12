from datetime import timedelta
from typing import Annotated

from forge.models import Decimal
from forge.builtins import DamlName
from Splice.RelRound import RelRound
from Splice.Types import Round


struct RatePerRound:
    rate: Decimal


struct FixedFee:
    fee: Decimal


struct SteppedRate:
    initial_rate: Annotated[Decimal, DamlName("initialRate")]
    steps: list[tuple[Decimal, Decimal]]


struct ExpiringAmount:
    initial_amount: Annotated[Decimal, DamlName("initialAmount")]
    created_at: Annotated[Round, DamlName("createdAt")]
    rate_per_round: Annotated[RatePerRound, DamlName("ratePerRound")]


struct RatePerDay:
    rate: Decimal


@DamlName("relTimeToMicros")
def rel_time_to_micros(dt: timedelta) -> Decimal:
    pass


@DamlName("microsPerDay")
def micros_per_day() -> Decimal:
    pass


@DamlName("relTimeToDays")
def rel_time_to_days(dt: timedelta) -> Decimal:
    pass


@DamlName("daysToRelTime")
def days_to_rel_time(d: Decimal) -> timedelta:
    pass


@DamlName("relTimeToSeconds")
def rel_time_to_seconds(dt: timedelta) -> Decimal:
    pass


@DamlName("chargeRatePerRound")
def charge_rate_per_round(rate: RatePerRound, dt: RelRound) -> Decimal:
    pass


@DamlName("scaleRatePerRound")
def scale_rate_per_round(s: Decimal, r: RatePerRound) -> RatePerRound:
    pass


@DamlName("positiveRatePerRound")
def positive_rate_per_round(r: RatePerRound) -> bool:
    pass


@DamlName("scaleFixedFee")
def scale_fixed_fee(s: Decimal, f: FixedFee) -> FixedFee:
    pass


@DamlName("positiveFixedFee")
def positive_fixed_fee(f: FixedFee) -> bool:
    pass


@DamlName("validSteppedRate")
def valid_stepped_rate(stepped_rate: SteppedRate) -> bool:
    pass


@DamlName("chargeSteppedRate")
def charge_stepped_rate(stepped_rate: SteppedRate, amount: Decimal) -> Decimal:
    pass


@DamlName("goChargeSteppedRate")
def go_charge_stepped_rate(tuple_value: tuple[Decimal, Decimal, Decimal], list_value: list[tuple[Decimal, Decimal]]) -> Decimal:
    pass


@DamlName("scaleSteppedRate")
def scale_stepped_rate(s: Decimal, r: SteppedRate) -> SteppedRate:
    pass


@DamlName("validExpiringAmount")
def valid_expiring_amount(e: ExpiringAmount) -> bool:
    pass


@DamlName("expiringAmount")
def expiring_amount(rate_per_round: RatePerRound, initial_amount: Decimal, created_at: Round) -> ExpiringAmount:
    pass


@DamlName("getValueAsOfRound0")
def get_value_as_of_round0(e: ExpiringAmount) -> Decimal:
    pass


@DamlName("chargeRatePerDay")
def charge_rate_per_day(rate: RatePerDay, dt: timedelta) -> Decimal:
    pass


@DamlName("ratePerRoundToRatePerDay")
def rate_per_round_to_rate_per_day(per_round: RatePerRound, tick_duration: timedelta) -> RatePerDay:
    pass
