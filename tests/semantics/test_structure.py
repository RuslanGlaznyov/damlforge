import pytest

from forge.ast.parse import parse_to_ast
from forge.exceptions import DamlForgeException, ExceptionList
from forge.semantics import analyze_module
from forge.semantics.analysis.imports import ImportsBuilder
from forge.models.error_codes import ErrorCodes


def _analyze(source):
    module = parse_to_ast(source, module_path="test.vy", resolved_path="test.vy")
    analyze_module(module)


VALID_TEMPLATE = """
template Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def transfer(new_owner: Party) -> bool:
        pass
"""


TEMPLATE_MISSING_SIGNATORY = """
template Asset:
    owner: Party

    @choice(controller=owner, consuming=True)
    def transfer(new_owner: Party) -> bool:
        pass
"""


CHOICE_MISSING_CONTROLLER = """
template Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @choice(consuming=True)
    def transfer(new_owner: Party) -> bool:
        pass
"""

CHOICE_LEADING_UNDERSCORE_NAME_NOT_ALLOWED = """
template Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def _mint(self) -> bool:
        return True
"""

CHOICE_DOUBLE_LEADING_UNDERSCORE_NAME_NOT_ALLOWED = """
template Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def __mint(self) -> bool:
        return True
"""

CHOICE_NAME_WITH_NO_LETTER_NOT_ALLOWED = """
template Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def _123(self) -> bool:
        return True
"""

CHOICE_ALL_UNDERSCORE_NAME_NOT_ALLOWED = """
template Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def ___(self) -> bool:
        return True
"""


SELF_REFERENCE_VIA_TEMPLATE_NAME_NOT_ALLOWED = """
template Asset:
    owner: Party
    balance: int

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def withdraw(self, amount: int) -> bool:
        return Asset.balance >= amount
"""

SELF_REFERENCE_VIA_ANOTHER_TEMPLATE_NAME_IS_ALLOWED = """
template Other:
    owner: Party

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def noop(self) -> bool:
        return True

template Asset:
    owner: Party
    balance: int

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def withdraw(self, amount: int) -> bool:
        return self.balance >= amount
"""

UNRESOLVED_NAME_USED_AS_ATTRIBUTE_BASE_NOT_ALLOWED = """
template Asset:
    owner: Party
    balance: int

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def withdraw(self, amount: int) -> bool:
        return SomeUndeclaredName.balance >= amount
"""

LOCAL_VARIABLE_USED_AS_ATTRIBUTE_BASE_IS_ALLOWED = """
template Asset:
    owner: Party
    balance: int

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def withdraw(self, amount: int) -> bool:
        other: Asset = self
        return other.balance >= amount
"""

UNRESOLVED_NAME_USED_AS_CALL_TARGET_NOT_ALLOWED = """
template Asset:
    owner: Party
    balance: int

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def withdraw(self, amount: int) -> bool:
        return some_undeclared_function(amount) > 0
"""

UNKNOWN_DECORATOR_NOT_ALLOWED = """
template Asset:
    owner: Party
    balance: int

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    @TotallyBogusDecorator("Asset_Withdraw")
    def withdraw(self, amount: int) -> bool:
        return True
"""

DAML_NAME_OVERRIDES_CHOICE_NAME_IS_ALLOWED = """
template Asset:
    owner: Party
    balance: int

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    @DamlName("Asset_Withdraw")
    def withdraw(self, amount: int) -> bool:
        return True
"""

DAML_NAME_WITH_NO_ARGUMENTS_NOT_ALLOWED = """
template Asset:
    owner: Party
    balance: int

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    @DamlName()
    def withdraw(self, amount: int) -> bool:
        return True
"""

DAML_NAME_WITH_NON_LITERAL_ARGUMENT_NOT_ALLOWED = """
template Asset:
    owner: Party
    balance: int

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    @DamlName(owner)
    def withdraw(self, amount: int) -> bool:
        return True
"""

KNOWN_BUILTIN_AND_STRUCT_CONSTRUCTOR_CALL_TARGETS_ARE_ALLOWED = """
struct Terms:
    label: Text

template Asset:
    owner: Party
    balance: int

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def withdraw(self, amount: int) -> bool:
        terms = Terms(label="ok")
        rounded = ceil(Decimal(amount))
        return len(terms.label) > 0 and rounded > 0
"""


