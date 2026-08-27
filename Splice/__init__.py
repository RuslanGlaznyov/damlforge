"""Real, importable Python stand-ins for real Splice/Canton Daml packages
(`Splice.Amulet`, `Splice.AmuletRules`, ...), mirroring their exact Daml
module path. Primary purpose is IDE/authoring support for `.vy` source -
these classes are never executed, and `.vy` source itself is parsed as
text, not run as real Python. See `forge/models/` for the equivalent
treatment of DamlForge's own constructs.

The compiler's semantic analysis (`forge/semantics/analysis/types.py`)
*does* import this package at analysis time, to validate that a `.vy`
file's `from Splice.X import Y` actually resolves to something real,
catching typos/wrong module paths before a real `dpm build` would. That's
the only reason this needs a marker: `__daml_mirror__` below lets that
resolver positively identify "this is a genuine Splice-Daml-mirror
package," rather than treating any coincidentally-importable Python module
as if it were one (a stray same-named sibling `.vy` file, an unrelated
third-party package, ...).
"""

# Positively identifies this package (and only this package) as a real
# Daml-module mirror, for `forge/semantics/analysis/types.py`'s import
# validation - see the module docstring above.
__daml_mirror__ = True
