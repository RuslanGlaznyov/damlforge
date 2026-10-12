from forge.models import Decimal
from forge.builtins import DamlName


Sci = tuple[Decimal, int]


def sqrt(x: Decimal) -> Decimal:
    pass


def exp(x: Decimal) -> Decimal:
    pass


@DamlName("log")
def log_(x: Decimal) -> Decimal:
    pass


@DamlName("logBase")
def log_base(b: Decimal, x: Decimal) -> Decimal:
    pass


def logt10k(x: Decimal) -> Decimal:
    pass


@DamlName("logt10kInner")
def logt10k_inner(n: int, x: Decimal) -> Decimal:
    pass


def e10(x: Decimal, n: int) -> Decimal:
    pass


def to36dig(tuple_value: tuple[Decimal, int]) -> tuple[Decimal, int]:
    pass


@DamlName("expInner")
def exp_inner(n: Decimal, t: Decimal, x: Decimal) -> tuple[Decimal, int]:
    pass


def sin(x: Decimal) -> Decimal:
    pass


def cos(x: Decimal) -> Decimal:
    pass


def tan(x: Decimal) -> Decimal:
    pass


def cordic(n: int, r: Decimal) -> tuple[Decimal, Decimal]:
    pass


@DamlName("cordicInner")
def cordic_inner(n: int, r: Decimal, v: tuple[Decimal, Decimal], pt: Decimal, angles: list[Decimal]) -> tuple[Decimal, Decimal]:
    pass
