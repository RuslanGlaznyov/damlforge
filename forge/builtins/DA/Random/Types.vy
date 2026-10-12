from forge.models import Optional, variant
from forge.builtins import DamlCaseAccessor, no_derive


@no_derive
@variant
class Minstd:
    def Minstd(value: int): pass


@DamlCaseAccessor("Minstd")
def minstd(value: Minstd) -> Optional[int]:
    pass
