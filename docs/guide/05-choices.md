# Choices

The templates in [Contract Templates](04-contract-templates.md) can only be
created and archived. This module adds behaviour. You'll learn to:

- Define data transformations with *choices*.
- Delegate the right to *exercise* a choice to another party.
- Call choices from Daml Script and from other `.vy` code.

The examples continue in the same `intro` project. Every one compiles with
`forge dar` and is exercised by a Daml Script test that passes.

## Choices as methods

A choice is a method on a template, decorated with `@choice`. It's a
permissioned function: only the parties named as its *controller* can run it,
and running it is a ledger update.

`main/daml/Contact.vy`:

```python
from forge.builtins.daml_lang import create
from forge.models import ContractId, Party, choice, template


@template
class Contact:
    owner: Party
    party: Party
    address: str
    telephone: str

    signatory: Party = owner
    observer: Party = party

    @choice(controller=owner, consuming=True)
    def UpdateTelephone(self, new_telephone: str) -> ContractId[Contact]:
        return create(
            Contact(
                owner=self.owner,
                party=self.party,
                address=self.address,
                telephone=new_telephone,
            )
        )
```

Generated Daml:

```haskell
    choice UpdateTelephone : ContractId Contact
      with
        new_telephone : Text
      controller owner
      do
        let self = this
        create (Contact with owner = self.owner, party = self.party, address = self.address, telephone = new_telephone)
```

| `.vy` | Daml | Meaning |
|---|---|---|
| `def UpdateTelephone` | `choice UpdateTelephone` | The choice name. The first letter is capitalized; the rest is kept as written |
| `new_telephone: str` | `with new_telephone : Text` | Choice arguments. `self` isn't an argument |
| `-> ContractId[Contact]` | `: ContractId Contact` | The return type. Every choice runs as an `Update`, so it isn't written |
| `controller=owner` | `controller owner` | Who may exercise the choice |
| `consuming=True` | `choice` | Exercising the choice archives this contract |
| The method body | `do ...` | What happens when the choice is exercised |

`controller` and `consuming` are required (`DF1203`). Inside the body, `self` is
the contract the choice is exercised on.

### Naming choices

Daml choices are conventionally `PascalCase`, and that's how the names appear in
Daml Script, generated client code, and the ledger. Name the method
`UpdateTelephone` to get `UpdateTelephone`. A `snake_case` method only has its
first letter capitalized, so `update_telephone` becomes `Update_telephone`. To
keep a Python-style method name and set the Daml name yourself, use
`@DamlName`:

```py
from forge.builtins import DamlName

    @DamlName("UpdateTelephone")
    @choice(controller=owner, consuming=True)
    def update_telephone(self, new_telephone: str) -> ContractId[Contact]:
        ...
```

Choice names can't start with `_` (`DF1218`). Choices are always public on the
ledger.

### Exercising a choice in Daml Script

`test/daml/ContactTest.daml`:

```haskell
module ContactTest where

import Daml.Script
import Contact

choice_test : Script ()
choice_test = do
  owner <- allocateParty "Alice"
  party <- allocateParty "Bob"

  contactCid <- submit owner do
    createCmd Contact with
      owner
      party
      address = "1 Bobstreet"
      telephone = "012 345 6789"

  submitMustFail party do
    exerciseCmd contactCid UpdateTelephone with
      new_telephone = "098 7654 321"

  newContactCid <- submit owner do
    exerciseCmd contactCid UpdateTelephone with
      new_telephone = "098 7654 321"
```

Bob can't change the telephone number because Alice controls that choice. When
Alice exercises it, the original contract is archived and a new one is created
with a new contract ID. Choice arguments are passed by their `.vy` names, here
`new_telephone`.

From Daml Script:

- `exerciseCmd cid Choice with ...` exercises a choice on an existing contract.
- `createAndExerciseCmd payload Choice` creates a contract and exercises a
  choice on it in one transaction. For a consuming choice, the contract is
  created and archived in that same transaction.
- `archiveCmd cid` exercises the built-in `Archive` choice.

## Choices as delegation

Alice is the only signatory of `Contact`, but she can delegate a specific right
to Bob by making him the controller of a choice:

```python
    @choice(controller=party, consuming=True)
    def UpdateAddress(self, new_address: str) -> ContractId[Contact]:
        return create(
            Contact(
                owner=self.owner,
                party=self.party,
                address=new_address,
                telephone=self.telephone,
            )
        )
```

