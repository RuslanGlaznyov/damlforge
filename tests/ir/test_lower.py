import pytest

from forge.ast.parse import parse_to_ast
from forge.ir import lower_module
from forge.ir.nodes import (
    Field,
    IRAssert,
    IRAssign,
    IRAttribute,
    IRBinOp,
    IRBoolOp,
    IRCall,
    IRCompare,
    IRConstant,
    IRDict,
    IRFor,
    IRIf,
    IRList,
    IRName,
    IRPass,
    IRReturn,
    IRSubscript,
    IRTuple,
    IRUnaryOp,
    TypeRef,
)
from forge.models.decorators import Consuming
from forge.semantics import analyze_module


def _lower(source):
    module = parse_to_ast(source, module_path="test.vy", resolved_path="test.vy")
    return lower_module(module)


def _analyze_and_lower(source):
    module = parse_to_ast(source, module_path="test.vy", resolved_path="test.vy")
    analyze_module(module)
    return lower_module(module)


def test_struct_lowers_to_fields_with_type_refs():
    ir = _lower("struct Point:\n    x: int128\n    y: Party\n")

    (point,) = ir.structs
    assert point.name == "Point"
    assert point.fields == (
        Field("x", TypeRef("int128")),
        Field("y", TypeRef("Party")),
    )


def test_flag_lowers_to_values():
    ir = _lower("flag Status:\n    PENDING\n    DONE\n")

    (status,) = ir.flags
    assert status.name == "Status"
    assert status.values == ("PENDING", "DONE")


def test_validated_flag_value_access_lowers_to_bare_name():
    ir = _analyze_and_lower(
        "flag Status:\n"
        "    PENDING\n"
        "    DONE\n\n"
        "def f() -> bool:\n"
        "    return Status.PENDING == Status.DONE\n"
    )

    (fn,) = ir.functions
    assert fn.body[0] == IRReturn(IRCompare(IRName("PENDING"), "==", IRName("DONE")))


def test_unvalidated_attribute_access_lowers_to_ir_attribute():
    ir = _lower(
        "def f(x: int128) -> bool:\n"
        "    return x.PENDING\n"
    )

    (fn,) = ir.functions
    assert fn.body[0] == IRReturn(IRAttribute(IRName("x"), "PENDING"))


def test_generic_type_ref_lowers_nested_subscripts():
    ir = _lower("struct Box:\n    items: Optional[list[Party]]\n")

    (box,) = ir.structs
    assert box.fields[0].type == TypeRef("Optional", (TypeRef("list", (TypeRef("Party"),)),))


def test_none_return_annotation_lowers_to_none_type_ref():
    ir = _lower("def f(x: int128) -> None:\n    pass\n")

    (fn,) = ir.functions
    assert fn.return_type == TypeRef("None")


def test_tuple_type_ref_lowers_multiple_args():
    ir = _lower("struct Box:\n    pair: tuple[Party, int128]\n")

    (box,) = ir.structs
    assert box.fields[0].type == TypeRef("tuple", (TypeRef("Party"), TypeRef("int128")))


def test_forward_ref_string_type_lowers_to_type_ref():
    ir = _lower(
        "template Asset:\n"
        "    owner: Party\n"
        "    signatory: list[Party] = [owner]\n"
        "    @choice(controller=owner, consuming=True)\n"
        "    def transfer(self, new_owner: Party) -> ContractId['Asset']:\n"
        "        pass\n"
    )

    (asset,) = ir.templates
    assert asset.choices[0].return_type == TypeRef("ContractId", (TypeRef("Asset"),))


def test_template_lowers_signatory_and_fields():
    ir = _lower("template Asset:\n    owner: Party\n    signatory: list[Party] = [owner]\n")

    (asset,) = ir.templates
    assert asset.name == "Asset"
    assert asset.fields == (Field("owner", TypeRef("Party")),)
    assert asset.signatory == IRList((IRName("owner"),))


def test_template_without_signatory_lowers_to_none():
    ir = _lower(
        "template Asset:\n"
        "    owner: Party\n"
        "    @choice(controller=owner, consuming=True)\n"
        "    def transfer(self, new_owner: Party) -> Party:\n"
        "        pass\n"
    )

    (asset,) = ir.templates
    assert asset.signatory is None


def test_template_lowers_ensure_and_excludes_it_from_fields():
    ir = _lower(
        "template Asset:\n"
        "    owner: Party\n"
        "    amount: Decimal\n"
        "    signatory: list[Party] = [owner]\n"
        "    ensure: bool = amount > Decimal(0)\n"
    )

    (asset,) = ir.templates
    assert asset.ensure == IRCompare(IRName("amount"), ">", IRCall(IRName("Decimal"), (IRConstant(0),)))
    assert asset.fields == (
        Field("owner", TypeRef("Party")),
        Field("amount", TypeRef("Decimal")),
    )


def test_template_without_ensure_lowers_to_none():
    ir = _lower("template Asset:\n    owner: Party\n    signatory: list[Party] = [owner]\n")

    (asset,) = ir.templates
    assert asset.ensure is None


def test_choice_lowers_controller_consuming_and_observer():
    ir = _lower(
        "template Asset:\n"
        "    owner: Party\n"
        "    issuer: Party\n"
        "    signatory: list[Party] = [owner]\n"
        "    @choice(controller=owner, consuming=True, observer=issuer)\n"
        "    def transfer(self, new_owner: Party) -> Party:\n"
        "        return new_owner\n"
    )

    (asset,) = ir.templates
    (transfer,) = asset.choices
    assert transfer.name == "transfer"
    assert transfer.controller == IRName("owner")
    assert transfer.consuming is Consuming.CONSUMING
    assert transfer.observer == IRName("issuer")
    assert transfer.args == (Field("new_owner", TypeRef("Party")),)
    assert transfer.return_type == TypeRef("Party")
    assert transfer.body == (IRReturn(IRName("new_owner")),)


