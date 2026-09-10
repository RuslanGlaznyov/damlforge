# How to add a new semantic rejection

"Semantic rejection" here means: `.vy` source that parses fine syntactically,
but should be a compile error — a `DamlForgeException` with a `DFxxxx` code,
collected into the `ExceptionList` and reported to the user, as opposed to
silently compiling to wrong Daml or crashing with a `CompilerPanic`.

Where the check belongs depends on *what* you're rejecting. There are four
different places, not one — picking the wrong one means duplicating work an
existing pass already does, or a check that never actually runs.

## Which mechanism do you need?

| You're rejecting... | Lives in | Example |
|---|---|---|
| A type name in an annotation | `_walk_type_ref` (`forge/semantics/analysis/types.py`) | `DF1213` unknown type, `DF1222` unmappable type |
| A bare name used as a call target or attribute base in an *expression* | `check_unresolved_names` (`types.py`) | `DF1219` |
| A decorator name itself | `check_unknown_decorators` (`forge/semantics/analysis/structure.py`) | `DF1220` |
| A decorator's own argument shape | that decorator's `__post_vy_check__` (`forge/builtins/*.py`) | `DF1221` (`DamlName`) |
| Anything else structural (missing field, wrong shape, naming convention) | a dedicated `check_*` function wired into `check_container` (`structure.py`) | `DF1201` signatory, `DF1218` choice naming |

If what you're rejecting doesn't fit any of these — e.g. it depends on
*value*, not just name/shape (like the map/optional/set method-call checks
in `self_mutation.py`, which fire during lowering, not semantic analysis) —
it may belong in codegen instead, as a `CompilerPanic`. Use a
`DamlForgeException`/`DFxxxx` when the mistake is something a `.vy` author
could plausibly write and needs a clear diagnostic for; use `CompilerPanic`
when it's an internal invariant that semantic analysis should have already
caught (see `render_set_type`'s arity check in
`how-to-add-a-primitive-type.md` for that distinction).

## Worked example: rejecting a type name (`DF1222`)

This is the simplest case, and the one most new type-related rejections need.
`bytes`/`complex`/`object`/etc. resolve fine as Python names but have no Daml
equivalent — rather than let them fall through to the generic "no builtin or
user-defined type" message, they get a specific one.

1. **Add the error code.** `forge/models/error_codes.py`:

   ```python
   DF1222 = "DF1222"
   ```

   Codes are sequential, never reused — check the last one in the file.

2. **Add the check inside `_walk_type_ref`** (`forge/semantics/analysis/types.py`), *before* the "unknown type" branch, since an unmappable name is also technically "unknown" to `known_names` and you want the more specific message to win:

   ```python
   _UNMAPPABLE_PYTHON_TYPES = frozenset(
       {"bytes", "bytearray", "memoryview", "complex", "type", "object", "slice"}
   )


   def _walk_type_ref(type_ref: TypeRef, known_names: set, node, context: str, errors: ExceptionList) -> None:
       if type_ref.name in _UNMAPPABLE_PYTHON_TYPES:
           errors.append(
               DamlForgeException(
                   f"`{type_ref.name}` has no Daml equivalent and cannot be used as a type ({context})",
                   node,
                   code=ErrorCodes.DF1222.value,
               )
           )
       elif type_ref.name not in known_names:
           ...  # existing DF1213 branch
       for arg in type_ref.args:
           _walk_type_ref(arg, known_names, node, context, errors)
   ```

   No new call site needed — `_walk_type_ref` is already invoked from every
   annotation-checking entry point (`check_function_type_annotations`,
   `check_struct_type_annotations`, `check_template_field_type_annotations`,
   `check_interface_view_type_annotation`), all funneling through
   `check_type_annotation`. Add the rule once, it applies everywhere an
   annotation is checked, including nested (`list[bytes]`,
   `GenMap[Party, complex]`) — the recursive `for arg in type_ref.args` walk
   handles that for free.

3. **Verify directly** before reaching for the test suite — annotate a field
   with the rejected name and confirm the message/code:

   ```python
   module = parse_to_ast(source, module_path="test.vy", resolved_path="test.vy")
   analyze_module(module)  # should raise DamlForgeException with code == "DF1222"
   ```

4. **Add a fixture to `tests/semantics/test_structure.py`**, wired into
   `test_invalid_template_raises`'s parametrized list — one fixture is
   usually enough for a type-name rejection, since the logic is identical
   for every rejected name (no need for one fixture per name in
   `_UNMAPPABLE_PYTHON_TYPES`).

## The other three mechanisms, briefly

- **`check_unresolved_names`** is for *expressions*, not annotations — a call
  target (`SomeFunc(...)`) or attribute base (`SomeThing.attr`) that doesn't
  resolve against local variables, declarations, or `known_global_names()`.
  If you're rejecting a bare name used as a value, not a type, this is the
  place — but check `known_global_names()` first, since a name that should
  legitimately resolve (a new builtin function, an import) belongs there
  instead of a rejection.

- **`check_unknown_decorators`** is a *closed vocabulary* check, deliberately
  separate from `check_unresolved_names` — decorators are DSL grammar
  (mirroring Vyper's own `_parse_decorators`), not general-purpose name
  resolution. See `how-to-add-a-builtin-decorator.md` for the full pattern;
  don't add decorator-specific logic to `check_unresolved_names` or
  `_walk_type_ref`.

- **A dedicated `check_*` structural function** is for everything that isn't
  "is this name/type known" — required fields, naming conventions, argument
  presence, cross-field consistency. Each one is independent, takes the
  declaration node + `errors`, and gets wired into `check_container`'s
  `TemplateDef`/`InterfaceDef`/`InstanceDef`/`FlagDef` branches as
  appropriate. Look at `check_template_signatory` (`DF1201`) for the
  simplest shape, or `check_choice_decorators`-turned-`choice.__post_vy_check__`
  (`DF1203`/`DF1218`) for one that moved onto a decorator's own class instead
  — prefer that shape (validation owned by the thing being validated) over a
  free-standing `structure.py` function when the check is specific to one
  decorator/type's own usage, not a general container-shape rule.

## Checklist

1. Identify which of the four mechanisms fits — don't default to
   `check_unresolved_names` or a new `structure.py` function just because
   they're the most general; a type-annotation rejection that goes through
   `_walk_type_ref` gets nested-type coverage for free that a hand-rolled
   check wouldn't.
2. Add the next sequential `DFxxxx` code to `forge/models/error_codes.py`.
3. Add the check at the identified call site — reuse the existing traversal
   rather than adding a new one over the same AST.
4. Verify directly against a minimal `.vy` snippet before writing tests.
5. Add a fixture to `tests/semantics/test_structure.py`'s
   `test_invalid_template_raises` (or the relevant existing parametrized
   test), asserting on the exact `DFxxxx` code, not just "an exception was
   raised."
