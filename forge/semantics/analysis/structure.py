import re
from collections import defaultdict
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

    known_decorators = builtins_module.known_decorator_names()

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


def check_consuming_variant_scope(container: vy_ast.TopLevel, errors: ExceptionList) -> None:
    from forge.builtins import _consuming_variant_from_ast

    for fn in container.body:
        if not isinstance(fn, vy_ast.FunctionDef):
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
                        "interface/instance choices — only `consuming`/`nonconsuming` are",
                        fn,
                        code=ErrorCodes.DF1208.value,
                    )
                )


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


def _module_names(module: vy_ast.Module) -> tuple[str, ...]:
    names = []
    for value in (getattr(module, "resolved_path", None), getattr(module, "path", None)):
        if not value:
            continue
        text = str(value)
        names.append(text)
        stem = text.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        names.append(stem)
        names.append(text.rsplit(".", 1)[0].replace("/", "."))
    return tuple(dict.fromkeys(names))


def _module_key(module: vy_ast.Module) -> str:
    names = _module_names(module)
    return names[0] if names else f"<module:{id(module)}>"


def _function_scope(fn: vy_ast.FunctionDef) -> tuple[str, ...]:
    parent = fn.parent
    if isinstance(parent, vy_ast.Module):
        return ()
    if isinstance(parent, vy_ast.TopLevel):
        return (parent.name,)
    return ()


def _function_key(fn: vy_ast.FunctionDef) -> tuple[str, tuple[str, ...], str]:
    return (_module_key(fn.module_node), _function_scope(fn), fn.name)


def _function_display(fn: vy_ast.FunctionDef) -> str:
    parts = [*_function_scope(fn), fn.name]
    module_names = _module_names(fn.module_node)
    if module_names:
        parts.insert(0, module_names[-1])
    return ".".join(parts)


def _iter_modules(modules) -> list[vy_ast.Module]:
    if isinstance(modules, vy_ast.Module):
        return [modules]
    for attr in ("modules", "resolved_modules", "imported_modules"):
        candidates = getattr(modules, attr, None)
        if candidates is not None:
            return _iter_modules(candidates)
    if hasattr(modules, "values"):
        candidates = modules.values()
    else:
        try:
            candidates = iter(modules)
        except TypeError:
            return []
    return [module for module in candidates if isinstance(module, vy_ast.Module)]


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
    stack = _iter_modules(modules)

    while stack:
        module = stack.pop()
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
                    stack.append(imported_module)

    return ordered


_FnKey = tuple[str, tuple[str, ...], str]


