# Design Patterns

Real workflows involve several parties, and nobody can be bound to a contract
without agreeing to it. This module builds a small coin model and uses it to show
the patterns that Daml applications are built from: composing choices,
propose-accept, delegation, authorization, locking, and multi-party agreement.

Every template on this page lives in one module, `main/daml/Coin.vy`, and every
pattern is exercised by a Daml Script test that passes.

## The coin model

`Coin.vy` starts with its imports:

```python
from datetime import datetime

from DA.List import sort, unique
from forge.builtins.daml_lang import archive, create, exercise, fetch
from forge.models import ContractId, Decimal, Party, choice, template
```

`sort` and `unique` come from Daml's standard library. A stub module under
`DA.List` makes them importable, and the compiler adds `import DA.List` to the
generated Daml.

The coin itself has two signatories. Neither the issuer nor the owner can create
or change a coin alone:

```python
@template
class Coin:
    issuer: Party
    owner: Party
    amount: Decimal
    delegates: list[Party]

    signatory: list[Party] = [issuer, owner]
    observer: list[Party] = delegates
    ensure: bool = amount > Decimal(0)
```

`delegates` lists the parties the owner has disclosed the coin to. They're
observers: they can see the coin, but they can't act on it by themselves.

## Composing choices

A choice body can create, fetch, archive, and exercise as many contracts as it
needs. Everything it does is committed as one transaction, or not at all.

```python
    @choice(controller=owner, consuming=True)
    def Split(self, split_amount: Decimal) -> tuple[ContractId[Coin], ContractId[Coin]]:
        split = create(
            Coin(issuer=self.issuer, owner=self.owner, amount=split_amount, delegates=[])
        )
        rest = create(
            Coin(
                issuer=self.issuer,
                owner=self.owner,
                amount=self.amount - split_amount,
                delegates=[],
            )
        )
        return (split, rest)

    @choice(controller=owner, consuming=True)
    def Merge(self, other_id: ContractId[Coin]) -> ContractId[Coin]:
        other = fetch(other_id)
        assert other.issuer == self.issuer and other.owner == self.owner
        archive(other_id)
        return create(
            Coin(
                issuer=self.issuer,
                owner=self.owner,
                amount=self.amount + other.amount,
                delegates=[],
            )
        )
```

