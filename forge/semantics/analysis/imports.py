"""Owns every import-resolution concern for `.vy` source, gathered behind a
single `ImportsBuilder`: classifying a root module as Python-annotation-only
scaffolding (`forge.*`, stdlib) vs a real Daml-mirror package (`Splice.*`),
validating `from X import name` against whichever kind it is, rejecting
per-symbol import aliasing (Daml has no such thing), deciding whether a given
imported name needs a corresponding real Daml `import` emitted at codegen
time, and resolving genuine cross-`.vy`-file imports by actually loading and
parsing sibling files from disk - DamlForge's own analog of Vyper's
`ImportAnalyzer` (`vyper/semantics/analysis/imports.py`). The sibling
resolver populates each import statement's `import_infos` metadata, the
exact shape `forge/semantics/analysis/structure.py`'s `_reachable_modules`/
`_target_module_from_import_info` already expect to consume."""

import importlib
import sys
from pathlib import Path
from typing import Optional

from forge.ast import nodes as vy_ast
from forge.ast.parse import parse_to_ast
from forge.exceptions import DamlForgeException, ExceptionList
from forge.models.error_codes import ErrorCodes


class ImportInfo:
    __slots__ = ("alias", "qualified_module_name", "resolved_path", "ast")

    def __init__(self, alias: str, qualified_module_name: str, resolved_path: Path, ast: vy_ast.Module):
        self.alias = alias
        self.qualified_module_name = qualified_module_name
        self.resolved_path = resolved_path
        self.ast = ast


