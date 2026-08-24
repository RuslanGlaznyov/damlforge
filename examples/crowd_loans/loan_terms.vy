from forge.models import ContractId, Decimal, Optional, Party, Text, Timestamp, choice, ledger_effect
from Splice.Amulet import Amulet
from Splice.AmuletRules import (
    AppTransferContext,
    CreatedAmulet,
    InputAmulet,
    Transfer,
    TransferInput,
    TransferOutput,
    created_amulet_to_holding,
    exercise_app_transfer,
)
from Splice.Api.Token.HoldingV1 import Holding, InstrumentId

struct RepaymentMilestone:
    due_date: Timestamp
    amount: Decimal
    paid: bool
    paid_date: Optional[Timestamp]


struct RepaymentSchedule:
    milestones: list[RepaymentMilestone]


flag PeriodPaymentStatus:
    PERIOD_PENDING
    PERIOD_PAID


struct PeriodPayment:
    period_number: int
    amount: Decimal
    status: PeriodPaymentStatus
    paid_date: Optional[Timestamp]


struct LoanRewards:
    multiplier: Decimal
    repayment_schedule: RepaymentSchedule
    number_of_periods: int
    period_payments: list[PeriodPayment]


struct PerformanceRewards:
    interest_rate: Decimal
    interest_len_months: Decimal


struct LoanTerms:
    loan_rewards: Optional[LoanRewards]
    performance_rewards: Optional[PerformanceRewards]


struct RepaymentDistribution:
    investor: Party
    amount: Decimal
    distributed_at: Timestamp


flag RepaymentClaimStatus:
    CLAIM_PENDING
    CLAIM_ACCEPTED
    CLAIM_EXPIRED


struct RepaymentClaimView:
    platform: Party
    developer: Party
    investor: Party
    dso: Party
    campaign_external_id: Text
    amount: Decimal
    status: RepaymentClaimStatus
    claim_before: Timestamp


struct LoanTrackerView:
    platform: Party
    developer: Party
    dso: Party
    campaign_external_id: Text
    loan_terms: LoanTerms
    total_repaid: Decimal
    balance: Decimal


def update_milestone_if_due(paid_amount: Decimal, milestone: RepaymentMilestone) -> RepaymentMilestone:
    if milestone.paid or paid_amount < milestone.amount:
        return milestone
    return RepaymentMilestone(
        due_date=milestone.due_date,
        amount=milestone.amount,
        paid=True,
        paid_date=milestone.paid_date,
    )


def update_milestones(paid_amount: Decimal, milestones: list[RepaymentMilestone]) -> list[RepaymentMilestone]:
    updated: list[RepaymentMilestone] = []
    for milestone: RepaymentMilestone in milestones:
        updated.append(update_milestone_if_due(paid_amount, milestone))
    return updated


@ledger_effect
def verify_amulets(dso_party: Party, amulets: list[ContractId[Amulet]]) -> Decimal:
    total = Decimal(0)
    for amulet_cid: ContractId[Amulet] in amulets:
        amulet = fetch(amulet_cid)
        assert amulet.dso == dso_party, "Amulet DSO must match"
        total = total + amulet.amount.initial_amount
    return total


def calculate_num_holdings_for_amount(holdings: list[ContractId[Holding]], amount: Decimal) -> int:
    return len(holdings)


def investment_parties(investments: list[tuple[Party, Decimal]]) -> list[Party]:
    parties: list[Party] = []
    for entry: tuple[Party, Decimal] in investments:
        parties.append(entry[0])
    return parties


def next_period_number(period_payments: list[PeriodPayment]) -> int:
    paid_count = 0
    for payment: PeriodPayment in period_payments:
        if payment.status == PeriodPaymentStatus.PERIOD_PAID:
            paid_count = paid_count + 1
    return paid_count + 1


def already_paid_periods(period_payments: list[PeriodPayment]) -> list[int]:
    paid_periods: list[int] = []
    for payment: PeriodPayment in period_payments:
        if payment.status == PeriodPaymentStatus.PERIOD_PAID:
            paid_periods.append(payment.period_number)
    return paid_periods


