import keyword
from functools import partial

from dazl._gen.com.digitalasset.daml.lf.archive.daml_lf2_pb2 import BuiltinType
from dazl.damlast.util import module_local_name, module_name

from forge.stubgen.parties import ARG, TPL, VIEW, PartyRefs

_RESERVED = {"struct", "interface", "event", "enum", "self"}

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

_GENERIC_PRIMS = {
    "LIST": "list",
    "CONTRACT_ID": "ContractId",
    "OPTIONAL": "Optional",
    "TEXTMAP": "TextMap",
    "GENMAP": "GenMap",
}

_FORGE_NAMES = {"Decimal", "Party", "ContractId", "Optional", "TextMap", "GenMap"}
_TIME_NAMES = {"datetime", "date", "timedelta"}

_STD_TYPES = {("DA.Time.Types", "RelTime"): "timedelta", ("DA.Set.Types", "Set"): "set"}


class Unsupported(Exception):
    pass


def _line(defn) -> int:
    loc = getattr(defn, "location", None)
    rng = getattr(loc, "range", None)
    return getattr(rng, "start_line", 0) or 0


def _prim_name(t):
    return BuiltinType.Name(int(t.prim.prim)) if t.prim is not None else None


def _party_kind(t):
    name = _prim_name(t)
    if name == "PARTY":
        return "one"
    if name == "LIST" and t.prim.args and _prim_name(t.prim.args[0]) == "PARTY":
        return "many"
    return None


def _party_expr(refs: list, kind, render, as_list: bool) -> str:
    parts = []
    singles = []
    for ref in refs:
        found = kind(ref)
        if found == "one":
            singles.append(render(ref))
        elif found == "many":
            if singles:
                parts.append(f"[{', '.join(singles)}]")
                singles = []
            parts.append(render(ref))
    if singles:
        parts.append(f"[{', '.join(singles)}]")
    if not as_list and len(parts) == 1 and parts[0].startswith("[") and "," not in parts[0]:
        return parts[0][1:-1]
    return " + ".join(parts)


def _tpl_party(ref) -> str:
    return ".".join(ref[1])


def _iface_party(ref) -> str:
    path = ".".join(ref[1])
    return f"view(self).{path}" if ref[0] == VIEW else path


