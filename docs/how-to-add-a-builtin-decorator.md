# How to add a new builtin `.vy` decorator

This covers decorators like `@choice(...)`, `@ledger_effect`, `@view`,
`@DamlName(...)` — the closed set of names DamlForge recognizes when they
appear in a `.vy` file's `decorator_list`. It does **not** cover registering
a plain callable builtin function (e.g. `days`, `add_rel_time`) — see
`forge/builtins/daml_lang.py` for that, a related but separate mechanism
(also driven by `@DamlName`, but applied to a real Python function instead
of subclassing `VyDecorator`).

## Why this isn't just "any importable name"

`.vy` source is never executed as Python — it's only parsed into an AST and
statically analyzed. So a decorator being a real, importable Python object
is not enough to make it meaningful: nothing calls it for real. Every
recognized decorator must have:

1. An explicit registration DamlForge's semantic checks can discover
   (`check_unknown_decorators` in `forge/semantics/analysis/structure.py`
   rejects anything else with `DF1220`, mirroring Vyper's own closed
   decorator grammar — see `vyper/semantics/types/function.py`'s
   `_parse_decorators`).
2. Defined codegen semantics, or it's a silent no-op that *looks* like it
   does something (this was a real bug: `@DamlName("Foo_Bar")` used to be
   importable and syntactically valid while doing nothing at all, because
   codegen never read its argument).

## Where decorators live

All recognized `.vy` decorators are defined in `forge/builtins/__init__.py`
as subclasses of `VyDecorator`. `forge/models/decorators.py` re-imports them
for backward compatibility (`from forge.models import choice`), but the
canonical definition — and the only place you need to add a new one — is
`forge/builtins/__init__.py`.

`known_decorator_names()` in that file auto-discovers every `VyDecorator`
subclass (and every function tagged `__vy_decorator__`) living in
`forge.builtins` or `forge.models.decorators`. **There is no separate
registration list to update** — defining the class is enough.

## Two shapes, depending on whether the decorator takes arguments

### Factory-style (takes arguments): `choice`, `DamlName`

Used as `@choice(controller=..., consuming=...)` — the decorator is
*instantiated* with args, then the instance is applied to the function.

```python
@dataclasses.dataclass(frozen=True)
class MyDecorator(VyDecorator):
    some_arg: str

    def __call__(self, fn):
        fn = super().__call__(fn)      # sets fn.__vy_decorator__ = True
        fn.__my_decorator__ = self.some_arg
        return fn

    def __post_init__(self) -> None:
        # optional: eager validation at construction time, e.g. reject
        # an empty/invalid argument immediately (see DamlName.__post_init__)
        ...

    @classmethod
    def __post_vy_check__(cls, container, fn, dec, errors):
        # required (VyDecorator.__post_vy_check__ is abstract) — validate
        # the *AST* shape of the decorator call as it appears in .vy source.
        # `dec` is the raw vy_ast.Call/Name node; nothing here was ever
        # actually constructed for real, so validate syntactically.
        ...
```

### Bare-marker style (no arguments): `ledger_effect`, `view`

Used as `@ledger_effect` — no parens, so Python calls `ledger_effect(fn)`
directly (the class *constructor*, not an instance's `__call__`). Override
`__new__` to tag and return `fn` itself instead of creating an instance:

```python
class MyMarker(VyDecorator):
    def __new__(cls, fn):
        fn.__vy_decorator__ = True
        fn.__my_marker__ = True
        return fn

    @classmethod
    def __post_vy_check__(cls, container, fn, dec, errors):
        from forge.models.error_codes import ErrorCodes

        if isinstance(dec, vy_ast.Call):
            errors.append(DamlForgeException(
                f"`@{cls.__name__}` on `{container.name}.{fn.name}` takes no arguments",
                fn, code=ErrorCodes.DF12XX.value,
            ))
```

## `__post_vy_check__`: your decorator's own validation

`VyDecorator.__post_vy_check__` is abstract — every subclass must implement
it (a no-op `pass` is fine if there's genuinely nothing to validate). It's
called automatically, once per occurrence, by
`check_unknown_decorators` for *every* known decorator found on a function,
with:

- `container` — the enclosing `TemplateDef`/`InterfaceDef`/`InstanceDef`
- `fn` — the decorated `FunctionDef`
- `dec` — the raw AST decorator node (`vy_ast.Call` if used with `(...)`,
  otherwise `vy_ast.Name`)
- `errors` — append `DamlForgeException(..., code=ErrorCodes.DFxxxx.value)`
  to report a problem; nothing is raised immediately, so multiple issues
  across a module are all collected and reported together

Use `container` to make decisions that depend on where the decorator
appears — e.g. `view.__post_vy_check__` checks `isinstance(container,
vy_ast.TemplateDef)` to reject `@view` inside a `template` (DF1207).

If you need a new error code, add it to `forge/models/error_codes.py`
(`DF1221` was the last one added, for `DamlName`'s argument-shape check).

## Making the decorator's argument affect generated Daml (optional)

Most decorators only need validation. If yours should influence the
*compiled output* — like `@DamlName("Foo_Bar")` overriding the emitted
choice name — you need a second piece in `forge/ir/lower.py`, since
`__post_vy_check__` only validates; it never runs during lowering. Add a
small AST-scanning helper (see `_daml_name_override` in `lower.py`) that
finds your decorator's `Call` node in `fn.decorator_list` and extracts its
argument, then use that value wherever the relevant `IR*` node is built
(see `lower_choice`'s `name=_daml_name_override(fn) or fn.name`).

Remember: nothing here executes your decorator's real `__call__`/`__new__`
— codegen has to read the argument straight off the AST node, the same way
`__post_vy_check__` does.

## Checklist

1. Define the class in `forge/builtins/__init__.py`, subclassing
   `VyDecorator`, choosing the factory or bare-marker shape.
2. Implement `__post_vy_check__` (required — validate the AST shape,
   append `DamlForgeException`s with a real error code for anything wrong).
3. Add a new `ErrorCodes` entry if needed.
4. If the decorator should affect generated Daml, add the corresponding
   AST-extraction + `IR*` wiring in `forge/ir/lower.py`.
5. Add test fixtures to `tests/semantics/test_structure.py` (valid usage,
   at least one invalid-shape case) and, if you touched codegen, to
   `tests/ir/test_lower.py`.
6. Nothing else — no manual registration, no allowlist to update. If it's
   missing from `known_decorator_names()`, check the class actually
   subclasses `VyDecorator` (or is tagged `__vy_decorator__`).
