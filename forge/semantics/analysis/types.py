from functools import cached_property

from forge.ast import nodes as vy_ast
from forge.exceptions import DamlForgeException, ExceptionList
from forge.ir.lower import lower_type
from forge.ir.nodes import TypeRef
from forge.models.error_codes import ErrorCodes
from forge.semantics.analysis.imports import ImportsBuilder
from forge.semantics.analysis.structure import _reachable_modules
from forge.semantics.primitive_specs import generic_spec, type_is_ordered


class _PrimT:
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


class PyStrT(_PrimT):
    _id = "str"


class DecimalT(_PrimT):
    _id = "Decimal"


class DateT(_PrimT):
    _id = "Date"


class TimestampT(_PrimT):
    _id = "Timestamp"


class RelTimeT(_PrimT):
    _id = "RelTime"


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
        PyStrT(),
        DecimalT(),
        DateT(),
        TimestampT(),
        RelTimeT(),
        BoolT(),
        NoneT(),
    ]
    return {t._id: t for t in types}


class _GenericT:
    _id: str


class ContractIdT(_GenericT):
    _id = "ContractId"


class OptionalT(_GenericT):
    _id = "Optional"


class ListT(_GenericT):
    _id = "list"


class TupleT(_GenericT):
    _id = "tuple"


class SetT(_GenericT):
    _id = "set"


class FrozenSetT(_GenericT):
    _id = "frozenset"


def _get_generic_types() -> dict:
    types = [ContractIdT(), OptionalT(), ListT(), TupleT(), SetT(), FrozenSetT()]
    return {t._id: t for t in types}


def daml_builtin_type_names() -> set:
    from forge.builtins.maps import known_map_types

    return set(_get_primitive_types()) | set(_get_generic_types()) | set(known_map_types())


_DECLARATION_TYPES = (
    vy_ast.StructDef,
    vy_ast.FlagDef,
    vy_ast.VariantDef,
    vy_ast.InterfaceDef,
    vy_ast.TemplateDef,
)


class ModuleScope:
    """Names and type information visible from one module."""

    def __init__(self, module: vy_ast.Module):
        self.module = module

    @cached_property
    def imported_declarations(self) -> dict:
        return _direct_imported_declarations(self.module)

    @cached_property
    def type_names(self) -> set:
        return known_type_names(self)

    @cached_property
    def declarations(self) -> dict:
        return known_declarations(self)

    @cached_property
    def field_types(self) -> dict:
        return known_field_types(self)

    @cached_property
    def return_types(self) -> dict:
        return known_return_types(self, self.field_types)

    @cached_property
    def global_names(self) -> frozenset:
        return known_global_names(self)

    @cached_property
    def function_param_types(self) -> dict:
        return known_function_param_types(self)

    @cached_property
    def list_returning_functions(self) -> frozenset:
        return known_list_returning_functions(self)


def _direct_imported_declarations(module: vy_ast.Module) -> dict:
    declarations = {}
    importable_types = (*_DECLARATION_TYPES, vy_ast.FunctionDef)
    for stmt in module.body:
        if not isinstance(stmt, vy_ast.ImportFrom):
            continue
        imported = {
            node.name: node
            for info in stmt._metadata.get("import_infos", ())
            for node in info.ast.body
            if isinstance(node, importable_types)
        }
        for info in stmt._metadata.get("import_infos", ()):
            for container in info.ast.body:
                for child in getattr(container, "body", ()):
                    export_name = ImportsBuilder._choice_export_name(child)
                    if export_name is not None:
                        imported[export_name] = child
        for alias in stmt.names:
            if alias.name == "*":
                declarations.update(imported)
            elif alias.name in imported:
                declarations[alias.asname or alias.name] = imported[alias.name]
    return declarations


def _scope_modules(modules) -> list[vy_ast.Module]:
    if isinstance(modules, ModuleScope):
        return [modules.module]
    return _reachable_modules(modules)


def _scope_nodes(modules):
    for module in _scope_modules(modules):
        yield from module.body
        if isinstance(modules, ModuleScope):
            yield from modules.imported_declarations.values()


def known_declarations(modules) -> dict:
    declarations = {}
    for module in _scope_modules(modules):
        for node in module.body:
            if isinstance(node, _DECLARATION_TYPES):
                declarations[node.name] = node
        if isinstance(modules, ModuleScope):
            declarations.update(
                {
                    name: node
                    for name, node in modules.imported_declarations.items()
                    if isinstance(node, _DECLARATION_TYPES)
                }
            )
    return declarations


