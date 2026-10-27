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


class Doc:
    __slots__ = ()


class Text(Doc):
    __slots__ = ("value",)

    def __init__(self, value: str):
        self.value = value


class Line(Doc):
    __slots__ = ()


class Nest(Doc):
    __slots__ = ("amount", "doc")

    def __init__(self, amount: int, doc: Doc):
        self.amount = amount
        self.doc = doc


class Concat(Doc):
    __slots__ = ("docs",)

    def __init__(self, docs):
        self.docs = tuple(docs)


def text(value: str) -> Doc:
    return Text(value)


def line() -> Doc:
    return Line()


def nest(amount: int, doc: Doc) -> Doc:
    return Nest(amount, doc)


def concat(docs) -> Doc:
    return Concat(docs)


def render(doc: Doc, initial_indent: int = 0) -> list:
    out = [" " * initial_indent]

    def go(node: Doc, indent: int) -> None:
        if isinstance(node, Text):
            out[-1] += node.value
        elif isinstance(node, Line):
            out.append(" " * indent)
        elif isinstance(node, Nest):
            go(node.doc, indent + node.amount)
        elif isinstance(node, Concat):
            for child in node.docs:
                go(child, indent)

    go(doc, initial_indent)
    return out
