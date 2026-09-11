"""Stand-in for the real `Splice.Api.FeaturedAppRightV1` Daml module
(`splice/daml/splice-api-featured-app-v1/daml/Splice/Api/FeaturedAppRightV1.daml`)
- IDE/authoring support only, see `Splice/__init__.py`.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Annotated

from forge.models.types import ContractId, Party
from ... import DamlName, no_derive


@dataclass(frozen=True)
class AppRewardBeneficiary:
    """Specification of a beneficiary of featured app rewards. Real Daml
    definition:

        data AppRewardBeneficiary = AppRewardBeneficiary
          with
            beneficiary : Party
            weight : Decimal
          deriving (Show, Eq, Ord)
    """

    beneficiary: Party
    weight: Decimal


class FeaturedAppRight:
    """The real Daml `Splice.Api.FeaturedAppRightV1.FeaturedAppRight`
    interface - referenced here only as a nominal type for
    `ContractId[FeaturedAppRight]`."""


class FeaturedAppActivityMarker:
    """The real Daml `Splice.Api.FeaturedAppRightV1.FeaturedAppActivityMarker`
    interface - referenced here only as a nominal type for
    `ContractId[FeaturedAppActivityMarker]`."""


@dataclass(frozen=True)
class FeaturedAppRight_CreateActivityMarker:
    """`FeaturedAppRight`'s `FeaturedAppRight_CreateActivityMarker` choice
    arguments. Real Daml definition:

        data FeaturedAppRight_CreateActivityMarker = FeaturedAppRight_CreateActivityMarker
          with
            beneficiaries : [AppRewardBeneficiary]
    """

    beneficiaries: list[AppRewardBeneficiary]


@no_derive
@dataclass(frozen=True)
class FeaturedAppRight_CreateActivityMarkerResult:
    """The real Daml `FeaturedAppRight_CreateActivityMarkerResult` record,
    returned by `FeaturedAppRight_CreateActivityMarker`. Real Daml definition:

        data FeaturedAppRight_CreateActivityMarkerResult = FeaturedAppRight_CreateActivityMarkerResult
          with
            activityMarkerCids : [ContractId FeaturedAppActivityMarker]
    """

    activity_marker_cids: Annotated[
        list[ContractId[FeaturedAppActivityMarker]], DamlName("activityMarkerCids")
    ]


@dataclass(frozen=True)
class FeaturedAppRightView:
    """The real Daml `FeaturedAppRightView` record - the `viewtype` of
    `FeaturedAppRight`. Real Daml definition:

        data FeaturedAppRightView = FeaturedAppRightView
          with
            dso : Party
            provider : Party
          deriving (Show, Eq)
    """

    dso: Party
    provider: Party
