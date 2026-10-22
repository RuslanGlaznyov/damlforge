from forge.models import ContractId, Party
from forge.builtins import DamlName
from Splice.Api.Token.MetadataV1 import Metadata
from Splice.Api.Token.TransferInstructionV2 import Transfer, TransferFactory, TransferFactory_Transfer, TransferInstruction, TransferInstructionResult, TransferInstruction_Accept, TransferInstruction_Reject, TransferInstruction_Withdraw
import Splice.Api.Token.TransferInstructionV1 as TransferInstructionV1


@DamlName("isValidTransferV2")
def is_valid_transfer_v2(transfer: Transfer) -> bool:
    pass


@DamlName("transferInstructionV2_receiverActor_acceptDefaultImplUsingV1", is_ledger_effect=True)
def transfer_instruction_v2_receiver_actor_accept_default_impl_using_v1(receiver: Party, self_: ContractId[TransferInstruction], arg: TransferInstruction_Accept) -> TransferInstructionResult:
    pass


@DamlName("transferInstructionV2_receiverActor_rejectDefaultImplUsingV1", is_ledger_effect=True)
def transfer_instruction_v2_receiver_actor_reject_default_impl_using_v1(receiver: Party, self_: ContractId[TransferInstruction], arg: TransferInstruction_Reject) -> TransferInstructionResult:
    pass


@DamlName("transferInstructionV2_senderActor_withdrawDefaultImplUsingV1", is_ledger_effect=True)
def transfer_instruction_v2_sender_actor_withdraw_default_impl_using_v1(sender: Party, self_: ContractId[TransferInstruction], arg: TransferInstruction_Withdraw) -> TransferInstructionResult:
    pass


@DamlName("transferFactoryV2_publicAsset_transferExtraObserversDefaultImpl")
def transfer_factory_v2_public_asset_transfer_extra_observers_default_impl(arg: TransferFactory_Transfer) -> list[Party]:
    pass


@DamlName("transferFactoryV2_privateAsset_transferExtraObserversDefaultImpl")
def transfer_factory_v2_private_asset_transfer_extra_observers_default_impl(arg: TransferFactory_Transfer) -> list[Party]:
    pass


@DamlName("transferInstructionV1_updateDefaultImplUsingV2", is_ledger_effect=True)
def transfer_instruction_v1_update_default_impl_using_v2(contract_id: ContractId[TransferInstructionV1.TransferInstruction], transfer_instruction_v1: TransferInstructionV1.TransferInstruction_Update) -> TransferInstructionV1.TransferInstructionResult:
    pass


@DamlName("transferFactoryV1_transferDefaultImplUsingV2", is_ledger_effect=True)
def transfer_factory_v1_transfer_default_impl_using_v2(this: TransferFactory, self_: ContractId[TransferInstructionV1.TransferFactory], arg: TransferInstructionV1.TransferFactory_Transfer) -> TransferInstructionV1.TransferInstructionResult:
    pass


@DamlName("transferAcceptanceTxHistoryV1ToMeta")
def transfer_acceptance_tx_history_v1_to_meta(transfer: Transfer, meta: Metadata) -> Metadata:
    pass
