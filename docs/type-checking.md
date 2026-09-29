# Type-checking architecture

The semantic checker uses a bidirectional model implemented in
`forge/semantics/analysis/typecheck.py`.

## Statement order

Statements are checked from top to bottom. A right-hand side is checked before
its assignment becomes visible:

```text
resolve annotation -> check RHS -> unify RHS with annotation -> bind name
```

Branches receive child environments. A loop binds its target from the element
type of the iterable. This keeps scope and visibility deterministic.

## Expression direction

Expressions accept an optional expected type and return an inferred type:

```text
check_expr(expression, expected_type, environment) -> inferred_type
```

Examples:

- `amount: Decimal = 1` checks the integer literal in Decimal context.
- `list[Int]` checks every list element against Int.
- A function call resolves its signature before checking each argument.
- An `if` condition is checked against Bool and both branches share a result
  type constraint.

## Inference and constraints

The `InferenceContext` creates type variables for expressions without an
annotation, then unifies them as values are visited. For example, an
unannotated list creates one element variable and unifies every element with
that same variable. A later incompatible element therefore produces a type
error instead of silently changing the list type chosen by the first element.

Optional values are represented as an explicit compatibility rule. Passing a
plain value to `Optional[T]` records a `Some` conversion; assigning an optional
value to `T` records an unwrap. Existing lowering consumes those metadata
markers.

Primitive bounds remain owned by the policy registry and are checked by the
primitive-policy phase. The type checker decides which expected type applies;
the policy checker decides whether the value is valid for that type.
