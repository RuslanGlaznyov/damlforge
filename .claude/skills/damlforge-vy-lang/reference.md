# DamlForge `.vy` Language Reference

`.vy` files are tokenized Python, re-keyworded by a pre-parser, then lowered straight to Daml source (`forge/ir`, `forge/codegen`). There is no runtime: nothing in a `.vy` file is ever executed by Python. Compile with:

```
python -m forge <file_or_dir> -o <out_dir>        # .vy -> .daml
python -m forge --dar <file_or_dir> -o <out_dir>  # .vy -> .daml -> real .dar via dpm build
python -m forge --json <file_or_dir>              # .vy -> JSON AST
```

## 1. Container keywords

The pre-parser rewrites these bare keywords (column 0) into Python `class`:

| `.vy` keyword | Compiles to | Real Daml shape |
|---|---|---|
| `struct Foo:` | plain data record | `data Foo = Foo with ...` |
| `template Foo:` | contract template | `template Foo where ...` |
| `interface Foo(view=V):` | interface | `interface Foo where viewtype V` |
| `instance Foo(Bar):` | interface implementation | `interface instance Bar for Foo where` |
| `flag Foo:` / `enum Foo:` | sum type of nullary constructors | `data Foo = A \| B \| ...` |

`@template\nclass Foo:` is an accepted alternative spelling of `template Foo:` (byte-identical output) - useful when you want a real decorator-looking header. It needs no import (the pre-parser consumes the `@template` line before it ever becomes a decorator call). **No other decorator combination with bare `class` is legal** - plain `class Foo:` and `@anything_else\nclass Foo:` both raise a hard `SyntaxException` at tokenize time.

`struct`/`interface`/`event`/`enum` (but not `template`/`instance`/`flag`) are also reserved identifiers - you cannot name a variable or field `struct`, etc.

`event`/`error` (`EventDef`/`ErrorDef`) parse but are not wired into codegen; the `exception` decorator explicitly raises `NotImplementedError` - none of these three are usable yet.

## 2. Type system

**Native Python types - always available, no import:** `str`, `int`, `float`, `bool`, `None`, `list[T]`, `tuple[T, ...]`, `set[T]`, `frozenset[T]`. `Optional[T]` needs `from typing import Optional` for the file to remain valid-looking Python, but the compiler itself doesn't require the import.

**DamlForge builtin types - recognized unconditionally by the type checker, but conventionally still imported from `forge.models` for readability:** `Party`, `Decimal`, `Int` (a distinct `Int` for real Daml `Int`, vs. Python `int`), `Date`, `Timestamp`, `RelTime`, `ContractId[T]`, `GenMap[K, V]`, `TextMap[V]`.

```python
from forge.models import ContractId, Decimal, Optional, Party, TextMap, Timestamp, choice
```

**Banned field types:** `dict[...]` and any unrecognized generic like `Map[...]` (`DF1213` - use `GenMap`/`TextMap`), and `bytes`/`bytearray`/`memoryview`/`complex`/`type`/`object`/`slice` (`DF1222` - no Daml equivalent).

**Type synonyms the checker treats as equal** when checking call-argument compatibility: `int`↔`Int`, `str`↔`Text`, `float`↔`Decimal`. A bare `X` is compatible where `Optional[X]` is expected (auto-wrapped, see §6). Generic args are checked recursively - `list[A]` is never compatible with `list[B]` unless `A`/`B` match.

**Your own types**: any `struct`/`template`/`interface`/`instance`/`flag` declared in a reachable module is automatically a valid type name - no import needed within the same module, real `from X import Y` needed across `.vy` files.

**Qualified module imports** - use when two real Daml packages export a same-named type (Daml itself would raise "Ambiguous occurrence" on an unqualified double-import):

```python
import Splice.Api.FeaturedAppRightV1 as FeaturedAppRightV1
import Splice.Api.FeaturedAppRightV2 as FeaturedAppRightV2
...
def f(x: FeaturedAppRightV1.FeaturedAppRight): ...
```

