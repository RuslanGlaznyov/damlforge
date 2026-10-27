# Variants

A *variant* is a type whose value is exactly one of several named cases, each
with its own data. A payment is cash, a card with its last digits, or a bank
transfer with an IBAN and a reference. Daml calls these *sum types* or
*algebraic data types*. In Python you'd model them with a class hierarchy or a
tagged union.

[Language Fundamentals](02-language-fundamentals.md#variants) shows the basic
declaration. This page covers the rest: payload styles, constructing and
comparing values, using variants in templates, recursive and generic variants,
testing with Daml Script, and what isn't supported yet.

The examples are in `main/daml/Order.vy` and `test/daml/OrderTest.daml`, and
every test passes.

## Declaring a variant

`Order.vy` starts with its imports:

```python
from typing import Generic, Optional, TypeVar

from forge.builtins.daml_lang import create
from forge.models import ContractId, Decimal, Party, choice, template, variant, variant_record
```

A variant is a class marked `@variant`. Each method declares one *constructor*:
its name is the case, its parameters are the case's data, and its body is
`pass`.

```python
@variant
class PaymentMethod:
    def Cash(): pass
    def Card(last_digits: str): pass

    @variant_record
    def BankTransfer(iban: str, reference: str): pass
```

```haskell
data PaymentMethod
  = Cash
  | Card Text
  | BankTransfer with
      iban : Text
      reference : Text
  deriving (Eq, Show)
```

There are three kinds of constructor:

| Constructor | `.vy` | Daml |
|---|---|---|
| No data | `def Cash(): pass` | `Cash` |
| Positional, one value | `def Card(last_digits: str): pass` | `Card Text` |
| Record, named fields | `@variant_record` on `def BankTransfer(iban: str, reference: str): pass` | `BankTransfer with iban : Text; reference : Text` |

- **Positional** constructors keep only the type of their value. The parameter
  name (`last_digits`) documents the `.vy` source but isn't part of the Daml
  type.
- **Record** constructors keep their field names. Use `@variant_record` when a
  constructor holds more than one value, or when the field names matter to
  clients, such as JSON API users.
- Every parameter needs a type annotation.
- The class may contain only constructors (`DF1203`). Put helper functions at
  the top level.
- Variants derive `Eq` and `Show`, so values can be compared and printed.

> **Warning: not available yet.** DamlForge doesn't check the two declarations
> below yet. Both compile without a `DF` error, then `damlc` rejects the
> generated Daml. Errors for both are planned for a future release.
>
> **1. A positional constructor with two or more values.**
>
> ```python
> @variant
> class Shape:
>     def Rect(width: int, height: int): pass
>     def Dot(): pass
> ```
>
> This generates `Rect Int Int`. Daml requires a constructor with more than one
> value to name its fields, so `damlc` reports `Constructors with multiple fields
> must give explicit field names`.
>
> **How to avoid it:** mark every constructor with two or more values as
> `@variant_record`, and construct it with keyword arguments:
>
> ```python
> @variant
> class Shape:
>     @variant_record
>     def Rect(width: int, height: int): pass
>
>     def Dot(): pass
>
>
> def square(side: int) -> Shape:
>     return Rect(width=side, height=side)
> ```
>
> ```haskell
> data Shape
>   = Rect with
>       width : Int
>       height : Int
>   | Dot
>   deriving (Eq, Show)
>
> square : Int -> Shape
> square side =
>   Rect with width = side, height = side
> ```
>
> Alternatively, group the values in a `struct` and keep one positional value:
> `def Rect(size: Size): pass`.
>
> **2. A variant with only one constructor, marked `@variant_record`.**
>
> ```python
> @variant
> class Payment:
>     @variant_record
>     def BankTransfer(iban: str, reference: str): pass
> ```
>
> This generates `data Payment = BankTransfer with ...`. Daml reads a type with a
> single named-field constructor as a record, and a record's constructor must
> have the type's name, so `damlc` reports `Record type Payment has constructor
> BankTransfer with different name`.
>
> **How to avoid it:** a variant with one case is really a record, so declare it
> as a `struct`:
>
> ```python
> struct Payment:
>     iban: str
>     reference: str
>
>
> def wire(iban: str, reference: str) -> Payment:
>     return Payment(iban=iban, reference=reference)
> ```
>
> ```haskell
> wire : Text -> Text -> Payment
> wire iban reference =
>   Payment with iban = iban, reference = reference
> ```
>
> If more cases are coming later, declare them now: with two or more
> constructors, as in `PaymentMethod` above, `@variant_record` constructors work
> as expected.

## Variants or enums

When no constructor carries data, you can use either a variant or a Python
`Enum`:

| | `Enum` | `@variant` |
|---|---|---|
| Declaration | `class Currency(Enum):` with `USD = auto()` | `@variant` with `def USD(): pass` |
| Value | `Currency.USD` | `USD()` |
| Daml | `data Currency = USD \| EUR` | the same |
| Member names | `SCREAMING_SNAKE_CASE` (`DF1217`) | any constructor name |

Use an `Enum` for a fixed list of labels. Use a variant as soon as one case
needs data, or when the case names must match an existing Daml API.

## Constructing values

Call a constructor by its bare name, like a function. Don't prefix it with the
variant name:

| `.vy` | Daml |
|---|---|
| `Cash()` | `Cash` |
| `Card("4242")` | `Card "4242"` |
| `BankTransfer(iban=iban, reference=ref)` | `BankTransfer with iban = iban, reference = ref` |
| `BankTransfer(iban, ref)` | `BankTransfer iban ref` |

`PaymentMethod.Cash()` fails with `DF1219`, because `PaymentMethod` is a type,
not a namespace. A constructor without data still needs `()` in `.vy`; the
parentheses disappear in Daml.

Constructors are ordinary expressions, so a function can build a variant value:

```python
def wire(iban: str, order_number: str) -> PaymentMethod:
    return BankTransfer(iban=iban, reference=order_number)
```

```haskell
wire : Text -> Text -> PaymentMethod
wire iban order_number =
  BankTransfer with iban = iban, reference = order_number
```

## Variants inside variants

A constructor's value can be another variant. An order's status records how it
was paid:

```python
@variant
class OrderStatus:
    def Placed(): pass
    def Paid(method: PaymentMethod): pass
```

`Paid(Card("4242"))` becomes `Paid (Card "4242")` in Daml. The compiler adds
the parentheses.

## Using variants in templates

A variant can be a template field, a choice argument, a choice result, or the
element type of `Optional` and `list`:

```python
@template
class Order:
    shop: Party
    customer: Party
    number: str
    amount: Decimal
    discount: Optional[Discount]
    status: OrderStatus
    history: list[OrderStatus]

    signatory: Party = shop
    observer: Party = customer
```

Each status change archives the order and creates a new one. This helper
copies the order with a new status and appends the old status to `history`:

```python
def with_status(order: Order, status: OrderStatus) -> Order:
    return Order(
        shop=order.shop,
        customer=order.customer,
        number=order.number,
        amount=order.amount,
        discount=order.discount,
        status=status,
        history=order.history + [order.status],
    )
```

### Comparing values

`==`, `!=`, `in`, and `not in` compare whole values, payload included:

```python
    @choice(controller=customer, consuming=True)
    def Pay(self, method: PaymentMethod) -> ContractId[Order]:
        assert self.status == Placed(), "the order is already paid"
        if self.amount > Decimal(1000):
            assert method != Cash(), "cash is accepted up to 1000"
        return create(with_status(self, Paid(method)))
```

```haskell
    choice Pay : ContractId Order
      with
        method : PaymentMethod
      controller customer
      do
        let self = this
        assertMsg "the order is already paid" (self.status == Placed)
        if self.amount > (1000.0 : Decimal)
          then do
            assertMsg "cash is accepted up to 1000" (method /= Cash)
            pure ()
          else do
            pure ()
        create (with_status self (Paid method))
```

`method != Cash()` is a reliable test, because `Cash` has no data. A
comparison with a case that has data matches only that exact value:
`method == Card("4242")` is `False` for `Card("1111")`.

To test for "any case except these", list the cases without data:

```python
    @choice(controller=shop, consuming=True)
    def Ship(self, tracking: str) -> ContractId[Shipment]:
        assert self.status not in [Placed()], "the order is not paid"
        return create(Shipment(shop=self.shop, customer=self.customer, order=self, tracking=tracking))
```

```haskell
        assertMsg "the order is not paid" (self.status `notElem` [Placed])
```

A choice can also build a variant from its arguments:

```python
    @choice(controller=customer, consuming=True)
    def PayByWire(self, iban: str) -> ContractId[Order]:
        assert self.status == Placed(), "the order is already paid"
        return create(with_status(self, Paid(wire(iban, self.number))))
```

## Recursive variants

A constructor can refer to its own variant, which builds trees. A discount is
none, a percentage, or two discounts combined:

```python
@variant
class Discount:
    def NoDiscount(): pass
    def Percent(value: Decimal): pass

    @variant_record
    def Both(first: Discount, second: Discount): pass
```

```haskell
data Discount
  = NoDiscount
  | Percent Decimal
  | Both with
      first : Discount
      second : Discount
  deriving (Eq, Show)
```

## Generic variants

A variant can take type parameters with `Generic`, like a generic Python class:

```python
T = TypeVar("T")


@variant
class Outcome(Generic[T]):
    def Done(value: T): pass
    def Rejected(reason: str): pass


@template
class Job:
    owner: Party
    outcome: Outcome[int]

    signatory: Party = owner
```

```haskell
data Outcome t
  = Done t
  | Rejected Text
  deriving (Eq, Show)
```

`Outcome[int]` becomes `Outcome Int`. The standard library's `Either` is
declared the same way, in `forge/builtins/DA/Types.vy`.

> **Warning: not available yet.** Generic variants can be declared and used as
> types, but `.vy` code can't construct their values yet. `Done(42)` in a
> function returning `Outcome[int]` fails with `DF1230` and `DF1226`. Values
> created by clients or Daml Script, such as `Job` above, work. Support is
> planned for a future release.

## Testing with Daml Script

Daml Script is Daml, so it uses the generated constructors: `Placed`,
`Card "4242"`, and `BankTransfer with ...`:

```haskell
place : Party -> Party -> Decimal -> Script (ContractId Order)
place shop customer amount =
  submit shop do
    createCmd Order with
      shop
      customer
      number = "A-1"
      amount
      discount = Some (Both with first = Percent 10.0, second = NoDiscount)
      status = Placed
      history = []
```

A test pays by card, checks the new status and history, and ships the order:

```haskell
  order <- place shop alice 50.0
  paid <- submit alice do
    exerciseCmd order Pay with method = Card "4242"
  Some paid_order <- queryContractId alice paid
  assert (paid_order.status == Paid (Card "4242"))
  assert (paid_order.history == [Placed])

  case paid_order.status of
    Paid (Card digits) -> assert (digits == "4242")
    _ -> abort "expected a card payment"

  submitMustFail alice do
    exerciseCmd paid Pay with method = Cash

  shipment <- submit shop do
    exerciseCmd paid Ship with tracking = "TRK-1"
```

The `case` expression reads the card digits out of the status. Daml Script can
do this; `.vy` code can't yet (see below).

The payment rules reject cash for a large order and shipping before payment:

```haskell
  large <- place shop alice 5000.0
  submitMustFail alice do
    exerciseCmd large Pay with method = Cash
  submitMustFail shop do
    exerciseCmd large Ship with tracking = "TRK-2"

  wired <- submit alice do
    exerciseCmd large PayByWire with iban = "DE89370400440532013000"
  Some wired_order <- queryContractId alice wired
  assert (wired_order.status == Paid (BankTransfer with iban = "DE89370400440532013000", reference = "A-1"))
```

```text
daml/OrderTest.daml:generic_test: ok, 1 active contracts, 1 transactions.
daml/OrderTest.daml:payment_rules_test: ok, 1 active contracts, 4 transactions.
daml/OrderTest.daml:order_test: ok, 1 active contracts, 4 transactions.
```

## Reading a variant's data

> **Warning: not available yet.** `.vy` has no way to check which case a value
> is and read its data. Daml does this with `case ... of`, but the Python
> equivalents don't compile:
>
> | `.vy` | Result |
> |---|---|
> | `match status:` with `case Paid(method):` | `Invalid syntax (unsupported 'Match' Python AST node)` |
> | `isinstance(method, Card)` | `DF1219`, `isinstance` is not defined |
> | `method.last_digits`, `method.iban` | Compiles to `method.last_digits`, which `damlc` rejects: a variant has no fields |
>
> Support for `match` is planned for a future release.

Until then:

- **Compare with `==` and `in`** when the cases you test have no data, as `Pay`
  and `Ship` do.
- **Store the data you need to read in its own field.** If a choice must read
  the card digits, keep them in a template field or choice argument, and use
  the variant to record which case applies.
- **Use an `Enum` for the case and a separate field for its data** when every
  choice needs to branch on the case.
- **Read the data off the ledger.** Daml Script and clients reading the ledger
  through the JSON API can inspect variant data in full.

## Next steps

[Compiler Errors](03-compiler-errors.md) lists the variant errors (`DF1203`,
`DF1205`). [Building and Packaging](10-building-packaging.md) explains how to
ship the package that declares your variants.
