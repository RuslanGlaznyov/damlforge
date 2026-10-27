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

# EXPERIMENTAL VYPER PARSER
import textwrap

from lark import Lark
from lark.indenter import Indenter


class PythonIndenter(Indenter):
    NL_type = "_NEWLINE"
    OPEN_PAREN_types = ["LPAR", "LSQB", "LBRACE"]
    CLOSE_PAREN_types = ["RPAR", "RSQB", "RBRACE"]
    INDENT_type = "_INDENT"
    DEDENT_type = "_DEDENT"
    tab_len = 4


_lark_grammar = None


def vyper_grammar():
    global _lark_grammar
    if _lark_grammar is None:
        _lark_grammar = Lark.open_from_package(
            "vyper",
            "grammar.lark",
            ("ast/",),
            parser="lalr",
            start="module",
            postlex=PythonIndenter(),
        )
    return _lark_grammar


def parse_vyper_source(code, dedent=False):
    if dedent:
        code = textwrap.dedent(code)
    return vyper_grammar().parse(code + "\n")
