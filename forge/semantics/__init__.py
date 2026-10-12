from forge.ast import nodes as vy_ast
from forge.builtin_stubs import scope_of, stub_scope
from forge.exceptions import ExceptionList
from forge.semantics.analysis.imports import ImportGraph, ImportsBuilder
from forge.semantics.analysis.module import ModuleAnalyzer, RecursionAnalyzer


def analyze_module(module: vy_ast.Module) -> ImportGraph:
    scope = scope_of(module)
    module._metadata["stub_scope"] = scope
    with stub_scope(scope):
        return _analyze_module(module)


def _analyze_module(module: vy_ast.Module) -> ImportGraph:
    errors = ExceptionList()
    imports_builder = ImportsBuilder()
    imports_builder.resolve_imports(module, errors)
    errors.raise_if_not_empty()

    ModuleAnalyzer(module, errors).analyze()
    RecursionAnalyzer(module, errors).analyze()
    errors.raise_if_not_empty()

    return imports_builder.graph
