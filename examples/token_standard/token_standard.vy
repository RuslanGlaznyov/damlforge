from datetime import datetime

from forge.models import ContractId, Decimal, Optional, Party, TextMap, choice, view, template
from forge.builtins.daml_lang import create, to_interface_contract_id

struct InstrumentId:
    admin: Party
    id: str


struct Metadata:
    values: TextMap[str]


struct ExtraArgs:
    context: str
    meta: Metadata


struct Lock:
    holders: list[Party]
    expires_at: Optional[datetime]


struct HoldingView:
    owner: Party
    instrument_id: InstrumentId
    amount: Decimal
    lock: Optional[Lock]
    meta: Metadata


interface Holding(view=HoldingView):
    pass


struct Transfer:
    sender: Party
    receiver: Party
    amount: Decimal
    instrument_id: InstrumentId
    execute_before: datetime
    meta: Metadata


struct TransferInstructionView:
    transfer: Transfer
    status: str


struct TransferInstructionResult:
    output_cid: Optional[ContractId[Holding]]
    sender_change_cid: Optional[ContractId[Holding]]


interface TransferInstruction(view=TransferInstructionView):

    @choice(controller=actors, consuming="nonconsuming")
    def transfer_instruction_accept(self, actors: list[Party], extra_args: ExtraArgs) -> TransferInstructionResult:
        pass

    @choice(controller=actors, consuming="nonconsuming")
    def transfer_instruction_reject(self, actors: list[Party], extra_args: ExtraArgs) -> TransferInstructionResult:
        pass

    @choice(controller=actors, consuming="nonconsuming")
    def transfer_instruction_withdraw(self, actors: list[Party], extra_args: ExtraArgs) -> TransferInstructionResult:
        pass


@template
class SimpleHolding(Holding):
    owner: Party
    issuer: Party
    amount: Decimal
    instrument_id: InstrumentId

    signatory: list[Party] = [owner, issuer]

    @view
    def get_view(self) -> HoldingView:
        return HoldingView(
            owner=self.owner,
            instrument_id=self.instrument_id,
            amount=self.amount,
            lock=None,
            meta=Metadata(values={}),
        )


@template
class PendingTransfer(TransferInstruction):
    sender: Party
    receiver: Party
    amount: Decimal
    instrument_id: InstrumentId
    execute_before: datetime

    signatory: list[Party] = [sender]
    observer: list[Party] = [receiver]

    @view
    def get_view(self) -> TransferInstructionView:
        return TransferInstructionView(
            transfer=Transfer(
                sender=self.sender,
                receiver=self.receiver,
                amount=self.amount,
                instrument_id=self.instrument_id,
                execute_before=self.execute_before,
                meta=Metadata(values={}),
            ),
            status="pending",
        )

    @choice(controller=receiver, consuming=True)
    def accept(self, extra_args: ExtraArgs) -> ContractId[SimpleHolding]:
        assert self.amount > Decimal(0), "transfer amount must be positive"
        assert extra_args.context != "", "accept requires a non-empty choice context"
        return create(
            SimpleHolding(
                owner=self.receiver,
                issuer=self.sender,
                amount=self.amount,
                instrument_id=self.instrument_id,
            )
        )

    @choice(controller=sender, consuming=True)
    def withdraw(self, extra_args: ExtraArgs) -> str:
        assert extra_args.context != "", "withdraw requires a reason in the choice context"
        return extra_args.context

    @choice(controller=actors, consuming="nonconsuming", observer=self.sender)
    def transfer_instruction_accept(self, actors: list[Party], extra_args: ExtraArgs) -> TransferInstructionResult:
        assert self.amount > Decimal(0), "transfer amount must be positive"
        assert extra_args.context != "", "accept requires a non-empty choice context"
        holding_cid = create(
            SimpleHolding(
                owner=self.receiver,
                issuer=self.sender,
                amount=self.amount,
                instrument_id=self.instrument_id,
            )
        )
        return TransferInstructionResult(
            output_cid=to_interface_contract_id(holding_cid),
            sender_change_cid=None,
        )

    @choice(controller=actors, consuming="nonconsuming")
    def transfer_instruction_reject(self, actors: list[Party], extra_args: ExtraArgs) -> TransferInstructionResult:
        assert self.sender not in actors, "sender should withdraw, not reject, their own transfer"
        return TransferInstructionResult(output_cid=None, sender_change_cid=None)

    @choice(controller=actors, consuming="nonconsuming")
    def transfer_instruction_withdraw(self, actors: list[Party], extra_args: ExtraArgs) -> TransferInstructionResult:
        assert extra_args.context != "", "withdraw requires a reason in the choice context"
        return TransferInstructionResult(output_cid=None, sender_change_cid=None)
