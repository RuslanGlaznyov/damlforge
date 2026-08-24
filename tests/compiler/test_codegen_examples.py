from pathlib import Path

import pytest

from forge.ast.parse import parse_to_ast
from forge.codegen import generate_daml
from forge.ir import lower_module
from forge.semantics import analyze_module

EXAMPLES_ROOT = Path(__file__).resolve().parents[2] / "examples"

EXAMPLE_FILES = [
    EXAMPLES_ROOT / "token_standard" / "token_standard.vy",
    EXAMPLES_ROOT / "crowd_loans" / "loan_terms.vy",
    EXAMPLES_ROOT / "crowd_loans" / "funding_campaign.vy",
]


def _full_pipeline(path):
    source = path.read_text()
    module = parse_to_ast(source, module_path=path.name, resolved_path=str(path))
    analyze_module(module)
    ir = lower_module(module)
    return generate_daml(ir)


@pytest.mark.parametrize("path", EXAMPLE_FILES, ids=lambda p: p.name)
def test_real_example_generates_daml_without_error(path):
    daml_source, source_map = _full_pipeline(path)

    assert daml_source
    assert isinstance(source_map["mappings"], list)
    assert len(source_map["mappings"]) > 0


def test_token_standard_example_generates_clean_daml_no_loop_placeholders():
    path = EXAMPLES_ROOT / "token_standard" / "token_standard.vy"
    daml_source, _ = _full_pipeline(path)

    assert "template SimpleHolding" in daml_source
    assert "template PendingTransfer" in daml_source
    assert "interface Holding" in daml_source
    assert "interface TransferInstruction" in daml_source
    # this example has no for-loops in any choice body - full real translation
    assert "TODO(damlforge)" not in daml_source


def test_loan_terms_example_translates_every_loop_for_real():
    path = EXAMPLES_ROOT / "crowd_loans" / "loan_terms.vy"
    daml_source, _ = _full_pipeline(path)

    # this example genuinely uses for-loops throughout - confirm they compile to
    # real recursive Daml helpers, not a placeholder
    assert "TODO(damlforge)" not in daml_source
    assert "for-loop translation not yet supported" not in daml_source
    assert "_damlforge_loop1" in daml_source


def test_funding_campaign_example_translates_every_loop_for_real():
    path = EXAMPLES_ROOT / "crowd_loans" / "funding_campaign.vy"
    daml_source, _ = _full_pipeline(path)

    assert "TODO(damlforge)" not in daml_source
    assert "for-loop translation not yet supported" not in daml_source
    assert "_damlforge_loop1" in daml_source


def test_decimal_calls_render_as_daml_numeric_literals():
    path = EXAMPLES_ROOT / "token_standard" / "token_standard.vy"
    daml_source, _ = _full_pipeline(path)

    assert "Decimal(0)" not in daml_source
    assert "Decimal 0" not in daml_source
    assert "0.0" in daml_source
