import pytest

from forge.ast.parse import parse_to_ast
from forge.builtins import collect_daml_builtins
from forge.codegen import generate_daml
from forge.exceptions import DamlForgeException
from forge.ir import lower_module
from forge.semantics import analyze_module

_DECORATOR_PREAMBLE = (
    "from forge.models import choice, template, view\n"
    "from forge.builtins import DamlName\n"
    "from forge.builtins.daml_lang import (\n"
    "    coerce_interface_contract_id,\n"
    "    create,\n"
    "    exercise,\n"
    "    fetch,\n"
    "    from_interface_contract_id,\n"
    "    to_interface,\n"
    ")\n"
)


def _compile(source):
    module = parse_to_ast(
        _DECORATOR_PREAMBLE + source, module_path="test.vy", resolved_path="test.vy"
    )
    analyze_module(module)
    ir = lower_module(module)
    daml_source, _ = generate_daml(ir, module_name="Test")
    return daml_source


def test_collect_daml_builtins_includes_daml_lang_functions():
    function_renames = collect_daml_builtins().function_renames

    assert function_renames["from_interface_contract_id"] == "fromInterfaceContractId"
    assert function_renames["to_interface_contract_id"] == "toInterfaceContractId"
    assert function_renames["to_interface"] == "toInterface"
    assert function_renames["coerce_interface_contract_id"] == "coerceInterfaceContractId"
    assert "add_rel_time" not in function_renames
    assert "sub_time" not in function_renames
    assert "from_unix_microseconds" not in function_renames
    assert "get_time" not in function_renames
    assert "date" not in function_renames
    assert "january" not in function_renames
    assert "time" not in function_renames


def test_prelude_functions_need_no_import():
    function_import_modules = collect_daml_builtins().function_import_modules

    assert "fromInterfaceContractId" not in function_import_modules
    assert "toInterfaceContractId" not in function_import_modules
    assert "toInterface" not in function_import_modules
    assert "coerceInterfaceContractId" not in function_import_modules


def test_exercise_app_transfer_and_unlock_and_transfer_are_ledger_effects():
    ledger_effect_fns = collect_daml_builtins().ledger_effect_fns

    assert "exercise_app_transfer" in ledger_effect_fns
    assert "unlock_and_transfer" in ledger_effect_fns
    assert "from_interface_contract_id" not in ledger_effect_fns


def test_variant_constructor_functions_are_derived():
    constructor_of = collect_daml_builtins().constructor_of

    assert constructor_of["InputAmulet"] == "TransferInput"
    assert constructor_of["TransferResultAmulet"] == "CreatedAmulet"
    assert constructor_of["TransferResultLockedAmulet"] == "CreatedAmulet"
    assert constructor_of["BatchOfBatches"] == "Batch"
    assert constructor_of["BatchOfMintingAllowances"] == "Batch"


def test_constructor_types_include_explicitly_marked_types_and_variant_targets():
    constructor_types = collect_daml_builtins().constructor_types

    assert "AppTransferContext" in constructor_types
    assert "TransferOutput" in constructor_types
    assert "Transfer" in constructor_types
    assert "TransferInput" in constructor_types
    assert "CreatedAmulet" in constructor_types
    assert "Batch" in constructor_types
    assert "DamlName" not in constructor_types
    assert "BuiltinMetadata" not in constructor_types


def test_constructor_types_includes_every_dataclass_record():
    constructor_types = collect_daml_builtins().constructor_types

    assert "TimeLock" in constructor_types
    assert "LockedAmulet_UnlockV2" in constructor_types
    assert "Amulet" in constructor_types
    assert "InstrumentId" in constructor_types


def test_constructor_types_excludes_plain_interface_marker_classes():
    constructor_types = collect_daml_builtins().constructor_types

    assert "Holding" not in constructor_types


def test_from_interface_contract_id_renders_and_needs_no_extra_import():
    daml = _compile(
        "@template\nclass Asset:\n"
        "    owner: Party\n\n"
        "    signatory: list[Party] = [owner]\n\n"
        "    @choice(controller=owner, consuming=True)\n"
        "    def downcast(self, holding_cid) -> bool:\n"
        "        amulet_cid = from_interface_contract_id(holding_cid)\n"
        "        return True\n"
    )

    assert "fromInterfaceContractId" in daml
    assert "import DA.Time" not in daml


