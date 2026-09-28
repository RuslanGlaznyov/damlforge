"""The Daml value and container policies enforced by semantic analysis.

This module is deliberately data-first.  Code which needs to validate a value
or a type reference should read the registry instead of carrying a second,
slightly different set of limits in an AST or code-generation module.

The bounds mirror the Daml 3.x language/reference documentation:

* ``Int`` and ``RelTime`` use signed 64-bit values.
* ``Decimal`` is ``Numeric 10``: 38 total digits and 10 fractional digits.
* ``Date`` and ``Time`` use the documented year range 1..9999.
* Daml tuples have arity 2..20; ``TextMap`` has Text keys; ``Map`` and ``Set``
  require ordered keys/elements.
"""

from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from decimal import Decimal
from types import MappingProxyType
from typing import Mapping

from forge.ir.nodes import TypeRef

INT_MIN = -(2**63)
INT_MAX = 2**63 - 1

DECIMAL_PRECISION = 38
DECIMAL_SCALE = 10
DECIMAL_MIN = -Decimal(10**38 - 1) / Decimal(10**DECIMAL_SCALE)
DECIMAL_MAX = Decimal(10**38 - 1) / Decimal(10**DECIMAL_SCALE)

DATE_MIN = date(1, 1, 1)
DATE_MAX = date(9999, 12, 31)
TIME_MIN = datetime(1, 1, 1, tzinfo=timezone.utc)
TIME_MAX = datetime(9999, 12, 31, 23, 59, 59, 999999, tzinfo=timezone.utc)


@dataclass(frozen=True)
class PrimitiveSpec:
    """Policy metadata for one Daml primitive type."""

    daml_name: str
    literal_kind: str | None = None
    min_value: object | None = None
    max_value: object | None = None
    precision: int | None = None
    scale: int | None = None
    ordered: bool = False
    comparable: bool = False
    serializable: bool = True
    notes: str = ""


@dataclass(frozen=True)
class GenericSpec:
    """Policy metadata for a Daml generic/container type."""

    daml_name: str
    min_arity: int
    max_arity: int
    ordered_element: bool = False
    ordered_key_position: int | None = None
    serializable: bool = True
    notes: str = ""


PRIMITIVE_TYPE_SPECS: Mapping[str, PrimitiveSpec] = MappingProxyType(
    {
        "Party": PrimitiveSpec(
            "Party",
            literal_kind="party",
            ordered=True,
            comparable=True,
            notes="Unicode party identifier; normally obtained from getParty.",
        ),
        "Text": PrimitiveSpec(
            "Text",
            literal_kind="text",
            ordered=True,
            comparable=True,
            notes="Unicode text; Daml specifies no fixed maximum length.",
        ),
        "Int": PrimitiveSpec(
            "Int",
            literal_kind="int",
            min_value=INT_MIN,
            max_value=INT_MAX,
            ordered=True,
            comparable=True,
            notes="Signed 64-bit integer.",
        ),
        "Decimal": PrimitiveSpec(
            "Decimal",
            literal_kind="decimal",
            min_value=DECIMAL_MIN,
            max_value=DECIMAL_MAX,
            precision=DECIMAL_PRECISION,
            scale=DECIMAL_SCALE,
            ordered=True,
            comparable=True,
            notes="Alias for Numeric 10: 38 total digits, 10 fractional digits.",
        ),
        "Date": PrimitiveSpec(
            "Date",
            ordered=True,
            comparable=True,
            min_value=DATE_MIN,
            max_value=DATE_MAX,
            notes="Calendar date from 0001-01-01 through 9999-12-31.",
        ),
        "Time": PrimitiveSpec(
            "Time",
            ordered=True,
            comparable=True,
            min_value=TIME_MIN,
            max_value=TIME_MAX,
            notes="UTC timestamp with microsecond precision.",
        ),
        "RelTime": PrimitiveSpec(
            "RelTime",
            literal_kind="reltime",
            min_value=INT_MIN,
            max_value=INT_MAX,
            ordered=True,
            comparable=True,
            notes="Relative time represented as a signed 64-bit microsecond count.",
        ),
        "Bool": PrimitiveSpec(
            "Bool", literal_kind="bool", ordered=True, comparable=True, notes="Boolean value."
        ),
        "Unit": PrimitiveSpec(
            "Unit",
            literal_kind="unit",
            ordered=True,
            comparable=True,
            notes="The single unit value ().",
        ),
        # Numeric is included in the registry even though the Python-facing
        # type surface currently exposes Decimal only.  Keeping its policy here
        # prevents a future Numeric[n] implementation from inventing limits.
        "Numeric": PrimitiveSpec(
            "Numeric",
            precision=DECIMAL_PRECISION,
            scale=None,
            ordered=True,
            comparable=True,
            notes="Numeric n, where n is an integer scale from 0 through 37.",
        ),
    }
)


