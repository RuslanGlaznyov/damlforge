import pytest

from forge.ast.parse import parse_to_ast
from forge.codegen.emit import generate_daml
from forge.exceptions import CompilerPanic, DamlForgeException, SyntaxException
from forge.ir import lower_module
from forge.semantics import analyze_module


def _compile(source: str):
    module = parse_to_ast(source, module_path="fuzz.vy", resolved_path="fuzz.vy")
    analyze_module(module)
    ir = lower_module(module)
    return generate_daml(ir, "Fuzz")


def test_malformed_type_subscript_is_rejected_instead_of_crashing():
    with pytest.raises(Exception) as exc_info:
        _compile(
            "from forge.models import Party, template\n"
            "@template\n"
            "class Iou:\n"
            "    signatory: 9223372036854775807[Party] = [issuer]\n"
        )

    assert not isinstance(exc_info.value, CompilerPanic)
    assert "No builtin or user-defined type" in str(exc_info.value)


def test_literal_type_annotation_is_rejected_instead_of_crashing():
    with pytest.raises(Exception) as exc_info:
        _compile(
            "from forge.models import Party, template\n"
            "@template\n"
            "class Iou:\n"
            "    issuer: False\n"
        )

    assert not isinstance(exc_info.value, CompilerPanic)
    assert "No builtin or user-defined type" in str(exc_info.value)


def test_nested_attribute_type_annotation_is_rejected_instead_of_crashing():
    with pytest.raises(Exception) as exc_info:
        _compile(
            "from forge.models import ContractId, Party, template\n"
            "@template\n"
            "class Iou:\n"
            "    signatory: list[Party] = [issuer]\n"
            "    def Sum(self, cids: list[ContractId[Iou]]) -> x.y.z:\n"
            "        return verify(cids, self.issuer)\n"
        )

    assert not isinstance(exc_info.value, CompilerPanic)
    assert "No builtin or user-defined type" in str(exc_info.value)


def test_invalid_local_generic_type_is_rejected_before_lowering():
    with pytest.raises(Exception) as exc_info:
        _compile(
            "from forge.models import ContractId, Decimal, Party, choice, template\n"
            "@template\n"
            "class Iou:\n"
            "    owner: Party\n"
            "    signatory: list[Party] = [issuer]\n"
            "    @choice(controller=owner, consuming=False)\n"
            "    def Many(self, owners: list[Party]) -> list[ContractId[Iou]]:\n"
            "        cids: list[ContractId[1]] = []\n"
        )

    assert not isinstance(exc_info.value, CompilerPanic)
    assert "No builtin or user-defined type" in str(exc_info.value)


def test_bad_indentation_is_reported_as_syntax_error():
    with pytest.raises(SyntaxException):
        parse_to_ast("            total = total + x\n    issuer: Party\n")


def test_loop_accumulator_with_early_return_is_reported_as_unsupported():
    with pytest.raises(DamlForgeException, match="loop-carried accumulator"):
        _compile(
            "from forge.models import ContractId, Party, choice, template\n"
            "@template\n"
            "class Iou:\n"
            "    owner: Party\n"
            "    signatory: list[Party] = [issuer]\n"
            "    @choice(controller=owner, consuming=False)\n"
            "    def Count(self, cids: list[ContractId[Iou]]) -> int:\n"
            "        n = 0\n"
            "        for c in cids:\n"
            "            if c == c:\n"
            "                return n\n"
            "            n = n + 1\n"
        )


def test_import_inside_function_is_rejected_before_lowering():
    with pytest.raises(Exception) as exc_info:
        _compile(
            "from forge.models import ContractId, Party, choice, template\n"
            "@template\n"
            "class Iou:\n"
            "    owner: Party\n"
            "    signatory: list[Party] = [issuer]\n"
            "    @choice(controller=owner, consuming=False)\n"
            "    def Many(self, owners: list[Party]) -> list[ContractId[Iou]]:\n"
            "        import os\n"
        )

    assert not isinstance(exc_info.value, CompilerPanic)
    assert "only supported at module scope" in str(exc_info.value)


def test_continue_is_rejected_before_lowering():
    with pytest.raises(DamlForgeException, match="`continue` is not supported"):
        _compile(
            "from forge.models import Decimal, Party, ledger_effect, template\n"
            "@ledger_effect\n"
            "def verify(cids: list[Party], p: Party) -> Decimal:\n"
            "    continue\n"
            "@template\n"
            "class Iou:\n"
            "    signatory: list[Party] = [issuer]\n"
        )


def test_raise_is_rejected_before_lowering():
    with pytest.raises(DamlForgeException, match="`raise` is not supported"):
        _compile(
            "from forge.models import ContractId, Decimal, Party, choice, template\n"
            "@template\n"
            "class Iou:\n"
            "    owner: Party\n"
            "    signatory: list[Party] = [issuer]\n"
            "    @choice(controller=owner, consuming=False)\n"
            "    def Many(self, owners: list[Party]) -> list[ContractId[Iou]]:\n"
            "        raise\n"
        )


def test_nested_function_is_rejected_before_lowering():
    with pytest.raises(DamlForgeException, match="Nested function definitions"):
        _compile(
            "from forge.models import Decimal, Party, ledger_effect, template\n"
            "@ledger_effect\n"
            "def verify(cids: list[Party], p: Party) -> Decimal:\n"
            "    def Count(self, cids: list[Party]) -> int:\n"
            "        return 0\n"
            "@template\n"
            "class Iou:\n"
            "    signatory: list[Party] = [issuer]\n"
        )


def test_non_name_template_field_target_is_rejected_without_attribute_error():
    with pytest.raises(Exception) as exc_info:
        _compile(
            "from forge.models import Party, template\n"
            "@template\n"
            "class Iou:\n"
            "    signatory: list[Party] = [issuer]\n"
            "    tuple[int, str]: Party\n"
        )

    assert not isinstance(exc_info.value, AttributeError)


def test_missing_annotation_only_module_is_reported_as_damlforge_error():
    with pytest.raises(DamlForgeException, match="No module named `forge.Iou`"):
        _compile(
            "from forge.Iou import Decimal, Party, choice, template\n"
            "@template\n"
            "class Iou:\n"
            "    issuer: Party\n"
        )


def test_malformed_for_syntax_is_reported_as_syntax_error():
    with pytest.raises(SyntaxException, match="Invalid for-loop syntax"):
        parse_to_ast("    for row for rows:\n        for x in row:\n")


def test_unsupported_bitwise_operator_is_rejected_before_lowering():
    with pytest.raises(DamlForgeException, match="operator `&` is not supported"):
        _compile(
            "from forge.models import Decimal\n"
            "def total_of(xs: list[Decimal]) -> Decimal:\n"
            "    total = total & x\n"
        )


def test_comprehension_like_for_syntax_is_reported_as_syntax_error():
    with pytest.raises(SyntaxException, match="Invalid for-loop syntax"):
        parse_to_ast(
            "from forge.models import Party, template\n"
            "@template\n"
            "class Iou:\n"
            "    if i.amount > [x for x in xs](1):\n"
            "        n = n + 1\n"
        )


def test_annotation_only_local_does_not_reach_codegen_as_none():
    daml, _ = _compile(
        "from forge.models import Decimal, Party, ledger_effect, template\n"
        "@ledger_effect\n"
        "def verify(cids: list[Party], p: Party) -> Decimal:\n"
        "    issuer: Party\n"
    )

    assert "let issuer =" not in daml
