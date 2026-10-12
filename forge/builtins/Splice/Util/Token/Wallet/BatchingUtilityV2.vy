from typing import Annotated, Generic, TypeVar

from forge.models import choice, ContractId, GenMap, ledger_effect, Optional, Party, template, TextMap, variant
from forge.builtins import DamlCaseAccessor, DamlName
from Splice.Api.Token.AllocationInstructionV1 import AllocationFactory_Allocate, AllocationInstructionResult, AllocationInstruction_Withdraw
from Splice.Api.Token.AllocationRequestV2 import AllocationRequest_Accept, AllocationRequest_AcceptResult, AllocationRequest_Reject, AllocationRequest_RejectResult
from Splice.Api.Token.AllocationV1 import Allocation_Withdraw, Allocation_WithdrawResult, TransferLeg
from Splice.Api.Token.HoldingV2 import Account, Holding, InstrumentId
from Splice.Api.Token.MetadataV1 import AnyContract
from Splice.Api.Token.TransferInstructionV1 import Transfer, TransferFactory_Transfer, TransferInstructionResult, TransferInstruction_Accept, TransferInstruction_Reject, TransferInstruction_Withdraw
import Splice.Api.Token.AllocationInstructionV2 as AllocationInstructionV2
import Splice.Api.Token.AllocationV2 as AllocationV2
import Splice.Api.Token.HoldingV1 as HoldingV1
import Splice.Api.Token.TransferInstructionV2 as TransferInstructionV2

Arg = TypeVar("Arg")
Ch = TypeVar("Ch")


@variant
class TokenStandardActionResult:
    def TSAR_AllocationInstructionResultV1(value: AllocationInstructionResult): pass
    def TSAR_TransferInstructionResultV1(value: TransferInstructionResult): pass
    def TSAR_AllocationWithdrawResultV1(value: Allocation_WithdrawResult): pass
    def TSAR_TransferInstructionResultV2(value: TransferInstructionV2.TransferInstructionResult): pass
    def TSAR_AllocationInstructionResultV2(value: AllocationInstructionV2.AllocationInstructionResult): pass
    def TSAR_AllocationResultV2(value: AllocationV2.AllocationResult): pass
    def TSAR_AllocationRequest_AcceptV2Result(value: AllocationRequest_AcceptResult): pass
    def TSAR_AllocationRequest_RejectV2Result(value: AllocationRequest_RejectResult): pass


@variant
class TokenStandardAction:
    def TSA_TransferFactory_TransferV1(value: ChoiceCall[TransferFactory_Transfer]): pass
    def TSA_TransferInstruction_AcceptV1(value: ChoiceCall[TransferInstruction_Accept]): pass
    def TSA_TransferInstruction_RejectV1(value: ChoiceCall[TransferInstruction_Reject]): pass
    def TSA_TransferInstruction_WithdrawV1(value: ChoiceCall[TransferInstruction_Withdraw]): pass
    def TSA_TransferFactory_TransferV2(value: ChoiceCall[TransferInstructionV2.TransferFactory_Transfer]): pass
    def TSA_TransferInstruction_AcceptV2(value: ChoiceCall[TransferInstructionV2.TransferInstruction_Accept]): pass
    def TSA_TransferInstruction_RejectV2(value: ChoiceCall[TransferInstructionV2.TransferInstruction_Reject]): pass
    def TSA_TransferInstruction_WithdrawV2(value: ChoiceCall[TransferInstructionV2.TransferInstruction_Withdraw]): pass
    def TSA_AllocationFactory_AllocateV1(value: ChoiceCall[AllocationFactory_Allocate]): pass
    def TSA_AllocationInstruction_WithdrawV1(value: ChoiceCall[AllocationInstruction_Withdraw]): pass
    def TSA_Allocation_WithdrawV1(value: ChoiceCall[Allocation_Withdraw]): pass
    def TSA_AllocationFactory_AllocateV2(value: ChoiceCall[AllocationInstructionV2.AllocationFactory_Allocate]): pass
    def TSA_AllocationInstruction_AcceptV2(value: ChoiceCall[AllocationInstructionV2.AllocationInstruction_Accept]): pass
    def TSA_AllocationInstruction_WithdrawV2(value: ChoiceCall[AllocationInstructionV2.AllocationInstruction_Withdraw]): pass
    def TSA_Allocation_WithdrawV2(value: ChoiceCall[AllocationV2.Allocation_Withdraw]): pass
    def TSA_AllocationRequest_AcceptV2(value: ChoiceCall[AllocationRequest_Accept]): pass
    def TSA_AllocationRequest_RejectV2(value: ChoiceCall[AllocationRequest_Reject]): pass


struct ScopedAccount:
    admin: Party
    account: Account


struct HoldingMap:
    by_admin_and_account: Annotated[GenMap[ScopedAccount, TextMap[list[ContractId[Holding]]]], DamlName("byAdminAndAccount")]


