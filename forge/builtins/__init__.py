import dataclasses
import importlib
import inspect
import pkgutil
import typing
from functools import lru_cache
from typing import Optional

from forge.ir.nodes import TypeRef


@dataclasses.dataclass(frozen=True)
class DamlName:
    name: str
    module: Optional[str] = None
    is_ledger_effect: bool = False

    __vy_decorator__ = True

    def __call__(self, fn):
        fn.__daml_name__ = self.name
        fn.__daml_module__ = self.module
        fn.__daml_ledger_effect__ = self.is_ledger_effect
        return fn


@dataclasses.dataclass(frozen=True)
class DamlCaseAccessor:
    constructor: str

    def __call__(self, fn):
        fn.__daml_case_accessor__ = self.constructor
        return fn


@dataclasses.dataclass(frozen=True)
class BuiltinMetadata:
    function_renames: dict
    field_renames: dict
    function_import_modules: dict
    ledger_effect_fns: frozenset
    constructor_types: frozenset
    constructor_of: dict
    case_accessors: dict
    field_types: dict
    function_return_types: dict


def _walk_submodules(package_name: str):
    package = importlib.import_module(package_name)
    for info in pkgutil.walk_packages(package.__path__, package_name + "."):
        yield importlib.import_module(info.name)


def known_decorator_names() -> frozenset:
    from forge.models import decorators as vy_decorators_module

    own_module = importlib.import_module(__name__)
    names = set()
    for module in (own_module, vy_decorators_module):
        names |= {
            name for name, obj in vars(module).items() if getattr(obj, "__vy_decorator__", False)
        }
    return frozenset(names)


def _python_type_to_type_ref(py_type) -> Optional[TypeRef]:
    if py_type is None:
        return None
    origin = typing.get_origin(py_type)
    if origin is None:
        name = getattr(py_type, "__name__", None)
        return TypeRef(name) if name else None
    args = typing.get_args(py_type)
    if origin is typing.Union:
        non_none = [a for a in args if a is not type(None)]
        if len(non_none) == 1 and len(non_none) != len(args):
            inner = _python_type_to_type_ref(non_none[0])
            return TypeRef("Optional", (inner,) if inner is not None else ())
        return None
    name = getattr(origin, "__name__", None)
    if name is None:
        return None
    arg_refs = tuple(ref for a in args if (ref := _python_type_to_type_ref(a)) is not None)
    return TypeRef(name, arg_refs)


@lru_cache(maxsize=1)
def collect_daml_builtins() -> BuiltinMetadata:
    function_renames: dict = {}
    field_renames: dict = {}
    function_import_modules: dict = {}
    ledger_effect_fns: set = set()
    marked_constructor_types: set = set()
    constructor_of: dict = {}
    case_accessors: dict = {}
    field_types: dict = {}
    function_return_types: dict = {}

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

            case_constructor = getattr(obj, "__daml_case_accessor__", None)
            if case_constructor is not None and callable(obj):
                case_accessors[name] = case_constructor

            if isinstance(obj, type):
                if dataclasses.is_dataclass(obj):
                    marked_constructor_types.add(name)
                    hints = typing.get_type_hints(obj, include_extras=True)
                    stripped_hints = typing.get_type_hints(obj, include_extras=False)
                    fields: dict = {}
                    for field in dataclasses.fields(obj):
                        for meta in getattr(hints.get(field.name), "__metadata__", ()):
                            if isinstance(meta, DamlName):
                                field_renames[field.name] = meta.name
                        type_ref = _python_type_to_type_ref(stripped_hints.get(field.name))
                        if type_ref is not None:
                            fields[field.name] = type_ref
                    field_types[name] = fields
                continue

            if inspect.isfunction(obj):
                return_type = typing.get_type_hints(obj).get("return")
                if name[:1].isupper() and return_type is not None:
                    constructor_of[name] = getattr(return_type, "__name__", str(return_type))
                type_ref = _python_type_to_type_ref(return_type)
                if type_ref is not None:
                    function_return_types[name] = type_ref

    return BuiltinMetadata(
        function_renames=function_renames,
        field_renames=field_renames,
        function_import_modules=function_import_modules,
        ledger_effect_fns=frozenset(ledger_effect_fns),
        constructor_types=frozenset(marked_constructor_types | set(constructor_of.values())),
        constructor_of=constructor_of,
        case_accessors=case_accessors,
        field_types=field_types,
        function_return_types=function_return_types,
    )
