from typing import TypeVar

from forge.builtins import DamlName
from DA.Internal.Fail.Types import FailureStatus

A = TypeVar("A")


@DamlName("failWithStatusPure")
def fail_with_status_pure(failure_status: FailureStatus) -> A:
    pass
