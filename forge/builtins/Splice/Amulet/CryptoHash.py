"""Stand-in for the real `Splice.Amulet.CryptoHash` Daml module
(`splice/daml/splice-amulet/daml/Splice/Amulet/CryptoHash.daml`) -
IDE/authoring support only, see `Splice/__init__.py`.
"""

from dataclasses import dataclass

from forge.models.types import Text


@dataclass(frozen=True)
class Hash:
    """The real Daml `Hash` record - an opaque content hash used to
    deduplicate reward-processing batches. Real Daml definition:

        data Hash = Hash with value : Text
    """

    value: Text
