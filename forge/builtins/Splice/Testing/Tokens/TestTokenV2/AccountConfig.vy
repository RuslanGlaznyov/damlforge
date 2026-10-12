from typing import Annotated, Generic, TypeVar

from forge.models import choice, ContractId, GenMap, ledger_effect, Optional, Party, template, variant
from forge.builtins import DamlCaseAccessor, DamlName, no_derive
from Splice.Api.Token.AllocationInstructionV2 import AllocationInstruction, AllocationInstructionAction, AllocationInstructionResult
from Splice.Api.Token.AllocationV2 import Allocation, AllocationAction, AllocationResult
from Splice.Api.Token.HoldingV2 import Account
from Splice.Api.Token.MetadataV1 import ChoiceContext, ExtraArgs
from Splice.Api.Token.TransferInstructionV2 import TransferInstruction, TransferInstructionAction, TransferInstructionResult

ActionType = TypeVar("ActionType")
StateType = TypeVar("StateType")


AccountConfigMap = GenMap[Account, tuple[AccountConfig, Optional[ContractId[AccountConfig]]]]


AuthState = GenMap[ActionType, list[Party]]


AuthStateMachine = GenMap[StateType, GenMap[ActionType, tuple[StateType, AuthSpec[ActionType]]]]


@no_derive
@variant
class AuthSpec(Generic[ActionType]):
    def STAS_Account(value: Account): pass
    def STAS_Action(value: ActionType): pass
    def STAS_Parties(value: list[Party]): pass


@variant
class AllocationState:
    def AS_Init(): pass
    def AS_Withdrawn(): pass
    def AS_Cancelled(): pass
    def AS_Settled(): pass


@variant
class AllocationInstructionState:
    def AIS_Init(): pass
    def AIS_Withdrawn(): pass
    def AIS_Accepted(): pass


@variant
class TransferInstructionState:
    def TIS_Init(): pass
    def TIS_Authorized(): pass
    def TIS_Withdrawn(): pass
    def TIS_Rejected(): pass
    def TIS_Accepted(): pass


struct PartyConfig:
    can_initiate: Annotated[bool, DamlName("canInitiate")]
    must_approve: Annotated[bool, DamlName("mustApprove")]


struct AccountProposal_Accept_Result:
    account_config: Annotated[ContractId[AccountConfig], DamlName("accountConfig")]


struct AccountProposal_Reject_Result:
    pass


struct AccountProposal_Withdraw_Result:
    pass


@template
class AccountConfig:
    admin: Party
    account: Account
    owner_config: Annotated[PartyConfig, DamlName("ownerConfig")]
    provider_config: Annotated[PartyConfig, DamlName("providerConfig")]

    signatory: list[Party] = [admin]
    observer: list[Party] = [admin]

    @choice(controller=[admin, actor], consuming="nonconsuming")
    def AuthorizeAllocationAction(self, actor: Party, authorizer: Party, action: AllocationAction, allocation_cid: Annotated[ContractId[Allocation], DamlName("allocationCid")], extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]) -> AllocationResult:
        pass

    @choice(controller=[admin, actor], consuming="nonconsuming")
    def AuthorizeAllocationInstructionAction(self, actor: Party, authorizer: Party, action: AllocationInstructionAction, instr_cid: Annotated[ContractId[AllocationInstruction], DamlName("instrCid")], extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]) -> AllocationInstructionResult:
        pass

    @choice(controller=[admin, actor], consuming="nonconsuming")
    def AuthorizeTransferInstructionAction(self, actor: Party, authorizer: Party, action: TransferInstructionAction, instr_cid: Annotated[ContractId[TransferInstruction], DamlName("instrCid")], extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]) -> TransferInstructionResult:
        pass


@template
class AccountProposal:
    config: AccountConfig

    signatory: list[Party] = []

    @choice(controller=[], consuming=True)
    def AccountProposal_Accept(self) -> AccountProposal_Accept_Result:
        pass

    @choice(controller=[], consuming=True)
    def AccountProposal_Reject(self) -> AccountProposal_Reject_Result:
        pass

    @choice(controller=[], consuming=True)
    def AccountProposal_Withdraw(self) -> AccountProposal_Withdraw_Result:
        pass


@DamlCaseAccessor("STAS_Account")
def stas_account(value: AuthSpec[ActionType]) -> Optional[Account]:
    pass


@DamlCaseAccessor("STAS_Action")
def stas_action(value: AuthSpec[ActionType]) -> Optional[ActionType]:
    pass


@DamlCaseAccessor("STAS_Parties")
def stas_parties(value: AuthSpec[ActionType]) -> Optional[list[Party]]:
    pass


