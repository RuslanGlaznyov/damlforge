from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ChoiceMeta:
    controller: Any
    consuming: bool


def choice(*, controller, consuming):
    if not isinstance(consuming, bool):
        raise TypeError(
            f"choice(consuming=...) must be a literal True/False, got {consuming!r}"
        )

    def wrap(fn):
        fn.__choice__ = ChoiceMeta(controller=controller, consuming=consuming)
        return fn

    return wrap


def ledger_effect(fn):
    fn.__ledger_effect__ = True
    return fn


def view(fn):
    fn.__view__ = True
    return fn
