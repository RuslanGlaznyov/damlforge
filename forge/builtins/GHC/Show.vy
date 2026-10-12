from typing import TypeVar

from forge.builtins import DamlName

A = TypeVar("A")


@DamlName("showsPrec")
def shows_prec(int_value: int, a: A, str_value: str) -> str:
    pass


def show(a: A) -> str:
    pass


@DamlName("showList")
def show_list(list_value: list[A], str_value: str) -> str:
    pass


def shows(x: A, str_value: str) -> str:
    pass


@DamlName("showString")
def show_string(str_value: str, str_value_1: str) -> str:
    pass


@DamlName("showSpace")
def show_space(str_value: str) -> str:
    pass


@DamlName("showCommaSpace")
def show_comma_space(str_value: str) -> str:
    pass