template LoanTracker:
    platform: Party
    developer: Party
    dso: Party
    campaign_external_id: Text
    loan_terms: LoanTerms
    total_repaid: Decimal
    repayment_history: list[RepaymentDistribution]
    investments: list[tuple[Party, Decimal]]
    total_raised: Decimal
    balance: Decimal
    holding_cids: list[ContractId[Holding]]

    signatory: list[Party] = [platform, developer]
    observer: list[Party] = investment_parties(investments)

    @choice(controller=[platform, developer], consuming=True)
    def deposit(
        self,
        inputs: list[ContractId[Amulet]],
        amount: Decimal,
        app_transfer_context: AppTransferContext,
    ) -> ContractId["LoanTracker"]:
        assert amount > Decimal(0), "Deposit amount must be positive"

        input_amount = verify_amulets(LoanTracker.dso, inputs)
        assert input_amount >= amount, "Insufficient funds for deposit"

        platform_output = TransferOutput(
            receiver=LoanTracker.platform,
            receiver_fee_ratio=Decimal(0),
            amount=amount,
            lock=None,
        )

        transfer_inputs: list[TransferInput] = []
        for input_cid: ContractId[Amulet] in inputs:
            transfer_inputs.append(InputAmulet(input_cid))

        transfer = Transfer(
            sender=LoanTracker.developer,
            provider=LoanTracker.platform,
            inputs=transfer_inputs,
            outputs=[platform_output],
            beneficiaries=None,
        )

        transfer_result = exercise_app_transfer(LoanTracker.dso, app_transfer_context, transfer)

        new_holdings: list[ContractId[Holding]] = []
        for created_amulet: CreatedAmulet in transfer_result.created_amulets:
            new_holdings.append(created_amulet_to_holding(created_amulet))

        combined_holdings: list[ContractId[Holding]] = []
        for existing_holding: ContractId[Holding] in LoanTracker.holding_cids:
            combined_holdings.append(existing_holding)
        for new_holding: ContractId[Holding] in new_holdings:
            combined_holdings.append(new_holding)

        return create(
            LoanTracker(
                platform=LoanTracker.platform,
                developer=LoanTracker.developer,
                dso=LoanTracker.dso,
                campaign_external_id=LoanTracker.campaign_external_id,
                loan_terms=LoanTracker.loan_terms,
                total_repaid=LoanTracker.total_repaid,
                repayment_history=LoanTracker.repayment_history,
                investments=LoanTracker.investments,
                total_raised=LoanTracker.total_raised,
                balance=LoanTracker.balance + amount,
                holding_cids=combined_holdings,
            )
        )

    @choice(controller=platform, consuming=True)
    def repay(
        self, repay_amount: Decimal, current_time: Timestamp, claim_before: Timestamp
    ) -> tuple[ContractId["LoanTracker"], list[ContractId[RepaymentClaim]]]:
        assert repay_amount > Decimal(0), "Repayment amount must be positive"
        assert len(LoanTracker.investments) > 0, "Must have investors to distribute to"
        assert claim_before > current_time, "Claim deadline must be in the future"
        assert LoanTracker.balance >= repay_amount, "Insufficient balance for repayment"
        assert len(LoanTracker.holding_cids) > 0, "No holdings available for repayment"

        num_holdings_needed = calculate_num_holdings_for_amount(LoanTracker.holding_cids, repay_amount)
        repayment_holdings: list[ContractId[Holding]] = []
        remaining_holdings: list[ContractId[Holding]] = []
        index = 0
        for holding_cid: ContractId[Holding] in LoanTracker.holding_cids:
            if index < num_holdings_needed:
                repayment_holdings.append(holding_cid)
            else:
                remaining_holdings.append(holding_cid)
            index = index + 1

        claim_cids: list[ContractId[RepaymentClaim]] = []
        new_distributions: list[RepaymentDistribution] = []
        for entry: tuple[Party, Decimal] in LoanTracker.investments:
            investor: Party = entry[0]
            invested_amount: Decimal = entry[1]
            share = invested_amount / LoanTracker.total_raised
            distribution_amount = repay_amount * share

            claim_cid = create(
                RepaymentClaim(
                    platform=LoanTracker.platform,
                    developer=LoanTracker.developer,
                    investor=investor,
                    dso=LoanTracker.dso,
                    campaign_external_id=LoanTracker.campaign_external_id,
                    amount=distribution_amount,
                    status=RepaymentClaimStatus.CLAIM_PENDING,
                    claim_before=claim_before,
                    holding_cids=repayment_holdings,
                )
            )
            claim_cids.append(claim_cid)
            new_distributions.append(
                RepaymentDistribution(
                    investor=investor,
                    amount=distribution_amount,
                    distributed_at=current_time,
                )
            )

        updated_loan_terms = LoanTracker.loan_terms
        if LoanTracker.loan_terms.loan_rewards != None:
            rewards: LoanRewards = LoanTracker.loan_terms.loan_rewards
            updated_milestones = update_milestones(repay_amount, rewards.repayment_schedule.milestones)
            updated_schedule = RepaymentSchedule(milestones=updated_milestones)
            updated_rewards = LoanRewards(
                multiplier=rewards.multiplier,
                repayment_schedule=updated_schedule,
                number_of_periods=rewards.number_of_periods,
                period_payments=rewards.period_payments,
            )
            updated_loan_terms = LoanTerms(
                loan_rewards=updated_rewards,
                performance_rewards=LoanTracker.loan_terms.performance_rewards,
            )

        combined_history: list[RepaymentDistribution] = []
        for existing_distribution: RepaymentDistribution in LoanTracker.repayment_history:
            combined_history.append(existing_distribution)
        for new_distribution: RepaymentDistribution in new_distributions:
            combined_history.append(new_distribution)

        new_tracker = create(
            LoanTracker(
                platform=LoanTracker.platform,
                developer=LoanTracker.developer,
                dso=LoanTracker.dso,
                campaign_external_id=LoanTracker.campaign_external_id,
                loan_terms=updated_loan_terms,
                total_repaid=LoanTracker.total_repaid + repay_amount,
                repayment_history=combined_history,
                investments=LoanTracker.investments,
                total_raised=LoanTracker.total_raised,
                balance=LoanTracker.balance - repay_amount,
                holding_cids=remaining_holdings,
            )
        )

        return (new_tracker, claim_cids)

    @choice(controller=platform, consuming=False)
    def check_default(self, current_time: Timestamp) -> bool:
        if LoanTracker.loan_terms.loan_rewards == None:
            return False

        rewards: LoanRewards = LoanTracker.loan_terms.loan_rewards
        for milestone: RepaymentMilestone in rewards.repayment_schedule.milestones:
            if not milestone.paid and current_time > milestone.due_date:
                return True
        return False

    @choice(controller=platform, consuming=True)
    def loan_rewards_repay(
        self, repay_amount: Decimal, current_time: Timestamp, claim_before: Timestamp
    ) -> tuple[ContractId["LoanTracker"], list[ContractId[RepaymentClaim]]]:
        assert repay_amount > Decimal(0), "Repayment amount must be positive"
        assert len(LoanTracker.investments) > 0, "Must have investors to distribute to"
        assert claim_before > current_time, "Claim deadline must be in the future"
        assert LoanTracker.balance >= repay_amount, "Insufficient balance for repayment"
        assert len(LoanTracker.holding_cids) > 0, "No holdings available for repayment"
        assert LoanTracker.loan_terms.loan_rewards != None, "No loan rewards defined"

        rewards: LoanRewards = LoanTracker.loan_terms.loan_rewards
        assert rewards.multiplier > Decimal(0), "Multiplier must be positive"
        assert rewards.number_of_periods > 0, "Number of periods must be positive"
        assert LoanTracker.total_raised > Decimal(0), "Total raised must be positive"

        total_to_repay = LoanTracker.total_raised * rewards.multiplier
        assert total_to_repay > Decimal(0) and total_to_repay < Decimal(1000000000), (
            "Total repayment amount overflow - multiplier too large"
        )

        amount_per_period = total_to_repay / Decimal(rewards.number_of_periods)
        assert amount_per_period > Decimal(0), "Period amount must be positive"

        next_period = next_period_number(rewards.period_payments)
        assert next_period <= rewards.number_of_periods, "All periods already paid"
        assert repay_amount >= amount_per_period, "Payment amount must be at least the period amount"

        num_holdings_needed = calculate_num_holdings_for_amount(LoanTracker.holding_cids, amount_per_period)
        assert num_holdings_needed <= len(LoanTracker.holding_cids), "Not enough holdings"

        repayment_holdings: list[ContractId[Holding]] = []
        remaining_holdings: list[ContractId[Holding]] = []
        index = 0
        for holding_cid: ContractId[Holding] in LoanTracker.holding_cids:
            if index < num_holdings_needed:
                repayment_holdings.append(holding_cid)
            else:
                remaining_holdings.append(holding_cid)
            index = index + 1

        claim_cids: list[ContractId[RepaymentClaim]] = []
        new_distributions: list[RepaymentDistribution] = []
        total_distributed = Decimal(0)
        for entry: tuple[Party, Decimal] in LoanTracker.investments:
            investor: Party = entry[0]
            invested_amount: Decimal = entry[1]
            share = invested_amount / LoanTracker.total_raised
            distribution_amount = amount_per_period * share
            total_distributed = total_distributed + distribution_amount

            claim_cid = create(
                RepaymentClaim(
                    platform=LoanTracker.platform,
                    developer=LoanTracker.developer,
                    investor=investor,
                    dso=LoanTracker.dso,
                    campaign_external_id=LoanTracker.campaign_external_id,
                    amount=distribution_amount,
                    status=RepaymentClaimStatus.CLAIM_PENDING,
                    claim_before=claim_before,
                    holding_cids=repayment_holdings,
                )
            )
            claim_cids.append(claim_cid)
            new_distributions.append(
                RepaymentDistribution(
                    investor=investor,
                    amount=distribution_amount,
                    distributed_at=current_time,
                )
            )

        distribution_error = total_distributed - amount_per_period
        if distribution_error < Decimal(0):
            distribution_error = Decimal(0) - distribution_error
        assert distribution_error < Decimal("0.01"), "Distribution total must equal period amount"

        new_period_payment = PeriodPayment(
            period_number=next_period,
            amount=amount_per_period,
            status=PeriodPaymentStatus.PERIOD_PAID,
            paid_date=current_time,
        )

        updated_period_payments: list[PeriodPayment] = []
        for payment: PeriodPayment in rewards.period_payments:
            updated_period_payments.append(payment)
        updated_period_payments.append(new_period_payment)

        updated_rewards = LoanRewards(
            multiplier=rewards.multiplier,
            repayment_schedule=rewards.repayment_schedule,
            number_of_periods=rewards.number_of_periods,
            period_payments=updated_period_payments,
        )
        updated_loan_terms = LoanTerms(
            loan_rewards=updated_rewards,
            performance_rewards=LoanTracker.loan_terms.performance_rewards,
        )

        combined_history: list[RepaymentDistribution] = []
        for existing_distribution: RepaymentDistribution in LoanTracker.repayment_history:
            combined_history.append(existing_distribution)
        for new_distribution: RepaymentDistribution in new_distributions:
            combined_history.append(new_distribution)

        new_tracker = create(
            LoanTracker(
                platform=LoanTracker.platform,
                developer=LoanTracker.developer,
                dso=LoanTracker.dso,
                campaign_external_id=LoanTracker.campaign_external_id,
                loan_terms=updated_loan_terms,
                total_repaid=LoanTracker.total_repaid + amount_per_period,
                repayment_history=combined_history,
                investments=LoanTracker.investments,
                total_raised=LoanTracker.total_raised,
                balance=LoanTracker.balance - amount_per_period,
                holding_cids=remaining_holdings,
            )
        )

        return (new_tracker, claim_cids)

    @choice(controller=platform, consuming=False)
    def get_loan_rewards_schedule(self) -> list[PeriodPayment]:
        if LoanTracker.loan_terms.loan_rewards == None:
            return []

        rewards: LoanRewards = LoanTracker.loan_terms.loan_rewards
        existing_payments = rewards.period_payments
        existing_periods = already_paid_periods(existing_payments)
        total_to_repay = LoanTracker.total_raised * rewards.multiplier
        amount_per_period = total_to_repay / Decimal(rewards.number_of_periods)

        pending_payments: list[PeriodPayment] = []
        period_num = 1
        while_bound = rewards.number_of_periods
        for _index: int in range(0, while_bound):
            period_num = _index + 1
            already_exists = False
            for existing_period: int in existing_periods:
                if existing_period == period_num:
                    already_exists = True
            if not already_exists:
                pending_payments.append(
                    PeriodPayment(
                        period_number=period_num,
                        amount=amount_per_period,
                        status=PeriodPaymentStatus.PERIOD_PENDING,
                        paid_date=None,
                    )
                )

        combined: list[PeriodPayment] = []
        for existing_payment: PeriodPayment in existing_payments:
            combined.append(existing_payment)
        for pending_payment: PeriodPayment in pending_payments:
            combined.append(pending_payment)
        return combined

    @choice(controller=platform, consuming=False)
    def get_loan_rewards_history(self) -> list[PeriodPayment]:
        if LoanTracker.loan_terms.loan_rewards == None:
            return []
        rewards: LoanRewards = LoanTracker.loan_terms.loan_rewards
        return rewards.period_payments


