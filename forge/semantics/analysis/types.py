from forge.ast import nodes as vy_ast
from forge.exceptions import DamlForgeException, ExceptionList
from forge.ir.lower import lower_type
from forge.ir.nodes import TypeRef
from forge.models.error_codes import ErrorCodes
from forge.semantics.analysis.imports import ImportsBuilder
from forge.semantics.analysis.structure import _reachable_modules


class _PrimT:
    """Base for a fixed, non-parametrized Daml primitive type - mirrors
    Vyper's `_PrimT` (`vyper/semantics/types/primitives.py`), which wraps
    even non-parametrized types like `BoolT`/`DecimalT`/`AddressT` as
    classes rather than bare string literals."""

    _id: str


class PartyT(_PrimT):
    _id = "Party"


class TextT(_PrimT):
    _id = "Text"


class IntT(_PrimT):
    _id = "Int"


class PyIntT(_PrimT):
    _id = "int"


class PyFloatT(_PrimT):
    _id = "float"


class DecimalT(_PrimT):
    _id = "Decimal"


class DateT(_PrimT):
    _id = "Date"


class TimestampT(_PrimT):
    _id = "Timestamp"


class BoolT(_PrimT):
    _id = "bool"


class NoneT(_PrimT):
    _id = "None"


def _get_primitive_types() -> dict:
    types = [
        PartyT(),
        TextT(),
        IntT(),
        PyIntT(),
        PyFloatT(),
        DecimalT(),
        DateT(),
        TimestampT(),
        BoolT(),
        NoneT(),
    ]
    return {t._id: t for t in types}


class _GenericT:
    """Base for a builtin generic/parametrized Daml type constructor -
    mirrors Vyper's sequence types (`HashMapT`/`DArrayT`), which are also
    registered by `_id` rather than a bare string in `GENERIC_TYPES`. Each
    of these may grow its own construction/arity checks later."""

    _id: str


class ContractIdT(_GenericT):
    _id = "ContractId"


class OptionalT(_GenericT):
    _id = "Optional"


class ListT(_GenericT):
    _id = "list"


class TupleT(_GenericT):
    _id = "tuple"


class TextMapT(_GenericT):
    _id = "TextMap"


class GenMapT(_GenericT):
    _id = "GenMap"


def _get_generic_types() -> dict:
    types = [ContractIdT(), OptionalT(), ListT(), TupleT(), TextMapT(), GenMapT()]
    return {t._id: t for t in types}


def daml_builtin_type_names() -> set:
    """Every name Daml's own prelude always has in scope - a Python stand-in
    for one of these (`forge.models.Party`, `decimal.Decimal`,
    `typing.Optional`, ...) needs no corresponding Daml `import` at all,
    unlike a genuine external Daml module reference (`Splice.*`, a sibling
    `.vy` module)."""
    return set(_get_primitive_types()) | set(_get_generic_types())


_DECLARATION_TYPES = (
    vy_ast.StructDef,
    vy_ast.FlagDef,
    vy_ast.InterfaceDef,
    vy_ast.TemplateDef,
    vy_ast.InstanceDef,
)


def known_declarations(modules) -> dict:
    declarations = {}
    for module in _reachable_modules(modules):
        for node in module.body:
            if isinstance(node, _DECLARATION_TYPES):
                declarations[node.name] = node
    return declarations


def known_type_names(modules) -> set:
    names = daml_builtin_type_names()
    for module in _reachable_modules(modules):
        names |= ImportsBuilder.imported_names(module)
    names |= known_declarations(modules).keys()
    return names


def _flag_members(node: vy_ast.FlagDef) -> frozenset:
    return frozenset(
        stmt.value.id
        for stmt in node.body
        if isinstance(stmt, vy_ast.Expr) and isinstance(stmt.value, vy_ast.Name)
    )


def check_flag_value_access(node: vy_ast.TopLevel, declarations: dict, errors: ExceptionList) -> None:
    for attr in node.get_descendants(vy_ast.Attribute):
        if not isinstance(attr.value, vy_ast.Name):
            continue
        declaration = declarations.get(attr.value.id)
        if not isinstance(declaration, vy_ast.FlagDef):
            continue
        members = _flag_members(declaration)
        if attr.attr in members:
            attr._metadata["is_flag_value"] = True
            continue
        errors.append(
            DamlForgeException(
                f"`{attr.attr}` is not a member of flag `{attr.value.id}` "
                f"(known members: {', '.join(sorted(members))})",
                attr,
                code=ErrorCodes.DF1216.value,
            )
        )


_NON_VARIABLE_DECLARATION_TYPES = (
    vy_ast.StructDef,
    vy_ast.InterfaceDef,
    vy_ast.TemplateDef,
    vy_ast.InstanceDef,
)

