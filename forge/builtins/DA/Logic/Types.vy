from typing import Generic, TypeVar

from forge.models import Optional, variant
from forge.builtins import DamlCaseAccessor, no_derive

A = TypeVar("A")


@no_derive
@variant
class Formula(Generic[A]):
    def Proposition(value: A): pass
    def Negation(value: Formula[A]): pass
    def Conjunction(value: list[Formula[A]]): pass
    def Disjunction(value: list[Formula[A]]): pass


@DamlCaseAccessor("Proposition")
def proposition(value: Formula[A]) -> Optional[A]:
    pass


@DamlCaseAccessor("Negation")
def negation(value: Formula[A]) -> Optional[Formula[A]]:
    pass


@DamlCaseAccessor("Conjunction")
def conjunction(value: Formula[A]) -> Optional[list[Formula[A]]]:
    pass


@DamlCaseAccessor("Disjunction")
def disjunction(value: Formula[A]) -> Optional[list[Formula[A]]]:
    pass
