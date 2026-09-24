"""Authoring stubs for ``Splice.Api.RewardAssignmentV1``."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Annotated

from forge.models.types import ContractId, Party
from ... import DamlName
from .Token.MetadataV1 import ExtraArgs


class RewardCoupon:
    pass


@dataclass(frozen=True)
class RewardBeneficiary:
    beneficiary: Party
    percentage: Decimal


@dataclass(frozen=True)
class RewardCoupon_AssignBeneficiaries:
    additional_coupons: Annotated[
        list[ContractId[RewardCoupon]], DamlName("additionalCoupons")
    ]
    new_beneficiaries: Annotated[list[RewardBeneficiary], DamlName("newBeneficiaries")]
    extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]


@dataclass(frozen=True)
class RewardCoupon_AssignBeneficiariesResult:
    new_beneficiaries_coupon_cids: Annotated[
        list[tuple[Party, list[ContractId[RewardCoupon]]]],
        DamlName("newBeneficiariesCouponCids"),
    ]
