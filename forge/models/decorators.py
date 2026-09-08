from forge.builtins import (
    ChoiceMeta,
    Consuming,
    InstanceMeta,
    InterfaceMeta,
    choice,
    instance,
    interface,
    ledger_effect,
    view,
)


def template(cls):
    cls.__template__ = True
    return cls


def exception(cls):
    raise NotImplementedError(
        "`exception` is excluded from the DamlForge PoC milestone "
        "(see Semantic constraints and differences from Daml.md); "
        "not usable yet."
    )