def test_to_interface_and_coerce_interface_contract_id_render_correctly():
    daml = _compile(
        "@template\nclass Asset:\n"
        "    owner: Party\n\n"
        "    signatory: list[Party] = [owner]\n\n"
        "    @choice(controller=owner, consuming=True)\n"
        "    def upcast(self, value, cid) -> bool:\n"
        "        as_interface = to_interface(value)\n"
        "        other_cid = coerce_interface_contract_id(cid)\n"
        "        return True\n"
    )

    assert "toInterface " in daml or "toInterface(" in daml
    assert "coerceInterfaceContractId" in daml


def test_python_datetime_plus_timedelta_lowers_to_add_rel_time():
    daml = _compile(
        "from datetime import datetime, timedelta\n\n"
        "@template\nclass Asset:\n"
        "    owner: Party\n"
        "    anchor: datetime\n\n"
        "    signatory: list[Party] = [owner]\n\n"
        "    @choice(controller=owner, consuming=True)\n"
        "    def bump(self, delta: timedelta) -> datetime:\n"
        "        return self.anchor + delta\n"
    )

    assert "addRelTime" in daml
    assert "import DA.Time" in daml


def test_python_datetime_subtraction_lowers_to_sub_time():
    daml = _compile(
        "from datetime import datetime, timedelta\n\n"
        "@template\nclass Asset:\n"
        "    owner: Party\n\n"
        "    signatory: list[Party] = [owner]\n\n"
        "    @choice(controller=owner, consuming=True)\n"
        "    def difference(self, later: datetime, earlier: datetime) -> timedelta:\n"
        "        return later - earlier\n"
    )

    assert "subTime" in daml
    assert "import DA.Time" in daml


def test_da_time_import_emitted_only_once_when_both_functions_used():
    daml = _compile(
        "from datetime import datetime, timedelta\n\n"
        "@template\nclass Asset:\n"
        "    owner: Party\n\n"
        "    signatory: list[Party] = [owner]\n\n"
        "    @choice(controller=owner, consuming=True)\n"
        "    def both(\n"
        "        self, t1: datetime, t2: datetime, delta: timedelta\n"
        "    ) -> bool:\n"
        "        diff = t1 - t2\n"
        "        bumped = t1 + delta\n"
        "        return True\n"
    )

    assert daml.count("import DA.Time") == 1


def test_python_timedelta_lowers_to_da_time_units():
    daml = _compile(
        "from datetime import timedelta\n\n"
        "def duration(count: int) -> timedelta:\n"
        "    return timedelta(days=count, hours=2, minutes=3)\n"
    )

    assert "duration : Int -> RelTime" in daml
    assert "days count" in daml
    assert "hours 2" in daml
    assert "minutes 3" in daml
    assert daml.count("import DA.Time") == 1
    assert "import datetime" not in daml


def test_qualified_python_timedelta_lowers_weeks_to_days():
    daml = _compile(
        "import datetime as dt\n\n"
        "def duration(count: int) -> dt.timedelta:\n"
        "    return dt.timedelta(weeks=count, seconds=4, milliseconds=5, microseconds=6)\n"
    )

    assert "duration : Int -> RelTime" in daml
    assert "days (count * 7)" in daml
    assert "seconds 4" in daml
    assert "milliseconds 5" in daml
    assert "microseconds 6" in daml
    assert daml.count("import DA.Time") == 1


def test_python_date_lowers_integer_month_to_daml_month():
    daml = _compile(
        "from datetime import date\n\n"
        "def build_date(year: int, month: int, day: int) -> date:\n"
        "    return date(year, month, day)\n"
    )

    assert "build_date : Int -> Int -> Int -> Date" in daml
    assert "date year (toEnum (month - 1)) day" in daml
    assert daml.count("import DA.Date") == 1
    assert "import datetime" not in daml


def test_qualified_python_date_lowers_literal_month_to_constructor():
    daml = _compile(
        "import datetime as dt\n\n"
        "def epoch() -> dt.date:\n"
        "    return dt.date(year=1970, month=1, day=1)\n"
    )

    assert "epoch : Date" in daml
    assert "date 1970 Jan 1" in daml
    assert daml.count("import DA.Date") == 1