class ModuleStub:
    def __init__(self, module, types: dict, values: dict):
        self.module = module
        self.name = str(module.name)
        self.types = types
        self.refs = PartyRefs(values)
        self.forge: set = set()
        self.times: set = set()
        self.imports: dict = {}
        self.aliases: dict = {}
        self.skipped: list = []
        self.local_names: set = set()

    def type_ref(self, t) -> str:
        if t.prim is not None:
            return self._prim(t.prim)
        if t.con is not None:
            return self._con(t.con)
        raise Unsupported("type variables, synonyms and structural types have no .vy form")

    def _prim(self, prim) -> str:
        kind = BuiltinType.Name(int(prim.prim))
        if kind in _PRIMS:
            name = _PRIMS[kind]
            self._use(name)
            return name
        if kind not in _GENERIC_PRIMS:
            raise Unsupported(f"builtin type {kind} has no .vy form")
        name = _GENERIC_PRIMS[kind]
        self._use(name)
        return f"{name}[{', '.join(self.type_ref(a) for a in prim.args)}]"

    def _con(self, con) -> str:
        mod = str(module_name(con.tycon))
        name = module_local_name(con.tycon)
        args = [self.type_ref(a) for a in con.args]
        std = _STD_TYPES.get((mod, name))
        if std is None and name.startswith("Tuple") and mod in ("DA.Types", "GHC.Tuple"):
            std = "tuple"
        if std is not None:
            self._use(std)
            return f"{std}[{', '.join(args)}]" if args else std
        ref = name if mod == self.name else self._import(mod, name)
        return f"{ref}[{', '.join(args)}]" if args else ref

    def _use(self, name: str) -> None:
        if name in _FORGE_NAMES:
            self.forge.add(name)
        elif name in _TIME_NAMES:
            self.times.add(name)

    def _import(self, mod: str, name: str) -> str:
        owner = next((m for m, names in self.imports.items() if name in names), None)
        if owner in (None, mod) and name not in self.local_names:
            self.imports.setdefault(mod, set()).add(name)
            return name
        alias = mod.rsplit(".", 1)[-1]
        self.aliases[mod] = alias
        return f"{alias}.{name}"

    def record(self, con) -> list:
        key = (str(module_name(con.tycon)), module_local_name(con.tycon))
        dt = self.types.get(key)
        if dt is None or dt.record is None:
            raise Unsupported(f"record {key[1]} not found in the DAR")
        return list(dt.record.fields)

    def _fields(self, fields, indent: str) -> list:
        lines = []
        for f in fields:
            if keyword.iskeyword(f.field) or f.field in _RESERVED:
                raise Unsupported(f"field name `{f.field}` is reserved in .vy")
            lines.append(f"{indent}{f.field}: {self.type_ref(f.type)}")
        return lines

    def _params(self, fields) -> str:
        return ", ".join(line.strip() for line in self._fields(fields, ""))

    def struct(self, dt) -> list:
        body = self._fields(dt.record.fields, "    ") or ["    pass"]
        return [f"struct {dt.name}:", *body]

    def variant(self, dt) -> list:
        self.forge.add("variant")
        lines = ["@variant", f"class {dt.name}:"]
        if dt.enum is not None:
            return lines + [f"    def {c}(): pass" for c in dt.enum.constructors]
        for f in dt.variant.fields:
            synth = f.type.con
            if synth is not None and module_local_name(synth.tycon) == f"{dt.name}.{f.field}":
                self.forge.add("variant_record")
                lines.append("    @variant_record")
                lines.append(f"    def {f.field}({self._params(self.record(synth))}): pass")
            elif _prim_name(f.type) == "UNIT":
                lines.append(f"    def {f.field}(): pass")
            else:
                lines.append(f"    def {f.field}(value: {self.type_ref(f.type)}): pass")
        return lines

    def _path_kind(self, roots: dict, ref):
        role, path = ref
        t = roots.get((role, path[0])) if path else None
        for field in path[1:]:
            dt = self.types.get(self._key(t.con.tycon)) if t is not None and t.con else None
            if dt is None or dt.record is None:
                return None
            t = next((f.type for f in dt.record.fields if f.field == field), None)
        return _party_kind(t) if t is not None else None

    def _choice(self, ch, env: dict, roots: dict, render, fallback: str) -> list:
        self.forge.add("choice")
        args = self.record(ch.arg_binder.type.con)
        roots.update({(ARG, f.field): f.type for f in args})
        kind = partial(self._path_kind, roots)
        ctrl = _party_expr(self.refs.collect(ch.controllers, env), kind, render, False)
        if not ctrl:
            first = next((f.field for f in args if _party_kind(f.type) == "one"), None)
            ctrl = first or fallback
        opts = [f"controller={ctrl}"]
        opts.append("consuming=True" if ch.consuming else 'consuming="nonconsuming"')
        if ch.observers is not None:
            obs = _party_expr(self.refs.collect(ch.observers, env), kind, render, True)
            if obs:
                opts.append(f"observer={obs}")
        params = self._params(args)
        sig = f"self, {params}" if params else "self"
        return [
            f"    @choice({', '.join(opts)})",
            f"    def {ch.name}({sig}) -> {self.type_ref(ch.ret_type)}:",
            "        pass",
        ]

    def interface(self, iface) -> list:
        view = iface.view
        bases = [self._con_name(r) for r in iface.requires]
        view_dt = self.types.get(self._key(view.con.tycon)) if view.con is not None else None
        roots = {}
        if view_dt is not None and view_dt.record is not None:
            roots = {(VIEW, f.field): f.type for f in view_dt.record.fields}
        if _prim_name(view) != "UNIT":
            bases.append(f"view={self.type_ref(view)}")
        head = (
            f"interface {iface.name}({', '.join(bases)}):" if bases else f"interface {iface.name}:"
        )
        first = next((f for (_, f), t in roots.items() if _party_kind(t) == "one"), None)
        fallback = f"view(self).{first}" if first else "[]"
        lines = [head]
        for ch in iface.choices:
            if ch.name == "Archive":
                continue
            env = {iface.param: (TPL, ()), ch.arg_binder.var: (ARG, ())}
            lines.extend(self._choice(ch, env, dict(roots), _iface_party, fallback))
            lines.append("")
        return lines[:-1] if len(lines) > 1 else lines + ["    pass"]

    def template(self, tpl) -> list:
        self.forge.update({"template", "Party"})
        fields = self.types[(self.name, str(tpl.tycon))].record.fields
        roots = {(TPL, f.field): f.type for f in fields}
        kind = partial(self._path_kind, roots)
        env = {tpl.param: (TPL, ())}
        sig = _party_expr(self.refs.collect(tpl.signatories, env), kind, _tpl_party, True)
        if not sig:
            first = [(TPL, (f.field,)) for f in fields if _party_kind(f.type)][:1]
            sig = _party_expr(first, kind, _tpl_party, True) or "[]"
        lines = ["@template", f"class {tpl.tycon}:", *self._fields(fields, "    "), ""]
        lines.append(f"    signatory: list[Party] = {sig}")
        if tpl.observers is not None:
            obs = _party_expr(self.refs.collect(tpl.observers, env), kind, _tpl_party, True)
            if obs:
                lines.append(f"    observer: list[Party] = {obs}")
        for ch in tpl.choices:
            if ch.name == "Archive":
                continue
            ch_env = {tpl.param: (TPL, ()), ch.arg_binder.var: (ARG, ())}
            lines.append("")
            lines.extend(self._choice(ch, ch_env, dict(roots), _tpl_party, sig))
        return lines

    def _key(self, tycon):
        return (str(module_name(tycon)), module_local_name(tycon))

    def _con_name(self, tycon) -> str:
        mod, name = self._key(tycon)
        return name if mod == self.name else self._import(mod, name)

    def _definitions(self) -> list:
        tpls = {str(t.tycon) for t in self.module.templates}
        choices = {c.name for t in self.module.templates for c in t.choices}
        choices |= {c.name for i in self.module.interfaces for c in i.choices}
        defs: list = []
        for dt in self.module.data_types:
            name = str(dt.name)
            if dt.interface is not None or "." in name or name in tpls or name in choices:
                continue
            if dt.params:
                self.skipped.append(f"{self.name}.{name}: generic data types are not supported")
            elif dt.record is not None:
                defs.append((dt, self.struct))
            elif dt.variant is not None or dt.enum is not None:
                defs.append((dt, self.variant))
        defs.sort(key=lambda d: _line(d[0]))
        defs.extend((i, self.interface) for i in self.module.interfaces)
        defs.extend((t, self.template) for t in sorted(self.module.templates, key=_line))
        return defs

    def render(self):
        defs = self._definitions()
        self.local_names = {str(d.name) for d, _ in defs}
        blocks = []
        for defn, emit in defs:
            try:
                blocks.append("\n".join(emit(defn)))
            except Unsupported as e:
                self.skipped.append(f"{self.name}.{defn.name}: {e}")
        if not blocks:
            return None
        head = "\n".join(self._header()).strip()
        body = "\n\n\n".join(blocks) + "\n"
        return f"{head}\n\n\n{body}" if head else body

    def _header(self) -> list:
        lines = []
        if self.times:
            lines.append(f"from datetime import {', '.join(sorted(self.times))}")
            lines.append("")
        if self.forge:
            lines.append(f"from forge.models import {', '.join(sorted(self.forge, key=str.lower))}")
        for mod in sorted(self.imports):
            lines.append(f"from {mod} import {', '.join(sorted(self.imports[mod]))}")
        for mod in sorted(self.aliases):
            lines.append(f"import {mod} as {self.aliases[mod]}")
        return lines
