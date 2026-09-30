from datetime import datetime
from typing import Optional

from forge.builtins import DamlName
from forge.builtins.daml_lang import create, exercise, from_interface_contract_id
from forge.models import ContractId, Party, checked_fetch, choice, template
from DA.Assert import assert_within_deadline
from Splice.Amulet import RewardCouponV2
from Splice.AmuletRules import (
    AmuletRules_Transfer,
    InputRewardCouponV2,
    PaymentTransferContext,
    Transfer,
    TransferContext,
    TransferInput,
    TransferResult,
)
from Splice.Api.RewardAssignmentV1 import (
    RewardCoupon,
    RewardCoupon_AssignBeneficiaries,
    RewardCoupon_AssignBeneficiariesResult,
)
from Splice.Types import ForOwner
from Splice.Util import fetch_and_archive, fetch_checked_interface


struct MintingDelegationProposal_AcceptResult:
    mintingDelegationCid: ContractId[MintingDelegation]


struct MintingDelegationProposal_RejectResult:
    pass


struct MintingDelegationProposal_WithdrawResult:
    pass


struct MintingDelegation_RejectResult:
    pass


struct MintingDelegation_WithdrawResult:
    pass


struct MintingDelegation_MintResult:
    transferResult: TransferResult


struct MintingDelegation_AssignAndMintResult:
    assignResult: RewardCoupon_AssignBeneficiariesResult
    transferResult: TransferResult


@template
class MintingDelegationProposal:
    delegation: MintingDelegation

    signatory: Party = delegation.beneficiary
    observer: Party = delegation.delegate

    @DamlName("MintingDelegationProposal_Accept")
    @choice(controller=delegation.delegate, consuming=True)
    def accept(
        self, existingDelegationCid: Optional[ContractId[MintingDelegation]]
    ) -> MintingDelegationProposal_AcceptResult:
        if existingDelegationCid is not None:
            cid: ContractId[MintingDelegation] = existingDelegationCid
            existing = fetch_and_archive(
                ForOwner(
                    dso=self.delegation.dso,
                    owner=self.delegation.beneficiary,
                ),
                cid,
            )
            assert existing.delegate == self.delegation.delegate, "delegate matches"
        delegation_cid = create(self.delegation)
        return MintingDelegationProposal_AcceptResult(
            mintingDelegationCid=delegation_cid
        )

    @DamlName("MintingDelegationProposal_Reject")
    @choice(controller=delegation.delegate, consuming=True)
    def reject(self) -> MintingDelegationProposal_RejectResult:
        return MintingDelegationProposal_RejectResult()

    @DamlName("MintingDelegationProposal_Withdraw")
    @choice(controller=delegation.beneficiary, consuming=True)
    def withdraw(self) -> MintingDelegationProposal_WithdrawResult:
        return MintingDelegationProposal_WithdrawResult()

    @checked_fetch
    def contract_group_id(self) -> ForOwner:
        return ForOwner(
            dso=self.delegation.dso, owner=self.delegation.beneficiary
        )


@template
class MintingDelegation:
    beneficiary: Party
    delegate: Party
    dso: Party
    expiresAt: datetime
    amuletMergeLimit: int

    signatory: list[Party] = [beneficiary, delegate]

    @DamlName("MintingDelegation_Mint")
    @choice(controller=delegate, consuming=False)
    def mint(
        self, inputs: list[TransferInput], context: PaymentTransferContext
    ) -> MintingDelegation_MintResult:
        assert_within_deadline("expiresAt", self.expiresAt)
        transfer_context = TransferContext(
            open_mining_round=context.context.open_mining_round,
            issuing_mining_rounds=context.context.issuing_mining_rounds,
            validator_rights=context.context.validator_rights,
            featured_app_right=None,
        )
        result = exercise(
            context.amulet_rules,
            AmuletRules_Transfer(
                transfer=Transfer(
                    sender=self.beneficiary,
                    provider=self.delegate,
                    inputs=inputs,
                    outputs=[],
                    beneficiaries=None,
                ),
                context=transfer_context,
                expected_dso=self.dso,
            ),
        )
        return MintingDelegation_MintResult(transferResult=result)

    @DamlName("MintingDelegation_AssignAndMint")
    @choice(controller=delegate, consuming=False)
    def assign_and_mint(
        self,
        couponCid: ContractId[RewardCoupon],
        assignBeneficiaries: RewardCoupon_AssignBeneficiaries,
        inputs: list[TransferInput],
        context: PaymentTransferContext,
    ) -> MintingDelegation_AssignAndMintResult:
        assert_within_deadline("expiresAt", self.expiresAt)
        fetch_checked_interface(
            ForOwner(dso=self.dso, owner=self.beneficiary), couponCid
        )
        assign_result = exercise(couponCid, assignBeneficiaries)

        transfer_inputs: list[TransferInput] = inputs
        for entry: tuple[Party, list[ContractId[RewardCoupon]]] in assign_result.new_beneficiaries_coupon_cids:
            party = entry[0]
            coupon_cids = entry[1]
            if party == self.beneficiary:
                for coupon_cid: ContractId[RewardCoupon] in coupon_cids:
                    transfer_inputs.append(
                        InputRewardCouponV2(
                            from_interface_contract_id(coupon_cid)
                        )
                    )

        transfer_context = TransferContext(
            open_mining_round=context.context.open_mining_round,
            issuing_mining_rounds=context.context.issuing_mining_rounds,
            validator_rights=context.context.validator_rights,
            featured_app_right=None,
        )
        transfer_result = exercise(
            context.amulet_rules,
            AmuletRules_Transfer(
                transfer=Transfer(
                    sender=self.beneficiary,
                    provider=self.delegate,
                    inputs=transfer_inputs,
                    outputs=[],
                    beneficiaries=None,
                ),
                context=transfer_context,
                expected_dso=self.dso,
            ),
        )
        return MintingDelegation_AssignAndMintResult(
            assignResult=assign_result, transferResult=transfer_result
        )

    @DamlName("MintingDelegation_Reject")
    @choice(controller=delegate, consuming=True)
    def reject(self) -> MintingDelegation_RejectResult:
        return MintingDelegation_RejectResult()

    @DamlName("MintingDelegation_Withdraw")
    @choice(controller=beneficiary, consuming=True)
    def withdraw(self) -> MintingDelegation_WithdrawResult:
        return MintingDelegation_WithdrawResult()

    @checked_fetch
    def contract_group_id(self) -> ForOwner:
        return ForOwner(dso=self.dso, owner=self.beneficiary)
