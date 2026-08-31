import dataclasses
import importlib
import inspect
import pkgutil
import typing
from functools import lru_cache
from typing import Optional


@dataclasses.dataclass(frozen=True)
class DamlName:
    name: str
    module: Optional[str] = None
    is_ledger_effect: bool = False

    def __call__(self, fn):
        fn.__daml_name__ = self.name
        fn.__daml_module__ = self.module
        fn.__daml_ledger_effect__ = self.is_ledger_effect
        return fn


@dataclasses.dataclass(frozen=True)
class ExposeConstructor:
    def __call__(self, cls):
        cls.__daml_expose_constructor__ = True
        return cls


@dataclasses.dataclass(frozen=True)
class BuiltinMetadata:
    function_renames: dict
    field_renames: dict
    function_import_modules: dict
    ledger_effect_fns: frozenset
    constructor_types: frozenset
    constructor_of: dict


def _walk_submodules(package_name: str):
    package = importlib.import_module(package_name)
    for info in pkgutil.walk_packages(package.__path__, package_name + "."):
        yield importlib.import_module(info.name)


@lru_cache(maxsize=1)
def collect_daml_builtins() -> BuiltinMetadata:
    function_renames: dict = {}
    field_renames: dict = {}
    function_import_modules: dict = {}
    ledger_effect_fns: set = set()
    marked_constructor_types: set = set()
    constructor_of: dict = {}

    for module in _walk_submodules("forge.builtins"):
        for name, obj in vars(module).items():
            if getattr(obj, "__module__", None) != module.__name__:
                continue

            daml_name = getattr(obj, "__daml_name__", None)
            if daml_name is not None and callable(obj):
                function_renames[name] = daml_name
                required_module = getattr(obj, "__daml_module__", None)
                if required_module is not None:
                    function_import_modules[daml_name] = required_module
                if getattr(obj, "__daml_ledger_effect__", False):
                    ledger_effect_fns.add(name)

            if isinstance(obj, type):
                if getattr(obj, "__daml_expose_constructor__", False):
                    marked_constructor_types.add(name)
                if dataclasses.is_dataclass(obj):
                    hints = typing.get_type_hints(obj, include_extras=True)
                    for field in dataclasses.fields(obj):
                        for meta in getattr(hints.get(field.name), "__metadata__", ()):
                            if isinstance(meta, DamlName):
                                field_renames[field.name] = meta.name
                continue

            if inspect.isfunction(obj) and name[:1].isupper():
                return_type = typing.get_type_hints(obj).get("return")
                if return_type is not None:
                    constructor_of[name] = getattr(return_type, "__name__", str(return_type))

    return BuiltinMetadata(
        function_renames=function_renames,
        field_renames=field_renames,
        function_import_modules=function_import_modules,
        ledger_effect_fns=frozenset(ledger_effect_fns),
        constructor_types=frozenset(marked_constructor_types | set(constructor_of.values())),
        constructor_of=constructor_of,
    )