struct ChoiceCall(Generic[Arg]):
    cid: ContractId[AnyContract]
    arg: Arg


struct BatchingUtility_ExecuteBatchResult:
    action_results: Annotated[list[TokenStandardActionResult], DamlName("actionResults")]
    output_holding_map: Annotated[HoldingMap, DamlName("outputHoldingMap")]


@template
class BatchingUtility:
    user: Party

    signatory: list[Party] = [user]

    @choice(controller=user, consuming="nonconsuming")
    def BatchingUtility_ExecuteBatch(self, input_holding_map: Annotated[HoldingMap, DamlName("inputHoldingMap")], actions: list[TokenStandardAction], archive_after_execution: Annotated[bool, DamlName("archiveAfterExecution")]) -> BatchingUtility_ExecuteBatchResult:
        pass


@DamlCaseAccessor("TSAR_AllocationInstructionResultV1")
def tsar_allocation_instruction_result_v1(value: TokenStandardActionResult) -> Optional[AllocationInstructionResult]:
    pass


@DamlCaseAccessor("TSAR_TransferInstructionResultV1")
def tsar_transfer_instruction_result_v1(value: TokenStandardActionResult) -> Optional[TransferInstructionResult]:
    pass


@DamlCaseAccessor("TSAR_AllocationWithdrawResultV1")
def tsar_allocation_withdraw_result_v1(value: TokenStandardActionResult) -> Optional[Allocation_WithdrawResult]:
    pass


@DamlCaseAccessor("TSAR_TransferInstructionResultV2")
def tsar_transfer_instruction_result_v2(value: TokenStandardActionResult) -> Optional[TransferInstructionV2.TransferInstructionResult]:
    pass


@DamlCaseAccessor("TSAR_AllocationInstructionResultV2")
def tsar_allocation_instruction_result_v2(value: TokenStandardActionResult) -> Optional[AllocationInstructionV2.AllocationInstructionResult]:
    pass


@DamlCaseAccessor("TSAR_AllocationResultV2")
def tsar_allocation_result_v2(value: TokenStandardActionResult) -> Optional[AllocationV2.AllocationResult]:
    pass


@DamlCaseAccessor("TSAR_AllocationRequest_AcceptV2Result")
def tsar_allocation_request_accept_v2_result(value: TokenStandardActionResult) -> Optional[AllocationRequest_AcceptResult]:
    pass


@DamlCaseAccessor("TSAR_AllocationRequest_RejectV2Result")
def tsar_allocation_request_reject_v2_result(value: TokenStandardActionResult) -> Optional[AllocationRequest_RejectResult]:
    pass


@DamlCaseAccessor("TSA_TransferFactory_TransferV1")
def tsa_transfer_factory_transfer_v1(value: TokenStandardAction) -> Optional[ChoiceCall[TransferFactory_Transfer]]:
    pass


@DamlCaseAccessor("TSA_TransferInstruction_AcceptV1")
def tsa_transfer_instruction_accept_v1(value: TokenStandardAction) -> Optional[ChoiceCall[TransferInstruction_Accept]]:
    pass


@DamlCaseAccessor("TSA_TransferInstruction_RejectV1")
def tsa_transfer_instruction_reject_v1(value: TokenStandardAction) -> Optional[ChoiceCall[TransferInstruction_Reject]]:
    pass


@DamlCaseAccessor("TSA_TransferInstruction_WithdrawV1")
def tsa_transfer_instruction_withdraw_v1(value: TokenStandardAction) -> Optional[ChoiceCall[TransferInstruction_Withdraw]]:
    pass


@DamlCaseAccessor("TSA_TransferFactory_TransferV2")
def tsa_transfer_factory_transfer_v2(value: TokenStandardAction) -> Optional[ChoiceCall[TransferInstructionV2.TransferFactory_Transfer]]:
    pass


@DamlCaseAccessor("TSA_TransferInstruction_AcceptV2")
def tsa_transfer_instruction_accept_v2(value: TokenStandardAction) -> Optional[ChoiceCall[TransferInstructionV2.TransferInstruction_Accept]]:
    pass


@DamlCaseAccessor("TSA_TransferInstruction_RejectV2")
def tsa_transfer_instruction_reject_v2(value: TokenStandardAction) -> Optional[ChoiceCall[TransferInstructionV2.TransferInstruction_Reject]]:
    pass


@DamlCaseAccessor("TSA_TransferInstruction_WithdrawV2")
def tsa_transfer_instruction_withdraw_v2(value: TokenStandardAction) -> Optional[ChoiceCall[TransferInstructionV2.TransferInstruction_Withdraw]]:
    pass


@DamlCaseAccessor("TSA_AllocationFactory_AllocateV1")
def tsa_allocation_factory_allocate_v1(value: TokenStandardAction) -> Optional[ChoiceCall[AllocationFactory_Allocate]]:
    pass


