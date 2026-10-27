# Language Fundamentals

A `.vy` file reads like Python, but it means Daml. Every type, function, and
statement you write has a direct Daml equivalent, and the compiler emits exactly
that equivalent. If you know Python, the syntax is familiar. If you know Daml, the
behaviour is familiar. This page covers both sides.

The examples build one module step by step. Joined in order, the `python` blocks
on this page form one valid file, `Fundamentals.vy`, which compiles and builds
into a DAR. Blocks marked `py` show code the compiler rejects or that you
should avoid.

## How `.vy` differs from Python

Keep these rules in mind. Most of the rest follows from them.

- **Nothing executes.** `forge` parses the file and lowers it to Daml. Python's
  runtime, standard library, and third-party packages aren't available. Only the
  constructs on this page are.
- **Values are immutable.** Daml has no mutation. When you reassign a variable or
  a field, the compiler rewrites it as a new value: a `let` binding, a record
  update, or a fold.
- **Types are checked at compile time.** Every function parameter and return
  value needs an annotation. Mismatches fail before Daml is generated.
- **Contracts are never edited.** A contract can only be created or archived.
  "Changing" a contract means archiving it and creating a new one with a new
  contract ID.

## Imports

```python
from datetime import date, datetime, timedelta
from enum import Enum, auto
from typing import Optional

from forge.builtins.daml_lang import create, exercise, fetch
from forge.models import ContractId, Decimal, GenMap, Party, TextMap, choice, template, variant
```

Import rules:

- Contract decorators (`@template`, `@variant`, `@choice`, `@view`,
  `@variant_record`) and DamlForge types come from `forge.models`. An unimported
  decorator fails with `DF1219`.
- Dates and times use Python's own `datetime` module.
- Enums use Python's `enum` module.
- Ledger operations (`create`, `fetch`, `exercise`, `archive`, `fetch_by_key`) come
  from `forge.builtins.daml_lang`. Import each one you use.
- `len`, `range`, `ceil`, and `floor` are built in and need no import.
- Aliased from-imports (`from X import Y as Z`) and wildcard imports are rejected
  with `DF1213`. When two packages export the same name, use a module alias such
  as `import Splice.Api.FeaturedAppRightV1 as FeaturedAppRightV1`.

## Native types

| `.vy` type | Daml type | Literal or constructor |
|---|---|---|
| `bool` | `Bool` | `True`, `False` |
| `int` | `Int` | `42` |
| `Decimal` | `Decimal` | `Decimal(0)`, `Decimal(1.5)` |
| `str` | `Text` | `"hello"` |
| `Party` | `Party` | Comes from the ledger, never written as a literal |
| `ContractId[T]` | `ContractId T` | Returned by `create`, passed in as an argument |
| `date` | `Date` | `date(2026, 12, 31)` |
| `datetime` | `Time` | `datetime.now()` inside an update |
| `timedelta` | `RelTime` | `timedelta(days=7, hours=12)` |
| `Optional[T]` | `Optional T` | A plain `T` value, or `None` |
| `list[T]` | `[T]` | `[1, 2, 3]` |
| `tuple[A, B]` | `(A, B)` | `(1, "one")` |
| `GenMap[K, V]` | `Map K V` | `{alice: Decimal(0)}` |
| `TextMap[V]` | `TextMap V` | `{"key": "value"}` |

`bytes`, `complex`, `object`, `type`, and other types with no Daml equivalent are
rejected with `DF1222`. `dict[K, V]` is rejected with `DF1213`; use `GenMap` or
`TextMap` instead.

## Functions

A top-level `def` becomes a Daml function with an explicit signature. Annotate
every parameter and the return type:

```python
def increment(n: int) -> int:
    return n + 1


def greet(name: str) -> str:
    return "Hello, " + name


def half(amount: Decimal) -> Decimal:
    return amount / Decimal(2)
```

```haskell
increment : Int -> Int
increment n =
  n + 1

greet : Text -> Text
greet name =
  "Hello, " <> name
```

Arithmetic, comparison, and boolean operators keep their Python spelling. A few
of them lower to a different Daml operator:

