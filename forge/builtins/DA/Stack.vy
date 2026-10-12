from forge.builtins import DamlName
from DA.Stack.Types import SrcLoc
import GHC.Stack.Types as Types


@DamlName("prettyCallStack")
def pretty_call_stack(types: Types.CallStack) -> str:
    pass


@DamlName("prettyCallStackLines")
def pretty_call_stack_lines(cs: Types.CallStack) -> list[str]:
    pass


@DamlName("prettySrcLoc")
def pretty_src_loc(src_loc: SrcLoc) -> str:
    pass


@DamlName("getCallStack")
def get_call_stack(stk: Types.CallStack) -> list[tuple[str, SrcLoc]]:
    pass


@DamlName("callStack")
def call_stack() -> Types.CallStack:
    pass


@DamlName("convSrcLoc")
def conv_src_loc(types: Types.SrcLoc) -> SrcLoc:
    pass
