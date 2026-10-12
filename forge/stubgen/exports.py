import re
from typing import Optional

_COMMENT = re.compile(r"\{-.*?-\}|--[^\n]*", re.S)
_HEADER = re.compile(r"\bmodule\s+[\w.]+\s*\((.*?)\)\s*where\b", re.S)
_NAME = re.compile(r"^(?:type\s+|pattern\s+)?([A-Za-z_][\w]*)$")


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
