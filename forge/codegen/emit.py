from decimal import Decimal
from functools import lru_cache
from typing import Optional

from forge.builtins import collect_daml_builtins
from forge.codegen.doc import concat, line, nest, render, text
from forge.codegen.maps import is_map_type, render_map_literal, render_map_type
from forge.codegen.maps import required_imports as required_map_imports
from forge.codegen.optional import is_optional_type, render_optional_type
from forge.codegen.optional import required_imports as required_optional_imports
from forge.codegen.sets import is_set_type, render_set_type
from forge.codegen.sets import required_imports as required_set_imports
from forge.exceptions import CompilerPanic
from forge.utils import daml_choice_name
from forge.ir.nodes import (
    IRAssert,
    IRAssign,
    IRAttribute,
    IRBinOp,
    IRBoolOp,
    IRCall,
    IRChoice,
    IRCompare,
    IRConstant,
    Field,
    IRDict,
    IRExprStmt,
    IRFlag,
    IRFor,
    IRFunction,
    IRIf,
    IRInterface,
    IRInterfaceInstance,
    IRList,
    IRModule,
    IRName,
    IRPass,
    IRRecordUpdate,
    IRReturn,
    IRStruct,
    IRSubscript,
    IRTemplate,
    IRTuple,
    IRUnaryOp,
    SourceSpan,
    TypeRef,
)
from forge.models.decorators import Consuming
from forge.codegen.loops import LoopAnalysis, LoopNamer
from forge.codegen.self_mutation import SELF, SelfFieldRewriter, SelfMutationInjector

_PRIMITIVE_TYPE_MAP = {
    "int": "Int",
    "Int": "Int",
    "float": "Decimal",
    "bool": "Bool",
    "Text": "Text",
    "str": "Text",
    "Decimal": "Decimal",
    "Date": "Date",
    "Timestamp": "Time",
    "Party": "Party",
    "None": "()",
}

_ATOMIC_GENERIC_NAMES = ("list", "tuple")

_COMPARE_OP_MAP = {
    "==": "==",
    "!=": "/=",
    "<": "<",
    "<=": "<=",
    ">": ">",
    ">=": ">=",
    "in": "`elem`",
    "not in": "`notElem`",
}
_BOOL_OP_MAP = {"and": "&&", "or": "||"}
_UNARY_OP_MAP = {"not": "not ", "-": "-"}
_BIN_OP_MAP = {"+": "+", "-": "-", "*": "*", "/": "/", "%": "%", "**": "**"}


def _is_text_literal(e) -> bool:
    return isinstance(e, IRConstant) and isinstance(e.value, str)


_CONSUMING_KEYWORD = {
    None: "",
    Consuming.CONSUMING: "",
    Consuming.NON_CONSUMING: "nonconsuming ",
    Consuming.PRE_CONSUMING: "preconsuming ",
    Consuming.POST_CONSUMING: "postconsuming ",
}

_MAX_TUPLE_ACCESSOR_INDEX = 8


def _required_field_type(f: Field) -> TypeRef:
    assert f.type is not None, f"field {f.name!r} is missing a type"
    return f.type


def render_type(t: TypeRef, as_arg: bool = False) -> str:
    rendered = _render_type_inner(t)
    if as_arg and _type_needs_parens_as_arg(t):
        return f"({rendered})"
    return rendered


def _type_needs_parens_as_arg(t: TypeRef) -> bool:
    return bool(t.args) and t.name not in _ATOMIC_GENERIC_NAMES


def _render_type_inner(t: TypeRef) -> str:
    if t.name == "list":
        return f"[{render_type(t.args[0])}]"
    if t.name == "tuple":
        return "(" + ", ".join(render_type(a) for a in t.args) + ")"
    if is_optional_type(t.name):
        return render_optional_type(t, render_type)
    if t.name == "ContractId":
        return f"ContractId {render_type(t.args[0], as_arg=True)}"
    if is_map_type(t.name):
        return render_map_type(t, render_type)
    if is_set_type(t.name):
        return render_set_type(t, render_type)
    if t.name in _PRIMITIVE_TYPE_MAP:
        return _PRIMITIVE_TYPE_MAP[t.name]
    return _external_builtin_renames().get(t.name, t.name)


def _type_ref_references_non_derivable_type(t: TypeRef) -> bool:
    bare_name = t.name.rsplit(".", 1)[-1]
    if bare_name in collect_daml_builtins().no_derive_types:
        return True
    return any(_type_ref_references_non_derivable_type(a) for a in t.args)


def render_constant(value) -> str:
    if value is None:
        return "None"
    if isinstance(value, bool):
        return "True" if value else "False"
    if isinstance(value, str):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    if isinstance(value, Decimal):
        return str(value)
    return str(value)


