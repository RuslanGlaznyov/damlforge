"""Stand-in for the real `Splice.Api.Token.MetadataV1` Daml module
(`splice/token-standard/splice-api-token-metadata-v1/daml/Splice/Api/Token/MetadataV1.daml`)
- IDE/authoring support only, see `Splice/__init__.py`.
"""

from dataclasses import dataclass

from forge.models.types import Text, TextMap


@dataclass(frozen=True)
class AnyValue:
    pass


class AnyContractId:
    pass


@dataclass(frozen=True)
class Metadata:
    """The real Daml `Metadata` record - free-form token-standard metadata
    key/value pairs attached to a transfer event. Real Daml definition:

        data Metadata = Metadata with
            values : TextMap Text
          deriving (Eq, Ord, Show)
    """

    values: TextMap[Text]


@dataclass(frozen=True)
class ChoiceContext:
    """The real Daml `ChoiceContext` record - implementation-specific
    key/value data a caller must pass back into a token-standard choice.
    Real Daml definition:

        data ChoiceContext = ChoiceContext with
            values : TextMap AnyValue
    """

    values: dict


@dataclass(frozen=True)
class ExtraArgs:
    """The real Daml `ExtraArgs` record - extra context/metadata passed
    alongside a token-standard choice exercise. Real Daml definition:

        data ExtraArgs = ExtraArgs with
            context : ChoiceContext
            meta : Metadata
    """

    context: ChoiceContext
    meta: Metadata
