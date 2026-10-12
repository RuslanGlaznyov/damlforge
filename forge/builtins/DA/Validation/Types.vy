from typing import Generic, TypeVar

from forge.models import Optional, variant
from forge.builtins import DamlCaseAccessor, no_derive
from DA.NonEmpty.Types import NonEmpty

A = TypeVar("A")
Errs = TypeVar("Errs")


@no_derive
@variant
class Validation(Generic[Errs, A]):
    def Errors(value: NonEmpty[Errs]): pass
    def Success(value: A): pass


@DamlCaseAccessor("Errors")
def errors(value: Validation[Errs, A]) -> Optional[NonEmpty[Errs]]:
    pass


@DamlCaseAccessor("Success")
def success(value: Validation[Errs, A]) -> Optional[A]:
    pass
