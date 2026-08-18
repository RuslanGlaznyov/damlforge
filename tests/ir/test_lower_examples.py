from pathlib import Path

import pytest

from forge.ast.parse import parse_to_ast
from forge.ir import lower_module
from forge.semantics import analyze_module

EXAMPLES_ROOT = Path(__file__).resolve().parents[2] / "examples"

EXAMPLE_FILES = [
    EXAMPLES_ROOT / "token_standard" / "token_standard.vy",
    EXAMPLES_ROOT / "crowd_loans" / "loan_terms.vy",
    EXAMPLES_ROOT / "crowd_loans" / "funding_campaign.vy",
]


@pytest.mark.parametrize("path", EXAMPLE_FILES, ids=lambda p: p.name)
def test_real_example_lowers_to_ir_without_error(path):
    source = path.read_text()
    module = parse_to_ast(source, module_path=path.name, resolved_path=str(path))
    analyze_module(module)

    lower_module(module)


def test_funding_campaign_invest_choice_lowers_correctly():
    path = EXAMPLES_ROOT / "crowd_loans" / "funding_campaign.vy"
    module = parse_to_ast(path.read_text(), module_path=path.name, resolved_path=str(path))
    analyze_module(module)
    ir = lower_module(module)

    (campaign,) = [t for t in ir.templates if t.name == "FundingCampaign"]
    (invest,) = [c for c in campaign.choices if c.name == "invest"]

    assert [f.name for f in invest.args] == [
        "investor",
        "inputs",
        "amount",
        "app_transfer_context",
    ]
    assert invest.return_type.name == "ContractId"
    assert invest.return_type.args[0].name == "FundingCampaign"
