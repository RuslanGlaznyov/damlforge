# Daml value policies

The executable registry for these rules is
[`forge/semantics/primitive_specs.py`](../forge/semantics/primitive_specs.py).
The semantic pass applies it after the AST and intrinsic metadata are ready.
Diagnostics use `DF1229`.

## Primitive values

| Daml type | Policy enforced here |
| --- | --- |
| `Int` | Signed 64-bit range: `-2^63 .. 2^63-1`. Constant arithmetic is checked when it can be evaluated at compile time. |
| `Decimal` / `Numeric 10` | 38 total digits, at most 10 fractional digits, and range `[-(10^38-1)/10^10, +(10^38-1)/10^10]`. |
| `Text` | Unicode text. There is no fixed Daml length limit; invalid UTF-16 surrogate code points are rejected. |
| `Party` | Ordered/comparable/serializable Daml value. Party identifiers are opaque values and should be obtained through the party lookup intrinsic rather than treated as arbitrary text. |
| `Date` | Gregorian date from `0001-01-01` through `9999-12-31`. Literal `datetime.date(...)` calls are checked. |
| `Time` / Python `datetime` | UTC timestamp through microsecond precision, from `0001-01-01T00:00:00` through `9999-12-31T23:59:59.999999`. The supported date/time constructors are checked before lowering. |
| `RelTime` | Signed 64-bit microsecond count. Literal `datetime.timedelta(...)` totals are checked before lowering. |
| `Bool` / Python `bool` | Boolean values only; serializable and comparable. |
| `Unit` / Python `None` | The single unit value; serializable and comparable. |

The registry also records the general `Numeric n` policy: precision 38 and a
scale `n` in `0..37`. The current Python-facing surface exposes `Decimal`
(`Numeric 10`) rather than arbitrary `Numeric[n]` annotations.

## Containers and type structure

| Type | Policy |
| --- | --- |
| `Optional[a]`, `list[a]`, `ContractId[a]`, `set[a]` / `frozenset[a]` | Exactly one type argument. |
| `tuple[a, ...]` | Daml-LF tuple arity is 2 through 20. |
| `TextMap[v]` | Exactly one value type; keys are always `Text`. |
| `GenMap[k, v]` | Exactly two type arguments; keys must have an ordered Daml representation. |
| `Set[k]` | Elements must have an ordered Daml representation. |

The registry keeps serializability, equality, and ordering metadata alongside
the bounds so future checks do not need to rediscover those properties. The
current semantic pass reports malformed arity and obviously unmappable map
keys; runtime-dependent container sizes and dynamically computed values remain
runtime concerns.

## Sources

These policies were extracted from the Digital Asset Daml 3.x reference:

- [Daml data types](https://docs.digitalasset.com/build/3.4/reference/daml/data-types.html)
- [Daml expressions and operators](https://docs.digitalasset.com/build/3.4/reference/daml/expressions.html)
- [DA.Time](https://archived.docs.digitalasset.com/build/3.5/reference/daml/stdlib/DA-Time.html)
- [DA.Set](https://docs.digitalasset.com/build/3.4/reference/daml/stdlib/DA-Set.html)
- [DA.Map](https://docs.digitalasset.com/build/3.5/reference/daml/stdlib/DA-Map.html)
- [DA.TextMap](https://docs.digitalasset.com/build/3.4/reference/daml/stdlib/DA-TextMap.html)
- [Daml-LF translation and serializable types](https://archived.docs.digitalasset.com/build/3.5/reference/damllf/daml-lf-translation.html)
- [JSON LF value ranges](https://archived.docs.digitalasset.com/build/3.4/reference/json-api/lf-value-specification.html)
