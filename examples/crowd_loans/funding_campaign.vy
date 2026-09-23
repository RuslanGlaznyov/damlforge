from decimal import Decimal
from typing import Optional
from forge.models import ContractId, Party, Timestamp, choice, ledger_effect
from forge.builtins import DamlName
from forge.builtins.daml_lang import archive, create, exercise, fetch
from loan_terms import LoanRewards, LoanTerms, LoanTracker, PeriodPayment, PeriodPaymentStatus
from Splice.Amulet import Amulet, LockedAmulet, LockedAmulet_UnlockV2
from Splice.AmuletRules import (
    AppTransferContext,
    CreatedAmulet,
    InputAmulet,
    Transfer,
    TransferInput,
    TransferOutput,
    created_amulet_locked_cid,
    created_amulet_to_holding,
    exercise_app_transfer,
)
from Splice.Api.Token.HoldingV1 import Holding, InstrumentId
from Splice.Expiry import TimeLock

flag CampaignStatus:
    ACTIVE
    SUCCESSFUL
    FAILED
    COMPLETED
    CANCELLED
    PAUSED


struct FundingCampaignView:
    platform: Party
    developer: Party
    dso: Party
    external_id: str
    target: Decimal
    deadline: Timestamp
    raised: Decimal
    status: CampaignStatus
    accepted_instrument_id: InstrumentId
    total_investors: int
    investments: list[tuple[Party, Decimal]]
    excess_investments: list[tuple[Party, Decimal]]


struct InstallmentReleaseView:
    platform: Party
    developer: Party
    external_id: str
    installment_number: int
    amount: Decimal
    release_date: Timestamp
    released: bool
    escrowed: bool
    paused: bool


flag TransferStatus:
    PENDING
    ACCEPTED
    REJECTED
    WITHDRAWN


struct InstallmentTransferView:
    platform: Party
    developer: Party
    dso: Party
    external_id: str
    installment_number: int
    amount: Decimal
    status: TransferStatus
    accept_before: Timestamp


flag FundMode:
    ALL_OR_NOTHING
    FLEXIBLE


struct Terms:
    platform_fees: Decimal
    fund_mode: FundMode
    cooldown_period_days: int
    flexible_funding_minimum: Decimal
    cap_at_target: bool
    locked_party: Optional[Party]
    unlocked_party: Optional[Party]


def or_empty_party_amounts(value: Optional[list[tuple[Party, Decimal]]]) -> list[tuple[Party, Decimal]]:
    if value == None:
        return []
    return value


def or_empty_locked_holdings(
    value: Optional[list[tuple[Party, ContractId[LockedAmulet]]]]
) -> list[tuple[Party, ContractId[LockedAmulet]]]:
    if value == None:
        return []
    return value


def or_empty_holdings(
    value: Optional[list[tuple[Party, ContractId[Holding]]]]
) -> list[tuple[Party, ContractId[Holding]]]:
    if value == None:
        return []
    return value


def or_empty_parties(value: Optional[list[Party]]) -> list[Party]:
    if value == None:
        return []
    return value


def update_investments(
    investor: Party, amount: Decimal, existing: list[tuple[Party, Decimal]]
) -> list[tuple[Party, Decimal]]:
    updated: list[tuple[Party, Decimal]] = []
    found = False
    for entry: tuple[Party, Decimal] in existing:
        party: Party = entry[0]
        existing_amount: Decimal = entry[1]
        if party == investor:
            updated.append((party, existing_amount + amount))
            found = True
        else:
            updated.append((party, existing_amount))
    if not found:
        updated.append((investor, amount))
    return updated


def campaign_observers(
    investments: list[tuple[Party, Decimal]], excess_investments: list[tuple[Party, Decimal]]
) -> list[Party]:
    observers: list[Party] = []
    for entry: tuple[Party, Decimal] in investments:
        party: Party = entry[0]
        already_seen = False
        for seen: Party in observers:
            if seen == party:
                already_seen = True
        if not already_seen:
            observers.append(party)
    for entry: tuple[Party, Decimal] in excess_investments:
        party: Party = entry[0]
        already_seen = False
        for seen: Party in observers:
            if seen == party:
                already_seen = True
        if not already_seen:
            observers.append(party)
    return observers


def calculate_installments(total: Decimal) -> list[Decimal]:
    third = total / Decimal(3)
    remainder = total - (third * Decimal(2))
    return [third, third, remainder]


def split_at_sizes(
    holdings: list[ContractId[Holding]], sizes: list[int]
) -> list[list[ContractId[Holding]]]:
    remaining: list[ContractId[Holding]] = []
    for holding_cid: ContractId[Holding] in holdings:
        remaining.append(holding_cid)

    chunks: list[list[ContractId[Holding]]] = []
    for chunk_size: int in sizes:
        chunk: list[ContractId[Holding]] = []
        taken = 0
        rest: list[ContractId[Holding]] = []
        for holding_cid: ContractId[Holding] in remaining:
            if taken < chunk_size:
                chunk.append(holding_cid)
                taken = taken + 1
            else:
                rest.append(holding_cid)
        chunks.append(chunk)
        remaining = rest

    return chunks


def split_holdings_into_tranches(
    holdings: list[ContractId[Holding]], num_tranches: int
) -> list[list[ContractId[Holding]]]:
    holdings_count = len(holdings)
    base_size = holdings_count / num_tranches
    remainder = holdings_count % num_tranches

    sizes: list[int] = []
    for _index: int in range(0, remainder):
        sizes.append(base_size + 1)
    for _index: int in range(0, num_tranches - remainder):
        sizes.append(base_size)

    return split_at_sizes(holdings, sizes)


def group_holdings_by_investor(
    holdings: list[tuple[Party, ContractId[Holding]]]
) -> list[tuple[Party, list[ContractId[Holding]]]]:
    investors: list[Party] = []
    for entry: tuple[Party, ContractId[Holding]] in holdings:
        party: Party = entry[0]
        already_seen = False
        for seen: Party in investors:
            if seen == party:
                already_seen = True
        if not already_seen:
            investors.append(party)

    grouped: list[tuple[Party, list[ContractId[Holding]]]] = []
    for investor: Party in investors:
        investor_holdings: list[ContractId[Holding]] = []
        for entry: tuple[Party, ContractId[Holding]] in holdings:
            if entry[0] == investor:
                investor_holdings.append(entry[1])
        grouped.append((investor, investor_holdings))
    return grouped


