from pkgutil import iter_modules
import re
from typing import Optional

from forge.ast import nodes as vy_ast
from forge.builtins import choice, collect_daml_builtins, ledger_effect
from forge.exceptions import DamlForgeException, ExceptionList
from forge.models.error_codes import ErrorCodes

FLAG_MEMBER_NAME = re.compile(r"^[A-Z][A-Z0-9_]*$")

# preconsuming/postconsuming are template-only; not supported on interface choices
# (compiler/damlc/daml-lf-conversion/src/DA/Daml/LFConversion.hs, "Preconsuming/Postconsuming
# choice for interface" is an unsupported-operation error there)
TEMPLATE_ONLY_CONSUMING_VARIANTS = {"preconsuming", "postconsuming"}


def _choice_calls(fn: vy_ast.FunctionDef):
    for dec in fn.decorator_list:
        if not isinstance(dec, vy_ast.Call):
            continue
        if isinstance(dec.func, vy_ast.Name) and dec.func.id == choice.__name__:
            yield dec


def _has_decorator(fn: vy_ast.FunctionDef, name: str) -> bool:
    for dec in fn.decorator_list:
        target = dec.func if isinstance(dec, vy_ast.Call) else dec
        if isinstance(target, vy_ast.Name) and target.id == name:
            return True
    return False


def check_unknown_decorators(container: vy_ast.TopLevel, errors: ExceptionList) -> None:
    import forge.builtins as builtins_module
    from forge.models import decorators as vy_decorators_module
    from forge.semantics.analysis.imports import ImportsBuilder

    known_decorators = builtins_module.known_decorator_names()
    imported_names = ImportsBuilder.imported_names(container.module_node)

    for fn in container.body:
        if not isinstance(fn, vy_ast.FunctionDef):
            continue

        for dec in fn.decorator_list:
            target = dec.func if isinstance(dec, vy_ast.Call) else dec
            if not (isinstance(target, vy_ast.Name) and target.id in known_decorators):
                name = target.id if isinstance(target, vy_ast.Name) else "<expression>"
                errors.append(
                    DamlForgeException(
                        f"Unknown decorator `@{name}` on `{container.name}.{fn.name}` - only "
                        f"{sorted(known_decorators)!r} are recognized decorators",
                        dec,
                        code=ErrorCodes.DF1220.value,
                    )
                )
                continue

            resolved = getattr(builtins_module, target.id, None) or getattr(
                vy_decorators_module, target.id, None
            )
            target._metadata["_type"] = resolved

            if isinstance(resolved, type) and issubclass(resolved, builtins_module.VyDecorator):
                resolved.__post_vy_check__(container, fn, dec, errors)

            if target.id not in imported_names:
                errors.append(
                    DamlForgeException(
                        f"`{target.id}` is not defined - import the decorator before using it",
                        target,
                        code=ErrorCodes.DF1219.value,
                    )
                )


def check_consuming_variant_scope(
    container: vy_ast.TopLevel, errors: ExceptionList, only_names: Optional[frozenset] = None
) -> None:
    from forge.builtins import _consuming_variant_from_ast

    for fn in container.body:
        if not isinstance(fn, vy_ast.FunctionDef):
            continue
        if only_names is not None and fn.name not in only_names:
            continue

        for call in _choice_calls(fn):
            kwargs = {kw.arg: kw.value for kw in call.keywords}
            consuming = kwargs.get("consuming")
            variant = None if consuming is None else _consuming_variant_from_ast(consuming)

            if variant in TEMPLATE_ONLY_CONSUMING_VARIANTS:
                errors.append(
                    DamlForgeException(
                        f"Choice `{container.name}.{fn.name}` declares "
                        f'`consuming="{variant}"`, which is not supported on '
                        "interface choices — only `consuming`/`nonconsuming` are",
                        fn,
                        code=ErrorCodes.DF1208.value,
                    )
                )


def _interface_choice_names(interface_decl: vy_ast.InterfaceDef) -> frozenset:
    return frozenset(
        stmt.name
        for stmt in interface_decl.body
        if isinstance(stmt, vy_ast.FunctionDef) and any(_choice_calls(stmt))
    )


def _interface_view_type_name(interface_decl: vy_ast.InterfaceDef) -> Optional[str]:
    for kw in interface_decl.keywords:
        if kw.arg == "view" and isinstance(kw.value, vy_ast.Name):
            return kw.value.id
    return None


