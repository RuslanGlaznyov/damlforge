"""Inline case accessors used by the DamlForge wallet batch dispatcher."""

from typing import Any, Optional

from ... import DamlCaseAccessor
from ..Api.Token.MetadataV1 import AnyContractId, AnyValue


@DamlCaseAccessor("AV_ContractId")
def av_contract_id(value: AnyValue) -> Optional[AnyContractId]:
    raise NotImplementedError


@DamlCaseAccessor("CO_AppPayment")
def co_app_payment(value: Any) -> Optional[Any]:
    raise NotImplementedError


@DamlCaseAccessor("CO_CompleteAcceptedTransfer")
def co_complete_accepted_transfer(value: Any) -> Optional[Any]:
    raise NotImplementedError


@DamlCaseAccessor("CO_SubscriptionAcceptAndMakeInitialPayment")
def co_subscription_accept_and_make_initial_payment(value: Any) -> Optional[Any]:
    raise NotImplementedError


@DamlCaseAccessor("CO_SubscriptionMakePayment")
def co_subscription_make_payment(value: Any) -> Optional[Any]:
    raise NotImplementedError


@DamlCaseAccessor("CO_MergeTransferInputs", arity=0)
def co_merge_transfer_inputs(value: Any) -> Optional[tuple]:
    raise NotImplementedError


@DamlCaseAccessor(
    "CO_BuyMemberTraffic",
    arity=6,
    result_constructor="BuyMemberTrafficArgs",
    field_names=(
        "trafficAmount",
        "memberId",
        "synchronizerId",
        "migrationId",
        "minTopupInterval",
        "topupStateCid",
    ),
)
def co_buy_member_traffic(value: Any) -> Optional[Any]:
    raise NotImplementedError


@DamlCaseAccessor("CO_CompleteBuyTrafficRequest")
def co_complete_buy_traffic_request(value: Any) -> Optional[Any]:
    raise NotImplementedError


@DamlCaseAccessor("CO_Tap")
def co_tap(value: Any) -> Optional[Any]:
    raise NotImplementedError


@DamlCaseAccessor("ExtAmuletOperation")
def ext_amulet_operation(value: Any) -> Optional[Any]:
    raise NotImplementedError


@DamlCaseAccessor("CO_CreateExternalPartySetupProposal", arity=2)
def co_create_external_party_setup_proposal(value: Any) -> Optional[Any]:
    raise NotImplementedError


@DamlCaseAccessor("CO_AcceptTransferPreapprovalProposal", arity=2)
def co_accept_transfer_preapproval_proposal(value: Any) -> Optional[Any]:
    raise NotImplementedError


@DamlCaseAccessor("CO_RenewTransferPreapproval", arity=2)
def co_renew_transfer_preapproval(value: Any) -> Optional[Any]:
    raise NotImplementedError


@DamlCaseAccessor("CO_TransferPreapprovalSend", arity=4)
def co_transfer_preapproval_send(value: Any) -> Optional[Any]:
    raise NotImplementedError