_LEDGER_EFFECT_BUILTINS = frozenset({"create", "fetch", "exercise", "archive", "lookup"})
_LANGUAGE_BUILTIN_NAMES = frozenset({"len", "ceil"})


def known_global_names(modules) -> frozenset:
    from forge.builtins import collect_daml_builtins

    names = set(daml_builtin_type_names())
    for module in _reachable_modules(modules):
        names |= ImportsBuilder.imported_names(module)
        for node in module.body:
            if isinstance(node, vy_ast.FunctionDef):
                names.add(node.name)
    names |= _LEDGER_EFFECT_BUILTINS
    names |= _LANGUAGE_BUILTIN_NAMES
    names |= set(collect_daml_builtins().function_renames.keys())
    return frozenset(names)


def _extract_bound_names(target, names: set) -> None:
    if isinstance(target, vy_ast.Name):
        names.add(target.id)
    elif isinstance(target, vy_ast.Tuple):
        for el in target.elements:
            _extract_bound_names(el, names)
    elif hasattr(target, "target"):
        _extract_bound_names(target.target, names)


def _local_bound_names(fn: vy_ast.FunctionDef) -> frozenset:
    names = {a.arg for a in fn.args.args}
    for assign in fn.get_descendants((vy_ast.Assign, vy_ast.AnnAssign)):
        _extract_bound_names(assign.target, names)
    for for_stmt in fn.get_descendants(vy_ast.For):
        _extract_bound_names(for_stmt.target, names)
    return frozenset(names)


def check_unresolved_attribute_base(
    node: vy_ast.TopLevel, declarations: dict, global_names: frozenset, errors: ExceptionList
) -> None:
    fns = [node] if isinstance(node, vy_ast.FunctionDef) else node.get_descendants(vy_ast.FunctionDef)
    for fn in fns:
        local_names = _local_bound_names(fn)
        for attr in fn.get_descendants(vy_ast.Attribute):
            if not isinstance(attr.value, vy_ast.Name):
                continue
            name = attr.value.id
            if name in local_names:
                continue
            declaration = declarations.get(name)
            if isinstance(declaration, vy_ast.FlagDef):
                continue
            if isinstance(declaration, _NON_VARIABLE_DECLARATION_TYPES):
                errors.append(
                    DamlForgeException(
                        f"`{name}` is a type name, not a variable - no variable named `{name}` "
                        f"exists in this scope; use `self.{attr.attr}` to access the current "
                        "contract's fields",
                        attr,
                        code=ErrorCodes.DF1219.value,
                    )
                )
                continue
            if name in global_names:
                continue
            errors.append(
                DamlForgeException(
                    f"`{name}` is not defined - no variable, parameter, import, or declaration "
                    f"named `{name}` exists in scope here",
                    attr,
                    code=ErrorCodes.DF1219.value,
                )
            )


def _is_list_type_annotation(node) -> bool:
    return (
        isinstance(node, vy_ast.Subscript)
        and isinstance(node.value, vy_ast.Name)
        and node.value.id == "list"
    )


def known_list_returning_functions(modules) -> frozenset:
    names = set()
    for module in _reachable_modules(modules):
        for node in module.body:
            if isinstance(node, vy_ast.FunctionDef) and _is_list_type_annotation(node.returns):
                names.add(node.name)
    return frozenset(names)


def _assigns_list_value(value, list_returning_fns: frozenset, list_names: set) -> bool:
    if isinstance(value, vy_ast.List):
        return True
    if isinstance(value, vy_ast.Name):
        return value.id in list_names
    if (
        isinstance(value, vy_ast.Call)
        and isinstance(value.func, vy_ast.Name)
        and value.func.id in list_returning_fns
    ):
        return True
    return False


def _mark_list_subscripts_in_body(stmts, list_returning_fns: frozenset, list_names: set) -> None:
    for stmt in stmts:
        for sub in stmt.get_descendants(vy_ast.Subscript, include_self=True):
            if (
                isinstance(sub.value, vy_ast.Name)
                and sub.value.id in list_names
                and isinstance(sub.slice, vy_ast.Int)
            ):
                sub._metadata["is_list_value"] = True
        if isinstance(stmt, vy_ast.Assign) and isinstance(stmt.target, vy_ast.Name):
            if _assigns_list_value(stmt.value, list_returning_fns, list_names):
                list_names.add(stmt.target.id)
            else:
                list_names.discard(stmt.target.id)


def mark_list_subscripts(node: vy_ast.TopLevel, list_returning_fns: frozenset) -> None:
    fns = [node] if isinstance(node, vy_ast.FunctionDef) else node.get_descendants(vy_ast.FunctionDef)
    for fn in fns:
        _mark_list_subscripts_in_body(fn.body, list_returning_fns, set())


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


