"""Real, importable Python stand-ins for real Splice/Canton Daml packages
(`Splice.Amulet`, `Splice.AmuletRules`, ...), mirroring their exact Daml
module path. Purpose is IDE/authoring support for `.vy` source only - these
classes are never executed, and the compiler pipeline never imports this
package; `.vy` source is parsed as text, not run as real Python. See
`forge/models/` for the equivalent treatment of DamlForge's own constructs.
"""
