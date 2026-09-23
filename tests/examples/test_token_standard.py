from pathlib import Path

from forge.ast.parse import parse_to_ast
from forge.semantics import analyze_module
from forge.ir import lower_module
from forge.codegen import generate_daml

EXAMPLE_PATH = (
    Path(__file__).resolve().parents[2] / "examples" / "token_standard" / "token_standard.vy"
)


def _parse_simple():
    source_path = Path(__file__).resolve().parents[2] / "examples" / "basic" / "simple.vy"
    source = source_path.read_text()
    return parse_to_ast(source, module_path="simple.vy", resolved_path=str(source_path))


def test_simple():
    module = _parse_simple()
    analyze_module(module)
    lowered = lower_module(module)
    source, map = generate_daml(lowered)
    assert source is not None
    assert map is not None
    assert "template SimpleTemplate" in source


def test_token_standard_example_declares_expected_containers():
    source = EXAMPLE_PATH.read_text()
    assert source is not None
    
    module = parse_to_ast(source, module_path="token_standard.vy", resolved_path=str(EXAMPLE_PATH))
    assert module is not None
    
    graph = analyze_module(module)
    assert graph is not None

    names_by_type = {}
    for node in module.body:
        if not hasattr(node, "name"):
            continue
        names_by_type.setdefault(type(node).__name__, []).append(node.name)

    assert names_by_type["InterfaceDef"] == ["Holding", "TransferInstruction"]
    assert names_by_type["TemplateDef"] == ["SimpleHolding", "PendingTransfer"]

    templates = [node for node in module.body if type(node).__name__ == "TemplateDef"]
    bases_by_name = {t.name: [b.id for b in t.bases] for t in templates}
    assert bases_by_name == {
        "SimpleHolding": ["Holding"],
        "PendingTransfer": ["TransferInstruction"],
    }
