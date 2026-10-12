from forge.models import ContractId, ledger_effect, Party, template
from forge.builtins import DamlName
from Splice.Api.Token.HoldingV2 import Account, HoldingView, InstrumentId


@template
class Token:
    holding: HoldingView

    signatory: list[Party] = [holding.instrument_id.admin]


@ledger_effect
@DamlName("fetchAndArchiveLockedToken")
def fetch_and_archive_locked_token(expected_instrument_id: InstrumentId, expected_owner: Account, token_cid: ContractId[Token]) -> Token:
    pass


@ledger_effect
@DamlName("fetchAndArchiveUnlockedToken")
def fetch_and_archive_unlocked_token(expected_instrument_id: InstrumentId, expected_owner: Account, token_cid: ContractId[Token]) -> Token:
    pass
