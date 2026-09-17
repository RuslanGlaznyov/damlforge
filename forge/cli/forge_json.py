from forge.ast.parse import parse_to_ast
from forge.semantics import analyze_module


def compile_json(input_vy: str) -> dict:
    ast = parse_to_ast(input_vy)
    analyze_module(ast)

    return ast.to_dict()
