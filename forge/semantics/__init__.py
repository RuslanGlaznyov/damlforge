from forge.ast import nodes as vy_ast
from forge.exceptions import ExceptionList
from forge.semantics.analysis.imports import ImportsBuilder
from forge.semantics.analysis.structure import _RecursionContext, check_container
from forge.semantics.analysis.types import (
    check_call_argument_types,
    check_call_arity,
    check_container_type_annotations,
    check_flag_value_access,
    check_unresolved_names,
    known_declarations,
    known_field_types,
    known_function_param_types,
    known_global_names,
    known_list_returning_functions,
    known_return_types,
    known_type_names,
    mark_list_subscripts,
    mark_optional_conversions,
)


def _iter_modules(modules) -> list[vy_ast.Module]:
    if isinstance(modules, vy_ast.Module):
        return [modules]
    for attr in ("modules", "resolved_modules", "imported_modules"):
        candidates = getattr(modules, attr, None)
        if candidates is not None:
            return _iter_modules(candidates)
    if hasattr(modules, "values"):
        candidates = modules.values()
    else:
        try:
            candidates = iter(modules)
        except TypeError:
            return []
    return [module for module in candidates if isinstance(module, vy_ast.Module)]


def analyze_module(module: vy_ast.Module):
    return analyze_modules([module])


def analyze_modules(modules):
    module_list = _iter_modules(modules)
    imports_builder = ImportsBuilder()
    errors = ExceptionList()
    for module in module_list:
        imports_builder.resolve_imports(module, errors)

    recursion_context = _RecursionContext(module_list)
    type_names = known_type_names(module_list)
    field_types = known_field_types(module_list)
    return_types = known_return_types(module_list, field_types)
    declarations = known_declarations(module_list)
    list_returning_fns = known_list_returning_functions(module_list)
    global_names = known_global_names(module_list)
    function_param_types = known_function_param_types(module_list)
    for module in module_list:
        for node in module.body:
            check_container(node, errors, recursion_context)
            check_container_type_annotations(node, type_names, errors)
            check_flag_value_access(node, declarations, errors)
            mark_list_subscripts(node, list_returning_fns)
            check_unresolved_names(node, declarations, global_names, errors)
            check_call_arity(node, function_param_types, errors)
            check_call_argument_types(node, function_param_types, errors)
            mark_optional_conversions(node, field_types, return_types)
    errors.raise_if_not_empty()

    return imports_builder.graph
