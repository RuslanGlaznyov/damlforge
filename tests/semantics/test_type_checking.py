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


def test_constructor_rejects_unknown_keyword_field():
    source = (
        "struct Terms:\n"
        "    label: Text\n\n"
        "def invalid() -> Terms:\n"
        '    return Terms(unknown="not a field")\n'
    )
    _assert_type_error(source, ErrorCodes.DF1226.value)


def test_function_keyword_arguments_are_type_checked():
    source = (
        "def takes_int(value: Int) -> Int:\n"
        "    return value\n\n"
        "def invalid() -> Int:\n"
        '    return takes_int(value="not an integer")\n'
    )
    _assert_type_error(source, ErrorCodes.DF1226.value)


def test_builtin_exercise_argument_count_is_checked():
    source = (
        "\n"
        "from forge.builtins.daml_lang import exercise\n\n"
        ""
        "def invalid(cid: ContractId[Int]) -> Int:\n"
        "    exercise(cid)\n"
        "    return 0\n"
    )
    _assert_type_error(source, ErrorCodes.DF1225.value)


def test_template_method_arguments_are_type_checked_on_attribute_calls():
    source = (
        "from forge.models import choice, template\n\n"
        "@template\n"
        "class Asset:\n"
        "    owner: Party\n"
        "    signatory: Party = owner\n\n"
        "    @choice(controller=owner, consuming=True)\n"
        "    def transfer(self, new_owner: Party) -> ContractId[Asset]:\n"
        "        return create(Asset(owner=new_owner))\n\n"
        "def invalid(cid: ContractId[Asset]) -> Int:\n"
        '    cid.transfer(new_owner="not a party")\n'
        "    return 0\n"
    )
    _assert_type_error(source, ErrorCodes.DF1226.value)


def test_contract_id_choice_attribute_call_is_checked_against_payload_type():
    source = (
        "from forge.models import choice, template\n"
        "from forge.builtins.daml_lang import exercise\n\n"
        "@template\n"
        "class Asset:\n"
        "    owner: Party\n"
        "    signatory: Party = owner\n\n"
        "    @choice(controller=owner, consuming=True)\n"
        "    def transfer(self, new_owner: Party) -> ContractId[Asset]:\n"
        "        return create(Asset(owner=new_owner))\n\n"
        "@template\n"
        "class Holder:\n"
        "    owner: Party\n"
        "    signatory: Party = owner\n\n"
        "    @choice(controller=owner, consuming=True)\n"
        "    def move(self, asset_cid: ContractId[Asset], new_owner: Party) -> ContractId[Asset]:\n"
        "        return exercise(asset_cid, asset_cid.transfer(new_owner=new_owner))\n"
    )

    _analyze(source)


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


@pytest.mark.parametrize(
    "exponent, valid",
    [("2", True), ("0", True), ("y", True), ("-1", False), ("-2147483648", False)],
)
def test_power_rejects_negative_literal_exponent(exponent, valid):
    source = f"def f(x: Int, y: Int) -> Int:\n    return x ** {exponent}\n"
    if valid:
        _analyze(source)
    else:
        _assert_type_error(source)


@pytest.mark.parametrize(
    "signature, body, valid",
    [
        ("(a: datetime, b: datetime) -> timedelta", "a - b", True),
        ("(a: datetime, b: datetime, d: timedelta) -> timedelta", "(a - b) + d", True),
        ("(d: timedelta, e: timedelta) -> timedelta", "d - e", True),
        ("(a: datetime, b: datetime, c: datetime) -> datetime", "c + (a - b)", True),
        ("(a: datetime, b: datetime) -> datetime", "a - b", False),
        ("(d: timedelta, n: Int) -> timedelta", "d - n", False),
    ],
)
def test_datetime_subtraction_yields_timedelta(signature, body, valid):
    source = (
        "from datetime import datetime, timedelta\n\n" f"def f{signature}:\n    return {body}\n"
    )
    if valid:
        _analyze(source)
    else:
        _assert_type_error(source)


@pytest.mark.parametrize(
    "signature, body, valid",
    [
        ("(a: datetime) -> datetime", "a - timedelta(seconds=1)", True),
        ("(a: datetime, d: timedelta) -> datetime", "a - d - d", True),
        ("(a: datetime, b: datetime, d: timedelta) -> timedelta", "(a - d) - b", True),
        ("(a: datetime, d: timedelta) -> timedelta", "a - d", False),
    ],
)
def test_datetime_minus_timedelta_yields_datetime(signature, body, valid):
    source = (
        "from datetime import datetime, timedelta\n\n" f"def f{signature}:\n    return {body}\n"
    )
    if valid:
        _analyze(source)
    else:
        _assert_type_error(source)
