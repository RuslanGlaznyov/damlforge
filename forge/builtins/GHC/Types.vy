from forge.models import variant
from forge.builtins import no_derive


@no_derive
@variant
class Ordering:
    def LT(): pass
    def EQ(): pass
    def GT(): pass
