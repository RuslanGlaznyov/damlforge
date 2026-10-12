from datetime import timedelta
from typing import Annotated, TypeVar

from forge.models import choice, ContractId, Decimal, GenMap, Optional, Party, template, variant, variant_record
from forge.builtins import DamlCaseAccessor, DamlName
from Splice.AmuletRules import AppTransferContext
from Splice.Wallet.Payment import AcceptedAppPayment, AppPaymentRequest, ReceiverAmuletAmount, TerminatedAppPayment

A = TypeVar("A")


@variant
class BalanceUpdateType:
    @variant_record
    def ExternalPayment(payer: Party, description: str, amount: Decimal): pass
    @variant_record
    def Transfer(sender: Party, receiver: Party, amount: Decimal): pass
    @variant_record
    def Netting(balance_changes: Annotated[GenMap[Party, GenMap[Party, Decimal]], DamlName("balanceChanges")]): pass
    @variant_record
    def ExtBalanceUpdateType(dummy_unit_field: Annotated[None, DamlName("dummyUnitField")]): pass


struct GroupKey:
    owner: Party
    provider: Party
    id: GroupId


struct GroupId:
    unpack: str


struct ForOwner:
    owner: Party
    provider: Party


struct ForApp:
    provider: Party


@template
class SplitwellInstallRequest:
    provider: Party
    user: Party

    signatory: list[Party] = [provider, user]

    @choice(controller=provider, consuming=True)
    def SplitwellInstallRequest_Accept(self) -> ContractId[SplitwellInstall]:
        pass

    @choice(controller=provider, consuming=True)
    def SplitwellInstallRequest_Reject(self) -> None:
        pass


@template
class SplitwellInstall:
    provider: Party
    user: Party

    signatory: list[Party] = [provider, user]


@template
class SplitwellRules:
    provider: Party

    signatory: list[Party] = [provider]

    @choice(controller=user, consuming="nonconsuming")
    def SplitwellRules_RequestInstall(self, user: Party) -> ContractId[SplitwellInstallRequest]:
        pass

    @choice(controller=user, consuming="nonconsuming")
    def SplitwellRules_RequestGroup(self, group: Group, user: Party) -> ContractId[GroupRequest]:
        pass

    @choice(controller=user, consuming="nonconsuming")
    def SplitwellRules_CreateInvite(self, group: ContractId[Group], user: Party) -> ContractId[GroupInvite]:
        pass

    @choice(controller=user, consuming="nonconsuming")
    def SplitwellRules_AcceptInvite(self, cid: ContractId[GroupInvite], user: Party) -> ContractId[AcceptedGroupInvite]:
        pass

    @choice(controller=user, consuming="nonconsuming")
    def SplitwellRules_Join(self, group: ContractId[Group], cid: ContractId[AcceptedGroupInvite], user: Party) -> ContractId[Group]:
        pass

    @choice(controller=user, consuming="nonconsuming")
    def SplitwellRules_EnterPayment(self, group: ContractId[Group], amount: Decimal, description: str, user: Party) -> ContractId[BalanceUpdate]:
        pass

    @choice(controller=user, consuming="nonconsuming")
    def SplitwellRules_InitiateTransfer(self, group: ContractId[Group], receiver_amounts: Annotated[list[ReceiverAmuletAmount], DamlName("receiverAmounts")], user: Party) -> tuple[ContractId[TransferInProgress], ContractId[AppPaymentRequest]]:
        pass

    @choice(controller=user, consuming="nonconsuming")
    def SplitwellRules_Net(self, group: ContractId[Group], balance_changes: Annotated[GenMap[Party, GenMap[Party, Decimal]], DamlName("balanceChanges")], user: Party) -> ContractId[BalanceUpdate]:
        pass


@template
class GroupRequest:
    group: Group

    signatory: list[Party] = [group.owner] + group.members + [group.provider]

    @choice(controller=group.provider, consuming=True)
    def GroupRequest_Accept(self) -> ContractId[Group]:
        pass

    @choice(controller=group.provider, consuming=True)
    def GroupRequest_Reject(self) -> None:
        pass


