from forge.builtins import (
    ChoiceMeta,
    checked_fetch,
    Consuming,
    InterfaceMeta,
    choice,
    interface,
    variant,
    variant_record,
    view,
    template,
)

__all__ = (
    "ChoiceMeta",
    "checked_fetch",
    "Consuming",
    "InterfaceMeta",
    "choice",
    "interface",
    "variant",
    "variant_record",
    "view",
    "template",
)


def exception(cls):
    raise NotImplementedError(
        "`exception` is excluded from the DamlForge PoC milestone "
        "(see Semantic constraints and differences from Daml.md); "
        "not usable yet."
    )
