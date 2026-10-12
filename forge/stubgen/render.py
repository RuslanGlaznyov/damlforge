import keyword
import re
from functools import partial

from dazl._gen.com.digitalasset.daml.lf.archive.daml_lf2_pb2 import BuiltinType
from dazl.damlast.util import module_local_name, module_name

from forge.ast.pre_parser import CUSTOM_STATEMENT_TYPES, VYPER_CLASS_TYPES
from forge.stubgen.parties import ARG, TPL, VIEW, PartyRefs

_RESERVED = {"enum", "self", *VYPER_CLASS_TYPES, *CUSTOM_STATEMENT_TYPES}
_CLAUSES = {"signatory", "observer", "key", "maintainer", "ensure"}
_PRIMS = {
    "UNIT": "None",
    "BOOL": "bool",
    "INT64": "int",
    "NUMERIC": "Decimal",
    "TEXT": "str",
    "TIMESTAMP": "datetime",
    "DATE": "date",
    "PARTY": "Party",
}
_GENERICS = {
    "LIST": "list",
    "CONTRACT_ID": "ContractId",
    "OPTIONAL": "Optional",
    "TEXTMAP": "TextMap",
    "GENMAP": "GenMap",
}
_STD_TYPES = {("DA.Time.Types", "RelTime"): "timedelta", ("DA.Set.Types", "Set"): "set"}
_SOURCES = {
    **dict.fromkeys(("datetime", "date", "timedelta"), "datetime"),
    **dict.fromkeys(("Annotated", "Generic", "TypeVar"), "typing"),
    **dict.fromkeys(("DamlName", "DamlCaseAccessor", "no_derive"), "forge.builtins"),
    **dict.fromkeys(
        ("Decimal", "Party", "ContractId", "Optional", "TextMap", "GenMap", "choice")
        + ("template", "variant", "variant_record", "ledger_effect"),
        "forge.models",
    ),
}
_TYPE_WORDS = {*_PRIMS.values(), *_GENERICS.values(), "timedelta", "set", "tuple"}
_SNAKE = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")
_BINDER = re.compile(r"^[a-z][A-Za-z0-9_]*$")


class Unsupported(Exception):
    pass


def snake(name: str) -> str:
    return _SNAKE.sub("_", name).lower()


def _safe(name: str) -> str:
    return f"{name}_" if keyword.iskeyword(name) or name in _RESERVED else name


def _type_var(var: str) -> str:
    clean = re.sub(r"\W", "", var) or "T"
    return clean[:1].upper() + clean[1:]


def _key(tycon) -> tuple:
    return str(module_name(tycon)), module_local_name(tycon)


def _line(defn) -> int:
    return getattr(getattr(getattr(defn, "location", None), "range", None), "start_line", 0) or 0


def _prim_name(t):
    return BuiltinType.Name(int(t.prim.prim)) if t.prim is not None else None


def _party_kind(t):
    if _prim_name(t) == "PARTY":
        return "one"
    if _prim_name(t) == "LIST" and t.prim.args and _prim_name(t.prim.args[0]) == "PARTY":
        return "many"
    return None


def _party_expr(refs: list, kind, render, as_list: bool) -> str:
    parts: list = []
    singles: list = []
    for ref in refs:
        if kind(ref) == "one":
            singles.append(render(ref))
        elif kind(ref) == "many":
            parts += [f"[{', '.join(singles)}]"] if singles else []
            singles = []
            parts.append(render(ref))
    parts += [f"[{', '.join(singles)}]"] if singles else []
    if not as_list and len(parts) == 1 and parts[0].startswith("[") and "," not in parts[0]:
        return parts[0][1:-1]
    return " + ".join(parts)


def _tpl_party(ref) -> str:
    return ".".join(snake(p) for p in ref[1])


def _iface_party(ref) -> str:
    return f"view.{_tpl_party(ref)}" if ref[0] == VIEW else _tpl_party(ref)


