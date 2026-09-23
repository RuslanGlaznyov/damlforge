from pathlib import Path

import pytest

from forge.ast.parse import parse_to_ast
from forge.exceptions import DamlForgeException
from forge.models.error_codes import ErrorCodes
from forge.semantics import analyze_module

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "type_annotations"


def _fixture_path(name: str) -> Path:
    return FIXTURES_DIR / name


def _read_fixture(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _analyze(source: str) -> None:
    module = parse_to_ast(source, module_path="test.vy", resolved_path="test.vy")
    analyze_module(module)


@pytest.mark.parametrize(
    "source_path",
    [
        _fixture_path("valid/primitive_field_types_are_allowed.vy"),
        _fixture_path("valid/generic_field_types_are_allowed.vy"),
        _fixture_path("valid/local_struct_reference_is_allowed.vy"),
    ],
    ids=lambda path: path.stem.upper(),
)
def test_known_types_pass(source_path):
    _analyze(_read_fixture(source_path))


@pytest.mark.parametrize(
    "source_path,expected_code",
    [
        (_fixture_path("invalid/template_field_unknown_type.vy"), ErrorCodes.DF1213.value),
        (_fixture_path("invalid/struct_field_unknown_type.vy"), ErrorCodes.DF1213.value),
        (_fixture_path("invalid/choice_arg_unknown_type.vy"), ErrorCodes.DF1213.value),
        (_fixture_path("invalid/choice_return_unknown_type.vy"), ErrorCodes.DF1213.value),
        (_fixture_path("invalid/function_arg_unknown_type.vy"), ErrorCodes.DF1213.value),
        (_fixture_path("invalid/interface_view_unknown_type.vy"), ErrorCodes.DF1213.value),
        (_fixture_path("invalid/nested_generic_unknown_type.vy"), ErrorCodes.DF1213.value),
    ],
)
def test_unknown_type_raises(source_path, expected_code):
    with pytest.raises(DamlForgeException) as exc_info:
        _analyze(_read_fixture(source_path))

    assert exc_info.value.code == expected_code
