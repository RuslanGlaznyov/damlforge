import dataclasses
import importlib
import inspect
import pkgutil
import typing
from enum import Enum
from functools import lru_cache
from typing import Any, Optional
from abc import ABC, abstractmethod

from forge.ast import nodes as vy_ast
from forge.exceptions import DamlForgeException, ExceptionList


@dataclasses.dataclass(frozen=True)
class VyDecorator(ABC):
    def __call__(self, fn):
        fn.__vy_decorator__ = True
        return fn

    @classmethod
    @abstractmethod
    def __post_vy_check__(cls, container: vy_ast.TopLevel,
                          fn: vy_ast.FunctionDef, dec, errors: ExceptionList):
        pass  # This method can be overridden in subclasses to perform additional checks


@dataclasses.dataclass(frozen=True)
class DamlName(VyDecorator):
    name: str
    module: Optional[str] = None
    is_ledger_effect: bool = False

    def __call__(self, fn):
        fn = super().__call__(fn)

        fn.__daml_name__ = self.name
        fn.__daml_module__ = self.module
        fn.__daml_ledger_effect__ = self.is_ledger_effect
        return fn

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("DamlName decorator requires a non-empty name")

    @classmethod
    def __post_vy_check__(cls, container: vy_ast.TopLevel,
                          fn: vy_ast.FunctionDef, dec, errors: ExceptionList):
        from forge.models.error_codes import ErrorCodes

        if (
                isinstance(dec, vy_ast.Call)
                and len(dec.args) == 1
                and not dec.keywords
                and isinstance(dec.args[0], vy_ast.Str)
        ):
            return

        errors.append(
            DamlForgeException(
                f"`@{cls.__name__}` on `{container.name}.{fn.name}` takes exactly one "
                "string literal argument",
                fn,
                code=ErrorCodes.DF1221.value,
            )
        )


class Consuming(Enum):
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


@dataclasses.dataclass(frozen=True)
class ChoiceMeta:
    controller: Any
    consuming: Consuming
    observer: Optional[Any] = None


CONSUMING_VARIANTS = {"preconsuming", "consuming", "nonconsuming", "postconsuming"}


def _consuming_variant_from_ast(node) -> Optional[str]:
    if isinstance(node, vy_ast.NameConstant) and isinstance(node.value, bool):
        return "consuming" if node.value else "nonconsuming"
    if isinstance(node, vy_ast.Str) and node.value in CONSUMING_VARIANTS:
        return node.value
    return None


@dataclasses.dataclass(frozen=True)
class choice(VyDecorator):
    controller: Any
    consuming: Any
    observer: Optional[Any] = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "consuming", _normalize_consuming(self.consuming))

    def __call__(self, fn):
        fn = super().__call__(fn)
        fn.__choice__ = ChoiceMeta(
            controller=self.controller, consuming=self.consuming, observer=self.observer
        )
        return fn

    @classmethod
    def __post_vy_check__(cls, container: vy_ast.TopLevel,
                          fn: vy_ast.FunctionDef, dec, errors: ExceptionList):
        from forge.models.error_codes import ErrorCodes

        kwargs = {kw.arg: kw.value for kw in dec.keywords} if isinstance(dec, vy_ast.Call) else {}
        qualified_name = f"{container.name}.{fn.name}"

        if fn.name.startswith("_"):
            errors.append(
                DamlForgeException(
                    f"Choice `{qualified_name}` starts with `_` - Python's own "
                    "convention for a private method, which contradicts `@choice` "
                    "making it a public, externally-exercisable Daml choice",
                    fn,
                    code=ErrorCodes.DF1218.value,
                )
            )

        if "controller" not in kwargs:
            errors.append(
                DamlForgeException(
                    f"Choice `{qualified_name}` must declare an explicit `controller`",
                    fn,
                    code=ErrorCodes.DF1203.value,
                )
            )

        consuming = kwargs.get("consuming")
        variant = None if consuming is None else _consuming_variant_from_ast(consuming)
        if variant is None:
            errors.append(
                DamlForgeException(
                    f"Choice `{qualified_name}` must explicitly declare `consuming` as "
                    f"True/False or one of {sorted(CONSUMING_VARIANTS)!r}",
                    fn,
                    code=ErrorCodes.DF1203.value,
                )
            )


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
        for name, obj in vars(module).items():
            is_decorator = getattr(obj, "__vy_decorator__", False) or (
                isinstance(obj, type) and obj is not VyDecorator and issubclass(obj, VyDecorator)
            )
            if is_decorator:
                names.add(name)
    return frozenset(names)


def _python_type_to_type_ref(py_type) -> "Optional[TypeRef]":
    from forge.ir.nodes import TypeRef

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