def _qualified_import_type_names(modules) -> set:
    names = set()
    for module in _scope_modules(modules):
        for stmt in module.body:
            if not isinstance(stmt, vy_ast.Import):
                continue
            for alias in stmt.names:
                if alias.asname is None:
                    continue
                mod = ImportsBuilder._import_real_module(alias.name)
                if mod is None:
                    continue
                for attr_name, obj in vars(mod).items():
                    if getattr(obj, "__module__", None) != mod.__name__:
                        continue
                    if isinstance(obj, type):
                        names.add(f"{alias.asname}.{attr_name}")
    return names


def known_type_names(modules) -> set:
    names = daml_builtin_type_names()
    for module in _scope_modules(modules):
        names |= ImportsBuilder.imported_names(module)
    names |= known_declarations(modules).keys()
    names |= _qualified_import_type_names(modules)
    return names


def _flag_members(node: vy_ast.FlagDef) -> frozenset:
    return frozenset(
        stmt.value.id
        for stmt in node.body
        if isinstance(stmt, vy_ast.Expr) and isinstance(stmt.value, vy_ast.Name)
    )


def check_flag_value_access(
    node: vy_ast.TopLevel, declarations: dict, errors: ExceptionList
) -> None:
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


_NON_VARIABLE_DECLARATION_TYPES = (vy_ast.StructDef, vy_ast.InterfaceDef, vy_ast.TemplateDef)

_LANGUAGE_BUILTIN_NAMES = frozenset({"len", "ceil", "floor", "range"})


def known_global_names(modules) -> frozenset:
    from forge.builtins import collect_daml_builtins

    names = set(daml_builtin_type_names())
    for module in _scope_modules(modules):
        names |= ImportsBuilder.imported_names(module)
        for node in module.body:
            if isinstance(node, vy_ast.FunctionDef):
                names.add(node.name)
            elif isinstance(node, vy_ast.VariantDef):
                names.update(fn.name for fn in node.body if isinstance(fn, vy_ast.FunctionDef))
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


_CONSTRUCTIBLE_DECLARATION_TYPES = (vy_ast.StructDef, vy_ast.TemplateDef)


def check_unresolved_names(
    node: vy_ast.TopLevel, declarations: dict, global_names: frozenset, errors: ExceptionList
) -> None:
    fns = (
        [node] if isinstance(node, vy_ast.FunctionDef) else node.get_descendants(vy_ast.FunctionDef)
    )
    enclosing_fields = {
        stmt.target.id
        for stmt in getattr(node, "body", ())
        if isinstance(node, vy_ast.TemplateDef)
        and isinstance(stmt, vy_ast.AnnAssign)
        and isinstance(stmt.target, vy_ast.Name)
    }
    for fn in fns:
        local_names = _local_bound_names(fn) | enclosing_fields
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

        for call in fn.get_descendants(vy_ast.Call):
            if not isinstance(call.func, vy_ast.Name):
                continue
            name = call.func.id
            if name in local_names or name in global_names:
                continue
            if isinstance(declarations.get(name), _CONSTRUCTIBLE_DECLARATION_TYPES):
                continue
            errors.append(
                DamlForgeException(
                    f"`{name}` is not defined - no function, import, or struct/template "
                    f"declaration named `{name}` exists in scope here",
                    call,
                    code=ErrorCodes.DF1219.value,
                )
            )


def known_function_param_types(modules) -> dict:
    types = {}
    for node in _scope_nodes(modules):
        if isinstance(node, vy_ast.FunctionDef):
            types[node.name] = tuple(
                lower_type(a.annotation) if a.annotation is not None else None
                for a in node.args.args
                if a.arg != "self"
            )
        elif isinstance(node, vy_ast.VariantDef):
            for constructor in node.body:
                if not isinstance(constructor, vy_ast.FunctionDef):
                    continue
                types[constructor.name] = tuple(
                    lower_type(a.annotation) if a.annotation is not None else None
                    for a in constructor.args.args
                    if a.arg != "self"
                )
    return types


def _calls_to_check(fn: vy_ast.FunctionDef, param_types: dict):
    decorator_call_ids = {id(d) for d in fn.decorator_list if isinstance(d, vy_ast.Call)}
    for call in fn.get_descendants(vy_ast.Call):
        if id(call) in decorator_call_ids:
            continue
        if not isinstance(call.func, vy_ast.Name) or call.keywords:
            continue
        expected_params = param_types.get(call.func.id)
        if expected_params is None:
            continue
        yield call, expected_params


