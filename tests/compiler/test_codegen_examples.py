from pathlib import Path

import pytest

from forge.ast.parse import parse_to_ast
from forge.codegen import generate_daml
from forge.ir import lower_module
from forge.semantics import analyze_module

EXAMPLES_ROOT = Path(__file__).resolve().parents[2] / "examples"
BATCHED_MARKERS_PROXY = (
    EXAMPLES_ROOT
    / "splice-util-batched-markers"
    / "daml"
    / "Splice"
    / "Util"
    / "FeaturedApp"
    / "batched_markers_proxy.vy"
)

EXAMPLE_FILES = [
    EXAMPLES_ROOT / "token_standard" / "token_standard.vy",
    EXAMPLES_ROOT / "crowd_loans" / "loan_terms.vy",
    EXAMPLES_ROOT / "crowd_loans" / "funding_campaign.py",
    EXAMPLES_ROOT / "basic" / "simple.vy",
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


def test_funding_campaign_example_import_exposure_matches_real_damlc_requirements():
    path = EXAMPLES_ROOT / "crowd_loans" / "funding_campaign.py"
    daml_source, _ = _full_pipeline(path)

    assert (
        "import Splice.Amulet (Amulet(..), LockedAmulet(..), LockedAmulet_UnlockV2(..))"
    ) in daml_source
    assert (
        "import Splice.AmuletRules (AppTransferContext(..), CreatedAmulet(..), "
        "Transfer(..), TransferInput(..), TransferOutput(..), "
        "createdAmuletToHolding, exerciseAppTransfer)"
    ) in daml_source
    assert "import Splice.Api.Token.HoldingV1 (Holding, InstrumentId(..))" in daml_source
    assert "import Splice.Expiry (TimeLock(..))" in daml_source
    assert (
        "import LoanTerms (LoanRewards(..), LoanTerms(..), LoanTracker(..), "
        "PeriodPayment(..), PeriodPaymentStatus(..))"
    ) in daml_source


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
    # real Daml folds, not a placeholder
    assert "TODO(damlforge)" not in daml_source
    assert "for-loop translation not yet supported" not in daml_source
    assert "foldl" in daml_source


def test_funding_campaign_example_translates_every_loop_for_real():
    path = EXAMPLES_ROOT / "crowd_loans" / "funding_campaign.py"
    daml_source, _ = _full_pipeline(path)

    assert "TODO(damlforge)" not in daml_source
    assert "for-loop translation not yet supported" not in daml_source
    assert "foldl" in daml_source


def test_batched_markers_assertion_loop_uses_all():
    daml_source, _ = _full_pipeline(BATCHED_MARKERS_PROXY)
    choice_body = daml_source.split("choice BatchedMarkersProxy_TestEqual", 1)[1].split(
        "choice BatchedMarkersProxy_CreateMarkersV2", 1
    )[0]

    assert "all (\\entry -> entry.weight >= (10.0 : Decimal)) parties" in choice_body
    assert "foldlA" not in choice_body


def test_simple_example_mutates_self_via_create_and_dict_via_map():
    path = EXAMPLES_ROOT / "basic" / "simple.vy"
    daml_source, _ = _full_pipeline(path)

    assert "TODO(damlforge)" not in daml_source
    assert "import DA.Map as Map" in daml_source
    assert "let self = this" in daml_source
    assert "Map.member" in daml_source
    assert "Map.insert" in daml_source
    assert "`elem`" not in daml_source
    assert "!!" not in daml_source
    # `SimpleTemplate_Mint` mutates self - its real Daml return type must reflect the new contract
    assert (
        "choice SimpleTemplate_Mint : (ContractId SimpleTemplate, ContractId SimpleTemplate)"
        in daml_source
    )
    # every self-rebind must mint a fresh SSA name (`_damlforge_selfN`), never
    # literally reusing `self` - real damlc rejects local `let X = f(X)` as
    # illegal recursion, even when `X` was originally bound by `this`
    assert "create _damlforge_self" in daml_source


def test_decimal_calls_render_as_daml_numeric_literals():
    path = EXAMPLES_ROOT / "token_standard" / "token_standard.vy"
    daml_source, _ = _full_pipeline(path)

    assert "Decimal(0)" not in daml_source
    assert "Decimal 0" not in daml_source
    assert "0.0" in daml_source
