from datetime import datetime
from typing import Annotated

from forge.models import choice, ContractId, Decimal, ledger_effect, Optional, Party, template, variant, variant_record
from forge.builtins import DamlCaseAccessor, DamlName
from Splice.Amulet import LockedAmulet
from Splice.AmuletAllocation import AmuletAllocation, AmuletAllocation_DsoExpireResult
from Splice.AmuletRules import InvalidTransferReason, PaymentTransferContext, TransferInput, TransferPreapproval, TransferResult
from Splice.Api.Token.AllocationInstructionV2 import AllocationFactory, AllocationFactory_Allocate, AllocationInstructionResult
from Splice.Api.Token.AllocationV2 import Allocation, Allocation_Cancel
from Splice.Api.Token.HoldingV1 import Holding
from Splice.Api.Token.MetadataV1 import Metadata
from Splice.Api.Token.TransferInstructionV1 import TransferFactory_Transfer, TransferInstructionResult
import Splice.Api.Token.AllocationInstructionV1 as AllocationInstructionV1


@variant
class TransferCommandResult:
    @variant_record
    def TransferCommandResultFailure(reason: InvalidTransferReason): pass
    @variant_record
    def TransferCommandResultSuccess(result: TransferResult): pass


struct ExternalPartyAmuletRules_ExpireAmuletAllocationInput:
    allocation_cid: Annotated[ContractId[AmuletAllocation], DamlName("allocationCid")]
    expire_lock: Annotated[bool, DamlName("expireLock")]


struct ExternalPartyAmuletRules_ExpireAmuletAllocationsResult:
    results: list[AmuletAllocation_DsoExpireResult]


struct ExternalPartyAmuletRules_ExpireAmuletAllocationsV2Result:
    pass


struct ExternalPartyAmuletRules_CreateTransferCommandResult:
    transfer_command_cid: Annotated[ContractId[TransferCommand], DamlName("transferCommandCid")]


struct TransferCommand_SendResult:
    result: TransferCommandResult
    sender: Party
    nonce: int


struct TransferCommand_WithdrawResult:
    sender: Party
    nonce: int


struct TransferCommand_ExpireResult:
    sender: Party
    nonce: int


@template
class ExternalPartyAmuletRules:
    dso: Party

    signatory: list[Party] = [dso]

    @choice(controller=dso, consuming="nonconsuming", observer=observers)
    def ExternalPartyAmuletRules_ExpireAmuletAllocations(self, expected_dso: Annotated[Party, DamlName("expectedDso")], inputs: list[ExternalPartyAmuletRules_ExpireAmuletAllocationInput], observers: list[Party]) -> ExternalPartyAmuletRules_ExpireAmuletAllocationsResult:
        pass

    @choice(controller=dso, consuming="nonconsuming", observer=observers)
    def ExternalPartyAmuletRules_ExpireAmuletAllocationsV2(self, cancellations: list[tuple[ContractId[Allocation], Allocation_Cancel]], observers: list[Party]) -> ExternalPartyAmuletRules_ExpireAmuletAllocationsV2Result:
        pass

    @choice(controller=sender, consuming="nonconsuming")
    def ExternalPartyAmuletRules_CreateTransferCommand(self, sender: Party, receiver: Party, delegate: Party, amount: Decimal, expires_at: Annotated[datetime, DamlName("expiresAt")], nonce: int, description: Optional[str], expected_dso: Annotated[Optional[Party], DamlName("expectedDso")]) -> ExternalPartyAmuletRules_CreateTransferCommandResult:
        pass


@template
class TransferCommandCounter:
    dso: Party
    sender: Party
    next_nonce: Annotated[int, DamlName("nextNonce")]

    signatory: list[Party] = [dso]
    observer: list[Party] = [sender]


@template
class TransferCommand:
    dso: Party
    sender: Party
    receiver: Party
    delegate: Party
    amount: Decimal
    expires_at: Annotated[datetime, DamlName("expiresAt")]
    nonce: int
    description: Optional[str]

    signatory: list[Party] = [dso, sender]
    observer: list[Party] = [delegate]

    @choice(controller=p, consuming=True)
    def TransferCommand_Expire(self, p: Party) -> TransferCommand_ExpireResult:
        pass

    @choice(controller=delegate, consuming=True)
    def TransferCommand_Send(self, context: PaymentTransferContext, inputs: list[TransferInput], transfer_preapproval_cid_o: Annotated[Optional[ContractId[TransferPreapproval]], DamlName("transferPreapprovalCidO")], transfer_counter_cid: Annotated[ContractId[TransferCommandCounter], DamlName("transferCounterCid")]) -> TransferCommand_SendResult:
        pass

    @choice(controller=sender, consuming=True)
    def TransferCommand_Withdraw(self) -> TransferCommand_WithdrawResult:
        pass


@DamlCaseAccessor("TransferCommandResultFailure")
def transfer_command_result_failure(value: TransferCommandResult) -> Optional[InvalidTransferReason]:
    pass


@DamlCaseAccessor("TransferCommandResultSuccess")
def transfer_command_result_success(value: TransferCommandResult) -> Optional[TransferResult]:
    pass


@ledger_effect
@DamlName("amulet_transferFactoryV1_transferImpl")
def amulet_transfer_factory_v1_transfer_impl(this: ExternalPartyAmuletRules, actors: list[Party], arg: TransferFactory_Transfer) -> TransferInstructionResult:
    pass


@ledger_effect
@DamlName("amulet_allocationFactoryV2_allocateImpl")
def amulet_allocation_factory_v2_allocate_impl(external_amulet_rules: ExternalPartyAmuletRules, contract_id: ContractId[AllocationFactory], arg: AllocationFactory_Allocate) -> AllocationInstructionResult:
    pass


@ledger_effect
@DamlName("amulet_allocationFactoryV2_allocateImplCore")
def amulet_allocation_factory_v2_allocate_impl_core(external_amulet_rules: ExternalPartyAmuletRules, arg: AllocationFactory_Allocate, funding_amount: Decimal) -> tuple[Optional[ContractId[LockedAmulet]], list[ContractId[Holding]], datetime, Metadata]:
    pass


@ledger_effect
@DamlName("amulet_allocationFactoryV1_allocateImpl")
def amulet_allocation_factory_v1_allocate_impl(external_amulet_rules: ExternalPartyAmuletRules, contract_id: ContractId[AllocationInstructionV1.AllocationFactory], arg: AllocationInstructionV1.AllocationFactory_Allocate) -> AllocationInstructionV1.AllocationInstructionResult:
    pass


@ledger_effect
@DamlName("requireExpectedAdminMatch")
def require_expected_admin_match(expected: Party, actual: Party) -> None:
    pass
