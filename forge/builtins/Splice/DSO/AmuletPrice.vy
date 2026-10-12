from datetime import datetime
from typing import Annotated

from forge.models import ContractId, Decimal, ledger_effect, Optional, Party, template
from forge.builtins import DamlName


@template
class AmuletPriceVote:
    dso: Party
    sv: Party
    amulet_price: Annotated[Optional[Decimal], DamlName("amuletPrice")]
    last_updated_at: Annotated[datetime, DamlName("lastUpdatedAt")]

    signatory: list[Party] = [dso]


@ledger_effect
@DamlName("fetchMedianAmuletPrice")
def fetch_median_amulet_price(party: Party, svs: list[Party], vote_cids: list[ContractId[AmuletPriceVote]]) -> Decimal:
    pass


def median(list_value: list[Decimal]) -> Decimal:
    pass
