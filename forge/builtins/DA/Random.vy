from forge.models import ledger_effect
from forge.builtins import DamlName
from DA.Random.Types import Minstd


def next(s: int) -> int:
    pass


def minstd_rand(bound: int, minstd: Minstd) -> tuple[Minstd, int]:
    pass


def minstd_init(int_value: int) -> Minstd:
    pass


@ledger_effect
@DamlName("minstd_initFromTime")
def minstd_init_from_time() -> Minstd:
    pass
