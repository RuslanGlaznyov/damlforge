from forge.ast import nodes as vy_ast
from forge.exceptions import ExceptionList
from forge.semantics.analysis.imports import ImportGraph, ImportsBuilder
from forge.semantics.analysis.module import ModuleAnalyzer, RecursionAnalyzer


def analyze_module(module: vy_ast.Module) -> ImportGraph:
    errors = ExceptionList()
    imports_builder = ImportsBuilder()
    imports_builder.resolve_imports(module, errors)
    errors.raise_if_not_empty()

    ModuleAnalyzer(module, errors).analyze()
    RecursionAnalyzer(module, errors).analyze()
    errors.raise_if_not_empty()

    return imports_builder.graph