| `.vy` | Daml |
|---|---|
| `a + b` on `str` | `a <> b` |
| `a + b` on lists | `a ++ b` |
| `a and b`, `a or b`, `not a` | `a && b`, `a \|\| b`, `not a` |
| `a != b` | `a /= b` |
| `a // b` | A generated helper with Python's floor-division semantics |
| `len(xs)` | `length xs` |

The compiler checks calls to your own functions. A wrong argument count fails with
`DF1225`, and an argument of the wrong type fails with `DF1226`.

A function can't call itself. Direct recursion is rejected with `DF1209`. Use a
`for` loop, which compiles to a fold, instead.

## Assembling types

### Tuples

Tuples group values without naming them. Index them with `[0]`, `[1]`, and so
on:

```python
def coords() -> tuple[int, int]:
    return (1, 2)


def pair_sum(pair: tuple[int, int]) -> int:
    return pair[0] + pair[1]
```

```haskell
pair_sum : (Int, Int) -> Int
pair_sum pair =
  (pair._1) + (pair._2)
```

### Lists

```python
def append_one(xs: list[int]) -> list[int]:
    return xs + [1]


def first_or_zero(xs: list[int]) -> int:
    if len(xs) == 0:
        return 0
    return xs[0]
```

`xs + [1]` builds a new list and leaves `xs` unchanged. Indexing with `xs[i]`
lowers to `DA.List.(!!)`, which walks the list. Daml lists are linked lists, so
iterate with `for` where you can.

### Structs

A `struct` is a named record, the Daml `data T = T with ...`. Use it to give
structure to contract data:

```python
struct Bank:
    party: Party
    name: str


struct Account:
    number: str
    bank: Bank
```

```haskell
data Bank = Bank
  with
    party : Party
    name : Text
  deriving (Eq, Show)
```

Build a struct with keyword arguments and read fields with dot access. Every
struct derives `Eq` and `Show`, so `==` works on it:

```python
struct Point:
    x: int
    y: int


def shift(p: Point, dx: int) -> Point:
    return Point(x=p.x + dx, y=p.y)
```

Structs hold data only. A `def` inside a `struct` body is dropped without any
error, so put helper logic in a top-level function:

```py
struct Point:
    x: int
    y: int

    def norm(self) -> int:
        return self.x + self.y
```

### Enums

An enum is a sum type whose constructors carry no data. Use Python's `Enum` with
bare names or `auto()`. Explicit values such as `USD = 1` are rejected with
`DF1231`:

```python
class Currency(Enum):
    USD = auto()
    EUR = auto()


def is_euro(c: Currency) -> bool:
    return c == Currency.EUR
```

```haskell
data Currency = USD | EUR
  deriving (Eq, Show)

is_euro : Currency -> Bool
is_euro c =
  c == EUR
```

### Variants

When constructors carry data, use `@variant`. Each method declares one
constructor, and its parameters are the payload:

```python
@variant
class Location:
    def InHand(): pass
    def InAccount(account: Account): pass
```

```haskell
data Location
  = InHand
  | InAccount Account
  deriving (Eq, Show)
```

Constructors are positional by default, so parameter names don't appear in Daml.
When the Daml API needs named fields (`Constructor with field : T`), mark the
constructor with `@variant_record`, imported from `forge.models`.
[Variants](11-variants.md) covers constructing, comparing, and testing variant
values, and what isn't supported yet.

### Optional values

`Optional[T]` is Daml's replacement for `null`. Write plain values: the compiler
inserts `Some` and `fromSome` based on the declared types.

```python
def maybe_name(flag: bool, name: str) -> Optional[str]:
    if flag:
        return name
    return None


def name_or_default(name: Optional[str]) -> str:
    if name is not None:
        return name
    return "anonymous"
```

```haskell
maybe_name : Bool -> Text -> (Optional Text)
maybe_name flag name =
  ...
  if flag
    then
      Some name
    ...

name_or_default : (Optional Text) -> Text
name_or_default name =
  ...
  if name /= None
    then
      fromSome name
    ...
```

Never write `Some(...)` or `from_some(...)` yourself. Check `is not None` before
using the value: unwrapping a `None` fails the transaction at runtime.

### Maps

