from forge.exceptions import CompilerPanic
from forge.ir.nodes import (
    IRAssert,
    IRAssign,
    IRAttribute,
    IRBinOp,
    IRCall,
    IRExprStmt,
    IRFor,
    IRIf,
    IRList,
    IRName,
    IRPass,
    IRReturn,
)

LEDGER_EFFECT_BUILTINS = {"create", "fetch", "exercise", "archive", "lookup"}


def _is_append_call(stmt) -> bool:
    return (
        isinstance(stmt, IRExprStmt)
        and isinstance(stmt.value, IRCall)
        and isinstance(stmt.value.func, IRAttribute)
        and stmt.value.func.attr == "append"
        and isinstance(stmt.value.func.value, IRName)
        and len(stmt.value.args) == 1
        and not stmt.value.keywords
    )


def rewrite_appends(stmts):
    """`n.append(item)` is a mutation with no direct IR meaning outside imperative
    code; rewrite it to the equivalent reassignment `n = n <> [item]` so the rest of
    the pipeline only ever has to deal with ordinary Assign statements."""
    rewritten = []
    for s in stmts:
        if isinstance(s, IRIf):
            rewritten.append(
                IRIf(s.test, tuple(rewrite_appends(s.body)), tuple(rewrite_appends(s.orelse)), src=s.src)
            )
        elif isinstance(s, IRFor):
            rewritten.append(IRFor(s.target, s.target_type, s.iter, tuple(rewrite_appends(s.body)), src=s.src))
        elif _is_append_call(s):
            target_name = s.value.func.value.id
            item = s.value.args[0]
            rewritten.append(
                IRAssign(IRName(target_name), IRBinOp("<>", IRName(target_name), IRList((item,))), src=s.src)
            )
        else:
            rewritten.append(s)
    return rewritten


def collect_accumulators(stmts, known, acc=None):
    """Names reassigned via a plain `Assign` (not `AnnAssign`) anywhere in this
    sequence - recursively through if/else branches and nested `for` bodies -
    that were ALREADY bound in `known` before this sequence started: these are
    genuine loop-carried state, mutated across iterations. `AnnAssign` is never
    an accumulator - it's how this codebase always spells "new local declared
    here", matching real Python scoping (`x: T = ...` reads as a fresh
    declaration). A plain `Assign` to a name NOT in `known` is also not an
    accumulator despite the bare `=` spelling: it's the name's first binding in
    this scope (e.g. `found = False` reset at the top of every iteration), not
    a mutation of something carried in from outside - threading it as a
    recursion parameter would reference a variable that was never bound."""
    if acc is None:
        acc = []
    for s in stmts:
        if isinstance(s, IRAssign) and s.type is None and isinstance(s.target, IRName):
            if s.target.id in known and s.target.id not in acc:
                acc.append(s.target.id)
        elif isinstance(s, IRIf):
            collect_accumulators(s.body, known, acc)
            collect_accumulators(s.orelse, known, acc)
        elif isinstance(s, IRFor):
            collect_accumulators(s.body, known, acc)
    return acc


def _is_effect_call(expr) -> bool:
    return isinstance(expr, IRCall) and isinstance(expr.func, IRName) and expr.func.id in LEDGER_EFFECT_BUILTINS


def body_has_ledger_effect(stmts) -> bool:
    for s in stmts:
        if isinstance(s, IRExprStmt) and _is_effect_call(s.value):
            return True
        if isinstance(s, IRAssign) and _is_effect_call(s.value):
            return True
        if isinstance(s, IRReturn) and s.value is not None and _is_effect_call(s.value):
            return True
        if isinstance(s, IRIf) and (body_has_ledger_effect(s.body) or body_has_ledger_effect(s.orelse)):
            return True
        if isinstance(s, IRFor) and body_has_ledger_effect(s.body):
            return True
    return False


class LoopNamer:
    def __init__(self):
        self._loop_n = 0
        self._cont_n = 0

    def next(self) -> str:
        self._loop_n += 1
        return f"_damlforge_loop{self._loop_n}"

    def next_cont(self) -> str:
        self._cont_n += 1
        return f"_damlforge_cont{self._cont_n}"