def test_choice_consuming_string_variant_lowers():
    ir = _lower(
        "interface Holding(view=View):\n"
        "    @choice(controller=actors, consuming='nonconsuming')\n"
        "    def accept(self, actors: list[Party]) -> bool:\n"
        "        pass\n"
    )

    (holding,) = ir.interfaces
    assert holding.choices[0].consuming is Consuming.NON_CONSUMING


def test_interface_lowers_view_and_requires():
    ir = _lower(
        "interface Base:\n    pass\n"
        "interface Holding(Base, view=HoldingView):\n    pass\n"
    )

    holding = ir.interfaces[1]
    assert holding.name == "Holding"
    assert holding.view == TypeRef("HoldingView")
    assert holding.requires == ("Base",)


def test_instance_lowers_bases_and_choices():
    ir = _lower(
        "interface Holding:\n    pass\n"
        "instance AssetAsHolding(Holding):\n"
        "    @view\n"
        "    def get_view(self) -> Party:\n"
        "        pass\n"
    )

    (instance,) = ir.instances
    assert instance.name == "AssetAsHolding"
    assert instance.bases == ("Holding",)
    assert instance.choices[0].name == "get_view"
    assert instance.choices[0].controller is None
    assert instance.choices[0].consuming is None


def test_init_lowers_as_dedicated_function():
    ir = _lower(
        "template Asset:\n"
        "    owner: Party\n"
        "    signatory: list[Party] = [owner]\n"
        "    def __init__(self, owner: Party):\n"
        "        assert owner != None, 'owner required'\n"
        "        self.owner = owner\n"
    )

    (asset,) = ir.templates
    assert asset.init is not None
    assert asset.init.name == "__init__"
    assert asset.init.args == (Field("owner", TypeRef("Party")),)
    assert isinstance(asset.init.body[0], IRAssert)


def test_module_level_function_lowers_with_decorators():
    ir = _lower(
        "@ledger_effect\n"
        "def helper(x: int128) -> int128:\n"
        "    return x\n"
    )

    (fn,) = ir.functions
    assert fn.name == "helper"
    assert fn.decorators == ("ledger_effect",)
    assert fn.args == (Field("x", TypeRef("int128")),)
    assert fn.return_type == TypeRef("int128")


@pytest.mark.parametrize(
    "stmt_source,expected",
    [
        ("assert x, 'msg'", IRAssert(IRName("x"), IRConstant("msg"))),
        ("assert x", IRAssert(IRName("x"), None)),
        ("y = x", IRAssign(IRName("y"), IRName("x"))),
        ("y: int128 = x", IRAssign(IRName("y"), IRName("x"), TypeRef("int128"))),
        ("pass", IRPass()),
        ("return x", IRReturn(IRName("x"))),
        ("return", IRReturn(None)),
    ],
)
def test_statement_lowering(stmt_source, expected):
    source = f"def f(x: int128) -> int128:\n    {stmt_source}\n"
    ir = _lower(source)
    (fn,) = ir.functions
    assert fn.body[0] == expected


def test_if_statement_lowers_body_and_orelse():
    ir = _lower(
        "def f(x: int128) -> int128:\n"
        "    if x > 0:\n"
        "        return x\n"
        "    else:\n"
        "        return 0\n"
    )
    (fn,) = ir.functions
    stmt = fn.body[0]
    assert isinstance(stmt, IRIf)
    assert stmt.test == IRCompare(IRName("x"), ">", IRConstant(0))
    assert stmt.body == (IRReturn(IRName("x")),)
    assert stmt.orelse == (IRReturn(IRConstant(0)),)


def test_for_statement_lowers_target_type_and_body():
    ir = _lower(
        "def f(xs: list[int128]) -> int128:\n"
        "    for item: int128 in xs:\n"
        "        return item\n"
        "    return 0\n"
    )
    (fn,) = ir.functions
    stmt = fn.body[0]
    assert isinstance(stmt, IRFor)
    assert stmt.target == "item"
    assert stmt.target_type == TypeRef("int128")
    assert stmt.iter == IRName("xs")
    assert stmt.body == (IRReturn(IRName("item")),)


@pytest.mark.parametrize(
    "expr_source,expected",
    [
        ("x", IRName("x")),
        ("x.y", IRAttribute(IRName("x"), "y")),
        ("x[0]", IRSubscript(IRName("x"), IRConstant(0))),
        ("f(x, y=1)", IRCall(IRName("f"), (IRName("x"),), (("y", IRConstant(1)),))),
        ("True", IRConstant(True)),
        ("None", IRConstant(None)),
        ("42", IRConstant(42)),
        ("[x, y]", IRList((IRName("x"), IRName("y")))),
        ("(x, y)", IRTuple((IRName("x"), IRName("y")))),
        ("{}", IRDict((), ())),
        ("x + y", IRBinOp("+", IRName("x"), IRName("y"))),
        ("x and y", IRBoolOp("and", (IRName("x"), IRName("y")))),
        ("not x", IRUnaryOp("not", IRName("x"))),
        ("x == y", IRCompare(IRName("x"), "==", IRName("y"))),
        ("x != y", IRCompare(IRName("x"), "!=", IRName("y"))),
        ("x in y", IRCompare(IRName("x"), "in", IRName("y"))),
    ],
)
def test_expression_lowering(expr_source, expected):
    source = f"def f(x: int128, y: int128) -> int128:\n    return {expr_source}\n"
    ir = _lower(source)
    (fn,) = ir.functions
    assert fn.body[0] == IRReturn(expected)
