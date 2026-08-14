import pytest

from forge.ast.parse import parse_to_ast
from forge.exceptions import DamlForgeException
from forge.semantics import analyze_module


def _analyze(source):
    module = parse_to_ast(source, module_path="test.vy", resolved_path="test.vy")
    analyze_module(module)


VALID_TEMPLATE = """
template Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def transfer(new_owner: Party) -> bool:
        pass
"""


TEMPLATE_MISSING_SIGNATORY = """
template Asset:
    owner: Party

    @choice(controller=owner, consuming=True)
    def transfer(new_owner: Party) -> bool:
        pass
"""


CHOICE_MISSING_CONTROLLER = """
template Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @choice(consuming=True)
    def transfer(new_owner: Party) -> bool:
        pass
"""


CHOICE_MISSING_CONSUMING = """
template Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @choice(controller=owner)
    def transfer(new_owner: Party) -> bool:
        pass
"""


CHOICE_NON_LITERAL_CONSUMING = """
template Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=owner)
    def transfer(new_owner: Party) -> bool:
        pass
"""


LEDGER_EFFECT_WITH_ARGS = """
template Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @ledger_effect(True)
    def replace(new_owner: Party) -> bool:
        pass
"""


HIDDEN_LEDGER_EFFECT = """
template Asset:
    owner: Party

    signatory: list[Party] = [owner]

    def replace(new_owner: Party) -> bool:
        archive(self)
"""


LEDGER_EFFECT_MARKED_IS_ALLOWED = """
template Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @ledger_effect
    def replace(new_owner: Party) -> bool:
        archive(self)
"""


CHOICE_BODY_LEDGER_EFFECT_IS_ALLOWED = """
template Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def transfer(new_owner: Party) -> bool:
        archive(self)
"""


VIEW_WITH_ARGS = """
interface Holding(view=HoldingView):
    @view(True)
    def get_view() -> bool:
        pass
"""


VIEW_IN_TEMPLATE = """
template Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @view
    def get_view() -> bool:
        pass
"""


VIEW_IN_INTERFACE_IS_ALLOWED = """
interface Holding(view=HoldingView):
    @view
    def get_view() -> bool:
        pass
"""


def test_valid_template_passes():
    _analyze(VALID_TEMPLATE)


@pytest.mark.parametrize(
    "source",
    [LEDGER_EFFECT_MARKED_IS_ALLOWED, CHOICE_BODY_LEDGER_EFFECT_IS_ALLOWED, VIEW_IN_INTERFACE_IS_ALLOWED],
)
def test_valid_decorator_usage_passes(source):
    _analyze(source)


@pytest.mark.parametrize(
    "source,expected_code",
    [
        (TEMPLATE_MISSING_SIGNATORY, "DF1201"),
        (CHOICE_MISSING_CONTROLLER, "DF1202"),
        (CHOICE_MISSING_CONSUMING, "DF1203"),
        (CHOICE_NON_LITERAL_CONSUMING, "DF1203"),
        (LEDGER_EFFECT_WITH_ARGS, "DF1204"),
        (HIDDEN_LEDGER_EFFECT, "DF1205"),
        (VIEW_WITH_ARGS, "DF1206"),
        (VIEW_IN_TEMPLATE, "DF1207"),
    ],
)
def test_invalid_template_raises(source, expected_code):
    with pytest.raises(DamlForgeException) as exc_info:
        _analyze(source)

    assert exc_info.value.code == expected_code


def test_multiple_violations_are_all_reported():
    source = """
template Asset:
    owner: Party

    @choice(consuming=True)
    def transfer(new_owner: Party) -> bool:
        pass
"""
    with pytest.raises(Exception) as exc_info:
        _analyze(source)

    message = str(exc_info.value)
    assert "DF1201" in message
    assert "DF1202" in message