def check_call_arity(node: vy_ast.TopLevel, param_types: dict, errors: ExceptionList) -> None:
    fns = (
        [node] if isinstance(node, vy_ast.FunctionDef) else node.get_descendants(vy_ast.FunctionDef)
    )
    for fn in fns:
        for call, expected_params in _calls_to_check(fn, param_types):
            expected = len(expected_params)
            actual = len(call.args)
            if actual == expected:
                continue
            errors.append(
                DamlForgeException(
                    f"`{call.func.id}(...)` called with {actual} argument"
                    f"{'' if actual == 1 else 's'}, but `{call.func.id}` takes {expected} "
                    f"argument{'' if expected == 1 else 's'}",
                    call,
                    code=ErrorCodes.DF1225.value,
                )
            )


def _render_type_ref(t: TypeRef) -> str:
    if not t.args:
        return t.name
    return f"{t.name}[{', '.join(_render_type_ref(a) for a in t.args)}]"


def _is_list_type_annotation(node) -> bool:
    return (
        isinstance(node, vy_ast.Subscript)
        and isinstance(node.value, vy_ast.Name)
        and node.value.id == "list"
    )


def known_list_returning_functions(modules) -> frozenset:
    names = set()
    for node in _scope_nodes(modules):
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
    fns = (
        [node] if isinstance(node, vy_ast.FunctionDef) else node.get_descendants(vy_ast.FunctionDef)
    )
    for fn in fns:
        _mark_list_subscripts_in_body(fn.body, list_returning_fns, set())


_UNMAPPABLE_PYTHON_TYPES = frozenset(
    {"bytes", "bytearray", "memoryview", "complex", "type", "object", "slice"}
)


def _walk_type_ref(
    type_ref: TypeRef, known_names: set, node, context: str, errors: ExceptionList
) -> None:
    if type_ref.name in _UNMAPPABLE_PYTHON_TYPES:
        errors.append(
            DamlForgeException(
                f"`{type_ref.name}` has no Daml equivalent and cannot be used as a "
                f"type ({context})",
                node,
                code=ErrorCodes.DF1222.value,
            )
        )
    elif type_ref.name not in known_names:
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
    _check_generic_policy(type_ref, node, context, errors)


def _check_generic_policy(type_ref: TypeRef, node, context: str, errors: ExceptionList) -> None:
    """Validate arity and container-specific Daml policies in one place."""

    spec = generic_spec(type_ref.name)
    if spec is not None:
        arity = len(type_ref.args)
        if not spec.min_arity <= arity <= spec.max_arity:
            expected = (
                str(spec.min_arity)
                if spec.min_arity == spec.max_arity
                else f"{spec.min_arity}..{spec.max_arity}"
            )
            errors.append(
                DamlForgeException(
                    f"`{type_ref.name}` expects {expected} type argument(s), got {arity} "
                    f"({context})",
                    node,
                    code=ErrorCodes.DF1229.value,
                )
            )
        if spec.ordered_key_position is not None and type_ref.args:
            key = type_ref.args[spec.ordered_key_position]
            if not type_is_ordered(key):
                errors.append(
                    DamlForgeException(
                        f"`{type_ref.name}` keys must be ordered Daml values; "
                        f"`{_render_type_ref(key)}` "
                        f"cannot be used as a key ({context})",
                        node,
                        code=ErrorCodes.DF1229.value,
                    )
                )
        if spec.ordered_element and type_ref.args and not type_is_ordered(type_ref.args[0]):
            element = type_ref.args[0]
            errors.append(
                DamlForgeException(
                    f"`{type_ref.name}` elements must be ordered Daml values; "
                    f"`{_render_type_ref(element)}` cannot be used as an element ({context})",
                    node,
                    code=ErrorCodes.DF1229.value,
                )
            )
    for arg in type_ref.args:
        _check_generic_policy(arg, node, context, errors)


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


def check_struct_type_annotations(
    node: vy_ast.StructDef, known_names: set, errors: ExceptionList
) -> None:
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
    from forge.builtins import collect_daml_builtins

    registry = dict(collect_daml_builtins().field_types)
    for node in _scope_nodes(modules):
        if isinstance(node, vy_ast.VariantDef):
            for constructor in node.body:
                if not isinstance(constructor, vy_ast.FunctionDef):
                    continue
                registry[constructor.name] = {
                    arg.arg: lower_type(arg.annotation)
                    for arg in constructor.args.args
                    if arg.arg != "self" and arg.annotation is not None
                }
            continue
        if not isinstance(node, (vy_ast.StructDef, vy_ast.TemplateDef)):
            continue
        fields = {}
        for stmt in node.body:
            if isinstance(stmt, vy_ast.AnnAssign) and isinstance(stmt.target, vy_ast.Name):
                fields[stmt.target.id] = lower_type(stmt.annotation)
        registry[node.name] = fields
    return registry


