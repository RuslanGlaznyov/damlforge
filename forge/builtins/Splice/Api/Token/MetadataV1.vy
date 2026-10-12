from datetime import date, datetime, timedelta

from forge.models import ContractId, Decimal, Optional, Party, TextMap, variant
from forge.builtins import DamlCaseAccessor, DamlName, no_derive


AnyContractId = ContractId[AnyContract]


struct ChoiceExecutionMetadata:
    meta: Metadata


struct ExtraArgs:
    context: ChoiceContext
    meta: Metadata


struct Metadata:
    values: TextMap[str]


struct ChoiceContext:
    values: TextMap[AnyValue]


@no_derive
struct AnyContractView:
    pass


@variant
class AnyValue:
    def AV_Text(value: str): pass
    def AV_Int(value: int): pass
    def AV_Decimal(value: Decimal): pass
    def AV_Bool(value: bool): pass
    def AV_Date(value: date): pass
    def AV_Time(value: datetime): pass
    def AV_RelTime(value: timedelta): pass
    def AV_Party(value: Party): pass
    def AV_ContractId(value: ContractId[AnyContract]): pass
    def AV_List(value: list[AnyValue]): pass
    def AV_Map(value: TextMap[AnyValue]): pass


interface AnyContract(view=AnyContractView):
    pass


@DamlCaseAccessor("AV_Text")
def av_text(value: AnyValue) -> Optional[str]:
    pass


@DamlCaseAccessor("AV_Int")
def av_int(value: AnyValue) -> Optional[int]:
    pass


@DamlCaseAccessor("AV_Decimal")
def av_decimal(value: AnyValue) -> Optional[Decimal]:
    pass


@DamlCaseAccessor("AV_Bool")
def av_bool(value: AnyValue) -> Optional[bool]:
    pass


@DamlCaseAccessor("AV_Date")
def av_date(value: AnyValue) -> Optional[date]:
    pass


@DamlCaseAccessor("AV_Time")
def av_time(value: AnyValue) -> Optional[datetime]:
    pass


@DamlCaseAccessor("AV_RelTime")
def av_rel_time(value: AnyValue) -> Optional[timedelta]:
    pass


@DamlCaseAccessor("AV_Party")
def av_party(value: AnyValue) -> Optional[Party]:
    pass


@DamlCaseAccessor("AV_ContractId")
def av_contract_id(value: AnyValue) -> Optional[ContractId[AnyContract]]:
    pass


@DamlCaseAccessor("AV_List")
def av_list(value: AnyValue) -> Optional[list[AnyValue]]:
    pass


@DamlCaseAccessor("AV_Map")
def av_map(value: AnyValue) -> Optional[TextMap[AnyValue]]:
    pass


@DamlName("emptyChoiceContext")
def empty_choice_context() -> ChoiceContext:
    pass


@DamlName("emptyMetadata")
def empty_metadata() -> Metadata:
    pass