def _template_implemented_interfaces(
    template: vy_ast.TemplateDef, declarations: dict
) -> list:
    result = []
    for base in template.bases:
        if isinstance(base, vy_ast.Name):
            decl = declarations.get(base.id)
            if isinstance(decl, vy_ast.InterfaceDef):
                result.append((base.id, decl))
    return result


def check_template_interface_bases(
    template: vy_ast.TemplateDef, declarations: dict, errors: ExceptionList
) -> None:
    template_method_names = {
        stmt.name for stmt in template.body if isinstance(stmt, vy_ast.FunctionDef)
    }

    for base in template.bases:
        if not isinstance(base, vy_ast.Name):
            errors.append(
                DamlForgeException(
                    f"Template `{template.name}` base must be a plain interface name",
                    base,
                    code=ErrorCodes.DF1227.value,
                )
            )
            continue

        decl = declarations.get(base.id)
        if not isinstance(decl, vy_ast.InterfaceDef):
            errors.append(
                DamlForgeException(
                    f"Template `{template.name}` declares `{base.id}` as a base, but "
                    f"`{base.id}` is not a known `interface`",
                    base,
                    code=ErrorCodes.DF1227.value,
                )
            )
            continue

        missing = _interface_choice_names(decl) - template_method_names
        for name in sorted(missing):
            errors.append(
                DamlForgeException(
                    f"Template `{template.name}` implements interface `{base.id}` but "
                    f"does not implement its choice `{name}`",
                    template,
                    code=ErrorCodes.DF1228.value,
                )
            )

        view_type = _interface_view_type_name(decl)
        if view_type is not None:
            has_matching_view = any(
                isinstance(stmt, vy_ast.FunctionDef)
                and _has_decorator(stmt, "view")
                and isinstance(stmt.returns, vy_ast.Name)
                and stmt.returns.id == view_type
                for stmt in template.body
            )
            if not has_matching_view:
                errors.append(
                    DamlForgeException(
                        f"Template `{template.name}` implements interface `{base.id}` but "
                        f"has no `@view` method returning `{view_type}`",
                        template,
                        code=ErrorCodes.DF1228.value,
                    )
                )


def check_template_interface_choice_consuming_variants(
    template: vy_ast.TemplateDef, declarations: dict, errors: ExceptionList
) -> None:
    interface_choice_names: set = set()
    for _, decl in _template_implemented_interfaces(template, declarations):
        interface_choice_names |= _interface_choice_names(decl)

    if interface_choice_names:
        check_consuming_variant_scope(template, errors, only_names=frozenset(interface_choice_names))


def check_hidden_ledger_effects(container: vy_ast.TopLevel, errors: ExceptionList) -> None:
    for fn in container.body:
        if not isinstance(fn, vy_ast.FunctionDef):
            continue

        if _has_decorator(fn, ledger_effect.__name__) or _has_decorator(fn, choice.__name__):
            continue

        for call in fn.get_descendants(vy_ast.Call):
            if (
                isinstance(call.func, vy_ast.Name)
                and call.func.id in collect_daml_builtins().ledger_effect_fns
            ):
                errors.append(
                    DamlForgeException(
                        f"`{container.name}.{fn.name}` calls `{call.func.id}` but is not "
                        f"decorated `@{ledger_effect.__name__}` and is not a `@{choice.__name__}`",
                        call,
                        code=ErrorCodes.DF1205.value,
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
            code=ErrorCodes.DF1201.value,
        )
    )


def _find_reserved_declaration(template: vy_ast.TemplateDef, name: str):
    for stmt in template.body:
        target = None
        if isinstance(stmt, (vy_ast.AnnAssign, vy_ast.Assign)):
            target = stmt.target

        if isinstance(target, vy_ast.Name) and target.id == name:
            return stmt
    return None


def _has_reserved_declaration(template: vy_ast.TemplateDef, name: str) -> bool:
    return _find_reserved_declaration(template, name) is not None


NON_BOOLEAN_EXPRESSION_TYPES = (
    vy_ast.Int,
    vy_ast.Decimal,
    vy_ast.Str,
    vy_ast.List,
    vy_ast.Tuple,
    vy_ast.Dict,
    vy_ast.BinOp,
)


