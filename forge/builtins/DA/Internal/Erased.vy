from forge.models import variant
from forge.builtins import no_derive


@no_derive
@variant
class Erased:
    pass
