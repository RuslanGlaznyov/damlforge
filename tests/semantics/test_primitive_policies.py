import pytest

from forge.ast.parse import parse_to_ast
from forge.exceptions import DamlForgeException
from forge.models.error_codes import ErrorCodes
from forge.semantics import analyze_module


def _analyze(source: str) -> None:
    analyze_module(parse_to_ast(source, module_path="test.vy", resolved_path="test.vy"))


def _assert_policy_error(source: str) -> None:
    with pytest.raises(DamlForgeException) as exc_info:
        _analyze(source)
    assert exc_info.value.code == ErrorCodes.DF1229.value


def test_int_uses_daml_signed_64_bit_range():
    _analyze("def max_value() -> Int:\n    return 9223372036854775807\n")
    _assert_policy_error("def too_large() -> Int:\n    return 9223372036854775808\n")
    _assert_policy_error("def too_small() -> Int:\n    return -9223372036854775809\n")


def test_decimal_uses_numeric_10_policy():
    _analyze("def amount() -> Decimal:\n    return 9999999999999999999999999999.9999999999\n")
    _assert_policy_error("def too_precise() -> Decimal:\n    return 1.12345678901\n")


def test_text_accepts_unicode():
    _analyze('def greeting() -> Text:\n    return "こんにちは, мир"\n')


def test_datetime_and_reltime_bounds_are_checked():
    _assert_policy_error(
        "from datetime import date\n\n" "def invalid() -> date:\n" "    return date(10000, 1, 1)\n"
    )
    _assert_policy_error(
        "from datetime import date, datetime, time\n\n"
        "def invalid(value: date) -> datetime:\n"
        "    return datetime.combine(value, time(24, 0, 0))\n"
    )
    _assert_policy_error(
        "from datetime import timedelta\n\n"
        "def invalid() -> timedelta:\n"
        "    return timedelta(microseconds=9223372036854775808)\n"
    )


def test_generic_arity_is_a_semantic_error():
    _assert_policy_error("struct Invalid:\n" "    value: tuple[Int]\n")
    _assert_policy_error("struct Invalid:\n" "    value: GenMap[Text]\n")