class ImportsBuilder:
    def __init__(self) -> None:
        self._sibling_cache: dict = {}

    @staticmethod
    def _root_of(module_path: str) -> str:
        return module_path.split(".", 1)[0]

    @staticmethod
    def is_annotation_only_root(root: str) -> bool:
        """True for a root that is pure Python/DSL scaffolding with no real
        Daml module behind it at all - derived from Python's own real stdlib
        registry (`sys.stdlib_module_names`), or positively self-identified
        via `__daml_annotation_only__` (`forge/__init__.py` sets this; mirrors
        `Splice/__init__.py`'s `__daml_mirror__` for the opposite case)."""
        if root in sys.stdlib_module_names:
            return True
        try:
            root_mod = importlib.import_module(root)
        except ImportError:
            return False
        return bool(getattr(root_mod, "__daml_annotation_only__", False))

    @staticmethod
    def _is_daml_mirror_package(root: str) -> bool:
        """Whether `root` positively identifies itself as a real Splice-Daml-
        mirror package (`Splice/__init__.py`'s `__daml_mirror__` sentinel),
        rather than merely being *some* Python module that happens to resolve
        successfully - a stray same-named sibling `.vy` file, or an unrelated
        third-party package on `sys.path`, must never be trusted as if it were
        real Daml content just because `importlib` could load it."""
        try:
            root_mod = importlib.import_module(root)
        except ImportError:
            return False
        return bool(getattr(root_mod, "__daml_mirror__", False))

    @classmethod
    def _import_real_module(cls, module_path: str):
        root = cls._root_of(module_path)
        if cls.is_annotation_only_root(root):
            return importlib.import_module(module_path)
        if not cls._is_daml_mirror_package(root):
            return None
        try:
            return importlib.import_module(module_path)
        except ImportError:
            return None

    # ---- Python-backed import validation --------------------------------------

    @classmethod
    def check_import_names_resolve(cls, node, errors: ExceptionList) -> None:
        """Validates every `from X import name` actually exists on the real
        module `X` - for an annotation-only root, `X` always resolves and is
        always checked; for anything else, only checked when it happens to
        resolve as real importable Python (`Splice.*`, when present). Mirrors
        Vyper's hard failure on an import that doesn't resolve
        (`ModuleNotFound`) instead of silently trusting whatever name string
        appears in the `.vy` source."""
        if not isinstance(node, vy_ast.ImportFrom):
            return

        mod = cls._import_real_module(node.module)
        if mod is None:
            return

        for alias in node.names:
            if alias.name == "*" or hasattr(mod, alias.name):
                continue
            errors.append(
                DamlForgeException(
                    f"No name `{alias.name}` in module `{node.module}`",
                    node,
                    code=ErrorCodes.DF1213.value,
                )
            )

    @classmethod
    def needs_daml_import(cls, module_path: str, name: str) -> bool:
        """Whether `name` imported from `module_path` needs a corresponding
        real Daml `import` statement emitted - false for ANYTHING from an
        annotation-only root (`forge.models`/`decimal`/`typing`), whether
        it's a Python stand-in of a Daml builtin type (`Party`, `Decimal`) or
        a DSL-only decorator/marker symbol (`choice`, `view`) - neither has a
        real Daml module behind it at all. True for genuine external Daml
        content (`Splice.*`, a sibling `.vy` module). Used by
        `forge/ir/lower.py`'s `_lower_imports` (via a deferred import there,
        to avoid a module-load-time circular import) as the single source of
        truth, instead of a separate, disconnected root-name heuristic."""
        if name == "*":
            return True  # can't classify a wildcard - surface it rather than silently dropping it
        return not cls.is_annotation_only_root(cls._root_of(module_path))

    @classmethod
    def imported_names(cls, module: vy_ast.Module) -> set:
        """Names this module's `import`/`from ... import` statements bind
        into its own namespace that are genuinely valid Daml TYPE references
        - a Daml builtin (for `decimal`/`typing`/`forge.*` DSL scaffolding),
        or any real exported name (for `Splice.*`/other external Daml
        modules, where everything exported is legitimately a type/choice).
        Excludes DSL-only decorator/marker symbols like `forge.models.choice`
        - those are never valid in a type-annotation position."""
        # deferred import: `types.py` imports `ImportsBuilder` from this
        # module, so importing it back at module-load time would be circular.
        from forge.semantics.analysis.types import daml_builtin_type_names

        names = set()
        builtins = daml_builtin_type_names()
        for stmt in module.body:
            if isinstance(stmt, vy_ast.Import):
                for alias in stmt.names:
                    names.add(alias.asname or alias.name)
            elif isinstance(stmt, vy_ast.ImportFrom):
                root = cls._root_of(stmt.module)
                for alias in stmt.names:
                    if alias.name == "*":
                        continue
                    bound = alias.asname or alias.name
                    if cls.is_annotation_only_root(root) and alias.name not in builtins:
                        continue
                    names.add(bound)
        return names

    @staticmethod
    def check_no_aliased_from_import(node, errors: ExceptionList) -> None:
        if not isinstance(node, vy_ast.ImportFrom):
            return

        for alias in node.names:
            if alias.asname and alias.name != "*":
                errors.append(
                    DamlForgeException(
                        f"Aliased imports (`{alias.name} as {alias.asname}`) are not "
                        "supported - Daml has no per-symbol import alias; import "
                        f"`{alias.name}` directly, or use `import {node.module} as ...` "
                        "for whole-module qualified aliasing instead",
                        node,
                        code=ErrorCodes.DF1213.value,
                    )
                )

    # ---- sibling `.vy`-file resolution -----------------------------------------

    @staticmethod
    def _module_str_to_relpath(module_str: str) -> Path:
        return Path(*module_str.split("."))

    @staticmethod
    def _search_base(module: vy_ast.Module) -> Path:
        resolved = getattr(module, "resolved_path", None) or getattr(module, "path", None)
        if resolved:
            return Path(resolved).resolve().parent
        return Path.cwd()

    @classmethod
    def _find_sibling_vy_file(cls, module_str: str, search_base: Path) -> Optional[Path]:
        candidate = (search_base / cls._module_str_to_relpath(module_str)).with_suffix(".vy")
        return candidate if candidate.is_file() else None

    @staticmethod
    def _module_strs_for(node) -> list:
        if isinstance(node, vy_ast.ImportFrom):
            return [node.module]
        if isinstance(node, vy_ast.Import):
            return [alias.name for alias in node.names]
        return []

    def resolve_sibling_imports(self, module: vy_ast.Module, _stack: tuple = ()) -> None:
        """Recursively resolves every `import`/`from ... import` in `module`
        that refers to a real sibling `.vy` file, populating `import_infos`
        metadata on each such statement so the rest of semantic analysis
        (`_reachable_modules`, `known_type_names`, `known_field_types`,
        `_RecursionContext`) sees the real sibling module instead of nothing.
        Detects import cycles (mirrors Vyper's `ImportCycle`), the same way a
        self-referential `A imports B imports A` chain would hang or silently
        duplicate-parse without it. Imports that don't resolve to a real
        `.vy` file on disk (Python-backed roots, or a genuinely missing
        reference) are left untouched - `check_import_names_resolve` handles
        those, or the reference surfaces later as an unknown-type error.
        Reuses `self._sibling_cache` across every top-level module in the
        same `analyze_modules()` pass, so a file shared by multiple modules
        is only ever read and parsed once."""
        search_base = self._search_base(module)
        resolved = getattr(module, "resolved_path", None) or getattr(module, "path", None)
        this_key = str(Path(resolved).resolve()) if resolved else f"<module:{id(module)}>"
        stack = _stack + (this_key,)

        for node in module.body:
            if not isinstance(node, (vy_ast.Import, vy_ast.ImportFrom)):
                continue

            infos = []
            for module_str in self._module_strs_for(node):
                path = self._find_sibling_vy_file(module_str, search_base)
                if path is None:
                    continue

                key = str(path.resolve())
                if key in stack:
                    cycle = " imports ".join((*stack, key))
                    raise DamlForgeException(
                        f"Import cycle detected: {cycle}", node, code=ErrorCodes.DF1213.value
                    )

                if key not in self._sibling_cache:
                    sibling_ast = parse_to_ast(path.read_text(), module_path=path.name, resolved_path=str(path))
                    self._sibling_cache[key] = sibling_ast
                    self.resolve_sibling_imports(sibling_ast, _stack=stack)

                infos.append(ImportInfo(module_str, module_str, path, self._sibling_cache[key]))

            if infos:
                node._metadata["import_infos"] = infos

    @staticmethod
    def check_sibling_import_names_resolve(node, errors: ExceptionList) -> None:
        """Validates every `from X import name` where `X` resolved to a real
        sibling `.vy` file actually names something that module declares -
        mirrors `check_import_names_resolve` (which does the same for
        Python-backed imports), completing the same protection for
        `.vy`-to-`.vy` imports: a typo like `from loan_terms import
        LoanTrackerTypo` is now caught here instead of silently trusted."""
        if not isinstance(node, vy_ast.ImportFrom):
            return

        infos = node._metadata.get("import_infos")
        if not infos:
            return

        declared = {
            n.name
            for info in infos
            for n in info.ast.body
            if isinstance(
                n,
                (
                    vy_ast.StructDef,
                    vy_ast.FlagDef,
                    vy_ast.InterfaceDef,
                    vy_ast.TemplateDef,
                    vy_ast.InstanceDef,
                    vy_ast.FunctionDef,
                ),
            )
        }

        for alias in node.names:
            if alias.name == "*" or alias.name in declared:
                continue
            errors.append(
                DamlForgeException(
                    f"No name `{alias.name}` in module `{node.module}`",
                    node,
                    code=ErrorCodes.DF1213.value,
                )
            )
