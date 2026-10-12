from typing import Annotated, Generic, TypeVar

from forge.builtins import DamlName, no_derive

A = TypeVar("A")


@no_derive
struct All:
    get_all: Annotated[bool, DamlName("getAll")]


@no_derive
struct Any:
    get_any: Annotated[bool, DamlName("getAny")]


@no_derive
struct Sum(Generic[A]):
    unpack: A


@no_derive
struct Product(Generic[A]):
    unpack: A
