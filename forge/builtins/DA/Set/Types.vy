from typing import Generic, TypeVar

from forge.models import GenMap
from forge.builtins import no_derive

K = TypeVar("K")


@no_derive
struct Set(Generic[K]):
    map: GenMap[K, None]