def test_python_date_rejects_invalid_literal_month():
    with pytest.raises(DamlForgeException, match="month must be in 1..12"):
        _compile(
            "from datetime import date\n\n"
            "def invalid() -> date:\n"
            "    return date(2026, 13, 1)\n"
        )


def test_python_datetime_combine_lowers_to_daml_time():
    daml = _compile(
        "from datetime import date, datetime, time\n\n"
        "def at(value: date, hour: int) -> datetime:\n"
        "    return datetime.combine(value, time(hour, minute=2, second=3))\n"
    )

    assert "at : Date -> Int -> Time" in daml
    assert "time value hour 2 3" in daml
    assert daml.count("import DA.Time") == 1
    assert "import datetime" not in daml


def test_qualified_python_datetime_combine_uses_time_defaults():
    daml = _compile(
        "import datetime as dt\n\n"
        "def midnight(value: dt.date) -> dt.datetime:\n"
        "    return dt.datetime.combine(value, dt.time())\n"
    )

    assert "midnight : Date -> Time" in daml
    assert "time value 0 0 0" in daml
    assert daml.count("import DA.Time") == 1


def test_python_time_rejects_standalone_use():
    with pytest.raises(DamlForgeException, match="no standalone Daml equivalent"):
        _compile("from datetime import time\n\n" "def noon():\n" "    return time(12)\n")


def test_python_fromtimestamp_lowers_seconds_to_epoch_offset():
    daml = _compile(
        "from datetime import datetime, timezone\n\n"
        "def from_seconds(seconds: int) -> datetime:\n"
        "    return datetime.fromtimestamp(seconds, tz=timezone.utc)\n"
    )

    assert "from_seconds : Int -> Time" in daml
    assert "addRelTime (time (date 1970 Jan 1) 0 0 0) (microseconds (seconds * 1000000))" in daml
    assert daml.count("import DA.Time") == 1
    assert daml.count("import DA.Date") == 1


def test_python_fromtimestamp_folds_literal_seconds():
    daml = _compile(
        "from datetime import datetime, timezone\n\n"
        "def epoch_plus() -> datetime:\n"
        "    return datetime.fromtimestamp(2, timezone.utc)\n"
    )

    assert "addRelTime (time (date 1970 Jan 1) 0 0 0) (microseconds 2000000)" in daml


def test_qualified_python_fromtimestamp_preserves_microseconds():
    daml = _compile(
        "import datetime as dt\n\n"
        "def from_microseconds(microseconds: int) -> dt.datetime:\n"
        "    return dt.datetime.fromtimestamp(\n"
        "        microseconds / 1000000, dt.timezone.utc\n"
        "    )\n"
    )

    assert "from_microseconds : Int -> Time" in daml
    assert "addRelTime (time (date 1970 Jan 1) 0 0 0) (microseconds microseconds)" in daml
    assert daml.count("import DA.Time") == 1
    assert daml.count("import DA.Date") == 1


def test_python_fromtimestamp_requires_utc():
    with pytest.raises(DamlForgeException, match="requires `timezone.utc`"):
        _compile(
            "from datetime import datetime\n\n"
            "def from_seconds(seconds: int) -> datetime:\n"
            "    return datetime.fromtimestamp(seconds)\n"
        )


def test_python_datetime_now_lowers_to_get_time_ledger_effect():
    daml = _compile(
        "from datetime import datetime\n\n"
        "@template\n"
        "class Clock:\n"
        "    owner: Party\n\n"
        "    signatory: list[Party] = [owner]\n\n"
        "    @choice(controller=owner, consuming=False)\n"
        "    def read(self) -> datetime:\n"
        "        now = datetime.now()\n"
        "        return now\n"
    )

    assert "nonconsuming choice Read : Time" in daml
    assert "now <- getTime" in daml
    assert "import datetime" not in daml


