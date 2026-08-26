"""Stand-in for the real `Splice.Types` Daml module
(`splice/daml/splice-amulet/daml/Splice/Types.daml`) - IDE/authoring support
only, see `Splice/__init__.py`.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Round:
    """The real Daml `Round` newtype - identifies a mining round by its
    sequence number. Real Daml definition:

        newtype Round = Round with number : Int
    """

    number: int
