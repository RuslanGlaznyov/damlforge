from typing import TypeVar

from forge.models import Decimal, Optional
from forge.builtins import DamlName
from DA.Types import Either

A = TypeVar("A")


SignatureHex = str


PublicKeyHex = str


BytesHex = str


@DamlName("hexByteToInt")
def hex_byte_to_int(str_value: str) -> int:
    pass


@DamlName("isHex")
def is_hex(str_value: str) -> bool:
    pass


@DamlName("isBytesHex")
def is_bytes_hex(hex: str) -> bool:
    pass


@DamlName("isDEREncoded")
def is_der_encoded(msg: str) -> bool:
    pass


def sha256(msg: str) -> str:
    pass


def keccak256(msg: str) -> str:
    pass


@DamlName("secp256k1WithEcdsaOnly")
def secp256k1_with_ecdsa_only(sig: str, msg: str, pk: str) -> bool:
    pass


def secp256k1(sig: str, msg: str, pk: str) -> bool:
    pass


@DamlName("toHex")
def to_hex(a: A) -> str:
    pass


@DamlName("uint16ToHexByte")
def uint16_to_hex_byte(int_value: int) -> str:
    pass


@DamlName("uint256ToHexByte")
def uint256_to_hex_byte(int_value: int) -> str:
    pass


@DamlName("uintToHexByteList")
def uint_to_hex_byte_list(int_value: int) -> list[str]:
    pass


@DamlName("numericViaStringToHex")
def numeric_via_string_to_hex(num: Decimal) -> str:
    pass


@DamlName("fromHex")
def from_hex(str_value: str) -> A:
    pass


@DamlName("calculateOptIntFromIntArgs")
def calculate_opt_int_from_int_args(left_int: int, right_int: int) -> Optional[int]:
    pass


@DamlName("numericViaStringFromHex")
def numeric_via_string_from_hex(hex: str) -> Optional[Decimal]:
    pass


@DamlName("byteCount")
def byte_count(str_value: str) -> int:
    pass


@DamlName("replicateList")
def replicate_list(int_value: int, a: A) -> list[A]:
    pass


@DamlName("byteRepeat")
def byte_repeat(int_value: int, str_value: str) -> str:
    pass


@DamlName("minBytes32Hex")
def min_bytes32_hex() -> str:
    pass


@DamlName("maxBytes32Hex")
def max_bytes32_hex() -> str:
    pass


@DamlName("isBytes32Hex")
def is_bytes32_hex(hex: str) -> bool:
    pass


@DamlName("minUInt32Hex")
def min_u_int32_hex() -> str:
    pass


@DamlName("maxUInt32Hex")
def max_u_int32_hex() -> str:
    pass


@DamlName("isUInt32Hex")
def is_u_int32_hex(hex: str) -> bool:
    pass


@DamlName("minUInt64Hex")
def min_u_int64_hex() -> str:
    pass


@DamlName("maxUInt64Hex")
def max_u_int64_hex() -> str:
    pass


@DamlName("isUInt64Hex")
def is_u_int64_hex(hex: str) -> bool:
    pass


@DamlName("minUInt256Hex")
def min_u_int256_hex() -> str:
    pass


@DamlName("maxUInt256Hex")
def max_u_int256_hex() -> str:
    pass


@DamlName("isUInt256Hex")
def is_u_int256_hex(hex: str) -> bool:
    pass


@DamlName("packHexBytes")
def pack_hex_bytes(hex: str, pad: int) -> Optional[str]:
    pass


@DamlName("sliceHexBytes")
def slice_hex_bytes(str_value: str, int_value: int, int_value_2: int) -> Either[str, str]:
    pass
