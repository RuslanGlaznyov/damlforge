import pytest

from forge.ast.parse import parse_to_ast
from forge.exceptions import DamlForgeException
from forge.semantics import analyze_module
from forge.models.error_codes import ErrorCodes


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

RECURSION_SINGLE_FUNC = """
template RecursionTemplate:
    platform: Party
    developer: Party
    dso: Party

    signatory: list[Party] = [platform]

    def __init__(
        self,
        platform: Party,
        developer: Party,
        dso: Party
    ):
        self.platform = platform
        self.developer = developer
        self.dso = dso
    
    @choice(controller=[developer, platform], consuming=True)
    def recursion(self) -> bool:
        return self.recursion()
"""


def _choice_template(consuming_literal, observer_clause=""):
    return f"""
template Asset:
    owner: Party
    issuer: Party

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming={consuming_literal}{observer_clause})
    def transfer(new_owner: Party) -> bool:
        pass
"""


CHOICE_PRECONSUMING_ON_TEMPLATE_IS_ALLOWED = _choice_template('"preconsuming"')
CHOICE_POSTCONSUMING_ON_TEMPLATE_IS_ALLOWED = _choice_template('"postconsuming"')
CHOICE_STRING_CONSUMING_ON_TEMPLATE_IS_ALLOWED = _choice_template('"consuming"')
CHOICE_WITH_OBSERVER_IS_ALLOWED = _choice_template("True", ", observer=issuer")


CHOICE_PRECONSUMING_ON_INTERFACE = """
interface Holding(view=HoldingView):
    @choice(controller=owner, consuming="preconsuming")
    def archive_holding() -> bool:
        pass
"""


CHOICE_POSTCONSUMING_ON_INSTANCE = """
interface Holding(view=HoldingView):
    pass
instance AssetHoldingInstance(Holding):
    @choice(controller=owner, consuming="postconsuming")
    def archive_holding() -> bool:
        pass
"""


TEMPLATE_KEY_WITHOUT_MAINTAINER = """
template Asset:
    owner: Party
    asset_id: Text

    signatory: list[Party] = [owner]
    key: tuple[Party, Text] = (owner, asset_id)
"""


TEMPLATE_MAINTAINER_WITHOUT_KEY = """
template Asset:
    owner: Party
    asset_id: Text

    signatory: list[Party] = [owner]
    maintainer: list[Party] = [owner]
"""


TEMPLATE_KEY_WITH_MAINTAINER_IS_ALLOWED = """
template Asset:
    owner: Party
    asset_id: Text

    signatory: list[Party] = [owner]
    key: tuple[Party, Text] = (owner, asset_id)
    maintainer: list[Party] = [owner]
"""


TEMPLATE_WITHOUT_KEY_OR_MAINTAINER_IS_ALLOWED = """
template Asset:
    owner: Party

    signatory: list[Party] = [owner]
"""


def test_valid_template_passes():
    _analyze(VALID_TEMPLATE)


@pytest.mark.parametrize(
    "source",
    [
        LEDGER_EFFECT_MARKED_IS_ALLOWED,
        CHOICE_BODY_LEDGER_EFFECT_IS_ALLOWED,
        VIEW_IN_INTERFACE_IS_ALLOWED,
        CHOICE_PRECONSUMING_ON_TEMPLATE_IS_ALLOWED,
        CHOICE_POSTCONSUMING_ON_TEMPLATE_IS_ALLOWED,
        CHOICE_STRING_CONSUMING_ON_TEMPLATE_IS_ALLOWED,
        CHOICE_WITH_OBSERVER_IS_ALLOWED,
        TEMPLATE_KEY_WITH_MAINTAINER_IS_ALLOWED,
        TEMPLATE_WITHOUT_KEY_OR_MAINTAINER_IS_ALLOWED,
    ],
)
def test_valid_decorator_usage_passes(source):
    _analyze(source)


@pytest.mark.parametrize(
    "source,expected_code",
    [
        (TEMPLATE_MISSING_SIGNATORY, ErrorCodes.DF1201.value),
        (CHOICE_MISSING_CONTROLLER, ErrorCodes.DF1202.value),
        (CHOICE_MISSING_CONSUMING, ErrorCodes.DF1203.value),
        (CHOICE_NON_LITERAL_CONSUMING, ErrorCodes.DF1203.value),
        (LEDGER_EFFECT_WITH_ARGS, ErrorCodes.DF1204.value),
        (HIDDEN_LEDGER_EFFECT, ErrorCodes.DF1205.value),
        (VIEW_WITH_ARGS, ErrorCodes.DF1206.value),
        (VIEW_IN_TEMPLATE, ErrorCodes.DF1207.value),
        (CHOICE_PRECONSUMING_ON_INTERFACE, ErrorCodes.DF1208.value),
        (CHOICE_POSTCONSUMING_ON_INSTANCE, ErrorCodes.DF1208.value),
        (RECURSION_SINGLE_FUNC, ErrorCodes.DF1209.value),
        (TEMPLATE_KEY_WITHOUT_MAINTAINER, ErrorCodes.DF1210.value),
        (TEMPLATE_MAINTAINER_WITHOUT_KEY, ErrorCodes.DF1211.value),
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
