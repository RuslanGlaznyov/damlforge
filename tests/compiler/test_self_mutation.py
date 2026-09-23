from forge.codegen.emit import generate_daml, render_expr
from forge.ir.nodes import (
    Field,
    IRAssign,
    IRAttribute,
    IRBinOp,
    IRChoice,
    IRCompare,
    IRConstant,
    IRIf,
    IRModule,
    IRName,
    IRRecordUpdate,
    IRReturn,
    IRSubscript,
    IRTemplate,
    TypeRef,
)
from forge.models.decorators import Consuming


def _template_with_choice(field_type, body, return_type=None):
    choice = IRChoice(
        name="mint",
        controller=IRName("owner"),
        consuming=Consuming.CONSUMING,
        observer=None,
        args=(),
        return_type=return_type,
        body=tuple(body),
    )
    template = IRTemplate(
        name="Asset",
        fields=(Field("owner", TypeRef("Party")), Field("balance", field_type)),
        signatory=IRName("owner"),
        observer=None,
        ensure=None,
        init=None,
        choices=(choice,),
    )
    return IRModule(templates=(template,))


def test_render_expr_record_update():
    e = IRRecordUpdate(IRName("self"), (("total", IRConstant(1)),))
    assert render_expr(e) == f"self {chr(123)} total = 1 {chr(125)}"


def test_self_field_assignment_becomes_record_update_and_synthesizes_create():
    body = [
        IRAssign(
            IRAttribute(IRName("self"), "balance"),
            IRBinOp("+", IRAttribute(IRName("self"), "balance"), IRConstant(1)),
        ),
        IRReturn(None),
    ]
    module = _template_with_choice(TypeRef("Decimal"), body)
    source, _ = generate_daml(module)

    assert "let self = this" in source
    assert f"self {chr(123)} balance = self.balance + 1 {chr(125)}" in source
    # `self` must be rebound to a fresh SSA name, never reused - real damlc
    # rejects any local `let X = f(X)` as illegal recursion
    assert "_damlforge_new_self <- create _damlforge_self1" in source
    assert "pure (_damlforge_new_self, ())" in source
    # no original return value declared -> augmented type is (ContractId Asset, ())
    assert "choice Mint : (ContractId Asset, ())" in source


def test_self_field_assignment_preserves_original_return_value():
    body = [
        IRAssign(IRAttribute(IRName("self"), "balance"), IRConstant(5)),
        IRReturn(IRConstant(True)),
    ]
    module = _template_with_choice(TypeRef("Decimal"), body, return_type=TypeRef("bool"))
    source, _ = generate_daml(module)

    assert "choice Mint : (ContractId Asset, Bool)" in source
    assert "pure (_damlforge_new_self, True)" in source


def test_dict_field_subscript_assignment_uses_map_insert():
    field_type = TypeRef("GenMap", (TypeRef("Party"), TypeRef("Decimal")))
    body = [
        IRAssign(IRSubscript(IRAttribute(IRName("self"), "balance"), IRName("k")), IRName("v")),
        IRReturn(None),
    ]
    module = _template_with_choice(field_type, body)
    source, _ = generate_daml(module)

    assert "import DA.Map as Map" in source
    assert f"self {chr(123)} balance = Map.insert k v self.balance {chr(125)}" in source


def test_dict_field_subscript_read_uses_map_lookup():
    field_type = TypeRef("GenMap", (TypeRef("Party"), TypeRef("Decimal")))
    body = [IRReturn(IRSubscript(IRAttribute(IRName("self"), "balance"), IRName("k")))]
    module = _template_with_choice(field_type, body, return_type=TypeRef("Decimal"))
    source, _ = generate_daml(module)

    assert "fromSome (Map.lookup k self.balance)" in source
    # no mutation happened here - no create/record-update machinery kicks in
    assert "create self" not in source
    assert "choice Mint : Decimal" in source


def test_dict_field_membership_uses_map_member_not_elem():
    field_type = TypeRef("GenMap", (TypeRef("Party"), TypeRef("Decimal")))
    body = [
        IRIf(
            IRCompare(IRName("k"), "in", IRAttribute(IRName("self"), "balance")),
            (IRReturn(IRConstant(True)),),
            (IRReturn(IRConstant(False)),),
        )
    ]
    module = _template_with_choice(field_type, body, return_type=TypeRef("bool"))
    source, _ = generate_daml(module)

    assert "Map.member k self.balance" in source
    assert "`elem`" not in source


def test_choice_without_self_mutation_is_unaffected():
    # `self` is always bound for a template choice (harmless if unused), but the
    # create-and-return-tuple augmentation only fires when self is actually
    # reassigned somewhere in the body.
    body = [IRReturn(IRConstant(True))]
    module = _template_with_choice(TypeRef("Decimal"), body, return_type=TypeRef("bool"))
    source, _ = generate_daml(module)

    assert "let self = this" in source
    assert "create self" not in source
    assert "choice Mint : Bool" in source
    assert "import DA.Map" not in source
