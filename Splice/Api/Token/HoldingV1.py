"""Stand-in for the real `Splice.Api.Token.HoldingV1` Daml module
(the `splice-api-token-holding-v1` package) - IDE/authoring support only,
see `Splice/__init__.py`. `Holding` is a real Daml `interface` with its own
large choice set (transfer, archive, ...); only referenced here as a
nominal `ContractId[Holding]` type, since that's the only way
`created_amulet_to_holding` (`Splice.AmuletRules`) is ever used in this
codebase's real examples - modeling the full token-standard Holding
interface is out of scope of the `AmuletRules` choice sweep.
"""

from dataclasses import dataclass

from forge.models.types import Party, Text


class Holding:
    """The real Daml `Splice.Api.Token.HoldingV1.Holding` interface -
    referenced here only as a nominal type for `ContractId[Holding]`."""


@dataclass(frozen=True)
class InstrumentId:
    """The real Daml `InstrumentId` record - identifies a token-standard
    instrument (e.g. Amulet itself) by its admin party and a free-form id.
    Real Daml definition:

        data InstrumentId = InstrumentId with
            admin : Party
            id : Text
          deriving (Eq, Ord, Show)
    """

    admin: Party
    id: Text