GENMAP_FIELD_IS_ALLOWED = """
template Asset:
    owner: Party
    balances: GenMap[Party, Decimal]

    signatory: list[Party] = [owner]
"""


TEXTMAP_FIELD_IS_ALLOWED = """
template Asset:
    owner: Party
    balances: TextMap[Decimal]

    signatory: list[Party] = [owner]
"""


DICT_TYPE_NOT_ALLOWED = """
template Asset:
    owner: Party
    balances: dict[Party, Decimal]

    signatory: list[Party] = [owner]
"""


UNKNOWN_MAP_TYPE_NOT_ALLOWED = """
template Asset:
    owner: Party
    balances: Map[Party, Decimal]

    signatory: list[Party] = [owner]
"""


CHOICE_MISSING_CONSUMING = """
template Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @choice(controller=owner)
    def transfer(new_owner: Party) -> bool:
        pass
"""


CHOICE_NON_LITERAL_CONSUMING = """
template Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=owner)
    def transfer(new_owner: Party) -> bool:
        pass
"""


LEDGER_EFFECT_WITH_ARGS = """
template Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @ledger_effect(True)
    def replace(new_owner: Party) -> bool:
        pass
"""


HIDDEN_LEDGER_EFFECT = """
template Asset:
    owner: Party

    signatory: list[Party] = [owner]

    def replace(new_owner: Party) -> bool:
        archive(self)
"""


LEDGER_EFFECT_MARKED_IS_ALLOWED = """
template Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @ledger_effect
    def replace(new_owner: Party) -> bool:
        archive(self)
"""


CHOICE_BODY_LEDGER_EFFECT_IS_ALLOWED = """
template Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def transfer(new_owner: Party) -> bool:
        archive(self)
"""


VIEW_WITH_ARGS = """
struct HoldingView:
    owner: Party

interface Holding(view=HoldingView):
    @view(True)
    def get_view() -> bool:
        pass
"""


VIEW_IN_TEMPLATE = """
template Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @view
    def get_view() -> bool:
        pass
"""


VIEW_IN_INTERFACE_IS_ALLOWED = """
struct HoldingView:
    owner: Party

interface Holding(view=HoldingView):
    @view
    def get_view() -> bool:
        pass
"""

RECURSION_SINGLE_FUNC = """
template RecursionTemplate:
    platform: Party
    developer: Party
    dso: Party

    signatory: list[Party] = [platform]

    def __init__(
        self,
        platform: Party,
        developer: Party,
        dso: Party
    ):
        self.platform = platform
        self.developer = developer
        self.dso = dso
    
    @choice(controller=[developer, platform], consuming=True)
    def recursion(self) -> bool:
        return self.recursion()
"""

MISSING_IMPORT = """
template Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def transfer(new_owner: Party, app_context: AppTransferContext) -> bool:
        pass
"""

WILDCARD_MISSING_IMPORT_NOT_ALLOWED = """
from Splice.AppTransferContext import *

template Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def transfer(new_owner: Party, app_context: AppTransferContext) -> bool:
        pass
"""

AS_IMPORT_NOT_ALLOWED = """
from Splice.AppTransferContext import AppTransferContext as AppTContext

template Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def transfer(new_owner: Party, app_context: AppTContext) -> bool:
        pass
"""

DOUBLE_IMPORTS_NOT_ALLOWED = """
from Splice.AppTransferContext import AppTransferContext
from Splice.AppTransferContext import AppTransferContext

template Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def transfer(new_owner: Party, app_context: AppTContext) -> bool:
        pass
"""

UNRESOLVABLE_IMPORT_NOT_ALLOWED = """
from totally_bogus_nonexistent_module import Something

template Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def transfer(new_owner: Party) -> bool:
        pass
"""

UNRESOLVABLE_BARE_IMPORT_NOT_ALLOWED = """
import totally_bogus_nonexistent_module

template Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def transfer(new_owner: Party) -> bool:
        pass
"""


def _choice_template(consuming_literal, observer_clause=""):
    return f"""
template Asset:
    owner: Party
    issuer: Party

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming={consuming_literal}{observer_clause})
    def transfer(new_owner: Party) -> bool:
        pass
"""


CHOICE_PRECONSUMING_ON_TEMPLATE_IS_ALLOWED = _choice_template('"preconsuming"')
CHOICE_POSTCONSUMING_ON_TEMPLATE_IS_ALLOWED = _choice_template('"postconsuming"')
CHOICE_STRING_CONSUMING_ON_TEMPLATE_IS_ALLOWED = _choice_template('"consuming"')
CHOICE_WITH_OBSERVER_IS_ALLOWED = _choice_template("True", ", observer=issuer")


