"""Stand-in for the real `Splice.Expiry` Daml module
(`splice/daml/splice-amulet/daml/Splice/Expiry.daml`) - IDE/authoring
support only, see `Splice/__init__.py`.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Annotated, Optional

from forge.models.types import Party, Text
from .. import DamlName


@dataclass(frozen=True)
class TimeLock:
    """The real Daml `TimeLock` record - locks a `LockedAmulet` to a set of
    holders until `expires_at`. Real Daml definition:

        data TimeLock = TimeLock with
            holders: [Party]
            expiresAt: Time
            optContext : Optional Text
          deriving (Eq, Show, Ord)
    """

    holders: list[Party]
    expires_at: Annotated[datetime, DamlName("expiresAt")]
    opt_context: Annotated[Optional[Text], DamlName("optContext")] = None