`GenMap[K, V]` maps any comparable key type to values. `TextMap[V]` uses `str`
keys. Both are immutable, so `insert` returns a new map:

```python
def has_key(names: GenMap[Party, str], key: Party) -> bool:
    return names.member(key)


def get_label(names: GenMap[Party, str], key: Party) -> Optional[str]:
    return names.lookup(key)


def add_label(names: GenMap[Party, str], key: Party, label: str) -> GenMap[Party, str]:
    return names.insert(key, label)


def find_name(names: TextMap[str], key: str) -> Optional[str]:
    return names.lookup(key)
```

Maps also support `.delete(k)`, `.keys()`, and `.values()`.

On template fields, you can use subscript and `in` syntax: `self.names[who]`,
`self.names[who] = label`, and `who in self.names`. See
[Changing a contract](#changing-a-contract).

> **Known limitation:** For maps passed as function parameters, use the method
> forms. `key in names` and `names[key]` on a parameter currently generate
> list operations, and `damlc` rejects the result.

## Control flow

### Branches

`if`, `elif`, and `else` compile to nested Daml `if ... then ... else`. Every
path of a function must return a value of the declared type:

```python
def describe(n: int) -> str:
    if n < 0:
        return "negative"
    elif n == 0:
        return "zero"
    else:
        return "positive"


def larger(a: int, b: int) -> int:
    return a if a > b else b
```

A conditional expression (`a if cond else b`) maps one-to-one to Daml's inline
`if`. An early `return` is fine: the compiler moves the code after the `if` into
the `else` branch.

### Loops

Daml has no mutable loop variable. A `for` loop compiles to a `foldl` that
threads every reassigned variable through as an accumulator:

```python
def total(values: list[Decimal]) -> Decimal:
    acc: Decimal = Decimal(0)
    for value: Decimal in values:
        acc = acc + value
    return acc
```

```haskell
total : [Decimal] -> Decimal
total values =
  let (acc : Decimal) = (0.0 : Decimal) in
  let _damlforge_acc2 =
        foldl
          (\acc value ->
            let _damlforge_acc1 = acc + value in
            _damlforge_acc1)
          acc values
  in
  _damlforge_acc2
```

The loop-variable annotation (`value: Decimal`) is `.vy` syntax. It's optional
when the iterable's type is known. `range(start, stop)` lowers to
`[start .. stop - 1]`, and `if` inside a loop body works as expected:

```python
def evens(n: int) -> list[int]:
    result: list[int] = []
    for i in range(0, n):
        if i % 2 == 0:
            result = result + [i]
    return result
```

`while` loops have no fold equivalent, so they aren't supported.

These loops are pure. A loop that reads or writes the ledger compiles to
`foldlA` instead. See [Loops with ledger effects](#loops-with-ledger-effects).

### Assertions

`assert condition, "message"` lowers to `assertMsg`. A failed assertion aborts
the whole transaction, so use it in choices to reject invalid input. An example
appears in [Changing a contract](#changing-a-contract).

## Dates and time

Use Python's `datetime` types. The compiler maps each operation to `DA.Time` or
`DA.Date`:

```python
def deadline(start: datetime) -> datetime:
    return start + timedelta(days=7)


def year_end() -> date:
    return date(2026, 12, 31)


def stamp() -> datetime:
    return datetime.now()
```

```haskell
deadline : Time -> Time
deadline start =
  addRelTime start (days 7)

year_end : Date
year_end =
  date 2026 Dec 31

stamp : Update Time
stamp = do
  getTime
```

- Months are Python-style integers, `1` through `12`.
- `timedelta` supports `weeks`, `days`, `hours`, `minutes`, `seconds`,
  `milliseconds`, and `microseconds`. Calendar years aren't fixed-length, so
  `years=` isn't supported.
- Subtracting two `datetime` values gives a `timedelta` (`subTime`).
- `datetime.now()` reads ledger time, so `stamp` returns `Update Time`. The next
  section explains why.
- Only these constructs are translated, not the whole `datetime` module.
  Attributes and methods such as `.date()` or `.weekday()` aren't available yet;
  [Working with Time](07-working-with-time.md#time-types) lists what works and the
  `DA.Date` helpers to use instead.

## Templates and contracts

A template is a contract schema. Think of it as a table where each contract is a
row. Fields are the columns, and a few reserved names hold the contract's
authorization rules:

```python
@template
class CashBalance:
    owner: Party
    bank: Bank
    currency: Currency
    amount: Decimal
    location: Location

    signatory: list[Party] = [bank.party, owner]
    ensure: bool = amount > Decimal(0)

    @choice(controller=owner, consuming=True)
    def move(self, new_location: Location) -> ContractId[CashBalance]:
        return create(CashBalance(
            owner=self.owner,
            bank=self.bank,
            currency=self.currency,
            amount=self.amount,
            location=new_location,
        ))
```

```haskell
template CashBalance
  with
    owner : Party
    bank : Bank
    currency : Currency
    amount : Decimal
    location : Location
  where
    signatory [bank.party, owner]
    ensure amount > (0.0 : Decimal)

    choice Move : ContractId CashBalance
      with
        new_location : Location
      controller owner
      do
        let self = this
        create (CashBalance with owner = self.owner, bank = self.bank, currency = self.currency, amount = self.amount, location = new_location)
```

| Clause | Meaning | Rule |
|---|---|---|
| `signatory` | Parties whose authority the contract needs | Required (`DF1201`). A single `Party` or a `list[Party]` |
| `observer` | Parties who can see the contract | Optional |
| `ensure` | A precondition checked on every create | Must be a `bool` comparison, boolean operation, or call (`DF1212`) |
| `key` / `maintainer` | A contract key and the parties who maintain it | Declare both or neither (`DF1210`, `DF1211`) |

An `__init__` method whose body contains `assert` statements also becomes
`ensure`. The examples in the repository use that form.

A choice is a method decorated with `@choice`. `controller` names the parties
who may exercise it. `consuming=True` archives the contract when the choice is
exercised, and `consuming=False` leaves it active (`nonconsuming` in Daml). Choice
names are capitalized in Daml: `move` becomes `Move`. Use `@DamlName("Name")`,
imported from `forge.builtins`, to choose the Daml name yourself.

`controller` and `observer` may only refer to template fields, the choice's own
arguments, or `self.<field>`. Anything else fails with `DF1224`.

### Changing a contract

Contracts are immutable, but a consuming choice can assign to `self`. The
compiler turns each assignment into a record update and creates a new contract
from the final value:

```python
@template
class Counter:
    owner: Party
    count: int
    history: list[int]

    signatory: Party = owner

    @choice(controller=owner, consuming=True)
    def bump(self, by: int) -> int:
        assert by > 0, "by must be positive"
        self.count = self.count + by
        self.history = self.history + [by]
        return self.count

    @choice(controller=owner, consuming=False)
    def peek(self) -> int:
        return self.count


@template
class Registry:
    admin: Party
    names: GenMap[Party, str]

    signatory: Party = admin

    @choice(controller=admin, consuming=True)
    def register(self, who: Party, label: str) -> int:
        if who in self.names:
            self.names[who] = self.names[who] + "!"
        else:
            self.names[who] = label
        return len(self.names.keys())
```

```haskell
    choice Bump : (ContractId Counter, Int)
      with
        by : Int
      controller owner
      do
        let self = this
        assertMsg "by must be positive" (by > 0)
        let _damlforge_self3 = self { count = self.count + by }
        let _damlforge_self4 = _damlforge_self3 { history = _damlforge_self3.history ++ [by] }
        _damlforge_new_self <- create _damlforge_self4
        pure (_damlforge_new_self, _damlforge_self4.count)
```

The declared return type was `int`, but the Daml choice returns
`(ContractId Counter, Int)`. The new contract's ID comes first, followed by your
return value. Callers need the new ID because the old one is now archived. Any
reference to the old ID is stale: fetching it fails.

Don't also call `create` for the same template in a choice that mutates `self`.
That creates a second copy of the contract.

### Ledger effects

Reading or writing the ledger is an *update* in Daml, and a function that does
this must return `Update T`. DamlForge infers this for you. Any function that
calls `create`, `fetch`, `exercise`, `archive`, a by-key lookup, or `datetime.now()`,
directly or through another function that does, is emitted as an update:

```python
def read_count(cid: ContractId[Counter]) -> int:
    counter = fetch(cid)
    return counter.count


def bump_once(cid: ContractId[Counter]) -> int:
    result = exercise(cid, cid.bump(by=1))
    return result[1]
```

```haskell
read_count : (ContractId Counter) -> Update Int
read_count cid = do
  counter <- fetch cid
  pure (counter.count)

bump_once : (ContractId Counter) -> Update Int
bump_once cid = do
  result <- exercise cid (Bump with by = 1)
  pure (result._2)
```

`exercise(cid, cid.choice_name(arg=value))` exercises a choice on a contract ID.
Choice arguments are always passed by keyword. Here, `bump` mutates `self`, so
the result is a tuple, and `result[1]` is the declared `int`.

Choice bodies are already updates, so they can call ledger operations directly.
In every case, import the operations from `forge.builtins.daml_lang`, as at the
top of this page.

### Loops with ledger effects

A `for` loop whose body calls `fetch`, `create`, `exercise`, or any other update
can't be a pure `foldl`, because each step has to run on the ledger. The compiler
emits `foldlA` from `DA.Action` instead, and imports it for you. Each step is a
`do` block that runs the effect, then passes the accumulator on:

```python
def total_count(cids: list[ContractId[Counter]]) -> int:
    total: int = 0
    for cid in cids:
        counter = fetch(cid)
        total = total + counter.count
    return total
```

```haskell
import DA.Action (foldlA)

total_count : [ContractId Counter] -> Update Int
total_count cids = do
  let (total : Int) = 0
  _damlforge_total2 <-
    foldlA
      (\total cid -> do
        counter <- fetch cid
        let _damlforge_total1 = total + counter.count
        pure _damlforge_total1)
      total cids
  pure (_damlforge_total2)
```

The `_damlforge_` names are compiler-generated, and their numbers depend on what
else is in the module.

The effect can also sit inside an expression or an `if` test. The compiler lifts
it into its own `<-` step first:

```python
def count_above(cids: list[ContractId[Counter]], limit: int) -> int:
    n: int = 0
    for cid in cids:
        if fetch(cid).count > limit:
            n = n + 1
    return n
```

```haskell
    foldlA
      (\n cid -> do
        _damlforge_effect1 <- fetch cid
        if _damlforge_effect1.count > limit
          then do
            let _damlforge_n2 = n + 1
            pure _damlforge_n2
          else do
            pure n)
      n cids
```

To collect results, `append` to a list. Here, each step creates a contract and
adds its ID:

```python
def open_counters(owners: list[Party]) -> list[ContractId[Counter]]:
    cids: list[ContractId[Counter]] = []
    for owner in owners:
        cids.append(create(Counter(owner=owner, count=0, history=[])))
    return cids
```

```haskell
    foldlA
      (\cids owner -> do
        _damlforge_cids_item1 <- create (Counter with owner = owner, count = 0, history = [])
        let _damlforge_cids2 = cids <> [_damlforge_cids_item1]
        pure _damlforge_cids2)
      cids owners
```

Effectful loops work the same way in choice bodies and in free functions. A free
function containing one is inferred as an update, like any other function that
touches the ledger.

The same limits apply as for pure loops. There's no `break` or `continue`, and a
loop can't both update a variable and `return` from inside its body (`DF1230`).

## Modules

Each `.vy` file is one Daml module, named after the file: `Fundamentals.vy`
becomes `module Fundamentals`. Within a file, declarations can refer to each
other in any order. To use a declaration from another `.vy` file in the same
project, import it by module name:

```py
from Fundamentals import CashBalance, Currency
```

Types from packages written in plain Daml are imported the same way, using the
Daml module name, for example `from Splice.AmuletRules import AppTransferContext`.
The package must be listed under `data-dependencies` in `daml.yaml`. Run
`forge stubs` on its DAR if you want readable `.vy` declarations for it.

## Next steps

You now have the building blocks: types, functions, control flow, and the
template model. When the compiler rejects something, look up its `DF12xx` code
in [Compiler Errors](03-compiler-errors.md). The next module,
[Contract Templates](04-contract-templates.md), builds your first contracts and
tests them with Daml Script.