Bob can now update the address, and only the address. The new contract is still
signed by Alice: by agreeing to the original contract, Alice authorized every
choice it contains.

```haskell
  newContactCid <- submit party do
    exerciseCmd newContactCid UpdateAddress with
      new_address = "1-10 Bobstreet"

  Some newContact <- queryContractId owner newContactCid
  assert (newContact.address == "1-10 Bobstreet")

  oldContact <- queryContractId owner contactCid
  assert (oldContact == None)
```

Bob can exercise the choice because he can see the contract: he's an observer.
The last check shows that the first contract is gone. Its ID is stale, and
querying it returns `None`.

## Changing the contract in place

Writing out every field to re-create a contract is verbose. In a consuming
choice, you can assign to `self` instead. The compiler builds the updated
contract and creates it for you:

```python
    @choice(controller=owner, consuming=True)
    def ChangeTelephone(self, new_telephone: str):
        self.telephone = new_telephone
```

```haskell
    choice ChangeTelephone : (ContractId Contact, ())
      with
        new_telephone : Text
      controller owner
      do
        let self = this
        let _damlforge_self1 = self { telephone = new_telephone }
        _damlforge_new_self <- create _damlforge_self1
        pure (_damlforge_new_self, ())
```

The choice's return type grows to a pair. The first element is the new
contract's ID, and the second is the value the method returns (`()` here,
because it returns nothing). Callers unpack it:

```haskell
  (newCid, ()) <- submit owner do
    exerciseCmd contactCid ChangeTelephone with
      new_telephone = "098 7654 321"
```

Don't also call `create` for the same template in a choice that assigns to
`self`: that creates the contract twice.

## Consuming and non-consuming choices

`consuming` decides what happens to the contract when the choice is exercised:

| `consuming=` | Daml | Contract after the choice |
|---|---|---|
| `True` or `"consuming"` | `choice` | Archived by the exercise |
| `False` or `"nonconsuming"` | `nonconsuming choice` | Stays active |
| `"preconsuming"` | `preconsuming choice` | Archived at the start of the body |
| `"postconsuming"` | `postconsuming choice` | Archived at the end of the body, so the body can still read it |

Use a non-consuming choice to read from a contract, or to act on other contracts
without changing this one:

```python
    @choice(controller=owner, consuming=False, observer=auditor)
    def ShowAddress(self, auditor: Party) -> str:
        return self.address

    @choice(controller=owner, consuming="postconsuming")
    def Close(self) -> str:
        return self.address
```

```haskell
    nonconsuming choice ShowAddress : Text
      with
        auditor : Party
      observer auditor
      controller owner
      do
        let self = this
        pure (self.address)

    postconsuming choice Close : Text
      controller owner
      do
        let self = this
        pure (self.address)
```

`ShowAddress` also shows a *choice observer*. `observer=` on `@choice` names
extra parties who are informed of this exercise and its consequences, without
becoming stakeholders of the contract. Here,
`auditor` is a choice argument, so the party exercising the choice decides who
gets to see it.

`controller` and `observer` may refer only to template fields, the choice's own
arguments, or `self.<field>` (`DF1224`). Either one can be a list, such as
`controller=[owner, party]`, which needs the authority of every listed party.

`preconsuming` and `postconsuming` aren't allowed on interface choices
(`DF1208`).

## Choices in the ledger model

A transaction is a list of *actions*. There are three kinds:

- `create` makes a new active contract.
- `fetch` checks that a contract exists and is active, and reads it.
- `exercise` runs a choice on a contract. It's consuming or non-consuming, and
  its body produces *consequences*: further `create`, `fetch`, and `exercise`
  actions.

Actions form a tree. `create` and `fetch` are always leaves, and each `exercise`
is the parent of its consequences. When Alice exercised `UpdateTelephone`, the
transaction held one consuming `exercise` with one `create` beneath it.

### The Archive choice

There's no separate archive action. Every template gets an implicit `Archive`
choice, with its signatories as controllers. In `.vy` code, `archive(cid)` from
`forge.builtins.daml_lang` exercises it, and in Daml Script it's `archiveCmd`.

## A simple cash model

The same pieces are enough for a basic model of cash: an IOU ("I owe you") that
records a liability, not where physical money is.

`main/daml/Iou.vy`:

