"""Stand-in for the real `Splice.ValidatorLicense` Daml module
(`splice/daml/splice-amulet/daml/Splice/ValidatorLicense.daml`) -
IDE/authoring support only, see `Splice/__init__.py`. Covers only the two
templates `AmuletRules_ClaimExpiredRewards` references by `ContractId`.
"""

from dataclasses import dataclass

from forge.models.types import ContractId, Party
from Splice.Round import ClosedMiningRound
from Splice.Types import Round


@dataclass(frozen=True)
class ValidatorFaucetCoupon:
    """The real Daml `ValidatorFaucetCoupon` template - a per-round faucet
    coupon for a validator operator. DEPRECATED in real Daml - use
    `ValidatorLicense_RecordValidatorLivenessActivity` instead. Real Daml
    definition:

        template ValidatorFaucetCoupon with
            dso : Party
            validator : Party
            round : Round
          where
            signatory dso, validator
    """

    dso: Party
    validator: Party
    round: Round


@dataclass(frozen=True)
class ValidatorFaucetCoupon_DsoExpire:
    """`ValidatorFaucetCoupon`'s `ValidatorFaucetCoupon_DsoExpire` choice -
    archives the coupon once its round has closed. Controller `dso`. Real
    Daml:

        choice ValidatorFaucetCoupon_DsoExpire : ValidatorFaucetCoupon_DsoExpireResult
          with
            closedRoundCid : ContractId ClosedMiningRound
    """

    closed_round_cid: ContractId[ClosedMiningRound]


@dataclass(frozen=True)
class ValidatorFaucetCoupon_DsoExpireResult:
    """Real Daml: `data ValidatorFaucetCoupon_DsoExpireResult = ...`
    (no fields)."""


@dataclass(frozen=True)
class ValidatorLivenessActivityRecord:
    """The real Daml `ValidatorLivenessActivityRecord` template - a record
    of a validator's liveness activity for a round; a copy of
    `ValidatorFaucetCoupon` where the validator is only an observer, so it
    can be expired without the validator's involvement. Real Daml
    definition:

        template ValidatorLivenessActivityRecord with
            dso : Party
            validator : Party
            round : Round
          where
            signatory dso
            observer validator
    """

    dso: Party
    validator: Party
    round: Round


@dataclass(frozen=True)
class ValidatorLivenessActivityRecord_DsoExpire:
    """`ValidatorLivenessActivityRecord`'s
    `ValidatorLivenessActivityRecord_DsoExpire` choice - archives the record
    once its round has closed. Controller `dso`. Real Daml:

        choice ValidatorLivenessActivityRecord_DsoExpire : ValidatorLivenessActivityRecord_DsoExpireResult
          with
            closedRoundCid : ContractId ClosedMiningRound
    """

    closed_round_cid: ContractId[ClosedMiningRound]


@dataclass(frozen=True)
class ValidatorLivenessActivityRecord_DsoExpireResult:
    """Real Daml: `data ValidatorLivenessActivityRecord_DsoExpireResult = ...`
    (no fields)."""