@template
class Group:
    owner: Party
    dso: Party
    members: list[Party]
    id: GroupId
    provider: Party
    accept_duration: Annotated[timedelta, DamlName("acceptDuration")]

    signatory: list[Party] = [owner] + members + [provider]

    @choice(controller=owner, consuming="nonconsuming")
    def Group_Net(self, balance_changes: Annotated[GenMap[Party, GenMap[Party, Decimal]], DamlName("balanceChanges")]) -> ContractId[BalanceUpdate]:
        pass

    @choice(controller=sender, consuming="nonconsuming")
    def Group_InitiateTransfer(self, sender: Party, receiver_amounts: Annotated[list[ReceiverAmuletAmount], DamlName("receiverAmounts")]) -> tuple[ContractId[TransferInProgress], ContractId[AppPaymentRequest]]:
        pass

    @choice(controller=payer, consuming="nonconsuming")
    def Group_EnterPayment(self, payer: Party, amount: Decimal, description: str) -> ContractId[BalanceUpdate]:
        pass

    @choice(controller=[owner, invitee], consuming=True)
    def Group_Join(self, invitee: Party) -> ContractId[Group]:
        pass

    @choice(controller=owner, consuming="nonconsuming")
    def Group_CreateInvite(self) -> ContractId[GroupInvite]:
        pass


@template
class TransferInProgress:
    group: Group
    sender: Party
    receiver_amounts: Annotated[list[ReceiverAmuletAmount], DamlName("receiverAmounts")]
    reference: ContractId[AppPaymentRequest]

    signatory: list[Party] = [group.owner] + group.members + [group.provider]

    @choice(controller=actor, consuming=True)
    def TransferInProgress_Terminate(self, actor: Party, terminated_app_payment_cid: Annotated[ContractId[TerminatedAppPayment], DamlName("terminatedAppPaymentCid")]) -> None:
        pass

    @choice(controller=group.provider, consuming="nonconsuming")
    def TransferInProgress_CompleteTransfer(self, accepted_payment_cid: Annotated[ContractId[AcceptedAppPayment], DamlName("acceptedPaymentCid")], transfer_context: Annotated[AppTransferContext, DamlName("transferContext")]) -> list[ContractId[BalanceUpdate]]:
        pass


@template
class BalanceUpdate:
    group: Group
    update: BalanceUpdateType

    signatory: list[Party] = [group.owner] + group.members + [group.provider]


@template
class GroupInvite:
    group: Group

    signatory: list[Party] = [group.provider, group.owner]

    @choice(controller=invitee, consuming="nonconsuming")
    def GroupInvite_Accept(self, invitee: Party) -> ContractId[AcceptedGroupInvite]:
        pass


@template
class AcceptedGroupInvite:
    group_key: Annotated[GroupKey, DamlName("groupKey")]
    invitee: Party

    signatory: list[Party] = [invitee, group_key.provider, group_key.owner]

    @choice(controller=group_key.owner, consuming=True)
    def AcceptedGroupInvite_Join(self, group: ContractId[Group]) -> ContractId[Group]:
        pass


@DamlCaseAccessor("ExternalPayment", arity=3)
def external_payment(value: BalanceUpdateType) -> Optional[tuple[Party, str, Decimal]]:
    pass


@DamlCaseAccessor("Transfer", arity=3)
def transfer(value: BalanceUpdateType) -> Optional[tuple[Party, Party, Decimal]]:
    pass


@DamlCaseAccessor("Netting")
def netting(value: BalanceUpdateType) -> Optional[GenMap[Party, GenMap[Party, Decimal]]]:
    pass


@DamlCaseAccessor("ExtBalanceUpdateType")
def ext_balance_update_type(value: BalanceUpdateType) -> Optional[None]:
    pass


@DamlName("groupMembers")
def group_members(group: Group) -> list[Party]:
    pass


def subset(list_value: list[A], list_value_1: list[A]) -> bool:
    pass


@DamlName("getGroupKey")
def get_group_key(group: Group) -> GroupKey:
    pass


@DamlName("transferInProgress_receivers")
def transfer_in_progress_receivers(transfer_in_progress: TransferInProgress) -> list[Party]:
    pass
