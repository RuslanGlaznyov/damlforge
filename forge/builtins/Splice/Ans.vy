from datetime import datetime, timedelta
from typing import Annotated

from forge.models import choice, ContractId, Decimal, ledger_effect, Party, template
from forge.builtins import DamlName, no_derive
from Splice.Amulet import Amulet, AmuletCreateSummary
from Splice.AmuletRules import AppTransferContext
from Splice.Wallet.Subscriptions import SubscriptionIdleState, SubscriptionInitialPayment, SubscriptionPayment, SubscriptionRequest, TerminatedSubscription


@no_derive
struct AnsRules_RequestEntryResult:
    entry_cid: Annotated[ContractId[AnsEntryContext], DamlName("entryCid")]
    request_cid: Annotated[ContractId[SubscriptionRequest], DamlName("requestCid")]


@no_derive
struct AnsRules_CollectInitialEntryPaymentResult:
    entry_cid: Annotated[ContractId[AnsEntry], DamlName("entryCid")]
    subscription_state_cid: Annotated[ContractId[SubscriptionIdleState], DamlName("subscriptionStateCid")]


@no_derive
struct AnsEntryContext_CollectInitialEntryPaymentResult:
    entry_cid: Annotated[ContractId[AnsEntry], DamlName("entryCid")]
    subscription_state_cid: Annotated[ContractId[SubscriptionIdleState], DamlName("subscriptionStateCid")]


@no_derive
struct AnsRules_CollectEntryRenewalPaymentResult:
    entry_cid: Annotated[ContractId[AnsEntry], DamlName("entryCid")]
    subscription_state_cid: Annotated[ContractId[SubscriptionIdleState], DamlName("subscriptionStateCid")]


@no_derive
struct AnsRules_RejectEntryInitialPaymentResult:
    amulet_sum: Annotated[AmuletCreateSummary[ContractId[Amulet]], DamlName("amuletSum")]


@no_derive
struct AnsEntryContext_CollectEntryRenewalPaymentResult:
    entry_cid: Annotated[ContractId[AnsEntry], DamlName("entryCid")]
    subscription_state_cid: Annotated[ContractId[SubscriptionIdleState], DamlName("subscriptionStateCid")]


@no_derive
struct AnsEntryContext_RejectEntryInitialPaymentResult:
    amulet_sum: Annotated[AmuletCreateSummary[ContractId[Amulet]], DamlName("amuletSum")]


@no_derive
struct AnsEntryContext_TerminateResult:
    pass


@no_derive
struct AnsEntry_ExpireResult:
    pass


@no_derive
struct AnsEntry_RenewResult:
    entry_cid: Annotated[ContractId[AnsEntry], DamlName("entryCid")]


struct ExpectedPayment:
    dso: Party
    sender: Party


struct ExpectedEntryContext:
    dso: Party
    user: Party
    reference: ContractId[SubscriptionRequest]


struct AnsRulesConfig:
    renewal_duration: Annotated[timedelta, DamlName("renewalDuration")]
    entry_lifetime: Annotated[timedelta, DamlName("entryLifetime")]
    entry_fee: Annotated[Decimal, DamlName("entryFee")]
    description_prefix: Annotated[str, DamlName("descriptionPrefix")]


@template
class AnsRules:
    dso: Party
    config: AnsRulesConfig

    signatory: list[Party] = [dso]

    @choice(controller=user, consuming="nonconsuming")
    def AnsRules_RequestEntry(self, name: str, url: str, description: str, user: Party) -> AnsRules_RequestEntryResult:
        pass

    @choice(controller=[dso, user], consuming="nonconsuming")
    def AnsRules_CollectInitialEntryPayment(self, user: Party, entry_context: Annotated[ContractId[AnsEntryContext], DamlName("entryContext")], payment_cid: Annotated[ContractId[SubscriptionInitialPayment], DamlName("paymentCid")], transfer_context: Annotated[AppTransferContext, DamlName("transferContext")]) -> AnsRules_CollectInitialEntryPaymentResult:
        pass

    @choice(controller=[dso, user], consuming="nonconsuming")
    def AnsRules_CollectEntryRenewalPayment(self, user: Party, entry_context: Annotated[ContractId[AnsEntryContext], DamlName("entryContext")], payment_cid: Annotated[ContractId[SubscriptionPayment], DamlName("paymentCid")], entry_cid: Annotated[ContractId[AnsEntry], DamlName("entryCid")], transfer_context: Annotated[AppTransferContext, DamlName("transferContext")]) -> AnsRules_CollectEntryRenewalPaymentResult:
        pass

    @choice(controller=dso, consuming="nonconsuming")
    def AnsRules_RejectEntryInitialPayment(self, payment_cid: Annotated[ContractId[SubscriptionInitialPayment], DamlName("paymentCid")], transfer_context: Annotated[AppTransferContext, DamlName("transferContext")]) -> AnsRules_RejectEntryInitialPaymentResult:
        pass


