from decimal import Decimal as PyDecimal

from forge.models import ContractId, Decimal, GenMap, Int, Party, Text, TextMap


def test_party_wraps_and_returns_underlying_value():
    assert Party("Alice") == "Alice"


def test_text_wraps_and_returns_underlying_value():
    assert Text("hello") == "hello"


def test_int_wraps_and_returns_underlying_value():
    assert Int(5) == 5


def test_decimal_is_python_decimal():
    assert Decimal is PyDecimal


def test_contract_id_is_subscriptable_with_a_template_type():
    class Asset:
        pass

    assert ContractId[Asset] is not None


def test_text_map_is_subscriptable():
    assert TextMap[int] is not None


def test_gen_map_is_subscriptable():
    assert GenMap[str, int] is not None
