from forge.models import ContractId, Decimal, Optional, Party, Text, TextMap, Timestamp, choice, view

struct InstrumentId:
    admin: Party
    id: Text


struct Metadata:
    values: TextMap[Text]


struct ExtraArgs:
    context: Text
    meta: Metadata


struct Lock:
    holders: list[Party]
    expires_at: Optional[Timestamp]


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
    execute_before: Timestamp
    meta: Metadata


struct TransferInstructionView:
    transfer: Transfer
    status: Text


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


template SimpleHolding:
    owner: Party
    issuer: Party
    amount: Decimal
    instrument_id: InstrumentId

    signatory: list[Party] = [owner, issuer]


instance SimpleHoldingAsHolding(Holding):
    template = SimpleHolding

    @view
    def get_view(self) -> HoldingView:
        return HoldingView(
            owner=SimpleHolding.owner,
            instrument_id=SimpleHolding.instrument_id,
            amount=SimpleHolding.amount,
            lock=None,
            meta=Metadata(values={}),
        )


template PendingTransfer:
    sender: Party
    receiver: Party
    amount: Decimal
    instrument_id: InstrumentId

    signatory: list[Party] = [sender]
    observer: list[Party] = [receiver]

    @choice(controller=receiver, consuming=True)
    def accept(self, extra_args: ExtraArgs) -> ContractId[SimpleHolding]:
        assert PendingTransfer.amount > Decimal(0), "transfer amount must be positive"
        assert extra_args.context != "", "accept requires a non-empty choice context"
        return create(
            SimpleHolding(
                owner=PendingTransfer.receiver,
                issuer=PendingTransfer.sender,
                amount=PendingTransfer.amount,
                instrument_id=PendingTransfer.instrument_id,
            )
        )

    @choice(controller=sender, consuming=True)
    def withdraw(self, extra_args: ExtraArgs) -> Text:
        assert extra_args.context != "", "withdraw requires a reason in the choice context"
        return extra_args.context


instance PendingTransferAsTransferInstruction(TransferInstruction):
    template = PendingTransfer

    @choice(controller=actors, consuming="nonconsuming", observer=PendingTransfer.sender)
    def transfer_instruction_accept(self, actors: list[Party], extra_args: ExtraArgs) -> TransferInstructionResult:
        return TransferInstructionResult(
            output_cid=exercise(self, PendingTransfer.accept, extra_args=extra_args),
            sender_change_cid=None,
        )

    @choice(controller=actors, consuming="nonconsuming")
    def transfer_instruction_reject(self, actors: list[Party], extra_args: ExtraArgs) -> TransferInstructionResult:
        assert PendingTransfer.sender not in actors, "sender should withdraw, not reject, their own transfer"
        archive(self)
        return TransferInstructionResult(output_cid=None, sender_change_cid=None)

    @choice(controller=actors, consuming="nonconsuming")
    def transfer_instruction_withdraw(self, actors: list[Party], extra_args: ExtraArgs) -> TransferInstructionResult:
        exercise(self, PendingTransfer.withdraw, extra_args=extra_args)
        return TransferInstructionResult(output_cid=None, sender_change_cid=None)