CHOICE_PRECONSUMING_ON_INTERFACE = """
struct HoldingView:
    owner: Party

interface Holding(view=HoldingView):
    @choice(controller=owner, consuming="preconsuming")
    def archive_holding() -> bool:
        pass
"""


CHOICE_POSTCONSUMING_ON_INSTANCE = """
struct HoldingView:
    owner: Party

interface Holding(view=HoldingView):
    pass
instance AssetHoldingInstance(Holding):
    @choice(controller=owner, consuming="postconsuming")
    def archive_holding() -> bool:
        pass
"""


TEMPLATE_KEY_WITHOUT_MAINTAINER = """
template Asset:
    owner: Party
    asset_id: Text

    signatory: list[Party] = [owner]
    key: tuple[Party, Text] = (owner, asset_id)
"""


TEMPLATE_MAINTAINER_WITHOUT_KEY = """
template Asset:
    owner: Party
    asset_id: Text

    signatory: list[Party] = [owner]
    maintainer: list[Party] = [owner]
"""


TEMPLATE_KEY_WITH_MAINTAINER_IS_ALLOWED = """
template Asset:
    owner: Party
    asset_id: Text

    signatory: list[Party] = [owner]
    key: tuple[Party, Text] = (owner, asset_id)
    maintainer: list[Party] = [owner]
"""


TEMPLATE_WITHOUT_KEY_OR_MAINTAINER_IS_ALLOWED = """
template Asset:
    owner: Party

    signatory: list[Party] = [owner]
"""


TEMPLATE_ENSURE_COMPARE_IS_ALLOWED = """
template Asset:
    owner: Party
    amount: Decimal

    signatory: list[Party] = [owner]
    ensure: bool = amount > Decimal(0)
"""


TEMPLATE_ENSURE_BOOLOP_IS_ALLOWED = """
template Asset:
    owner: Party
    amount: Decimal
    issuer: Party

    signatory: list[Party] = [owner]
    ensure: bool = amount > Decimal(0) and issuer != owner
"""


TEMPLATE_ENSURE_CALL_IS_ALLOWED = """
template Asset:
    owner: Party
    amount: Decimal

    signatory: list[Party] = [owner]
    ensure: bool = is_valid(amount)
"""


TEMPLATE_WITHOUT_ENSURE_IS_ALLOWED = """
template Asset:
    owner: Party

    signatory: list[Party] = [owner]
"""


TEMPLATE_ENSURE_NON_BOOLEAN_LITERAL = """
template Asset:
    owner: Party
    amount: Decimal

    signatory: list[Party] = [owner]
    ensure: Decimal = amount
"""


TEMPLATE_ENSURE_ARITHMETIC_EXPRESSION = """
template Asset:
    owner: Party
    amount: Decimal

    signatory: list[Party] = [owner]
    ensure: Decimal = amount + Decimal(0)
"""


TEMPLATE_ENSURE_WITHOUT_VALUE = """
template Asset:
    owner: Party

    signatory: list[Party] = [owner]
    ensure: bool
"""

FLAG_VALUE_ACCESS_IS_ALLOWED = """
flag Status:
    PENDING
    PAID

template Asset:
    owner: Party
    status: Status

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def mark_paid(self) -> bool:
        return self.status == Status.PENDING
"""

FLAG_VALUE_ACCESS_UNKNOWN_MEMBER = """
flag Status:
    PENDING
    PAID

template Asset:
    owner: Party
    status: Status

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def mark_paid(self) -> bool:
        return self.status == Status.TYPO
"""

FLAG_MEMBER_LOWERCASE_NOT_ALLOWED = """
flag Status:
    pending
    PAID

template Asset:
    owner: Party

    signatory: list[Party] = [owner]
"""

FLAG_MEMBER_MIXED_CASE_NOT_ALLOWED = """
flag Status:
    Pending
    PAID

template Asset:
    owner: Party

    signatory: list[Party] = [owner]
"""


def test_valid_template_passes():
    _analyze(VALID_TEMPLATE)