def calculate_num_holdings_needed(
    holdings: list[tuple[Party, ContractId[Holding]]], target_amount: Decimal
) -> int:
    total_holdings = len(holdings)
    if total_holdings > 0:
        avg_amount_per_holding = target_amount / Decimal(total_holdings)
    else:
        avg_amount_per_holding = Decimal(0)
    return ceil(target_amount / avg_amount_per_holding)


@ledger_effect
def verify_amulets(dso_party: Party, amulets: list[ContractId[Amulet]]) -> Decimal:
    total = Decimal(0)
    for amulet_cid: ContractId[Amulet] in amulets:
        amulet = fetch(amulet_cid)
        assert amulet.dso == dso_party, "Amulet DSO must match"
        total = total + amulet.amount.initial_amount
    return total


@template
class FundingCampaign:
    platform: Party
    developer: Party
    dso: Party
    external_id: str
    target: Decimal
    deadline: Timestamp
    raised: Decimal
    balance: Decimal
    status: CampaignStatus
    accepted_instrument_id: InstrumentId
    terms: Terms
    investments: Optional[list[tuple[Party, Decimal]]]
    excess_investments: Optional[list[tuple[Party, Decimal]]]
    excess_holdings: Optional[list[tuple[Party, ContractId[LockedAmulet]]]]
    locked_holdings: Optional[list[tuple[Party, ContractId[LockedAmulet]]]]
    unlocked_holdings: Optional[list[tuple[Party, ContractId[Holding]]]]
    refunded_investors: Optional[list[Party]]
    loan_terms: Optional[LoanTerms]
    finalized_at: Optional[Timestamp]

    signatory: list[Party] = [platform, developer]
    observer: list[Party] = campaign_observers(
        or_empty_party_amounts(investments), or_empty_party_amounts(excess_investments)
    )

    def __init__(
        self,
        platform: Party,
        developer: Party,
        dso: Party,
        external_id: str,
        target: Decimal,
        deadline: Timestamp,
        raised: Decimal,
        balance: Decimal,
        status: CampaignStatus,
        accepted_instrument_id: InstrumentId,
        terms: Terms,
        investments: Optional[list[tuple[Party, Decimal]]],
        excess_investments: Optional[list[tuple[Party, Decimal]]],
        excess_holdings: Optional[list[tuple[Party, ContractId[LockedAmulet]]]],
        locked_holdings: Optional[list[tuple[Party, ContractId[LockedAmulet]]]],
        unlocked_holdings: Optional[list[tuple[Party, ContractId[Holding]]]],
        refunded_investors: Optional[list[Party]],
        loan_terms: Optional[LoanTerms],
        finalized_at: Optional[Timestamp],
    ):
        assert target > Decimal(0), "target must be positive"
        assert raised >= Decimal(0), "raised must be non-negative"
        assert balance <= raised, "balance must not exceed raised"
        assert terms.platform_fees >= Decimal(0), "platform_fees must be non-negative"
        assert terms.platform_fees <= Decimal(1), "platform_fees must not exceed 1"
        assert terms.flexible_funding_minimum >= Decimal(0), "flexible_funding_minimum must be non-negative"
        assert terms.flexible_funding_minimum <= target, "flexible_funding_minimum must not exceed target"
        assert terms.cooldown_period_days >= 0, "cooldown_period_days must be non-negative"

        self.platform = platform
        self.developer = developer
        self.dso = dso
        self.external_id = external_id
        self.target = target
        self.deadline = deadline
        self.raised = raised
        self.balance = balance
        self.status = status
        self.accepted_instrument_id = accepted_instrument_id
        self.terms = terms
        self.investments = investments
        self.excess_investments = excess_investments
        self.excess_holdings = excess_holdings
        self.locked_holdings = locked_holdings
        self.unlocked_holdings = unlocked_holdings
        self.refunded_investors = refunded_investors
        self.loan_terms = loan_terms
        self.finalized_at = finalized_at

    @choice(controller=[investor, platform], consuming=True)
    def FundingCampaign_Invest(
        self,
        investor: Party,
        inputs: list[ContractId[Amulet]],
        amount: Decimal,
        app_transfer_context: AppTransferContext,
    ) -> ContractId[FundingCampaign]:
        assert self.status == CampaignStatus.ACTIVE, "campaign must be Active"
        assert amount > Decimal(0), "investment amount must be positive"

        input_amount = verify_amulets(self.dso, inputs)
        assert input_amount >= amount, "insufficient funds for investment"

        remaining = amount
        if self.terms.cap_at_target:
            headroom = self.target - self.raised
            if headroom > Decimal(0):
                remaining = headroom
            else:
                remaining = Decimal(0)

        accepted_amount = amount
        if remaining < amount:
            accepted_amount = remaining
        excess_amount = amount - accepted_amount

        accepted_outputs: list[TransferOutput] = []
        if accepted_amount > Decimal(0):
            accepted_lock = TimeLock(
                holders=[self.platform],
                expires_at=self.deadline,
                opt_context="Investment for campaign " + self.external_id,
            )
            accepted_outputs.append(
                TransferOutput(
                    receiver=self.platform,
                    receiver_fee_ratio=Decimal(0),
                    amount=accepted_amount,
                    lock=accepted_lock,
                )
            )

        excess_outputs: list[TransferOutput] = []
        if excess_amount > Decimal(0):
            excess_lock = TimeLock(
                holders=[self.platform],
                expires_at=self.deadline,
                opt_context="Excess for campaign " + self.external_id,
            )
            excess_outputs.append(
                TransferOutput(
                    receiver=self.platform,
                    receiver_fee_ratio=Decimal(0),
                    amount=excess_amount,
                    lock=excess_lock,
                )
            )

        combined_outputs: list[TransferOutput] = []
        for output: TransferOutput in accepted_outputs:
            combined_outputs.append(output)
        for output: TransferOutput in excess_outputs:
            combined_outputs.append(output)

        transfer_inputs: list[TransferInput] = []
        for input_cid: ContractId[Amulet] in inputs:
            transfer_inputs.append(InputAmulet(input_cid))

        transfer = Transfer(
            sender=self.platform,
            provider=self.platform,
            inputs=transfer_inputs,
            outputs=combined_outputs,
            beneficiaries=None,
        )

        transfer_result = exercise_app_transfer(self.dso, app_transfer_context, transfer)

        locked_cids: list[ContractId[LockedAmulet]] = []
        for created_amulet: CreatedAmulet in transfer_result.created_amulets:
            locked_cid = created_amulet_locked_cid(created_amulet)
            if locked_cid != None:
                locked_cids.append(locked_cid)

        accepted_cids: list[ContractId[LockedAmulet]] = []
        excess_cids: list[ContractId[LockedAmulet]] = []
        if accepted_amount > Decimal(0) and excess_amount > Decimal(0):
            index = 0
            for locked_cid: ContractId[LockedAmulet] in locked_cids:
                if index < 1:
                    accepted_cids.append(locked_cid)
                else:
                    excess_cids.append(locked_cid)
                index = index + 1
        elif accepted_amount > Decimal(0):
            for locked_cid: ContractId[LockedAmulet] in locked_cids:
                accepted_cids.append(locked_cid)
        else:
            for locked_cid: ContractId[LockedAmulet] in locked_cids:
                excess_cids.append(locked_cid)

        current_investments = or_empty_party_amounts(self.investments)
        current_locked_holdings = or_empty_locked_holdings(self.locked_holdings)
        current_excess_investments = or_empty_party_amounts(self.excess_investments)
        current_excess_holdings = or_empty_locked_holdings(self.excess_holdings)

        if accepted_amount > Decimal(0):
            new_investments = update_investments(investor, accepted_amount, current_investments)
        else:
            new_investments = current_investments

        if excess_amount > Decimal(0):
            new_excess_investments = update_investments(investor, excess_amount, current_excess_investments)
        else:
            new_excess_investments = current_excess_investments

        new_locked_holdings: list[tuple[Party, ContractId[LockedAmulet]]] = []
        for accepted_cid: ContractId[LockedAmulet] in accepted_cids:
            new_locked_holdings.append((investor, accepted_cid))
        for entry: tuple[Party, ContractId[LockedAmulet]] in current_locked_holdings:
            new_locked_holdings.append(entry)

        new_excess_holdings: list[tuple[Party, ContractId[LockedAmulet]]] = []
        for excess_cid: ContractId[LockedAmulet] in excess_cids:
            new_excess_holdings.append((investor, excess_cid))
        for entry: tuple[Party, ContractId[LockedAmulet]] in current_excess_holdings:
            new_excess_holdings.append(entry)

        new_raised = self.raised + accepted_amount
        new_balance = self.balance + accepted_amount

        return create(
            FundingCampaign(
                platform=self.platform,
                developer=self.developer,
                dso=self.dso,
                external_id=self.external_id,
                target=self.target,
                deadline=self.deadline,
                raised=new_raised,
                balance=new_balance,
                status=self.status,
                accepted_instrument_id=self.accepted_instrument_id,
                terms=self.terms,
                investments=new_investments,
                excess_investments=new_excess_investments,
                excess_holdings=new_excess_holdings,
                locked_holdings=new_locked_holdings,
                unlocked_holdings=self.unlocked_holdings,
                refunded_investors=self.refunded_investors,
                loan_terms=self.loan_terms,
                finalized_at=self.finalized_at,
            )
        )

    @choice(controller=platform, consuming=True)
    def finalize(self, current_time: Timestamp) -> ContractId["FundingCampaign"]:
        assert self.status == CampaignStatus.ACTIVE, "Must be Active"

        if self.terms.fund_mode == FundMode.ALL_OR_NOTHING:
            if self.raised >= self.target:
                new_status = CampaignStatus.SUCCESSFUL
            else:
                new_status = CampaignStatus.FAILED
        else:
            if self.raised >= self.terms.flexible_funding_minimum:
                new_status = CampaignStatus.SUCCESSFUL
            else:
                new_status = CampaignStatus.FAILED

        return create(
            FundingCampaign(
                platform=self.platform,
                developer=self.developer,
                dso=self.dso,
                external_id=self.external_id,
                target=self.target,
                deadline=self.deadline,
                raised=self.raised,
                balance=self.balance,
                status=new_status,
                accepted_instrument_id=self.accepted_instrument_id,
                terms=self.terms,
                investments=self.investments,
                excess_investments=self.excess_investments,
                excess_holdings=self.excess_holdings,
                locked_holdings=self.locked_holdings,
                unlocked_holdings=self.unlocked_holdings,
                refunded_investors=self.refunded_investors,
                loan_terms=self.loan_terms,
                finalized_at=current_time,
            )
        )

    @choice(controller=platform, consuming=True)
    @DamlName("FundingCampaign_Cancel")
    def cancel(self) -> ContractId["FundingCampaign"]:
        assert (
            self.status == CampaignStatus.SUCCESSFUL
            or self.status == CampaignStatus.COMPLETED
        ), "Can only cancel Successful or Completed campaigns"

        current_locked_holdings = or_empty_locked_holdings(self.locked_holdings)
        current_unlocked_holdings = or_empty_holdings(self.unlocked_holdings)
        assert len(current_locked_holdings) > 0 or len(current_unlocked_holdings) > 0, (
            "Must have remaining holdings to refund"
        )

        return create(
            FundingCampaign(
                platform=self.platform,
                developer=self.developer,
                dso=self.dso,
                external_id=self.external_id,
                target=self.target,
                deadline=self.deadline,
                raised=self.raised,
                balance=self.balance,
                status=CampaignStatus.CANCELLED,
                accepted_instrument_id=self.accepted_instrument_id,
                terms=self.terms,
                investments=self.investments,
                excess_investments=self.excess_investments,
                excess_holdings=self.excess_holdings,
                locked_holdings=self.locked_holdings,
                unlocked_holdings=self.unlocked_holdings,
                refunded_investors=self.refunded_investors,
                loan_terms=self.loan_terms,
                finalized_at=self.finalized_at,
            )
        )

    @choice(controller=[platform, developer], consuming=True)
    def create_installments(
        self, app_transfer_context: AppTransferContext
    ) -> tuple[list[ContractId[InstallmentRelease]], ContractId["FundingCampaign"]]:
        assert self.status == CampaignStatus.SUCCESSFUL, "must be successful"
        assert self.raised > Decimal(0), "must have funds to distribute"

        current_locked_holdings = or_empty_locked_holdings(self.locked_holdings)
        current_investments = or_empty_party_amounts(self.investments)

        new_unlocked_holdings: list[tuple[Party, ContractId[Holding]]] = []
        for entry: tuple[Party, ContractId[LockedAmulet]] in current_locked_holdings:
            investor: Party = entry[0]
            locked_cid: ContractId[LockedAmulet] = entry[1]
            unlock_result = exercise(locked_cid, LockedAmulet_UnlockV2)
            holding_cid: ContractId[Holding] = to_interface_contract_id(unlock_result.amulet_cid)
            new_unlocked_holdings.append((investor, holding_cid))

        tracker_cid: Optional[ContractId[LoanTracker]] = None
        if self.loan_terms != None:
            lt: LoanTerms = self.loan_terms
            new_tracker_cid = create(
                LoanTracker(
                    platform=self.platform,
                    developer=self.developer,
                    dso=self.dso,
                    campaign_external_id=self.external_id,
                    loan_terms=lt,
                    total_repaid=Decimal(0),
                    repayment_history=[],
                    investments=current_investments,
                    total_raised=self.raised,
                    balance=Decimal(0),
                    holding_cids=[],
                )
            )
            tracker_cid = new_tracker_cid

        installment_amounts = calculate_installments(self.raised)

        just_holdings: list[ContractId[Holding]] = []
        for entry: tuple[Party, ContractId[Holding]] in new_unlocked_holdings:
            just_holdings.append(entry[1])
        holdings_per_installment = split_holdings_into_tranches(just_holdings, 3)

        first_installment_holdings = holdings_per_installment[0]

        remaining_holdings_for_installments: list[ContractId[Holding]] = []
        tranche_index = 0
        for tranche: list[ContractId[Holding]] in holdings_per_installment:
            if tranche_index > 0:
                for holding_cid: ContractId[Holding] in tranche:
                    remaining_holdings_for_installments.append(holding_cid)
            tranche_index = tranche_index + 1

        if self.finalized_at != None:
            anchor_time: Timestamp = self.finalized_at
        else:
            anchor_time: Timestamp = self.deadline

        first_installment_amount = installment_amounts[0]

        installments: list[ContractId[InstallmentRelease]] = []
        month = 1
        first_installment = create(
            InstallmentRelease(
                platform=self.platform,
                developer=self.developer,
                dso=self.dso,
                external_id=self.external_id,
                installment_number=month,
                amount=first_installment_amount,
                release_date=add_rel_time(anchor_time, days(self.terms.cooldown_period_days + 30 * month)),
                released=False,
                escrowed=True,
                platform_fees=self.terms.platform_fees,
                holding_cids=first_installment_holdings,
                paused=False,
                loan_tracker_cid=tracker_cid,
            )
        )
        installments.append(first_installment)

        other_month: int = 2
        for amount: Decimal in installment_amounts:
            if other_month >= 2 and other_month <= 3:
                other_installment = create(
                    InstallmentRelease(
                        platform=self.platform,
                        developer=self.developer,
                        dso=self.dso,
                        external_id=self.external_id,
                        installment_number=other_month,
                        amount=installment_amounts[other_month - 1],
                        release_date=add_rel_time(
                            anchor_time, days(self.terms.cooldown_period_days + 30 * other_month)
                        ),
                        released=False,
                        escrowed=False,
                        platform_fees=self.terms.platform_fees,
                        holding_cids=[],
                        paused=False,
                        loan_tracker_cid=tracker_cid,
                    )
                )
                installments.append(other_installment)
            other_month = other_month + 1

        remaining_unlocked_holdings_list: list[tuple[Party, ContractId[Holding]]] = []
        for entry: tuple[Party, ContractId[Holding]] in new_unlocked_holdings:
            holding_cid: ContractId[Holding] = entry[1]
            still_remaining = False
            for remaining_cid: ContractId[Holding] in remaining_holdings_for_installments:
                if remaining_cid == holding_cid:
                    still_remaining = True
            if still_remaining:
                remaining_unlocked_holdings_list.append(entry)

        updated_campaign = create(
            FundingCampaign(
                platform=self.platform,
                developer=self.developer,
                dso=self.dso,
                external_id=self.external_id,
                target=self.target,
                deadline=self.deadline,
                raised=self.raised,
                balance=self.balance - first_installment_amount,
                status=CampaignStatus.COMPLETED,
                accepted_instrument_id=self.accepted_instrument_id,
                terms=self.terms,
                investments=self.investments,
                excess_investments=self.excess_investments,
                excess_holdings=self.excess_holdings,
                locked_holdings=[],
                unlocked_holdings=remaining_unlocked_holdings_list,
                refunded_investors=self.refunded_investors,
                loan_terms=self.loan_terms,
                finalized_at=self.finalized_at,
            )
        )

        return (installments, updated_campaign)

    @choice(controller=[investor, platform], consuming=True)
    def claim_refund(
        self, investor: Party, receiver: Party, app_transfer_context: AppTransferContext
    ) -> tuple[ContractId["FundingCampaign"], list[ContractId[Holding]]]:
        assert (
            self.status == CampaignStatus.FAILED
            or self.status == CampaignStatus.CANCELLED
        ), "Campaign must be Failed or Cancelled"

        current_refunded_investors = or_empty_parties(self.refunded_investors)
        current_locked_holdings = or_empty_locked_holdings(self.locked_holdings)
        current_investments = or_empty_party_amounts(self.investments)

        already_refunded = False
        for refunded: Party in current_refunded_investors:
            if refunded == investor:
                already_refunded = True
        assert not already_refunded, "Investor has already been refunded"
        assert len(current_locked_holdings) > 0, "Must have holdings to refund"

        investor_amount = Decimal(0)
        for entry: tuple[Party, Decimal] in current_investments:
            if entry[0] == investor:
                investor_amount = entry[1]
        assert investor_amount > Decimal(0), "Investor has no recorded investment"

        total_investments = Decimal(0)
        for entry: tuple[Party, Decimal] in current_investments:
            total_investments = total_investments + entry[1]
        proportion = investor_amount / total_investments
        total_holdings = len(current_locked_holdings)

        if total_holdings == 0:
            num_holdings_for_investor = 0
        else:
            computed = floor(proportion * Decimal(total_holdings))
            if computed > 1:
                num_holdings_for_investor = computed
            else:
                num_holdings_for_investor = 1

        capped_num = num_holdings_for_investor
        if total_holdings < capped_num:
            capped_num = total_holdings

        all_locked_cids: list[ContractId[LockedAmulet]] = []
        for entry: tuple[Party, ContractId[LockedAmulet]] in current_locked_holdings:
            all_locked_cids.append(entry[1])

        refund_locked_cids: list[ContractId[LockedAmulet]] = []
        remaining_locked_cids: list[ContractId[LockedAmulet]] = []
        index = 0
        for locked_cid: ContractId[LockedAmulet] in all_locked_cids:
            if index < capped_num:
                refund_locked_cids.append(locked_cid)
            else:
                remaining_locked_cids.append(locked_cid)
            index = index + 1

        unlocked_amulet_cids: list[ContractId[Amulet]] = []
        refunded_amount = Decimal(0)
        for locked_cid: ContractId[LockedAmulet] in refund_locked_cids:
            unlock_result = exercise(locked_cid, LockedAmulet_UnlockV2)
            amulet = fetch(unlock_result.amulet_cid)
            unlocked_amulet_cids.append(unlock_result.amulet_cid)
            refunded_amount = refunded_amount + amulet.amount.initial_amount

        refund_output = TransferOutput(
            receiver=receiver,
            receiver_fee_ratio=Decimal(1),
            amount=refunded_amount,
            lock=None,
        )

        transfer_inputs: list[TransferInput] = []
        for amulet_cid: ContractId[Amulet] in unlocked_amulet_cids:
            transfer_inputs.append(InputAmulet(amulet_cid))

        transfer = Transfer(
            sender=self.platform,
            provider=self.platform,
            inputs=transfer_inputs,
            outputs=[refund_output],
            beneficiaries=None,
        )

        transfer_result = exercise_app_transfer(self.dso, app_transfer_context, transfer)

        refunded_holdings: list[ContractId[Holding]] = []
        for created_amulet: CreatedAmulet in transfer_result.created_amulets:
            refunded_holdings.append(created_amulet_to_holding(created_amulet))

        new_locked_holdings: list[tuple[Party, ContractId[LockedAmulet]]] = []
        for entry: tuple[Party, ContractId[LockedAmulet]] in current_locked_holdings:
            still_remaining = False
            for remaining_cid: ContractId[LockedAmulet] in remaining_locked_cids:
                if remaining_cid == entry[1]:
                    still_remaining = True
            if still_remaining:
                new_locked_holdings.append(entry)

        new_refunded_investors: list[Party] = []
        new_refunded_investors.append(investor)
        for existing: Party in current_refunded_investors:
            new_refunded_investors.append(existing)

        new_campaign = create(
            FundingCampaign(
                platform=self.platform,
                developer=self.developer,
                dso=self.dso,
                external_id=self.external_id,
                target=self.target,
                deadline=self.deadline,
                raised=self.raised,
                balance=self.balance - refunded_amount,
                status=self.status,
                accepted_instrument_id=self.accepted_instrument_id,
                terms=self.terms,
                investments=self.investments,
                excess_investments=self.excess_investments,
                excess_holdings=self.excess_holdings,
                locked_holdings=new_locked_holdings,
                unlocked_holdings=self.unlocked_holdings,
                refunded_investors=new_refunded_investors,
                loan_terms=self.loan_terms,
                finalized_at=self.finalized_at,
            )
        )

        return (new_campaign, refunded_holdings)

    @choice(controller=[investor, platform], consuming=True)
    def claim_excess(
        self, investor: Party, receiver: Party, app_transfer_context: AppTransferContext
    ) -> tuple[ContractId["FundingCampaign"], list[ContractId[Holding]]]:
        current_excess_investments = or_empty_party_amounts(self.excess_investments)
        current_excess_holdings = or_empty_locked_holdings(self.excess_holdings)

        investor_excess = Decimal(0)
        for entry: tuple[Party, Decimal] in current_excess_investments:
            if entry[0] == investor:
                investor_excess = entry[1]
        assert investor_excess > Decimal(0), "Investor has no excess to claim"

        investor_locked_cids: list[ContractId[LockedAmulet]] = []
        for entry: tuple[Party, ContractId[LockedAmulet]] in current_excess_holdings:
            if entry[0] == investor:
                investor_locked_cids.append(entry[1])
        assert len(investor_locked_cids) > 0, "Investor has no excess holdings"

        unlocked_amulet_cids: list[ContractId[Amulet]] = []
        returned_amount = Decimal(0)
        for locked_cid: ContractId[LockedAmulet] in investor_locked_cids:
            unlock_result = exercise(locked_cid, LockedAmulet_UnlockV2)
            amulet = fetch(unlock_result.amulet_cid)
            unlocked_amulet_cids.append(unlock_result.amulet_cid)
            returned_amount = returned_amount + amulet.amount.initial_amount

        return_output = TransferOutput(
            receiver=receiver,
            receiver_fee_ratio=Decimal(1),
            amount=returned_amount,
            lock=None,
        )

        transfer_inputs: list[TransferInput] = []
        for amulet_cid: ContractId[Amulet] in unlocked_amulet_cids:
            transfer_inputs.append(InputAmulet(amulet_cid))

        transfer = Transfer(
            sender=self.platform,
            provider=self.platform,
            inputs=transfer_inputs,
            outputs=[return_output],
            beneficiaries=None,
        )

        transfer_result = exercise_app_transfer(self.dso, app_transfer_context, transfer)

        returned_holdings: list[ContractId[Holding]] = []
        for created_amulet: CreatedAmulet in transfer_result.created_amulets:
            returned_holdings.append(created_amulet_to_holding(created_amulet))

        new_excess_holdings: list[tuple[Party, ContractId[LockedAmulet]]] = []
        for entry: tuple[Party, ContractId[LockedAmulet]] in current_excess_holdings:
            if entry[0] != investor:
                new_excess_holdings.append(entry)

        new_excess_investments: list[tuple[Party, Decimal]] = []
        for entry: tuple[Party, Decimal] in current_excess_investments:
            if entry[0] != investor:
                new_excess_investments.append(entry)

        new_campaign = create(
            FundingCampaign(
                platform=self.platform,
                developer=self.developer,
                dso=self.dso,
                external_id=self.external_id,
                target=self.target,
                deadline=self.deadline,
                raised=self.raised,
                balance=self.balance,
                status=self.status,
                accepted_instrument_id=self.accepted_instrument_id,
                terms=self.terms,
                investments=self.investments,
                excess_investments=new_excess_investments,
                excess_holdings=new_excess_holdings,
                locked_holdings=self.locked_holdings,
                unlocked_holdings=self.unlocked_holdings,
                refunded_investors=self.refunded_investors,
                loan_terms=self.loan_terms,
                finalized_at=self.finalized_at,
            )
        )

        return (new_campaign, returned_holdings)

    @choice(controller=platform, consuming=True)
    def pause(
        self, installment_cids: list[ContractId[InstallmentRelease]]
    ) -> tuple[ContractId["FundingCampaign"], list[ContractId[InstallmentRelease]]]:
        assert self.status == CampaignStatus.SUCCESSFUL, "Can only pause Successful campaigns"

        paused_installments: list[ContractId[InstallmentRelease]] = []
        for installment_cid: ContractId[InstallmentRelease] in installment_cids:
            installment_data = fetch(installment_cid)
            if installment_data.released or installment_data.paused:
                paused_installments.append(installment_cid)
            else:
                archive(installment_cid)
                paused_installments.append(
                    create(
                        InstallmentRelease(
                            platform=installment_data.platform,
                            developer=installment_data.developer,
                            dso=installment_data.dso,
                            external_id=installment_data.external_id,
                            installment_number=installment_data.installment_number,
                            amount=installment_data.amount,
                            release_date=installment_data.release_date,
                            released=installment_data.released,
                            escrowed=installment_data.escrowed,
                            platform_fees=installment_data.platform_fees,
                            holding_cids=installment_data.holding_cids,
                            paused=True,
                            loan_tracker_cid=installment_data.loan_tracker_cid,
                        )
                    )
                )

        new_campaign = create(
            FundingCampaign(
                platform=self.platform,
                developer=self.developer,
                dso=self.dso,
                external_id=self.external_id,
                target=self.target,
                deadline=self.deadline,
                raised=self.raised,
                balance=self.balance,
                status=CampaignStatus.PAUSED,
                accepted_instrument_id=self.accepted_instrument_id,
                terms=self.terms,
                investments=self.investments,
                excess_investments=self.excess_investments,
                excess_holdings=self.excess_holdings,
                locked_holdings=self.locked_holdings,
                unlocked_holdings=self.unlocked_holdings,
                refunded_investors=self.refunded_investors,
                loan_terms=self.loan_terms,
                finalized_at=self.finalized_at,
            )
        )

        return (new_campaign, paused_installments)

    @choice(controller=platform, consuming=True)
    def resume(
        self, installment_cids: list[ContractId[InstallmentRelease]]
    ) -> tuple[ContractId["FundingCampaign"], list[ContractId[InstallmentRelease]]]:
        assert self.status == CampaignStatus.PAUSED, "Campaign not paused"

        resumed_installments: list[ContractId[InstallmentRelease]] = []
        for installment_cid: ContractId[InstallmentRelease] in installment_cids:
            installment_data = fetch(installment_cid)
            if not installment_data.paused:
                resumed_installments.append(installment_cid)
            else:
                archive(installment_cid)
                resumed_installments.append(
                    create(
                        InstallmentRelease(
                            platform=installment_data.platform,
                            developer=installment_data.developer,
                            dso=installment_data.dso,
                            external_id=installment_data.external_id,
                            installment_number=installment_data.installment_number,
                            amount=installment_data.amount,
                            release_date=installment_data.release_date,
                            released=installment_data.released,
                            escrowed=installment_data.escrowed,
                            platform_fees=installment_data.platform_fees,
                            holding_cids=installment_data.holding_cids,
                            paused=False,
                            loan_tracker_cid=installment_data.loan_tracker_cid,
                        )
                    )
                )

        new_campaign = create(
            FundingCampaign(
                platform=self.platform,
                developer=self.developer,
                dso=self.dso,
                external_id=self.external_id,
                target=self.target,
                deadline=self.deadline,
                raised=self.raised,
                balance=self.balance,
                status=CampaignStatus.SUCCESSFUL,
                accepted_instrument_id=self.accepted_instrument_id,
                terms=self.terms,
                investments=self.investments,
                excess_investments=self.excess_investments,
                excess_holdings=self.excess_holdings,
                locked_holdings=self.locked_holdings,
                unlocked_holdings=self.unlocked_holdings,
                refunded_investors=self.refunded_investors,
                loan_terms=self.loan_terms,
                finalized_at=self.finalized_at,
            )
        )

        return (new_campaign, resumed_installments)

    @choice(controller=platform, consuming=False)
    def get_investments(self) -> list[tuple[Party, Decimal]]:
        return or_empty_party_amounts(self.investments)