_NEEDS_PARENS_AS_INFIX_OPERAND = (IRBinOp, IRBoolOp, IRUnaryOp, IRCompare)
_NEEDS_PARENS_AS_CALL_ARG = (IRCall, IRBinOp, IRBoolOp, IRUnaryOp, IRCompare)


def _render_infix_operand(e) -> str:
    rendered = render_expr(e)
    if isinstance(e, _NEEDS_PARENS_AS_INFIX_OPERAND):
        return f"({rendered})"
    return rendered


def _render_call_arg(e) -> str:
    rendered = render_expr(e)
    if isinstance(e, _NEEDS_PARENS_AS_CALL_ARG):
        return f"({rendered})"
    return rendered


_LANGUAGE_BUILTIN_RENAMES = {"len": "length", "ceil": "ceiling", "from_some": "fromSome"}


@lru_cache(maxsize=1)
def _external_builtin_renames() -> dict:
    return {**_LANGUAGE_BUILTIN_RENAMES, **collect_daml_builtins().function_renames}


@lru_cache(maxsize=1)
def _external_field_renames() -> dict:
    return collect_daml_builtins().field_renames


@lru_cache(maxsize=1)
def _builtin_import_modules() -> dict:
    return collect_daml_builtins().function_import_modules


@lru_cache(maxsize=1)
def _case_accessors() -> dict:
    return collect_daml_builtins().case_accessors


def render_expr(e) -> str:
    if isinstance(e, IRName):
        return _external_builtin_renames().get(e.id, e.id)
    if isinstance(e, IRAttribute):
        return f"{_render_atom_for_attr(e.value)}.{_external_field_renames().get(e.attr, e.attr)}"
    if isinstance(e, IRSubscript):
        return _render_subscript(e)
    if isinstance(e, IRCall):
        return _render_call(e)
    if isinstance(e, IRConstant):
        return render_constant(e.value)
    if isinstance(e, IRList):
        return "[" + ", ".join(render_expr(el) for el in e.elements) + "]"
    if isinstance(e, IRTuple):
        return "(" + ", ".join(render_expr(el) for el in e.elements) + ")"
    if isinstance(e, IRDict):
        return render_map_literal(e.keys, e.values, render_expr, e.kind)
    if isinstance(e, IRBinOp):
        op = _BIN_OP_MAP.get(e.op, e.op)
        if e.op == "+" and (_is_text_literal(e.left) or _is_text_literal(e.right)):
            op = "<>"
        elif e.op == "+" and (isinstance(e.left, IRList) or isinstance(e.right, IRList)):
            op = "++"
        return f"{_render_infix_operand(e.left)} {op} {_render_infix_operand(e.right)}"
    if isinstance(e, IRBoolOp):
        op = f" {_BOOL_OP_MAP.get(e.op, e.op)} "
        return op.join(_render_infix_operand(v) for v in e.values)
    if isinstance(e, IRUnaryOp):
        return f"{_UNARY_OP_MAP.get(e.op, e.op)}{_render_infix_operand(e.operand)}"
    if isinstance(e, IRCompare):
        op = _COMPARE_OP_MAP.get(e.op, e.op)
        return f"{_render_infix_operand(e.left)} {op} {_render_infix_operand(e.right)}"
    if isinstance(e, IRRecordUpdate):
        updates_str = ", ".join(f"{name} = {render_expr(v)}" for name, v in e.updates)
        return f"{_render_atom_for_attr(e.base)} {{ {updates_str} }}"
    raise CompilerPanic(f"render_expr: unsupported IR expression {type(e).__name__}")


def _render_atom_for_attr(value) -> str:
    if isinstance(value, IRName):
        return value.id
    return f"({render_expr(value)})"


def _render_subscript(e: IRSubscript) -> str:
    if (
        not e.is_list
        and isinstance(e.index, IRConstant)
        and isinstance(e.index.value, int)
        and e.index.value >= 0
    ):
        if e.index.value <= _MAX_TUPLE_ACCESSOR_INDEX:
            return f"{_render_atom_for_attr(e.value)}._{e.index.value + 1}"
    return f"({render_expr(e.value)}) !! ({render_expr(e.index)})"


def _render_decimal_literal(value) -> str:
    text = str(value)
    text = text if "." in text else f"{text}.0"
    return f"({text} : Decimal)"


def _render_record_field_value(v) -> str:
    rendered = render_expr(v)
    if isinstance(v, IRCall) and v.keywords:
        return f"({rendered})"
    return rendered