def _signature(value) -> tuple:
    t = value.name_with_type.type
    while t.forall is not None:
        t = t.forall.body
    params = []
    while _prim_name(t) == "ARROW":
        params.append(t.prim.args[0])
        t = t.prim.args[1]
    return params, t


def _binders(value, count: int) -> list:
    try:
        expr = value.expr
    except Exception:
        expr = None
    names: list = []
    while expr is not None and expr.ty_abs is not None:
        expr = expr.ty_abs.body
    while expr is not None and expr.abs is not None and len(names) < count:
        names.extend(p.var for p in expr.abs.param)
        expr = expr.abs.body
    return names + [None] * (count - len(names))


def _def_name(defn) -> str:
    if (named := getattr(defn, "name_with_type", None)) is not None:
        return snake(".".join(named.name))
    segments = getattr(defn.name, "segments", None)
    return ".".join(segments) if segments is not None else str(defn.name)


class ModuleStub:
    def __init__(self, module, types: dict, values: dict):
        self.module = module
        self.name = str(module.name)
        self.types = types
        self.refs = PartyRefs(values)
        self.instances = {".".join(v.name_with_type.name) for v in module.values}
        self.qualified: set = set()
        self.reexports: dict = {}
        self.rendered: set = set()
        self._reset()

    def _reset(self) -> None:
        self.used: dict = {}
        self.imports: dict = {}
        self.aliases: dict = {}
        self.tvars: set = set()
        self.skipped: list = []
        self.local_names: set = set()

    def _use(self, *names: str) -> str:
        for name in names:
            if name in _SOURCES:
                self.used.setdefault(_SOURCES[name], set()).add(name)
        return names[-1]

    def _tvar(self, var: str) -> str:
        name = _type_var(var)
        self.tvars.add(name)
        self._use("TypeVar")
        return name

    def _ref(self, mod: str, name: str) -> str:
        if mod == self.name:
            return name
        owner = next((m for m, names in self.imports.items() if name in names), None)
        if mod not in self.qualified and owner in (None, mod) and name not in self.local_names:
            self.imports.setdefault(mod, set()).add(name)
            return name
        alias = mod.rsplit(".", 1)[-1]
        self.aliases[mod] = f"{alias}Module" if alias in self.local_names else alias
        return f"{self.aliases[mod]}.{name}"

    def type_ref(self, t) -> str:
        if t.prim is not None:
            kind = BuiltinType.Name(int(t.prim.prim))
            if kind in _PRIMS:
                return self._use(_PRIMS[kind])
            if kind not in _GENERICS:
                raise Unsupported(f"builtin type {kind} has no .vy form")
            head, args = self._use(_GENERICS[kind]), [self.type_ref(a) for a in t.prim.args]
        elif t.con is not None:
            mod, name = _key(t.con.tycon)
            args = [self.type_ref(a) for a in t.con.args]
            std = _STD_TYPES.get((mod, name))
            if std is None and name.startswith("Tuple") and mod in ("DA.Types", "GHC.Tuple"):
                std = "tuple"
            head = self._use(std) if std else self._ref(mod, name)
        elif t.var is not None and not t.var.args:
            return self._tvar(t.var.var)
        elif t.syn is not None:
            mod, name = _key(t.syn.tysyn)
            target = self.types.get(("syn", mod, name))
            if target is None or target.type.struct is not None:
                raise Unsupported(f"typeclass `{name}` has no .vy form")
            args = [self.type_ref(a) for a in t.syn.args]
            head = self._ref(mod, name)
        else:
            raise Unsupported("higher-kinded or structural types have no .vy form")
        return f"{head}[{', '.join(args)}]" if args else head

    def record(self, con) -> list:
        dt = self.types.get(_key(con.tycon))
        if dt is None or dt.record is None:
            raise Unsupported(f"record {module_local_name(con.tycon)} not found in the DAR")
        return list(dt.record.fields)

    def _field(self, f) -> str:
        py = snake(f.field)
        if not py.isidentifier():
            raise Unsupported(f"field name `{f.field}` is not a valid Python name")
        py = f"{py}_" if py in _CLAUSES else _safe(py)
        ty = self.type_ref(f.type)
        if py != f.field:
            ty = f'Annotated[{ty}, DamlName("{f.field}")]'
            self._use("Annotated", "DamlName")
        return f"{py}: {ty}"

    def _params(self, fields) -> str:
        return ", ".join(map(self._field, fields))

    def _generic(self, dt) -> str:
        if not dt.params:
            return ""
        names = [self._tvar(p.var) for p in dt.params]
        self._use("Generic")
        return f"(Generic[{', '.join(names)}])"

    def _no_derive(self, name: str) -> list:
        if {f"$$fEq{name}", f"$$fShow{name}"} <= self.instances:
            return []
        return [f"@{self._use('no_derive')}"]

    def _constructors(self, dt) -> list:
        ctors: list = []
        for f in dt.variant.fields:
            con = f.type.con
            if con is not None and module_local_name(con.tycon) == f"{dt.name}.{f.field}":
                ctors.append((f.field, "record", self.record(con)))
            else:
                ctors.append((f.field, "unit" if _prim_name(f.type) == "UNIT" else "value", f.type))
        return ctors

    def struct(self, dt) -> list:
        body = [f"    {self._field(f)}" for f in dt.record.fields] or ["    pass"]
        return [*self._no_derive(str(dt.name)), f"struct {dt.name}{self._generic(dt)}:", *body]

    def variant(self, dt) -> list:
        self._use("variant")
        lines = [*self._no_derive(str(dt.name)), "@variant", f"class {dt.name}{self._generic(dt)}:"]
        if dt.enum is not None:
            return lines + [f"    def {c}(): pass" for c in dt.enum.constructors]
        if not dt.variant.fields:
            return lines + ["    pass"]
        for ctor, kind, payload in self._constructors(dt):
            if kind == "record":
                lines.append(f"    @{self._use('variant_record')}")
                lines.append(f"    def {ctor}({self._params(payload)}): pass")
            else:
                param = "" if kind == "unit" else f"value: {self.type_ref(payload)}"
                lines.append(f"    def {ctor}({param}): pass")
        return lines

    def accessors(self, dt) -> list:
        self._use("DamlCaseAccessor", "Optional")
        args = [_type_var(p.var) for p in dt.params]
        target = f"{dt.name}[{', '.join(args)}]" if args else str(dt.name)
        blocks = []
        for ctor, kind, payload in self._constructors(dt):
            if kind == "record":
                types = [self.type_ref(f.type) for f in payload]
                arity, result = len(types), (
                    types[0] if len(types) == 1 else f"tuple[{', '.join(types)}]"
                )
            else:
                arity, result = (0, "None") if kind == "unit" else (1, self.type_ref(payload))
            spec = f'"{ctor}"' if arity == 1 else f'"{ctor}", arity={arity}'
            blocks.append(
                f"@DamlCaseAccessor({spec})\n"
                f"def {_safe(snake(ctor))}(value: {target}) -> Optional[{result}]:\n    pass"
            )
        return "\n\n\n".join(blocks).split("\n")

    def synonym(self, syn) -> list:
        for p in syn.params:
            self._tvar(p.var)
        return [f"{'.'.join(syn.name.segments)} = {self.type_ref(syn.type)}"]

    def _arg_name(self, binder, ty: str, seen: set) -> str:
        name = snake(binder) if binder and _BINDER.match(binder) else ""
        if not name or name.startswith("ds") or not name.isidentifier():
            name = snake(re.split(r"\W", ty)[0]) or "value"
        name = _safe(name)
        base = f"{name}_value" if name in _TYPE_WORDS else name
        name = base
        while name in seen or keyword.iskeyword(name):
            name = f"{base}_{len(seen)}"
        seen.add(name)
        return name

    def function(self, value) -> list:
        name = ".".join(value.name_with_type.name)
        params, result = _signature(value)
        seen: set = set()
        args = []
        for param, binder in zip(params, _binders(value, len(params))):
            if param.syn is None:
                ty = self.type_ref(param)
                args.append(f"{self._arg_name(binder, ty, seen)}: {ty}")
        lines = []
        if _prim_name(result) == "UPDATE" or (result.var is not None and len(result.var.args) == 1):
            result = result.prim.args[0] if result.prim is not None else result.var.args[0]
            lines.append(f"@{self._use('ledger_effect')}")
        py = snake(name)
        if not py.isidentifier():
            raise Unsupported(f"`{name}` is not a valid Python name")
        if (py := _safe(py)) != name:
            lines.append(f'@{self._use("DamlName")}("{name}")')
        return lines + [f"def {py}({', '.join(args)}) -> {self.type_ref(result)}:", "    pass"]

    def _path_kind(self, roots: dict, ref):
        role, path = ref
        t = roots.get((role, path[0])) if path else None
        for name in path[1:]:
            dt = self.types.get(_key(t.con.tycon)) if t is not None and t.con else None
            if dt is None or dt.record is None:
                return None
            t = next((f.type for f in dt.record.fields if f.field == name), None)
        return _party_kind(t) if t is not None else None

    def _choices(self, choices, param: str, roots: dict, render, fallback: str) -> list:
        blocks = []
        for ch in (c for c in choices if c.name != "Archive"):
            self._use("choice")
            env = {param: (TPL, ()), ch.arg_binder.var: (ARG, ())}
            args = self.record(ch.arg_binder.type.con)
            scope = {**roots, **{(ARG, f.field): f.type for f in args}}
            kind = partial(self._path_kind, scope)
            ctrl = _party_expr(self.refs.collect(ch.controllers, env), kind, render, False)
            if not ctrl:
                first = next((f.field for f in args if _party_kind(f.type) == "one"), None)
                ctrl = snake(first) if first else fallback
            opts = [
                f"controller={ctrl}",
                "consuming=True" if ch.consuming else 'consuming="nonconsuming"',
            ]
            if ch.observers is not None:
                if obs := _party_expr(self.refs.collect(ch.observers, env), kind, render, True):
                    opts.append(f"observer={obs}")
            params = ", ".join(["self", self._params(args)]) if args else "self"
            blocks.append(
                [
                    f"    @choice({', '.join(opts)})",
                    f"    def {ch.name}({params}) -> {self.type_ref(ch.ret_type)}:",
                    "        pass",
                ]
            )
        return blocks

    def interface(self, iface) -> list:
        view = iface.view
        bases = [self._ref(*_key(r)) for r in iface.requires]
        view_dt = self.types.get(_key(view.con.tycon)) if view.con is not None else None
        roots = {}
        if view_dt is not None and view_dt.record is not None:
            roots = {(VIEW, f.field): f.type for f in view_dt.record.fields}
        if _prim_name(view) != "UNIT":
            bases.append(f"view={self.type_ref(view)}")
        head = (
            f"interface {iface.name}({', '.join(bases)}):" if bases else f"interface {iface.name}:"
        )
        first = next((f for (_, f), t in roots.items() if _party_kind(t) == "one"), None)
        fallback = f"view.{snake(first)}" if first else "[]"
        blocks = self._choices(iface.choices, iface.param, roots, _iface_party, fallback)
        if not blocks:
            return [head, "    pass"]
        return [head] + [line for block in blocks for line in [*block, ""]][:-1]

    def template(self, tpl) -> list:
        self._use("template", "Party")
        fields = self.types[(self.name, str(tpl.tycon))].record.fields
        roots = {(TPL, f.field): f.type for f in fields}
        kind = partial(self._path_kind, roots)
        env = {tpl.param: (TPL, ())}
        sig = _party_expr(self.refs.collect(tpl.signatories, env), kind, _tpl_party, True)
        if not sig:
            first = [(TPL, (f.field,)) for f in fields if _party_kind(f.type)][:1]
            sig = _party_expr(first, kind, _tpl_party, True) or "[]"
        lines = [*self._no_derive(str(tpl.tycon)), "@template", f"class {tpl.tycon}:"]
        lines += [f"    {self._field(f)}" for f in fields]
        lines += ["", f"    signatory: list[Party] = {sig}"]
        if tpl.observers is not None:
            if obs := _party_expr(self.refs.collect(tpl.observers, env), kind, _tpl_party, True):
                lines.append(f"    observer: list[Party] = {obs}")
        for block in self._choices(tpl.choices, tpl.param, roots, _tpl_party, sig):
            lines += ["", *block]
        return lines

    def _definitions(self) -> list:
        own = {str(t.tycon) for t in self.module.templates}
        own |= {
            c.name for t in (*self.module.templates, *self.module.interfaces) for c in t.choices
        }
        types: list = [(s, self.synonym) for s in self.module.synonyms if s.type.struct is None]
        extras: list = []
        for dt in self.module.data_types:
            if dt.interface is not None or "." in str(dt.name) or str(dt.name) in own:
                continue
            if dt.record is not None:
                types.append((dt, self.struct))
            elif dt.variant is not None or dt.enum is not None:
                types.append((dt, self.variant))
                if dt.variant is not None and dt.variant.fields:
                    extras.append((dt, self.accessors))
        for value in self.module.values:
            name = ".".join(value.name_with_type.name)
            if "$" not in name and name[:1].islower() and not getattr(value, "is_test", False):
                extras.append((value, self.function))
        types.sort(key=lambda d: _line(d[0]))
        types += [(i, self.interface) for i in self.module.interfaces]
        types += [(t, self.template) for t in sorted(self.module.templates, key=_line)]
        return types + sorted(extras, key=lambda d: _line(d[0]))

    def render(self):
        source = self._render_once()
        while set(self.aliases) & set(self.imports):
            self.qualified |= set(self.aliases)
            self._reset()
            source = self._render_once()
        return source

    def _valid(self, defn) -> bool:
        ctors = [f.field for f in getattr(getattr(defn, "variant", None), "fields", ())]
        ctors += list(getattr(getattr(defn, "enum", None), "constructors", ()))
        return all(n.isidentifier() for n in (_def_name(defn), *ctors))

    def _render_once(self):
        defs = []
        for defn, emit in self._definitions():
            if self._valid(defn):
                defs.append((defn, emit))
            else:
                self.skipped.append(f"{self.name}.{_def_name(defn)}: not a valid Python name")
        self.local_names = {_def_name(d) for d, _ in defs}
        self.rendered = set()
        blocks = []
        for defn, emit in defs:
            try:
                blocks.append("\n".join(emit(defn)))
                self.rendered.add(_def_name(defn))
            except Unsupported as e:
                self.skipped.append(f"{self.name}.{_def_name(defn)}: {e}")
        for mod, names in self.reexports.items():
            self.imports.setdefault(mod, set()).update(names - self.local_names)
        if not blocks and not self.reexports:
            return None
        head = "\n".join(self._header()).strip()
        if not blocks:
            return head + "\n"
        body = "\n\n\n".join(blocks) + "\n"
        return f"{head}\n\n\n{body}" if head else body

    def _header(self) -> list:
        def line(mod: str, names, key=None) -> str:
            return f"from {mod} import {', '.join(sorted(names, key=key))}"

        lines = [line(m, self.used[m]) for m in ("datetime", "typing") if m in self.used]
        lines += [""] if lines else []
        lines += [
            line(m, self.used[m], str.lower)
            for m in ("forge.models", "forge.builtins")
            if m in self.used
        ]
        lines += [line(m, names) for m, names in sorted(self.imports.items())]
        lines += [f"import {m} as {a}" for m, a in sorted(self.aliases.items())]
        if self.tvars:
            lines += ["", *(f'{name} = TypeVar("{name}")' for name in sorted(self.tvars))]
        return lines
