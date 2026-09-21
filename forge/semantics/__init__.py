from forge.ast import nodes as vy_ast
from forge.exceptions import ExceptionList
from forge.semantics.analysis.imports import ImportGraph, ImportsBuilder
from forge.semantics.analysis.structure import (
    _RecursionContext,
    check_container,
)
from forge.semantics.analysis.types import (
    check_call_argument_types,
    check_call_arity,
    check_container_type_annotations,
    check_flag_value_access,
    check_unresolved_names,
    ModuleScope,
    mark_list_subscripts,
    mark_optional_conversions,
)


def analyze_module(module: vy_ast.Module) -> ImportGraph:
    errors = ExceptionList()
    imports_builder = ImportsBuilder()
    imports_builder.resolve_imports(module, errors)
    errors.raise_if_not_empty()
    
    for graph_module in imports_builder.graph:
        scope = ModuleScope(graph_module)
        recursion_context = _RecursionContext([graph_module])
        for node in graph_module.body:
            check_container(node, errors, recursion_context, scope.declarations)
            check_container_type_annotations(node, scope.type_names, errors)
            check_flag_value_access(node, scope.declarations, errors)
            mark_list_subscripts(node, scope.list_returning_functions)
            check_unresolved_names(node, scope.declarations, scope.global_names, errors)
            check_call_arity(node, scope.function_param_types, errors)
            check_call_argument_types(node, scope.function_param_types, errors)
            mark_optional_conversions(node, scope.field_types, scope.return_types)
    errors.raise_if_not_empty()

    return imports_builder.graph
