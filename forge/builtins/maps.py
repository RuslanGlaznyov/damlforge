from typing import Generic, TypeVar

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


class DamlMapType:
    arity: int
    module: str

    def __init__(self, items=()):
        self._data = dict(items)

    def insert(self, key, value):
        new_data = dict(self._data)
        new_data[key] = value
        return type(self)(new_data.items())

    def lookup(self, key):
        return self._data.get(key)

    def member(self, key) -> bool:
        return key in self._data

    def delete(self, key):
        new_data = dict(self._data)
        new_data.pop(key, None)
        return type(self)(new_data.items())

    def keys(self):
        return list(self._data.keys())

    def values(self):
        return list(self._data.values())

    def __eq__(self, other):
        return isinstance(other, DamlMapType) and self._data == other._data

    def __repr__(self):
        return f"{type(self).__name__}({self._data!r})"

    @classmethod
    def method_names(cls) -> frozenset:
        return frozenset(
            name for name, value in vars(DamlMapType).items() if not name.startswith("_") and callable(value)
        )


class TextMap(DamlMapType, Generic[T]):
    arity = 1
    module = "TextMap"


class GenMap(DamlMapType, Generic[K, V]):
    arity = 2
    module = "Map"


def known_map_types() -> dict:
    return {cls.__name__: cls for cls in (TextMap, GenMap)}
