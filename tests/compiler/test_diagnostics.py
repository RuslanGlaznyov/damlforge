import pytest

from forge.ast.parse import parse_to_ast
from forge.exceptions import CompilerPanic
from forge.ir import lower_module


def test_internal_lowering_errors_include_source_context():
    source = "def broken() -> tuple(int, str):\n    pass\n"
    module = parse_to_ast(source, module_path="broken.vy", resolved_path="broken.vy")

    with pytest.raises(CompilerPanic) as error:
        lower_module(module)

    message = str(error.value)
    assert 'contract "broken.vy:1"' in message
    assert 'function "broken"' in message
    assert "line 1:16" in message
    assert "def broken() -> tuple(int, str):" in message
