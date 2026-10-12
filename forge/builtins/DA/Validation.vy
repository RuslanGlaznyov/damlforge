from typing import TypeVar

from forge.builtins import DamlName
from DA.NonEmpty.Types import NonEmpty
from DA.Types import Either
from DA.Validation.Types import Validation

A = TypeVar("A")
Err = TypeVar("Err")


def invalid(err1: Err) -> Validation[Err, A]:
    pass


def ok(a1: A) -> Validation[Err, A]:
    pass


def validate(either: Either[Err, A]) -> Validation[Err, A]:
    pass


def run(validation: Validation[Err, A]) -> Either[NonEmpty[Err], A]:
    pass


def run1(validation: Validation[Err, A]) -> Either[Err, A]:
    pass


@DamlName("runWithDefault")
def run_with_default(d: A, validation: Validation[Err, A]) -> A:
    pass
