from forge.ast import nodes as vy_ast
from forge.exceptions import ExceptionList
from forge.semantics.analysis.imports import ImportsBuilder
from forge.semantics.analysis.structure import _RecursionContext, check_container
from forge.semantics.analysis.types import (
    check_container_type_annotations,
    check_optional_field_construction,
    known_field_types,
    known_type_names,
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


def analyze_module(module: vy_ast.Module) -> None:
    analyze_modules([module])


def analyze_modules(modules) -> None:
    module_list = _iter_modules(modules)
    imports_builder = ImportsBuilder()
    for module in module_list:
        imports_builder.resolve_sibling_imports(module)

    errors = ExceptionList()
    recursion_context = _RecursionContext(module_list)
    type_names = known_type_names(module_list)
    field_types = known_field_types(module_list)
    for module in module_list:
        for node in module.body:
            check_container(node, errors, recursion_context)
            imports_builder.check_no_aliased_from_import(node, errors)
            imports_builder.check_import_names_resolve(node, errors)
            imports_builder.check_sibling_import_names_resolve(node, errors)
            check_container_type_annotations(node, type_names, errors)
            check_optional_field_construction(node, field_types, errors)
    errors.raise_if_not_empty()