def test_qualified_python_datetime_now_lowers_to_get_time():
    daml = _compile(
        "import datetime as dt\n\n"
        ""
        "def current_time() -> dt.datetime:\n"
        "    return dt.datetime.now()\n"
    )

    assert "current_time : Update Time" in daml
    assert "getTime" in daml
    assert "import datetime" not in daml


def test_python_datetime_now_is_inferred_without_an_effect_marker():
    daml = _compile(
        "from datetime import datetime\n\n"
        "def current_time() -> datetime:\n"
        "    return datetime.now()\n"
    )

    assert "current_time : Update Time" in daml


def test_python_datetime_now_rejects_arguments():
    with pytest.raises(DamlForgeException, match="does not accept arguments"):
        _compile(
            "from datetime import datetime\n\n"
            ""
            "def current_time() -> datetime:\n"
            "    return datetime.now(None)\n"
        )


def test_python_timedelta_rejects_non_python_years_argument():
    with pytest.raises(DamlForgeException, match="does not support `years=`"):
        _compile(
            "from datetime import timedelta\n\n"
            "def duration() -> timedelta:\n"
            "    return timedelta(years=1)\n"
        )


def test_builtin_splice_struct_optional_field_auto_wraps_without_manual_some():
    daml = _compile(
        "from Splice.Expiry import TimeLock\n\n"
        "@template\nclass Asset:\n"
        "    owner: Party\n\n"
        "    signatory: list[Party] = [owner]\n\n"
        "    @choice(controller=owner, consuming=True)\n"
        "    def lock(self, deadline) -> bool:\n"
        "        holders: list[Party] = [self.owner]\n"
        '        lock = TimeLock(holders=holders, expires_at=deadline, opt_context="reason")\n'
        "        return True\n"
    )

    assert 'optContext = Some "reason"' in daml


@pytest.mark.parametrize(
    "signature, body, expected",
    [
        ("() -> int", "int(Decimal(-2147483648))", "truncate ((-2147483648.0 : Decimal))"),
        ("(x: Decimal) -> int", "int(x * 2.5) + 1", "truncate (x * 2.5) + 1"),
        ("(n: int) -> int", "int(n)", "f n =\n  n\n"),
    ],
)
def test_python_int_conversion(signature, body, expected):
    daml = _compile(f"def f{signature}:\n    return {body}\n")

    assert expected in daml
    assert "int (" not in daml


def test_python_int_rejects_unsupported_source_type():
    with pytest.raises(DamlForgeException, match="cannot convert `Text`"):
        _compile("def f(s: str) -> int:\n    return int(s)\n")


@pytest.mark.parametrize(
    "signature, body, call, helpers",
    [
        ("(a: int, b: int) -> int", "a // b", "_damlforge_floorDiv a b", ["_damlforge_floorDiv"]),
        (
            "(a: Decimal, b: Decimal) -> Decimal",
            "a // b",
            "_damlforge_floorDivDecimal a b",
            ["_damlforge_floorDivDecimal"],
        ),
        ("(a: int) -> int", "-a // -2", "_damlforge_floorDiv (-a) (-2)", ["_damlforge_floorDiv"]),
        ("(a: int, b: int) -> int", "a / b", "a / b", []),
    ],
)
def test_floor_division_uses_generated_helper(signature, body, call, helpers):
    daml = _compile(f"def f{signature}:\n    return {body}\n")

    assert call in daml
    assert " // " not in daml
    for name in ("_damlforge_floorDiv", "_damlforge_floorDivDecimal"):
        assert (f"\n{name} : " in daml) is (name in helpers)


@pytest.mark.parametrize(
    "returns, body, expected",
    [
        ("date", "date(2024, int(d), 1)", "date 2024 (toEnum (truncate d - 1)) 1"),
        ("datetime", "datetime.combine(day, time(int(d), 0, 0))", "time day (truncate d) 0 0"),
        ("timedelta", "timedelta(seconds=int(d))", "seconds (truncate d)"),
        (
            "datetime",
            "datetime.fromtimestamp(int(d), timezone.utc)",
            "(microseconds (truncate d * 1000000))",
        ),
    ],
)
def test_python_int_conversion_inside_datetime_intrinsics(returns, body, expected):
    daml = _compile(
        "from datetime import date, datetime, time, timedelta, timezone\n\n"
        f"def f(d: Decimal, day: date) -> {returns}:\n    return {body}\n"
    )

    assert expected in daml
    assert "int (" not in daml and "(int d" not in daml