`from X import Y as Z` (aliased *from*-import) is banned outright, as is `from X import *`, importing the same name twice, and importing a module/name that doesn't actually resolve - all raise `DF1213`.

## 3. Decorators - always require import

Unlike ledger builtins (§4), decorators are ordinary Python objects with no compiler-side "always known" carve-out, so every one must be imported before use - an unimported decorator fails exactly like any other unresolved name (`DF1219`, "not defined"), not with a decorator-specific error.

```python
from forge.models import choice, ledger_effect, template, view, interface, instance
from forge.builtins import DamlName
```

| Decorator | Where legal | Rules |
|---|---|---|
| `@choice(controller=..., consuming=..., observer=...)` | method inside `template`/`interface`/`instance` | `controller` required (`DF1203`); `consuming` required, must be a literal `True`/`False` or one of `"preconsuming"`/`"consuming"`/`"nonconsuming"`/`"postconsuming"` (`DF1203`); name can't start with `_` (`DF1218`); `"preconsuming"` banned on `interface` choices, `"postconsuming"` banned on `instance` choices (`DF1208`) |
| `@view` | method inside `interface`/`instance` only | no args (`DF1206`); banned inside `template` (`DF1207`) |
| `@ledger_effect` | plain top-level `def` or method | bare only, no args (`DF1204`) |
| `@DamlName("RealName")` | any function/choice | exactly one string-literal positional arg (`DF1221`); overrides the auto-derived Daml-side name |
| `@template` | immediately before `class Foo:`, nothing else | see §1 |

### `controller=`/`observer=` name rules (`DF1224`)

