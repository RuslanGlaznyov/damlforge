from typing import Annotated

from forge.builtins import DamlName, no_derive


@no_derive
struct SrcLoc:
    src_loc_package: Annotated[str, DamlName("srcLocPackage")]
    src_loc_module: Annotated[str, DamlName("srcLocModule")]
    src_loc_file: Annotated[str, DamlName("srcLocFile")]
    src_loc_start_line: Annotated[int, DamlName("srcLocStartLine")]
    src_loc_start_col: Annotated[int, DamlName("srcLocStartCol")]
    src_loc_end_line: Annotated[int, DamlName("srcLocEndLine")]
    src_loc_end_col: Annotated[int, DamlName("srcLocEndCol")]
