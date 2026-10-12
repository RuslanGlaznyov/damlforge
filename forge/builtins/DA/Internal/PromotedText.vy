from typing import Generic, TypeVar

from forge.models import variant
from forge.builtins import no_derive

T = TypeVar("T")


@no_derive
@variant
class PromotedText(Generic[T]):
    pass
