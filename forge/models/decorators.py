from dataclasses import dataclass, field
from typing import Any, Tuple

from forge.builtins import ChoiceMeta, Consuming, choice, ledger_effect


@dataclass(frozen=True)
class VyDecorator:
    def __call__(self, fn):
        fn.__vy_decorator__ = True
        return fn


@dataclass(frozen=True)
class InterfaceMeta:
    view: Any
    requires: Tuple[Any, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class InstanceMeta:
    interface: Any


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
