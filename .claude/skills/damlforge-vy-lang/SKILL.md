---
name: DamlForge-Vy-Lang
description: Use when writing, reading, or reviewing .vy source files in the DamlForge compiler (this repo) - a Python/Vyper-syntax DSL that compiles to real Daml/Canton smart contracts. Applies whenever asked to author a Daml template/choice/interface in .vy, translate a .daml file to .vy, or explain DF12xx compiler errors.
---

# DamlForge .vy Language

## Overview

DamlForge compiles `.vy` files (Python syntax, Vyper-flavored keywords) into real `.daml` source. It is NOT Vyper (no EVM/gas/storage concepts survive) and NOT Python (nothing executes - it's an AST that lowers straight to Daml). Full detail: [reference.md](reference.md).

## Before writing any .vy file

1. Every field/type name in the file must resolve to one of: a Python-native type, a DamlForge builtin type (`Party`, `Decimal`, `Int`, `Date`, `Timestamp`, `ContractId[T]`, `GenMap[K,V]`, `TextMap[T]`), or a `struct`/`template`/`interface`/`flag` declared/imported in scope. See reference.md § Type System.
2. Every **decorator** (`@choice`, `@view`, `@ledger_effect`, `@template`, `@DamlName`) must be imported from `forge.models` or `forge.builtins` - unlike ledger builtins, decorators are NOT auto-available. See reference.md § Decorators.
3. Every `template` needs `signatory`. `key` requires `maintainer` and vice versa. `ensure` (if present) must be a `bool`-typed comparison/boolop/call, never bare arithmetic. See reference.md § Template Fields.
4. A plain `def` that calls `fetch`/`exercise`/`create`/`archive`/`lookup` must be marked `@ledger_effect` (choices are exempt). See reference.md § Ledger Effects.
5. Never put a `def` inside a `struct` - it is silently dropped, no error. Use a free top-level function instead.

## Quick Reference

| Concept | `.vy` syntax |
|---|---|
| Record type | `struct Foo:` |
| Contract type | `template Foo:` or `@template\nclass Foo:` |
| Interface | `interface Foo(view=FooView):` |
| Interface impl | `template Bar(Foo):` (subclass the interface directly - no `instance` keyword) |
| Sum type / enum | `flag Status:\n    PENDING\n    PAID` (members MUST be `SCREAMING_CASE`) |
| Choice | `@choice(controller=..., consuming=True)` |
| Fetch/exercise/create/archive/lookup | called directly, no import needed |
| Optional field | `Optional[X]` - never write `Some(...)`/`from_some(...)` yourself, the compiler inserts it |
| Map | `GenMap[K, V]` / `TextMap[V]`, dict literal `{...}`, `m[k]`, `k in m` |
| Typed for-loop | `for x: T in xs:` (annotation is mandatory before `in`) |

## Common Mistakes

| Mistake | Fix |
|---|---|
| Using `@choice`/`@view`/`@template` without importing it | `from forge.models import choice, view, template` (or `forge.builtins` for `DamlName`) |
| Writing `def helper(): ...` inside a `struct` | Move it to a top-level `def`; structs are plain data records |
| `controller=`/`observer=` referencing a name that isn't a with-arg, a template field, or `self.<field>` | Only reference the choice's own arguments/fields - anything else either resolves to an unrelated same-named field or fails `damlc` with "Ambiguous occurrence" (`DF1224`) |
| `key` without `maintainer` (or vice versa) | Always declare both together (`DF1210`/`DF1211`) |
| A bare `def` calling `archive(self)`/`fetch(...)` etc. | Add `@ledger_effect` above it (`DF1205`) |
| `from X import Y as Z` | Aliased from-imports are banned; use `import X as Y` (module alias) instead if disambiguation is needed |
| `dict[K, V]` or a hand-rolled `Map[...]` field | Use `GenMap[K, V]` / `TextMap[V]` |

Full syntax, decorator/builtin tables, type system, error-code index, and a worked example: [reference.md](reference.md).
