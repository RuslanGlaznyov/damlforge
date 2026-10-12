from datetime import datetime, timedelta
from typing import Annotated

from forge.models import Decimal, Optional, Party
from forge.builtins import DamlName
from Splice.Api.Token.MetadataV1 import Metadata


struct HoldingView:
    owner: Party
    instrument_id: Annotated[InstrumentId, DamlName("instrumentId")]
    amount: Decimal
    lock: Optional[Lock]
    meta: Metadata


struct Lock:
    holders: list[Party]
    expires_at: Annotated[Optional[datetime], DamlName("expiresAt")]
    expires_after: Annotated[Optional[timedelta], DamlName("expiresAfter")]
    context: Optional[str]


struct InstrumentId:
    admin: Party
    id: str


interface Holding(view=HoldingView):
    pass
