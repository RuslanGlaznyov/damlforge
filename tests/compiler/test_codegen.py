import pytest

from forge.codegen.emit import generate_daml, render_body, render_expr, render_stmt, render_type
from forge.ir.nodes import (
    Field,
    IRAssert,
    IRAssign,
    IRAttribute,
    IRBinOp,
    IRBoolOp,
    IRCall,
    IRChoice,
    IRCompare,
    IRConstant,
    IRExprStmt,
    IRFlag,
    IRFor,
    IRIf,
    IRInterface,
    IRList,
    IRModule,
    IRName,
    IRPass,
    IRReturn,
    IRStruct,
    IRSubscript,
    IRTemplate,
    IRTuple,
    IRUnaryOp,
    TypeRef,
)
from forge.models.decorators import Consuming


@pytest.mark.parametrize(
    "type_ref,expected",
    [
        (TypeRef("Party"), "Party"),
        (TypeRef("Text"), "Text"),
        (TypeRef("int"), "Int"),
        (TypeRef("bool"), "Bool"),
        (TypeRef("None"), "()"),
        (TypeRef("list", (TypeRef("Party"),)), "[Party]"),
        (TypeRef("Optional", (TypeRef("Party"),)), "Optional Party"),
        (TypeRef("ContractId", (TypeRef("Asset"),)), "ContractId Asset"),
        (
            TypeRef("Optional", (TypeRef("ContractId", (TypeRef("Asset"),)),)),
            "Optional (ContractId Asset)",
        ),
        (TypeRef("tuple", (TypeRef("Party"), TypeRef("Text"))), "(Party, Text)"),
        (TypeRef("TextMap", (TypeRef("Text"),)), "TextMap Text"),
        (TypeRef("GenMap", (TypeRef("Text"), TypeRef("int"))), "Map.Map Text Int"),
        (TypeRef("Asset"), "Asset"),
    ],
)
def test_render_type(type_ref, expected):
    assert render_type(type_ref) == expected


@pytest.mark.parametrize(
    "expr,expected",
    [
        (IRName("owner"), "owner"),
        (IRAttribute(IRName("holding"), "amount"), "holding.amount"),
        (IRConstant(True), "True"),
        (IRConstant(None), "None"),
        (IRConstant("hi"), '"hi"'),
        (IRConstant(5), "5"),
        (IRCompare(IRName("a"), "!=", IRName("b")), "a /= b"),
        (IRCompare(IRName("a"), "==", IRName("b")), "a == b"),
        (IRBoolOp("and", (IRName("a"), IRName("b"))), "a && b"),
        (IRBoolOp("or", (IRName("a"), IRName("b"))), "a || b"),
        (IRUnaryOp("not", IRName("a")), "not a"),
        (IRBinOp("+", IRName("a"), IRName("b")), "a + b"),
        (IRBinOp("+", IRConstant("a"), IRName("b")), '"a" <> b'),
        (IRBinOp("+", IRName("a"), IRConstant("b")), 'a <> "b"'),
        (IRBinOp("+", IRList((IRName("a"),)), IRName("b")), "[a] ++ b"),
        (IRBinOp("+", IRName("a"), IRList((IRName("b"),))), "a ++ [b]"),
        (IRSubscript(IRName("entry"), IRConstant(0)), "entry._1"),
        (IRSubscript(IRName("entry"), IRConstant(1)), "entry._2"),
        (IRCall(IRName("create"), (IRName("x"),)), "create x"),
        (
            IRCall(IRName("Asset"), (), (("owner", IRName("o")), ("amount", IRName("a")))),
            "Asset with owner = o, amount = a",
        ),
        (IRTuple((IRName("a"), IRName("b"))), "(a, b)"),
        (IRCall(IRName("Decimal"), (IRConstant(0),)), "(0.0 : Decimal)"),
        (IRCall(IRName("Decimal"), (IRConstant(5),)), "(5.0 : Decimal)"),
    ],
)
def test_render_expr(expr, expected):
    assert render_expr(expr) == expected


def test_render_expr_nested_generic_type_parenthesized():
    t = TypeRef("list", (TypeRef("tuple", (TypeRef("Party"), TypeRef("int"))),))
    assert render_type(t) == "[(Party, Int)]"


