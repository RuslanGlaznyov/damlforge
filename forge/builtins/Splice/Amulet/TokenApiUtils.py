from forge.builtins import DamlName
from forge.models.types import Party, Text
from ..Api.Token.HoldingV1 import InstrumentId as InstrumentIdV1
from ..Api.Token.HoldingV2 import InstrumentId as InstrumentIdV2


@DamlName("amuletInstrumentId")
def amulet_instrument_id(dso: Party) -> InstrumentIdV1:
    raise NotImplementedError


@DamlName("amuletInstrumentIdV2")
def amulet_instrument_id_v2(dso: Party) -> InstrumentIdV2:
    raise NotImplementedError


@DamlName("amuletInstrumentIdName")
def amulet_instrument_id_name() -> Text:
    raise NotImplementedError