template RepaymentClaim:
    platform: Party
    developer: Party
    investor: Party
    dso: Party
    campaign_external_id: Text
    amount: Decimal
    status: RepaymentClaimStatus
    claim_before: Timestamp
    holding_cids: list[ContractId[Holding]]

    signatory: list[Party] = [platform, developer]
    observer: list[Party] = [investor]

    def __init__(
        self,
        platform: Party,
        developer: Party,
        investor: Party,
        dso: Party,
        campaign_external_id: Text,
        amount: Decimal,
        status: RepaymentClaimStatus,
        claim_before: Timestamp,
        holding_cids: list[ContractId[Holding]],
    ):
        assert amount > Decimal(0), "amount must be positive"
        assert len(holding_cids) > 0, "holding_cids must not be empty"
        self.platform = platform
        self.developer = developer
        self.investor = investor
        self.dso = dso
        self.campaign_external_id = campaign_external_id
        self.amount = amount
        self.status = status
        self.claim_before = claim_before
        self.holding_cids = holding_cids

    @choice(controller=[investor, platform], consuming=True)
    def accept(
        self, current_time: Timestamp, app_transfer_context: AppTransferContext
    ) -> list[ContractId[Holding]]:
        assert RepaymentClaim.status == RepaymentClaimStatus.CLAIM_PENDING, "Claim must be Pending"
        assert current_time < RepaymentClaim.claim_before, "Claim deadline has passed"

        total_amount = Decimal(0)
        for holding_cid: ContractId[Holding] in RepaymentClaim.holding_cids:
            amulet_cid = from_interface_contract_id(holding_cid)
            amulet = fetch(amulet_cid)
            total_amount = total_amount + amulet.amount.initial_amount

        investor_output = TransferOutput(
            receiver=RepaymentClaim.investor,
            receiver_fee_ratio=Decimal(1),
            amount=total_amount,
            lock=None,
        )

        transfer_inputs: list[TransferInput] = []
        for holding_cid: ContractId[Holding] in RepaymentClaim.holding_cids:
            transfer_inputs.append(InputAmulet(from_interface_contract_id(holding_cid)))

        transfer = Transfer(
            sender=RepaymentClaim.platform,
            provider=RepaymentClaim.platform,
            inputs=transfer_inputs,
            outputs=[investor_output],
            beneficiaries=None,
        )

        transfer_result = exercise_app_transfer(RepaymentClaim.dso, app_transfer_context, transfer)

        new_holdings: list[ContractId[Holding]] = []
        for created_amulet: CreatedAmulet in transfer_result.created_amulets:
            new_holdings.append(created_amulet_to_holding(created_amulet))
        return new_holdings

    @choice(controller=platform, consuming=True)
    def expire(self, current_time: Timestamp) -> None:
        assert RepaymentClaim.status == RepaymentClaimStatus.CLAIM_PENDING, "Claim must be Pending"
        assert current_time >= RepaymentClaim.claim_before, "Cannot expire before deadline"
