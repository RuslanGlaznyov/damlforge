# Contract Keys

A contract ID changes every time a contract is archived and recreated, for example
when a choice updates it. A *contract key* gives a contract a stable identity built
from values it holds, like a bank and an account number, so a choice can find the
current contract without tracking its ID.

The examples on this page are in `main/daml/Account.vy` and
`test/daml/AccountTest.daml`, and every test passes.

A key needs two clauses:

```py
    key: tuple[Party, str] = (bank, number)
    maintainer: Party = key[0]
```

- `key` is computed from template fields. It needs a type annotation (`DF1213`).
- `maintainer` names the parties responsible for the key. It's computed from
  `key` only, never from template fields (`DF1236`).
- Each needs the other (`DF1210`, `DF1211`).

## Requirements

Contract keys compile only with Daml SDK 3.5 or later and the Daml-LF 2.3 target.
Add the target to the `daml.yaml` of every package that declares or uses keys:

```yaml
sdk-version: 3.5.2
build-options:
  - --target=2.3
```

Without it, `forge dar` stops with `DF1234` before calling `damlc`.

In Daml 3.5, keys aren't unique: two active contracts can have the same key.
`fetch_by_key` and `lookup_by_key` return one of them, and `lookup_all_by_key`
returns all of them.

## Declaring a key

```python
@template
class Account:
    bank: Party
    owner: Party
    number: str

    signatory: Party = bank
    observer: Party = owner
    key: tuple[Party, str] = (bank, number)
    maintainer: Party = key[0]

    @choice(controller=bank, consuming="nonconsuming")
    def GetOwner(self) -> Party:
        return self.owner
```

```haskell
template Account
  with
    bank : Party
    owner : Party
    number : Text
  where
    signatory bank
    observer owner
    key (bank, number) : (Party, Text)
    maintainer key._1
```

`key[0]` becomes `key._1`, Daml's first tuple element. A key can also be a single
field (`key: Party = owner`) or a struct (`key: AccountKey = AccountKey(bank=bank,
number=number)`).

## Using a key

These builtins come from `forge.builtins.daml_lang`, like `fetch`:

| `.vy` | Daml | Returns |
|---|---|---|
| `lookup_by_key(key)` | `lookupByKey` | `Optional[ContractId[T]]` |
| `fetch_by_key(key)` | `fetchByKey` | `tuple[ContractId[T], T]` |
| `lookup_all_by_key(key)` | `lookupAllByKey` | `list[tuple[ContractId[T], T]]` |
| `lookup_n_by_key(limit, key)` | `lookupNByKey` | at most `limit` matches, same type as above |
| `exercise_by_key(T, key, T.Choice(...))` | `exerciseByKey @T` | the choice's result |
| `visible_by_key(T, key)` | `visibleByKey @T` | `bool` |

Daml finds the template from the type of the result. For the first four, give the
variable that receives the result a type annotation, as in the example below.
Without one, `damlc` can't tell which template you mean. `exercise_by_key` and
`visible_by_key` return something that doesn't mention the template, so they take
it as their first argument (`DF1235`). Their choice argument is written as
`Template.Choice(...)`, because there is no contract ID to call it on.

`lookup_all_by_key` and `lookup_n_by_key` need `DA.ContractKeys` in Daml. The
compiler adds that import for you.

A second template in the same file uses every builtin:

```python
@template
class Registry:
    bank: Party

    signatory: Party = bank

    @choice(controller=bank, consuming="nonconsuming")
    def Find(self, number: str) -> Optional[Party]:
        found: Optional[ContractId[Account]] = lookup_by_key((self.bank, number))
        if found is None:
            return None
        return exercise_by_key(Account, (self.bank, number), Account.GetOwner())

    @choice(controller=bank, consuming="nonconsuming")
    def Owner(self, number: str) -> Party:
        pair: tuple[ContractId[Account], Account] = fetch_by_key((self.bank, number))
        return pair[1].owner

    @choice(controller=bank, consuming="nonconsuming")
    def Count(self, number: str) -> int:
        rows: list[tuple[ContractId[Account], Account]] = lookup_all_by_key((self.bank, number))
        return len(rows)

    @choice(controller=bank, consuming="nonconsuming")
    def CountFirst(self, number: str) -> int:
        rows: list[tuple[ContractId[Account], Account]] = lookup_n_by_key(1, (self.bank, number))
        return len(rows)

    @choice(controller=bank, consuming="nonconsuming")
    def Visible(self, number: str) -> bool:
        return visible_by_key(Account, (self.bank, number))
```