GENERIC_TYPE_SPECS: Mapping[str, GenericSpec] = MappingProxyType(
    {
        "ContractId": GenericSpec("ContractId", 1, 1),
        "Optional": GenericSpec("Optional", 1, 1),
        "list": GenericSpec("List", 1, 1),
        "tuple": GenericSpec("Tuple", 2, 20),
        "set": GenericSpec("Set", 1, 1, ordered_element=True),
        "frozenset": GenericSpec("Set", 1, 1, ordered_element=True),
        "TextMap": GenericSpec("TextMap", 1, 1),
        "GenMap": GenericSpec("Map", 2, 2, ordered_key_position=0),
    }
)


TYPE_NAME_ALIASES: Mapping[str, str] = MappingProxyType(
    {
        "int": "Int",
        "str": "Text",
        "float": "Decimal",
        "bool": "Bool",
        "None": "Unit",
        "Timestamp": "Time",
    }
)


def canonical_type_name(name: str) -> str:
    return TYPE_NAME_ALIASES.get(name, name)


def primitive_spec(name: str) -> PrimitiveSpec | None:
    return PRIMITIVE_TYPE_SPECS.get(canonical_type_name(name))


def generic_spec(name: str) -> GenericSpec | None:
    return GENERIC_TYPE_SPECS.get(name)


def type_is_ordered(type_ref: TypeRef) -> bool:
    """Return whether the registry can prove an ``Ord`` instance exists."""

    name = canonical_type_name(type_ref.name)
    spec = primitive_spec(name)
    if spec is not None:
        return spec.ordered
    generic = generic_spec(name)
    if generic is None:
        # User-defined records may derive Ord in a future code-generation
        # phase.  Leave those to that phase rather than rejecting them here.
        return True
    if name == "ContractId":
        return True
    if name in ("Optional", "list", "set", "frozenset"):
        return bool(type_ref.args) and type_is_ordered(type_ref.args[0])
    if name == "tuple":
        return bool(type_ref.args) and all(type_is_ordered(arg) for arg in type_ref.args)
    return False


def decimal_policy_error(value: Decimal) -> str | None:
    """Return a user-facing reason when ``value`` is not a Daml Decimal."""

    if not value.is_finite():
        return "must be finite"
    if value < DECIMAL_MIN or value > DECIMAL_MAX:
        return f"must be between {DECIMAL_MIN} and {DECIMAL_MAX}"
    exponent = value.as_tuple().exponent
    if not isinstance(exponent, int):
        return "must be finite"
    scale = max(0, -exponent)
    if scale > DECIMAL_SCALE:
        return f"may have at most {DECIMAL_SCALE} digits after the decimal point"
    digits = len(value.as_tuple().digits)
    if digits > DECIMAL_PRECISION:
        return f"may have at most {DECIMAL_PRECISION} total digits"
    return None


def text_policy_error(value: str) -> str | None:
    """Return a reason when a Python string is not a valid Unicode Text value."""

    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        return "contains an invalid Unicode surrogate"
    return None


def date_policy_error(year: int, month: int, day: int) -> str | None:
    try:
        value = date(year, month, day)
    except ValueError as exc:
        return str(exc)
    if not DATE_MIN <= value <= DATE_MAX:
        return f"must be between {DATE_MIN.isoformat()} and {DATE_MAX.isoformat()}"
    return None


def time_policy_error(hour: int, minute: int, second: int, microsecond: int = 0) -> str | None:
    try:
        time(hour, minute, second, microsecond)
    except ValueError as exc:
        return str(exc)
    return None


def reltime_policy_error(microseconds: int) -> str | None:
    if not INT_MIN <= microseconds <= INT_MAX:
        return f"must be between {INT_MIN} and {INT_MAX} microseconds"
    return None
