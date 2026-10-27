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

import re

from forge.exceptions import StructureException


def validate_identifier(attr, ast_node=None):
    if not re.match("^[_a-zA-Z][a-zA-Z0-9_]*$", attr):
        raise StructureException(f"'{attr}' contains invalid character(s)", ast_node)
    if attr.lower() in RESERVED_KEYWORDS:
        raise StructureException(f"'{attr}' is a reserved keyword", ast_node)


# https://docs.python.org/3/reference/lexical_analysis.html#keywords
# note we don't technically need to block all python reserved keywords,
# but do it for hygiene
_PYTHON_RESERVED_KEYWORDS = {
    "False",
    "None",
    "True",
    "and",
    "as",
    "assert",
    "async",
    "await",
    "break",
    "class",
    "continue",
    "def",
    "del",
    "elif",
    "else",
    "except",
    "finally",
    "for",
    "from",
    "global",
    "if",
    "import",
    "in",
    "is",
    "lambda",
    "nonlocal",
    "not",
    "or",
    "pass",
    "raise",
    "return",
    "try",
    "while",
    "with",
    "yield",
}
_PYTHON_RESERVED_KEYWORDS = {s.lower() for s in _PYTHON_RESERVED_KEYWORDS}

# Cannot be used for variable or member naming
RESERVED_KEYWORDS = _PYTHON_RESERVED_KEYWORDS | {
    # "class" keywords
    "interface",
    "struct",
    "event",
    # special functions (no name mangling)
    "init",
    "_init_",
    "___init___",
    "____init____",
    "default",
    "_default_",
    "___default___",
    "____default____",
    # more control flow and special operations
    "range",
    # more special operations
    "indexed",
    # constants
    "inf",
}