def _render_call(e: IRCall) -> str:
    if (
        isinstance(e.func, IRName)
        and e.func.id == "Decimal"
        and len(e.args) == 1
        and not e.keywords
    ):
        if isinstance(e.args[0], IRConstant):
            return _render_decimal_literal(e.args[0].value)
        return f"intToDecimal {_render_call_arg(e.args[0])}"

    if (
        isinstance(e.func, IRName)
        and e.func.id == "range"
        and not e.keywords
        and len(e.args) in (1, 2)
    ):
        start = e.args[0] if len(e.args) == 2 else IRConstant(0)
        stop = e.args[-1]
        return f"[{render_expr(start)} .. ({render_expr(stop)}) - 1]"

    if isinstance(e.func, IRName) and not e.keywords and len(e.args) == 1:
        constructor = _case_accessors().get(e.func.id)
        if constructor is not None:
            scrutinee = _render_call_arg(e.args[0])
            return f"(case {scrutinee} of {constructor} _damlforge_case_val -> Some _damlforge_case_val; _ -> None)"

    func_name = render_expr(e.func)
    if e.keywords:
        renames = _external_field_renames()
        kw_str = ", ".join(
            f"{renames.get(k, k)} = {_render_record_field_value(v)}" for k, v in e.keywords
        )
        return f"{func_name} with {kw_str}"
    if not e.args:
        return func_name
    args_str = " ".join(_render_call_arg(a) for a in e.args)
    return f"{func_name} {args_str}"