class _RecursionContext:
    def __init__(self, modules) -> None:
        self.modules = _reachable_modules(modules)
        self.functions_by_key: dict[_FnKey, vy_ast.FunctionDef] = {}
        self.functions_by_module_name: dict[str, str] = {}
        self.top_level_by_module: defaultdict[str, dict[str, _FnKey]] = defaultdict(dict)
        self.methods_by_scope: defaultdict[tuple[str, tuple[str, ...]], dict[str, _FnKey]] = (
            defaultdict(dict)
        )
        self.module_aliases: defaultdict[str, dict[str, str]] = defaultdict(dict)
        self.direct_imports: defaultdict[str, dict[str, _FnKey]] = defaultdict(dict)
        self.edges: defaultdict[_FnKey, list[tuple[_FnKey, vy_ast.Call]]] = defaultdict(list)
        self._recursive_calls: Optional[list[tuple[vy_ast.FunctionDef, vy_ast.Call]]] = None

        self._index_modules()
        self._index_imports()
        self._index_edges()

    def _index_modules(self) -> None:
        for module in self.modules:
            key = _module_key(module)
            for name in _module_names(module):
                self.functions_by_module_name[name] = key

            for fn in module.get_descendants(vy_ast.FunctionDef):
                fn_key = _function_key(fn)
                self.functions_by_key[fn_key] = fn
                if _function_scope(fn):
                    self.methods_by_scope[(key, _function_scope(fn))][fn.name] = fn_key
                else:
                    self.top_level_by_module[key][fn.name] = fn_key

    def _find_module_key(self, name: str) -> Optional[str]:
        if name in self.functions_by_module_name:
            return self.functions_by_module_name[name]
        short_name = name.rsplit(".", 1)[-1]
        return self.functions_by_module_name.get(short_name)

    def _index_imports(self) -> None:
        for module in self.modules:
            module_key = _module_key(module)
            for stmt in module.body:
                if isinstance(stmt, vy_ast.Import):
                    for alias in stmt.names:
                        imported_key = self._find_module_key(alias.name)
                        if imported_key is not None:
                            self.module_aliases[module_key][
                                alias.asname or alias.name
                            ] = imported_key
                elif isinstance(stmt, vy_ast.ImportFrom):
                    imported_key = self._find_module_key(stmt.module)
                    if imported_key is None:
                        continue
                    for alias in stmt.names:
                        imported_fn = self.top_level_by_module[imported_key].get(alias.name)
                        if imported_fn is not None:
                            self.direct_imports[module_key][
                                alias.asname or alias.name
                            ] = imported_fn

    def _resolve_call(
        self, fn: vy_ast.FunctionDef, call: vy_ast.Call
    ) -> Optional[tuple[str, tuple[str, ...], str]]:
        module_key, scope, _ = _function_key(fn)
        call_fn = call.func

        if isinstance(call_fn, vy_ast.Name):
            name = call_fn.id
            if scope and (target := self.methods_by_scope[(module_key, scope)].get(name)):
                return target
            if target := self.top_level_by_module[module_key].get(name):
                return target
            return self.direct_imports[module_key].get(name)

        if not isinstance(call_fn, vy_ast.Attribute):
            return None

        attr = call_fn.attr
        value = call_fn.value
        if isinstance(value, vy_ast.Name):
            if value.id == "self" and scope:
                return self.methods_by_scope[(module_key, scope)].get(attr)
            if imported_key := self.module_aliases[module_key].get(value.id):
                return self.top_level_by_module[imported_key].get(attr)

        return None

    def _index_edges(self) -> None:
        for fn_key, fn in self.functions_by_key.items():
            for call in fn.get_descendants(vy_ast.Call):
                target = self._resolve_call(fn, call)
                if target is not None:
                    self.edges[fn_key].append((target, call))

    def recursive_calls(self) -> list[tuple[vy_ast.FunctionDef, vy_ast.Call]]:
        if self._recursive_calls is not None:
            return self._recursive_calls

        calls = []
        index = 0
        stack = []
        indexes = {}
        lowlinks = {}
        on_stack = set()

        def strongconnect(fn_key):
            nonlocal index
            indexes[fn_key] = index
            lowlinks[fn_key] = index
            index += 1
            stack.append(fn_key)
            on_stack.add(fn_key)

            for target, _ in self.edges.get(fn_key, ()):
                if target not in indexes:
                    strongconnect(target)
                    lowlinks[fn_key] = min(lowlinks[fn_key], lowlinks[target])
                elif target in on_stack:
                    lowlinks[fn_key] = min(lowlinks[fn_key], indexes[target])

            if lowlinks[fn_key] != indexes[fn_key]:
                return

            component = set()
            while True:
                target = stack.pop()
                on_stack.remove(target)
                component.add(target)
                if target == fn_key:
                    break

            if len(component) == 1:
                only = next(iter(component))
                for target, call in self.edges.get(only, ()):
                    if target == only:
                        calls.append((self.functions_by_key[only], call))
                return

            for source in component:
                for target, call in self.edges.get(source, ()):
                    if target in component:
                        calls.append((self.functions_by_key[source], call))

        for fn_key in self.functions_by_key:
            if fn_key not in indexes:
                strongconnect(fn_key)

        self._recursive_calls = calls
        return calls


def _recursion_targets(node: vy_ast.TopLevel) -> set[tuple[str, tuple[str, ...], str]]:
    if isinstance(node, vy_ast.FunctionDef):
        return {_function_key(node)}
    return {_function_key(fn) for fn in node.get_descendants(vy_ast.FunctionDef)}


def check_recursion(
    node: vy_ast.TopLevel, errors: ExceptionList, context: Optional[_RecursionContext] = None
) -> None:
    module = node if isinstance(node, vy_ast.Module) else node.module_node
    context = context or _RecursionContext(module)
    targets = _recursion_targets(node)
    if not targets:
        return

    for fn, call in context.recursive_calls():
        if _function_key(fn) not in targets:
            continue
        errors.append(
            DamlForgeException(
                f"Function `{_function_display(fn)}` is recursive, which is not supported",
                call,
                code=ErrorCodes.DF1209.value,
            )
        )


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
    recursion_context: Optional[_RecursionContext] = None,
) -> None:
    if isinstance(node, vy_ast.FlagDef):
        check_flag_member_names(node, errors)
    elif isinstance(node, vy_ast.TemplateDef):
        check_template_signatory(node, errors)
        check_template_key_maintainer(node, errors)
        check_template_ensure(node, errors)
        check_unknown_decorators(node, errors)
        check_hidden_ledger_effects(node, errors)
        check_recursion(node, errors, recursion_context)
    elif isinstance(node, (vy_ast.InterfaceDef, vy_ast.InstanceDef)):
        check_unknown_decorators(node, errors)
        check_consuming_variant_scope(node, errors)
        check_hidden_ledger_effects(node, errors)
        check_recursion(node, errors, recursion_context)
    elif isinstance(node, vy_ast.FunctionDef):
        check_recursion(node, errors, recursion_context)