@template
class InstallmentRelease:
    platform: Party
    developer: Party
    dso: Party
    external_id: str
    installment_number: int
    amount: Decimal
    release_date: Timestamp
    released: bool
    escrowed: bool
    platform_fees: Decimal
    holding_cids: list[ContractId[Holding]]
    paused: bool
    loan_tracker_cid: Optional[ContractId[LoanTracker]]

    signatory: list[Party] = [platform, developer]

    def __init__(
        self,
        platform: Party,
        developer: Party,
        dso: Party,
        external_id: str,
        installment_number: int,
        amount: Decimal,
        release_date: Timestamp,
        released: bool,
        escrowed: bool,
        platform_fees: Decimal,
        holding_cids: list[ContractId[Holding]],
        paused: bool,
        loan_tracker_cid: Optional[ContractId[LoanTracker]],
    ):
        assert amount > Decimal(0), "amount must be positive"
        assert installment_number > 0, "installment_number must be positive"
        assert platform_fees >= Decimal(0), "platform_fees must be non-negative"
        assert platform_fees <= Decimal(1), "platform_fees must not exceed 1"
        assert escrowed == (len(holding_cids) > 0), "escrowed must match whether holding_cids is non-empty"

        self.platform = platform
        self.developer = developer
        self.dso = dso
        self.external_id = external_id
        self.installment_number = installment_number
        self.amount = amount
        self.release_date = release_date
        self.released = released
        self.escrowed = escrowed
        self.platform_fees = platform_fees
        self.holding_cids = holding_cids
        self.paused = paused
        self.loan_tracker_cid = loan_tracker_cid

    @choice(controller=platform, consuming=True)
    def escrow(
        self, campaign_cid: ContractId[FundingCampaign]
    ) -> tuple[ContractId["InstallmentRelease"], ContractId[FundingCampaign]]:
        assert not self.paused, "Installment is paused"
        assert not self.escrowed, "Installment already escrowed"
        assert not self.released, "Cannot escrow released installment"

        campaign_data = fetch(campaign_cid)

        assert campaign_data.status == CampaignStatus.COMPLETED, "Campaign must be Completed"
        assert campaign_data.balance >= self.amount, "Campaign has insufficient balance"

        current_unlocked_holdings = or_empty_holdings(campaign_data.unlocked_holdings)
        just_holdings: list[ContractId[Holding]] = []
        for entry: tuple[Party, ContractId[Holding]] in current_unlocked_holdings:
            just_holdings.append(entry[1])
        num_holdings_needed = calculate_num_holdings_needed(current_unlocked_holdings, self.amount)

        escrowed_holdings: list[tuple[Party, ContractId[Holding]]] = []
        remaining_holdings: list[tuple[Party, ContractId[Holding]]] = []
        index = 0
        for entry: tuple[Party, ContractId[Holding]] in current_unlocked_holdings:
            if index < num_holdings_needed:
                escrowed_holdings.append(entry)
            else:
                remaining_holdings.append(entry)
            index = index + 1

        archive(campaign_cid)
        updated_campaign = create(
            FundingCampaign(
                platform=campaign_data.platform,
                developer=campaign_data.developer,
                dso=campaign_data.dso,
                external_id=campaign_data.external_id,
                target=campaign_data.target,
                deadline=campaign_data.deadline,
                raised=campaign_data.raised,
                balance=campaign_data.balance - self.amount,
                status=campaign_data.status,
                accepted_instrument_id=campaign_data.accepted_instrument_id,
                terms=campaign_data.terms,
                investments=campaign_data.investments,
                excess_investments=campaign_data.excess_investments,
                excess_holdings=campaign_data.excess_holdings,
                locked_holdings=campaign_data.locked_holdings,
                unlocked_holdings=remaining_holdings,
                refunded_investors=campaign_data.refunded_investors,
                loan_terms=campaign_data.loan_terms,
                finalized_at=campaign_data.finalized_at,
            )
        )

        escrowed_holding_cids: list[ContractId[Holding]] = []
        for entry: tuple[Party, ContractId[Holding]] in escrowed_holdings:
            escrowed_holding_cids.append(entry[1])

        updated_installment = create(
            InstallmentRelease(
                platform=self.platform,
                developer=self.developer,
                dso=self.dso,
                external_id=self.external_id,
                installment_number=self.installment_number,
                amount=self.amount,
                release_date=self.release_date,
                released=self.released,
                escrowed=True,
                platform_fees=self.platform_fees,
                holding_cids=escrowed_holding_cids,
                paused=self.paused,
                loan_tracker_cid=self.loan_tracker_cid,
            )
        )

        return (updated_installment, updated_campaign)

    @choice(controller=platform, consuming=True)
    def release(
        self, current_time: Timestamp, accept_before: Timestamp
    ) -> tuple[ContractId["InstallmentRelease"], ContractId[InstallmentTransfer], list[ContractId[Holding]]]:
        assert not self.paused, "installment is currently paused and cannot be released"
        assert current_time >= self.release_date, "release date not reached"
        assert not self.released, "installment has already been released"
        assert self.escrowed, "installment must be escrowed before release"
        assert len(self.holding_cids) > 0, "installment has no holdings to release"
        assert accept_before > current_time, "accept deadline must be after current time"

        if self.loan_tracker_cid != None:
            tracker_cid: ContractId[LoanTracker] = self.loan_tracker_cid
            if self.installment_number > 1:
                tracker_data = fetch(tracker_cid)
                assert (
                    tracker_data.loan_terms.loan_rewards != None or self.installment_number == 1
                ), "loan tracker state appears inconsistent"

                if tracker_data.loan_terms.loan_rewards != None:
                    rewards: LoanRewards = tracker_data.loan_terms.loan_rewards
                    required_period = self.installment_number - 1
                    paid_period_numbers: list[int] = []
                    for payment: PeriodPayment in rewards.period_payments:
                        if payment.status == PeriodPaymentStatus.PERIOD_PAID:
                            paid_period_numbers.append(payment.period_number)
                    required_period_paid = False
                    for paid_period: int in paid_period_numbers:
                        if paid_period == required_period:
                            required_period_paid = True
                    assert required_period_paid, "required period must be paid before releasing this installment"

        num_holdings = len(self.holding_cids)
        assert num_holdings > 0, "installment must have at least one holding"

        num_for_platform = floor(Decimal(num_holdings) * self.platform_fees)

        platform_holding_cids: list[ContractId[Holding]] = []
        developer_holding_cids: list[ContractId[Holding]] = []
        index = 0
        for holding_cid: ContractId[Holding] in self.holding_cids:
            if index < num_for_platform:
                platform_holding_cids.append(holding_cid)
            else:
                developer_holding_cids.append(holding_cid)
            index = index + 1

        assert len(developer_holding_cids) > 0, "developer must receive at least one holding"

        transfer_cid = create(
            InstallmentTransfer(
                platform=self.platform,
                developer=self.developer,
                dso=self.dso,
                external_id=self.external_id,
                installment_number=self.installment_number,
                amount=self.amount,
                status=TransferStatus.PENDING,
                accept_before=accept_before,
                holding_cids=developer_holding_cids,
            )
        )

        updated_installment = create(
            InstallmentRelease(
                platform=self.platform,
                developer=self.developer,
                dso=self.dso,
                external_id=self.external_id,
                installment_number=self.installment_number,
                amount=self.amount,
                release_date=self.release_date,
                released=True,
                escrowed=False,
                platform_fees=self.platform_fees,
                holding_cids=[],
                paused=self.paused,
                loan_tracker_cid=self.loan_tracker_cid,
            )
        )

        return (updated_installment, transfer_cid, platform_holding_cids)

    @choice(controller=platform, consuming=True)
    def pause_installment(self) -> ContractId["InstallmentRelease"]:
        assert not self.paused, "Installment already paused"
        assert not self.released, "Cannot pause released installment"
        return create(
            InstallmentRelease(
                platform=self.platform,
                developer=self.developer,
                dso=self.dso,
                external_id=self.external_id,
                installment_number=self.installment_number,
                amount=self.amount,
                release_date=self.release_date,
                released=self.released,
                escrowed=self.escrowed,
                platform_fees=self.platform_fees,
                holding_cids=self.holding_cids,
                paused=True,
                loan_tracker_cid=self.loan_tracker_cid,
            )
        )

    @choice(controller=platform, consuming=True)
    def resume_installment(self) -> ContractId["InstallmentRelease"]:
        assert self.paused, "Installment not paused"
        return create(
            InstallmentRelease(
                platform=self.platform,
                developer=self.developer,
                dso=self.dso,
                external_id=self.external_id,
                installment_number=self.installment_number,
                amount=self.amount,
                release_date=self.release_date,
                released=self.released,
                escrowed=self.escrowed,
                platform_fees=self.platform_fees,
                holding_cids=self.holding_cids,
                paused=False,
                loan_tracker_cid=self.loan_tracker_cid,
            )
        )


