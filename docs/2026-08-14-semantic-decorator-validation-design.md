# Semantic decorator + structural validation — design

## Status
Approved. First slice of `forge/semantics/`.

## Architecture
New pipeline stage, separate from parsing, matching `Compiler pipeline,
errors, and source mapping.md`'s stage 2 ("Name resolution and DamlForge
type/semantic checking"). Entry point: `forge.semantics.analyze_module(module:
vy_ast.Module) -> None`, called after `parse_to_ast()`, not fused into it.
Scoped to a single module — no cross-module name resolution/imports (that's
future work, distinct from Vyper's original `analyze_modules`).

## Layout
Matches the `forge/semantics/analysis/...` shape `forge/compiler/phases.py`
already expects (currently deferred/broken, but this is the right path to
eventually satisfy it):

```
forge/semantics/__init__.py           # analyze_module() entry point
forge/semantics/analysis/structure.py # the actual check functions
```

## Checks in this slice
1. `TemplateDef` must contain a `signatory` assignment in its body — checked
   by scanning `TemplateDef.body` for an `AnnAssign`/`Assign` whose target
   name is `"signatory"`. No new AST node type — pattern-matches on the
   target name rather than requiring the "reserved declaration"
   formalization from section C of `Type annotations and Daml type
   mapping.md` (still an open question there, not resolved by this slice).
2. A `FunctionDef` decorated with `@choice(...)` must have a `controller=`
   keyword argument.
3. `@choice(...)`'s `consuming=` keyword argument must be present and a
   literal `True`/`False` (matches `DF1203` from the doc).

`@ledger_effect`/`@view` validation (added after initial approval, same
slice):
4. `@ledger_effect` and `@view` must be bare markers — no call arguments.
5. A function not decorated `@ledger_effect` and not a `@choice` body must
   not call a ledger builtin (`create`/`fetch`/`exercise`/`archive`/
   `lookup`) anywhere in its body (`FunctionDef.get_descendants(Call)`) —
   "no hidden ledger effects."
6. `@view` is rejected outside `interface`/`instance` bodies (i.e. inside a
   `template`).

Not covered: cross-referencing an `instance`'s `@view` method against its
base `interface`'s declared `view=` type, or verifying an `instance`
implements all choices its interface declares — both need name resolution
across declarations, out of scope for this AST-only slice.

## Diagnostics
New `DamlForgeException(VyperException)` in `forge/exceptions.py` carrying
an optional `code` (e.g. `"DF1203"`). `analyze_module` collects violations
into the existing `ExceptionList` (already in `forge/exceptions.py`, unused
until now) and calls `raise_if_not_empty()` once at the end, so a module
with multiple problems reports all of them, not just the first.

## Approach chosen over the alternative
Rule-per-check collection into `ExceptionList`, rather than fail-fast
inline validation (like `FunctionDef.validate()` does today at parse time).
Fail-fast is simpler but only ever surfaces one error at a time and doesn't
reuse the multi-error machinery already present in the codebase.

## Testing
`tests/semantics/test_structure.py`, table-driven, at least 3 scenarios per
check (valid case, missing case, invalid-value case), asserting on the
specific `DamlForgeException`/code raised.