@pytest.mark.parametrize(
    "source",
    [
        LEDGER_EFFECT_MARKED_IS_ALLOWED,
        CHOICE_BODY_LEDGER_EFFECT_IS_ALLOWED,
        VIEW_IN_INTERFACE_IS_ALLOWED,
        CHOICE_PRECONSUMING_ON_TEMPLATE_IS_ALLOWED,
        CHOICE_POSTCONSUMING_ON_TEMPLATE_IS_ALLOWED,
        CHOICE_STRING_CONSUMING_ON_TEMPLATE_IS_ALLOWED,
        CHOICE_WITH_OBSERVER_IS_ALLOWED,
        TEMPLATE_KEY_WITH_MAINTAINER_IS_ALLOWED,
        TEMPLATE_WITHOUT_KEY_OR_MAINTAINER_IS_ALLOWED,
        TEMPLATE_ENSURE_COMPARE_IS_ALLOWED,
        TEMPLATE_ENSURE_BOOLOP_IS_ALLOWED,
        TEMPLATE_ENSURE_CALL_IS_ALLOWED,
        TEMPLATE_WITHOUT_ENSURE_IS_ALLOWED,
        FLAG_VALUE_ACCESS_IS_ALLOWED,
        SELF_REFERENCE_VIA_ANOTHER_TEMPLATE_NAME_IS_ALLOWED,
        LOCAL_VARIABLE_USED_AS_ATTRIBUTE_BASE_IS_ALLOWED,
        KNOWN_BUILTIN_AND_STRUCT_CONSTRUCTOR_CALL_TARGETS_ARE_ALLOWED,
        DAML_NAME_OVERRIDES_CHOICE_NAME_IS_ALLOWED,
        GENMAP_FIELD_IS_ALLOWED,
        TEXTMAP_FIELD_IS_ALLOWED,
    ],
)
def test_valid_decorator_usage_passes(source):
    _analyze(source)


@pytest.mark.parametrize(
    "source,expected_code",
    [
        (TEMPLATE_MISSING_SIGNATORY, ErrorCodes.DF1201.value),
        (CHOICE_MISSING_CONTROLLER, ErrorCodes.DF1203.value),
        (CHOICE_MISSING_CONSUMING, ErrorCodes.DF1203.value),
        (CHOICE_NON_LITERAL_CONSUMING, ErrorCodes.DF1203.value),
        (LEDGER_EFFECT_WITH_ARGS, ErrorCodes.DF1204.value),
        (HIDDEN_LEDGER_EFFECT, ErrorCodes.DF1205.value),
        (VIEW_WITH_ARGS, ErrorCodes.DF1206.value),
        (VIEW_IN_TEMPLATE, ErrorCodes.DF1207.value),
        (CHOICE_PRECONSUMING_ON_INTERFACE, ErrorCodes.DF1208.value),
        (CHOICE_POSTCONSUMING_ON_INSTANCE, ErrorCodes.DF1208.value),
        (RECURSION_SINGLE_FUNC, ErrorCodes.DF1209.value),
        (TEMPLATE_KEY_WITHOUT_MAINTAINER, ErrorCodes.DF1210.value),
        (TEMPLATE_MAINTAINER_WITHOUT_KEY, ErrorCodes.DF1211.value),
        (TEMPLATE_ENSURE_NON_BOOLEAN_LITERAL, ErrorCodes.DF1212.value),
        (TEMPLATE_ENSURE_ARITHMETIC_EXPRESSION, ErrorCodes.DF1212.value),
        (TEMPLATE_ENSURE_WITHOUT_VALUE, ErrorCodes.DF1212.value),
        (MISSING_IMPORT, ErrorCodes.DF1213.value),
        (DICT_TYPE_NOT_ALLOWED, ErrorCodes.DF1213.value),
        (UNKNOWN_MAP_TYPE_NOT_ALLOWED, ErrorCodes.DF1213.value),
        (WILDCARD_MISSING_IMPORT_NOT_ALLOWED, ErrorCodes.DF1213.value),
        (AS_IMPORT_NOT_ALLOWED, ErrorCodes.DF1213.value),
        (DOUBLE_IMPORTS_NOT_ALLOWED, ErrorCodes.DF1213.value),
        (UNRESOLVABLE_IMPORT_NOT_ALLOWED, ErrorCodes.DF1213.value),
        (UNRESOLVABLE_BARE_IMPORT_NOT_ALLOWED, ErrorCodes.DF1213.value),
        (FLAG_VALUE_ACCESS_UNKNOWN_MEMBER, ErrorCodes.DF1216.value),
        (FLAG_MEMBER_LOWERCASE_NOT_ALLOWED, ErrorCodes.DF1217.value),
        (FLAG_MEMBER_MIXED_CASE_NOT_ALLOWED, ErrorCodes.DF1217.value),
        (CHOICE_LEADING_UNDERSCORE_NAME_NOT_ALLOWED, ErrorCodes.DF1218.value),
        (CHOICE_DOUBLE_LEADING_UNDERSCORE_NAME_NOT_ALLOWED, ErrorCodes.DF1218.value),
        (CHOICE_NAME_WITH_NO_LETTER_NOT_ALLOWED, ErrorCodes.DF1218.value),
        (CHOICE_ALL_UNDERSCORE_NAME_NOT_ALLOWED, ErrorCodes.DF1218.value),
        (SELF_REFERENCE_VIA_TEMPLATE_NAME_NOT_ALLOWED, ErrorCodes.DF1219.value),
        (UNRESOLVED_NAME_USED_AS_ATTRIBUTE_BASE_NOT_ALLOWED, ErrorCodes.DF1219.value),
        (UNRESOLVED_NAME_USED_AS_CALL_TARGET_NOT_ALLOWED, ErrorCodes.DF1219.value),
        (UNKNOWN_DECORATOR_NOT_ALLOWED, ErrorCodes.DF1220.value),
        (DAML_NAME_WITH_NO_ARGUMENTS_NOT_ALLOWED, ErrorCodes.DF1221.value),
        (DAML_NAME_WITH_NON_LITERAL_ARGUMENT_NOT_ALLOWED, ErrorCodes.DF1221.value),
    ],
)
def test_invalid_template_raises(source, expected_code):
    with pytest.raises(DamlForgeException) as exc_info:
        _analyze(source)

    assert exc_info.value.code == expected_code


