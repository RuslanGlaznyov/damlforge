from forge.models import Party
from forge.builtins import DamlName


struct Round:
    number: int


struct ForDso:
    dso: Party


struct ForRound:
    dso: Party
    round: Round


struct ForOwner:
    dso: Party
    owner: Party


@DamlName("isDefinedRound")
def is_defined_round(round: Round) -> bool:
    pass
