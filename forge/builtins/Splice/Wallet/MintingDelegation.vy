from datetime import datetime
from typing import Annotated

from forge.models import choice, ContractId, Optional, Party, template
from forge.builtins import DamlName
from Splice.AmuletRules import PaymentTransferContext, TransferInput, TransferResult
from Splice.Api.RewardAssignmentV1 import RewardCoupon, RewardCoupon_AssignBeneficiaries, RewardCoupon_AssignBeneficiariesResult


struct MintingDelegationProposal_AcceptResult:
    minting_delegation_cid: Annotated[ContractId[MintingDelegation], DamlName("mintingDelegationCid")]


struct MintingDelegationProposal_RejectResult:
    pass


struct MintingDelegationProposal_WithdrawResult:
    pass


struct MintingDelegation_RejectResult:
    pass


struct MintingDelegation_WithdrawResult:
    pass


struct MintingDelegation_MintResult:
    transfer_result: Annotated[TransferResult, DamlName("transferResult")]


struct MintingDelegation_AssignAndMintResult:
    assign_result: Annotated[RewardCoupon_AssignBeneficiariesResult, DamlName("assignResult")]
    transfer_result: Annotated[TransferResult, DamlName("transferResult")]


@template
class MintingDelegationProposal:
    delegation: MintingDelegation

    signatory: list[Party] = [delegation.beneficiary]
    observer: list[Party] = [delegation.delegate]

    @choice(controller=delegation.delegate, consuming=True)
    def MintingDelegationProposal_Accept(self, existing_delegation_cid: Annotated[Optional[ContractId[MintingDelegation]], DamlName("existingDelegationCid")]) -> MintingDelegationProposal_AcceptResult:
        pass

    @choice(controller=delegation.delegate, consuming=True)
    def MintingDelegationProposal_Reject(self) -> MintingDelegationProposal_RejectResult:
        pass

    @choice(controller=delegation.beneficiary, consuming=True)
    def MintingDelegationProposal_Withdraw(self) -> MintingDelegationProposal_WithdrawResult:
        pass


@template
class MintingDelegation:
    beneficiary: Party
    delegate: Party
    dso: Party
    expires_at: Annotated[datetime, DamlName("expiresAt")]
    amulet_merge_limit: Annotated[int, DamlName("amuletMergeLimit")]

    signatory: list[Party] = [beneficiary, delegate]

    @choice(controller=delegate, consuming="nonconsuming")
    def MintingDelegation_Mint(self, inputs: list[TransferInput], context: PaymentTransferContext) -> MintingDelegation_MintResult:
        pass

    @choice(controller=delegate, consuming="nonconsuming")
    def MintingDelegation_AssignAndMint(self, coupon_cid: Annotated[ContractId[RewardCoupon], DamlName("couponCid")], assign_beneficiaries: Annotated[RewardCoupon_AssignBeneficiaries, DamlName("assignBeneficiaries")], inputs: list[TransferInput], context: PaymentTransferContext) -> MintingDelegation_AssignAndMintResult:
        pass

    @choice(controller=delegate, consuming=True)
    def MintingDelegation_Reject(self) -> MintingDelegation_RejectResult:
        pass

    @choice(controller=beneficiary, consuming=True)
    def MintingDelegation_Withdraw(self) -> MintingDelegation_WithdrawResult:
        pass