@DamlName("isValidAccountConfig")
def is_valid_account_config(config: AccountConfig) -> bool:
    pass


@DamlName("transferInstructionStateMachineSpec")
def transfer_instruction_state_machine_spec(sender: Account, receiver: Account) -> GenMap[TransferInstructionState, GenMap[TransferInstructionAction, tuple[TransferInstructionState, AuthSpec[TransferInstructionAction]]]]:
    pass


@DamlName("allocationInstructionStateMachineSpec")
def allocation_instruction_state_machine_spec(authorizer: Account) -> GenMap[AllocationInstructionState, GenMap[AllocationInstructionAction, tuple[AllocationInstructionState, AuthSpec[AllocationInstructionAction]]]]:
    pass


@DamlName("allocationStateMachineSpec")
def allocation_state_machine_spec(authorizer: Account, executors: list[Party], admin: Party) -> GenMap[AllocationState, GenMap[AllocationAction, tuple[AllocationState, AuthSpec[AllocationAction]]]]:
    pass


@DamlName("authorizationTransfers")
def authorization_transfers(config: AccountConfig) -> list[tuple[Party, Party]]:
    pass


@DamlName("authorizationTransferFromState")
def authorization_transfer_from_state(party: Party, list_value: list[Party], action_type: ActionType, state_type: StateType, gen_map: GenMap[StateType, GenMap[ActionType, tuple[StateType, AuthSpec[ActionType]]]], gen_map_5: GenMap[ActionType, list[Party]], gen_map_6: GenMap[Account, tuple[AccountConfig, Optional[ContractId[AccountConfig]]]]) -> Optional[tuple[Party, Party, ContractId[AccountConfig]]]:
    pass


@DamlName("toAuthStateMachine")
def to_auth_state_machine(list_value: list[tuple[StateType, ActionType, StateType, AuthSpec[ActionType]]]) -> GenMap[StateType, GenMap[ActionType, tuple[StateType, AuthSpec[ActionType]]]]:
    pass


@DamlName("getActionAuth")
def get_action_auth(action: ActionType, auth_state: GenMap[ActionType, list[Party]]) -> list[Party]:
    pass


@DamlName("getNeededAuthorizers")
def get_needed_authorizers(admin: Party, transition_auth: AuthSpec[ActionType], auth_state: GenMap[ActionType, list[Party]]) -> list[Party]:
    pass


@DamlName("getMissingAuthorizers")
def get_missing_authorizers(admin: Party, action: ActionType, transition_auth: AuthSpec[ActionType], auth_state: GenMap[ActionType, list[Party]]) -> list[Party]:
    pass


@DamlName("getNextActors")
def get_next_actors(admin: Party, action: ActionType, auth_spec: AuthSpec[ActionType], auth_state: GenMap[ActionType, list[Party]], account_map: GenMap[Account, tuple[AccountConfig, Optional[ContractId[AccountConfig]]]]) -> list[list[Party]]:
    pass


@DamlName("getState")
def get_state(admin: Party, spec: GenMap[StateType, GenMap[ActionType, tuple[StateType, AuthSpec[ActionType]]]], auth_state: GenMap[ActionType, list[Party]]) -> StateType:
    pass


@DamlName("tryAdvanceState")
def try_advance_state(admin: Party, spec: GenMap[StateType, GenMap[ActionType, tuple[StateType, AuthSpec[ActionType]]]], auth_state: GenMap[ActionType, list[Party]], from_state: StateType) -> StateType:
    pass


@DamlName("mkAvailableActions")
def mk_available_actions(admin: Party, spec: GenMap[StateType, GenMap[ActionType, tuple[StateType, AuthSpec[ActionType]]]], auth_state: GenMap[ActionType, list[Party]], account_map: GenMap[Account, tuple[AccountConfig, Optional[ContractId[AccountConfig]]]]) -> GenMap[ActionType, list[list[Party]]]:
    pass


@DamlName("storeAccountConfigFor")
def store_account_config_for(account: Account, account_map: GenMap[Account, tuple[AccountConfig, Optional[ContractId[AccountConfig]]]], context: ChoiceContext) -> ChoiceContext:
    pass


@ledger_effect
@DamlName("extractAccountConfigMap")
def extract_account_config_map(admin: Party, extra_args: ExtraArgs, as_: list[Account]) -> GenMap[Account, tuple[AccountConfig, Optional[ContractId[AccountConfig]]]]:
    pass


@DamlName("accountConfigsContextKey")
def account_configs_context_key() -> str:
    pass
