from forge.models import ContractId, Party, template
from forge.builtins import DamlName
from Splice.Api.Token.HoldingV2 import Account, HoldingView, InstrumentId


@template
class Token:
    holding: HoldingView

    signatory: list[Party] = [holding.instrument_id.admin]


@DamlName("fetchAndArchiveLockedToken", is_ledger_effect=True)
def fetch_and_archive_locked_token(expected_instrument_id: InstrumentId, expected_owner: Account, token_cid: ContractId[Token]) -> Token:
    pass


@DamlName("fetchAndArchiveUnlockedToken", is_ledger_effect=True)
def fetch_and_archive_unlocked_token(expected_instrument_id: InstrumentId, expected_owner: Account, token_cid: ContractId[Token]) -> Token:
    pass
