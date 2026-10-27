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

from forge.exceptions import CompilerPanic
from forge.ir.nodes import IRCall, IRName

_TYPE_NAMES = frozenset({"set", "frozenset"})

_ARITY = 1

_MODULE = "Set"

_METHODS = frozenset({"insert", "delete", "member", "size", "toList", "null"})


def is_set_type(name: str) -> bool:
    return name in _TYPE_NAMES


def render_set_type(t, render_type) -> str:
    if len(t.args) != _ARITY:
        raise CompilerPanic(
            f"render_set_type: `{t.name}` expects {_ARITY} type argument(s), got {len(t.args)}"
        )
    return f"{_MODULE}.{_MODULE} {render_type(t.args[0], as_arg=True)}"


_IMPORT_MARKER = f"{_MODULE}."
_IMPORT_LINE = f"import DA.Set as {_MODULE}\n\n"


def required_imports(body_source: str) -> list:
    return [_IMPORT_LINE] if _IMPORT_MARKER in body_source else []


def known_set_methods() -> frozenset:
    return _METHODS


def set_method_call(method: str, args, receiver):
    if method not in _METHODS:
        return None
    return IRCall(IRName(f"{_MODULE}.{method}"), tuple(args) + (receiver,))
