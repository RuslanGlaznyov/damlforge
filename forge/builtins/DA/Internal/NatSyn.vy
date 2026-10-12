from typing import Generic, TypeVar

from forge.models import variant
from forge.builtins import no_derive

N = TypeVar("N")


@no_derive
@variant
class NatSyn(Generic[N]):
    pass
