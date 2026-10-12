from forge.builtins import DamlName


Chr = str


@DamlName("showsPrecText")
def shows_prec_text(int_value: int, x: str, str_value: str) -> str:
    pass


@DamlName("primExplode")
def prim_explode(str_value: str) -> list[str]:
    pass


@DamlName("primTextToCodePoints")
def prim_text_to_code_points(str_value: str) -> list[int]:
    pass


@DamlName("primIntToText")
def prim_int_to_text(int_value: int) -> str:
    pass


def explode(str_value: str) -> list[str]:
    pass


@DamlName("startsWithDigit")
def starts_with_digit(t: str) -> bool:
    pass


@DamlName("startsWithUppercaseH")
def starts_with_uppercase_h(t: str) -> bool:
    pass


def ord(t: str) -> int:
    pass


@DamlName("showString")
def show_string(str_value: str, str_value_1: str) -> str:
    pass


@DamlName("showInt")
def show_int(int_value: int, str_value: str) -> str:
    pass


@DamlName("showLitText")
def show_lit_text(str_value: str, str_value_1: str) -> str:
    pass


@DamlName("showLitChrs")
def show_lit_chrs(list_value: list[str], str_value: str) -> str:
    pass


@DamlName("showLitChr")
def show_lit_chr(c: str, str_value: str) -> str:
    pass


@DamlName("ctrlChrText")
def ctrl_chr_text(c: str) -> str:
    pass
