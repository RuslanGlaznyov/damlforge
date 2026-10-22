from forge.builtins import DamlName
from DA.Random.Types import Minstd


def next(s: int) -> int:
    pass


def minstd_rand(bound: int, minstd: Minstd) -> tuple[Minstd, int]:
    pass


def minstd_init(int_value: int) -> Minstd:
    pass


@DamlName("minstd_initFromTime", is_ledger_effect=True)
def minstd_init_from_time() -> Minstd:
    pass
