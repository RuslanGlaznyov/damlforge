from typing import Annotated

from forge.models import Optional, variant
from forge.builtins import DamlCaseAccessor, DamlName, no_derive


@no_derive
@variant
class CallStack:
    def EmptyCallStack(): pass
    def PushCallStack(value: tuple[str, SrcLoc, CallStack]): pass
    def FreezeCallStack(value: CallStack): pass


@no_derive
struct SrcLoc:
    src_loc_package: Annotated[str, DamlName("srcLocPackage")]
    src_loc_module: Annotated[str, DamlName("srcLocModule")]
    src_loc_file: Annotated[str, DamlName("srcLocFile")]
    src_loc_start_line: Annotated[int, DamlName("srcLocStartLine")]
    src_loc_start_col: Annotated[int, DamlName("srcLocStartCol")]
    src_loc_end_line: Annotated[int, DamlName("srcLocEndLine")]
    src_loc_end_col: Annotated[int, DamlName("srcLocEndCol")]


@DamlCaseAccessor("EmptyCallStack", arity=0)
def empty_call_stack(value: CallStack) -> Optional[None]:
    pass


@DamlCaseAccessor("PushCallStack")
def push_call_stack(value: CallStack) -> Optional[tuple[str, SrcLoc, CallStack]]:
    pass


@DamlCaseAccessor("FreezeCallStack")
def freeze_call_stack(value: CallStack) -> Optional[CallStack]:
    pass


@DamlName("emptyCallStack")
def empty_call_stack() -> CallStack:
    pass


@DamlName("pushCallStack")
def push_call_stack(tuple_value: tuple[str, SrcLoc], stk: CallStack) -> CallStack:
    pass


@DamlName("popCallStack")
def pop_call_stack(stk: CallStack) -> CallStack:
    pass