@template
class InstallmentTransfer:
    platform: Party
    developer: Party
    dso: Party
    external_id: str
    installment_number: int
    amount: Decimal
    status: TransferStatus
    accept_before: Timestamp
    holding_cids: list[ContractId[Holding]]

    signatory: list[Party] = [platform, developer]

    def __init__(
        self,
        platform: Party,
        developer: Party,
        dso: Party,
        external_id: str,
        installment_number: int,
        amount: Decimal,
        status: TransferStatus,
        accept_before: Timestamp,
        holding_cids: list[ContractId[Holding]],
    ):
        assert amount > Decimal(0), "amount must be positive"
        assert installment_number > 0, "installment_number must be positive"
        assert len(holding_cids) > 0, "holding_cids must not be empty"

        self.platform = platform
        self.developer = developer
        self.dso = dso
        self.external_id = external_id
        self.installment_number = installment_number
        self.amount = amount
        self.status = status
        self.accept_before = accept_before
        self.holding_cids = holding_cids

    @choice(controller=[developer, platform], consuming=True)
    def accept(
        self, current_time: Timestamp, app_transfer_context: AppTransferContext
    ) -> list[ContractId[Holding]]:
        assert self.status == TransferStatus.PENDING, "Transfer must be Pending"
        assert current_time < self.accept_before, "Accept deadline has passed"

        total_amount = Decimal(0)
        for holding_cid: ContractId[Holding] in self.holding_cids:
            amulet_cid: ContractId[Amulet] = from_interface_contract_id(holding_cid)
            amulet = fetch(amulet_cid)
            total_amount = total_amount + amulet.amount.initial_amount

        developer_output = TransferOutput(
            receiver=self.developer,
            receiver_fee_ratio=Decimal(1),
            amount=total_amount,
            lock=None,
        )

        transfer_inputs: list[TransferInput] = []
        for holding_cid: ContractId[Holding] in self.holding_cids:
            transfer_inputs.append(InputAmulet(from_interface_contract_id(holding_cid)))

        transfer = Transfer(
            sender=self.platform,
            provider=self.platform,
            inputs=transfer_inputs,
            outputs=[developer_output],
            beneficiaries=None,
        )

        transfer_result = exercise_app_transfer(self.dso, app_transfer_context, transfer)

        new_holdings: list[ContractId[Holding]] = []
        for created_amulet: CreatedAmulet in transfer_result.created_amulets:
            new_holdings.append(created_amulet_to_holding(created_amulet))
        return new_holdings

    @choice(controller=developer, consuming=True)
    def reject(self) -> None:
        assert self.status == TransferStatus.PENDING, "Transfer must be Pending"

    @choice(controller=platform, consuming=True)
    def withdraw(self, current_time: Timestamp) -> None:
        assert self.status == TransferStatus.PENDING, "Transfer must be Pending"
        assert current_time >= self.accept_before, "Cannot withdraw before deadline"
