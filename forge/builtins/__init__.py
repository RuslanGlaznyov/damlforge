import dataclasses
import importlib
import pkgutil
import typing
from functools import lru_cache
from typing import Optional


@dataclasses.dataclass(frozen=True)
class DamlName:
    name: str
    module: Optional[str] = None

    def __call__(self, fn):
        fn.__daml_name__ = self.name
        fn.__daml_module__ = self.module
        return fn


def _walk_submodules(package_name: str):
    package = importlib.import_module(package_name)
    yield package
    for info in pkgutil.walk_packages(package.__path__, package_name + "."):
        yield importlib.import_module(info.name)


@lru_cache(maxsize=1)
def collect_daml_renames() -> tuple:
    function_renames: dict = {}
    field_renames: dict = {}
    function_import_modules: dict = {}
    for module in _walk_submodules("forge.builtins"):
        for name, obj in vars(module).items():
            daml_name = getattr(obj, "__daml_name__", None)
            if daml_name is not None and callable(obj):
                function_renames[name] = daml_name
                required_module = getattr(obj, "__daml_module__", None)
                if required_module is not None:
                    function_import_modules[daml_name] = required_module
            if isinstance(obj, type) and dataclasses.is_dataclass(obj):
                hints = typing.get_type_hints(obj, include_extras=True)
                for field in dataclasses.fields(obj):
                    for meta in getattr(hints.get(field.name), "__metadata__", ()):
                        if isinstance(meta, DamlName):
                            field_renames[field.name] = meta.name
    return function_renames, field_renames, function_import_modules
