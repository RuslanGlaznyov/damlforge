from forge.ast import nodes as vy_ast
from forge.exceptions import ExceptionList
from forge.semantics.analysis.structure import check_container


def analyze_module(module: vy_ast.Module) -> None:
    errors = ExceptionList()
    for node in module.body:
        check_container(node, errors)
    errors.raise_if_not_empty()
