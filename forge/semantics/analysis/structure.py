from forge.ast import nodes as vy_ast
from forge.exceptions import DamlForgeException, ExceptionList

CHOICE_DECORATOR = "choice"
LEDGER_EFFECT_DECORATOR = "ledger_effect"
VIEW_DECORATOR = "view"

LEDGER_EFFECT_BUILTINS = {"create", "fetch", "exercise", "archive", "lookup"}


def _choice_calls(fn: vy_ast.FunctionDef):
    for dec in fn.decorator_list:
        if not isinstance(dec, vy_ast.Call):
            continue
        if isinstance(dec.func, vy_ast.Name) and dec.func.id == CHOICE_DECORATOR:
            yield dec


def _is_bool_literal(node) -> bool:
    return isinstance(node, vy_ast.NameConstant) and isinstance(node.value, bool)


def _has_decorator(fn: vy_ast.FunctionDef, name: str) -> bool:
    for dec in fn.decorator_list:
        target = dec.func if isinstance(dec, vy_ast.Call) else dec
        if isinstance(target, vy_ast.Name) and target.id == name:
            return True
    return False


def _check_bare_marker_decorator(
    container: vy_ast.TopLevel, name: str, code: str, errors: ExceptionList
) -> None:
    for fn in container.body:
        if not isinstance(fn, vy_ast.FunctionDef):
            continue

        for dec in fn.decorator_list:
            target = dec.func if isinstance(dec, vy_ast.Call) else dec
            if not (isinstance(target, vy_ast.Name) and target.id == name):
                continue

            if isinstance(dec, vy_ast.Call):
                errors.append(
                    DamlForgeException(
                        f"`@{name}` on `{container.name}.{fn.name}` takes no arguments",
                        fn,
                        code=code,
                    )
                )


def check_choice_decorators(container: vy_ast.TopLevel, errors: ExceptionList) -> None:
    for fn in container.body:
        if not isinstance(fn, vy_ast.FunctionDef):
            continue

        for call in _choice_calls(fn):
            kwargs = {kw.arg: kw.value for kw in call.keywords}
            qualified_name = f"{container.name}.{fn.name}"

            if "controller" not in kwargs:
                errors.append(
                    DamlForgeException(
                        f"Choice `{qualified_name}` must declare an explicit `controller`",
                        fn,
                        code="DF1202",
                    )
                )

            consuming = kwargs.get("consuming")
            if consuming is None or not _is_bool_literal(consuming):
                errors.append(
                    DamlForgeException(
                        f"Choice `{qualified_name}` must explicitly declare "
                        "`consuming=True` or `consuming=False`",
                        fn,
                        code="DF1203",
                    )
                )


def check_ledger_effect_decorator(container: vy_ast.TopLevel, errors: ExceptionList) -> None:
    _check_bare_marker_decorator(container, LEDGER_EFFECT_DECORATOR, "DF1204", errors)


def check_hidden_ledger_effects(container: vy_ast.TopLevel, errors: ExceptionList) -> None:
    for fn in container.body:
        if not isinstance(fn, vy_ast.FunctionDef):
            continue

        if _has_decorator(fn, LEDGER_EFFECT_DECORATOR) or _has_decorator(fn, CHOICE_DECORATOR):
            continue

        for call in fn.get_descendants(vy_ast.Call):
            if isinstance(call.func, vy_ast.Name) and call.func.id in LEDGER_EFFECT_BUILTINS:
                errors.append(
                    DamlForgeException(
                        f"`{container.name}.{fn.name}` calls `{call.func.id}` but is not "
                        f"decorated `@{LEDGER_EFFECT_DECORATOR}` and is not a `@{CHOICE_DECORATOR}`",
                        call,
                        code="DF1205",
                    )
                )


def check_view_decorator(container: vy_ast.TopLevel, errors: ExceptionList) -> None:
    _check_bare_marker_decorator(container, VIEW_DECORATOR, "DF1206", errors)


def check_view_outside_interface(container: vy_ast.TopLevel, errors: ExceptionList) -> None:
    for fn in container.body:
        if not isinstance(fn, vy_ast.FunctionDef):
            continue

        if _has_decorator(fn, VIEW_DECORATOR):
            errors.append(
                DamlForgeException(
                    f"`@{VIEW_DECORATOR}` on `{container.name}.{fn.name}` is only valid "
                    "inside `interface`/`instance`, not `template`",
                    fn,
                    code="DF1207",
                )
            )


def check_template_signatory(template: vy_ast.TemplateDef, errors: ExceptionList) -> None:
    for stmt in template.body:
        target = None
        if isinstance(stmt, (vy_ast.AnnAssign, vy_ast.Assign)):
            target = stmt.target

        if isinstance(target, vy_ast.Name) and target.id == "signatory":
            return

    errors.append(
        DamlForgeException(
            f"Template `{template.name}` must declare an explicit `signatory`",
            template,
            code="DF1201",
        )
    )


def check_container(node: vy_ast.TopLevel, errors: ExceptionList) -> None:
    if isinstance(node, vy_ast.TemplateDef):
        check_template_signatory(node, errors)
        check_choice_decorators(node, errors)
        check_ledger_effect_decorator(node, errors)
        check_hidden_ledger_effects(node, errors)
        check_view_decorator(node, errors)
        check_view_outside_interface(node, errors)
    elif isinstance(node, (vy_ast.InterfaceDef, vy_ast.InstanceDef)):
        check_choice_decorators(node, errors)
        check_ledger_effect_decorator(node, errors)
        check_hidden_ledger_effects(node, errors)
        check_view_decorator(node, errors)
