from forge.builtins.maps import known_map_types
from forge.codegen.maps import map_method_call
from forge.codegen.optional import is_optional_type, optional_method_call
from forge.codegen.sets import is_set_type, known_set_methods, set_method_call
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
    IRSubscript,
    IRTuple,
    IRUnaryOp,
)

SELF = "self"


class SelfFieldRewriter:
    DICT_TYPE_NAMES = tuple(known_map_types())

    @classmethod
    def rewrite_stmts(cls, stmts, field_types):
        local_types = cls._collect_local_types(stmts)
        return [cls.rewrite_stmt(s, field_types, local_types) for s in stmts]

    @classmethod
    def _collect_local_types(cls, stmts) -> dict:
        types: dict = {}
        for s in stmts:
            if isinstance(s, IRAssign) and isinstance(s.target, IRName) and s.type is not None:
                types[s.target.id] = s.type
            elif isinstance(s, IRIf):
                types.update(cls._collect_local_types(s.body))
                types.update(cls._collect_local_types(s.orelse))
            elif isinstance(s, IRFor):
                types.update(cls._collect_local_types(s.body))
        return types

    @classmethod
    def rewrite_stmt(cls, s, field_types, local_types):
        if isinstance(s, IRAssert):
            msg = cls.rewrite_expr(s.msg, field_types, local_types) if s.msg is not None else None
            return IRAssert(cls.rewrite_expr(s.test, field_types, local_types), msg, src=s.src)
        if isinstance(s, IRAssign):
            field = cls._self_field(s.target, field_types)
            if field is not None:
                return cls._self_update(
                    field[0], cls.rewrite_expr(s.value, field_types, local_types)
                )
            if isinstance(s.target, IRSubscript):
                receiver = s.target.value
                field = cls._self_field(receiver, field_types)
                if field is not None:
                    name, recv_type = field
                    if not cls._is_dict_type(recv_type):
                        raise CompilerPanic(
                            f"rewrite_stmt: subscript assignment to `self.{name}` is only "
                            "supported for GenMap/TextMap fields, not a value of type "
                            f"'{recv_type.name if recv_type is not None else 'unknown'}'"
                        )
                    key = cls.rewrite_expr(s.target.index, field_types, local_types)
                    value = cls.rewrite_expr(s.value, field_types, local_types)
                    current = IRAttribute(IRName(SELF), name)
                    call = map_method_call(recv_type.name, "insert", (key, value), current)
                    return cls._self_update(name, call)
                if isinstance(receiver, IRName) and cls._is_dict_type(local_types.get(receiver.id)):
                    recv_type = local_types[receiver.id]
                    key = cls.rewrite_expr(s.target.index, field_types, local_types)
                    value = cls.rewrite_expr(s.value, field_types, local_types)
                    call = map_method_call(recv_type.name, "insert", (key, value), receiver)
                    return IRAssign(receiver, call, src=s.src)
            return IRAssign(
                s.target,
                cls.rewrite_expr(s.value, field_types, local_types),
                type=s.type,
                src=s.src,
            )
        if isinstance(s, IRIf):
            return IRIf(
                cls.rewrite_expr(s.test, field_types, local_types),
                tuple(cls.rewrite_stmt(st, field_types, local_types) for st in s.body),
                tuple(cls.rewrite_stmt(st, field_types, local_types) for st in s.orelse),
                src=s.src,
            )
        if isinstance(s, IRFor):
            return IRFor(
                s.target,
                s.target_type,
                cls.rewrite_expr(s.iter, field_types, local_types),
                tuple(cls.rewrite_stmt(st, field_types, local_types) for st in s.body),
                src=s.src,
            )
        if isinstance(s, IRReturn):
            value = (
                cls.rewrite_expr(s.value, field_types, local_types) if s.value is not None else None
            )
            return IRReturn(value, src=s.src)
        if isinstance(s, IRPass):
            return s
        if isinstance(s, IRExprStmt):
            return IRExprStmt(cls.rewrite_expr(s.value, field_types, local_types), src=s.src)
        raise CompilerPanic(f"rewrite_stmt: unsupported IR statement {type(s).__name__}")

    @classmethod
    def rewrite_expr(cls, e, field_types, local_types):
        if isinstance(e, (IRName, IRConstant)):
            return e
        if isinstance(e, IRSubscript):
            recv_type = cls._receiver_type(e.value, field_types, local_types)
            if cls._is_dict_type(recv_type):
                key = cls.rewrite_expr(e.index, field_types, local_types)
                lookup = map_method_call(recv_type.name, "lookup", (key,), e.value)
                return IRCall(IRName("fromSome"), (lookup,))
            return IRSubscript(
                cls.rewrite_expr(e.value, field_types, local_types),
                cls.rewrite_expr(e.index, field_types, local_types),
                is_list=e.is_list,
            )
        if isinstance(e, IRAttribute):
            return IRAttribute(cls.rewrite_expr(e.value, field_types, local_types), e.attr)
        if isinstance(e, IRCall):
            if isinstance(e.func, IRAttribute):
                recv_type = cls._receiver_type(e.func.value, field_types, local_types)
                if cls._is_dict_type(recv_type):
                    receiver = cls.rewrite_expr(e.func.value, field_types, local_types)
                    args = tuple(cls.rewrite_expr(a, field_types, local_types) for a in e.args)
                    call = map_method_call(recv_type.name, e.func.attr, args, receiver)
                    if call is None:
                        raise CompilerPanic(
                            f"rewrite_expr: `{e.func.attr}` is not a supported {recv_type.name} "
                            f"method (supported: "
                            f"{sorted(known_map_types()[recv_type.name].method_names())})"
                        )
                    return call
                if recv_type is not None and is_optional_type(recv_type.name):
                    receiver = cls.rewrite_expr(e.func.value, field_types, local_types)
                    args = tuple(cls.rewrite_expr(a, field_types, local_types) for a in e.args)
                    call = optional_method_call(e.func.attr, args, receiver)
                    if call is not None:
                        return call
                if recv_type is not None and is_set_type(recv_type.name):
                    receiver = cls.rewrite_expr(e.func.value, field_types, local_types)
                    args = tuple(cls.rewrite_expr(a, field_types, local_types) for a in e.args)
                    call = set_method_call(e.func.attr, args, receiver)
                    if call is None:
                        raise CompilerPanic(
                            f"rewrite_expr: `{e.func.attr}` is not a supported {recv_type.name} "
                            f"method (supported: {sorted(known_set_methods())})"
                        )
                    return call
            return IRCall(
                cls.rewrite_expr(e.func, field_types, local_types),
                tuple(cls.rewrite_expr(a, field_types, local_types) for a in e.args),
                tuple((k, cls.rewrite_expr(v, field_types, local_types)) for k, v in e.keywords),
            )
        if isinstance(e, IRList):
            return IRList(
                tuple(cls.rewrite_expr(el, field_types, local_types) for el in e.elements)
            )
        if isinstance(e, IRTuple):
            return IRTuple(
                tuple(cls.rewrite_expr(el, field_types, local_types) for el in e.elements)
            )
        if isinstance(e, IRDict):
            return IRDict(
                tuple(cls.rewrite_expr(k, field_types, local_types) for k in e.keys),
                tuple(cls.rewrite_expr(v, field_types, local_types) for v in e.values),
                kind=e.kind,
            )
        if isinstance(e, IRBinOp):
            return IRBinOp(
                e.op,
                cls.rewrite_expr(e.left, field_types, local_types),
                cls.rewrite_expr(e.right, field_types, local_types),
            )
        if isinstance(e, IRBoolOp):
            return IRBoolOp(
                e.op, tuple(cls.rewrite_expr(v, field_types, local_types) for v in e.values)
            )
        if isinstance(e, IRUnaryOp):
            return IRUnaryOp(e.op, cls.rewrite_expr(e.operand, field_types, local_types))
        if isinstance(e, IRCompare):
            if e.op in ("in", "not in"):
                recv_type = cls._receiver_type(e.right, field_types, local_types)
                if cls._is_dict_type(recv_type):
                    left = cls.rewrite_expr(e.left, field_types, local_types)
                    receiver = cls.rewrite_expr(e.right, field_types, local_types)
                    member = map_method_call(recv_type.name, "member", (left,), receiver)
                    return IRUnaryOp("not", member) if e.op == "not in" else member
            return IRCompare(
                cls.rewrite_expr(e.left, field_types, local_types),
                e.op,
                cls.rewrite_expr(e.right, field_types, local_types),
            )
        if isinstance(e, IRRecordUpdate):
            return IRRecordUpdate(
                cls.rewrite_expr(e.base, field_types, local_types),
                tuple(
                    (name, cls.rewrite_expr(v, field_types, local_types)) for name, v in e.updates
                ),
            )
        if isinstance(e, IRIfExp):
            return IRIfExp(
                cls.rewrite_expr(e.test, field_types, local_types),
                cls.rewrite_expr(e.body, field_types, local_types),
                cls.rewrite_expr(e.orelse, field_types, local_types),
            )
        raise CompilerPanic(f"rewrite_expr: unsupported IR expression {type(e).__name__}")

    @staticmethod
    def _self_field(e, field_types):
        if isinstance(e, IRAttribute) and isinstance(e.value, IRName) and e.value.id == SELF:
            if e.attr in field_types:
                return e.attr, field_types[e.attr]
        return None

    @classmethod
    def _receiver_type(cls, e, field_types, local_types):
        field = cls._self_field(e, field_types)
        if field is not None:
            return field[1]
        if isinstance(e, IRName):
            return local_types.get(e.id)
        return None

    @classmethod
    def _is_dict_type(cls, t) -> bool:
        return t is not None and t.name in cls.DICT_TYPE_NAMES

    @staticmethod
    def _self_update(field, new_value):
        return IRAssign(IRName(SELF), IRRecordUpdate(IRName(SELF), ((field, new_value),)))