@pytest.mark.parametrize(
    "stmt,expected_lines",
    [
        (IRAssert(IRName("cond"), None), ["assert (cond)", "pure ()"]),
        (IRAssert(IRName("cond"), IRConstant("bad")), ['assertMsg "bad" (cond)', "pure ()"]),
        (IRAssign(IRName("x"), IRName("y")), ["let x = y", "pure ()"]),
        (IRReturn(IRName("x")), ["pure (x)"]),
        (IRReturn(None), ["pure ()"]),
        (IRPass(), ['error "damlforge: not implemented"']),
    ],
)
def test_render_stmt_simple(stmt, expected_lines):
    # a lone non-terminal statement still needs "what happens next" - here, the
    # implicit fall-off-the-end `pure ()` a real Daml `do`-block requires as its
    # final expression. `return` and `pass` (last two cases) are both terminal -
    # `error "..."` unifies with any type only as a do-block's OWN final
    # statement, so `pass` must stop the sequence exactly like `return` does,
    # never followed by a continuation that would make ITS type the real one.
    assert render_stmt(stmt, indent=0) == expected_lines


def test_render_stmt_if_else():
    stmt = IRIf(IRName("cond"), (IRReturn(IRConstant(True)),), (IRReturn(IRConstant(False)),))
    lines = render_stmt(stmt, indent=0)
    assert lines == ["if cond", "  then do", "    pure (True)", "  else do", "    pure (False)"]


def test_render_stmt_for_with_no_accumulators_and_no_effects_is_dropped():
    # a pure loop with no accumulator, no `return`, and no ledger effect has
    # no observable outcome at all - real damlc has no use for it, so it's
    # elided entirely rather than hoisting a dead top-level function.
    stmt = IRFor("item", TypeRef("Party"), IRName("xs"), (IRPass(),))
    hoisted = []
    lines = render_stmt(stmt, indent=0)
    joined = "\n".join(lines)
    assert "_damlforge_loop" not in joined
    assert hoisted == []


def test_render_stmt_for_with_single_assert_uses_all():
    # unlike a `pass`-only loop, a loop whose only content is `assert` has a
    # real, observable effect (it can abort the transaction) - it must never
    # be silently elided just because it has no accumulator.
    stmt = IRFor(
        "item",
        TypeRef("Party"),
        IRName("xs"),
        (IRAssert(IRConstant(True), IRConstant("must hold")),),
    )
    hoisted = []
    lines = render_body([stmt], indent=0, hoisted=hoisted)
    joined = "\n".join(lines)
    assert 'assertMsg "must hold" (all (\\item -> True) xs)' in joined
    assert "foldlA" not in joined
    assert hoisted == []


def test_render_stmt_for_with_multiple_asserts_uses_action_fold():
    stmt = IRFor(
        "item",
        TypeRef("Party"),
        IRName("xs"),
        (IRAssert(IRConstant(True)), IRAssert(IRConstant(False))),
    )
    joined = "\n".join(render_body([stmt], indent=0))

    assert "foldlA" in joined


def test_render_body_for_with_accumulator_uses_fold_and_fresh_binding():
    # `total` must already be bound (here, as if it were a choice/function
    # parameter) for a plain reassignment inside the loop to count as a real
    # loop-carried accumulator rather than a fresh per-iteration local.
    loop = IRFor(
        "item",
        TypeRef("Party"),
        IRName("xs"),
        (IRExprStmt(IRCall(IRAttribute(IRName("total"), "append"), (IRName("item"),))),),
    )
    hoisted = []
    lines = render_body(
        [loop, IRReturn(IRName("total"))], indent=0, known={"total"}, hoisted=hoisted
    )
    joined = "\n".join(lines)

    assert "foldl" in joined
    assert "\\total item ->" in joined
    assert hoisted == []

    # the post-loop rebind must mint a fresh SSA name for `total` rather than
    # reusing the original - real damlc rejects any local `let X = f(X)` as
    # illegal recursion, even when `X` was bound by a function parameter
    assert "let _damlforge_total2 =" in joined
    assert "pure (_damlforge_total2)" in joined


