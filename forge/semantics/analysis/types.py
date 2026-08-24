from forge.ast import nodes as vy_ast
from forge.exceptions import DamlForgeException, ExceptionList
from forge.ir.lower import lower_type
from forge.ir.nodes import TypeRef
from forge.models.error_codes import ErrorCodes
from forge.semantics.analysis.structure import _reachable_modules

PRIMITIVE_TYPES = {
    "Party",
    "Text",
    "Int",
    "int",
    "float",
    "Decimal",
    "Date",
    "Timestamp",
    "bool",
    "None",
}
GENERIC_TYPES = {"ContractId", "Optional", "list", "tuple", "TextMap", "GenMap"}
BUILTIN_TYPE_NAMES = PRIMITIVE_TYPES | GENERIC_TYPES

_LOCAL_DECLARATION_TYPES = (
    vy_ast.StructDef,
    vy_ast.FlagDef,
    vy_ast.InterfaceDef,
    vy_ast.TemplateDef,
    vy_ast.InstanceDef,
)


def _imported_names(module: vy_ast.Module) -> set:
    names = set()
    for stmt in module.body:
        if isinstance(stmt, vy_ast.Import):
            for alias in stmt.names:
                names.add(alias.asname or alias.name)
        elif isinstance(stmt, vy_ast.ImportFrom):
            for alias in stmt.names:
                names.add(alias.asname or alias.name)
    return names


def known_type_names(modules) -> set:
    names = set(BUILTIN_TYPE_NAMES)
    for module in _reachable_modules(modules):
        names |= _imported_names(module)
        for node in module.body:
            if isinstance(node, _LOCAL_DECLARATION_TYPES):
                names.add(node.name)
    return names


def _walk_type_ref(type_ref: TypeRef, known_names: set, node, context: str, errors: ExceptionList) -> None:
    if type_ref.name not in known_names:
        errors.append(
            DamlForgeException(
                f"No builtin or user-defined type named `{type_ref.name}` ({context})",
                node,
                code=ErrorCodes.DF1213.value,
            )
        )
    for arg in type_ref.args:
        _walk_type_ref(arg, known_names, node, context, errors)


def check_type_annotation(node, known_names: set, context: str, errors: ExceptionList) -> None:
    if node is None:
        return
    type_ref = lower_type(node)
    _walk_type_ref(type_ref, known_names, node, context, errors)


def check_function_type_annotations(
    fn: vy_ast.FunctionDef, known_names: set, errors: ExceptionList
) -> None:
    for arg in fn.args.args:
        if arg.arg == "self" or arg.annotation is None:
            continue
        check_type_annotation(
            arg.annotation, known_names, f"argument `{arg.arg}` of `{fn.name}`", errors
        )
    if fn.returns is not None:
        check_type_annotation(fn.returns, known_names, f"return type of `{fn.name}`", errors)


def check_struct_type_annotations(node: vy_ast.StructDef, known_names: set, errors: ExceptionList) -> None:
    for stmt in node.body:
        if isinstance(stmt, vy_ast.AnnAssign):
            check_type_annotation(
                stmt.annotation, known_names, f"field `{stmt.target.id}` of `{node.name}`", errors
            )


def check_template_field_type_annotations(
    node: vy_ast.TemplateDef, known_names: set, errors: ExceptionList
) -> None:
    reserved = ("signatory", "observer", "key", "maintainer", "ensure")
    for stmt in node.body:
        if not isinstance(stmt, vy_ast.AnnAssign):
            continue
        if isinstance(stmt.target, vy_ast.Name) and stmt.target.id in reserved:
            continue
        check_type_annotation(
            stmt.annotation, known_names, f"field `{stmt.target.id}` of `{node.name}`", errors
        )


def check_interface_view_type_annotation(
    node: vy_ast.InterfaceDef, known_names: set, errors: ExceptionList
) -> None:
    for kw in node.keywords:
        if kw.arg == "view":
            check_type_annotation(kw.value, known_names, f"`view=` of `{node.name}`", errors)


def check_container_type_annotations(node: vy_ast.TopLevel, known_names: set, errors: ExceptionList) -> None:
    if isinstance(node, vy_ast.StructDef):
        check_struct_type_annotations(node, known_names, errors)
        return

    if isinstance(node, vy_ast.TemplateDef):
        check_template_field_type_annotations(node, known_names, errors)
    elif isinstance(node, vy_ast.InterfaceDef):
        check_interface_view_type_annotation(node, known_names, errors)

    if isinstance(node, (vy_ast.TemplateDef, vy_ast.InterfaceDef, vy_ast.InstanceDef)):
        for stmt in node.body:
            if isinstance(stmt, vy_ast.FunctionDef):
                check_function_type_annotations(stmt, known_names, errors)
    elif isinstance(node, vy_ast.FunctionDef):
        check_function_type_annotations(node, known_names, errors)
