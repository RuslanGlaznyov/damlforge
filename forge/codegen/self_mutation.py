from forge.exceptions import CompilerPanic
from forge.ir.nodes import (
    IRAssert,
    IRAssign,
    IRAttribute,
    IRBinOp,
    IRBoolOp,
    IRCall,
    IRCompare,
    IRConstant,
    IRDict,
    IRExprStmt,
    IRFor,
    IRIf,
    IRList,
    IRName,
    IRPass,
    IRRecordUpdate,
    IRReturn,
    IRSubscript,
    IRTuple,
    IRUnaryOp,
)

SELF = "self"
_DICT_TYPE_NAMES = ("GenMap", "TextMap")


def _self_field(e, field_types):
    """If `e` is `self.field` for a field this template actually declares,
    return (field_name, field_type); otherwise None."""
    if isinstance(e, IRAttribute) and isinstance(e.value, IRName) and e.value.id == SELF:
        if e.attr in field_types:
            return e.attr, field_types[e.attr]
    return None


def _is_dict_type(t) -> bool:
    return t is not None and t.name in _DICT_TYPE_NAMES


def rewrite_self_expr(e, field_types):
    """Recursively rewrite an expression so dict-typed `self.field` reads and
    membership tests use real Daml map operations instead of the list
    operators (`!!`, `elem`) that are only correct for `self.field` being a
    plain `list`. Everything else is rebuilt unchanged, recursing into
    children so a rewrite anywhere inside a larger expression is found."""
    if isinstance(e, (IRName, IRConstant)):
        return e
    if isinstance(e, IRSubscript):
        field = _self_field(e.value, field_types)
        if field is not None and _is_dict_type(field[1]):
            lookup = IRCall(IRName("Map.lookup"), (rewrite_self_expr(e.index, field_types), e.value))
            return IRCall(IRName("fromSome"), (lookup,))
        return IRSubscript(rewrite_self_expr(e.value, field_types), rewrite_self_expr(e.index, field_types))
    if isinstance(e, IRAttribute):
        return IRAttribute(rewrite_self_expr(e.value, field_types), e.attr)
    if isinstance(e, IRCall):
        return IRCall(
            rewrite_self_expr(e.func, field_types),
            tuple(rewrite_self_expr(a, field_types) for a in e.args),
            tuple((k, rewrite_self_expr(v, field_types)) for k, v in e.keywords),
        )
    if isinstance(e, IRList):
        return IRList(tuple(rewrite_self_expr(el, field_types) for el in e.elements))
    if isinstance(e, IRTuple):
        return IRTuple(tuple(rewrite_self_expr(el, field_types) for el in e.elements))
    if isinstance(e, IRDict):
        return IRDict(
            tuple(rewrite_self_expr(k, field_types) for k in e.keys),
            tuple(rewrite_self_expr(v, field_types) for v in e.values),
        )
    if isinstance(e, IRBinOp):
        return IRBinOp(e.op, rewrite_self_expr(e.left, field_types), rewrite_self_expr(e.right, field_types))
    if isinstance(e, IRBoolOp):
        return IRBoolOp(e.op, tuple(rewrite_self_expr(v, field_types) for v in e.values))
    if isinstance(e, IRUnaryOp):
        return IRUnaryOp(e.op, rewrite_self_expr(e.operand, field_types))
    if isinstance(e, IRCompare):
        if e.op in ("in", "not in"):
            field = _self_field(e.right, field_types)
            if field is not None and _is_dict_type(field[1]):
                member = IRCall(IRName("Map.member"), (rewrite_self_expr(e.left, field_types), e.right))
                return IRUnaryOp("not", member) if e.op == "not in" else member
        return IRCompare(rewrite_self_expr(e.left, field_types), e.op, rewrite_self_expr(e.right, field_types))
    if isinstance(e, IRRecordUpdate):
        return IRRecordUpdate(
            rewrite_self_expr(e.base, field_types),
            tuple((name, rewrite_self_expr(v, field_types)) for name, v in e.updates),
        )
    raise CompilerPanic(f"rewrite_self_expr: unsupported IR expression {type(e).__name__}")


def _self_update(field, new_value):
    return IRAssign(IRName(SELF), IRRecordUpdate(IRName(SELF), ((field, new_value),)))


