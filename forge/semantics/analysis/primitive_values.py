"""Semantic validation for Daml primitive values and constant expressions."""

from decimal import Decimal, InvalidOperation, localcontext

from forge.ast import nodes as vy_ast
from forge.exceptions import DamlForgeException, ExceptionList
from forge.ir.lower import lower_type
from forge.ir.nodes import TypeRef
from forge.models.error_codes import ErrorCodes
from forge.semantics.primitive_specs import (
    INT_MAX,
    INT_MIN,
    canonical_type_name,
    decimal_policy_error,
    text_policy_error,
)

_LITERAL_NODES = (vy_ast.Int, vy_ast.Decimal, vy_ast.Str, vy_ast.NameConstant)


def _canonical(ref: TypeRef) -> TypeRef:
    return TypeRef(canonical_type_name(ref.name), tuple(_canonical(arg) for arg in ref.args))


def _literal_value(expr):
    if isinstance(expr, vy_ast.Int):
        return "Int", expr.value
    if isinstance(expr, vy_ast.Decimal):
        return "Decimal", expr.value
    if isinstance(expr, vy_ast.Str):
        return "Text", expr.value
    if isinstance(expr, vy_ast.NameConstant):
        if expr.value is None:
            return "Unit", None
        if isinstance(expr.value, bool):
            return "Bool", expr.value
    return None


def _constant_value(expr):
    """Evaluate the small constant subset needed for overflow diagnostics."""

    literal = _literal_value(expr)
    if literal is not None:
        return literal
    if isinstance(expr, vy_ast.UnaryOp) and isinstance(expr.operand, vy_ast.Num):
        value = _constant_value(expr.operand)
        if value is None:
            return None
        kind, number = value
        if isinstance(expr.op, vy_ast.USub) and kind in ("Int", "Decimal"):
            return kind, -number
        return None
    if not isinstance(expr, vy_ast.BinOp):
        return None
    left = _constant_value(expr.left)
    right = _constant_value(expr.right)
    if left is None or right is None or left[0] not in ("Int", "Decimal"):
        return None
    if right[0] not in ("Int", "Decimal"):
        return None
    kind = "Decimal" if "Decimal" in (left[0], right[0]) else "Int"
    lhs, rhs = left[1], right[1]
    try:
        with localcontext() as context:
            context.prec = 100
            if kind == "Decimal":
                lhs, rhs = Decimal(lhs), Decimal(rhs)
            if isinstance(expr.op, vy_ast.Add):
                value = lhs + rhs
            elif isinstance(expr.op, vy_ast.Sub):
                value = lhs - rhs
            elif isinstance(expr.op, vy_ast.Mult):
                value = lhs * rhs
            elif isinstance(expr.op, (vy_ast.Div, vy_ast.FloorDiv)):
                if rhs == 0:
                    return None
                value = lhs / rhs if kind == "Decimal" else int(lhs / rhs)
            elif isinstance(expr.op, vy_ast.Mod):
                if rhs == 0:
                    return None
                value = lhs % rhs
            elif isinstance(expr.op, vy_ast.Pow) and isinstance(rhs, int) and rhs >= 0:
                value = lhs**rhs
            else:
                return None
    except (ArithmeticError, InvalidOperation):
        return None
    return kind, value


