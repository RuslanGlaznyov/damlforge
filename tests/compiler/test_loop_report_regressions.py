import pytest

from forge.ast.parse import parse_to_ast
from forge.codegen import generate_daml
from forge.exceptions import DamlForgeException
from forge.ir import lower_module
from forge.semantics import analyze_module


def _compile(source: str) -> str:
    module = parse_to_ast(source, module_path="loop_report.vy", resolved_path="loop_report.vy")
    analyze_module(module)
    ir = lower_module(module)
    return generate_daml(ir, module_name="LoopReport")[0]


def test_nested_fold_uses_current_captured_binding_and_tuple_assignment_is_simultaneous():
    daml = _compile("""
from forge.models import Party

def f(xs: list[int]) -> int:
    a: int = 0
    b: int = 0
    for x: int in xs:
        a = a + x
        for y: int in xs:
            b = b + a * y
    return a * 1000 + b

def swap(xs: list[int]) -> int:
    a: int = 0
    b: int = 1
    for x: int in xs:
        a, b = b, a + x
    return a * 1000 + b
""")
    assert "_damlforge_a1 * y" in daml
    assert "_damlforge_tuple" in daml
    assert "let (a, b) = (b, a)" not in daml


def test_struct_and_self_list_mutation_become_fold_state():
    daml = _compile("""
from forge.models import Party, choice, template

struct Acc:
    s: int

def sum_fields(xs: list[int]) -> int:
    acc: Acc = Acc(s=0)
    for x: int in xs:
        acc.s = acc.s + x
    return acc.s

@template
class Box:
    owner: Party
    xs: list[int]
    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=False)
    def Add(self) -> int:
        for x: int in [1, 2]:
            self.xs.append(x)
        return len(self.xs)
""")
    assert "foldl" in daml
    assert "acc { s =" in daml
    assert "self { xs = self.xs <>" in daml
    assert ".append" not in daml


def test_effectful_lazy_operands_are_lowered_inside_action_branches():
    daml = _compile("""
from forge.models import ContractId, Party, choice, template

@template
class Item:
    owner: Party
    value: int
    signatory: list[Party] = [owner]

@template
class Box:
    owner: Party
    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=False)
    def Read(self, cids: list[ContractId[Item]]) -> int:
        total: int = 0
        for c: ContractId[Item] in cids:
            total = total + (fetch(c).value if total >= 0 else 0)
        return total
""")
    assert "foldlA" in daml
    assert "<- fetch c" in daml
    assert "if total >= 0 then (fetch c).value" not in daml


def test_loop_scoped_values_are_carried_as_optional_fold_state():
    daml = _compile("""
def f(xs: list[int]) -> int:
    total: int = 0
    for x: int in xs:
        total = total + x
    return total + x
""")
    assert "Some x" in daml
    assert "fromSome" in daml
    assert "import DA.Optional (fromSome)" in daml


def test_reported_expression_lowerings_are_buildable_shapes():
    daml = _compile("""
from forge.models import Decimal, TextMap

def f(i: int, x: int, m: TextMap[int]) -> Decimal:
    return Decimal(0.0000005) if x not in [[5]][i] else Decimal(1)

def g(xs: list[int], m: TextMap[int]) -> int:
    total: int = 0
    for x: int in range(5, 0, -2):
        total = total + x
    return total + len(m.keys())
""")
    assert "0.0000005 : Decimal" in daml
    assert "notElem" in daml
    assert "TextMap.toList" in daml
    assert "5, 5 + (-2)" in daml


def test_duplicate_enum_constructors_are_rejected_before_daml_generation():
    with pytest.raises(DamlForgeException, match="constructors must be unique"):
        _compile("""
from enum import Enum, auto

class First(Enum):
    SAME = auto()

class Second(Enum):
    SAME = auto()
""")
