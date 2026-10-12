from typing import TypeVar

from forge.builtins import DamlName
from DA.Action.State.Type import State

A = TypeVar("A")
S = TypeVar("S")


@DamlName("evalState")
def eval_state(a1: State[S, A], s1: S) -> A:
    pass


@DamlName("execState")
def exec_state(a1: State[S, A], s1: S) -> S:
    pass
