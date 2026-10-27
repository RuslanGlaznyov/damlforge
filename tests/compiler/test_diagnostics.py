# Copyright 2026 Noders Team
# Author: Artem Bogomaz <artembogomaz@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
