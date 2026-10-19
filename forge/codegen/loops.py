from dataclasses import dataclass, fields, is_dataclass, replace

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
    IRIfExp,
    IRList,
    IRName,
    IRPass,
    IRRecordUpdate,
    IRReturn,
    IRStmt,
    IRSubscript,
    IRTuple,
    IRUnaryOp,
)


@dataclass(frozen=True)
class LoopPlan:
    body: tuple[IRStmt, ...]
    accumulators: tuple[str, ...]
    captured: tuple[str, ...]
    assertion: IRAssert | None
    has_return: bool
    in_update_block: bool


class LoopAnalysis:
    @classmethod
    def rewrite_appends(cls, stmts, namer=None, known_effect_fns: frozenset = frozenset()):
        rewritten: list[IRStmt] = []
        for s in stmts:
            if isinstance(s, IRIf):
                rewritten.append(
                    IRIf(
                        s.test,
                        tuple(cls.rewrite_appends(s.body, namer, known_effect_fns)),
                        tuple(cls.rewrite_appends(s.orelse, namer, known_effect_fns)),
                        src=s.src,
                    )
                )
            elif isinstance(s, IRFor):
                rewritten.append(
                    IRFor(
                        s.target,
                        s.target_type,
                        s.iter,
                        tuple(cls.rewrite_appends(s.body, namer, known_effect_fns)),
                        src=s.src,
                    )
                )
            elif cls._is_append_call(s):
                target_name = s.value.func.value.id
                target_type = s.value.func.value.type
                item = s.value.args[0]
                if namer is not None and cls.is_effect_call(item, known_effect_fns):
                    temp = namer.next_rebind(f"{target_name}_item")
                    item_type = item.type if isinstance(item, IRName) else None
                    rewritten.append(IRAssign(IRName(temp, item_type), item, src=s.src))
                    item = IRName(temp, item_type)
                rewritten.append(
                    IRAssign(
                        IRName(target_name, target_type),
                        IRBinOp("<>", IRName(target_name, target_type), IRList((item,))),
                        src=s.src,
                    )
                )
            else:
                rewritten.append(s)
        return rewritten

    @staticmethod
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

    @classmethod
    def collect_accumulators(cls, stmts, known, acc=None):
        if acc is None:
            acc = []
        for s in stmts:
            if isinstance(s, IRAssign) and s.type is None and isinstance(s.target, IRName):
                if s.target.id in known and s.target.id not in acc:
                    acc.append(s.target.id)
            elif isinstance(s, IRIf):
                cls.collect_accumulators(s.body, known, acc)
                cls.collect_accumulators(s.orelse, known, acc)
            elif isinstance(s, IRFor):
                cls.collect_accumulators(s.body, known, acc)
        return acc

    @classmethod
    def collect_assigned_names(cls, stmts, acc=None) -> set:
        if acc is None:
            acc = set()
        for s in stmts:
            if isinstance(s, IRAssign) and isinstance(s.target, IRName):
                acc.add(s.target.id)
            elif isinstance(s, IRIf):
                cls.collect_assigned_names(s.body, acc)
                cls.collect_assigned_names(s.orelse, acc)
            elif isinstance(s, IRFor):
                cls.collect_assigned_names(s.body, acc)
        return acc

    @classmethod
    def hoist_nested_effects(cls, stmts, namer, known_effect_fns: frozenset) -> list[IRStmt]:
        result: list[IRStmt] = []
        for s in stmts:
            if isinstance(s, IRIf):
                s = replace(
                    s,
                    body=tuple(cls.hoist_nested_effects(s.body, namer, known_effect_fns)),
                    orelse=tuple(cls.hoist_nested_effects(s.orelse, namer, known_effect_fns)),
                )
            elif isinstance(s, IRFor):
                s = replace(
                    s, body=tuple(cls.hoist_nested_effects(s.body, namer, known_effect_fns))
                )
            elif isinstance(s, (IRReturn, IRAssign, IRExprStmt)) and s.value is not None:
                lifted: list[tuple[str, IRCall]] = []
                value = cls._lift_effects(s.value, lifted, namer, known_effect_fns, top=True)
                result.extend(IRAssign(IRName(name), call, src=s.src) for name, call in lifted)
                s = replace(s, value=value)
            result.append(s)
        return result

    @classmethod
    def _lift_effects(cls, expr, lifted, namer, known_effect_fns, top=False):
        if isinstance(expr, IRIfExp):
            return replace(expr, test=cls._lift_effects(expr.test, lifted, namer, known_effect_fns))
        if isinstance(expr, IRBoolOp):
            first = cls._lift_effects(expr.values[0], lifted, namer, known_effect_fns)
            return replace(expr, values=(first, *expr.values[1:]))
        if isinstance(expr, (IRName, IRConstant)) or not is_dataclass(expr):
            return expr
        rebuilt = replace(
            expr,
            **{
                f.name: cls._lift_field(getattr(expr, f.name), lifted, namer, known_effect_fns)
                for f in fields(expr)
            },
        )
        if not top and cls.is_effect_call(rebuilt, known_effect_fns):
            name = namer.next_rebind("effect")
            lifted.append((name, rebuilt))
            return IRName(name)
        return rebuilt

    @classmethod
    def _lift_field(cls, value, lifted, namer, known_effect_fns):
        if isinstance(value, tuple):
            return tuple(cls._lift_field(item, lifted, namer, known_effect_fns) for item in value)
        return cls._lift_effects(value, lifted, namer, known_effect_fns)

    @classmethod
    def is_effect_call(cls, expr, known_effect_fns: frozenset = frozenset()) -> bool:
        return (
            isinstance(expr, IRCall)
            and isinstance(expr.func, IRName)
            and expr.func.id in known_effect_fns
        )

    @classmethod
    def body_has_ledger_effect(cls, stmts, known_effect_fns: frozenset = frozenset()) -> bool:
        for s in stmts:
            if isinstance(s, IRAssert):
                return True
            if isinstance(s, IRExprStmt) and cls.is_effect_call(s.value, known_effect_fns):
                return True
            if isinstance(s, IRAssign) and cls.is_effect_call(s.value, known_effect_fns):
                return True
            if (
                isinstance(s, IRReturn)
                and s.value is not None
                and cls.is_effect_call(s.value, known_effect_fns)
            ):
                return True
            if isinstance(s, IRIf) and (
                cls.body_has_ledger_effect(s.body, known_effect_fns)
                or cls.body_has_ledger_effect(s.orelse, known_effect_fns)
            ):
                return True
            if isinstance(s, IRFor) and cls.body_has_ledger_effect(s.body, known_effect_fns):
                return True
        return False

    @classmethod
    def _expr_free_names(cls, e, acc: set) -> None:
        if isinstance(e, IRName):
            acc.add(e.id)
        elif isinstance(e, IRAttribute):
            cls._expr_free_names(e.value, acc)
        elif isinstance(e, IRSubscript):
            cls._expr_free_names(e.value, acc)
            cls._expr_free_names(e.index, acc)
        elif isinstance(e, IRCall):
            cls._expr_free_names(e.func, acc)
            for a in e.args:
                cls._expr_free_names(a, acc)
            for _, v in e.keywords:
                cls._expr_free_names(v, acc)
        elif isinstance(e, IRConstant):
            pass
        elif isinstance(e, (IRList, IRTuple)):
            for el in e.elements:
                cls._expr_free_names(el, acc)
        elif isinstance(e, IRDict):
            for k in e.keys:
                cls._expr_free_names(k, acc)
            for v in e.values:
                cls._expr_free_names(v, acc)
        elif isinstance(e, IRBinOp):
            cls._expr_free_names(e.left, acc)
            cls._expr_free_names(e.right, acc)
        elif isinstance(e, IRBoolOp):
            for v in e.values:
                cls._expr_free_names(v, acc)
        elif isinstance(e, IRUnaryOp):
            cls._expr_free_names(e.operand, acc)
        elif isinstance(e, IRCompare):
            cls._expr_free_names(e.left, acc)
            cls._expr_free_names(e.right, acc)
        elif isinstance(e, IRRecordUpdate):
            cls._expr_free_names(e.base, acc)
            for _, v in e.updates:
                cls._expr_free_names(v, acc)
        elif isinstance(e, IRIfExp):
            cls._expr_free_names(e.test, acc)
            cls._expr_free_names(e.body, acc)
            cls._expr_free_names(e.orelse, acc)
        else:
            raise CompilerPanic(f"_expr_free_names: unsupported IR expression {type(e).__name__}")

    @classmethod
    def collect_free_names(cls, stmts, acc=None, bound=frozenset()) -> set:
        if acc is None:
            acc = set()
        for s in stmts:
            names: set = set()
            if isinstance(s, IRAssert):
                cls._expr_free_names(s.test, names)
                if s.msg is not None:
                    cls._expr_free_names(s.msg, names)
            elif isinstance(s, IRAssign):
                cls._expr_free_names(s.value, names)
                if not isinstance(s.target, IRName):
                    cls._expr_free_names(s.target, names)
            elif isinstance(s, IRIf):
                cls._expr_free_names(s.test, names)
                cls.collect_free_names(s.body, acc, bound)
                cls.collect_free_names(s.orelse, acc, bound)
            elif isinstance(s, IRFor):
                cls._expr_free_names(s.iter, names)
                cls.collect_free_names(s.body, acc, bound)
            elif isinstance(s, IRReturn):
                if s.value is not None:
                    cls._expr_free_names(s.value, names)
            elif isinstance(s, IRExprStmt):
                cls._expr_free_names(s.value, names)
            elif not isinstance(s, IRPass):
                raise CompilerPanic(
                    f"collect_free_names: unsupported IR statement {type(s).__name__}"
                )
            acc |= names - bound
            if isinstance(s, IRAssign) and isinstance(s.target, IRName):
                bound = bound | {s.target.id}
        return acc

    @classmethod
    def body_has_return(cls, stmts) -> bool:
        for s in stmts:
            if isinstance(s, IRReturn):
                return True
            if isinstance(s, IRIf) and (
                cls.body_has_return(s.body) or cls.body_has_return(s.orelse)
            ):
                return True
        return False

    @classmethod
    def apply_renames(cls, e, renames: dict):
        if not renames:
            return e
        if isinstance(e, IRName):
            return IRName(renames.get(e.id, e.id), e.type)
        if isinstance(e, IRAttribute):
            return IRAttribute(cls.apply_renames(e.value, renames), e.attr)
        if isinstance(e, IRSubscript):
            return IRSubscript(
                cls.apply_renames(e.value, renames),
                cls.apply_renames(e.index, renames),
                is_list=e.is_list,
            )
        if isinstance(e, IRCall):
            return IRCall(
                cls.apply_renames(e.func, renames),
                tuple(cls.apply_renames(a, renames) for a in e.args),
                tuple((k, cls.apply_renames(v, renames)) for k, v in e.keywords),
            )
        if isinstance(e, IRConstant):
            return e
        if isinstance(e, IRList):
            return IRList(tuple(cls.apply_renames(el, renames) for el in e.elements))
        if isinstance(e, IRTuple):
            return IRTuple(tuple(cls.apply_renames(el, renames) for el in e.elements))
        if isinstance(e, IRDict):
            return IRDict(
                tuple(cls.apply_renames(k, renames) for k in e.keys),
                tuple(cls.apply_renames(v, renames) for v in e.values),
            )
        if isinstance(e, IRBinOp):
            return IRBinOp(
                e.op, cls.apply_renames(e.left, renames), cls.apply_renames(e.right, renames)
            )
        if isinstance(e, IRBoolOp):
            return IRBoolOp(e.op, tuple(cls.apply_renames(v, renames) for v in e.values))
        if isinstance(e, IRUnaryOp):
            return IRUnaryOp(e.op, cls.apply_renames(e.operand, renames))
        if isinstance(e, IRCompare):
            return IRCompare(
                cls.apply_renames(e.left, renames), e.op, cls.apply_renames(e.right, renames)
            )
        if isinstance(e, IRRecordUpdate):
            return IRRecordUpdate(
                cls.apply_renames(e.base, renames),
                tuple((n, cls.apply_renames(v, renames)) for n, v in e.updates),
            )
        if isinstance(e, IRIfExp):
            return IRIfExp(
                cls.apply_renames(e.test, renames),
                cls.apply_renames(e.body, renames),
                cls.apply_renames(e.orelse, renames),
            )
        raise CompilerPanic(f"apply_renames: unsupported IR expression {type(e).__name__}")


