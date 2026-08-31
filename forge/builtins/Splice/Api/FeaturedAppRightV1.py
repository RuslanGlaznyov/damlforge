"""Stand-in for the real `Splice.Api.FeaturedAppRightV1` Daml module
(`splice/daml/splice-api-featured-app-v1/daml/Splice/Api/FeaturedAppRightV1.daml`)
- IDE/authoring support only, see `Splice/__init__.py`.
"""

from dataclasses import dataclass
from decimal import Decimal

from forge.models.types import Party


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