def known_return_types(modules, field_types: dict) -> dict:
    from forge.builtins import collect_daml_builtins

    types = {name: TypeRef(name) for name in field_types}
    types.update(collect_daml_builtins().function_return_types)
    for node in _scope_nodes(modules):
        if isinstance(node, vy_ast.FunctionDef) and node.returns is not None:
            types[node.name] = lower_type(node.returns)
        elif isinstance(node, vy_ast.VariantDef):
            types.update(
                {
                    constructor.name: TypeRef(node.name)
                    for constructor in node.body
                    if isinstance(constructor, vy_ast.FunctionDef)
                }
            )
    return types


def _infer_expr_type(
    expr, enclosing_type, local_types: dict, field_types: dict, return_types: dict
):
    if isinstance(expr, vy_ast.Call) and expr._metadata.get("datetime_now"):
        return TypeRef("Timestamp")
    if isinstance(expr, vy_ast.Call) and "datetime_combine_arguments" in expr._metadata:
        return TypeRef("Timestamp")
    if isinstance(expr, vy_ast.Call) and "fromtimestamp_argument" in expr._metadata:
        return TypeRef("Timestamp")
    if isinstance(expr, vy_ast.Call) and "date_arguments" in expr._metadata:
        return TypeRef("Date")
    if isinstance(expr, vy_ast.Call) and "timedelta_arguments" in expr._metadata:
        return TypeRef("RelTime")
    if isinstance(expr, vy_ast.BinOp) and expr._metadata.get("add_rel_time"):
        return TypeRef("Timestamp")
    if isinstance(expr, vy_ast.BinOp) and expr._metadata.get("sub_time"):
        return TypeRef("RelTime")
    if isinstance(expr, vy_ast.NameConstant) and expr.value is None:
        return TypeRef("None")
    if isinstance(expr, vy_ast.List):
        return TypeRef("list")
    if isinstance(expr, vy_ast.Tuple):
        return TypeRef("tuple")
    if isinstance(expr, (vy_ast.Int, vy_ast.Decimal, vy_ast.Str, vy_ast.NameConstant)):
        return TypeRef(type(expr).__name__)
    if isinstance(expr, (vy_ast.BinOp, vy_ast.BoolOp, vy_ast.UnaryOp, vy_ast.Compare)):
        return TypeRef(type(expr).__name__)
    if isinstance(expr, vy_ast.Name):
        return local_types.get(expr.id)
    if isinstance(expr, vy_ast.Attribute):
        if isinstance(expr.value, vy_ast.Name) and expr.value.id == "self":
            base_type_name = enclosing_type
        else:
            base_type = _infer_expr_type(
                expr.value, enclosing_type, local_types, field_types, return_types
            )
            base_type_name = base_type.name if base_type is not None else None
        if base_type_name is None:
            return None
        return field_types.get(base_type_name, {}).get(expr.attr)
    if isinstance(expr, vy_ast.Call) and isinstance(expr.func, vy_ast.Name):
        fn = expr.func.id
        if fn == "fetch" and expr.args:
            cid_type = _infer_expr_type(
                expr.args[0], enclosing_type, local_types, field_types, return_types
            )
            if cid_type is not None and cid_type.name == "ContractId" and cid_type.args:
                return cid_type.args[0]
            return None
        if fn == "create" and expr.args:
            payload_type = _infer_expr_type(
                expr.args[0], enclosing_type, local_types, field_types, return_types
            )
            return TypeRef("ContractId", (payload_type,) if payload_type is not None else ())
        return return_types.get(fn)
    return None


def _functions_and_enclosing_type(node: vy_ast.TopLevel):
    if isinstance(node, (vy_ast.TemplateDef, vy_ast.InterfaceDef)):
        functions = [n for n in node.body if isinstance(n, vy_ast.FunctionDef)]
        enclosing_type = node.name if isinstance(node, vy_ast.TemplateDef) else None
        return functions, enclosing_type
    if isinstance(node, vy_ast.FunctionDef):
        return [node], None
    return [], None


