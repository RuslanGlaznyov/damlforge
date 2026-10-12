from forge.models import Decimal, Optional
from forge.builtins import DamlName


def explode(str_value: str) -> list[str]:
    pass


def implode(list_value: list[str]) -> str:
    pass


@DamlName("isEmpty")
def is_empty(str_value: str) -> bool:
    pass


@DamlName("isNotEmpty")
def is_not_empty(str_value: str) -> bool:
    pass


def length(str_value: str) -> int:
    pass


def trim(str_value: str) -> str:
    pass


def replace(from_: str, to: str, xs: str) -> str:
    pass


def lines(str_value: str) -> list[str]:
    pass


def unlines(list_value: list[str]) -> str:
    pass


def words(str_value: str) -> list[str]:
    pass


def unwords(list_value: list[str]) -> str:
    pass


def intercalate(t: str, list_value: list[str]) -> str:
    pass


@DamlName("dropPrefix")
def drop_prefix(a: str, b: str) -> str:
    pass


@DamlName("dropSuffix")
def drop_suffix(a: str, b: str) -> str:
    pass


@DamlName("stripSuffix")
def strip_suffix(a: str, b: str) -> Optional[str]:
    pass


@DamlName("stripPrefix")
def strip_prefix(a: str, b: str) -> Optional[str]:
    pass


@DamlName("isPrefixOf")
def is_prefix_of(a: str, b: str) -> bool:
    pass


@DamlName("isSuffixOf")
def is_suffix_of(a: str, b: str) -> bool:
    pass


@DamlName("isInfixOf")
def is_infix_of(a: str, b: str) -> bool:
    pass


@DamlName("splitOnHelper")
def split_on_helper(s: list[str], t: list[str]) -> list[str]:
    pass


@DamlName("splitOn")
def split_on(str_value: str, str_value_1: str) -> list[str]:
    pass


@DamlName("splitAt")
def split_at(n: int, t: str) -> tuple[str, str]:
    pass


def take(n: int, str_value: str) -> str:
    pass


def drop(n: int, str_value: str) -> str:
    pass


def substring(s: int, l: int, str_value: str) -> str:
    pass


@DamlName("isSpace")
def is_space(str_value: str) -> bool:
    pass


@DamlName("isNewLine")
def is_new_line(str_value: str) -> bool:
    pass


@DamlName("isUpper")
def is_upper(str_value: str) -> bool:
    pass


@DamlName("isLower")
def is_lower(str_value: str) -> bool:
    pass


@DamlName("isDigit")
def is_digit(str_value: str) -> bool:
    pass


@DamlName("isAlpha")
def is_alpha(str_value: str) -> bool:
    pass


@DamlName("isAlphaNum")
def is_alpha_num(str_value: str) -> bool:
    pass


@DamlName("parseInt")
def parse_int(str_value: str) -> Optional[int]:
    pass


@DamlName("parseNumeric")
def parse_numeric(str_value: str) -> Optional[Decimal]:
    pass


@DamlName("parseDecimal")
def parse_decimal(str_value: str) -> Optional[Decimal]:
    pass


def sha256(str_value: str) -> str:
    pass


def reverse(str_value: str) -> str:
    pass


@DamlName("toCodePoints")
def to_code_points(str_value: str) -> list[int]:
    pass


@DamlName("fromCodePoints")
def from_code_points(list_value: list[int]) -> str:
    pass


@DamlName("asciiToLower")
def ascii_to_lower(str_value: str) -> str:
    pass


@DamlName("asciiToUpper")
def ascii_to_upper(str_value: str) -> str:
    pass
