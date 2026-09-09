from forge.exceptions import CompilerPanic
from forge.ir.nodes import IRCall, IRName

OPTIONAL_TYPE_NAME = "Optional"

_ARITY = 1

_METHODS = frozenset({"isSome", "isNone", "fromSome", "fromSomeNote", "fromOptional"})


def is_optional_type(name: str) -> bool:
    return name == OPTIONAL_TYPE_NAME


def render_optional_type(t, render_type) -> str:
    if len(t.args) != _ARITY:
        raise CompilerPanic(
            f"render_optional_type: `{t.name}` expects {_ARITY} type argument(s), got {len(t.args)}"
        )
    return f"{OPTIONAL_TYPE_NAME} {render_type(t.args[0], as_arg=True)}"


_IMPORT_LINE = "import DA.Optional\n\n"


def required_imports(body_source: str) -> list:
    if any(method in body_source for method in _METHODS):
        return [_IMPORT_LINE]
    return []


def known_optional_methods() -> frozenset:
    return _METHODS


def optional_method_call(method: str, args, receiver):
    if method not in _METHODS:
        return None
    return IRCall(IRName(method), tuple(args) + (receiver,))
