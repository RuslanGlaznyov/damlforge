from forge.ast import nodes as vy_ast
from forge.exceptions import ExceptionList
from forge.semantics.analysis.structure import _RecursionContext, check_container


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
    errors = ExceptionList()
    recursion_context = _RecursionContext(module_list)
    for module in module_list:
        for node in module.body:
            check_container(node, errors, recursion_context)
    errors.raise_if_not_empty()
