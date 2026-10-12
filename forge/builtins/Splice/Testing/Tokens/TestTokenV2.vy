from datetime import datetime
from typing import Annotated

from forge.models import choice, ContractId, Decimal, ledger_effect, Optional, Party, template
from forge.builtins import DamlName
from Splice.Api.Token.AllocationInstructionV2 import AllocationFactory, AllocationFactory_Allocate, AllocationInstructionResult
from Splice.Api.Token.HoldingV2 import Account, InstrumentId
from Splice.Api.Token.MetadataV1 import ExtraArgs, Metadata
from Splice.Api.Token.TransferInstructionV2 import Transfer, TransferInstructionResult
from Splice.Testing.Tokens.TestTokenV2.AccountConfig import AccountConfig, AccountConfigMap, AccountProposal, AccountProposal_Accept_Result, AccountProposal_Reject_Result, AccountProposal_Withdraw_Result, AllocationInstructionState, AllocationState, AuthSpec, AuthState, AuthStateMachine, PartyConfig, TransferInstructionState, account_configs_context_key, allocation_instruction_state_machine_spec, allocation_state_machine_spec, authorization_transfer_from_state, authorization_transfers, extract_account_config_map, get_action_auth, get_missing_authorizers, get_needed_authorizers, get_next_actors, get_state, is_valid_account_config, mk_available_actions, store_account_config_for, to_auth_state_machine, transfer_instruction_state_machine_spec, try_advance_state
from Splice.Testing.Tokens.TestTokenV2.Allocation import AllocationKind, TokenAllocationInstructionV1, TokenAllocationInstructionV2, TokenAllocationV1, TokenAllocationV2, allocate_token_allocation, apply_allocation_instruction_transitions, apply_allocation_transitions, create_token_allocation, create_token_allocation_instruction, lock_allocation_funds, mk_available_allocation_actions, settle_token_allocation_v2, token_allocation_cancel_impl_v2, token_allocation_instruction_accept_impl_v2, token_allocation_instruction_withdraw_impl_v2, token_allocation_settle_impl_v2, token_allocation_withdraw_impl_v2, unlock_token_allocation_v2, valid_allocate_before
from Splice.Testing.Tokens.TestTokenV2.Holding import Token, fetch_and_archive_locked_token, fetch_and_archive_unlocked_token
from Splice.Testing.Tokens.TestTokenV2.Transfer import TokenTransferOffer, apply_transfer_instruction_transitions, create_locked_inputs, sender_holding_from_transfer, token_transfer_instruction_accept_impl_v2, token_transfer_instruction_reject_impl_v2, token_transfer_instruction_withdraw_impl_v2, transfer_instruction_transition, unlock_token_transfer_offer
from Splice.Testing.Tokens.TestTokenV2.Util import CallSource


struct TokenRules_OfferMintResult:
    offer_cid: Annotated[ContractId[TokenTransferOffer], DamlName("offerCid")]
    meta: Metadata


@template
class TokenRules:
    admin: Party

    signatory: list[Party] = [admin]

    @choice(controller=admin, consuming="nonconsuming")
    def TokenRules_OfferMint(self, receiver: Account, amount: Decimal, instrument_id: Annotated[InstrumentId, DamlName("instrumentId")], offered_at: Annotated[datetime, DamlName("offeredAt")], receiver_config: Annotated[AccountConfig, DamlName("receiverConfig")]) -> TokenRules_OfferMintResult:
        pass


@ledger_effect
@DamlName("token_transferFactory_transferImpl")
def token_transfer_factory_transfer_impl(admin: Party, actors: list[Party], transfer: Transfer, extra_args: ExtraArgs) -> TransferInstructionResult:
    pass


@ledger_effect
@DamlName("token_allocationFactoryV2_allocateImpl")
def token_allocation_factory_v2_allocate_impl(call_source: CallSource, allocation_kind: AllocationKind, token_rules: TokenRules, allocate_before: Optional[datetime], contract_id: ContractId[AllocationFactory], arg: AllocationFactory_Allocate) -> AllocationInstructionResult:
    pass