def _mark_dict_kind(value, target_type) -> None:
    if target_type is None or not isinstance(value, vy_ast.Dict):
        return
    from forge.builtins.maps import known_map_types

    if target_type.name in known_map_types():
        value._metadata["map_kind"] = target_type.name


def _call_constructor_name(func) -> "str | None":
    if isinstance(func, vy_ast.Name):
        return func.id
    if isinstance(func, vy_ast.Attribute):
        return func.attr
    return None


def _mark_call_optional_conversions(
    call, enclosing_type, local_types: dict, field_types: dict, return_types: dict
) -> None:
    constructor_name = _call_constructor_name(call.func)
    if constructor_name is not None and constructor_name in field_types:
        fields = field_types[constructor_name]
        for kw in call.keywords:
            field_type = fields.get(kw.arg)
            _mark_dict_kind(kw.value, field_type)
            if field_type is None or field_type.name != "Optional":
                continue
            value_type = _infer_expr_type(
                kw.value, enclosing_type, local_types, field_types, return_types
            )
            if value_type is not None and value_type.name not in ("Optional", "None"):
                kw.value._metadata["needs_some_wrap"] = True

    if (
        isinstance(call.func, vy_ast.Attribute)
        and call.func.attr == "append"
        and isinstance(call.func.value, vy_ast.Name)
        and len(call.args) == 1
    ):
        list_type = local_types.get(call.func.value.id)
        if list_type is not None and list_type.name == "list" and list_type.args:
            element_type = list_type.args[0]
            if element_type.name != "Optional":
                value_type = _infer_expr_type(
                    call.args[0], enclosing_type, local_types, field_types, return_types
                )
                if value_type is not None and value_type.name == "Optional":
                    call.args[0]._metadata["needs_from_some_unwrap"] = True


def _mark_expr_optional_conversions(
    expr, enclosing_type, local_types: dict, field_types: dict, return_types: dict
) -> None:
    if expr is None:
        return
    for binary in reversed(list(expr.get_descendants(vy_ast.BinOp, include_self=True))):
        if not isinstance(binary.op, (vy_ast.Add, vy_ast.Sub)):
            continue
        left_type = _infer_expr_type(
            binary.left, enclosing_type, local_types, field_types, return_types
        )
        right_type = _infer_expr_type(
            binary.right, enclosing_type, local_types, field_types, return_types
        )
        if isinstance(binary.op, vy_ast.Add) and (
            left_type is not None
            and left_type.name in ("Timestamp", "Time")
            and right_type is not None
            and right_type.name == "RelTime"
        ):
            binary._metadata["add_rel_time"] = True
        elif (
            isinstance(binary.op, vy_ast.Sub)
            and left_type is not None
            and left_type.name in ("Timestamp", "Time")
            and right_type is not None
            and right_type.name in ("Timestamp", "Time")
        ):
            binary._metadata["sub_time"] = True
    for call in expr.get_descendants(vy_ast.Call, include_self=True):
        _mark_call_optional_conversions(
            call, enclosing_type, local_types, field_types, return_types
        )


