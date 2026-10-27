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
from typing import Optional

_COMMENT = re.compile(r"\{-.*?-\}|--[^\n]*", re.S)
_HEADER = re.compile(r"\bmodule\s+[\w.]+\s*\((.*?)\)\s*where\b", re.S)
_NAME = re.compile(r"^(?:type\s+|pattern\s+)?(?:[A-Z]\w*\.)*([A-Za-z_]\w*)$")


def _split(body: str) -> list:
    items = []
    depth = start = 0
    for index, ch in enumerate(body):
        depth += (ch == "(") - (ch == ")")
        if ch == "," and depth == 0:
            items.append(body[start:index])
            start = index + 1
    items.append(body[start:])
    return [item.strip() for item in items if item.strip()]


def export_items(source: str) -> Optional[list]:
    match = _HEADER.search(_COMMENT.sub("", source))
    if match is None:
        return None
    exports = []
    for item in _split(match.group(1)):
        if item.startswith("module "):
            exports.append(("module", item.split()[1]))
        elif found := _NAME.match(item.split("(", 1)[0].strip()):
            exports.append(("name", found.group(1)))
    return exports