`Split` archives the coin (it's consuming) and creates two new ones. If either
`create` fails, the whole transaction fails: splitting off the full amount leaves
a remainder of zero, `ensure` rejects it, and the original coin stays active.

`Merge` fetches a second coin, checks that it belongs to the same issuer and
owner, archives it, and creates one coin with the combined amount. The owner
controls `Merge`, and the issuer's authority comes from the coin's signatories, so
the choice can archive a coin the issuer also signed.

```haskell
compose_test : Script ()
compose_test = do
  bank <- allocateParty "Bank"
  alice <- allocateParty "Alice"
  coin <- issue_coin bank alice
  (split, rest) <- submit alice do
    exerciseCmd coin Split with split_amount = 30.0
  merged <- submit alice do
    exerciseCmd split Merge with other_id = rest
  Some whole <- queryContractId alice merged
  assert (whole.amount == 100.0)
  submitMustFail alice do
    exerciseCmd merged Split with split_amount = 100.0
```

A choice that returns a tuple returns a Daml tuple, so Script code can unpack it
with `(split, rest) <- ...`.

## Propose and accept

A coin needs both the issuer and the owner to sign it, but a single transaction
is submitted by one party. The propose-accept pattern collects the signatures in
steps: one party proposes, the other accepts.

```python
@template
class CoinMaster:
    issuer: Party

    signatory: Party = issuer

    @choice(controller=issuer, consuming=False)
    def Invite(self, owner: Party) -> ContractId[CoinIssueProposal]:
        return create(CoinIssueProposal(issuer=self.issuer, owner=owner))


@template
class CoinIssueProposal:
    issuer: Party
    owner: Party

    signatory: Party = issuer
    observer: Party = owner

    @choice(controller=owner, consuming=True)
    def AcceptCoinProposal(self) -> ContractId[CoinIssueAgreement]:
        return create(CoinIssueAgreement(issuer=self.issuer, owner=self.owner))


@template
class CoinIssueAgreement:
    issuer: Party
    owner: Party

    signatory: list[Party] = [issuer, owner]

    @choice(controller=issuer, consuming=False)
    def Issue(self, amount: Decimal) -> ContractId[Coin]:
        return create(Coin(issuer=self.issuer, owner=self.owner, amount=amount, delegates=[]))
```

1. The issuer exercises `Invite`, which creates a proposal signed by the issuer.
   The owner is an observer, so they can see it.
2. The owner exercises `AcceptCoinProposal`. The proposal carries the issuer's
   signature, and the owner adds theirs as the controller, so the choice has the
   authority of both. It creates a `CoinIssueAgreement` that both have signed.
3. The agreement is a standing permission. The issuer exercises `Issue` as often
   as they like, and each new coin is signed by both parties.

The test package uses this flow as a helper for every other test:

```haskell
issue_coin : Party -> Party -> Script (ContractId Coin)
issue_coin issuer owner = do
  master <- submit issuer do
    createCmd CoinMaster with issuer = issuer
  proposal <- submit issuer do
    exerciseCmd master Invite with owner = owner
  issue_agreement <- submit owner do
    exerciseCmd proposal AcceptCoinProposal
  submit issuer do
    exerciseCmd issue_agreement Issue with amount = 100.0
```

`agreement` is a reserved word in Daml, so a Script variable can't use that name.

## Delegation

Delegation lets an agent act for a principal. The principal signs a power of
attorney, and the agent exercises its choices:

```python
@template
class CoinPoA:
    attorney: Party
    principal: Party

    signatory: Party = principal
    observer: Party = attorney

    @choice(controller=principal, consuming=True)
    def WithdrawPoA(self) -> None:
        pass

    @choice(controller=attorney, consuming=False)
    def TransferCoin(
        self, coin_id: ContractId[Coin], new_owner: Party
    ) -> ContractId[TransferProposal]:
        return exercise(coin_id, coin_id.Transfer(new_owner=new_owner))
```

`TransferCoin` exercises the coin's `Transfer` choice, which only the owner may
control. That works because the body of `TransferCoin` has the authority of
`CoinPoA`'s signatory, the principal.

Authority isn't enough on its own: the agent also has to see the coin. The owner
discloses it first with `Disclose`, which adds the agent to the coin's observers:

```python
    @choice(controller=owner, consuming=True)
    def Disclose(self, delegate: Party):
        self.delegates = self.delegates + [delegate]
```

`Disclose` assigns to `self`, so it returns the new contract ID together with the
choice's result, as described in [Choices](05-choices.md).

```haskell
  poa <- submit alice do
    createCmd CoinPoA with attorney = agent; principal = alice
  submitMustFail agent do
    exerciseCmd poa TransferCoin with coin_id = coin; new_owner = bob
  (disclosed, _) <- submit alice do
    exerciseCmd coin Disclose with delegate = agent
  proposal <- submit agent do
    exerciseCmd poa TransferCoin with coin_id = disclosed; new_owner = bob
```

The first attempt fails because the agent can't see the coin. After `Disclose`, the
same call succeeds.

## Authorization

Sometimes a choice should only run if a third party has given permission. The
permission is itself a contract, and the choice takes its ID as an argument:

```python
@template
class CoinOwnerAuthorization:
    issuer: Party
    owner: Party

    signatory: Party = issuer
    observer: Party = owner

    @choice(controller=issuer, consuming=True)
    def WithdrawAuthorization(self) -> None:
        pass
```

`Coin.Transfer` creates a `TransferProposal`, and the new owner accepts it with an
authorization token:

```python
@template
class TransferProposal:
    coin: Coin
    new_owner: Party

    signatory: list[Party] = [coin.issuer, coin.owner]
    observer: Party = new_owner

    @choice(controller=new_owner, consuming=True)
    def AcceptTransfer(self, token: ContractId[CoinOwnerAuthorization]) -> ContractId[Coin]:
        authorization = fetch(token)
        assert authorization.issuer == self.coin.issuer
        assert authorization.owner == self.new_owner
        return create(
            Coin(
                issuer=self.coin.issuer,
                owner=self.new_owner,
                amount=self.coin.amount,
                delegates=[],
            )
        )

    @choice(controller=coin.owner, consuming=True)
    def WithdrawTransfer(self) -> ContractId[Coin]:
        return create(self.coin)
```

A field can hold a whole template value, like `coin: Coin` here, and clauses can
reach into it (`coin.issuer`). `create(self.coin)` recreates the original coin.

`fetch(token)` fails if the token was archived, so withdrawing the authorization
blocks the transfer:

```haskell
  token <- submit bank do
    createCmd CoinOwnerAuthorization with issuer = bank; owner = bob
  proposal <- submit alice do
    exerciseCmd coin Transfer with new_owner = bob
  submit bank do
    exerciseCmd token WithdrawAuthorization
  submitMustFail bob do
    exerciseCmd proposal AcceptTransfer with token
```

## Locking

Locking freezes an asset, for example while a trade settles. One way to lock a
contract is to archive it and create a locked version that can be restored:

```python
    @choice(controller=owner, consuming=True)
    def Lock(self, locker: Party, maturity: datetime) -> ContractId[LockedCoin]:
        return create(LockedCoin(coin=self, locker=locker, maturity=maturity))
```

```python
@template
class LockedCoin:
    coin: Coin
    locker: Party
    maturity: datetime

    signatory: list[Party] = [coin.issuer, coin.owner]
    observer: Party = locker

    @choice(controller=locker, consuming=True)
    def Unlock(self) -> ContractId[Coin]:
        return create(self.coin)

    @choice(controller=coin.owner, consuming=True)
    def Clawback(self) -> ContractId[Coin]:
        assert datetime.now() >= self.maturity
        return create(self.coin)
```

While the coin is locked, none of `Coin`'s choices can be exercised, because the
coin isn't active. The locker can release it with `Unlock`. If the locker never
does, the owner can take it back with `Clawback` once `maturity` has passed.
`datetime.now()` reads the ledger time; [Working with Time](07-working-with-time.md)
covers it in detail.

```haskell
  locked <- submit alice do
    exerciseCmd coin Lock with locker = escrow; maturity = addRelTime now (days 1)
  submitMustFail alice do
    exerciseCmd locked Clawback
  passTime (days 2)
  restored <- submit alice do
    exerciseCmd locked Clawback
```

## Multiple-party agreement

Propose-accept works for two parties. When many parties must sign one contract, a
pending contract collects the signatures one at a time:

```python
@template
class Agreement:
    signatories: list[Party]

    signatory: list[Party] = signatories
    ensure: bool = unique(signatories)


@template
class Pending:
    final_contract: Agreement
    already_signed: list[Party]

    signatory: list[Party] = already_signed
    observer: list[Party] = final_contract.signatories
    ensure: bool = unique(already_signed)

    @choice(controller=signer, consuming=True)
    def Sign(self, signer: Party):
        assert signer in self.final_contract.signatories
        assert signer not in self.already_signed
        self.already_signed = [signer] + self.already_signed

    @choice(controller=signer, consuming=True)
    def Finalize(self, signer: Party) -> ContractId[Agreement]:
        assert sort(self.already_signed) == sort(self.final_contract.signatories)
        return create(self.final_contract)
```

Each `Sign` archives the pending contract and recreates it with one more
signatory. The controller is a choice argument, so whoever signs must submit the
transaction themselves. Once everyone has signed, any signer can `Finalize`, and
the `Agreement` is created with the authority of all of them.

```haskell
  let final_contract = Agreement with signatories = [alice, bob, carol]
  pending <- submit alice do
    createCmd Pending with final_contract = final_contract; already_signed = [alice]
  submitMustFail alice do
    exerciseCmd pending Finalize with signer = alice
  (pending, _) <- submit bob do
    exerciseCmd pending Sign with signer = bob
  (pending, _) <- submit carol do
    exerciseCmd pending Sign with signer = carol
```

## Running the tests

```text
daml/CoinTest.daml:multi_party_test: ok, 1 active contracts, 5 transactions.
daml/CoinTest.daml:compose_test: ok, 3 active contracts, 7 transactions.
daml/CoinTest.daml:propose_accept_test: ok, 3 active contracts, 4 transactions.
daml/CoinTest.daml:authorization_test: ok, 4 active contracts, 10 transactions.
daml/CoinTest.daml:delegation_test: ok, 4 active contracts, 8 transactions.
daml/CoinTest.daml:locking_test: ok, 3 active contracts, 10 transactions.
```

## Next steps

[Working with Time](07-working-with-time.md) shows how to add deadlines, waiting
periods, and time windows to choices like `AcceptTransfer`.
