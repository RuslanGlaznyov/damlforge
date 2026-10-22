from typing import Annotated, TypeVar

from forge.models import choice, ContractId, GenMap, Optional, Party, template
from forge.builtins import DamlName
from Splice.Api.FeaturedAppRightV1 import AppRewardBeneficiary, FeaturedAppRight
from Splice.Api.Token.HoldingV1 import Holding, InstrumentId
from Splice.Api.Token.MetadataV1 import Metadata
from Splice.Api.Token.TransferInstructionV1 import TransferFactory, TransferFactory_Transfer, TransferInstructionResult

A = TypeVar("A")


InstrumentHoldingMap = GenMap[InstrumentId, list[ContractId[Holding]]]


struct TransferCall:
    factory_cid: Annotated[ContractId[TransferFactory], DamlName("factoryCid")]
    choice_arg: Annotated[TransferFactory_Transfer, DamlName("choiceArg")]


struct FeaturedAppRightCall:
    app_right_cid: Annotated[ContractId[FeaturedAppRight], DamlName("appRightCid")]
    beneficiaries: list[AppRewardBeneficiary]


struct MergeDelegation_MergeResult:
    opt_merge_transfer_result: Annotated[Optional[TransferInstructionResult], DamlName("optMergeTransferResult")]
    opt_extra_transfer_result: Annotated[Optional[TransferInstructionResult], DamlName("optExtraTransferResult")]


struct MergeDelegation_RejectResult:
    result: None


struct MergeDelegation_WithdrawResult:
    result: None


struct MergeDelegationCall:
    delegation_cid: Annotated[ContractId[MergeDelegation], DamlName("delegationCid")]
    choice_arg: Annotated[MergeDelegation_Merge, DamlName("choiceArg")]


struct BatchMergeUtility_BatchMergeResult:
    results: list[MergeDelegation_MergeResult]
    operator_change_map: Annotated[GenMap[InstrumentId, list[ContractId[Holding]]], DamlName("operatorChangeMap")]


struct MergeDelegationProposal_AcceptResult:
    merge_delegation_cid: Annotated[ContractId[MergeDelegation], DamlName("mergeDelegationCid")]


struct MergeDelegationProposal_RejectResult:
    result: None


struct MergeDelegationProposal_WithdrawResult:
    result: None


@template
class MergeDelegation:
    operator: Party
    owner: Party
    meta: Metadata

    signatory: list[Party] = [operator, owner]

    @choice(controller=operator, consuming="nonconsuming")
    def MergeDelegation_Merge(self, opt_merge_transfer: Annotated[Optional[TransferCall], DamlName("optMergeTransfer")], opt_extra_transfer: Annotated[Optional[TransferCall], DamlName("optExtraTransfer")], opt_featured_app_right: Annotated[Optional[FeaturedAppRightCall], DamlName("optFeaturedAppRight")]) -> MergeDelegation_MergeResult:
        pass

    @choice(controller=operator, consuming=True)
    def MergeDelegation_Reject(self) -> MergeDelegation_RejectResult:
        pass

    @choice(controller=owner, consuming=True)
    def MergeDelegation_Withdraw(self) -> MergeDelegation_WithdrawResult:
        pass


@template
class BatchMergeUtility:
    operator: Party

    signatory: list[Party] = [operator]

    @choice(controller=operator, consuming="nonconsuming")
    def BatchMergeUtility_BatchMerge(self, merge_calls: Annotated[list[MergeDelegationCall], DamlName("mergeCalls")]) -> BatchMergeUtility_BatchMergeResult:
        pass


@template
class MergeDelegationProposal:
    delegation: MergeDelegation

    signatory: list[Party] = [delegation.owner]
    observer: list[Party] = [delegation.operator]

    @choice(controller=delegation.operator, consuming=True)
    def MergeDelegationProposal_Accept(self) -> MergeDelegationProposal_AcceptResult:
        pass

    @choice(controller=delegation.operator, consuming=True)
    def MergeDelegationProposal_Reject(self) -> MergeDelegationProposal_RejectResult:
        pass

    @choice(controller=delegation.owner, consuming=True)
    def MergeDelegationProposal_Withdraw(self) -> MergeDelegationProposal_WithdrawResult:
        pass


@DamlName("runBatch", is_ledger_effect=True)
def run_batch(party: Party, list_value: list[MergeDelegationCall], holding_map: GenMap[InstrumentId, list[ContractId[Holding]]], results: list[MergeDelegation_MergeResult]) -> BatchMergeUtility_BatchMergeResult:
    pass


@DamlName("createActivityMarkerForProvider", is_ledger_effect=True)
def create_activity_marker_for_provider(provider: Party, call: FeaturedAppRightCall) -> None:
    pass


@DamlName("checkExpected", is_ledger_effect=True)
def check_expected(description: str, expected: A, actual: A) -> None:
    pass


@DamlName("require", is_ledger_effect=True)
def require(msg: str, invariant: bool) -> None:
    pass