def _mark_stmts_optional_conversions(
    stmts, enclosing_type, local_types: dict, field_types: dict, return_types: dict, return_type
) -> None:
    for stmt in stmts:
        if isinstance(stmt, vy_ast.AnnAssign):
            _mark_expr_optional_conversions(
                stmt.value, enclosing_type, local_types, field_types, return_types
            )
            target_type = lower_type(stmt.annotation)
            _mark_dict_kind(stmt.value, target_type)
            if stmt.value is not None and target_type.name != "Optional":
                value_type = _infer_expr_type(
                    stmt.value, enclosing_type, local_types, field_types, return_types
                )
                if value_type is not None and value_type.name == "Optional":
                    stmt.value._metadata["needs_from_some_unwrap"] = True
            if isinstance(stmt.target, vy_ast.Name):
                local_types[stmt.target.id] = target_type
        elif isinstance(stmt, vy_ast.Assign):
            _mark_expr_optional_conversions(
                stmt.value, enclosing_type, local_types, field_types, return_types
            )
            if isinstance(stmt.target, vy_ast.Name):
                existing_type = local_types.get(stmt.target.id)
                _mark_dict_kind(stmt.value, existing_type)
                if existing_type is not None and existing_type.name == "Optional":
                    value_type = _infer_expr_type(
                        stmt.value, enclosing_type, local_types, field_types, return_types
                    )
                    if value_type is not None and value_type.name not in ("Optional", "None"):
                        stmt.value._metadata["needs_some_wrap"] = True
                elif existing_type is None:
                    value_type = _infer_expr_type(
                        stmt.value, enclosing_type, local_types, field_types, return_types
                    )
                    if value_type is not None:
                        local_types[stmt.target.id] = value_type
        elif isinstance(stmt, vy_ast.If):
            _mark_expr_optional_conversions(
                stmt.test, enclosing_type, local_types, field_types, return_types
            )
            body_types = dict(local_types)
            orelse_types = dict(local_types)
            _mark_stmts_optional_conversions(
                stmt.body, enclosing_type, body_types, field_types, return_types, return_type
            )
            _mark_stmts_optional_conversions(
                stmt.orelse, enclosing_type, orelse_types, field_types, return_types, return_type
            )
            for target_name, body_type in body_types.items():
                if local_types.get(target_name) == body_type:
                    continue
                if orelse_types.get(target_name) == body_type:
                    local_types[target_name] = body_type
        elif isinstance(stmt, vy_ast.For):
            _mark_expr_optional_conversions(
                stmt.iter, enclosing_type, local_types, field_types, return_types
            )
            body_types = dict(local_types)
            target = stmt.target.target if hasattr(stmt.target, "target") else stmt.target
            annotation = getattr(stmt.target, "annotation", None)
            if isinstance(target, vy_ast.Name) and annotation is not None:
                body_types[target.id] = lower_type(annotation)
            _mark_stmts_optional_conversions(
                stmt.body, enclosing_type, body_types, field_types, return_types, return_type
            )
        elif isinstance(stmt, vy_ast.Return):
            _mark_expr_optional_conversions(
                stmt.value, enclosing_type, local_types, field_types, return_types
            )
            _mark_dict_kind(stmt.value, return_type)
            if (
                stmt.value is not None
                and return_type is not None
                and return_type.name != "Optional"
            ):
                value_type = _infer_expr_type(
                    stmt.value, enclosing_type, local_types, field_types, return_types
                )
                if value_type is not None and value_type.name == "Optional":
                    stmt.value._metadata["needs_from_some_unwrap"] = True
        elif isinstance(stmt, vy_ast.Assert):
            _mark_expr_optional_conversions(
                stmt.test, enclosing_type, local_types, field_types, return_types
            )
            _mark_expr_optional_conversions(
                stmt.msg, enclosing_type, local_types, field_types, return_types
            )
        elif isinstance(stmt, vy_ast.Expr):
            _mark_expr_optional_conversions(
                stmt.value, enclosing_type, local_types, field_types, return_types
            )


def mark_optional_conversions(node: vy_ast.TopLevel, field_types: dict, return_types: dict) -> None:
    functions, enclosing_type = _functions_and_enclosing_type(node)
    for fn in functions:
        local_types = {}
        for arg in fn.args.args:
            if arg.arg == "self" or arg.annotation is None:
                continue
            local_types[arg.arg] = lower_type(arg.annotation)
        return_type = lower_type(fn.returns) if fn.returns is not None else None
        _mark_stmts_optional_conversions(
            fn.body, enclosing_type, local_types, field_types, return_types, return_type
        )
    if any(
        binary._metadata.get("add_rel_time") or binary._metadata.get("sub_time")
        for binary in node.get_descendants(vy_ast.BinOp, include_self=True)
    ):
        required = set(node.module_node._metadata.get("required_daml_modules", ()))
        required.add("DA.Time")
        node.module_node._metadata["required_daml_modules"] = tuple(sorted(required))


def check_container_type_annotations(
    node: vy_ast.TopLevel, known_names: set, errors: ExceptionList
) -> None:
    if isinstance(node, vy_ast.StructDef):
        check_struct_type_annotations(node, known_names, errors)
        return

    if isinstance(node, vy_ast.VariantDef):
        for constructor in node.body:
            if isinstance(constructor, vy_ast.FunctionDef):
                check_function_type_annotations(constructor, known_names, errors)
        return

    if isinstance(node, vy_ast.TemplateDef):
        check_template_field_type_annotations(node, known_names, errors)
    elif isinstance(node, vy_ast.InterfaceDef):
        check_interface_view_type_annotation(node, known_names, errors)

    if isinstance(node, (vy_ast.TemplateDef, vy_ast.InterfaceDef)):
        for stmt in node.body:
            if isinstance(stmt, vy_ast.FunctionDef):
                check_function_type_annotations(stmt, known_names, errors)
    elif isinstance(node, vy_ast.FunctionDef):
        check_function_type_annotations(node, known_names, errors)