@DamlCaseAccessor("TSA_AllocationInstruction_WithdrawV1")
def tsa_allocation_instruction_withdraw_v1(value: TokenStandardAction) -> Optional[ChoiceCall[AllocationInstruction_Withdraw]]:
    pass


@DamlCaseAccessor("TSA_Allocation_WithdrawV1")
def tsa_allocation_withdraw_v1(value: TokenStandardAction) -> Optional[ChoiceCall[Allocation_Withdraw]]:
    pass


@DamlCaseAccessor("TSA_AllocationFactory_AllocateV2")
def tsa_allocation_factory_allocate_v2(value: TokenStandardAction) -> Optional[ChoiceCall[AllocationInstructionV2.AllocationFactory_Allocate]]:
    pass


@DamlCaseAccessor("TSA_AllocationInstruction_AcceptV2")
def tsa_allocation_instruction_accept_v2(value: TokenStandardAction) -> Optional[ChoiceCall[AllocationInstructionV2.AllocationInstruction_Accept]]:
    pass


@DamlCaseAccessor("TSA_AllocationInstruction_WithdrawV2")
def tsa_allocation_instruction_withdraw_v2(value: TokenStandardAction) -> Optional[ChoiceCall[AllocationInstructionV2.AllocationInstruction_Withdraw]]:
    pass


@DamlCaseAccessor("TSA_Allocation_WithdrawV2")
def tsa_allocation_withdraw_v2(value: TokenStandardAction) -> Optional[ChoiceCall[AllocationV2.Allocation_Withdraw]]:
    pass


@DamlCaseAccessor("TSA_AllocationRequest_AcceptV2")
def tsa_allocation_request_accept_v2(value: TokenStandardAction) -> Optional[ChoiceCall[AllocationRequest_Accept]]:
    pass


@DamlCaseAccessor("TSA_AllocationRequest_RejectV2")
def tsa_allocation_request_reject_v2(value: TokenStandardAction) -> Optional[ChoiceCall[AllocationRequest_Reject]]:
    pass


@DamlName("holdingMapFromList")
def holding_map_from_list(entries: list[tuple[ScopedAccount, TextMap[list[ContractId[Holding]]]]]) -> HoldingMap:
    pass


@DamlName("holdingMapMerge")
def holding_map_merge(holding_map: HoldingMap, holding_map_1: HoldingMap) -> HoldingMap:
    pass


@DamlName("getHoldingsFor")
def get_holdings_for(k: ScopedAccount, holding_map: HoldingMap) -> tuple[list[ContractId[Holding]], HoldingMap]:
    pass


@DamlName("getHoldingsForInstrument")
def get_holdings_for_instrument(account: Account, instrument_id: InstrumentId, holding_map: HoldingMap) -> tuple[list[ContractId[Holding]], HoldingMap]:
    pass


@ledger_effect
@DamlName("executeTokenStandardAction")
def execute_token_standard_action(actor: Party, acc: tuple[HoldingMap, list[TokenStandardActionResult]], action: TokenStandardAction) -> tuple[HoldingMap, list[TokenStandardActionResult]]:
    pass


@DamlName("holdingMapForV1")
def holding_map_for_v1(actor: Party, instrument_id: HoldingV1.InstrumentId, cids: list[ContractId[HoldingV1.Holding]]) -> HoldingMap:
    pass


@DamlName("holdingMapFromTransferV1")
def holding_map_from_transfer_v1(transfer: Transfer, result: TransferInstructionResult) -> HoldingMap:
    pass


@DamlName("holdingMapFromTransferLegV1")
def holding_map_from_transfer_leg_v1(transfer_leg: TransferLeg, sender_holding_cids: list[ContractId[HoldingV1.Holding]]) -> HoldingMap:
    pass


@DamlName("holdingMapFromTransferV2")
def holding_map_from_transfer_v2(transfer: TransferInstructionV2.Transfer, result: TransferInstructionV2.TransferInstructionResult) -> HoldingMap:
    pass


@DamlName("holdingMapFromAllocationV2")
def holding_map_from_allocation_v2(allocation: AllocationV2.AllocationSpecification, result: AllocationV2.AllocationResult) -> HoldingMap:
    pass


@DamlName("holdingMapFromAllocationInstructionV2")
def holding_map_from_allocation_instruction_v2(allocation: AllocationV2.AllocationSpecification, result: AllocationInstructionV2.AllocationInstructionResult) -> HoldingMap:
    pass


@ledger_effect
@DamlName("transferInstructionCallV1")
def transfer_instruction_call_v1(call: ChoiceCall[Ch], acc: tuple[HoldingMap, list[TokenStandardActionResult]]) -> tuple[HoldingMap, list[TokenStandardActionResult]]:
    pass


@ledger_effect
@DamlName("transferInstructionCallV2")
def transfer_instruction_call_v2(call: ChoiceCall[Ch], acc: tuple[HoldingMap, list[TokenStandardActionResult]]) -> tuple[HoldingMap, list[TokenStandardActionResult]]:
    pass