class BodyTranslator:
    def __init__(
        self,
        namer: LoopNamer,
        hoisted: list,
        known_effect_fns: frozenset = frozenset(),
        self_type: Optional[str] = None,
    ):
        self.namer = namer
        self.hoisted = hoisted
        self.known_effect_fns = known_effect_fns
        self.self_type = self_type

    def render_body(self, stmts, indent: int, monadic: bool = True, known=frozenset()) -> list:
        rewritten = LoopAnalysis.rewrite_appends(list(stmts), self.namer, self.known_effect_fns)
        tail = lambda i, extra_known=frozenset(), renames=None: self._final_tail(i, monadic)
        return self._translate(rewritten, indent, monadic, tail, known)

    def render_stmt(self, stmt, indent: int, monadic: bool = True) -> list:
        return self.render_body([stmt], indent, monadic)

    @staticmethod
    def _final_tail(i: int, monadic: bool) -> list:
        pad = "  " * i
        return [f"{pad}pure ()"] if monadic else [f"{pad}()"]

    @staticmethod
    def _resolve_all(names, renames: dict) -> list:
        return [renames.get(n, n) for n in names]

    @staticmethod
    def _render_assign_target(s: IRAssign) -> str:
        rendered = render_expr(s.target)
        if s.type is None or not isinstance(s.target, IRName):
            return rendered
        return f"({rendered} : {render_type(s.type)})"

    def _render_leaf(self, s, indent: int, monadic: bool, renames: dict) -> list:
        pad = "  " * indent
        if isinstance(s, IRAssert):
            test = LoopAnalysis.apply_renames(s.test, renames)
            if s.msg is not None:
                msg = LoopAnalysis.apply_renames(s.msg, renames)
                return [f"{pad}assertMsg {render_expr(msg)} ({render_expr(test)})"]
            return [f"{pad}assert ({render_expr(test)})"]
        if isinstance(s, IRAssign):
            value = LoopAnalysis.apply_renames(s.value, renames)
            target = self._render_assign_target(s)
            if monadic and LoopAnalysis.is_effect_call(s.value, self.known_effect_fns):
                return [f"{pad}{target} <- {render_expr(value)}"]
            binding = f"let {target} = {render_expr(value)}"
            return [f"{pad}{binding} in" if not monadic else f"{pad}{binding}"]
        if isinstance(s, IRExprStmt):
            return [f"{pad}{render_expr(LoopAnalysis.apply_renames(s.value, renames))}"]
        raise CompilerPanic(f"_render_leaf: unsupported IR statement {type(s).__name__}")

    def _translate(
        self, stmts, indent, monadic, make_tail, known=frozenset(), renames=None
    ) -> list:
        renames = renames or {}
        pad = "  " * indent
        if not stmts:
            return make_tail(indent, frozenset(), renames)

        first, rest = stmts[0], stmts[1:]

        if isinstance(first, IRReturn):
            if first.value is None:
                return [f"{pad}pure ()"] if monadic else [f"{pad}()"]
            value_expr = render_expr(LoopAnalysis.apply_renames(first.value, renames))
            if monadic and LoopAnalysis.is_effect_call(first.value, self.known_effect_fns):
                return [f"{pad}{value_expr}"]
            already_parenthesized = isinstance(first.value, IRTuple)
            wrapped = value_expr if already_parenthesized else f"({value_expr})"
            return [f"{pad}pure {wrapped}"] if monadic else [f"{pad}{value_expr}"]

        if isinstance(first, IRPass):
            return [f'{pad}error "damlforge: not implemented"']

        if isinstance(first, IRIf):
            branch_tail = make_tail
            cont_lines = []
            if rest:
                branch_stmts = list(first.body) + list(first.orelse)
                cont_vars = LoopAnalysis.collect_accumulators(branch_stmts, known)
                free_after = LoopAnalysis.collect_free_names(rest)
                new_vars = sorted(
                    n
                    for n in LoopAnalysis.collect_assigned_names(branch_stmts)
                    if n not in known and n in free_after and n not in cont_vars
                )
                cont_vars = cont_vars + new_vars
                cont_name = self.namer.next_cont()
                params = " ".join(cont_vars)
                header = f"{cont_name} {params}".rstrip()
                cont_lines = [f"{pad}let {header} = do" if monadic else f"{pad}let {header} ="]
                cont_renames = {k: v for k, v in renames.items() if k not in cont_vars}
                cont_lines.extend(
                    self._translate(
                        rest, indent + 3, monadic, make_tail, known | set(cont_vars), cont_renames
                    )
                )
                if not monadic:
                    cont_lines.append(f"{pad}in")

                def branch_tail(i, extra_known=frozenset(), br_renames=None):
                    args = " ".join(self._resolve_all(cont_vars, br_renames or {}))
                    call = f"{cont_name} {args}".rstrip()
                    return [f"{'  ' * i}{call}"]

            test_expr = render_expr(LoopAnalysis.apply_renames(first.test, renames))
            lines = [f"{pad}if {test_expr}", f"{pad}  then do" if monadic else f"{pad}  then"]
            lines.extend(
                self._translate(list(first.body), indent + 2, monadic, branch_tail, known, renames)
            )
            lines.append(f"{pad}  else do" if monadic else f"{pad}  else")
            lines.extend(
                self._translate(
                    list(first.orelse), indent + 2, monadic, branch_tail, known, renames
                )
            )
            return cont_lines + lines

        if isinstance(first, IRFor):

            def rest_tail(i, extra_known=frozenset(), for_renames=None):
                return self._translate(
                    rest, i, monadic, make_tail, known | extra_known, for_renames or {}
                )

            return self._translate_for(first, indent, monadic, rest_tail, known, renames)

        if isinstance(first, IRAssign) and isinstance(first.target, IRName):
            if first.target.id in known:
                value = LoopAnalysis.apply_renames(first.value, renames)
                fresh = self.namer.next_rebind(first.target.id)
                fresh_target = (
                    f"({fresh} : {render_type(first.type)})" if first.type is not None else fresh
                )
                binding = f"let {fresh_target} = {render_expr(value)}"
                line = f"{pad}{binding}" if monadic else f"{pad}{binding} in"
                new_renames = {**renames, first.target.id: fresh}
                return [line] + self._translate(
                    rest, indent, monadic, make_tail, known, new_renames
                )
            known = known | {first.target.id}

        return self._render_leaf(first, indent, monadic, renames) + self._translate(
            rest, indent, monadic, make_tail, known, renames
        )

    def _wrap_returns_as_some(self, stmts):
        result = []
        for s in stmts:
            if isinstance(s, IRReturn):
                value = s.value if s.value is not None else IRTuple(())
                result.append(IRReturn(IRCall(IRName("Some"), (value,)), src=s.src))
            elif isinstance(s, IRIf):
                result.append(
                    IRIf(
                        s.test,
                        tuple(self._wrap_returns_as_some(s.body)),
                        tuple(self._wrap_returns_as_some(s.orelse)),
                        src=s.src,
                    )
                )
            else:
                result.append(s)
        return result

    def _translate_for(
        self, node: IRFor, indent, monadic, make_tail, known=frozenset(), renames=None
    ) -> list:
        renames = renames or {}
        pad = "  " * indent
        body = LoopAnalysis.rewrite_appends(list(node.body), self.namer, self.known_effect_fns)
        accumulators = LoopAnalysis.collect_accumulators(body, known)
        has_return = LoopAnalysis.body_has_return(body)
        if accumulators and has_return:
            raise CompilerPanic(
                "_translate_for: a `for` loop with both loop-carried accumulator "
                "mutation and an early `return` inside its body is not supported"
            )
        loop_is_monadic = monadic and LoopAnalysis.body_has_ledger_effect(
            body, self.known_effect_fns
        )
        helper = self.namer.next()
        rest_name = "_damlforge_rest"
        captured = sorted(
            (LoopAnalysis.collect_free_names(body) & known) - set(accumulators) - {node.target}
        )
        inner_known = known | {node.target} | set(accumulators)
        fresh_here = set(accumulators) | set(captured) | {node.target}
        inner_renames = {k: v for k, v in renames.items() if k not in fresh_here}
        param_names = captured + accumulators
        base_params = [
            f"({p} : {self.self_type})" if p == SELF and self.self_type else p for p in param_names
        ]
        base_head = f"{helper} {' '.join(base_params + ['[]'])}".strip()
        rec_head = f"{helper} {' '.join(param_names + [f'({node.target} :: {rest_name})'])}"
        resolved_captured = self._resolve_all(captured, renames)
        iter_expr = render_expr(LoopAnalysis.apply_renames(node.iter, renames))

        if accumulators:
            acc_tuple = f"({', '.join(accumulators)})" if len(accumulators) > 1 else accumulators[0]
            base_rhs = f"pure {acc_tuple}" if loop_is_monadic else acc_tuple

            def recursive_tail(i, extra_known=frozenset(), rec_renames=None):
                args = captured + self._resolve_all(accumulators, rec_renames or {})
                call = f"{helper} {' '.join(args)} {rest_name}".strip()
                return [f"{'  ' * i}{call}"]

            def_lines = [
                f"{base_head} = {base_rhs}",
                f"{rec_head} = do" if loop_is_monadic else f"{rec_head} =",
            ]
            def_lines.extend(
                self._translate(
                    body, 1, loop_is_monadic, recursive_tail, inner_known, inner_renames
                )
            )
            self.hoisted.extend(def_lines)
            self.hoisted.append("")

            resolved_acc = self._resolve_all(accumulators, renames)
            call_expr = f"{helper} {' '.join(resolved_captured + resolved_acc)} {iter_expr}".strip()
            fresh_names = [self.namer.next_rebind(a) for a in accumulators]
            fresh_tuple = ", ".join(fresh_names) if len(fresh_names) > 1 else fresh_names[0]
            fresh_bind_target = f"({fresh_tuple})" if len(fresh_names) > 1 else fresh_tuple
            lines = []
            if loop_is_monadic:
                lines.append(f"{pad}{fresh_bind_target} <- {call_expr}")
            else:
                suffix = "" if monadic else " in"
                lines.append(f"{pad}let {fresh_bind_target} = {call_expr}{suffix}")
            post_renames = {**renames, **dict(zip(accumulators, fresh_names))}
            lines.extend(make_tail(indent, set(accumulators), post_renames))
            return lines

        if has_return:
            wrapped_body = self._wrap_returns_as_some(body)
            base_rhs = "pure None" if loop_is_monadic else "None"

            def recursive_tail_b(i, extra_known=frozenset(), rec_renames=None):
                call = f"{helper} {' '.join(captured)} {rest_name}".strip()
                return [f"{'  ' * i}{call}"]

            def_lines = [
                f"{base_head} = {base_rhs}",
                f"{rec_head} = do" if loop_is_monadic else f"{rec_head} =",
            ]
            def_lines.extend(
                self._translate(
                    wrapped_body, 1, loop_is_monadic, recursive_tail_b, inner_known, inner_renames
                )
            )
            self.hoisted.extend(def_lines)
            self.hoisted.append("")

            call_expr = f"{helper} {' '.join(resolved_captured)} {iter_expr}".strip()
            maybe_name = self.namer.next_rebind("maybe")
            early_name = self.namer.next_rebind("early")
            lines = [
                (
                    f"{pad}{maybe_name} <- {call_expr}"
                    if loop_is_monadic
                    else f"{pad}let {maybe_name} = {call_expr}"
                )
            ]
            lines.append(f"{pad}case {maybe_name} of")
            lines.append(
                f"{pad}  Some {early_name} -> " + (f"pure {early_name}" if monadic else early_name)
            )
            lines.append(f"{pad}  None -> do" if monadic else f"{pad}  None ->")
            lines.extend(make_tail(indent + 2, frozenset(), renames))
            return lines

        if not loop_is_monadic:
            return make_tail(indent, frozenset(), renames)

        def recursive_tail_c(i, extra_known=frozenset(), rec_renames=None):
            call = f"{helper} {' '.join(captured)} {rest_name}".strip()
            return [f"{'  ' * i}{call}"]

        def_lines = [f"{base_head} = pure ()", f"{rec_head} = do"]
        def_lines.extend(
            self._translate(body, 1, loop_is_monadic, recursive_tail_c, inner_known, inner_renames)
        )
        self.hoisted.extend(def_lines)
        self.hoisted.append("")

        call_expr = f"{helper} {' '.join(resolved_captured)} {iter_expr}".strip()
        lines = [f"{pad}_ <- {call_expr}"]
        lines.extend(make_tail(indent, frozenset(), renames))
        return lines


