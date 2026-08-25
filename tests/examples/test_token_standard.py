from pathlib import Path

from forge.ast.parse import parse_to_ast
from forge.semantics import analyze_module
from forge.ir import lower_module
from forge.codegen import generate_daml

EXAMPLE_PATH = (
    Path(__file__).resolve().parents[2] / "examples" / "token_standard" / "token_standard.vy"
)


def _parse_example():
    source = EXAMPLE_PATH.read_text()
    return parse_to_ast(
        source, module_path="token_standard.vy", resolved_path=str(EXAMPLE_PATH)
    )

def _parse_simple():
    source_path = Path(__file__).resolve().parents[2] / "examples" / "basic" / "simple.vy"
    source = source_path.read_text()
    return parse_to_ast(
        source, module_path="simple.vy", resolved_path=str(source_path)
    )

def test_token_standard_example_parses_and_passes_semantic_analysis():
    module = _parse_example()

    analyze_module(module)

def test_simple():
    module = _parse_simple()

    analyze_module(module)
    lowered = lower_module(module)
    source, map = generate_daml(lowered)
    print(source)

def test_token_standard_example_declares_expected_containers():
    module = _parse_example()

    names_by_type = {}
    for node in module.body:
        if not hasattr(node, "name"):
            continue
        names_by_type.setdefault(type(node).__name__, []).append(node.name)

    assert names_by_type["InterfaceDef"] == ["Holding", "TransferInstruction"]
    assert names_by_type["TemplateDef"] == ["SimpleHolding", "PendingTransfer"]
    assert names_by_type["InstanceDef"] == [
        "SimpleHoldingAsHolding",
        "PendingTransferAsTransferInstruction",
    ]