def known_field_types(modules) -> dict:
    """Registry of `{struct_or_template_name: {field_name: TypeRef}}`, built
    from every struct/template field declaration across all reachable
    modules. DamlForge does no general type inference or checking (IR is
    structural, not typed - see the codegen design doc), but this narrow
    registry is enough to catch one real, previously-undetected class of bug:
    a field declared `Optional[T]` constructed with a value that is provably
    NOT itself optional or `None` - real Daml's `Optional` is a genuine sum
    type needing an explicit `Some(...)` wrapper, unlike Python's own
    `Optional[T] = T | None` typing (which accepts a bare `T` with no wrapping
    at all) - so this specific mismatch compiles fine as `.vy`/Python but
    fails the real Daml compiler outright ("Couldn't match expected type
    'Optional X' with actual type 'X'"), and nothing in this codebase caught
    it before real `dpm build` validation started."""
    registry = {}
    for module in _reachable_modules(modules):
        for node in module.body:
            if not isinstance(node, (vy_ast.StructDef, vy_ast.TemplateDef)):
                continue
            fields = {}
            for stmt in node.body:
                if isinstance(stmt, vy_ast.AnnAssign) and isinstance(stmt.target, vy_ast.Name):
                    fields[stmt.target.id] = lower_type(stmt.annotation)
            registry[node.name] = fields
    return registry


def _local_value_types(fn: vy_ast.FunctionDef, field_types: dict) -> dict:
    """Best-effort, non-flow-sensitive map of `{name: TypeRef}` for names
    whose type can be determined from this function's own signature/body: an
    explicit parameter annotation, an explicit `AnnAssign`, or - failing an
    annotation - assignment from a call to a known struct/template
    constructor (which always produces that exact, non-optional type). Not
    real type inference - just enough to catch the shapes actually seen in
    practice without false-positiving on anything more complex (a value
    computed via a plain function call, attribute access, or unannotated
    parameter is left unresolved and never flagged)."""
    local_types = {}
    for arg in fn.args.args:
        if arg.arg == "self" or arg.annotation is None:
            continue
        local_types[arg.arg] = lower_type(arg.annotation)
    for stmt in fn.get_descendants(vy_ast.AnnAssign):
        if isinstance(stmt.target, vy_ast.Name):
            local_types[stmt.target.id] = lower_type(stmt.annotation)
    for stmt in fn.get_descendants(vy_ast.Assign):
        if (
            isinstance(stmt.target, vy_ast.Name)
            and stmt.target.id not in local_types
            and isinstance(stmt.value, vy_ast.Call)
            and isinstance(stmt.value.func, vy_ast.Name)
            and stmt.value.func.id in field_types
        ):
            local_types[stmt.target.id] = TypeRef(stmt.value.func.id)
    return local_types


def check_optional_field_construction(node: vy_ast.TopLevel, field_types: dict, errors: ExceptionList) -> None:
    if isinstance(node, (vy_ast.TemplateDef, vy_ast.InterfaceDef, vy_ast.InstanceDef)):
        functions = [n for n in node.body if isinstance(n, vy_ast.FunctionDef)]
    elif isinstance(node, vy_ast.FunctionDef):
        functions = [node]
    else:
        return

    for fn in functions:
        local_types = _local_value_types(fn, field_types)
        for call in fn.get_descendants(vy_ast.Call):
            if not (isinstance(call.func, vy_ast.Name) and call.func.id in field_types):
                continue
            fields = field_types[call.func.id]
            for kw in call.keywords:
                field_type = fields.get(kw.arg)
                if field_type is None or field_type.name != "Optional":
                    continue
                
                valid = False
                if isinstance(kw.value, vy_ast.NameConstant) and kw.value.value is None:
                    valid = False
                if isinstance(kw.value, vy_ast.Call) and isinstance(kw.value.func, vy_ast.Name) and kw.value.func.id in field_types:
                    # constructing another known struct/template directly always
                    # produces that exact type, never `Optional` of it.
                    valid = True
                if isinstance(kw.value, vy_ast.Name) and kw.value.id in local_types:
                    valid = local_types[kw.value.id].name != "Optional"
                if valid:
                    errors.append(
                        DamlForgeException(
                            f"`{call.func.id}.{kw.arg}` is declared `Optional[...]` but is "
                            "constructed here with a value that is not itself optional or "
                            f"`None` - wrap it, e.g. `Some({kw.arg})`",
                            kw.value,
                            code=ErrorCodes.DF1215.value,
                        )
                    )


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