@pytest.mark.parametrize(
    "literal, expected",
    [
        ("2.5", "truncate ((2.5 : Decimal))"),
        ("-2147483648.0", "truncate ((-2147483648.0 : Decimal))"),
        ("Decimal(7)", "truncate ((7.0 : Decimal))"),
    ],
)
def test_python_int_of_decimal_literal_is_annotated(literal, expected):
    assert expected in _compile(f"def f() -> int:\n    return int({literal})\n")


def test_integer_literal_expected_as_decimal_is_annotated():
    daml = _compile(
        "@template\n"
        "class Asset:\n"
        "    owner: Party\n"
        "    amount: Decimal\n"
        "    signatory: list[Party] = [owner]\n"
        "    ensure: bool = amount > 0\n"
    )

    assert "ensure amount > (0.0 : Decimal)" in daml


@pytest.mark.parametrize(
    "argument, value, expected",
    [
        ("x: int", "str(x)", "show x"),
        ("x: Decimal", "str(x)", "show x"),
        ("x: bool", "str(x)", "show x"),
        ("x: Party", "str(x)", "partyToText x"),
        ("x: str", "str(x)", "f x =\n  x\n"),
        ("x: int", "str(1.5)", "show ((1.5 : Decimal))"),
    ],
)
def test_python_str_conversion(argument, value, expected):
    daml = _compile(f"def f({argument}) -> str:\n    return {value}\n")

    assert expected in daml
    assert "str " not in daml


def test_python_str_rejects_unsupported_source_type():
    with pytest.raises(DamlForgeException, match="`str\\(...\\)` cannot convert `list`"):
        _compile("def f(xs: list[int]) -> str:\n    return str(xs)\n")


@pytest.mark.parametrize(
    "signature, body, expected",
    [
        ("(a: str, b: str) -> str", "    return a + b\n", "a <> b"),
        ("(a: int) -> str", "    return str(a) + str(a)\n", "show a <> show a"),
        ("(a: list[int], b: list[int]) -> list[int]", "    return a + b\n", "a ++ b"),
        ("(a: str, b: str) -> str", "    c: str = a\n    c += b\n    return c\n", "c <> b"),
        (
            "(a: Decimal, b: Decimal) -> Decimal",
            "    c: Decimal = a\n    c //= b\n    return c\n",
            "_damlforge_floorDivDecimal c b",
        ),
        ("(a: int, b: int) -> int", "    return a + b\n", "a + b"),
    ],
)
def test_addition_uses_inferred_operand_type(signature, body, expected):
    assert expected in _compile(f"def f{signature}:\n{body}")


@pytest.mark.parametrize(
    "body, expected",
    [
        ("    return a - d\n", "addRelTime a (negate d)"),
        ("    return a - d - d\n", "addRelTime (addRelTime a (negate d)) (negate d)"),
        ("    t: datetime = a\n    t += d\n    return t\n", "addRelTime t d"),
        ("    t: datetime = a\n    t -= d\n    return t\n", "addRelTime t (negate d)"),
    ],
)
def test_datetime_shift_by_timedelta_lowers_to_add_rel_time(body, expected):
    daml = _compile(
        "from datetime import datetime, timedelta\n\n"
        f"def f(a: datetime, d: timedelta) -> datetime:\n{body}"
    )

    assert expected in daml
    assert daml.count("import DA.Time") == 1


def _compile_choice(returns, body, args=""):
    return _compile(
        "@template\nclass Tpl:\n"
        "    owner: Party\n"
        "    signatory: Party = owner\n\n"
        "    @choice(controller=owner, consuming=False)\n"
        f"    def Go(self{args}) -> {returns}:\n{body}"
    )


_NEW_TPL = "create(Tpl(owner=self.owner))"


