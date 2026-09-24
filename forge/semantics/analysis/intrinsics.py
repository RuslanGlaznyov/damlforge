from forge.ast import nodes as vy_ast
from forge.exceptions import DamlForgeException, ExceptionList
from forge.models.error_codes import ErrorCodes

COMPILER_INTRINSIC_IMPORTS = {"datetime": frozenset({"timedelta"})}

_TIMEDELTA_PARAMETERS = (
    "days",
    "seconds",
    "microseconds",
    "milliseconds",
    "minutes",
    "hours",
    "weeks",
)


class DatetimeIntrinsicAnalyzer:
    """Resolve Python datetime constructs that lower directly to Daml."""

    def __init__(self, module: vy_ast.Module, errors: ExceptionList) -> None:
        self.module = module
        self.errors = errors
        self.timedelta_names: set[str] = set()
        self.datetime_aliases: set[str] = set()
        self._index_imports()

    def _index_imports(self) -> None:
        for stmt in self.module.body:
            if isinstance(stmt, vy_ast.ImportFrom) and stmt.module == "datetime":
                self.timedelta_names.update(
                    alias.asname or alias.name for alias in stmt.names if alias.name == "timedelta"
                )
            elif isinstance(stmt, vy_ast.Import):
                self.datetime_aliases.update(
                    alias.asname or alias.name for alias in stmt.names if alias.name == "datetime"
                )

    @staticmethod
    def _local_names(fn: vy_ast.FunctionDef | None) -> set[str]:
        if fn is None:
            return set()
        names = {arg.arg for arg in fn.args.args}
        for node in fn.get_descendants((vy_ast.Assign, vy_ast.AnnAssign, vy_ast.For)):
            target = node.target
            if isinstance(target, vy_ast.Name):
                names.add(target.id)
        return names

    def _is_timedelta(self, node, local_names: set[str]) -> bool:
        if isinstance(node, vy_ast.Name):
            return node.id in self.timedelta_names and node.id not in local_names
        return (
            isinstance(node, vy_ast.Attribute)
            and node.attr == "timedelta"
            and isinstance(node.value, vy_ast.Name)
            and node.value.id in self.datetime_aliases
            and node.value.id not in local_names
        )

    def _normalize_arguments(self, call: vy_ast.Call):
        if len(call.args) > len(_TIMEDELTA_PARAMETERS):
            self._invalid_call(
                call, f"takes at most {len(_TIMEDELTA_PARAMETERS)} positional arguments"
            )
            return None

        values = dict(zip(_TIMEDELTA_PARAMETERS, call.args))
        for keyword in call.keywords:
            if keyword.arg is None:
                self._invalid_call(call, "does not support unpacked keyword arguments")
                return None
            if keyword.arg not in _TIMEDELTA_PARAMETERS:
                self._invalid_call(
                    call,
                    f"does not support `{keyword.arg}=`; supported units are "
                    f"{', '.join(_TIMEDELTA_PARAMETERS)}",
                )
                return None
            if keyword.arg in values:
                self._invalid_call(call, f"got multiple values for `{keyword.arg}`")
                return None
            values[keyword.arg] = keyword.value

        return tuple((name, values[name]) for name in _TIMEDELTA_PARAMETERS if name in values)

    def _invalid_call(self, call: vy_ast.Call, reason: str) -> None:
        self.errors.append(
            DamlForgeException(
                f"`datetime.timedelta(...)` {reason}", call, code=ErrorCodes.DF1225.value
            )
        )

    def analyze(self) -> None:
        if not self.timedelta_names and not self.datetime_aliases:
            return

        used = False
        local_names: dict[int, set[str]] = {}
        for call in self.module.get_descendants(vy_ast.Call):
            fn = call.get_ancestor(vy_ast.FunctionDef)
            names = local_names.setdefault(id(fn), self._local_names(fn))
            if not self._is_timedelta(call.func, names):
                continue
            arguments = self._normalize_arguments(call)
            if arguments is None:
                continue
            call._metadata["timedelta_arguments"] = arguments
            used = True

        for node in self.module.get_descendants((vy_ast.Name, vy_ast.Attribute)):
            if self._is_timedelta(node, set()):
                node._metadata["daml_type_name"] = "RelTime"

        if used:
            required = set(self.module._metadata.get("required_daml_modules", ()))
            required.add("DA.Time")
            self.module._metadata["required_daml_modules"] = tuple(sorted(required))