def test_sibling_vy_import_still_resolves_via_load_import(tmp_path):
    sibling_path = tmp_path / "loan_terms.vy"
    sibling_path.write_text("template LoanTerms:\n    rate: int\n")

    main_path = tmp_path / "main.vy"
    main_path.write_text(
        "from loan_terms import LoanTerms\n\n"
        "template Asset:\n"
        "    owner: Party\n\n"
        "    signatory: list[Party] = [owner]\n"
    )

    module = parse_to_ast(
        main_path.read_text(), module_path="main.vy", resolved_path=str(main_path)
    )
    analyze_module(module)


def test_integrity_sum_is_deterministic_for_identical_source():
    module1 = parse_to_ast(VALID_TEMPLATE, module_path="test.vy", resolved_path="test.vy")
    module2 = parse_to_ast(VALID_TEMPLATE, module_path="test.vy", resolved_path="test.vy")

    assert ImportsBuilder().integrity_sum(module1) == ImportsBuilder().integrity_sum(module2)


def test_integrity_sum_changes_when_source_changes():
    module1 = parse_to_ast(VALID_TEMPLATE, module_path="test.vy", resolved_path="test.vy")
    module2 = parse_to_ast(VALID_TEMPLATE + "\n", module_path="test.vy", resolved_path="test.vy")

    assert ImportsBuilder().integrity_sum(module1) != ImportsBuilder().integrity_sum(module2)


def test_integrity_sum_changes_when_sibling_import_changes(tmp_path):
    sibling_path = tmp_path / "sibling.vy"
    sibling_path.write_text("template Sibling:\n    owner: Party\n")

    main_path = tmp_path / "main.vy"
    main_path.write_text("from sibling import Sibling\n" + VALID_TEMPLATE)

    def _main_integrity_sum():
        module = parse_to_ast(
            main_path.read_text(), module_path="main.vy", resolved_path=str(main_path)
        )
        builder = ImportsBuilder()
        builder.resolve_imports(module, ExceptionList())
        return builder.integrity_sum(module)

    before = _main_integrity_sum()
    sibling_path.write_text("template Sibling:\n    owner: Party\n    extra: Text\n")
    after = _main_integrity_sum()

    assert before != after


def test_multiple_violations_are_all_reported():
    source = """
template Asset:
    owner: Party

    @choice(consuming=True)
    def transfer(new_owner: Party) -> bool:
        pass
"""
    with pytest.raises(Exception) as exc_info:
        _analyze(source)

    message = str(exc_info.value)
    assert "DF1201" in message
    assert "DF1202" in message
