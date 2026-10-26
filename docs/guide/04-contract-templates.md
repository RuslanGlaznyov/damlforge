# Contract Templates

This module builds the simplest possible contract: a token that a party issues to
itself and can't transfer. It isn't useful on its own, but it introduces the
basic concepts every DamlForge contract relies on: transactions, modules,
templates, contracts, signatories, and observers.

Every example on this page compiles with `forge dar` and is exercised by a Daml
Script test that passes.

## Project setup

Start from the DPM skeleton, as in
[Development Environment Setup](01-dev-environment.md), and remove its sample
files:

```bash
dpm new intro
cd intro
rm main/daml/Main.daml test/daml/Test.daml
```

Contracts go in `main/daml/` as `.vy` files. Tests go in `test/daml/` as Daml
Script. After every change to a `.vy` file, rebuild the main package to the path
the test package expects, then run the tests:

```bash
forge dar main -o main/.daml/dist/intro-main-0.0.1.dar
cd test && dpm test
```

## Ledger basics

A Daml ledger is a list of *commits*. A commit is the result of a *party*
successfully *submitting* a *transaction*. The two simplest things a transaction
can do are create a *contract* and archive one.

A contract is *active* from the transaction that creates it until the
transaction that archives it. Contracts are immutable: the only way to change
the set of active contracts is to create new ones or archive existing ones.

The rules that decide which transactions are legal are written in your
contracts. Together they're called the *contract model*. In DamlForge you write
that model in `.vy` files, and the compiler turns it into the Daml that the
ledger runs.

## Modules and files

Each `.vy` file is one Daml module, named after the file. `Token.vy` compiles to:

```haskell
module Token where
```

Comments (`#`) are for readers of the `.vy` source. They aren't copied into the
generated Daml.

## Templates

A *template* defines a type of contract: what data it holds and who has to agree
to its creation. Each contract on the ledger is an instance of a template.

`main/daml/Token.vy`:

```python
from forge.models import Party, template


@template
class Token:
    owner: Party

    signatory: Party = owner
```

Generated `Token.daml`:

```haskell
template Token
  with
    owner : Party
  where
    signatory owner
```

| `.vy` | Daml | Meaning |
|---|---|---|
| `@template` above `class Token:` | `template Token` | Declares the template. `@template` comes from `forge.models` |
| `owner: Party` | `with owner : Party` | A field, also called a *create argument*. Every contract stores its own value |
| `signatory: Party = owner` | `where signatory owner` | A template clause, not a field. It holds the contract's rules |

Template fields are written like Python class annotations, in the order you want
them in Daml. Clauses (`signatory`, `observer`, `ensure`) are written as
annotated assignments and refer to fields by bare name. Order matters only for
readability: clauses go after the fields.

A template body may contain fields, clauses, and choices only. A plain method
that isn't a choice is rejected with `DF1233`. Move helper logic to a top-level
function.

## Signatories

The `signatory` clause names the parties whose authority is needed to create or
archive the contract. Every template must declare at least one signatory
(`DF1201`).

It can be one party or a list:

```py
signatory: Party = owner
signatory: list[Party] = [issuer, owner]
```

Signatories are guaranteed to see every transaction that uses their authority.
They always see the creation and archival of their own contracts.

Because `owner` is the only signatory of `Token`, Alice can create a token for
herself, but Bob can't create one in her name. Only Alice can archive it.

## Observers and preconditions

A second template in the same file adds two more clauses:

```python
@template
class Asset:
    issuer: Party
    owner: Party
    name: str
    quantity: int

    signatory: Party = issuer
    observer: Party = owner
    ensure: bool = name != "" and quantity > 0
```

```haskell
template Asset
  with
    issuer : Party
    owner : Party
    name : Text
    quantity : Int
  where
    signatory issuer
    observer owner
    ensure (name /= "") && (quantity > 0)
```

**Observers** can see the contract but don't authorize it. Here, `owner` sees
the asset that `issuer` created. Like `signatory`, `observer` takes a single
`Party` or a `list[Party]`.

**`ensure`** is a precondition checked every time a contract of this template is
created. If it's `False`, the transaction fails. The value must be a boolean
expression: a comparison, `and`/`or`/`not`, or a call that returns `bool`
(`DF1212`).

You can also write preconditions as `assert` statements in an `__init__`
method. The compiler combines them into one `ensure` clause:

```py
    def __init__(self, name: str, quantity: int):
        assert name != "", "name must not be empty"
        assert quantity > 0
```

Assertion messages aren't carried into Daml, which has no message on `ensure`.

> **Known limitation:** an empty list literal, such as
> `observer: list[Party] = []`, generates `observer []`, which `damlc` rejects
> because it can't infer the element type. Leave out a clause you don't need.

## Contract keys

`key` and `maintainer` are accepted and checked as a pair (`DF1210`,
`DF1211`), but DamlForge doesn't emit them in the generated Daml. Don't rely on
contract keys. Refer to contracts by their contract ID.

## Testing templates with Daml Script

`test/daml/TokenTest.daml`:

```haskell
module TokenTest where

import Daml.Script
import Token

token_test : Script ()
token_test = do
  alice <- allocateParty "Alice"
  bob <- allocateParty "Bob"

  aliceToken <- submit alice do
    createCmd Token with owner = alice

  submitMustFail bob do
    createCmd Token with owner = alice

  submitMustFail bob do
    archiveCmd aliceToken

  submit alice do
    archiveCmd aliceToken

  submitMustFail alice do
    createCmd Asset with
      issuer = alice
      owner = bob
      name = "TV"
      quantity = 0

  assetCid <- submit alice do
    createCmd Asset with
      issuer = alice
      owner = bob
      name = "TV"
      quantity = 1

  Some asset <- queryContractId bob assetCid
  assert (asset.name == "TV")
```

The script checks each rule on this page:

| Step | Result | Why |
|---|---|---|
| Alice creates her own `Token` | Succeeds | Alice is the signatory and submits |
| Bob creates a `Token` owned by Alice | Fails | It needs Alice's authority, and only Bob submitted |
| Bob archives Alice's token | Fails | Archiving needs the signatory's authority too |
| Alice archives her token | Succeeds | The contract is no longer active |
| Alice creates an `Asset` with `quantity = 0` | Fails | `ensure` is `False` |
| Alice creates a valid `Asset` | Succeeds | |
| Bob queries the asset | Finds it | Bob is an observer |

Run it:

```bash
cd test
dpm test
```

```text
daml/TokenTest.daml:token_test: ok, 1 active contracts, 6 transactions.
```

Daml Script uses the generated Daml names: the template is `Token`, and the
fields keep their `.vy` names.

## Next steps

These contracts can be created and archived, but nothing else. Continue to
[Choices](05-choices.md) to give contracts behaviour: letting parties change
them and delegate rights to each other.
