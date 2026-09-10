# How to add a new primitive or generic `.vy` type

This covers registering a new *type name* `.vy` source can write in an
annotation — either a **primitive** (no type arguments, like `str`/`Text`) or
a **generic** (takes type arguments, like `list[X]`/`GenMap[K, V]`). It does
not cover decorators (see `how-to-add-a-builtin-decorator.md`) or rejecting a
type outright (see `how-to-add-a-semantic-rejection.md`).

## The registry: `daml_builtin_type_names()`

Every type name usable in a `.vy` annotation without an import — `Party`,
`Decimal`, `str`, `list`, `Optional`, `GenMap`, `set` — comes from one place:
`daml_builtin_type_names()` in `forge/semantics/analysis/types.py`. It's a
union of three sources:

```python
def daml_builtin_type_names() -> set:
    from forge.builtins.maps import known_map_types

    return set(_get_primitive_types()) | set(_get_generic_types()) | set(known_map_types())
```

- `_get_primitive_types()` — 0-arity names (`Party`, `Decimal`, `str`, ...).
- `_get_generic_types()` — N-arity names that don't need a real backing class
  (`list`, `tuple`, `Optional`, `set`, `frozenset`).
- `known_map_types()` — the one family that genuinely needs a real, importable
  class (`GenMap`/`TextMap`), because `.vy` source can actually call methods
  on values of these types (see `how-to-add-a-builtin-decorator.md`'s sibling
  pattern in `forge/codegen/maps.py` for why).

**The type name resolving is entirely separate from codegen.** Registering a
name here only makes `.vy` source able to *write* it in an annotation without
tripping `check_type_annotation`'s "no builtin or user-defined type named X"
rejection (`DF1213`). It says nothing about what the compiled Daml looks
like — that's a second, independent step.

## Adding a primitive (0 type arguments)

Add a one-line marker class and list it in `_get_primitive_types()`:

```python
class PyStrT(_PrimT):
    _id = "str"
```

```python
def _get_primitive_types() -> dict:
    types = [
        PartyT(),
        TextT(),
        IntT(),
        PyIntT(),
        PyFloatT(),
        PyStrT(),
        ...
    ]
    return {t._id: t for t in types}
```

That's the *entire* semantic-layer registration — the marker class carries no
behavior, `_id` is the only thing that matters (it's what ends up as
`TypeRef.name`). Note the existing pattern of **dual spellings mapping to the
same Daml output**: `IntT._id = "Int"` and `PyIntT._id = "int"` are two
separate classes so both the Daml-style and the native-Python-style spelling
resolve — `str`/`Text` follow the identical shape.

Then teach codegen how to render it, in `forge/codegen/emit.py`'s
`_PRIMITIVE_TYPE_MAP`:

```python
_PRIMITIVE_TYPE_MAP = {
    "int": "Int",
    "Int": "Int",
    ...
    "str": "Text",
}
```

`_render_type_inner` falls through to `_PRIMITIVE_TYPE_MAP.get(t.name, t.name)`
for anything that isn't `list`/`tuple`/`Optional`/`ContractId`/a map/a set —
so a primitive with a 1:1 name mapping needs *only* this dict entry, no
dedicated render function.

## Adding a generic (takes type arguments)

If the type doesn't need real methods callable from `.vy` source, follow
`set`/`frozenset`'s shape — a marker class plus a small `forge/codegen/*.py`
module, no builtin class:

```python
class SetT(_GenericT):
    _id = "set"


class FrozenSetT(_GenericT):
    _id = "frozenset"
```

```python
def _get_generic_types() -> dict:
    types = [ContractIdT(), OptionalT(), ListT(), TupleT(), SetT(), FrozenSetT()]
    return {t._id: t for t in types}
```

**The semantic layer never validates arity.** `_walk_type_ref` only checks
that `type_ref.name` is a known name — `GenMap[Party]` (missing the value
type) or `set[Party, Decimal]` (too many) both pass semantic analysis
untouched. Arity is validated later, in codegen, by whatever `render_*`
function handles the type — see `forge/codegen/sets.py::render_set_type`:

```python
def render_set_type(t, render_type) -> str:
    if len(t.args) != _ARITY:
        raise CompilerPanic(
            f"render_set_type: `{t.name}` expects {_ARITY} type argument(s), got {len(t.args)}"
        )
    return f"{_MODULE}.{_MODULE} {render_type(t.args[0], as_arg=True)}"
```

This is a `CompilerPanic`, not a `DamlForgeException` — it's deliberately a
"should have been caught earlier" backstop, not a user-facing diagnostic. If
a type's arity mistakes are common enough to deserve a real error code and
message, add a proper semantic check instead (see
`how-to-add-a-semantic-rejection.md`) rather than relying on this panic.

Wire the new type into `forge/codegen/emit.py`'s `_render_type_inner`, in the
same `is_map_type`/`is_optional_type` style:

```python
if is_set_type(t.name):
    return render_set_type(t, render_type)
```

If the type needs an import in the generated Daml (`import DA.Set as Set`),
add a `required_imports(body_source)` function to the same codegen module,
matching `forge/codegen/maps.py`'s `_MAP_IMPORT_MARKERS`/`required_imports` —
pick a precise marker string (the type's *qualified prefix*, e.g. `"Set."`,
not a bare method name like `"insert"`) so you don't false-trigger on
unrelated generated code.

## If the type needs real methods callable from `.vy` source

`GenMap`/`TextMap` are the one case that needed a real, importable class
(`forge/builtins/maps.py`) instead of a bare marker — because `.vy` source
can write `some_map.insert(k, v)`, and that dispatch needs somewhere to look
up "is `insert` a real method of this type" from. If your new type needs the
same (method-call syntax, not just an annotation), follow
`forge/codegen/self_mutation.py`'s `SelfFieldRewriter` — the `_receiver_type`
+ `is_set_type`/`set_method_call` pattern generalizes directly.

**But check whether the type is a DamlForge invention first.** `GenMap`/
`TextMap` earned a real class because DamlForge invented those names — there
was no pre-existing Python equivalent. `Optional`/`set`/`frozenset` are
Python's own native types; they got the *lighter* treatment (plain constants
in a codegen module, no builtin class) specifically because DamlForge
doesn't own them and shouldn't pretend to. If you're adding support for
another native Python type, default to the lighter pattern unless there's a
concrete reason a real class is needed.

## Checklist

1. Decide: primitive (no args) or generic (takes args)?
2. Add the marker class(es) to `_get_primitive_types()` or
   `_get_generic_types()` in `forge/semantics/analysis/types.py`. Consider
   whether a dual native-Python/Daml spelling makes sense (like `int`/`Int`).
3. Primitive with a 1:1 Daml name: add one entry to `emit.py`'s
   `_PRIMITIVE_TYPE_MAP`. Generic, or a primitive that needs real rendering
   logic: add a small `forge/codegen/*.py` module (`is_X_type`/`render_X_type`
   at minimum), wire it into `_render_type_inner`.
4. If the type needs a Daml-side import, add `required_imports` to the same
   module and wire it into `_render_header`.
5. Only if `.vy` source needs to call real methods on values of this type:
   decide real class (DamlForge-invented type) vs. plain constants (native
   Python type), then wire method-call dispatch into `self_mutation.py`.
6. Add test fixtures to `tests/semantics/test_structure.py` (valid usage) and,
   if you touched codegen, verify rendered output directly or in
   `tests/compiler/test_codegen.py`.