@pytest.mark.parametrize(
    "returns, body, expected",
    [
        (
            "tuple[ContractId[Tpl], ContractId[Tpl]]",
            f"        return ({_NEW_TPL}, {_NEW_TPL})\n",
            [
                "_damlforge_effect1 <- create (Tpl with owner = self.owner)",
                "_damlforge_effect2 <- create (Tpl with owner = self.owner)",
                "pure (_damlforge_effect1, _damlforge_effect2)",
            ],
        ),
        (
            "list[ContractId[Tpl]]",
            f"        return [{_NEW_TPL}]\n",
            ["_damlforge_effect1 <- create", "pure ([_damlforge_effect1])"],
        ),
        (
            "tuple[int, ContractId[Tpl]]",
            f"        pair: tuple[int, ContractId[Tpl]] = (1, {_NEW_TPL})\n        return pair\n",
            [
                "_damlforge_effect1 <- create",
                "let (pair : (Int, ContractId Tpl)) = (1, _damlforge_effect1)",
            ],
        ),
        (
            "ContractId[Tpl]",
            f"        return {_NEW_TPL}\n",
            ["create (Tpl with owner = self.owner)"],
        ),
    ],
)
def test_choice_hoists_nested_ledger_effects(returns, body, expected):
    daml = _compile_choice(returns, body)

    for line in expected:
        assert line in daml
    assert "pure (create" not in daml and ", create" not in daml


@pytest.mark.parametrize(
    "returns, body, args, expected",
    [
        ("Optional[int]", "        return -5\n", "", "pure (Some (-5))"),
        ("Optional[Optional[int]]", "        return 1\n", "", "pure (Some (Some 1))"),
        ("Optional[TextMap[int]]", "        return {}\n", "", "pure (Some (TextMap.fromList []))"),
        ("Optional[list[int]]", "        return []\n", "", "pure (Some [])"),
        ("Optional[int]", "        return o\n", ", o: Optional[int]", "pure (o)"),
        ("Optional[int]", "        return None\n", "", "pure (None)"),
        (
            "Optional[ContractId[Tpl]]",
            f"        return {_NEW_TPL}\n",
            "",
            "pure (Some _damlforge_effect1)",
        ),
    ],
)
def test_choice_optional_return_is_wrapped_in_some(returns, body, args, expected):
    assert expected in _compile_choice(returns, body, args)


@pytest.mark.parametrize(
    "returns, value, expected",
    [
        ("Optional[int]", "1", "Some 1"),
        ("Optional[Optional[int]]", "1", "Some (Some 1)"),
        ("Optional[Optional[int]]", "None", "  None"),
    ],
)
def test_function_optional_return_wraps_each_layer(returns, value, expected):
    assert expected in _compile(f"def f() -> {returns}:\n    return {value}\n")


def _compile_counter_choice(body, args=""):
    return _compile(
        "@template\nclass Counter:\n"
        "    owner: Party\n"
        "    n: int\n"
        "    signatory: Party = owner\n\n"
        "    @choice(controller=owner, consuming=True)\n"
        f"    def Go(self{args}) -> int:\n{body}"
    )


@pytest.mark.parametrize(
    "body, args",
    [
        (
            "        self.n = 2\n        if b:\n            return 1\n"
            "        else:\n            x: int = 0\n        return 0\n",
            ", b: bool",
        ),
        (
            "        if b:\n            self.n = 1\n            if c:\n                return 5\n"
            "        else:\n            x: int = 0\n        return 0\n",
            ", b: bool, c: bool",
        ),
        (
            "        if b:\n            self.n = self.n + 1\n"
            "        else:\n            x: int = 0\n        return 0\n",
            ", b: bool",
        ),
    ],
)
def test_self_mutation_continuation_does_not_take_new_self(body, args):
    daml = _compile_counter_choice(body, args)

    assert "_damlforge_new_self <- create" in daml
    assert "_damlforge_new_self =" not in daml
    for line in daml.splitlines():
        if "_damlforge_cont" in line:
            assert "_damlforge_new_self" not in line


def test_rebound_ledger_effect_uses_bind():
    daml = _compile_choice(
        "ContractId[Tpl]",
        f"        cid: ContractId[Tpl] = {_NEW_TPL}\n"
        f"        cid = {_NEW_TPL}\n"
        "        return cid\n",
    )

    assert "_damlforge_cid1 <- create (Tpl with owner = self.owner)" in daml
    assert "let _damlforge_cid1" not in daml
