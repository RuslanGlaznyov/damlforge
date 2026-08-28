from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _version
from pathlib import Path as _Path

from forge.compiler import compile_code, compile_from_file_input

# Positively identifies this package as pure Python/DSL scaffolding with no
# Daml module behind it at all - decorator/marker symbols (`choice`, `view`)
# and Daml-builtin-type stand-ins (`Party`, `Decimal`) both live here, and
# neither ever needs a Daml `import` emitted for them. Mirrors
# `Splice/__init__.py`'s `__daml_mirror__` for the opposite case - see
# `forge/semantics/analysis/types.py`'s `_is_annotation_only_root`.
__daml_annotation_only__ = True

_commit_hash_file = _Path(__file__).parent.joinpath("damlforge_git_commithash.txt")

if _commit_hash_file.exists():
    with _commit_hash_file.open() as fp:
        __commit__ = fp.read()
else:
    __commit__ = "unknown"

__version__: str
try:
    __version__ = _version(__name__)
except PackageNotFoundError:
    from forge.version import version

    __version__ = version

# pep440 version with commit hash
__long_version__ = f"{__version__}+commit.{__commit__}"
