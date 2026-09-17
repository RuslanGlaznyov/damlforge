from forge.builtins.maps import GenMap, TextMap, known_map_types
from forge.exceptions import CompilerPanic
from forge.ir.nodes import IRCall, IRName


def _render_text_map(args, render_type) -> str:
    return f"TextMap {render_type(args[0], as_arg=True)}"


def _render_gen_map(args, render_type) -> str:
    key, value = args
    return f"Map.Map {render_type(key, as_arg=True)} {render_type(value, as_arg=True)}"


_MAP_RENDERERS = {TextMap.__name__: _render_text_map, GenMap.__name__: _render_gen_map}


def is_map_type(name: str) -> bool:
    return name in _MAP_RENDERERS


def render_map_type(t, render_type) -> str:
    cls = known_map_types().get(t.name)
    renderer = _MAP_RENDERERS.get(t.name)
    if cls is None or renderer is None:
        raise CompilerPanic(f"render_map_type: unsupported map type `{t.name}`")
    if len(t.args) != cls.arity:
        raise CompilerPanic(
            f"render_map_type: `{t.name}` expects {cls.arity} type argument(s), got {len(t.args)}"
        )
    return renderer(t.args, render_type)


_MAP_IMPORT_MARKERS = {
    GenMap.__name__: ("Map.", "import DA.Map as Map\n\n"),
    TextMap.__name__: ("TextMap", "import DA.TextMap as TextMap\n\n"),
}


def required_imports(body_source: str) -> list:
    return [
        import_line for marker, import_line in _MAP_IMPORT_MARKERS.values() if marker in body_source
    ]


def render_map_literal(keys, values, render_expr, kind=None) -> str:
    cls = known_map_types().get(kind, TextMap)
    pairs = ", ".join(f"({render_expr(k)}, {render_expr(v)})" for k, v in zip(keys, values))
    return f"{cls.module}.fromList [{pairs}]"


def known_map_methods(type_name: str) -> frozenset:
    cls = known_map_types().get(type_name)
    return cls.method_names() if cls is not None else frozenset()


def map_method_call(type_name: str, method: str, args, receiver):
    cls = known_map_types().get(type_name)
    if cls is None or method not in cls.method_names():
        return None
    return IRCall(IRName(f"{cls.module}.{method}"), tuple(args) + (receiver,))
