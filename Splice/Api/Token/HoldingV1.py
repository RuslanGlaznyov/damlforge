"""Stand-in for the real `Splice.Api.Token.HoldingV1` Daml module
(the `splice-api-token-holding-v1` package) - IDE/authoring support only,
see `Splice/__init__.py`. `Holding` is a real Daml `interface` with its own
large choice set (transfer, archive, ...); only referenced here as a
nominal `ContractId[Holding]` type, since that's the only way
`created_amulet_to_holding` (`Splice.AmuletRules`) is ever used in this
codebase's real examples - modeling the full token-standard Holding
interface is out of scope of the `AmuletRules` choice sweep.
"""


class Holding:
    """The real Daml `Splice.Api.Token.HoldingV1.Holding` interface -
    referenced here only as a nominal type for `ContractId[Holding]`."""