@template
class AnsEntryContext:
    dso: Party
    user: Party
    name: str
    url: str
    description: str
    reference: ContractId[SubscriptionRequest]

    signatory: list[Party] = [dso, user]

    @choice(controller=actor, consuming=True)
    def AnsEntryContext_Terminate(self, actor: Party, terminated_subscription_cid: Annotated[ContractId[TerminatedSubscription], DamlName("terminatedSubscriptionCid")]) -> AnsEntryContext_TerminateResult:
        pass

    @choice(controller=dso, consuming="nonconsuming")
    def AnsEntryContext_CollectInitialEntryPayment(self, payment_cid: Annotated[ContractId[SubscriptionInitialPayment], DamlName("paymentCid")], transfer_context: Annotated[AppTransferContext, DamlName("transferContext")], ans_rules_cid: Annotated[ContractId[AnsRules], DamlName("ansRulesCid")]) -> AnsEntryContext_CollectInitialEntryPaymentResult:
        pass

    @choice(controller=dso, consuming="nonconsuming")
    def AnsEntryContext_CollectEntryRenewalPayment(self, payment_cid: Annotated[ContractId[SubscriptionPayment], DamlName("paymentCid")], entry_cid: Annotated[ContractId[AnsEntry], DamlName("entryCid")], transfer_context: Annotated[AppTransferContext, DamlName("transferContext")], ans_rules_cid: Annotated[ContractId[AnsRules], DamlName("ansRulesCid")]) -> AnsEntryContext_CollectEntryRenewalPaymentResult:
        pass

    @choice(controller=dso, consuming="nonconsuming")
    def AnsEntryContext_RejectEntryInitialPayment(self, payment_cid: Annotated[ContractId[SubscriptionInitialPayment], DamlName("paymentCid")], transfer_context: Annotated[AppTransferContext, DamlName("transferContext")], ans_rules_cid: Annotated[ContractId[AnsRules], DamlName("ansRulesCid")]) -> AnsEntryContext_RejectEntryInitialPaymentResult:
        pass


@template
class AnsEntry:
    user: Party
    dso: Party
    name: str
    url: str
    description: str
    expires_at: Annotated[datetime, DamlName("expiresAt")]

    signatory: list[Party] = [user, dso]

    @choice(controller=[user, dso], consuming=True)
    def AnsEntry_Renew(self, extension: timedelta) -> AnsEntry_RenewResult:
        pass

    @choice(controller=actor, consuming=True)
    def AnsEntry_Expire(self, actor: Party) -> AnsEntry_ExpireResult:
        pass


@ledger_effect
@DamlName("fetchAndValidateInitialPayment")
def fetch_and_validate_initial_payment(cid: ContractId[SubscriptionInitialPayment], expected_payment: ExpectedPayment) -> SubscriptionInitialPayment:
    pass


@ledger_effect
@DamlName("fetchAndValidatePayment")
def fetch_and_validate_payment(cid: ContractId[SubscriptionPayment], expected_payment: ExpectedPayment) -> SubscriptionPayment:
    pass


@ledger_effect
@DamlName("fetchAndValidateEntryContext")
def fetch_and_validate_entry_context(cid: ContractId[AnsEntryContext], expected_entry_context: ExpectedEntryContext) -> AnsEntryContext:
    pass


@DamlName("validAnsConfig")
def valid_ans_config(ans_rules_config: AnsRulesConfig) -> bool:
    pass
