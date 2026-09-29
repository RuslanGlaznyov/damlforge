import pytest

from forge.ast.nodes import EnumDef, InterfaceDef, NameConstant, TemplateDef, VariantDef
from forge.ast.parse import parse_to_ast
from forge.codegen import generate_daml
from forge.exceptions import SyntaxException
from forge.ir import lower_module
from forge.semantics import analyze_module


def _parse(source):
    return parse_to_ast(source, module_path="test.vy", resolved_path="test.vy")


def test_template_keyword_produces_template_def():
    module = _parse("@template\nclass Asset:\n    owner: Party\n")

    template = module.body[0]

    assert isinstance(template, TemplateDef)
    assert template.name == "Asset"
    assert len(template.body) == 1


def test_template_keyword_captures_base_interface():
    source = "interface Holding:\n    pass\n@template\nclass Asset(Holding):\n    owner: Party\n"
    module = _parse(source)

    template = module.body[1]

    assert isinstance(template, TemplateDef)
    assert template.name == "Asset"
    assert [base.id for base in template.bases] == ["Holding"]


def test_interface_keyword_captures_view_keyword_argument():
    module = _parse("interface Holding(view=HoldingView):\n    pass\n")

    interface = module.body[0]

    assert isinstance(interface, InterfaceDef)
    assert [kw.arg for kw in interface.keywords] == ["view"]
    assert interface.keywords[0].value.id == "HoldingView"


def test_bare_class_keyword_still_rejected():
    with pytest.raises(SyntaxException):
        _parse("class Asset:\n    pass\n")


def test_python_enum_class_produces_enum_def():
    module = _parse(
        "from enum import Enum, auto\n\n"
        "class Status(Enum):\n"
        "    ACTIVE = auto()\n"
        "    CLOSED = auto()\n"
    )

    enum = module.body[1]

    assert isinstance(enum, EnumDef)
    assert enum.name == "Status"
    assert [stmt.target.id for stmt in enum.body] == ["ACTIVE", "CLOSED"]


def test_flag_keyword_is_rejected():
    with pytest.raises(SyntaxException):
        _parse("flag Status:\n    ACTIVE\n")


def test_interface_keyword_captures_requires_base_interfaces():
    source = (
        "interface MyInterface:\n    pass\n"
        "interface YourInterface:\n    pass\n"
        "interface OurInterface(MyInterface, YourInterface, view=EmptyView):\n    pass\n"
    )
    module = _parse(source)

    our_interface = module.body[2]

    assert isinstance(our_interface, InterfaceDef)
    assert [base.id for base in our_interface.bases] == ["MyInterface", "YourInterface"]
    assert [kw.arg for kw in our_interface.keywords] == ["view"]


def test_interface_method_declaration_parses_as_bare_annotation():
    module = _parse("interface Holding(view=HoldingView):\n    method1: Party\n")

    holding = module.body[0]
    method_decl = holding.body[0]

    assert method_decl.target.id == "method1"
    assert method_decl.value is None


def test_none_literal_is_accepted_for_optional_fields():
    module = _parse("@template\nclass Asset:\n    lock: Optional[Party] = None\n")

    template = module.body[0]
    assigned_value = template.body[0].value

    assert isinstance(assigned_value, NameConstant)
    assert assigned_value.value is None


def test_template_decorator_on_class_produces_template_def():
    module = _parse("@template\nclass Asset:\n    owner: Party\n")

    template = module.body[0]

    assert isinstance(template, TemplateDef)
    assert template.name == "Asset"
    assert len(template.body) == 1


def test_variant_decorator_on_class_produces_variant_def():
    module = _parse(
        "@variant\n"
        "class Result:\n"
        "    def Accepted(value: Party): pass\n"
        "    def Rejected(reason: str): pass\n"
    )

    variant = module.body[0]

    assert isinstance(variant, VariantDef)
    assert variant.name == "Result"
    assert [constructor.name for constructor in variant.body] == ["Accepted", "Rejected"]


def test_variant_keyword_is_rejected():
    with pytest.raises(SyntaxException):
        _parse("variant Result:\n    pass\n")


def test_bare_class_without_template_decorator_is_still_rejected():
    with pytest.raises(SyntaxException):
        _parse("class Asset:\n    owner: Party\n")


def test_class_with_unrelated_decorator_is_still_rejected():
    with pytest.raises(SyntaxException):
        _parse("@view\nclass Asset:\n    owner: Party\n")


def _compile_to_daml(source: str) -> str:
    module = parse_to_ast(source, module_path="test.vy", resolved_path="test.vy")
    import_graph = analyze_module(module)
    ir = lower_module(module, import_graph=import_graph)
    daml_source, _ = generate_daml(ir, module_name="Test")
    return daml_source


def test_template_decorator_on_class_compiles_identically_to_template_keyword():
    keyword_source = (
        "from forge.models import Party, choice\n\n"
        "@template\nclass Asset:\n"
        "    owner: Party\n\n"
        "    signatory: list[Party] = [owner]\n\n"
        "    @choice(controller=owner, consuming=True)\n"
        "    def transfer(self, new_owner: Party) -> bool:\n"
        "        pass\n"
    )
    decorator_source = (
        "from forge.models import Party, choice, template\n\n"
        "@template\n"
        "class Asset:\n"
        "    owner: Party\n\n"
        "    signatory: list[Party] = [owner]\n\n"
        "    @choice(controller=owner, consuming=True)\n"
        "    def transfer(self, new_owner: Party) -> bool:\n"
        "        pass\n"
    )

    assert _compile_to_daml(keyword_source) == _compile_to_daml(decorator_source)
