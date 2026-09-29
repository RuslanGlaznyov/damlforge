import pytest

from forge.ast.parse import parse_to_ast
from forge.exceptions import DamlForgeException
from forge.models.error_codes import ErrorCodes
from forge.semantics import analyze_module


def _analyze(source: str) -> None:
    module = parse_to_ast(source, module_path="test.vy", resolved_path="test.vy")
    analyze_module(module)


def _assert_type_error(source: str, code: str = ErrorCodes.DF1230.value) -> None:
    with pytest.raises(DamlForgeException) as exc_info:
        _analyze(source)
    assert code in str(exc_info.value)


def test_expected_type_flows_into_assignment_value():
    _analyze("def valid() -> Decimal:\n    amount: Decimal = 1\n    return amount\n")
    _assert_type_error(
        'def invalid() -> Int:\n    amount: Int = "not an integer"\n    return amount\n'
    )


def test_function_arguments_are_checked_left_to_right_against_signature():
    source = (
        "def takes_int(value: Int) -> Int:\n"
        "    return value\n\n"
        "def invalid() -> Int:\n"
        '    return takes_int("not an integer")\n'
    )
    _assert_type_error(source, ErrorCodes.DF1226.value)


def test_all_list_elements_share_one_expected_type():
    _analyze("def valid() -> list[Int]:\n    return [1, 2, 3]\n")
    _assert_type_error('def invalid() -> list[Int]:\n    return [1, "wrong"]\n')


def test_control_flow_condition_is_checked_as_bool():
    _assert_type_error(
        "def invalid() -> Int:\n" '    if "not a boolean":\n' "        return 1\n" "    return 0\n"
    )


def test_optional_parameter_uses_explicit_inference_conversion():
    _analyze(
        "def accepts(value: Optional[Int]) -> Int:\n"
        "    return 0\n\n"
        "def valid() -> Int:\n"
        "    return accepts(1)\n"
    )