Every bare name inside a choice's `controller=`/`observer=` expression must be one of: that choice's own `with`-arguments, one of the template's own declared fields, or `self`. `self.<attr>` is further checked to be a real field (not `self.signatory` - `signatory` is a Daml typeclass function, not a stored field). This exists because Daml's own name resolution would otherwise silently pick an unrelated same-named field elsewhere in the module, or fail with a confusing `damlc`-time "Ambiguous occurrence" error. This check only runs for `template` choices - `interface`/`instance` choices are skipped (they commonly need `(view this).x`-style access that `.vy` can't express yet).

```python
@choice(controller=owner, consuming=True)                 # owner: template field - OK
def transfer(self, new_owner: Party) -> bool: ...

@choice(controller=owner, consuming=True, observer=new_owner)   # new_owner is `transfer`'s
def rename(self, label: str) -> bool: ...                       # arg, not `rename`'s - DF1224
```

## 4. Ledger primitives - always available, no import

`fetch`, `exercise`, `create`, `archive`, `lookup`, `view` (interface view extraction, distinct from the `@view` decorator), `from_interface_contract_id`, `to_interface_contract_id`, `to_interface`, `coerce_interface_contract_id` (all `forge/builtins/daml_lang.py`) are treated as core language builtins - like `len`/`range`/`ceil`/`floor` - and resolve with **no import statement required**, even though real, introspectable Python objects back them (for tooling/codegen metadata). Importing them anyway (`from forge.builtins.daml_lang import fetch, create`) is harmless and matches most existing examples' style, but is not enforced.

```python
def f(cid: ContractId[Asset]) -> Asset:
    return fetch(cid)          # works with zero imports
```

### Hidden ledger effects (`DF1205`)

A plain `def` (not a `@choice`) that calls any of `fetch`/`exercise`/`create`/`archive`/`lookup` **must** be decorated `@ledger_effect`:

```python
@ledger_effect
def replace(new_owner: Party) -> bool:
    archive(self)          # OK - effect is declared
```

```python
def replace(new_owner: Party) -> bool:
    archive(self)          # DF1205 - hidden ledger effect
```

Choice bodies are exempt - a `@choice` method may call ledger builtins directly with no extra marker.

## 5. Template fields

```python
template Asset:
    owner: Party
    asset_id: Text

    signatory: list[Party] = [owner]        # required (DF1201 if missing)
    observer: list[Party] = [...]           # optional
    key: tuple[Party, Text] = (owner, asset_id)   # optional, but...
    maintainer: list[Party] = [owner]             # ...requires key, and vice versa (DF1210/DF1211)
    ensure: bool = amount > Decimal(0)      # optional; must be bool-typed comparison/boolop/call
                                             # (not bare arithmetic, not missing a value - DF1212)
```

`signatory`/`observer`/`key`/`maintainer`/`ensure` are special clause names, not ordinary fields - don't reference them via `self.signatory` etc. in choice logic (the compiler flags this as `DF1224`).

## 6. `Optional`, `Some`, auto-unwrapping

Never write `Some(...)` or `from_some(...)` by hand. Based on a field/return's declared `Optional[X]` type, the compiler automatically wraps a plain `X` value into `Some(X)` on assignment/return, and unwraps `Optional[X]` into `X` where a plain `X` is required. Just write the plain values:

```python
lock: Optional[Lock] = None
...
return HoldingView(..., lock=None, ...)     # compiler emits `None`
return HoldingView(..., lock=existing_lock, ...)   # if existing_lock: Lock, compiler emits `Some existing_lock`
```

## 7. Maps

```python
from forge.models import GenMap, TextMap

balances: GenMap[Party, Decimal] = {alice: Decimal(0), bob: Decimal(0)}
values: TextMap[str] = {}

balances[alice]                 # lookup
balances[alice] = Decimal(5)    # insert/update
alice in balances               # membership
```

`GenMap`/`TextMap` also expose `.insert(k, v)`, `.lookup(k)`, `.member(k)`, `.delete(k)`, `.keys()`, `.values()` if you prefer explicit method calls over subscript/`in` sugar.

## 8. Flags (sum types)

```python
flag PeriodPaymentStatus:
    PERIOD_PENDING
    PERIOD_PAID
```

Members **must** be `SCREAMING_CASE` (`DF1217` on lowercase or mixed case). Access via `PeriodPaymentStatus.PERIOD_PAID`, compare with `==`/`!=`. Flags have no payload and no methods.

## 9. Structs

Plain data records - fields only:

```python
struct InstrumentId:
    admin: Party
    id: str
```

**No methods.** A `def` inside a `struct` body is currently silently dropped (no error raised) - this mirrors a real gap relative to Vyper, which explicitly rejects struct methods with `StructureException`. Treat "structs can't have methods" as a hard rule and use a free top-level `def` instead:

```python
def update_milestone_if_due(paid_amount: Decimal, milestone: RepaymentMilestone) -> RepaymentMilestone:
    if milestone.paid or paid_amount < milestone.amount:
        return milestone
    return RepaymentMilestone(due_date=milestone.due_date, amount=milestone.amount,
                               paid=True, paid_date=milestone.paid_date)
```

## 10. Interfaces and instances

```python
struct HoldingView:
    owner: Party

interface Holding(view=HoldingView):
    @choice(controller=actors, consuming="nonconsuming")
    def withdraw(self, actors: list[Party], extra_args: ExtraArgs) -> bool:
        pass                      # interface choices are declared with `pass` bodies

template SimpleHolding:
    owner: Party
    issuer: Party
    signatory: list[Party] = [owner, issuer]

instance SimpleHoldingAsHolding(Holding):
    template = SimpleHolding

    @view
    def get_view(self) -> HoldingView:
        return HoldingView(owner=self.owner)

    @choice(controller=actors, consuming="nonconsuming")
    def withdraw(self, actors: list[Party], extra_args: ExtraArgs) -> bool:
        ...                       # instance re-implements the real choice body
```

`interface(view=..., requires=(...))` and `instance(InterfaceCls)` also exist as explicit function-call decorators (`forge/builtins/__init__.py`) for cases the bare `interface(...)`/`instance(...)` keyword forms don't cover, but the keyword forms above are the normal spelling.

## 11. Functions, loops, calls

Free top-level functions are plain `def`s; call-argument arity (`DF1225`) and type-compatibility (`DF1226`, only for `Name` arguments with a known declared type) are checked for any call to a known top-level `.vy` function.

Direct self-recursion is banned (`DF1209`) - a function/choice cannot call itself.

For-loops require an explicit type annotation on the loop variable before `in` (this is `.vy`-specific sugar the pre-parser slurps out, since bare PEP-526 annotations aren't legal there in real Python):

```python
for milestone: RepaymentMilestone in milestones:
    ...
for _index: int in range(0, count):
    ...
```

`len`, `range`, `ceil`, `floor` are always-available builtins (no import) and rename on the Daml side (`len`→`length`, `ceil`→`ceiling`; `floor`/`range` pass through).

## 12. Error code index

| Code | Meaning |
|---|---|
| DF1201 | template missing `signatory` |
| DF1203 | `@choice` missing `controller` or missing/invalid `consuming` |
| DF1204 | `@ledger_effect` given arguments |
| DF1205 | plain function has a hidden ledger effect (missing `@ledger_effect`) |
| DF1206 | `@view` given arguments |
| DF1207 | `@view` used inside a `template` |
| DF1208 | `"preconsuming"` on an interface choice, or `"postconsuming"` on an instance choice |
| DF1209 | direct self-recursion |
| DF1210 | `key` without `maintainer` |
| DF1211 | `maintainer` without `key` |
| DF1212 | `ensure` missing a value, or not a bool-typed comparison/boolop/call |
| DF1213 | import errors (wildcard, aliased from-import, duplicate, unresolvable) or a banned field type (`dict`, unknown map) |
| DF1216 | unknown flag member accessed |
| DF1217 | flag member not `SCREAMING_CASE` |
| DF1218 | choice name starts with `_` |
| DF1219 | name not defined / not in scope |
| DF1220 | unknown/unrecognized decorator |
| DF1221 | `@DamlName` given the wrong argument shape |
| DF1222 | field type with no Daml equivalent (`bytes`, `complex`, ...) |
| DF1224 | `controller=`/`observer=` references a name that isn't a with-arg/field/`self` |
| DF1225 | wrong argument count on a known function call |
| DF1226 | argument type incompatible with a known function's declared parameter type |

## 13. Worked example

```python
from forge.models import ContractId, Decimal, Optional, Party, TextMap, Timestamp, choice, view
from forge.builtins.daml_lang import archive, create

struct InstrumentId:
    admin: Party
    id: str

struct Metadata:
    values: TextMap[str]

struct HoldingView:
    owner: Party
    instrument_id: InstrumentId
    amount: Decimal
    meta: Metadata

interface Holding(view=HoldingView):
    pass

template SimpleHolding:
    owner: Party
    issuer: Party
    amount: Decimal
    instrument_id: InstrumentId

    signatory: list[Party] = [owner, issuer]

instance SimpleHoldingAsHolding(Holding):
    template = SimpleHolding

    @view
    def get_view(self) -> HoldingView:
        return HoldingView(
            owner=self.owner,
            instrument_id=self.instrument_id,
            amount=self.amount,
            meta=Metadata(values={}),
        )

template PendingTransfer:
    sender: Party
    receiver: Party
    amount: Decimal
    instrument_id: InstrumentId

    signatory: list[Party] = [sender]
    observer: list[Party] = [receiver]

    @choice(controller=receiver, consuming=True)
    def accept(self) -> ContractId[SimpleHolding]:
        assert self.amount > Decimal(0), "transfer amount must be positive"
        return create(SimpleHolding(
            owner=self.receiver,
            issuer=self.sender,
            amount=self.amount,
            instrument_id=self.instrument_id,
        ))
```

Full source: `examples/token_standard/token_standard.vy` (verified against real `dpm build`). `examples/crowd_loans/` is the largest real example, exercising `flag`, `GenMap`, nested `for` loops, and cross-package Splice imports.