def _is_boolean_shaped(node) -> bool:
    if node is None:
        return False
    if isinstance(node, vy_ast.NameConstant):
        return isinstance(node.value, bool)
    if isinstance(node, NON_BOOLEAN_EXPRESSION_TYPES):
        return False
    return True


def _declared_annotation_rejects_bool(stmt) -> bool:
    if not isinstance(stmt, vy_ast.AnnAssign):
        return False
    annotation = stmt.annotation
    return not (isinstance(annotation, vy_ast.Name) and annotation.id == "bool")


def check_template_ensure(template: vy_ast.TemplateDef, errors: ExceptionList) -> None:
    stmt = _find_reserved_declaration(template, "ensure")
    if stmt is None:
        return

    value = stmt.value if isinstance(stmt, (vy_ast.AnnAssign, vy_ast.Assign)) else None
    invalid = not _is_boolean_shaped(value) or _declared_annotation_rejects_bool(stmt)
    if invalid:
        errors.append(
            DamlForgeException(
                f"Template `{template.name}` declares `ensure` with a value that isn't "
                "a boolean-shaped expression (comparison, boolean operator, `not`, or a call)",
                stmt,
                code=ErrorCodes.DF1212.value,
            )
        )


def check_template_key_maintainer(template: vy_ast.TemplateDef, errors: ExceptionList) -> None:
    has_key = _has_reserved_declaration(template, "key")
    has_maintainer = _has_reserved_declaration(template, "maintainer")

    if has_key and not has_maintainer:
        errors.append(
            DamlForgeException(
                f"Template `{template.name}` declares `key` without a `maintainer`",
                template,
                code=ErrorCodes.DF1210.value,
            )
        )
    elif has_maintainer and not has_key:
        errors.append(
            DamlForgeException(
                f"Template `{template.name}` declares `maintainer` without a `key`",
                template,
                code=ErrorCodes.DF1211.value,
            )
        )


def _target_module_from_import_info(info):
    for attr in ("module", "module_ast", "ast", "resolved_module"):
        module = getattr(info, attr, None)
        if isinstance(module, vy_ast.Module):
            return module
    if isinstance(info, dict):
        for attr in ("module", "module_ast", "ast", "resolved_module"):
            module = info.get(attr)
            if isinstance(module, vy_ast.Module):
                return module
    return None


def _reachable_modules(modules) -> list[vy_ast.Module]:
    seen = set()
    ordered = []

    while modules:
        module = modules.pop()
        marker = id(module)
        if marker in seen:
            continue
        seen.add(marker)
        ordered.append(module)

        for stmt in module.body:
            if not isinstance(stmt, (vy_ast.Import, vy_ast.ImportFrom)):
                continue
            for info in stmt._metadata.get("import_infos", ()) or ():
                imported_module = _target_module_from_import_info(info)
                if imported_module is not None:
                    modules.append(imported_module)

    return ordered


def check_flag_member_names(node: vy_ast.FlagDef, errors: ExceptionList) -> None:
    for stmt in node.body:
        if not (isinstance(stmt, vy_ast.Expr) and isinstance(stmt.value, vy_ast.Name)):
            continue
        name = stmt.value.id
        if not FLAG_MEMBER_NAME.match(name):
            errors.append(
                DamlForgeException(
                    f"Flag member `{name}` of `{node.name}` must be SCREAMING_SNAKE_CASE",
                    stmt,
                    code=ErrorCodes.DF1217.value,
                )
            )


def check_container(
    node: vy_ast.TopLevel,
    errors: ExceptionList,
    declarations: Optional[dict] = None,
) -> None:
    if isinstance(node, vy_ast.FlagDef):
        check_flag_member_names(node, errors)
    elif isinstance(node, vy_ast.TemplateDef):
        check_template_signatory(node, errors)
        check_template_key_maintainer(node, errors)
        check_template_ensure(node, errors)
        check_unknown_decorators(node, errors)
        check_hidden_ledger_effects(node, errors)
        if node.bases:
            check_template_interface_bases(node, declarations or {}, errors)
            check_template_interface_choice_consuming_variants(node, declarations or {}, errors)
    elif isinstance(node, vy_ast.InterfaceDef):
        check_unknown_decorators(node, errors)
        check_consuming_variant_scope(node, errors)
        check_hidden_ledger_effects(node, errors)
