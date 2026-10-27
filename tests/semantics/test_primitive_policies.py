# Copyright 2026 Noders Team
# Author: Artem Bogomaz <artembogomaz@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from decimal import Decimal

import pytest

from forge.ast import nodes as vy_ast
from forge.ast.parse import parse_to_ast
from forge.exceptions import DamlForgeException
from forge.models.error_codes import ErrorCodes
from forge.semantics import analyze_module
from forge.semantics.analysis.primitive_values import _constant_value


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


@pytest.mark.parametrize(
    "expr, valid",
    [
        ("2 ** 62", True),
        ("1 ** 99999999999", True),
        ("(-1) ** 99999999999", True),
        ("2 ** 64", False),
        ("2147483648 ** 2147483648", False),
        ("(-2) ** 99999999999", False),
    ],
)
def test_int_power_folding_is_bounded(expr, valid):
    source = f"def f() -> Int:\n    return {expr}\n"
    if valid:
        _analyze(source)
    else:
        _assert_policy_error(source)


@pytest.mark.parametrize("year", ["99999999999", "2147483648", "-99999999999"])
def test_date_with_oversized_year_is_a_policy_error(year):
    _assert_policy_error(
        f"from datetime import date\n\ndef f() -> date:\n    return date({year}, 1, 1)\n"
    )


@pytest.mark.parametrize(
    "expr, valid",
    [
        ("9223372036854775807 / 1", True),
        ("-9223372036854775807 / -1", True),
        ("-9223372036854775808 // 1", True),
        ("-9223372036854775808 // -1", False),
        ("-9223372036854775808 / -1", False),
    ],
)
def test_int_division_folding_is_exact(expr, valid):
    source = f"def f() -> Int:\n    return {expr}\n"
    if valid:
        _analyze(source)
    else:
        _assert_policy_error(source)


@pytest.mark.parametrize(
    "expr, expected",
    [
        ("-7 // 2", ("Int", -4)),
        ("-7 / 2", ("Int", -3)),
        ("-7.5 // 2.0", ("Decimal", Decimal("-4"))),
        ("7.5 // 2.0", ("Decimal", Decimal("3"))),
        ("1.0 / 3.0", ("Decimal", Decimal("0.3333333333"))),
        ("1.0 / 2048.0", ("Decimal", Decimal("0.0004882812"))),
        ("3.0 / 2048.0", ("Decimal", Decimal("0.0014648438"))),
        ("-2.0 / 3.0", ("Decimal", Decimal("-0.6666666667"))),
    ],
)
def test_division_folding_matches_daml(expr, expected):
    tree = parse_to_ast(f"x: constant(Int) = {expr}\n", module_path="t.vy", resolved_path="t.vy")
    assert _constant_value(tree.get_descendants(vy_ast.BinOp)[0]) == expected


@pytest.mark.parametrize(
    "expr, valid",
    [
        ("1.0 / 3.0", True),
        ("-7.5 // 2.0", True),
        ("2.0 / 2048.0", True),
        ("9999999999999999999999999999.0 // 0.1", False),
    ],
)
def test_decimal_division_folding_policy(expr, valid):
    source = f"def f() -> Decimal:\n    return {expr}\n"
    if valid:
        _analyze(source)
    else:
        _assert_policy_error(source)