class LoopAnalyzer:
    def __init__(self, namer, known_effect_fns: frozenset = frozenset()):
        self.namer = namer
        self.known_effect_fns = known_effect_fns

    def normalize(self, stmts) -> list[IRStmt]:
        rewritten = LoopAnalysis.rewrite_appends(stmts, self.namer, self.known_effect_fns)
        return LoopAnalysis.hoist_nested_effects(rewritten, self.namer, self.known_effect_fns)

    def plan(self, node: IRFor, known: frozenset, in_update_block: bool) -> LoopPlan:
        body = tuple(node.body)
        accumulators = tuple(LoopAnalysis.collect_accumulators(body, known))
        assertion = body[0] if self._is_assertion_only_loop(body) else None
        captured = tuple(
            sorted(
                (LoopAnalysis.collect_free_names(body) & known) - set(accumulators) - {node.target}
            )
        )
        return LoopPlan(
            body=body,
            accumulators=accumulators,
            captured=captured,
            assertion=assertion,
            has_return=LoopAnalysis.body_has_return(body),
            in_update_block=assertion is None
            and in_update_block
            and LoopAnalysis.body_has_ledger_effect(body, self.known_effect_fns),
        )

    @staticmethod
    def _is_assertion_only_loop(body: tuple[IRStmt, ...]) -> bool:
        return (
            len(body) == 1
            and isinstance(body[0], IRAssert)
            and (body[0].msg is None or isinstance(body[0].msg, IRConstant))
        )


class LoopNamer:
    def __init__(self):
        self._loop_n = 0
        self._cont_n = 0
        self._rebind_n = 0

    def next(self) -> str:
        self._loop_n += 1
        return f"_damlforge_loop{self._loop_n}"

    def next_cont(self) -> str:
        self._cont_n += 1
        return f"_damlforge_cont{self._cont_n}"

    def next_rebind(self, base: str) -> str:
        self._rebind_n += 1
        return f"_damlforge_{base}{self._rebind_n}"
