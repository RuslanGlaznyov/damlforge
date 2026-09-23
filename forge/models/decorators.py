from forge.builtins import (
    ChoiceMeta,
    Consuming,
    InterfaceMeta,
    choice,
    interface,
    ledger_effect,
    view,
    template,
)


def exception(cls):
    raise NotImplementedError(
        "`exception` is excluded from the DamlForge PoC milestone "
        "(see Semantic constraints and differences from Daml.md); "
        "not usable yet."
    )