def render_body(
    stmts,
    indent: int,
    monadic: bool = True,
    known=frozenset(),
    hoisted: list = None,
    namer: LoopNamer = None,
    self_type: str = None,
    known_effect_fns: frozenset = frozenset(),
) -> list:
    namer = namer if namer is not None else LoopNamer()
    translator = BodyTranslator(
        namer, hoisted if hoisted is not None else [], known_effect_fns, self_type
    )
    return translator.render_body(stmts, indent, monadic, known)


def render_stmt(stmt, indent: int, monadic: bool = True) -> list:
    return render_body([stmt], indent, monadic)


class Emitter:
    def __init__(self, known_effect_fns: frozenset = frozenset()):
        self.lines: list = []
        self.mappings: list = []
        self.namer = LoopNamer()
        self.hoisted: list = []
        self.known_effect_fns = known_effect_fns

    def line(self, text: str = "") -> None:
        self.lines.append(text)

    def lines_block(self, texts) -> None:
        self.lines.extend(texts)

    def record(self, src: Optional[SourceSpan], kind: str, name: str, start_line: int) -> None:
        if src is None:
            return
        self.mappings.append(
            {
                "generated": {"startLine": start_line, "endLine": len(self.lines)},
                "source": {
                    "startLine": src.lineno,
                    "startColumn": src.col_offset,
                    "endLine": src.end_lineno,
                    "endColumn": src.end_col_offset,
                },
                "kind": kind,
                "name": name,
            }
        )

    def _translator(self, self_type: Optional[str] = None) -> BodyTranslator:
        return BodyTranslator(self.namer, self.hoisted, self.known_effect_fns, self_type)

    def emit_struct(self, s: IRStruct) -> None:
        start = len(self.lines) + 1
        parts = [text(f"data {s.name} = {s.name}")]
        if s.fields:
            field_lines = concat(
                concat([line(), text(f"{f.name} : {render_type(_required_field_type(f))}")])
                for f in s.fields
            )
            parts.append(nest(2, concat([line(), text("with"), nest(2, field_lines)])))
        if not any(
            _type_ref_references_non_derivable_type(_required_field_type(f)) for f in s.fields
        ):
            parts.append(nest(2, concat([line(), text("deriving (Eq, Show)")])))
        self.lines_block(render(concat(parts)))
        self.record(s.src, "struct", s.name, start)

    def emit_flag(self, f: IRFlag) -> None:
        start = len(self.lines) + 1
        if not f.values:
            doc = text(f"data {f.name}")
        else:
            doc = concat(
                [
                    text(f"data {f.name} = " + " | ".join(f.values)),
                    nest(2, concat([line(), text("deriving (Eq, Show)")])),
                ]
            )
        self.lines_block(render(doc))
        self.record(f.src, "flag", f.name, start)

    def emit_choice(
        self,
        c: IRChoice,
        container_name: str,
        indent: int,
        field_types=None,
        delegate_to: Optional[str] = None,
    ) -> None:
        start = len(self.lines) + 1
        is_template_choice = field_types is not None
        known = frozenset(a.name for a in c.args)

        body = c.body
        display_return_type = c.return_type
        if is_template_choice:
            body = SelfFieldRewriter.rewrite_stmts(list(body), field_types)
            known = known | {SELF}
            if SelfMutationInjector.body_mutates_self(body):
                body = SelfMutationInjector.inject_self_create(body)
                original = c.return_type if c.return_type is not None else TypeRef("tuple", ())
                display_return_type = TypeRef(
                    "tuple", (TypeRef("ContractId", (TypeRef(container_name),)), original)
                )

        consuming_kw = _CONSUMING_KEYWORD.get(c.consuming, "")
        return_type = render_type(display_return_type) if display_return_type is not None else "()"
        controller_expr = (
            render_expr(c.controller) if c.controller is not None else "-- MISSING controller"
        )

        parts = [text(f"{consuming_kw}choice {daml_choice_name(c.name)} : {return_type}")]
        if c.args:
            arg_lines = concat(
                concat(
                    [
                        line(),
                        text(f"{a.name} : {render_type(a.type) if a.type is not None else '()'}"),
                    ]
                )
                for a in c.args
            )
            parts.append(nest(2, concat([line(), text("with"), nest(2, arg_lines)])))
        if c.observer is not None:
            parts.append(nest(2, concat([line(), text(f"observer {render_expr(c.observer)}")])))
        parts.append(nest(2, concat([line(), text(f"controller {controller_expr}")])))

        if delegate_to is not None:
            arg_names = " ".join(a.name for a in c.args)
            call = f"{delegate_to} this self" + (f" {arg_names}" if arg_names else "")
            parts.append(nest(2, concat([line(), text(f"do {call}")])))
            self.lines_block(render(concat(parts), initial_indent=indent * 2))
            self.record(c.src, "choice", f"{container_name}.{c.name}", start)
            return

        parts.append(nest(2, concat([line(), text("do")])))
        self.lines_block(render(concat(parts), initial_indent=indent * 2))

        body_lines = [f"{'  ' * indent}    let {SELF} = this"] if is_template_choice else []
        translator = self._translator(self_type=container_name if is_template_choice else None)
        body_lines.extend(translator.render_body(body, indent + 2, known=known))
        self.lines_block(body_lines)
        self.record(c.src, "choice", f"{container_name}.{c.name}", start)

    def emit_interface_choice_impl(
        self, c: IRChoice, container_name: str, indent: int, field_types
    ) -> None:
        start = len(self.lines) + 1
        arg_names = [a.name for a in c.args]
        header = f"{c.name}_impl _self" + "".join(f" {n}" for n in arg_names)
        self.lines_block([f"{'  ' * indent}{header} = do"])

        body = SelfFieldRewriter.rewrite_stmts(list(c.body), field_types)
        known = frozenset(arg_names) | {SELF}
        body_lines = [f"{'  ' * indent}    let {SELF} = this"]
        translator = self._translator(self_type=container_name)
        body_lines.extend(translator.render_body(body, indent + 2, known=known))
        self.lines_block(body_lines)
        self.record(c.src, "interface_choice_impl", f"{container_name}.{c.name}_impl", start)

    def emit_function(self, fn: IRFunction) -> None:
        start = len(self.lines) + 1
        is_monadic = "ledger_effect" in fn.decorators
        return_type = (
            render_type(fn.return_type, as_arg=True) if fn.return_type is not None else "()"
        )
        full_return = f"Update {return_type}" if is_monadic else return_type
        arg_types = [
            render_type(a.type, as_arg=True) if a.type is not None else "()" for a in fn.args
        ]
        self.line(f"{fn.name} : {' -> '.join(arg_types + [full_return])}")
        header = f"{fn.name} {' '.join(a.name for a in fn.args)}".rstrip()
        self.line(f"{header} = do" if is_monadic else f"{header} =")
        translator = self._translator()
        self.lines_block(
            translator.render_body(
                fn.body, 1, monadic=is_monadic, known=frozenset(a.name for a in fn.args)
            )
        )
        self.record(fn.src, "function", fn.name, start)

    def emit_template(self, t: IRTemplate) -> None:
        start = len(self.lines) + 1
        parts = [text(f"template {t.name}")]
        if t.fields:
            field_lines = concat(
                concat([line(), text(f"{f.name} : {render_type(_required_field_type(f))}")])
                for f in t.fields
            )
            parts.append(nest(2, concat([line(), text("with"), nest(2, field_lines)])))

        signatory_expr = (
            render_expr(t.signatory) if t.signatory is not None else "-- MISSING signatory"
        )
        where_parts = [line(), text(f"signatory {signatory_expr}")]
        if t.observer is not None:
            where_parts.extend([line(), text(f"observer {render_expr(t.observer)}")])

        ensure_conditions = []
        if t.init:
            for b in t.init.body:
                if (
                    isinstance(b, IRExprStmt)
                    and isinstance(b.value, IRCall)
                    and isinstance(b.value.func, IRName)
                    and b.value.func.id in ("ensure", "assert")
                    and b.value.args
                ):
                    ensure_conditions.append(render_expr(b.value.args[0]))
                if isinstance(b, IRAssert) and b.test is not None:
                    ensure_conditions.append(render_expr(b.test))
        if ensure_conditions:
            where_parts.extend([line(), text("ensure " + " && ".join(ensure_conditions))])

        parts.append(nest(2, concat([line(), text("where"), nest(2, concat(where_parts))])))
        self.lines_block(render(concat(parts)))

        field_types = {f.name: f.type for f in t.fields}
        for c in t.choices:
            self.line("")
            self.emit_choice(c, t.name, indent=2, field_types=field_types)
        for ii in t.interface_instances:
            self.line("")
            self.emit_interface_instance(ii, t.name, field_types)
        self.record(t.src, "template", t.name, start)

    def emit_interface(self, i: IRInterface) -> None:
        start = len(self.lines) + 1
        requires_clause = f" requires {', '.join(i.requires)}" if i.requires else ""
        view_type = render_type(i.view) if i.view is not None else "()"

        header = concat(
            [
                text(f"interface {i.name}{requires_clause} where"),
                nest(2, concat([line(), text(f"viewtype {view_type}")])),
            ]
        )
        self.lines_block(render(header))

        for c in i.choices:
            self.line("")
            impl_name = f"{c.name}_impl"
            arg_types = [
                render_type(a.type, as_arg=True) if a.type is not None else "()" for a in c.args
            ]
            return_type_str = (
                render_type(c.return_type, as_arg=True) if c.return_type is not None else "()"
            )
            sig_types = " -> ".join([f"ContractId {i.name}", *arg_types, f"Update {return_type_str}"])
            self.lines_block([f"  {impl_name} : {sig_types}"])
            self.line("")
            self.emit_choice(c, i.name, indent=1, delegate_to=impl_name)
        self.record(i.src, "interface", i.name, start)

    def emit_interface_instance(
        self, ii: IRInterfaceInstance, template_name: str, field_types
    ) -> None:
        start = len(self.lines) + 1

        rendered_view = "-- MISSING view"
        if ii.view is not None:
            view_body = SelfFieldRewriter.rewrite_stmts(list(ii.view.body), field_types)
            view_expr = (
                view_body[-1].value
                if len(view_body) == 1 and isinstance(view_body[-1], IRReturn)
                else None
            )
            if view_expr is not None:
                rendered_view = f"let {SELF} = this in {render_expr(view_expr)}"

        header = concat(
            [
                text(f"interface instance {ii.interface} for {template_name} where"),
                nest(2, concat([line(), text(f"view = {rendered_view}")])),
            ]
        )
        self.lines_block(render(header, initial_indent=4))

        for c in ii.choices:
            self.line("")
            self.emit_interface_choice_impl(c, template_name, indent=3, field_types=field_types)
        self.record(ii.src, "interface_instance", f"{ii.interface}_for_{template_name}", start)

    def _render_header(self, imports, body_source: str, module_name: Optional[str]) -> str:
        header = f"module {module_name} where\n\n" if module_name is not None else ""
        builtins = collect_daml_builtins()
        for imp in imports:
            if imp.alias is not None:
                header += f"import qualified {imp.module} as {imp.alias}\n\n"
                continue
            if imp.names is None:
                header += f"import {imp.module}\n\n"
                continue
            present = set(imp.names)
            rendered_names = []
            for n in imp.names:
                constructor_of = builtins.constructor_of.get(n)
                if constructor_of is not None and constructor_of in present:
                    continue
                renamed = _external_builtin_renames().get(n, n)
                if renamed in builtins.constructor_types or n in imp.constructor_names:
                    renamed = f"{renamed}(..)"
                rendered_names.append(renamed)
            header += f"import {imp.module} ({', '.join(rendered_names)})\n\n"
        for import_line in required_map_imports(body_source):
            header += import_line
        for import_line in required_set_imports(body_source):
            header += import_line
        if " !! " in body_source:
            header += "import DA.List ((!!))\n\n"
        for import_line in required_optional_imports(body_source):
            header += import_line
        required_modules = {
            module
            for daml_name, module in _builtin_import_modules().items()
            if daml_name in body_source
        }
        for module in sorted(required_modules):
            header += f"import {module}\n\n"
        return header

    def generate(self, module: IRModule, module_name: Optional[str] = None):
        for s in module.structs:
            self.emit_struct(s)
            self.line("")
        for f in module.flags:
            self.emit_flag(f)
            self.line("")
        for fn in module.functions:
            self.emit_function(fn)
            self.line("")
        for i in module.interfaces:
            self.emit_interface(i)
            self.line("")
        for t in module.templates:
            self.emit_template(t)
            self.line("")
        if self.hoisted:
            self.lines_block(self.hoisted)

        body_source = "\n".join(self.lines).rstrip("\n") + "\n"
        mappings = self.mappings
        header = self._render_header(module.imports, body_source, module_name)
        if header:
            offset = header.count("\n")
            mappings = [
                {
                    **m,
                    "generated": {
                        "startLine": m["generated"]["startLine"] + offset,
                        "endLine": m["generated"]["endLine"] + offset,
                    },
                }
                for m in mappings
            ]
        source = header + body_source
        return source, {"mappings": mappings}


def generate_daml(module: IRModule, module_name: Optional[str] = None):
    known_effect_fns = (
        frozenset(fn.name for fn in module.functions if "ledger_effect" in fn.decorators)
        | collect_daml_builtins().ledger_effect_fns
    )
    return Emitter(known_effect_fns).generate(module, module_name)
