import pytest

from forge.ast.nodes import InstanceDef, InterfaceDef, TemplateDef
from forge.ast.parse import parse_to_ast
from forge.exceptions import SyntaxException


def _parse(source):
    return parse_to_ast(source, module_path="test.vy", resolved_path="test.vy")


def test_template_keyword_produces_template_def():
    module = _parse("template Asset:\n    owner: Party\n")

    template = module.body[0]

    assert isinstance(template, TemplateDef)
    assert template.name == "Asset"
    assert len(template.body) == 1


def test_instance_keyword_captures_base_interface():
    source = "interface Holding:\n    pass\ninstance AssetHoldingInstance(Holding):\n    pass\n"
    module = _parse(source)

    instance = module.body[1]

    assert isinstance(instance, InstanceDef)
    assert instance.name == "AssetHoldingInstance"
    assert [base.id for base in instance.bases] == ["Holding"]


def test_interface_keyword_captures_view_keyword_argument():
    module = _parse("interface Holding(view=HoldingView):\n    pass\n")

    interface = module.body[0]

    assert isinstance(interface, InterfaceDef)
    assert [kw.arg for kw in interface.keywords] == ["view"]
    assert interface.keywords[0].value.id == "HoldingView"


def test_bare_class_keyword_still_rejected():
    with pytest.raises(SyntaxException):
        _parse("class Asset:\n    pass\n")
