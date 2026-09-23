"""Stand-in for the real `Splice.Api.FeaturedAppRightV2` Daml module
(`splice/daml/splice-api-featured-app-v2/daml/Splice/Api/FeaturedAppRightV2.daml`)
- IDE/authoring support only, see `Splice/__init__.py`.

`FeaturedAppRightV1` and `FeaturedAppRightV2` both export a real Daml type
named `FeaturedAppRight` (and `AppRewardBeneficiary`, and so on) - two
different real packages, same names. A `.vy` file that needs both imports
each module qualified (`import Splice.Api.FeaturedAppRightV1 as FAR1`)
and references types as `FAR1.FeaturedAppRight` / `FAR2.FeaturedAppRight`,
so the real names are kept here unchanged.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Annotated, Optional

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
    """The real Daml `Splice.Api.FeaturedAppRightV2.FeaturedAppRight`
    interface - referenced here only as a nominal type for
    `ContractId[FeaturedAppRight]`."""


class FeaturedAppActivityMarker:
    """The real Daml `Splice.Api.FeaturedAppRightV2.FeaturedAppActivityMarker`
    interface - referenced here only as a nominal type for
    `ContractId[FeaturedAppActivityMarker]`."""


@dataclass(frozen=True)
class FeaturedAppRight_CreateActivityMarker:
    """`FeaturedAppRight`'s `FeaturedAppRight_CreateActivityMarker` choice
    arguments. Real Daml definition:

        data FeaturedAppRight_CreateActivityMarker = FeaturedAppRight_CreateActivityMarker
          with
            beneficiaries : [AppRewardBeneficiary]
            weight : Optional Decimal
    """

    beneficiaries: list[AppRewardBeneficiary]
    weight: Optional[Decimal]


@no_derive
@dataclass(frozen=True)
class FeaturedAppRight_CreateActivityMarkerResult:
    """The real Daml `FeaturedAppRight_CreateActivityMarkerResult` record,
    returned by `FeaturedAppRight_CreateActivityMarker`. Real Daml definition:

        data FeaturedAppRight_CreateActivityMarkerResult =
          FeaturedAppRight_CreateActivityMarkerResult
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
