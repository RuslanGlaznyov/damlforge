from forge.exceptions import CompilerPanic
from forge.ir.nodes import IRCall, IRName

_TYPE_NAMES = frozenset({"set", "frozenset"})

_ARITY = 1

_MODULE = "Set"

_METHODS = frozenset({"insert", "delete", "member", "size", "toList", "null"})


def is_set_type(name: str) -> bool:
    return name in _TYPE_NAMES


def render_set_type(t, render_type) -> str:
    if len(t.args) != _ARITY:
        raise CompilerPanic(
            f"render_set_type: `{t.name}` expects {_ARITY} type argument(s), got {len(t.args)}"
        )
    return f"{_MODULE}.{_MODULE} {render_type(t.args[0], as_arg=True)}"


_IMPORT_MARKER = f"{_MODULE}."
_IMPORT_LINE = f"import DA.Set as {_MODULE}\n\n"


def required_imports(body_source: str) -> list:
    return [_IMPORT_LINE] if _IMPORT_MARKER in body_source else []


def known_set_methods() -> frozenset:
    return _METHODS


def set_method_call(method: str, args, receiver):
    if method not in _METHODS:
        return None
    return IRCall(IRName(f"{_MODULE}.{method}"), tuple(args) + (receiver,))
