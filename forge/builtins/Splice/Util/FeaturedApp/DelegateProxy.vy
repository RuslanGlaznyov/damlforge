from typing import Annotated, Generic, TypeVar

from forge.models import choice, ContractId, Party, template
from forge.builtins import DamlName, no_derive
from Splice.Api.FeaturedAppRightV1 import AppRewardBeneficiary, FeaturedAppRight, FeaturedAppRight_CreateActivityMarkerResult
from Splice.Api.Token.AllocationInstructionV1 import AllocationFactory, AllocationFactory_Allocate, AllocationInstructionResult
from Splice.Api.Token.AllocationV1 import Allocation, Allocation_Withdraw, Allocation_WithdrawResult
from Splice.Api.Token.TransferInstructionV1 import TransferFactory, TransferFactory_Transfer, TransferInstruction, TransferInstructionResult, TransferInstruction_Accept, TransferInstruction_Reject, TransferInstruction_Withdraw

Arg = TypeVar("Arg")
Ch = TypeVar("Ch")
R = TypeVar("R")
T = TypeVar("T")


struct ProxyArg(Generic[Arg]):
    choice_arg: Annotated[Arg, DamlName("choiceArg")]
    featured_app_right_cid: Annotated[ContractId[FeaturedAppRight], DamlName("featuredAppRightCid")]
    beneficiaries: list[AppRewardBeneficiary]


@no_derive
struct ProxyResult(Generic[R]):
    marker_result: Annotated[FeaturedAppRight_CreateActivityMarkerResult, DamlName("markerResult")]
    choice_result: Annotated[R, DamlName("choiceResult")]


@template
class DelegateProxy:
    provider: Party
    delegate: Party

    signatory: list[Party] = [provider]
    observer: list[Party] = [delegate]

    @choice(controller=delegate, consuming="nonconsuming")
    def DelegateProxy_TransferFactory_Transfer(self, cid: ContractId[TransferFactory], proxy_arg: Annotated[ProxyArg[TransferFactory_Transfer], DamlName("proxyArg")]) -> ProxyResult[TransferInstructionResult]:
        pass

    @choice(controller=delegate, consuming="nonconsuming")
    def DelegateProxy_TransferInstruction_Accept(self, cid: ContractId[TransferInstruction], proxy_arg: Annotated[ProxyArg[TransferInstruction_Accept], DamlName("proxyArg")]) -> ProxyResult[TransferInstructionResult]:
        pass

    @choice(controller=delegate, consuming="nonconsuming")
    def DelegateProxy_TransferInstruction_Reject(self, cid: ContractId[TransferInstruction], proxy_arg: Annotated[ProxyArg[TransferInstruction_Reject], DamlName("proxyArg")]) -> ProxyResult[TransferInstructionResult]:
        pass

    @choice(controller=delegate, consuming="nonconsuming")
    def DelegateProxy_TransferInstruction_Withdraw(self, cid: ContractId[TransferInstruction], proxy_arg: Annotated[ProxyArg[TransferInstruction_Withdraw], DamlName("proxyArg")]) -> ProxyResult[TransferInstructionResult]:
        pass

    @choice(controller=delegate, consuming="nonconsuming")
    def DelegateProxy_AllocationFactory_Allocate(self, cid: ContractId[AllocationFactory], proxy_arg: Annotated[ProxyArg[AllocationFactory_Allocate], DamlName("proxyArg")]) -> ProxyResult[AllocationInstructionResult]:
        pass

    @choice(controller=delegate, consuming="nonconsuming")
    def DelegateProxy_Allocation_Withdraw(self, cid: ContractId[Allocation], proxy_arg: Annotated[ProxyArg[Allocation_Withdraw], DamlName("proxyArg")]) -> ProxyResult[Allocation_WithdrawResult]:
        pass


@DamlName("exerciseProxyChoice", is_ledger_effect=True)
def exercise_proxy_choice(proxy: DelegateProxy, cid: ContractId[T], proxy_arg: ProxyArg[Ch]) -> ProxyResult[R]:
    pass


@DamlName("require", is_ledger_effect=True)
def require(msg: str, invariant: bool) -> None:
    pass