def test_if_without_branch_carried_values_does_not_create_continuation():
    stmt = IRIf(
        IRName("cond"),
        (IRAssert(IRConstant(True)),),
        (IRAssert(IRConstant(False)),),
    )
    lines = render_body([stmt, IRReturn(IRConstant(True))], indent=0)
    joined = "\n".join(lines)

    assert "_damlforge_cont" not in joined
    assert joined.endswith("pure (True)")


def test_generate_daml_struct():
    module = IRModule(structs=(IRStruct("Point", (Field("x", TypeRef("Party")),)),))
    source, _ = generate_daml(module)
    assert "data Point = Point" in source
    assert "x : Party" in source
    assert "deriving (Eq, Show, Serializable)" in source


def test_generate_daml_struct_with_no_derive_field_type_skips_deriving():
    module = IRModule(
        structs=(
            IRStruct(
                "Wrapper",
                (
                    Field(
                        "value",
                        TypeRef(
                            "list", (TypeRef("FAR.FeaturedAppRight_CreateActivityMarkerResult"),)
                        ),
                    ),
                ),
            ),
        )
    )
    source, _ = generate_daml(module)
    assert "data Wrapper = Wrapper" in source
    assert "value : [FAR.FeaturedAppRight_CreateActivityMarkerResult]" in source
    assert "deriving (Eq, Show)" not in source


def test_generate_daml_flag():
    module = IRModule(flags=(IRFlag("Status", ("PENDING", "DONE")),))
    source, _ = generate_daml(module)
    assert "data Status = PENDING | DONE" in source


def test_generate_daml_template_with_choice_and_source_map():
    choice = IRChoice(
        name="transfer",
        controller=IRName("owner"),
        consuming=Consuming.CONSUMING,
        observer=None,
        args=(Field("new_owner", TypeRef("Party")),),
        return_type=TypeRef("ContractId", (TypeRef("Asset"),)),
        body=(IRReturn(IRName("new_owner")),),
        src=None,
    )
    template = IRTemplate(
        name="Asset",
        fields=(Field("owner", TypeRef("Party")),),
        signatory=IRName("owner"),
        observer=None,
        ensure=None,
        init=None,
        choices=(choice,),
    )
    module = IRModule(templates=(template,))
    source, source_map = generate_daml(module)

    assert "template Asset" in source
    assert "signatory owner" in source
    assert "choice Transfer : ContractId Asset" in source
    assert "controller owner" in source
    assert "do" in source
    assert "pure (new_owner)" in source
    # no src was set on this hand-built fixture, so no mapping entries expected
    assert source_map["mappings"] == []


def test_generate_daml_choice_observer_precedes_controller():
    choice = IRChoice(
        name="transfer",
        controller=IRName("owner"),
        consuming=Consuming.CONSUMING,
        observer=IRName("issuer"),
        args=(Field("new_owner", TypeRef("Party")),),
        return_type=TypeRef("ContractId", (TypeRef("Asset"),)),
        body=(IRReturn(IRName("new_owner")),),
        src=None,
    )
    template = IRTemplate(
        name="Asset",
        fields=(Field("owner", TypeRef("Party")),),
        signatory=IRName("owner"),
        observer=None,
        ensure=None,
        init=None,
        choices=(choice,),
    )
    module = IRModule(templates=(template,))
    source, _ = generate_daml(module)

    observer_index = source.index("observer issuer")
    controller_index = source.index("controller owner")
    assert observer_index < controller_index


def test_generate_daml_interface_with_requires():
    choice = IRChoice(
        name="get_amount",
        controller=IRName("actors"),
        consuming=Consuming.NON_CONSUMING,
        observer=None,
        args=(),
        return_type=TypeRef("Decimal"),
        body=(IRPass(),),
    )
    interface = IRInterface(
        name="Holding",
        view=TypeRef("HoldingView"),
        requires=("Base",),
        keywords=(),
        choices=(choice,),
    )
    module = IRModule(interfaces=(interface,))
    source, _ = generate_daml(module)

    assert "interface Holding requires Base where" in source
    assert "viewtype HoldingView" in source
    assert "nonconsuming choice Get_amount : Decimal" in source
