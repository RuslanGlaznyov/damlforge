import pytest

from forge.ast.parse import parse_to_ast
from forge.exceptions import DamlForgeException
from forge.models.error_codes import ErrorCodes
from forge.semantics import analyze_module

_DECORATOR_PREAMBLE = (
    "from forge.models import choice, ledger_effect, template, view\n"
    "from forge.builtins import DamlName\n"
)


def _analyze(source):
    module = parse_to_ast(
        _DECORATOR_PREAMBLE + source, module_path="test.vy", resolved_path="test.vy"
    )
    analyze_module(module)


PRIMITIVE_FIELD_TYPES_ARE_ALLOWED = """
struct Point:
    owner: Party
    label: Text
    count: Int
    amount: Decimal
    created: Date
    expires: Timestamp
    active: bool
"""


GENERIC_FIELD_TYPES_ARE_ALLOWED = """
struct Box:
    holding: ContractId[Party]
    maybe: Optional[Party]
    items: list[Party]
    pair: tuple[Party, Text]
    values: TextMap[Text]
    mapping: GenMap[Text, Int]
"""


LOCAL_STRUCT_REFERENCE_IS_ALLOWED = """
struct InstrumentId:
    admin: Party
    id: Text

struct HoldingView:
    instrument_id: InstrumentId
"""


TEMPLATE_FIELD_UNKNOWN_TYPE = """
template Asset:
    owner: TotallyBogusType

    signatory: list[Party] = [owner]
"""


STRUCT_FIELD_UNKNOWN_TYPE = """
struct Point:
    owner: NotARealType
"""


CHOICE_ARG_UNKNOWN_TYPE = """
template Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def transfer(self, new_owner: NotAType) -> bool:
        pass
"""


CHOICE_RETURN_UNKNOWN_TYPE = """
template Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def transfer(self, new_owner: Party) -> NotAType:
        pass
"""


FUNCTION_ARG_UNKNOWN_TYPE = """
def helper(x: NotAType) -> bool:
    pass
"""


INTERFACE_VIEW_UNKNOWN_TYPE = """
interface Holding(view=NotAViewType):
    pass
"""


NESTED_GENERIC_UNKNOWN_TYPE = """
template Asset:
    owner: Party
    holdings: list[ContractId[NotARealHolding]]

    signatory: list[Party] = [owner]
"""


@pytest.mark.parametrize(
    "source",
    [
        PRIMITIVE_FIELD_TYPES_ARE_ALLOWED,
        GENERIC_FIELD_TYPES_ARE_ALLOWED,
        LOCAL_STRUCT_REFERENCE_IS_ALLOWED,
    ],
)
def test_known_types_pass(source):
    _analyze(source)


@pytest.mark.parametrize(
    "source",
    [
        TEMPLATE_FIELD_UNKNOWN_TYPE,
        STRUCT_FIELD_UNKNOWN_TYPE,
        CHOICE_ARG_UNKNOWN_TYPE,
        CHOICE_RETURN_UNKNOWN_TYPE,
        FUNCTION_ARG_UNKNOWN_TYPE,
        INTERFACE_VIEW_UNKNOWN_TYPE,
        NESTED_GENERIC_UNKNOWN_TYPE,
    ],
)
def test_unknown_type_raises(source):
    with pytest.raises(DamlForgeException) as exc_info:
        _analyze(source)

    assert exc_info.value.code == ErrorCodes.DF1213.value