```python
from forge.builtins.daml_lang import create, exercise
from forge.models import ContractId, Decimal, Party, choice, template


struct Cash:
    currency: str
    amount: Decimal


@template
class SimpleIou:
    issuer: Party
    owner: Party
    cash: Cash

    signatory: Party = issuer
    observer: Party = owner

    @choice(controller=owner, consuming=True)
    def Transfer(self, new_owner: Party) -> ContractId[SimpleIou]:
        return create(SimpleIou(issuer=self.issuer, owner=new_owner, cash=self.cash))

    @choice(controller=owner, consuming=False)
    def Describe(self) -> str:
        return self.cash.currency
```

The issuer signs the IOU, and the owner may transfer it with `Transfer`. The
model relies on trust: the issuer could archive the IOU at any time. Because
every transaction is on the ledger, though, the owner could prove that the
issuer cancelled it.

```haskell
iou_test : Script ()
iou_test = do
  dora <- allocateParty "Dora"
  alice <- allocateParty "Alice"
  bob <- allocateParty "Bob"

  iouCid <- submit dora do
    createCmd SimpleIou with
      issuer = dora
      owner = alice
      cash = Cash with currency = "USD", amount = 100.0

  currency <- submit alice do
    exerciseCmd iouCid Describe
  assert (currency == "USD")

  bobIouCid <- submit alice do
    exerciseCmd iouCid Transfer with new_owner = bob

  Some bobIou <- queryContractId bob bobIouCid
  assert (bobIou.owner == bob)

  submit dora do
    archiveCmd bobIouCid
```

### Exercising choices from `.vy` code

Choices can exercise choices on other contracts. Call
`exercise(cid, cid.Choice(arg=value))`, passing choice arguments by keyword.
This `Wallet` moves many IOUs in one transaction:

```python
@template
class Wallet:
    owner: Party

    signatory: Party = owner

    @choice(controller=owner, consuming=False)
    def TransferAll(
        self, cids: list[ContractId[SimpleIou]], new_owner: Party
    ) -> list[ContractId[SimpleIou]]:
        moved: list[ContractId[SimpleIou]] = []
        for cid in cids:
            moved.append(exercise(cid, cid.Transfer(new_owner=new_owner)))
        return moved
```

```haskell
    nonconsuming choice TransferAll : [ContractId SimpleIou]
      with
        cids : [ContractId SimpleIou]
        new_owner : Party
      controller owner
      do
        let self = this
        let (moved : [ContractId SimpleIou]) = []
        _damlforge_moved3 <-
          foldlA
            (\moved cid -> do
              _damlforge_moved_item1 <- exercise cid (Transfer with new_owner = new_owner)
              let _damlforge_moved2 = moved <> [_damlforge_moved_item1]
              pure _damlforge_moved2)
            moved cids
        pure (_damlforge_moved3)
```

The loop calls a ledger operation, so it compiles to `foldlA` (see
[Loops with ledger effects](02-language-fundamentals.md#loops-with-ledger-effects)).

Authorization still applies inside the loop. `TransferAll` runs with the wallet
owner's authority, and `Transfer` needs the IOU owner's. Alice can move her own
IOUs, but Bob's wallet can't move an IOU that Alice owns:

```haskell
  moved <- submit alice do
    exerciseCmd wallet TransferAll with cids = [iou1, iou2], new_owner = bob
  assert (length moved == 2)

  iou3 <- submit dora do
    createCmd SimpleIou with
      issuer = dora
      owner = alice
      cash = Cash with currency = "CHF", amount = 5.0

  bobWallet <- submit bob do
    createCmd Wallet with owner = bob
  submitMustFail bob do
    exerciseCmd bobWallet TransferAll with cids = [iou3], new_owner = bob
```

Run all the tests:

```bash
forge dar main -o main/.daml/dist/intro-main-0.0.1.dar
cd test && dpm test
```

```text
daml/ContactTest.daml:choice_test: ok, 1 active contracts, 4 transactions.
daml/ContactTest.daml:self_update_test: ok, 0 active contracts, 5 transactions.
daml/IouTest.daml:iou_test: ok, 0 active contracts, 4 transactions.
daml/IouTest.daml:wallet_test: ok, 5 active contracts, 7 transactions.
daml/TokenTest.daml:token_test: ok, 1 active contracts, 6 transactions.
```

## Next steps

You can now store data, transform it with choices, and delegate rights to other
parties. When the compiler rejects a choice, look up its code in
[Compiler Errors](03-compiler-errors.md).

Continue to [Design Patterns](06-design-patterns.md) to combine choices into
multi-party workflows.