class SelfMutationInjector:
    NEW_SELF_CID = "_damlforge_new_self"

    @classmethod
    def body_mutates_self(cls, stmts) -> bool:
        for s in stmts:
            if isinstance(s, IRAssign) and isinstance(s.target, IRName) and s.target.id == SELF:
                return True
            if isinstance(s, IRIf) and (
                cls.body_mutates_self(s.body) or cls.body_mutates_self(s.orelse)
            ):
                return True
            if isinstance(s, IRFor) and cls.body_mutates_self(s.body):
                return True
        return False

    @classmethod
    def inject_self_create(cls, stmts):
        result = cls._replace_returns(stmts)
        if not cls._always_terminates(stmts):
            result = result + cls._create_self_pair(IRTuple(()))
        return result

    @classmethod
    def _create_self_pair(cls, value):
        return [
            IRAssign(IRName(cls.NEW_SELF_CID), IRCall(IRName("create"), (IRName(SELF),))),
            IRReturn(IRTuple((IRName(cls.NEW_SELF_CID), value))),
        ]

    @classmethod
    def _always_terminates(cls, stmts) -> bool:
        if not stmts:
            return False
        last = stmts[-1]
        if isinstance(last, IRReturn):
            return True
        if isinstance(last, IRIf):
            return (
                bool(last.orelse)
                and cls._always_terminates(list(last.body))
                and cls._always_terminates(list(last.orelse))
            )
        return False

    @classmethod
    def _replace_returns(cls, stmts):
        result = []
        for s in stmts:
            if isinstance(s, IRReturn):
                value = s.value if s.value is not None else IRTuple(())
                result.extend(cls._create_self_pair(value))
            elif isinstance(s, IRIf):
                result.append(
                    IRIf(
                        s.test,
                        tuple(cls._replace_returns(list(s.body))),
                        tuple(cls._replace_returns(list(s.orelse))),
                        src=s.src,
                    )
                )
            elif isinstance(s, IRFor):
                result.append(
                    IRFor(
                        s.target,
                        s.target_type,
                        s.iter,
                        tuple(cls._replace_returns(list(s.body))),
                        src=s.src,
                    )
                )
            else:
                result.append(s)
        return result
