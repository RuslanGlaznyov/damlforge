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

"""
isort:skip_file
"""

import sys

from . import nodes
from .nodes import as_tuple
from .utils import ast_to_dict
from .parse import parse_to_ast

# adds vyper.ast.nodes classes into the local namespace
for name, obj in (
    (k, v) for k, v in nodes.__dict__.items() if type(v) is type and nodes.VyperNode in v.__mro__
):
    setattr(sys.modules[__name__], name, obj)
