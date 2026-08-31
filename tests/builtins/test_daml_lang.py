from forge.ast.parse import parse_to_ast
from forge.builtins import collect_daml_renames
from forge.codegen import generate_daml
from forge.ir import lower_module
from forge.semantics import analyze_module


def _compile(source):
    module = parse_to_ast(source, module_path="test.vy", resolved_path="test.vy")
    analyze_module(module)
    ir = lower_module(module)
    daml_source, _ = generate_daml(ir, module_name="Test")
    return daml_source


def test_collect_daml_renames_includes_daml_lang_functions():
    function_renames, _, function_import_modules = collect_daml_renames()

    assert function_renames["from_interface_contract_id"] == "fromInterfaceContractId"
    assert function_renames["to_interface_contract_id"] == "toInterfaceContractId"
    assert function_renames["to_interface"] == "toInterface"
    assert function_renames["coerce_interface_contract_id"] == "coerceInterfaceContractId"
    assert function_renames["add_rel_time"] == "addRelTime"
    assert function_renames["sub_time"] == "subTime"


def test_prelude_functions_need_no_import():
    _, _, function_import_modules = collect_daml_renames()

    assert "fromInterfaceContractId" not in function_import_modules
    assert "toInterfaceContractId" not in function_import_modules
    assert "toInterface" not in function_import_modules
    assert "coerceInterfaceContractId" not in function_import_modules


def test_da_time_functions_require_da_time_import():
    _, _, function_import_modules = collect_daml_renames()

    assert function_import_modules["addRelTime"] == "DA.Time"
    assert function_import_modules["subTime"] == "DA.Time"


def test_from_interface_contract_id_renders_and_needs_no_extra_import():
    daml = _compile(
        "template Asset:\n"
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
        "template Asset:\n"
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


def test_add_rel_time_renders_and_requires_da_time_import():
    daml = _compile(
        "template Asset:\n"
        "    owner: Party\n"
        "    anchor: Timestamp\n\n"
        "    signatory: list[Party] = [owner]\n\n"
        "    @choice(controller=owner, consuming=True)\n"
        "    def bump(self, delta) -> Timestamp:\n"
        "        return add_rel_time(self.anchor, delta)\n"
    )

    assert "addRelTime" in daml
    assert "import DA.Time" in daml


def test_sub_time_renders_and_requires_da_time_import():
    daml = _compile(
        "template Asset:\n"
        "    owner: Party\n\n"
        "    signatory: list[Party] = [owner]\n\n"
        "    @choice(controller=owner, consuming=True)\n"
        "    def compare_times(self, t1, t2) -> bool:\n"
        "        diff = sub_time(t1, t2)\n"
        "        return True\n"
    )

    assert "subTime" in daml
    assert "import DA.Time" in daml


def test_da_time_import_emitted_only_once_when_both_functions_used():
    daml = _compile(
        "template Asset:\n"
        "    owner: Party\n\n"
        "    signatory: list[Party] = [owner]\n\n"
        "    @choice(controller=owner, consuming=True)\n"
        "    def both(self, t1, t2, delta) -> bool:\n"
        "        diff = sub_time(t1, t2)\n"
        "        bumped = add_rel_time(t1, delta)\n"
        "        return True\n"
    )

    assert daml.count("import DA.Time") == 1
