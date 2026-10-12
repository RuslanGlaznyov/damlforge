from forge.builtins import DamlName
from Splice.Types import Round


struct RelRound:
    diff: int


@DamlName("addRelRound")
def add_rel_round(round: Round, i: RelRound) -> Round:
    pass


@DamlName("subRound")
def sub_round(round: Round, round_1: Round) -> RelRound:
    pass
