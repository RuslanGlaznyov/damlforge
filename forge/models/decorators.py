from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Tuple


@dataclass(frozen=True)
class VyDecorator:
    def __call__(self, fn):
        fn.__vy_decorator__ = True
        return fn


class Consuming(Enum):
    """Mirrors Daml's `Consuming` LF-AST type: PreConsuming | Consuming | NonConsuming | PostConsuming."""

    PRE_CONSUMING = "preconsuming"
    CONSUMING = "consuming"
    NON_CONSUMING = "nonconsuming"
    POST_CONSUMING = "postconsuming"


def _normalize_consuming(consuming) -> Consuming:
    if isinstance(consuming, Consuming):
        return consuming
    if isinstance(consuming, bool):
        return Consuming.CONSUMING if consuming else Consuming.NON_CONSUMING
    if isinstance(consuming, str):
        try:
            return Consuming(consuming)
        except ValueError:
            pass
    valid_strings = [c.value for c in Consuming]
    raise TypeError(
        "choice(consuming=...) must be True/False, a Consuming member, or one of "
        f"{valid_strings!r}; got {consuming!r}"
    )


@dataclass(frozen=True)
class ChoiceMeta:
    controller: Any
    consuming: Consuming
    observer: Optional[Any] = None


@dataclass(frozen=True)
class InterfaceMeta:
    view: Any
    requires: Tuple[Any, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class InstanceMeta:
    interface: Any


@VyDecorator()
def choice(*, controller, consuming, observer=None):
    normalized_consuming = _normalize_consuming(consuming)

    def wrap(fn):
        fn.__choice__ = ChoiceMeta(
            controller=controller, consuming=normalized_consuming, observer=observer
        )
        return fn

    return wrap


@VyDecorator()
def ledger_effect(fn):
    fn.__ledger_effect__ = True
    return fn


@VyDecorator()
def view(fn):
    fn.__view__ = True
    return fn


def template(cls):
    cls.__template__ = True
    return cls


def interface(*, view, requires=()):
    def wrap(cls):
        cls.__interface__ = InterfaceMeta(view=view, requires=tuple(requires))
        return cls

    return wrap


def instance(interface_cls):
    def wrap(cls):
        cls.__instance__ = InstanceMeta(interface=interface_cls)
        return cls

    return wrap


def exception(cls):
    raise NotImplementedError(
        "`exception` is excluded from the DamlForge PoC milestone "
        "(see Semantic constraints and differences from Daml.md); "
        "not usable yet."
    )