def rewrite_self_stmt(s, field_types):
    """Recursively rewrite a statement so `self.field = value` and
    `self.field[key] = value` (Daml has no in-place mutation) become a
    reassignment of a whole new `self` record built via a record update -
    `self = self { field = value }` - which is then just an ordinary
    already-bound-name reassignment to the rest of the pipeline (loops/ifs
    already thread that correctly via the existing accumulator machinery)."""
    if isinstance(s, IRAssert):
        msg = rewrite_self_expr(s.msg, field_types) if s.msg is not None else None
        return IRAssert(rewrite_self_expr(s.test, field_types), msg, src=s.src)
    if isinstance(s, IRAssign):
        field = _self_field(s.target, field_types)
        if field is not None:
            return _self_update(field[0], rewrite_self_expr(s.value, field_types))
        if isinstance(s.target, IRSubscript):
            field = _self_field(s.target.value, field_types)
            if field is not None:
                name, field_type = field
                if not _is_dict_type(field_type):
                    raise CompilerPanic(
                        f"rewrite_self_stmt: subscript assignment to `self.{name}` is only "
                        "supported for GenMap/TextMap fields, not a value of type "
                        f"'{field_type.name if field_type is not None else 'unknown'}'"
                    )
                key = rewrite_self_expr(s.target.index, field_types)
                value = rewrite_self_expr(s.value, field_types)
                current = IRAttribute(IRName(SELF), name)
                return _self_update(name, IRCall(IRName("Map.insert"), (key, value, current)))
        return IRAssign(s.target, rewrite_self_expr(s.value, field_types), type=s.type, src=s.src)
    if isinstance(s, IRIf):
        return IRIf(
            rewrite_self_expr(s.test, field_types),
            tuple(rewrite_self_stmt(st, field_types) for st in s.body),
            tuple(rewrite_self_stmt(st, field_types) for st in s.orelse),
            src=s.src,
        )
    if isinstance(s, IRFor):
        return IRFor(
            s.target,
            s.target_type,
            rewrite_self_expr(s.iter, field_types),
            tuple(rewrite_self_stmt(st, field_types) for st in s.body),
            src=s.src,
        )
    if isinstance(s, IRReturn):
        value = rewrite_self_expr(s.value, field_types) if s.value is not None else None
        return IRReturn(value, src=s.src)
    if isinstance(s, IRPass):
        return s
    if isinstance(s, IRExprStmt):
        return IRExprStmt(rewrite_self_expr(s.value, field_types), src=s.src)
    raise CompilerPanic(f"rewrite_self_stmt: unsupported IR statement {type(s).__name__}")


def rewrite_self_stmts(stmts, field_types):
    return [rewrite_self_stmt(s, field_types) for s in stmts]


def body_mutates_self(stmts) -> bool:
    """True if `self` is ever reassigned anywhere in this (already-rewritten)
    statement sequence, at any nesting depth."""
    for s in stmts:
        if isinstance(s, IRAssign) and isinstance(s.target, IRName) and s.target.id == SELF:
            return True
        if isinstance(s, IRIf) and (body_mutates_self(s.body) or body_mutates_self(s.orelse)):
            return True
        if isinstance(s, IRFor) and body_mutates_self(s.body):
            return True
    return False


_NEW_SELF_CID = "_damlforge_new_self"


def _create_self_pair(value):
    return [
        IRAssign(IRName(_NEW_SELF_CID), IRCall(IRName("create"), (IRName(SELF),))),
        IRReturn(IRTuple((IRName(_NEW_SELF_CID), value))),
    ]


def _always_terminates(stmts) -> bool:
    """Best-effort check for "every path through this sequence ends in an
    explicit `return`" - just enough to avoid appending an unreachable,
    dead-code copy of the create-self-and-return pair after a body that
    already ends in one. Not exhaustive (doesn't need to be: an under-
    detected case just means a harmless extra dead `let` binding, not wrong
    output - Daml/GHC accepts unused do-block bindings)."""
    if not stmts:
        return False
    last = stmts[-1]
    if isinstance(last, IRReturn):
        return True
    if isinstance(last, IRIf):
        return bool(last.orelse) and _always_terminates(list(last.body)) and _always_terminates(list(last.orelse))
    return False


def _replace_returns(stmts):
    """Replace every explicit `return X` - at any nesting depth, including
    inside `for`/`if` - with `create self` bound followed by `return (newCid,
    X)`. Does NOT touch "falls off the end without an explicit `return`" -
    that only means "the function is over" at the outermost level; falling
    off the end of a `for` loop's body just means "go to the next iteration",
    and injecting a `return` there would make the loop stop after one."""
    result = []
    for s in stmts:
        if isinstance(s, IRReturn):
            value = s.value if s.value is not None else IRTuple(())
            result.extend(_create_self_pair(value))
        elif isinstance(s, IRIf):
            result.append(IRIf(s.test, tuple(_replace_returns(list(s.body))), tuple(_replace_returns(list(s.orelse))), src=s.src))
        elif isinstance(s, IRFor):
            result.append(IRFor(s.target, s.target_type, s.iter, tuple(_replace_returns(list(s.body))), src=s.src))
        else:
            result.append(s)
    return result


def inject_self_create(stmts):
    """Once `self` has been mutated, a choice must actually `create` the new
    contract state for the change to exist on the ledger at all - real Daml
    has no in-place update. Rewrites every explicit `return` (see
    `_replace_returns`) and, only at this outermost level, appends the same
    create-and-return pair after the sequence's natural end if it can fall off
    the end without ever hitting one."""
    result = _replace_returns(stmts)
    if not _always_terminates(stmts):
        result = result + _create_self_pair(IRTuple(()))
    return result