The file starts with these imports:

```python
from typing import Optional

from forge.builtins.daml_lang import (
    exercise_by_key,
    fetch_by_key,
    lookup_all_by_key,
    lookup_by_key,
    lookup_n_by_key,
    visible_by_key,
)
from forge.models import ContractId, Party, choice, template
```

The annotated assignments become typed bindings, and the template argument becomes
a Daml type application:

```haskell
        (pair : (ContractId Account, Account)) <- fetchByKey (self.bank, number)
```

```haskell
        visibleByKey @Account (self.bank, number)
```

A Script test creates two accounts with the same key, which Daml 3.5 allows:

```haskell
  submit bank do
    createCmd Account with bank; owner = alice; number = "1"
  submit bank do
    createCmd Account with bank; owner = bob; number = "1"

  owner <- submit bank do
    exerciseCmd registry Owner with number = "1"
  assert (owner == alice || owner == bob)

  found <- submit bank do
    exerciseCmd registry Find with number = "1"
  assert (found == Some owner)

  count <- submit bank do
    exerciseCmd registry Count with number = "1"
  assert (count == 2)

  first <- submit bank do
    exerciseCmd registry CountFirst with number = "1"
  assert (first == 1)
```

`fetch_by_key` on a key with no contract fails the transaction:

```haskell
  submitMustFail bank do
    exerciseCmd registry Owner with number = "2"
```

## Lookup order

Because keys aren't unique, a lookup can match several contracts. Daml returns
them in this order:

1. Contracts created earlier in the same transaction, most recent first.
2. Contracts disclosed to the submitter, in the order the command lists them.
3. Other contracts the submitting parties can see.

`fetch_by_key`, `lookup_by_key`, and `exercise_by_key` use the first match.
`lookup_n_by_key` and `lookup_all_by_key` return matches in the same order. The
lookups are fastest when a key matches at most one contract, so design keys that
your application keeps unique, such as account or invoice numbers.

## Authorization

- `fetch_by_key` needs the authority of one of the contract's stakeholders, like
  `fetch`. It fails the transaction if no visible contract has the key.
- `lookup_by_key` needs the authority of every maintainer, and returns `None`
  when no contract matches.
- `exercise_by_key` needs the authority of the choice's controllers, like
  `exercise`.

`Registry` has the bank as its only signatory and the bank is the maintainer of
every `Account` key, so each of its choices has the authority it needs.

## Keys in Daml Script

Daml Script can query and exercise by key from outside a transaction:

```haskell
script_key_test : Script ()
script_key_test = do
  bank <- allocateParty "Bank"
  alice <- allocateParty "Alice"
  submit bank do
    createCmd Account with bank; owner = alice; number = "7"
  Some (_, account) <- queryByKey @Account bank (bank, "7")
  assert (account.owner == alice)
  owner <- submit bank do
    exerciseByKeyCmd @Account (bank, "7") GetOwner
  assert (owner == alice)
  rows <- queryNByKey @Account bank 10 (bank, "7")
  assert (length rows == 1)
```

| Function | Returns |
|---|---|
| `queryByKey @T party key` | `Optional (ContractId T, T)`, the first match visible to `party` |
| `queryNByKey @T party n key` | up to `n` matches |
| `exerciseByKeyCmd @T key choice` | a command for `submit`, like `exerciseCmd` |

```text
daml/AccountTest.daml:script_key_test: ok, 1 active contracts, 2 transactions.
daml/AccountTest.daml:keys_test: ok, 3 active contracts, 11 transactions.
```

## Next steps

[Interfaces](09-interfaces.md) shows how different templates can share one set of
choices, so code can work with any of them.
