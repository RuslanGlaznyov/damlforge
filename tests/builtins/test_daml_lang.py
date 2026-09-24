import pytest

from forge.ast.parse import parse_to_ast
from forge.builtins import collect_daml_builtins
from forge.codegen import generate_daml
from forge.exceptions import DamlForgeException
from forge.ir import lower_module
from forge.semantics import analyze_module

_DECORATOR_PREAMBLE = (
    "from forge.models import choice, ledger_effect, template, view\n"
    "from forge.builtins import DamlName\n"
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
        _compile(
            "from datetime import time\n\n"
            "def noon():\n"
            "    return time(12)\n"
        )


def test_python_fromtimestamp_lowers_seconds_to_unix_microseconds():
    daml = _compile(
        "from datetime import datetime, timezone\n\n"
        "def from_seconds(seconds: int) -> datetime:\n"
        "    return datetime.fromtimestamp(seconds, tz=timezone.utc)\n"
    )

    assert "from_seconds : Int -> Time" in daml
    assert "fromUnixMicroseconds (seconds * 1000000)" in daml
    assert daml.count("import DA.Time") == 1


def test_qualified_python_fromtimestamp_preserves_microseconds():
    daml = _compile(
        "import datetime as dt\n\n"
        "def from_microseconds(microseconds: int) -> dt.datetime:\n"
        "    return dt.datetime.fromtimestamp(\n"
        "        microseconds / 1000000, dt.timezone.utc\n"
        "    )\n"
    )

    assert "from_microseconds : Int -> Time" in daml
    assert "fromUnixMicroseconds microseconds" in daml
    assert daml.count("import DA.Time") == 1


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
        "@ledger_effect\n"
        "def current_time() -> dt.datetime:\n"
        "    return dt.datetime.now()\n"
    )

    assert "current_time : Update Time" in daml
    assert "getTime" in daml
    assert "import datetime" not in daml


def test_python_datetime_now_requires_ledger_effect_context():
    with pytest.raises(DamlForgeException, match="calls `datetime.now`"):
        _compile(
            "from datetime import datetime\n\n"
            "@template\n"
            "class Clock:\n"
            "    owner: Party\n\n"
            "    signatory: list[Party] = [owner]\n\n"
            "    def read(self) -> datetime:\n"
            "        return datetime.now()\n"
        )


def test_python_datetime_now_rejects_arguments():
    with pytest.raises(DamlForgeException, match="does not accept arguments"):
        _compile(
            "from datetime import datetime\n\n"
            "@ledger_effect\n"
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