class PrimitivePolicyChecker:
    def __init__(
        self,
        node: vy_ast.TopLevel,
        field_types: dict,
        return_types: dict,
        function_param_types: dict,
        errors: ExceptionList,
    ) -> None:
        self.node = node
        self.field_types = field_types
        self.return_types = return_types
        self.function_param_types = function_param_types
        self.errors = errors
        self._reported: set[tuple[int, str]] = set()

    def _error(self, message: str, node) -> None:
        key = (id(node), message)
        if key in self._reported:
            return
        self._reported.add(key)
        self.errors.append(DamlForgeException(message, node, code=ErrorCodes.DF1229.value))

    def _check_primitive(self, kind: str, value, node, expected: str | None = None) -> None:
        expected = canonical_type_name(expected) if expected is not None else kind
        if expected == "Int":
            if kind != "Int":
                return
            if not INT_MIN <= value <= INT_MAX:
                self._error(
                    f"Daml Int literal must be between {INT_MIN} and {INT_MAX}; got {value}", node
                )
            return

        if expected == "Decimal":
            if kind not in ("Int", "Decimal"):
                return
            decimal_value = Decimal(value)
            reason = decimal_policy_error(decimal_value)
            if reason is not None:
                self._error(f"Daml Decimal literal {reason}; got {value}", node)
            return

        if expected == "Text" and kind == "Text":
            reason = text_policy_error(value)
            if reason is not None:
                self._error(f"Daml Text literal {reason}", node)
            return

        if expected == "RelTime" and kind == "Int":
            if not INT_MIN <= value <= INT_MAX:
                self._error(
                    f"Daml RelTime must be between {INT_MIN} and {INT_MAX} microseconds; "
                    f"got {value}",
                    node,
                )

    def _check_expr(self, expr, expected: TypeRef | None) -> None:
        if expr is None:
            return
        expected = _canonical(expected) if expected is not None else None
        constant = _constant_value(expr)
        if constant is not None:
            self._check_primitive(
                constant[0], constant[1], expr, expected.name if expected else None
            )
            return

        literal = _literal_value(expr)
        if literal is not None:
            self._check_primitive(literal[0], literal[1], expr, expected.name if expected else None)
            return

        if expected is not None and expected.name == "Optional" and expected.args:
            if not (isinstance(expr, vy_ast.NameConstant) and expr.value is None):
                self._check_expr(expr, expected.args[0])
            return
        if isinstance(expr, vy_ast.List) and expected is not None and expected.args:
            for element in expr.elements:
                self._check_expr(element, expected.args[0])
            return
        if isinstance(expr, vy_ast.Tuple) and expected is not None:
            for element, element_type in zip(expr.elements, expected.args):
                self._check_expr(element, element_type)
            return
        if isinstance(expr, vy_ast.Dict) and expected is not None:
            if expected.name == "TextMap" and expected.args:
                for key, value in zip(expr.keys, expr.values):
                    self._check_expr(key, TypeRef("Text"))
                    self._check_expr(value, expected.args[0])
            elif expected.name == "GenMap" and len(expected.args) == 2:
                for key, value in zip(expr.keys, expr.values):
                    self._check_expr(key, expected.args[0])
                    self._check_expr(value, expected.args[1])
            return

        if isinstance(expr, vy_ast.Call):
            self._check_call_arguments(expr)
            return

        for child in expr.get_descendants(_LITERAL_NODES, include_self=True):
            literal = _literal_value(child)
            if literal is not None:
                self._check_primitive(literal[0], literal[1], child)

    def _check_call_arguments(self, call: vy_ast.Call) -> None:
        if not isinstance(call.func, vy_ast.Name):
            return
        expected = self.function_param_types.get(call.func.id)
        if expected is not None and not call.keywords:
            for arg, type_ref in zip(call.args, expected):
                if type_ref is not None:
                    self._check_expr(arg, type_ref)
            return
        fields = self.field_types.get(call.func.id)
        if fields is not None:
            for keyword in call.keywords:
                field_type = fields.get(keyword.arg)
                if field_type is not None:
                    self._check_expr(keyword.value, field_type)

    def _check_function(self, fn: vy_ast.FunctionDef) -> None:
        return_type = lower_type(fn.returns) if fn.returns is not None else None
        local_types = {}
        for argument in fn.args.args:
            if argument.arg != "self" and argument.annotation is not None:
                local_types[argument.arg] = lower_type(argument.annotation)

        for stmt in fn.body:
            self._check_statement(stmt, return_type, local_types)

    def _check_statement(self, stmt, return_type: TypeRef | None, local_types: dict) -> None:
        expected_type: TypeRef | None = None
        if isinstance(stmt, vy_ast.AnnAssign):
            expected_type = lower_type(stmt.annotation)
            if stmt.value is not None:
                self._check_expr(stmt.value, expected_type)
            if isinstance(stmt.target, vy_ast.Name):
                local_types[stmt.target.id] = expected_type
        elif isinstance(stmt, vy_ast.Assign):
            if isinstance(stmt.target, vy_ast.Name):
                expected_type = local_types.get(stmt.target.id)
            self._check_expr(stmt.value, expected_type)
            if isinstance(stmt.target, vy_ast.Name) and expected_type is None:
                constant = _constant_value(stmt.value)
                if constant is not None:
                    local_types[stmt.target.id] = TypeRef(constant[0])
        elif isinstance(stmt, vy_ast.Return):
            self._check_expr(stmt.value, return_type)
        elif isinstance(stmt, vy_ast.Expr):
            self._check_expr(stmt.value, None)
        else:
            for child in stmt.get_descendants(vy_ast.Expr, include_self=True):
                if isinstance(child, vy_ast.Expr):
                    self._check_expr(child.value, None)

    def run(self) -> None:
        # Always validate literals, including literals nested in expressions
        # that do not yet have enough type information for a full type check.
        for literal in self.node.get_descendants(_LITERAL_NODES, include_self=True):
            value = _literal_value(literal)
            if value is not None:
                self._check_primitive(value[0], value[1], literal)

        if isinstance(self.node, (vy_ast.StructDef, vy_ast.TemplateDef)):
            for stmt in self.node.body:
                if isinstance(stmt, vy_ast.AnnAssign) and stmt.value is not None:
                    self._check_expr(stmt.value, lower_type(stmt.annotation))

        functions = []
        if isinstance(self.node, vy_ast.FunctionDef):
            functions.append(self.node)
        elif isinstance(self.node, (vy_ast.TemplateDef, vy_ast.InterfaceDef)):
            functions.extend(
                child for child in self.node.body if isinstance(child, vy_ast.FunctionDef)
            )
        elif type(self.node).__name__ == "VariantDef":
            functions.extend(
                child for child in self.node.body if isinstance(child, vy_ast.FunctionDef)
            )
        for fn in functions:
            self._check_function(fn)


def check_primitive_policies(
    node: vy_ast.TopLevel,
    field_types: dict,
    return_types: dict,
    function_param_types: dict,
    errors: ExceptionList,
) -> None:
    PrimitivePolicyChecker(node, field_types, return_types, function_param_types, errors).run()
