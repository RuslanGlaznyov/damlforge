from typing import Annotated, Generic, TypeVar

from forge.models import choice, ContractId, Decimal, GenMap, ledger_effect, Optional, Party, template
from forge.builtins import DamlName, no_derive
from Splice.Api.FeaturedAppRightV1 import AppRewardBeneficiary, FeaturedAppRight, FeaturedAppRight_CreateActivityMarkerResult
from Splice.Api.Token.AllocationInstructionV1 import AllocationFactory, AllocationFactory_Allocate, AllocationInstructionResult
from Splice.Api.Token.AllocationV1 import Allocation, Allocation_Withdraw, Allocation_WithdrawResult
from Splice.Api.Token.HoldingV1 import Holding, InstrumentId
from Splice.Api.Token.TransferInstructionV1 import TransferFactory, TransferFactory_Transfer, TransferInstruction, TransferInstructionResult, TransferInstruction_Accept, TransferInstruction_Reject, TransferInstruction_Withdraw

Arg = TypeVar("Arg")
Ch = TypeVar("Ch")
R = TypeVar("R")
T = TypeVar("T")


InstrumentHoldingMap = GenMap[InstrumentId, list[ContractId[Holding]]]


struct ProxyArg(Generic[Arg]):
    user: Party
    choice_arg: Annotated[Arg, DamlName("choiceArg")]
    featured_app_right_cid: Annotated[ContractId[FeaturedAppRight], DamlName("featuredAppRightCid")]


@no_derive
struct ProxyResult(Generic[R]):
    marker_result: Annotated[FeaturedAppRight_CreateActivityMarkerResult, DamlName("markerResult")]
    choice_result: Annotated[R, DamlName("choiceResult")]


struct TransferFactoryCall:
    factory_cid: Annotated[ContractId[TransferFactory], DamlName("factoryCid")]
    choice_arg: Annotated[TransferFactory_Transfer, DamlName("choiceArg")]


struct WalletUserProxy_BatchTransferResult:
    transfer_results: Annotated[list[TransferInstructionResult], DamlName("transferResults")]
    sender_change_map: Annotated[GenMap[InstrumentId, list[ContractId[Holding]]], DamlName("senderChangeMap")]


@template
class WalletUserProxy:
    provider: Party
    provider_weight: Annotated[Decimal, DamlName("providerWeight")]
    user_weight: Annotated[Decimal, DamlName("userWeight")]
    extra_beneficiaries: Annotated[list[AppRewardBeneficiary], DamlName("extraBeneficiaries")]
    opt_allow_list: Annotated[Optional[list[Party]], DamlName("optAllowList")]

    signatory: list[Party] = [provider]

    @choice(controller=[provider], consuming="nonconsuming")
    def WalletUserProxy_BatchTransfer(self, transfer_calls: Annotated[list[TransferFactoryCall], DamlName("transferCalls")], opt_featured_app_right_cid: Annotated[Optional[ContractId[FeaturedAppRight]], DamlName("optFeaturedAppRightCid")]) -> WalletUserProxy_BatchTransferResult:
        pass

    @choice(controller=proxy_arg.user, consuming="nonconsuming")
    def WalletUserProxy_TransferFactory_Transfer(self, cid: ContractId[TransferFactory], proxy_arg: Annotated[ProxyArg[TransferFactory_Transfer], DamlName("proxyArg")]) -> ProxyResult[TransferInstructionResult]:
        pass

    @choice(controller=proxy_arg.user, consuming="nonconsuming")
    def WalletUserProxy_TransferInstruction_Accept(self, cid: ContractId[TransferInstruction], proxy_arg: Annotated[ProxyArg[TransferInstruction_Accept], DamlName("proxyArg")]) -> ProxyResult[TransferInstructionResult]:
        pass

    @choice(controller=proxy_arg.user, consuming="nonconsuming")
    def WalletUserProxy_TransferInstruction_Reject(self, cid: ContractId[TransferInstruction], proxy_arg: Annotated[ProxyArg[TransferInstruction_Reject], DamlName("proxyArg")]) -> ProxyResult[TransferInstructionResult]:
        pass

    @choice(controller=proxy_arg.user, consuming="nonconsuming")
    def WalletUserProxy_TransferInstruction_Withdraw(self, cid: ContractId[TransferInstruction], proxy_arg: Annotated[ProxyArg[TransferInstruction_Withdraw], DamlName("proxyArg")]) -> ProxyResult[TransferInstructionResult]:
        pass

    @choice(controller=proxy_arg.user, consuming="nonconsuming")
    def WalletUserProxy_AllocationFactory_Allocate(self, cid: ContractId[AllocationFactory], proxy_arg: Annotated[ProxyArg[AllocationFactory_Allocate], DamlName("proxyArg")]) -> ProxyResult[AllocationInstructionResult]:
        pass

    @choice(controller=proxy_arg.user, consuming="nonconsuming")
    def WalletUserProxy_Allocation_Withdraw(self, cid: ContractId[Allocation], proxy_arg: Annotated[ProxyArg[Allocation_Withdraw], DamlName("proxyArg")]) -> ProxyResult[Allocation_WithdrawResult]:
        pass

    @choice(controller=actor, consuming="nonconsuming")
    def WalletUserProxy_PublicFetch(self, actor: Party) -> WalletUserProxy:
        pass


@DamlName("getFirstSender")
def get_first_sender(list_value: list[TransferFactoryCall]) -> Party:
    pass


@ledger_effect
@DamlName("runBatch")
def run_batch(proxy: WalletUserProxy, wallet_user_proxy_batch_transfer: WalletUserProxy_BatchTransfer) -> WalletUserProxy_BatchTransferResult:
    pass


@ledger_effect
@DamlName("executeTransferCalls")
def execute_transfer_calls(wallet_user_proxy: WalletUserProxy, party: Party, optional: Optional[ContractId[FeaturedAppRight]], list_value: list[TransferFactoryCall], holding_map: GenMap[InstrumentId, list[ContractId[Holding]]], results: list[TransferInstructionResult]) -> WalletUserProxy_BatchTransferResult:
    pass


@ledger_effect
@DamlName("validateAppRight")
def validate_app_right(proxy: WalletUserProxy, featured_app_right_cid: ContractId[FeaturedAppRight]) -> None:
    pass


@ledger_effect
@DamlName("checkAllowList")
def check_allow_list(optional: Optional[list[Party]], party: Party) -> None:
    pass


@ledger_effect
@DamlName("createAppMarker")
def create_app_marker(proxy: WalletUserProxy, user: Party, featured_app_right_cid: ContractId[FeaturedAppRight]) -> FeaturedAppRight_CreateActivityMarkerResult:
    pass


@DamlName("proxyBeneficiaries")
def proxy_beneficiaries(wallet_user_proxy: WalletUserProxy, user: Party) -> list[AppRewardBeneficiary]:
    pass


@DamlName("validProxy")
def valid_proxy(wallet_user_proxy: WalletUserProxy) -> bool:
    pass


@ledger_effect
def require(msg: str, invariant: bool) -> None:
    pass
