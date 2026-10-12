from forge.models import Decimal, GenMap, variant
from forge.builtins import DamlName, no_derive


@no_derive
@variant
class RoundingMode:
    def RoundingUp(): pass
    def RoundingDown(): pass
    def RoundingCeiling(): pass
    def RoundingFloor(): pass
    def RoundingHalfUp(): pass
    def RoundingHalfDown(): pass
    def RoundingHalfEven(): pass
    def RoundingUnnecessary(): pass


def mul(decimal: Decimal, decimal_1: Decimal) -> Decimal:
    pass


def div(decimal: Decimal, decimal_1: Decimal) -> Decimal:
    pass


def cast(decimal: Decimal) -> Decimal:
    pass


@DamlName("castAndRound")
def cast_and_round(decimal: Decimal) -> Decimal:
    pass


def shift(decimal: Decimal) -> Decimal:
    pass


def pi() -> Decimal:
    pass


def epsilon0() -> Decimal:
    pass


@DamlName("minBound0")
def min_bound0() -> Decimal:
    pass


@DamlName("maxBound0")
def max_bound0() -> Decimal:
    pass


def epsilon() -> Decimal:
    pass


@DamlName("roundHalfEven")
def round_half_even(x: Decimal) -> Decimal:
    pass


@DamlName("roundCeiling")
def round_ceiling(decimal: Decimal) -> Decimal:
    pass


@DamlName("roundFloor")
def round_floor(decimal: Decimal) -> Decimal:
    pass


@DamlName("roundUp")
def round_up(x: Decimal) -> Decimal:
    pass


@DamlName("roundDown")
def round_down(x: Decimal) -> Decimal:
    pass


@DamlName("roundHalfCeiling")
def round_half_ceiling(decimal: Decimal) -> Decimal:
    pass


@DamlName("roundHalfFloor")
def round_half_floor(decimal: Decimal) -> Decimal:
    pass


@DamlName("roundHalfUp")
def round_half_up(x: Decimal) -> Decimal:
    pass


@DamlName("roundHalfDown")
def round_half_down(x: Decimal) -> Decimal:
    pass


@DamlName("roundUnnecessary")
def round_unnecessary(decimal: Decimal) -> Decimal:
    pass


@DamlName("roundNumeric")
def round_numeric(i: int, m: RoundingMode, x: Decimal) -> Decimal:
    pass
