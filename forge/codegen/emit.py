from decimal import Decimal
from functools import lru_cache
from typing import Optional

from forge.builtins import collect_daml_builtins
from forge.exceptions import CompilerPanic
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
    IRDict,
    IRExprStmt,
    IRFlag,
    IRFor,
    IRFunction,
    IRIf,
    IRInterface,
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
from forge.codegen.loops import (
    LoopNamer,
    body_has_ledger_effect,
    collect_accumulators,
    is_effect_call,
    rewrite_appends,
)
from forge.codegen.self_mutation import (
    SELF,
    body_mutates_self,
    inject_self_create,
    rewrite_self_stmts,
)

_PRIMITIVE_TYPE_MAP = {
    "int": "Int",
    "Int": "Int",
    "float": "Decimal",
    "bool": "Bool",
    "Text": "Text",
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
_CONSUMING_KEYWORD = {
    None: "",
    Consuming.CONSUMING: "",
    Consuming.NON_CONSUMING: "nonconsuming ",
    Consuming.PRE_CONSUMING: "preconsuming ",
    Consuming.POST_CONSUMING: "postconsuming ",
}

_MAX_TUPLE_ACCESSOR_INDEX = 8


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
    return _PRIMITIVE_TYPE_MAP.get(t.name, t.name)


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


_LANGUAGE_BUILTIN_RENAMES = {"len": "length"}


@lru_cache(maxsize=1)
def _external_builtin_renames() -> dict:
    return {**_LANGUAGE_BUILTIN_RENAMES, **collect_daml_builtins().function_renames}


@lru_cache(maxsize=1)
def _external_field_renames() -> dict:
    return collect_daml_builtins().field_renames


@lru_cache(maxsize=1)
def _builtin_import_modules() -> dict:
    return collect_daml_builtins().function_import_modules


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
        pairs = ", ".join(
            f"({render_expr(k)}, {render_expr(v)})" for k, v in zip(e.keys, e.values)
        )
        return f"TextMap.fromList [{pairs}]"
    if isinstance(e, IRBinOp):
        op = _BIN_OP_MAP.get(e.op, e.op)
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
    if isinstance(e.index, IRConstant) and isinstance(e.index.value, int) and e.index.value >= 0:
        if e.index.value <= _MAX_TUPLE_ACCESSOR_INDEX:
            return f"{_render_atom_for_attr(e.value)}._{e.index.value + 1}"
    return f"({render_expr(e.value)}) !! ({render_expr(e.index)})"


def _render_decimal_literal(value) -> str:
    text = str(value)
    return text if "." in text else f"{text}.0"


def _render_call(e: IRCall) -> str:
    # DamlForge source constructs Decimal values by calling `Decimal(N)`, but real
    # Daml has no such constructor function - it just uses numeric literals (`0.0`).
    if (
        isinstance(e.func, IRName)
        and e.func.id == "Decimal"
        and len(e.args) == 1
        and not e.keywords
        and isinstance(e.args[0], IRConstant)
    ):
        return _render_decimal_literal(e.args[0].value)

    # `range(stop)` / `range(start, stop)` is a `for`-loop-iterable idiom with no
    # Daml callable equivalent - it becomes a real Daml enumeration list.
    if isinstance(e.func, IRName) and e.func.id == "range" and not e.keywords and len(e.args) in (1, 2):
        start = e.args[0] if len(e.args) == 2 else IRConstant(0)
        stop = e.args[-1]
        return f"[{render_expr(start)} .. ({render_expr(stop)}) - 1]"

    func_name = render_expr(e.func)
    if e.keywords:
        kw_str = ", ".join(f"{k} = {render_expr(v)}" for k, v in e.keywords)
        return f"{func_name} with {kw_str}"
    if not e.args:
        return func_name
    args_str = " ".join(_render_call_arg(a) for a in e.args)
    return f"{func_name} {args_str}"


def _render_leaf(s, indent: int, monadic: bool) -> list:
    """Render one non-control-flow statement. In monadic (do-block) context these are
    ordinary statements; in pure context, `let`-bindings need a trailing `in` since a
    pure function body is one expression, not a sequence of statements."""
    pad = "  " * indent
    if isinstance(s, IRAssert):
        if s.msg is not None:
            return [f"{pad}assertMsg {render_expr(s.msg)} ({render_expr(s.test)})"]
        return [f"{pad}assert ({render_expr(s.test)})"]
    if isinstance(s, IRAssign):
        if monadic and is_effect_call(s.value):
            # `create`/`fetch`/`exercise`/`archive`/`lookup` are `Update` actions,
            # not pure values - binding their result needs `<-`, not `let =`.
            return [f"{pad}{render_expr(s.target)} <- {render_expr(s.value)}"]
        binding = f"let {render_expr(s.target)} = {render_expr(s.value)}"
        return [f"{pad}{binding} in" if not monadic else f"{pad}{binding}"]
    if isinstance(s, IRPass):
        # `pure ()` only type-checks when the enclosing return type is really `()` -
        # DamlForge's `pass` marks an abstract/unimplemented body (e.g. an interface's
        # choice declaration) whose return type is usually something else entirely.
        # `error` unifies with any type, so this always type-checks; it only fails at
        # runtime if the (unimplemented) body is ever actually exercised.
        return [f'{pad}error "damlforge: not implemented"']
    if isinstance(s, IRExprStmt):
        return [f"{pad}{render_expr(s.value)}"]
    raise CompilerPanic(f"_render_leaf: unsupported IR statement {type(s).__name__}")


def translate_sequence(stmts, indent: int, monadic: bool, make_tail, namer: LoopNamer, known=frozenset()) -> list:
    """
    Continuation-passing translation of a statement sequence into Daml lines.

    `make_tail(indent, extra_known=frozenset())` supplies the lines - rendered
    at the given indent, with `extra_known` names additionally treated as bound
    - for "what happens when this sequence completes normally" (falls off the
    end without an explicit `return`): threaded into both branches of every
    `if` and the "list exhausted" base case of every `for` loop. Taking
    `indent` as a parameter (rather than closing over a fixed one) lets the
    same tail be re-rendered at whatever depth it ends up nested at - e.g.
    inside a loop helper's base case, one level deeper than where the loop
    itself sits. An explicit `return` ends the sequence immediately, ignoring
    `make_tail` entirely - exactly Python's own semantics, and exactly what
    lets a `for` loop compose correctly with code that follows it (the code
    after a loop is just the loop's own "list exhausted" continuation).

    `known` is the set of names already bound before this sequence starts -
    used to tell a genuine loop-carried accumulator (a name mutated that
    already existed outside the loop/if it's mutated in) apart from a name's
    first binding in this scope (e.g. a per-iteration local reset every time),
    which must never be threaded as a recursion parameter since no outer
    binding for it exists to pass in.
    """
    pad = "  " * indent
    if not stmts:
        return make_tail(indent)

    first, rest = stmts[0], stmts[1:]

    if isinstance(first, IRReturn):
        if first.value is None:
            return [f"{pad}pure ()"] if monadic else [f"{pad}()"]
        value_expr = render_expr(first.value)
        # a tuple/unit value already renders its own parens - don't add a second pair
        already_parenthesized = isinstance(first.value, IRTuple)
        wrapped = value_expr if already_parenthesized else f"({value_expr})"
        return [f"{pad}pure {wrapped}"] if monadic else [f"{pad}{value_expr}"]

    if isinstance(first, IRIf):
        branch_tail = make_tail
        cont_lines = []
        if rest:
            # `rest` (everything after this `if`) is this branch's continuation,
            # and BOTH the then- and else-branch need it - render it exactly once,
            # bound to a shared helper, instead of inlining it into both branches
            # (which would duplicate its size on every branch point, compounding
            # exponentially across sequential/nested `if`s).
            cont_vars = collect_accumulators(list(first.body) + list(first.orelse), known)
            cont_name = namer.next_cont()
            params = " ".join(cont_vars)
            header = f"{cont_name} {params}".rstrip()
            cont_lines = [f"{pad}let {header} = do" if monadic else f"{pad}let {header} ="]
            cont_lines.extend(translate_sequence(rest, indent + 3, monadic, make_tail, namer, known | set(cont_vars)))

            def branch_tail(i, extra_known=frozenset()):
                return [f"{'  ' * i}{header}"]

        lines = [f"{pad}if {render_expr(first.test)}", f"{pad}  then do" if monadic else f"{pad}  then"]
        lines.extend(translate_sequence(list(first.body), indent + 2, monadic, branch_tail, namer, known))
        lines.append(f"{pad}  else do" if monadic else f"{pad}  else")
        lines.extend(translate_sequence(list(first.orelse), indent + 2, monadic, branch_tail, namer, known))
        return cont_lines + lines

    if isinstance(first, IRFor):
        def rest_tail(i, extra_known=frozenset()):
            return translate_sequence(rest, i, monadic, make_tail, namer, known | extra_known)

        return _translate_for(first, indent, monadic, rest_tail, namer, known)

    if isinstance(first, IRAssign) and isinstance(first.target, IRName):
        known = known | {first.target.id}

    return _render_leaf(first, indent, monadic) + translate_sequence(rest, indent, monadic, make_tail, namer, known)


def _translate_for(node: IRFor, indent: int, monadic: bool, make_tail, namer: LoopNamer, known=frozenset()) -> list:
    pad = "  " * indent
    body = rewrite_appends(list(node.body))
    accumulators = collect_accumulators(body, known)
    loop_is_monadic = monadic and body_has_ledger_effect(body)
    helper = namer.next()
    rest_name = "_damlforge_rest"
    acc_params = " ".join(accumulators)
    header_params = f"{acc_params} " if acc_params else ""
    case_head = f"{pad}    {helper} {header_params}({node.target} : {rest_name})"
    case_arrow = " = do" if loop_is_monadic else " ="
    inner_known = known | {node.target} | set(accumulators)

    if accumulators:
        # loop-carried state is mutated: the helper returns the final accumulator
        # values, and code after the loop is a *separate* continuation once we
        # have them back - so its base case is just "return what we're holding",
        # never the outer continuation itself.
        acc_tuple = ", ".join(accumulators) if len(accumulators) > 1 else accumulators[0]
        bind_target = f"({acc_tuple})" if len(accumulators) > 1 else acc_tuple
        base_rhs = f"pure {bind_target}" if loop_is_monadic else bind_target

        def recursive_tail(i, extra_known=frozenset()):
            call = f"{helper} {acc_params} {rest_name}".strip()
            return [f"{'  ' * i}{call}"]

        lines = [f"{pad}let {helper} {header_params}[] = {base_rhs}", case_head + case_arrow]
        lines.extend(translate_sequence(body, indent + 3, loop_is_monadic, recursive_tail, namer, inner_known))

        call_expr = f"{helper} {acc_params} {render_expr(node.iter)}".strip()
        if loop_is_monadic:
            lines.append(f"{pad}{bind_target} <- {call_expr}")
        else:
            suffix = "" if monadic else " in"
            lines.append(f"{pad}let {bind_target} = {call_expr}{suffix}")
        lines.extend(make_tail(indent, set(accumulators)))
        return lines

    # no loop-carried state: this loop's only purpose is control flow (an early
    # `return` search, or pure side effects) - so "what happens after the loop"
    # becomes the helper's own base case directly, and invoking the helper *is*
    # the terminal action for this branch of the sequence.
    # the base case's body must sit deeper than the column `helper` starts at
    # (pad + len("let ")) or Daml/Haskell's layout rule would read it as closing
    # this `let` block early instead of continuing the first equation's RHS -
    # indent + 3 matches the recursive-case body below and is always safely past it.
    lines = [f"{pad}let {helper} [] = do" if loop_is_monadic else f"{pad}let {helper} [] ="]
    lines.extend(make_tail(indent + 3))
    lines.append(case_head + case_arrow)

    def recursive_tail_no_acc(i, extra_known=frozenset()):
        return [f"{'  ' * i}{helper} {rest_name}"]

    lines.extend(translate_sequence(body, indent + 3, loop_is_monadic, recursive_tail_no_acc, namer, inner_known))
    lines.append(f"{pad}{helper} {render_expr(node.iter)}")
    return lines


def _final_tail(i: int, monadic: bool, extra_known=frozenset()) -> list:
    pad = "  " * i
    return [f"{pad}pure ()"] if monadic else [f"{pad}()"]


def render_body(stmts, indent: int, monadic: bool = True, known=frozenset()) -> list:
    namer = LoopNamer()
    rewritten = rewrite_appends(list(stmts))
    tail = lambda i, extra_known=frozenset(): _final_tail(i, monadic)
    return translate_sequence(rewritten, indent, monadic, tail, namer, known)


def render_stmt(stmt, indent: int, monadic: bool = True) -> list:
    """Single-statement convenience wrapper over `translate_sequence`, used by
    unit tests that exercise one IR statement kind at a time."""
    return render_body([stmt], indent, monadic)


class Emitter:
    def __init__(self):
        self.lines: list = []
        self.mappings: list = []

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


def emit_struct(em: Emitter, s: IRStruct) -> None:
    start = len(em.lines) + 1
    em.line(f"data {s.name} = {s.name}")
    if s.fields:
        em.line("  with")
        for f in s.fields:
            em.line(f"    {f.name} : {render_type(f.type)}")
    em.line("  deriving (Eq, Show)")
    em.record(s.src, "struct", s.name, start)


def emit_flag(em: Emitter, f: IRFlag) -> None:
    start = len(em.lines) + 1
    if not f.values:
        em.line(f"data {f.name}")
    else:
        em.line(f"data {f.name} = " + " | ".join(f.values))
        em.line("  deriving (Eq, Show)")
    em.record(f.src, "flag", f.name, start)


def emit_choice(em: Emitter, c: IRChoice, container_name: str, indent: int, field_types=None) -> None:
    pad = "  " * indent
    start = len(em.lines) + 1
    is_template_choice = field_types is not None
    known = frozenset(a.name for a in c.args)

    body = c.body
    display_return_type = c.return_type
    if is_template_choice:
        body = rewrite_self_stmts(list(body), field_types)
        known = known | {SELF}
        if body_mutates_self(body):
            body = inject_self_create(body)
            original = c.return_type if c.return_type is not None else TypeRef("tuple", ())
            display_return_type = TypeRef("tuple", (TypeRef("ContractId", (TypeRef(container_name),)), original))

    consuming_kw = _CONSUMING_KEYWORD.get(c.consuming, "")
    return_type = render_type(display_return_type) if display_return_type is not None else "()"
    em.line(f"{pad}{consuming_kw}choice {c.name} : {return_type}")
    if c.args:
        em.line(f"{pad}  with")
        for a in c.args:
            arg_type = render_type(a.type) if a.type is not None else "()"
            em.line(f"{pad}    {a.name} : {arg_type}")
    controller_expr = render_expr(c.controller) if c.controller is not None else "-- MISSING controller"
    em.line(f"{pad}  controller {controller_expr}")
    if c.observer is not None:
        em.line(f"{pad}  observer {render_expr(c.observer)}")
    em.line(f"{pad}  do")
    body_lines = [f"{pad}    let {SELF} = this"] if is_template_choice else []
    body_lines.extend(render_body(body, indent + 2, known=known))
    em.lines_block(body_lines)
    em.record(c.src, "choice", f"{container_name}.{c.name}", start)


def emit_function(em: Emitter, fn: IRFunction) -> None:
    start = len(em.lines) + 1
    is_monadic = "ledger_effect" in fn.decorators
    return_type = render_type(fn.return_type, as_arg=True) if fn.return_type is not None else "()"
    full_return = f"Update {return_type}" if is_monadic else return_type
    arg_types = [render_type(a.type, as_arg=True) if a.type is not None else "()" for a in fn.args]
    em.line(f"{fn.name} : {' -> '.join(arg_types + [full_return])}")
    header = f"{fn.name} {' '.join(a.name for a in fn.args)}".rstrip()
    em.line(f"{header} = do" if is_monadic else f"{header} =")
    em.lines_block(render_body(fn.body, 1, monadic=is_monadic, known=frozenset(a.name for a in fn.args)))
    em.record(fn.src, "function", fn.name, start)


def emit_template(em: Emitter, t: IRTemplate) -> None:
    start = len(em.lines) + 1
    em.line(f"template {t.name}")
    if t.fields:
        em.line("  with")
        for f in t.fields:
            em.line(f"    {f.name} : {render_type(f.type)}")
    em.line("  where")
    signatory_expr = render_expr(t.signatory) if t.signatory is not None else "-- MISSING signatory"
    em.line(f"    signatory {signatory_expr}")
    if t.observer is not None:
        em.line(f"    observer {render_expr(t.observer)}")

    ensure_conditions = []
    if t.init:
        for b in t.init.body:
            if (
                isinstance(b, IRExprStmt)
                and isinstance(b.value, IRCall)
                and isinstance(b.value.func, IRName)
                and b.value.func.id == "ensure"
                and b.value.args
            ):
                ensure_conditions.append(render_expr(b.value.args[0]))
    if ensure_conditions:
        em.line("    ensure " + " && ".join(ensure_conditions))

    field_types = {f.name: f.type for f in t.fields}
    for c in t.choices:
        em.line("")
        emit_choice(em, c, t.name, indent=2, field_types=field_types)
    em.record(t.src, "template", t.name, start)


def emit_interface(em: Emitter, i: IRInterface) -> None:
    start = len(em.lines) + 1
    requires_clause = f" requires {', '.join(i.requires)}" if i.requires else ""
    em.line(f"interface {i.name}{requires_clause} where")
    view_type = render_type(i.view) if i.view is not None else "()"
    em.line(f"  viewtype {view_type}")
    for c in i.choices:
        em.line("")
        emit_choice(em, c, i.name, indent=1)
    em.record(i.src, "interface", i.name, start)


def generate_daml(module: IRModule):
    em = Emitter()

    for s in module.structs:
        emit_struct(em, s)
        em.line("")

    for f in module.flags:
        emit_flag(em, f)
        em.line("")

    for fn in module.functions:
        emit_function(em, fn)
        em.line("")

    for i in module.interfaces:
        emit_interface(em, i)
        em.line("")

    for t in module.templates:
        emit_template(em, t)
        em.line("")

    body_source = "\n".join(em.lines).rstrip("\n") + "\n"
    mappings = em.mappings
    # a small, deliberate exception to "no import emission yet" (see codegen
    # design doc): `Map.lookup`/`Map.member`/`Map.insert` (from dict-typed
    # `self.field` operations) need `DA.Map` in scope to resolve at all.
    header = ""
    if "Map." in body_source:
        header = "import DA.Map as Map\n\n"
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
    source_map = {"mappings": mappings}
    return source, source_map
