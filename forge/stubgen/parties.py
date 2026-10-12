from dazl.damlast.daml_lf_1 import Expr, Type
from dazl.damlast.util import module_local_name, module_name

TPL = "tpl"
ARG = "arg"
VIEW = "view"


def _strip(expr):
    while expr.ty_app is not None:
        expr = expr.ty_app.expr
    return expr


def _children(obj):
    names = list(getattr(type(obj), "__slots__", ()))
    if hasattr(obj, "__dict__"):
        names.extend(vars(obj))
    return [getattr(obj, n, None) for n in names if n != "location"]


class PartyRefs:
    def __init__(self, values: dict):
        self.values = values
        self.found: list = []
        self.seen: set = set()

    def collect(self, expr, env: dict) -> list:
        self.found = []
        self.seen = set()
        self._walk(expr, env, [])
        return self.found

    def _ref(self, expr, env):
        if expr is None:
            return None
        if expr.var is not None:
            return env.get(expr.var)
        if expr.ty_app is not None:
            return self._ref(expr.ty_app.expr, env)
        if expr.rec_proj is not None:
            base = self._ref(expr.rec_proj.record, env)
            return (base[0], (*base[1], expr.rec_proj.field)) if base else None
        if expr.view_interface is not None:
            return self._view(expr.view_interface.expr, env)
        if expr.app is not None and expr.app.args:
            fun = _strip(expr.app.fun)
            if fun.val is not None and module_local_name(fun.val) == "view":
                return self._view(expr.app.args[-1], env)
        return None

    def _view(self, expr, env):
        return (VIEW, ()) if self._ref(expr, env) == (TPL, ()) else None

    def _walk(self, obj, env, pending) -> None:
        if obj is None or isinstance(obj, (str, int, float, bool, Type)):
            return
        if isinstance(obj, (list, tuple)):
            for item in obj:
                self._walk(item, env, [])
            return
        if not isinstance(obj, Expr):
            for item in _children(obj):
                self._walk(item, env, [])
            return
        kind = obj._Sum_name
        node = obj._Sum_value
        if kind == "rec_proj":
            ref = self._ref(obj, env)
            if ref is not None and ref not in self.found:
                self.found.append(ref)
            self._walk(node.record, env, [])
        elif kind == "let":
            scope = dict(env)
            for bind in node.bindings:
                self._walk(bind.bound, scope, [])
                scope[bind.binder.var] = self._ref(bind.bound, scope)
            self._walk(node.body, scope, pending)
        elif kind == "abs":
            scope = dict(env)
            rest = list(pending)
            for param in node.param:
                scope[param.var] = rest.pop(0) if rest else None
            self._walk(node.body, scope, rest)
        elif kind == "app":
            self._app(node, env)
        elif kind == "ty_app":
            self._walk(node.expr, env, pending)
        else:
            for item in _children(node):
                self._walk(item, env, [])

    def _app(self, node, env) -> None:
        refs = [self._ref(arg, env) for arg in node.args]
        for arg in node.args:
            self._walk(arg, env, [])
        fun = _strip(node.fun)
        if fun.val is None:
            self._walk(fun, env, refs if fun.abs is not None else [])
            return
        key = (str(module_name(fun.val)), module_local_name(fun.val))
        value = self.values.get(key)
        if value is None or (key, tuple(refs)) in self.seen or not any(refs):
            return
        self.seen.add((key, tuple(refs)))
        try:
            body = value.expr
        except Exception:
            return
        self._walk(body, {}, refs)
