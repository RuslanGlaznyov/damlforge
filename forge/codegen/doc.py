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
